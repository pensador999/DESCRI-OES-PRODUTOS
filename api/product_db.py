"""
Vercel Serverless Function: API de Consulta ao Banco de Dados BRK (api/product_db.py)

Permite ao Userscript do Tampermonkey consultar diretamente os dados reais dos produtos
nas 3 lojas BRK (Fishing, Agro, Motors), obtendo descrições oficiais Modo B compiladas,
status de auditoria e filas para automação assistida.

Endpoints suportados:
  GET /api/product_db?store=brk_fishing&id=8421653250114
    -> Retorna o produto individual com status, SKU, título, arquétipo e mode_b_html.

  GET /api/product_db?store=brk_fishing&action=queue&status=SEM_DESCRICAO&limit=25
    -> Retorna lote dos próximos N produtos filtrados por status com mode_b_html.

  GET /api/product_db?store=brk_fishing&action=stats
    -> Retorna estatísticas de contagem e saúde da loja no banco de dados.
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import sys

# Cache em memória para processos warm da Vercel
_CACHED_STORES = {}

ALLOWED_STORES = {
    "brk_fishing": "brk_fishing.json",
    "brk_agro": "brk_agro.json",
    "brk_motors": "brk_motors.json"
}

STORE_SLUG_MAP = {
    "brkfishing": "brk_fishing",
    "brkagro": "brk_agro",
    "brkmotors25": "brk_motors",
    "brk_fishing": "brk_fishing",
    "brk_agro": "brk_agro",
    "brk_motors": "brk_motors"
}

def get_base_dir():
    # Diretório raiz do projeto (um nível acima de api/)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_store_database(store_key: str):
    """Carrega e indexa o arquivo de dados da loja com cache em memória"""
    store_norm = STORE_SLUG_MAP.get(store_key, store_key)
    if store_norm in _CACHED_STORES:
        return _CACHED_STORES[store_norm]

    filename = ALLOWED_STORES.get(store_norm)
    if not filename:
        return None

    base_dir = get_base_dir()
    json_path = os.path.join(base_dir, "data", "stores", filename)

    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        products = data.get("products", []) if isinstance(data, dict) else data

        # Criar índices em memória
        by_id = {}
        by_handle = {}
        by_sku = {}
        empty_list = []
        broken_list = []

        for p in products:
            p_id = str(p.get("id", ""))
            p_handle = str(p.get("handle", "")).lower()
            p_sku = str(p.get("master_sku") or p.get("sku") or "").upper()
            status = p.get("status", "")

            if p_id:
                by_id[p_id] = p
            if p_handle:
                by_handle[p_handle] = p
            if p_sku:
                by_sku[p_sku] = p

            if status == "SEM_DESCRICAO":
                empty_list.append(p)
            elif status == "IMAGENS_QUEBRADAS":
                broken_list.append(p)

        store_pack = {
            "products": products,
            "by_id": by_id,
            "by_handle": by_handle,
            "by_sku": by_sku,
            "empty": empty_list,
            "broken": broken_list,
            "total": len(products)
        }

        _CACHED_STORES[store_norm] = store_pack
        return store_pack

    except Exception as e:
        print(f"[-] Erro ao carregar {json_path}: {e}")
        return None

def sanitize_product(p: dict) -> dict:
    """Retorna apenas os campos necessários para a injeção do Modo B"""
    return {
        "id": str(p.get("id", "")),
        "handle": p.get("handle", ""),
        "master_sku": p.get("master_sku") or p.get("sku") or "",
        "title": p.get("title", "Sem Título"),
        "status": p.get("status", "SAUDAVEL"),
        "archetype_id": p.get("archetype_id", "uv_performance"),
        "archetype_name": p.get("archetype_name", "Modo B"),
        "mode_b_html": p.get("mode_b_html") or p.get("body_html") or "",
        "updated_at": p.get("updated_at") or p.get("published_at") or ""
    }

class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def _respond_json(self, status_code: int, data: dict, cache_control: str = "no-store"):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", cache_control)
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        raw_store = (qs.get("store") or ["brk_fishing"])[0]
        store_key = STORE_SLUG_MAP.get(raw_store, raw_store)

        if store_key not in ALLOWED_STORES:
            return self._respond_json(400, {
                "success": False,
                "error": f"Loja '{raw_store}' desconhecida.",
                "allowed_stores": list(ALLOWED_STORES.keys())
            })

        db = load_store_database(store_key)
        if not db:
            return self._respond_json(500, {
                "success": False,
                "error": f"Não foi possível carregar o banco de dados da loja '{store_key}'."
            })

        action = (qs.get("action") or ["product"])[0]

        # ---------------------------------------------------------------------
        # 1. Consulta de Fila para Automação em Lote (Action = queue)
        # ---------------------------------------------------------------------
        if action == "queue":
            status_filter = (qs.get("status") or ["SEM_DESCRICAO"])[0].upper()
            try:
                limit = int((qs.get("limit") or ["25"])[0])
            except ValueError:
                limit = 25

            if status_filter == "SEM_DESCRICAO":
                pool = db["empty"]
            elif status_filter == "IMAGENS_QUEBRADAS":
                pool = db["broken"]
            else:
                pool = db["products"]

            batch = pool[:limit]
            sanitized_batch = [sanitize_product(p) for p in batch]

            return self._respond_json(200, {
                "success": True,
                "store": store_key,
                "status_filter": status_filter,
                "total_available": len(pool),
                "count": len(sanitized_batch),
                "items": sanitized_batch
            }, cache_control="public, s-maxage=60")

        # ---------------------------------------------------------------------
        # 2. Estatísticas do Banco de Dados (Action = stats)
        # ---------------------------------------------------------------------
        if action == "stats":
            return self._respond_json(200, {
                "success": True,
                "store": store_key,
                "total_products": db["total"],
                "sem_descricao_count": len(db["empty"]),
                "imagens_quebradas_count": len(db["broken"]),
                "healthy_count": db["total"] - len(db["empty"]) - len(db["broken"])
            }, cache_control="public, s-maxage=120")

        # ---------------------------------------------------------------------
        # 3. Consulta de Produto Único por ID ou SKU (Action = product)
        # ---------------------------------------------------------------------
        p_id = (qs.get("id") or [""])[0].strip()
        p_sku = (qs.get("sku") or [""])[0].strip().upper()
        p_handle = (qs.get("handle") or [""])[0].strip().lower()

        found_product = None
        if p_id:
            found_product = db["by_id"].get(p_id)
        elif p_sku:
            found_product = db["by_sku"].get(p_sku)
        elif p_handle:
            found_product = db["by_handle"].get(p_handle)

        if not found_product:
            return self._respond_json(404, {
                "success": False,
                "error": f"Produto não encontrado no banco da loja '{store_key}' (ID='{p_id}', SKU='{p_sku}', Handle='{p_handle}').",
                "store": store_key
            })

        return self._respond_json(200, {
            "success": True,
            "store": store_key,
            "product": sanitize_product(found_product)
        }, cache_control="public, s-maxage=180")
