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
import re

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

_ENGINE = None
_BUILDER = None

def get_engine_and_builder():
    global _ENGINE, _BUILDER
    if _ENGINE is None:
        base_dir = get_base_dir()
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        try:
            from core.template_engine import TemplateEngine
            from core.html_builder import HTMLBuilder
            _ENGINE = TemplateEngine()
            _BUILDER = HTMLBuilder()
        except Exception as e:
            print(f"[-] Erro ao carregar TemplateEngine/HTMLBuilder: {e}")
    return _ENGINE, _BUILDER

def ensure_mode_b_html(p: dict, store_key: str = "brk_fishing") -> str:
    """Garante que a descrição seja o Modo B oficial compilado (>1000 chars, com 3 Atos e Detalhes Técnicos XTech Pro)."""
    raw_b = p.get("mode_b_html")
    arch_id = p.get("archetype_id") or ""
    title_l = (p.get("title") or "").lower()
    is_cap_or_hat = arch_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy") or (
        bool(re.search(r'\b(boné|bone|bonés|chapéu|chapeu|chapéus|chapeus)\b', title_l))
        and not any(w in title_l for w in ["copo", "garrafa", "camisa", "till the bones"])
    )
    is_uv = (arch_id == "uv_performance") or any(w in title_l for w in ["camisa", "uv", "armorx", "xtech"])

    # Se já tem o formato oficial correspondente, reaproveita direto
    if raw_b and len(raw_b.strip()) > 500 and "<!-- BRK-MODO-B" in raw_b:
        if is_cap_or_hat:
            if "brk-cap-description" in raw_b:
                return raw_b
        elif not is_uv:
            return raw_b
        else:
            has_new_sg = any(term in raw_b for term in ["49,5 cm", "Baby Look", "1 a 2 Anos", "brk-sg-subtitle"]) and "ALTURA" in raw_b
            engine, builder = get_engine_and_builder()
            is_ready = engine.is_ready_delivery(p) if engine else False
            expected_prazo = "Pronta entrega" if is_ready else "10 dias úteis"
            has_correct_prazo = expected_prazo in raw_b
            
            sku_low = str(p.get("master_sku") or p.get("sku") or "").lower()
            is_fusion_or_hyb = "fusion" in title_l or "fusion" in sku_low or "hybrid" in title_l or sku_low.startswith("hyb")
            has_no_zipper_violation = not is_fusion_or_hyb or (not bool(re.search(r'\b(zíper|ziper)\b', raw_b, re.I)))
            
            if "Detalhes Técnicos" in raw_b and "XTech Pro" in raw_b and has_new_sg and has_correct_prazo and has_no_zipper_violation:
                return raw_b

    engine, builder = get_engine_and_builder()
    if engine and builder:
        try:
            detected_arch = arch_id or engine.detect_archetype(
                p.get("title", ""), p.get("category", ""), p.get("tags", []), vendor=p.get("vendor", "")
            )
            images = p.get("gallery") or p.get("cdn_images") or []
            narrative = engine.generate_narrative_from_template(p, detected_arch, images, store_key=store_key)
            compiled_b = builder.build_shopify_html(narrative)
            p["mode_b_html"] = compiled_b
            return compiled_b
        except Exception as e:
            print(f"[-] Erro na compilação do Modo B para {p.get('id')}: {e}")

    # Fallback apenas se a compilação falhar
    return p.get("mode_b_html") or p.get("body_html") or ""

def sanitize_product(p: dict, store_key: str = "brk_fishing") -> dict:
    """Retorna apenas os campos necessários para a injeção do Modo B garantido"""
    mode_b = ensure_mode_b_html(p, store_key)
    return {
        "id": str(p.get("id", "")),
        "handle": p.get("handle", ""),
        "master_sku": p.get("master_sku") or p.get("sku") or "",
        "title": p.get("title", "Sem Título"),
        "status": p.get("status", "SAUDAVEL"),
        "archetype_id": p.get("archetype_id", "uv_performance"),
        "archetype_name": p.get("archetype_name", "Modo B"),
        "mode_b_html": mode_b,
        "mode_b_chars": len(mode_b),
        "has_official_mode_b": "<!-- BRK-MODO-B" in mode_b,
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
            sanitized_batch = [sanitize_product(p, store_key) for p in batch]

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
            "product": sanitize_product(found_product, store_key)
        }, cache_control="public, s-maxage=180")
