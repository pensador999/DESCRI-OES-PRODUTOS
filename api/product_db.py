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
import urllib.request

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
    """Garante que a descrição seja o Modo B oficial compilado (>1000 chars, com 3 Atos ou Molde D2C Bonés e Ficha Técnica)."""
    raw_b = p.get("mode_b_html")
    arch_id = p.get("archetype_id") or ""
    title_l = (p.get("title") or "").lower()
    sku_str = str(p.get("master_sku") or p.get("sku") or "").strip()
    is_cap_or_hat = arch_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy") or (
        bool(re.search(r'\b(boné|bone|bonés|chapéu|chapeu|chapéus|chapeus)\b', title_l))
        and not any(w in title_l for w in ["copo", "garrafa", "camisa", "till the bones"])
    )
    is_uv = (arch_id == "uv_performance") or any(w in title_l for w in ["camisa", "uv", "armorx", "xtech"])

    # Verificar se a cor de tema corresponde à loja
    expected_theme_marker = {
        "brk_fishing": ("#0284c7", "#00a8ff"),
        "brk_agro": ("#15803d", "#22c55e"),
        "brk_motors": ("#ea580c", "#f97316"),
    }.get(store_key, ("#0284c7", "#00a8ff"))

    # Se já tem o formato oficial correspondente e atualizado (Fase 5/6), reaproveita direto
    if raw_b and len(raw_b.strip()) > 500 and "<!-- BRK-MODO-B" in raw_b and "use-brk-images-s3" not in raw_b:
        has_store_color = any(c in raw_b for c in expected_theme_marker)
        if is_cap_or_hat:
            if "brk-cap-description" in raw_b and has_store_color:
                return raw_b
        elif not is_uv:
            if has_store_color:
                return raw_b
        else:
            has_new_sg = any(term in raw_b for term in ["49,5 cm", "Baby Look", "2 Anos", "1 a 2 Anos", "brk-sg-subtitle"]) and "ALTURA" in raw_b
            engine, builder = get_engine_and_builder()
            is_ready = engine.is_ready_delivery(p) if engine else False
            expected_prazo = "Pronta entrega" if is_ready else "10 dias úteis"
            has_correct_prazo = expected_prazo in raw_b

            sku_low = sku_str.lower()
            is_fusion_or_hyb = "fusion" in title_l or "fusion" in sku_low or "hybrid" in title_l or sku_low.startswith("hyb")
            has_no_zipper_violation = not is_fusion_or_hyb or (not bool(re.search(r'\b(zíper|ziper)\b', raw_b, re.I)))

            if "Detalhes Técnicos" in raw_b and has_new_sg and has_correct_prazo and has_no_zipper_violation and has_store_color:
                return raw_b

    engine, builder = get_engine_and_builder()
    if engine and builder:
        try:
            detected_arch = arch_id or engine.detect_archetype(
                p.get("title", ""), p.get("category", ""), p.get("tags", []), vendor=p.get("vendor", ""), sku=sku_str
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

STORE_THEME_METADATA = {
    "brk_fishing": {
        "name": "BRK Fishing",
        "accent": "#0284c7",
        "accent_light": "#38bdf8",
        "badge_bg": "#0c4a6e",
        "label": "Azul Náutico (#0284c7)"
    },
    "brk_agro": {
        "name": "BRK Agro",
        "accent": "#15803d",
        "accent_light": "#4ade80",
        "badge_bg": "#14532d",
        "label": "Verde Campo (#15803d)"
    },
    "brk_motors": {
        "name": "BRK Motors",
        "accent": "#ea580c",
        "accent_light": "#fb923c",
        "badge_bg": "#7c2d12",
        "label": "Laranja Racing (#ea580c)"
    }
}

def detect_audience_badge(p: dict, mode_b: str) -> str:
    title_l = (p.get("title") or "").lower()
    sku_u = str(p.get("master_sku") or p.get("sku") or "").upper()
    if "INFANTIL" in mode_b or "2 Anos" in mode_b or any(w in title_l for w in ["infantil", "kids", "juvenil", "junior"]):
        return "INFANTIL (2 a 13 Anos | PP ao G2)"
    if "FEMININO" in mode_b or "Baby Look" in mode_b or any(w in title_l for w in ["feminina", "feminino", "baby look", "babylook", "dama"]):
        return "FEMININO (Baby Look)"
    return "ADULTO / MASCULINO"

def sanitize_product(p: dict, store_key: str = "brk_fishing") -> dict:
    """Retorna os campos necessários para a injeção do Modo B garantido e diagnóstico completo no HUD"""
    mode_b = ensure_mode_b_html(p, store_key)
    imgs = p.get("cdn_images") or p.get("gallery") or []
    is_cap_layout = "brk-cap-description" in mode_b
    has_size_guide = "brk-size-guide" in mode_b
    delivery_time = "Pronta entrega" if "Pronta entrega" in mode_b else "10 dias úteis"
    return {
        "id": str(p.get("id", "")),
        "handle": p.get("handle", ""),
        "master_sku": p.get("master_sku") or p.get("sku") or "",
        "title": p.get("title", "Sem Título"),
        "category": p.get("category") or "Geral",
        "status": p.get("status", "SAUDAVEL"),
        "archetype_id": p.get("archetype_id", "uv_performance"),
        "archetype_name": p.get("archetype_name", "Modo B"),
        "audience_badge": detect_audience_badge(p, mode_b),
        "layout_type": "Molde D2C Bonés & Chapéus" if is_cap_layout else ("3 Atos + Ficha + Guia de Medidas" if has_size_guide else "3 Atos + Ficha Técnica"),
        "delivery_time": delivery_time,
        "store_theme": STORE_THEME_METADATA.get(store_key, STORE_THEME_METADATA["brk_fishing"]),
        "cdn_images": imgs,
        "gallery": imgs,
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
            category_filter = (qs.get("category") or ["ALL"])[0].strip()
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

            if category_filter and category_filter.upper() != "ALL":
                cat_l = category_filter.lower()
                filtered_pool = []
                for p in pool:
                    p_cat = str(p.get("category") or "").lower()
                    p_arch = str(p.get("archetype_id") or "").lower()
                    p_title = str(p.get("title") or "").lower()
                    if cat_l == "bones_chapeus":
                        if p_arch in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy") or "boné" in p_cat or "chapéu" in p_cat or "boné" in p_title or "chapéu" in p_title:
                            filtered_pool.append(p)
                    elif cat_l == "camisas":
                        if "camisa" in p_cat or p_arch in ("uv_performance", "casual_cotton", "casual_lifestyle", "button_shirts_work"):
                            filtered_pool.append(p)
                    elif cat_l == "calcas":
                        if "calça" in p_cat or "bermuda" in p_cat or p_arch == "pants_tactical":
                            filtered_pool.append(p)
                    elif cat_l == "corta_vento":
                        if "corta" in p_cat or "jaqueta" in p_cat or "moletom" in p_cat or p_arch in ("windbreaker_jacket", "hoodie_fleece"):
                            filtered_pool.append(p)
                    elif cat_l == "infantil":
                        if any(w in p_title for w in ["infantil", "kids", "juvenil", "junior"]):
                            filtered_pool.append(p)
                    elif cat_l == "feminino":
                        if any(w in p_title for w in ["feminina", "feminino", "baby look", "babylook"]):
                            filtered_pool.append(p)
                    elif cat_l in p_cat or cat_l in p_arch:
                        filtered_pool.append(p)
                pool = filtered_pool

            batch = pool[:limit]
            sanitized_batch = [sanitize_product(p, store_key) for p in batch]

            return self._respond_json(200, {
                "success": True,
                "store": store_key,
                "status_filter": status_filter,
                "category_filter": category_filter,
                "total_available": len(pool),
                "count": len(sanitized_batch),
                "items": sanitized_batch
            }, cache_control="public, s-maxage=60")

        # ---------------------------------------------------------------------
        # 2. Estatísticas do Banco de Dados (Action = stats)
        # ---------------------------------------------------------------------
        if action == "stats":
            cat_counts = {}
            for p in db["products"]:
                c = p.get("category") or "Geral"
                cat_counts[c] = cat_counts.get(c, 0) + 1
            return self._respond_json(200, {
                "success": True,
                "store": store_key,
                "store_theme": STORE_THEME_METADATA.get(store_key, STORE_THEME_METADATA["brk_fishing"]),
                "total_products": db["total"],
                "sem_descricao_count": len(db["empty"]),
                "imagens_quebradas_count": len(db["broken"]),
                "healthy_count": db["total"] - len(db["empty"]) - len(db["broken"]),
                "categories": cat_counts
            }, cache_control="public, s-maxage=120")

        # ---------------------------------------------------------------------
        # 3. Consulta de Produto Único por ID, SKU ou Handle (Action = product)
        # ---------------------------------------------------------------------
        p_id = (qs.get("id") or [""])[0].strip()
        p_sku = (qs.get("sku") or [""])[0].strip().upper()
        p_handle = (qs.get("handle") or [""])[0].strip().lower()

        store_domains = {
            "brk_fishing": "https://www.brkfishing.com.br",
            "brk_agro": "https://www.brkagro.com.br",
            "brk_motors": "https://www.brkmotors.com.br"
        }

        found_product = None
        if p_id:
            found_product = db["by_id"].get(p_id)
        if not found_product and p_sku:
            found_product = db["by_sku"].get(p_sku)
        if not found_product and p_handle:
            found_product = db["by_handle"].get(p_handle)

        # Fallback: se o produto foi recém-criado na Shopify ainda hoje e não consta no JSON estático,
        # busca ao vivo na vitrine pública da loja (por handle ou nos 50 produtos mais recentes por ID)
        if not found_product and (p_handle or p_id):
            base_url = store_domains.get(store_key, "https://www.brkfishing.com.br")
            live_p = None
            try:
                if p_handle:
                    req_h = urllib.request.Request(f"{base_url}/products/{p_handle}.json", headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_h, timeout=6) as resp_h:
                        live_p = json.loads(resp_h.read().decode("utf-8")).get("product")
                if not live_p and p_id:
                    req_l = urllib.request.Request(f"{base_url}/products.json?limit=50", headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_l, timeout=6) as resp_l:
                        recent_list = json.loads(resp_l.read().decode("utf-8")).get("products", [])
                        for rp in recent_list:
                            if str(rp.get("id", "")) == p_id:
                                live_p = rp
                                break
            except Exception as ex:
                print(f"[!] Fallback live lookup falhou para ID={p_id} Handle={p_handle}: {ex}")

            if live_p:
                raw_imgs = [img.get("src") if isinstance(img, dict) else img for img in (live_p.get("images") or []) if img]
                dedup_imgs, seen_r = [], set()
                for u in raw_imgs:
                    r = u.split("?")[0].lower()
                    if r not in seen_r:
                        seen_r.add(r)
                        dedup_imgs.append(u)
                variants = live_p.get("variants") or []
                v_skus = [str(v.get("sku") or "").strip() for v in variants if v.get("sku")]
                master_s = v_skus[0].split("-")[0] if v_skus else ""
                raw_tags = live_p.get("tags") or []
                if isinstance(raw_tags, str):
                    raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
                body_h = (live_p.get("body_html") or "").strip()
                found_product = {
                    "id": live_p.get("id"),
                    "handle": live_p.get("handle", ""),
                    "title": live_p.get("title", ""),
                    "vendor": live_p.get("vendor", "BRK"),
                    "tags": raw_tags,
                    "master_sku": master_s,
                    "variants_skus": v_skus,
                    "body_html": body_h,
                    "status": "SEM_DESCRICAO" if len(re.sub(r"<[^>]+>", "", body_h).strip()) < 20 else "SAUDAVEL",
                    "cdn_images": dedup_imgs,
                    "gallery": dedup_imgs,
                    "image": dedup_imgs[0] if dedup_imgs else "",
                    "updated_at": live_p.get("updated_at", "")
                }

        if not found_product:
            return self._respond_json(404, {
                "success": False,
                "error": f"Produto não encontrado no banco da loja '{store_key}' (ID='{p_id}', SKU='{p_sku}', Handle='{p_handle}').",
                "store": store_key
            })

        sync_live = (qs.get("sync_live") or ["0"])[0] == "1"
        if sync_live and found_product:
            handle = found_product.get("handle") or p_handle
            base_url = store_domains.get(store_key, "https://www.brkfishing.com.br")
            if handle:
                try:
                    req_u = urllib.request.Request(f"{base_url}/products/{handle}.json", headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_u, timeout=6) as resp_u:
                        live_data = json.loads(resp_u.read().decode("utf-8")).get("product", {})
                        if live_data:
                            if live_data.get("title"):
                                found_product["title"] = live_data["title"]
                            if live_data.get("images"):
                                raw_imgs = [img.get("src") if isinstance(img, dict) else img for img in live_data["images"] if img]
                                dedup_imgs, seen_r = [], set()
                                for u in raw_imgs:
                                    r = u.split("?")[0].lower()
                                    if r not in seen_r:
                                        seen_r.add(r)
                                        dedup_imgs.append(u)
                                if dedup_imgs:
                                    found_product["images"] = live_data["images"]
                                    found_product["cdn_images"] = dedup_imgs
                                    found_product["gallery"] = dedup_imgs
                                    found_product["image"] = dedup_imgs[0]
                            found_product.pop("split_images", None)
                            found_product.pop("narrative_blocks", None)
                            found_product["mode_b_html"] = ""  # Forçar regeneração com as fotos e título novos
                except Exception as ex:
                    print(f"[!] Falha ao sincronizar live para {handle}: {ex}")

        return self._respond_json(200, {
            "success": True,
            "store": store_key,
            "sync_live": sync_live,
            "product": sanitize_product(found_product, store_key)
        }, cache_control="public, s-maxage=180" if not sync_live else "no-store")
