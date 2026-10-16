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

def evaluate_guideline_compliance(p: dict, store_key: str = "brk_fishing") -> tuple:
    """
    Avalia se a descrição atual do produto na Shopify (body_html) está 100% dentro das
    Diretrizes Modo B v5 ou se possui alguma violação de regra.
    Retorna: (is_mode_b_compliant: bool, guideline_status: str, guideline_reason: str)
    """
    orig_html = p.get("body_html") or p.get("original_body_html") or ""
    title_l = str(p.get("title") or "").lower()
    sku_l = str(p.get("master_sku") or p.get("sku") or "").lower()
    status = str(p.get("status") or "")

    plain_text = re.sub(r"<style.*?</style>", " ", orig_html, flags=re.S | re.I)
    plain_text = re.sub(r"<[^>]+>", " ", plain_text)
    plain_text = re.sub(r"\s+", " ", plain_text).strip()

    if len(plain_text) < 20:
        return (False, "SEM_DESCRICAO", "Sem descrição cadastrada na Shopify")
    if "use-brk-images-s3" in orig_html.lower() or "photobucket" in orig_html.lower():
        return (False, "IMAGENS_QUEBRADAS", "Contém imagens quebradas (AWS S3 404)")

    has_mode_b_structure = any(m in orig_html for m in ("<!-- BRK-MODO-B", "brk-desc-wrapper", "brk-cap-description"))
    if not has_mode_b_structure:
        return (False, "FORA_PADRAO_MODO_B", "Descrição legada fora do padrão oficial Modo B (sem 3 Atos / D2C)")

    expected_colors = {
        "brk_fishing": ("#0284c7", "#00a8ff"),
        "brk_agro": ("#15803d", "#22c55e", "#16a34a"),
        "brk_motors": ("#ea580c", "#f97316"),
    }.get(store_key, ("#0284c7", "#00a8ff"))

    violations = []
    if "troca descomplicada" in orig_html.lower() or "dinheiro de volta" in orig_html.lower():
        violations.append("Rodapé antigo com 'Troca Descomplicada / Satisfação garantida ou seu dinheiro de volta' (retirar conforme nova diretriz)")
    if "Tabela de Medidas de Luvas" in orig_html and any(w in title_l or w in sku_l for w in ("camisa", "camiseta", "armorx", "cax", "hyb", "fusion")):
        violations.append("Camisa com Tabela de Luvas (corrigir para Tabela de Camisa PP ao G2)")
    if "Tabela de Medidas Adulto (P ao EXG)" in orig_html:
        violations.append("Tabela Adulto antiga (P ao EXG em vez de PP ao G2)")
    if ("fillet" in title_l or "mfk75t" in title_l or "79081379076" in sku_l) and "bainha" in orig_html.lower() and "bainha" not in title_l:
        violations.append("Faca Marine MFK75T com menção indevida a bainha")
    if ("fusion" in title_l or "fusion" in sku_l or "hybrid" in title_l or sku_l.startswith("hyb")) and re.search(r'\b(zíper|ziper)\b', orig_html, re.I):
        violations.append("Modelo Fusion/Hybrid com menção indevida a zíper")
    if ("fusion" in title_l or "fusion" in sku_l or "hybrid" in title_l or sku_l.startswith("hyb")) and "sem contar" not in orig_html.lower():
        violations.append("Tabela de Medidas sem orientação de Capuz/Bandana Embutida (medir do ombro à barra sem contar o capuz)")
    if "eQxQuY7.jpg" in orig_html and "ba09" not in sku_l:
        violations.append("Boné com foto genérica repetida")

    orig_img_srcs = [u.split("?")[0].lower() for u in re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', orig_html, re.I) if not u.split("?")[0].lower().endswith(".svg")]
    if len(orig_img_srcs) != len(set(orig_img_srcs)):
        violations.append("Fotos repetidas nos Atos/Cards")

    if not any(c in orig_html.lower() for c in expected_colors) and any(c in orig_html.lower() for c in ("#0284c7", "#15803d", "#ea580c", "#f97316")):
        violations.append("Cor de outra loja no HTML")

    if violations:
        return (False, "MODO_B_DESATUALIZADO", "; ".join(violations))

    return (True, "CONFORME_MODO_B", "100% dentro das diretrizes oficiais Modo B")


# Os 32 produtos fora da coleção Super Ofertas (Camisas UV, Bandanas, Facas, Girador, Trava Varas, Chinelo)
# rastreados ao vivo em brkfishing.com.br que foram aplicados com o rodapé antigo "Troca Descomplicada".
TRACKED_OUTSIDE_SUPER_OFERTAS_IDS = [
    "8430512537666",  # [01] FUSION260PP - Camisa FusionX Fantasia de Esqueleto Branco com Proteção UV50+
    "8437007351874",  # [02] T673 - Bandana Halloween Freddy Vermelha UV50+
    "8437006958658",  # [03] T672 - Bandana Halloween Jason Preta UV50+
    "8445327114306",  # [04] BP011BLPP - Camiseta Brasil Patriota Feminina Brasil Acima de Tudo Branca
    "8445323018306",  # [05] BP106PP - Camisa Brasil Patriota Brasil Acima de Todos Amarelo e Verde com UV50+
    "8445323214914",  # [06] BP105PP - Camisa Brasil Patriota Brasil Acima de Todos Branco e Verde com UV50+
    "8424113864770",  # [07] HYB092BLPP - Camisa de Pesca Feminina Brk com Capuz Hybrid Pescaiaque Chumbo
    "8424114126914",  # [08] FUSION197PP - Camisa FusionX Brk Pescaiaque Azul e Amarelo com Proteção UV50+
    "8424113897538",  # [09] HYB092PP - Camisa de Pesca Brk com Capuz Hybrid Pescaiaque Chumbo
    "8424114192450",  # [10] CAX050BLPP - Camisa ArmorX Feminina Brk Pescaiaque Chumbo com Listra Amarela
    "8424113963074",  # [11] HYB091PP - Camisa de Pesca Brk com Capuz Hybrid Pescaiaque Azul
    "8424113930306",  # [12] HYB091BLPP - Camisa de Pesca Feminina Brk com Capuz Hybrid Pescaiaque Azul
    "8424114225218",  # [13] CAX050PP - Camisa ArmorX Brk Pescaiaque Chumbo com Listra Amarela
    "8421653250114",  # [14] CAX049BLPP - Camisa ArmorX Feminina BRK Pescaiaque Azul com Listra e Luva
    "8421653315650",  # [15] CAX049PP - Camisa ArmorX Brk Pescaiaque Azul com Listra e Luva
    "8411025539138",  # [16] FACA27 - Faca Brk Pescaria Cabo Madeira e Resina Transparente com Isca Azul
    "8335319269442",  # [17] CAX040BLPP - Camisa ArmorX Feminina Brk Pinhal com Luva e Proteção UV50+
    "8379931951170",  # [18] HYB090PP - Camisa de Pesca Brk com Capuz Hybrid Camuflada Verde Militar
    "8379931918402",  # [19] HYB090BLPP - Camisa de Pesca Feminina Brk com Capuz Hybrid Camuflada Verde Militar
    "8379931787330",  # [20] CAX048PP - Camisa ArmorX Camuflada Verde Militar com Luva e Proteção UV50
    "8379931754562",  # [21] CAX048BLPP - Camisa ArmorX Feminina Camuflada Verde Militar com Luva e Proteção UV50
    "8370981961794",  # [22] 7908137907694 - Faca Marine Sports Fillet Knife MFK75T 19cm
    "7595719622722",  # [23] C01046BLPP_FULL - Camisa Feminina Brk Basic Cinza Claro com Proteção Solar UV50
    "8369524146242",  # [24] 7898480922799 - Girador Bss Nickel | 1 Caixa com 50 Unidades
    "7595720015938",  # [25] C01349P_FULL - Camisa de Pesca BRK Azul Ocean com Proteção UV50+
    "7595718541378",  # [26] C02363P_FULL - Camisa Brk Clean Bandeira dos EUA com Proteção UV50+
    "7595720114242",  # [27] C0897P_FULL - Camisa de Pesca Brk Azul e Preta com Uv50
    "7595719917634",  # [28] C01806P_FULL - Camisa de Pesca Brk Garateia Clean Bandeira Brasil com Proteção UV50
    "7595719360578",  # [29] C02257P_FULL - Camisa Brk Mescla Preto Cinza com Proteção Solar UV50+
    "8370981929026",  # [30] TRAVAVARA-ROSA - Trava Varas Premium Aço Inox Fishing
    "8337841651778",  # [31] CMB06P - Camisa Work Areia com Proteção UV50+
    "7551701647426",  # [32] COLTAZUL_37_38 - Chinelo Boaonda Conforto Extremo para Pés Sensíveis - Azul
]


_SUPER_OFERTAS_AUDIT = None

def load_super_ofertas_audit() -> dict:
    """Carrega os dados homologados do pente fino de 91 produtos / 627 imagens da coleção Super Ofertas Fishing."""
    global _SUPER_OFERTAS_AUDIT
    if _SUPER_OFERTAS_AUDIT is not None:
        return _SUPER_OFERTAS_AUDIT
    audit_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "super_ofertas_audit_data.json")
    if os.path.exists(audit_path):
        try:
            with open(audit_path, "r", encoding="utf-8") as f:
                _SUPER_OFERTAS_AUDIT = json.load(f)
                return _SUPER_OFERTAS_AUDIT
        except Exception as e:
            print(f"[-] Erro ao carregar super_ofertas_audit_data.json: {e}")
    _SUPER_OFERTAS_AUDIT = {}
    return _SUPER_OFERTAS_AUDIT


def audit_live_gallery_and_variants(p: dict) -> dict:
    """
    Executa diagnóstico de variantes sem foto vinculada (image_id=null), fotos compartilhadas/duplicadas
    e imagens de baixa resolução para qualquer produto da Shopify ou da coleção Super Ofertas.
    """
    pid = str(p.get("id", ""))
    so_audit = load_super_ofertas_audit()
    if pid in so_audit:
        entry = so_audit[pid]
        return {
            "in_super_ofertas": True,
            "collection_index": entry.get("index", 0),
            "total_variants": entry.get("total_variants", 1),
            "total_images": entry.get("total_images", 1),
            "has_unlinked_variants": bool(entry.get("has_unlinked_variants")),
            "unlinked_variants": entry.get("unlinked_variants", []),
            "has_duplicate_images": bool(entry.get("has_duplicate_images")),
            "duplicate_images": entry.get("duplicate_images", []),
            "has_low_res_images": bool(entry.get("has_low_res_images")),
            "low_res_images": entry.get("low_res_images", []),
            "needs_media_fix": bool(entry.get("needs_media_fix"))
        }

    # Diagnóstico dinâmico para produtos de outras coleções/lojas
    variants = p.get("variants") or []
    images = p.get("images") or []
    title_l = str(p.get("title") or "").lower()
    is_line = "linha" in title_l
    unlinked_vars = []
    iid_to_vars = {}
    if len(variants) > 1 and not is_line:
        for v in variants:
            if not isinstance(v, dict):
                continue
            vtitle = str(v.get("title") or "").strip()
            if not vtitle or vtitle == "Default Title":
                continue
            iid = v.get("image_id")
            if not iid and isinstance(v.get("featured_image"), dict):
                iid = v["featured_image"].get("id")
            if iid is None:
                unlinked_vars.append(vtitle)
            else:
                iid_to_vars.setdefault(str(iid), []).append(vtitle)

    dups = []
    for iid_k, vlist in iid_to_vars.items():
        if len(vlist) > 1:
            dups.append({
                "pos1": 0,
                "pos2": 0,
                "v1": vlist,
                "v2": [],
                "type": "SHARED_VARIANT_IMG",
                "summary": f"Mesma foto vinculada a múltiplas variantes: {', '.join(vlist)}"
            })

    low_res = []
    for idx_img, img in enumerate(images, 1):
        if isinstance(img, dict):
            w = img.get("width") or 0
            h = img.get("height") or 0
            pos = img.get("position") or idx_img
            if (w and w < 800) or (h and h < 800):
                low_res.append({
                    "pos": pos,
                    "w": w,
                    "h": h,
                    "kb": 0,
                    "variants": [],
                    "reasons": [f"Baixa resolução ({w}x{h}px)"],
                    "summary": f"Pos {pos}: {w}x{h}px - Baixa resolução (<800px)"
                })

    has_null = len(unlinked_vars) > 0
    has_dup = len(dups) > 0
    has_low = len(low_res) > 0
    return {
        "in_super_ofertas": False,
        "collection_index": 0,
        "total_variants": len(variants) if variants else 1,
        "total_images": len(images) if images else len(p.get("cdn_images") or p.get("gallery") or []),
        "has_unlinked_variants": has_null,
        "unlinked_variants": unlinked_vars,
        "has_duplicate_images": has_dup,
        "duplicate_images": dups,
        "has_low_res_images": has_low,
        "low_res_images": low_res,
        "needs_media_fix": has_null or has_dup or has_low
    }


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

        # Se for brk_fishing, garantir que todos os 91 produtos da coleção Super Ofertas constem no banco
        so_audit = load_super_ofertas_audit() if store_norm == "brk_fishing" else {}
        existing_ids = {str(p.get("id", "")) for p in products}
        if store_norm == "brk_fishing" and so_audit:
            for pid, so_entry in so_audit.items():
                if pid not in existing_ids:
                    products.append({
                        "id": int(pid) if pid.isdigit() else pid,
                        "handle": so_entry.get("handle", ""),
                        "title": so_entry.get("title", ""),
                        "vendor": so_entry.get("vendor", "BRK Fishing"),
                        "category": "Iscas Artificiais" if "isca" in so_entry.get("title", "").lower() else "Equipamentos de Pesca",
                        "master_sku": so_entry.get("master_sku", f"ID-{pid}"),
                        "variants_skus": so_entry.get("variants_skus", []),
                        "cdn_images": so_entry.get("cdn_images", []),
                        "gallery": so_entry.get("cdn_images", []),
                        "image": (so_entry.get("cdn_images") or [""])[0],
                        "body_html": so_entry.get("body_html", ""),
                        "status": "SAUDAVEL",
                        "in_super_ofertas": True
                    })

        # Criar índices em memória com avaliação estrita de diretrizes
        by_id = {}
        by_handle = {}
        by_sku = {}
        outdated_mode_b_list = []
        empty_list = []
        broken_list = []
        legacy_list = []
        compliant_list = []
        super_ofertas_list = []

        for p in products:
            p_id = str(p.get("id", ""))
            p_handle = str(p.get("handle", "")).lower()
            p_sku = str(p.get("master_sku") or p.get("sku") or "").upper()

            if store_norm == "brk_fishing" and p_id in so_audit:
                so_entry = so_audit[p_id]
                p["in_super_ofertas"] = True
                p["super_ofertas_index"] = so_entry.get("index", 999)
                if so_entry.get("cdn_images"):
                    p["cdn_images"] = so_entry["cdn_images"]
                    p["gallery"] = so_entry["cdn_images"]
                if so_entry.get("handle"):
                    p["handle"] = so_entry["handle"]
                    p_handle = so_entry["handle"].lower()
                super_ofertas_list.append(p)

            p["media_audit"] = audit_live_gallery_and_variants(p)

            is_comp, g_status, g_reason = evaluate_guideline_compliance(p, store_norm)
            p["is_mode_b_compliant"] = is_comp
            p["guideline_status"] = g_status
            p["guideline_reason"] = g_reason

            if p_id:
                by_id[p_id] = p
            if p_handle:
                by_handle[p_handle] = p
            if p_sku:
                by_sku[p_sku] = p

            if g_status == "MODO_B_DESATUALIZADO":
                outdated_mode_b_list.append(p)
            elif g_status == "SEM_DESCRICAO":
                empty_list.append(p)
            elif g_status == "IMAGENS_QUEBRADAS":
                broken_list.append(p)
            elif g_status == "FORA_PADRAO_MODO_B":
                legacy_list.append(p)
            else:
                compliant_list.append(p)

        super_ofertas_list.sort(key=lambda x: x.get("super_ofertas_index", 999))

        # Fila prioritária de itens fora das diretrizes (exclui 100% os itens já CONFORME_MODO_B)
        non_compliant_list = outdated_mode_b_list + empty_list + broken_list + legacy_list

        store_pack = {
            "products": products,
            "by_id": by_id,
            "by_handle": by_handle,
            "by_sku": by_sku,
            "outdated_mode_b": outdated_mode_b_list,
            "empty": empty_list,
            "broken": broken_list,
            "legacy": legacy_list,
            "compliant": compliant_list,
            "non_compliant": non_compliant_list,
            "super_ofertas": super_ofertas_list,
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

    # Se já tem o formato oficial correspondente e atualizado (Fase 5/6/7/8), verifica saúde de imagens e reaproveita
    engine, builder = get_engine_and_builder()
    if raw_b and len(raw_b.strip()) > 500 and "<!-- BRK-MODO-B" in raw_b and "use-brk-images-s3" not in raw_b and "troca descomplicada" not in raw_b.lower() and "dinheiro de volta" not in raw_b.lower() and "BRK-MODO-B v1" not in raw_b:
        img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw_b, re.I)
        img_roots = [u.split("?")[0].lower() for u in img_srcs]
        has_dup_imgs = len(img_roots) != len(set(img_roots))
        if not has_dup_imgs and engine and hasattr(engine, "KNOWN_SHOPIFY_DUP_IMAGE_TOKENS"):
            has_dup_imgs = any(tok in u for u in img_roots for tok in engine.KNOWN_SHOPIFY_DUP_IMAGE_TOKENS)
        has_store_color = any(c in raw_b for c in expected_theme_marker)
        sku_low = sku_str.lower()
        has_mfk75t_violation = ("fillet" in title_l or "mfk75t" in title_l or "79081379076" in sku_low) and "bainha" in raw_b.lower()
        if not has_dup_imgs and not has_mfk75t_violation:
            if is_cap_or_hat:
                if "brk-cap-description" in raw_b and has_store_color:
                    return raw_b
            elif not is_uv:
                if has_store_color:
                    return raw_b
            else:
                has_new_sg = any(term in raw_b for term in ["49,5 cm", "Baby Look", "2 Anos", "1 a 2 Anos", "brk-sg-subtitle"]) and "ALTURA" in raw_b and "Tabela de Medidas de Luvas" not in raw_b and (not ("casal" in title_l and ("kit" in title_l or "combo" in title_l)) or "Kit Casal" in raw_b)
                is_ready = engine.is_ready_delivery(p) if engine else False
                expected_prazo = "Pronta entrega" if is_ready else "10 dias úteis"
                has_correct_prazo = expected_prazo in raw_b

                is_fusion_or_hyb = "fusion" in title_l or "fusion" in sku_low or "hybrid" in title_l or sku_low.startswith("hyb")
                has_no_zipper_violation = not is_fusion_or_hyb or (not bool(re.search(r'\b(zíper|ziper)\b', raw_b, re.I)))
                has_hood_sg_note = not is_fusion_or_hyb or ("sem contar" in raw_b.lower())

                if "Detalhes Técnicos" in raw_b and has_new_sg and has_correct_prazo and has_no_zipper_violation and has_hood_sg_note and has_store_color:
                    return raw_b

    engine, builder = get_engine_and_builder()
    if engine and builder:
        try:
            detected_arch = arch_id or engine.detect_archetype(
                p.get("title", ""), p.get("category", ""), p.get("tags", []), vendor=p.get("vendor", ""), sku=sku_str
            )
            p["archetype_id"] = detected_arch
            p["archetype_name"] = engine.templates.get(detected_arch, {}).get("name", "Modo B")
            raw_images = p.get("images") or p.get("gallery") or p.get("cdn_images") or []
            images = engine._sanitize_and_dedup_images(raw_images, archetype_id=detected_arch, title=p.get("title", ""))
            p["cdn_images"] = images
            p["gallery"] = images
            narrative = engine.generate_narrative_from_template(p, detected_arch, images, store_key=store_key)
            compiled_b = builder.build_shopify_html(narrative)
            p["mode_b_html"] = compiled_b
            return compiled_b
        except Exception as e:
            print(f"[-] Erro na compilação do Modo B para {p.get('id')}: {e}")

    # Fallback apenas se a compilação falhar (sempre limpando eventual Troca Descomplicada residual)
    fb_html = p.get("mode_b_html") or p.get("body_html") or ""
    if "troca descomplicada" in fb_html.lower() or "dinheiro de volta" in fb_html.lower():
        fb_html = re.sub(
            r'\s*<div class="brk-trust-item">\s*<span class="brk-trust-[^"]*">.*?</span>\s*<div>\s*<div class="brk-trust-title">Troca Descomplicada</div>\s*<div class="brk-trust-desc">Satisfação garantida ou seu dinheiro de volta</div>\s*</div>\s*</div>',
            "",
            fb_html,
            flags=re.S | re.I
        )
        fb_html = re.sub(
            r"(\.brk-desc-trust-bar\s*\{[^}]*?)grid-template-columns:\s*repeat\(3,\s*1fr\);",
            r"\1grid-template-columns: repeat(2, 1fr);",
            fb_html,
            flags=re.S
        )
    return fb_html

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
    has_size_guide = '<div class="brk-size-guide">' in mode_b
    delivery_time = "Pronta entrega" if "Pronta entrega" in mode_b else "10 dias úteis"
    is_comp, g_status, g_reason = evaluate_guideline_compliance(p, store_key)
    media_audit = p.get("media_audit") or audit_live_gallery_and_variants(p)
    return {
        "id": str(p.get("id", "")),
        "handle": p.get("handle", ""),
        "master_sku": p.get("master_sku") or p.get("sku") or "",
        "title": p.get("title", "Sem Título"),
        "category": p.get("category") or "Geral",
        "status": p.get("status", "SAUDAVEL"),
        "is_mode_b_compliant": is_comp,
        "guideline_status": g_status,
        "guideline_reason": g_reason,
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
        "in_super_ofertas": bool(p.get("in_super_ofertas") or media_audit.get("in_super_ofertas")),
        "media_audit": media_audit,
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
        exclude_raw = (qs.get("exclude_ids") or [""])[0]
        excluded_tokens = {tok.strip().upper() for tok in exclude_raw.split(",") if tok.strip()}

        # ---------------------------------------------------------------------
        # 1. Consulta de Fila para Automação em Lote (Action = queue)
        #    Suporta Lote Geral, Categorias e Coleções Específicas (ex: Super Ofertas 🔥)
        # ---------------------------------------------------------------------
        if action == "queue":
            status_filter = (qs.get("status") or ["FORA_DIRETRIZES"])[0].upper()
            category_filter = (qs.get("category") or ["ALL"])[0].strip()
            collection_raw = (qs.get("collection") or [""])[0].strip()
            try:
                limit = int((qs.get("limit") or ["25"])[0])
            except ValueError:
                limit = 25

            # Normalizar handle de coleção caso venha URL completa
            col_handle = collection_raw
            if "/collections/" in col_handle:
                col_handle = col_handle.split("/collections/")[-1].split("?")[0].split("/")[0].strip()
            col_handle_low = urllib.parse.unquote(col_handle).lower() if hasattr(urllib, "parse") else col_handle.lower()

            is_super_ofertas = (
                category_filter.lower() == "super_ofertas"
                or "super-ofertas" in col_handle_low
                or "super_ofertas" in col_handle_low
            )
            is_tracked_outside_so = (
                category_filter.lower() in ("rastreados_camisas", "rastreados_fora_so")
                or status_filter == "RASTREADOS_TROCA_DESCOMPLICADA"
            )

            collection_pool = None
            if is_tracked_outside_so and store_key == "brk_fishing":
                collection_pool = []
                for tid in TRACKED_OUTSIDE_SUPER_OFERTAS_IDS:
                    tp = db["by_id"].get(tid)
                    if tp:
                        collection_pool.append(tp)
            elif is_super_ofertas and store_key == "brk_fishing":
                collection_pool = list(db.get("super_ofertas") or [])
            elif col_handle:
                store_domains_map = {
                    "brk_fishing": "https://www.brkfishing.com.br",
                    "brk_agro": "https://www.brkagro.com.br",
                    "brk_motors": "https://www.brkmotors.com.br"
                }
                base_u = store_domains_map.get(store_key, "https://www.brkfishing.com.br")
                try:
                    encoded_col = urllib.parse.quote(col_handle, safe="-_%")
                    req_c = urllib.request.Request(
                        f"{base_u}/collections/{encoded_col}/products.json?limit=250",
                        headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req_c, timeout=7) as resp_c:
                        live_col_prods = json.loads(resp_c.read().decode("utf-8")).get("products", [])
                        collection_pool = []
                        for lp in live_col_prods:
                            lp_id = str(lp.get("id", ""))
                            db_p = db["by_id"].get(lp_id)
                            if db_p:
                                db_p["media_audit"] = audit_live_gallery_and_variants(lp if not db_p.get("in_super_ofertas") else db_p)
                                collection_pool.append(db_p)
                            else:
                                variants = lp.get("variants") or []
                                v_skus = [str(v.get("sku") or "").strip() for v in variants if v.get("sku")]
                                master_s = v_skus[0].split("-")[0] if v_skus else f"ID-{lp_id}"
                                dedup_imgs = [img.get("src") if isinstance(img, dict) else img for img in (lp.get("images") or []) if img]
                                body_h = (lp.get("body_html") or "").strip()
                                new_p = {
                                    "id": lp.get("id"),
                                    "handle": lp.get("handle", ""),
                                    "title": lp.get("title", ""),
                                    "vendor": lp.get("vendor", "BRK"),
                                    "master_sku": master_s,
                                    "variants_skus": v_skus,
                                    "body_html": body_h,
                                    "status": "SEM_DESCRICAO" if len(re.sub(r"<[^>]+>", "", body_h).strip()) < 20 else "SAUDAVEL",
                                    "cdn_images": dedup_imgs,
                                    "gallery": dedup_imgs,
                                    "image": dedup_imgs[0] if dedup_imgs else "",
                                    "variants": variants,
                                    "images": lp.get("images") or []
                                }
                                is_c, g_st, g_rs = evaluate_guideline_compliance(new_p, store_key)
                                new_p["is_mode_b_compliant"] = is_c
                                new_p["guideline_status"] = g_st
                                new_p["guideline_reason"] = g_rs
                                new_p["media_audit"] = audit_live_gallery_and_variants(new_p)
                                collection_pool.append(new_p)
                except Exception as ex:
                    print(f"[!] Falha ao buscar coleção ao vivo '{col_handle}': {ex}")
                    collection_pool = []

            media_status_filters = {
                "COLECAO_COMPLETA",
                "RASTREADOS_TROCA_DESCOMPLICADA",
                "AJUSTE_FOTOS_GERAL",
                "CRITICOS_FOTOS_CORES",
                "COR_SEM_FOTO",
                "FOTOS_DUPLICADAS",
                "FOTOS_BAIXA_QUALIDADE"
            }

            if collection_pool is not None:
                base_pool = collection_pool
            elif status_filter in media_status_filters:
                base_pool = db.get("super_ofertas") or db["products"]
            elif status_filter in ("CRITICOS_LOJA", "PRIORIDADE_CRITICA"):
                base_pool = db["outdated_mode_b"] + db["empty"] + db["broken"]
            elif status_filter == "MODO_B_DESATUALIZADO":
                base_pool = db["outdated_mode_b"]
            elif status_filter == "SEM_DESCRICAO":
                base_pool = db["empty"]
            elif status_filter == "IMAGENS_QUEBRADAS":
                base_pool = db["broken"]
            elif status_filter == "FORA_PADRAO_MODO_B":
                base_pool = db["legacy"]
            else:
                base_pool = db["non_compliant"]

            # Aplicar filtro de status (Diretrizes Modo B ou Auditoria Visual de Fotos/Variantes)
            pool = []
            for p in base_pool:
                pid_u = str(p.get("id", "")).upper()
                sku_u = str(p.get("master_sku") or p.get("sku") or "").upper()
                if pid_u in excluded_tokens or (sku_u and sku_u in excluded_tokens):
                    continue

                ma = p.get("media_audit") or {}
                if status_filter in ("COLECAO_COMPLETA", "RASTREADOS_TROCA_DESCOMPLICADA") or is_tracked_outside_so:
                    pool.append(p)
                elif status_filter == "AJUSTE_FOTOS_GERAL":
                    if ma.get("needs_media_fix"):
                        pool.append(p)
                elif status_filter == "CRITICOS_FOTOS_CORES":
                    if ma.get("has_unlinked_variants") or ma.get("has_duplicate_images"):
                        pool.append(p)
                elif status_filter == "COR_SEM_FOTO":
                    if ma.get("has_unlinked_variants"):
                        pool.append(p)
                elif status_filter == "FOTOS_DUPLICADAS":
                    if ma.get("has_duplicate_images"):
                        pool.append(p)
                elif status_filter == "FOTOS_BAIXA_QUALIDADE":
                    if ma.get("has_low_res_images"):
                        pool.append(p)
                elif status_filter in ("CRITICOS_LOJA", "PRIORIDADE_CRITICA"):
                    if p.get("guideline_status") in ("MODO_B_DESATUALIZADO", "SEM_DESCRICAO", "IMAGENS_QUEBRADAS") and not p.get("is_mode_b_compliant", False):
                        pool.append(p)
                elif status_filter in ("MODO_B_DESATUALIZADO", "SEM_DESCRICAO", "IMAGENS_QUEBRADAS", "FORA_PADRAO_MODO_B"):
                    if p.get("guideline_status") == status_filter and not p.get("is_mode_b_compliant", False):
                        pool.append(p)
                else:
                    # FORA_DIRETRIZES: retorna apenas os produtos que não estão 100% conformes com o Modo B v5
                    if not p.get("is_mode_b_compliant", False):
                        pool.append(p)

            # Aplicar filtro de categoria (exceto quando category_filter == super_ofertas ou rastreados_camisas, já resolvido em collection_pool)
            if category_filter and category_filter.upper() not in ("ALL", "SUPER_OFERTAS", "RASTREADOS_CAMISAS", "RASTREADOS_FORA_SO"):
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
                    elif cat_l == "iscas_artificiais":
                        if p_arch == "fishing_lures" or "isca" in p_title or "isca" in p_cat:
                            filtered_pool.append(p)
                    elif cat_l == "equipamentos_pesca":
                        if p_arch in ("fishing_tackle_gear", "tackle_boxes_storage") or any(w in p_title or w in p_cat for w in ["vara", "carretilha", "molinete", "alicate", "caixa", "estojo", "maleta"]):
                            filtered_pool.append(p)
                    elif cat_l == "linhas_pesca":
                        if "linha" in p_title or "linha" in p_cat or "multifilamento" in p_title or "monofilamento" in p_title or "fluorcarbono" in p_title:
                            filtered_pool.append(p)
                    elif cat_l in p_cat or cat_l in p_arch:
                        filtered_pool.append(p)
                pool = filtered_pool

            batch = pool[:limit]
            sanitized_batch = [sanitize_product(p, store_key) for p in batch]
            non_compliant_codes = [
                {
                    "id": str(p.get("id", "")),
                    "sku": str(p.get("master_sku") or p.get("sku") or f"ID-{p.get('id', '')}"),
                    "title": p.get("title", ""),
                    "guideline_status": p.get("guideline_status", "FORA_PADRAO_MODO_B"),
                    "guideline_reason": p.get("guideline_reason", ""),
                    "needs_media_fix": bool((p.get("media_audit") or {}).get("needs_media_fix")),
                    "has_unlinked_variants": bool((p.get("media_audit") or {}).get("has_unlinked_variants")),
                    "has_duplicate_images": bool((p.get("media_audit") or {}).get("has_duplicate_images")),
                    "has_low_res_images": bool((p.get("media_audit") or {}).get("has_low_res_images"))
                }
                for p in pool[:95]
            ]

            return self._respond_json(200, {
                "success": True,
                "store": store_key,
                "status_filter": status_filter,
                "category_filter": category_filter,
                "collection_filter": col_handle or ("super-ofertas-🔥" if is_super_ofertas else ""),
                "total_available": len(pool),
                "compliant_excluded_count": len(db["compliant"]),
                "count": len(sanitized_batch),
                "non_compliant_codes": non_compliant_codes,
                "items": sanitized_batch
            }, cache_control="no-store" if excluded_tokens else "public, s-maxage=60")

        # ---------------------------------------------------------------------
        # 2. Estatísticas do Banco de Dados e Mapa de Códigos Fora das Diretrizes (Action = stats)
        # ---------------------------------------------------------------------
        if action == "stats":
            cat_counts = {}
            for p in db["products"]:
                c = p.get("category") or "Geral"
                cat_counts[c] = cat_counts.get(c, 0) + 1
            active_non_compliant = [
                p for p in db["non_compliant"]
                if str(p.get("id", "")).upper() not in excluded_tokens
                and str(p.get("master_sku") or p.get("sku") or "").upper() not in excluded_tokens
            ]
            pending_by_group = {
                "camisas": 0,
                "bones_chapeus": 0,
                "iscas_artificiais": 0,
                "equipamentos_pesca": 0,
                "calcas": 0,
                "corta_vento": 0,
                "infantil": 0,
                "feminino": 0
            }
            for p in active_non_compliant:
                p_cat = str(p.get("category") or "").lower()
                p_arch = str(p.get("archetype_id") or "").lower()
                p_title = str(p.get("title") or "").lower()
                if p_arch in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy") or "boné" in p_cat or "chapéu" in p_cat or "boné" in p_title or "chapéu" in p_title:
                    pending_by_group["bones_chapeus"] += 1
                if "camisa" in p_cat or p_arch in ("uv_performance", "casual_cotton", "casual_lifestyle", "button_shirts_work"):
                    pending_by_group["camisas"] += 1
                if "calça" in p_cat or "bermuda" in p_cat or p_arch == "pants_tactical":
                    pending_by_group["calcas"] += 1
                if "corta" in p_cat or "jaqueta" in p_cat or "moletom" in p_cat or p_arch in ("windbreaker_jacket", "hoodie_fleece"):
                    pending_by_group["corta_vento"] += 1
                if any(w in p_title for w in ["infantil", "kids", "juvenil", "junior"]):
                    pending_by_group["infantil"] += 1
                if any(w in p_title for w in ["feminina", "feminino", "baby look", "babylook"]):
                    pending_by_group["feminino"] += 1
                if p_arch == "fishing_lures" or "isca" in p_title or "isca" in p_cat:
                    pending_by_group["iscas_artificiais"] += 1
                if p_arch in ("fishing_tackle_gear", "tackle_boxes_storage") or any(w in p_title or w in p_cat for w in ["vara", "carretilha", "molinete", "alicate", "caixa", "estojo", "maleta"]):
                    pending_by_group["equipamentos_pesca"] += 1

            so_list = db.get("super_ofertas") or []
            so_stats = {
                "total": len(so_list),
                "needs_media_fix": sum(1 for p in so_list if (p.get("media_audit") or {}).get("needs_media_fix")),
                "unlinked_variants": sum(1 for p in so_list if (p.get("media_audit") or {}).get("has_unlinked_variants")),
                "duplicate_images": sum(1 for p in so_list if (p.get("media_audit") or {}).get("has_duplicate_images")),
                "low_res_images": sum(1 for p in so_list if (p.get("media_audit") or {}).get("has_low_res_images")),
            }
            non_compliant_codes = [
                {
                    "id": str(p.get("id", "")),
                    "sku": str(p.get("master_sku") or p.get("sku") or f"ID-{p.get('id', '')}"),
                    "title": p.get("title", ""),
                    "guideline_status": p.get("guideline_status", "FORA_PADRAO_MODO_B"),
                    "guideline_reason": p.get("guideline_reason", "")
                }
                for p in active_non_compliant[:120]
            ]
            comp_cnt = len(db["compliant"]) + (len(db["non_compliant"]) - len(active_non_compliant))
            out_cnt = len([p for p in db["outdated_mode_b"] if str(p.get("id", "")).upper() not in excluded_tokens])
            emp_cnt = len([p for p in db["empty"] if str(p.get("id", "")).upper() not in excluded_tokens])
            brk_cnt = len([p for p in db["broken"] if str(p.get("id", "")).upper() not in excluded_tokens])
            leg_cnt = len([p for p in db["legacy"] if str(p.get("id", "")).upper() not in excluded_tokens])
            progress_pct = round((comp_cnt / max(1, db["total"])) * 100, 1)

            return self._respond_json(200, {
                "success": True,
                "store": store_key,
                "store_theme": STORE_THEME_METADATA.get(store_key, STORE_THEME_METADATA["brk_fishing"]),
                "total_products": db["total"],
                "compliant_count": comp_cnt,
                "non_compliant_count": len(active_non_compliant),
                "progress_pct": progress_pct,
                "criticos_loja_count": out_cnt + emp_cnt + brk_cnt,
                "modo_b_desatualizado_count": out_cnt,
                "sem_descricao_count": emp_cnt,
                "imagens_quebradas_count": brk_cnt,
                "fora_padrao_modo_b_count": leg_cnt,
                "healthy_count": db["total"] - len(db["empty"]) - len(db["broken"]),
                "pending_by_group": pending_by_group,
                "super_ofertas_stats": so_stats,
                "non_compliant_codes": non_compliant_codes,
                "categories": cat_counts
            }, cache_control="no-store" if excluded_tokens else "public, s-maxage=60")

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
                engine_inst, _ = get_engine_and_builder()
                if engine_inst:
                    dedup_imgs = engine_inst._sanitize_and_dedup_images(live_p.get("images") or [], title=live_p.get("title", ""))
                else:
                    dedup_imgs = [img.get("src") if isinstance(img, dict) else img for img in (live_p.get("images") or []) if img]
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
                                engine_inst, _ = get_engine_and_builder()
                                if engine_inst:
                                    dedup_imgs = engine_inst._sanitize_and_dedup_images(
                                        live_data["images"],
                                        archetype_id=found_product.get("archetype_id", "uv_performance"),
                                        title=live_data.get("title") or found_product.get("title", "")
                                    )
                                else:
                                    dedup_imgs = [img.get("src") if isinstance(img, dict) else img for img in live_data["images"] if img]
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
