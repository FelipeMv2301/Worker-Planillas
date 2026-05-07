import os
import httpx
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

logger = logging.getLogger("SAPClientWorker")

class AsyncSAPClientWorker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AsyncSAPClientWorker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.base_url = os.getenv("SAP_BASE_URL", "").rstrip('/')
        self.db = os.getenv("SAP_DB", "")
        self.user = os.getenv("SAP_USER", "")
        self.password = os.getenv("SAP_PASSWORD", "")
        self.session_token = None
        self.route_id = None
        self.last_login = None
        self.session_timeout = timedelta(minutes=25)
        
        self.client = httpx.AsyncClient(verify=ssl_context, timeout=60.0)
        self._initialized = True

    def _is_session_valid(self):
        if not self.session_token or not self.last_login:
            return False
        return (datetime.now() - self.last_login) < self.session_timeout

    async def login(self):
        if self._is_session_valid():
            return True

        logger.info("🔐 Iniciando sesión Async en SAP (Worker)...")
        try:
            payload = {
                "CompanyDB": self.db,
                "UserName": self.user,
                "Password": self.password
            }
            
            for attempt in range(2):
                response = await self.client.post(f"{self.base_url}/Login", json=payload)
                if response.status_code in (200, 204):
                    self.session_token = response.cookies.get("B1SESSION")
                    self.route_id = response.cookies.get("ROUTEID")
                    self.last_login = datetime.now()
                    return True
                
                if "-304" in response.text and attempt == 0:
                    await asyncio.sleep(1)
                    continue
                
                logger.error(f"❌ Error Login SAP ({response.status_code}): {response.text}")
                break
                
            return False
        except Exception as e:
            logger.error(f"❌ Error en login de SAP Async: {e}")
            return False

    def get_cookies(self):
        cookies = {}
        if self.session_token:
            cookies["B1SESSION"] = self.session_token
        if self.route_id:
            cookies["ROUTEID"] = self.route_id
        return cookies

    async def get_invoices_without_folio(self, days_back: int = 2) -> list:
        """
        Busca facturas emitidas en los últimos N días que no tienen folio.
        """
        if not await self.login():
            return []
            
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        # Filtros extraídos desde n8n
        params = {
            "$select": "DocEntry,DocNum,FolioNumber,FolioPrefixString,U_Contacto,CardCode,DocTotal,U_WedDocNum",
            "$filter": f"(FolioNumber eq null or FolioNumber eq 0) and CreationDate ge '{date_from}'",
            "$orderby": "DocEntry asc"
        }
        url = f"{self.base_url}/Invoices"
        try:
            response = await self.client.get(url, params=params, cookies=self.get_cookies())
            if response.status_code == 200:
                data = response.json()
                return data.get('value', [])
            else:
                logger.error(f"Error fetching invoices without folio: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error de red: {e}")
            return []

    async def update_invoice_folio(self, doc_entry: int, folio_number: int) -> bool:
        if not await self.login():
            return False
        url = f"{self.base_url}/Invoices({doc_entry})"
        try:
            response = await self.client.patch(url, json={"FolioNumber": folio_number}, cookies=self.get_cookies())
            if response.status_code in (204, 200):
                return True
            logger.error(f"Error updating SAP folio: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Error de red actualizando folio: {e}")
            return False
