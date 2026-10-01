"""
Cliente para a API Pública da Shopify (/products.json e /products/{handle}.json).
Permite varredura completa de catálogos sem necessidade imediata de tokens privados.
"""

import time
import requests
from typing import List, Dict, Any, Optional
from core.config import STORES, HTTP_HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY

class ShopifyPublicAPI:
    def __init__(self, store_key: str = "brk"):
        if store_key not in STORES:
            raise ValueError(f"Loja '{store_key}' não configurada em STORES.")
        self.store_key = store_key
        self.store_info = STORES[store_key]
        self.base_url = self.store_info["base_url"].rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

    def fetch_products_page(self, page: int = 1, limit: int = 250) -> List[Dict[str, Any]]:
        """Busca uma página de produtos via /products.json."""
        url = f"{self.base_url}/products.json"
        params = {"page": page, "limit": min(limit, 250)}
        
        for attempt in range(3):
            try:
                response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("products", [])
                elif response.status_code == 429:
                    # Rate limit respeitoso
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    response.raise_for_status()
            except requests.RequestException as e:
                if attempt == 2:
                    print(f"[ERRO] Falha ao buscar página {page}: {e}")
                    return []
                time.sleep(1)
        return []

    def fetch_product_by_handle(self, handle: str) -> Optional[Dict[str, Any]]:
        """Busca os dados detalhados de um produto específico pelo handle."""
        url = f"{self.base_url}/products/{handle}.json"
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                return data.get("product")
        except requests.RequestException as e:
            print(f"[ERRO] Falha ao buscar produto {handle}: {e}")
        return None

    def fetch_all_products(self, max_products: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Varre o catálogo completo da loja através de paginação.
        Para quando não houver mais produtos ou quando atingir max_products.
        """
        all_products = []
        page = 1
        page_size = 250
        
        print(f"[*] Iniciando varredura no catálogo de {self.store_info['name']} ({self.base_url})...")
        while True:
            products = self.fetch_products_page(page=page, limit=page_size)
            if not products:
                break
                
            all_products.extend(products)
            print(f" -> Página {page}: {len(products)} produtos carregados (Total até agora: {len(all_products)})")
            
            if max_products and len(all_products) >= max_products:
                all_products = all_products[:max_products]
                break
                
            if len(products) < page_size:
                # Última página atingida
                break
                
            page += 1
            time.sleep(REQUEST_DELAY)

        print(f"[OK] Varredura concluida. Total de produtos coletados: {len(all_products)}")
        return all_products
