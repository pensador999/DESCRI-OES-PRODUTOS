"""
Sincronizador Automático de Produtos Recentes (BRK Fishing, Agro, Motors).
Consulta /products.json?limit=250 das 3 lojas, detecta produtos novos, novas fotos
ou descrições atualizadas na vitrine e sincroniza tanto os catálogos fonte
(reports/.../catalog_ui_data.json) quanto os bancos compilados (data/stores/*.json e .js).
"""

import urllib.request
import json
import os
import re
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder
from core.html_replacer import HTMLReplacer

STORES = [
    {
        "key": "brk_fishing",
        "name": "BRK Fishing",
        "url": "https://www.brkfishing.com.br",
        "file": os.path.join(BASE_DIR, "data", "stores", "brk_fishing.json"),
        "js_file": os.path.join(BASE_DIR, "data", "stores", "brk_fishing.js"),
        "js_var": "__STORE_BRK_FISHING",
        "raw_file": os.path.join(BASE_DIR, "reports", "catalog_ui_data.json"),
    },
    {
        "key": "brk_agro",
        "name": "BRK Agro",
        "url": "https://www.brkagro.com.br",
        "file": os.path.join(BASE_DIR, "data", "stores", "brk_agro.json"),
        "js_file": os.path.join(BASE_DIR, "data", "stores", "brk_agro.js"),
        "js_var": "__STORE_BRK_AGRO",
        "raw_file": os.path.join(BASE_DIR, "reports", "brk_agro", "catalog_ui_data.json"),
    },
    {
        "key": "brk_motors",
        "name": "BRK Motors",
        "url": "https://www.brkmotors.com.br",
        "file": os.path.join(BASE_DIR, "data", "stores", "brk_motors.json"),
        "js_file": os.path.join(BASE_DIR, "data", "stores", "brk_motors.js"),
        "js_var": "__STORE_BRK_MOTORS",
        "raw_file": os.path.join(BASE_DIR, "reports", "brk_motors", "catalog_ui_data.json"),
    },
]

DEAD_BODY_RE = re.compile(r"use-brk-images-s3|photobucket|imageshack|tinytake|yampi", re.IGNORECASE)


def _evaluate_status(body_html: str) -> tuple:
    body = (body_html or "").strip()
    clean_b = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
    clean_b = re.sub(r"<[^>]+>", " ", clean_b).strip()
    clean_b = re.sub(r"\s+", " ", clean_b)
    w_count = len(clean_b.split()) if clean_b else 0
    is_empty = (
        not body
        or w_count == 0
        or clean_b.lower() in ("a", "p", "br", "-", ".", "none", "null", "undefined")
        or (w_count < 20 and not any(t in body.lower() for t in ("<table", "<div", "<ul")))
        or w_count < 5
    )
    if DEAD_BODY_RE.search(body):
        return "IMAGENS_QUEBRADAS", True, w_count
    if is_empty:
        return "SEM_DESCRICAO", True, w_count
    return "SAUDAVEL", False, w_count


def _extract_dedup_images(lp: dict) -> list:
    raw = [img.get("src") if isinstance(img, dict) else img for img in lp.get("images", []) if img]
    seen = set()
    out = []
    for u in raw:
        if not u or not isinstance(u, str):
            continue
        clean_u = u.strip()
        if not clean_u:
            continue
        root = clean_u.split("?")[0].lower()
        if root not in seen:
            seen.add(root)
            out.append(clean_u)
    return out


def sync_recent():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando varredura de produtos recentes na vitrine...")
    total_updated = 0
    engine = TemplateEngine()
    builder = HTMLBuilder()
    replacer = HTMLReplacer()

    for st in STORES:
        file_path = st["file"]
        js_path = st["js_file"]
        raw_path = st["raw_file"]
        if not os.path.exists(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            store_data = json.load(f)

        raw_data = None
        raw_by_handle = {}
        raw_by_id = {}
        if os.path.exists(raw_path):
            try:
                with open(raw_path, "r", encoding="utf-8") as rf:
                    raw_data = json.load(rf)
                raw_prods = raw_data.get("products", [])
                raw_by_handle = {p.get("handle"): p for p in raw_prods if p.get("handle")}
                raw_by_id = {str(p.get("id")): p for p in raw_prods if p.get("id")}
            except Exception:
                raw_data = None

        products = store_data.get("products", [])
        by_handle = {p.get("handle"): p for p in products if p.get("handle")}
        by_id = {str(p.get("id")): p for p in products if p.get("id")}

        # Buscar últimos 250 produtos da vitrine na Shopify
        url = f"{st['url']}/products.json?limit=250"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                live_prods = json.loads(resp.read().decode("utf-8")).get("products", [])
        except Exception as e:
            print(f"  [!] Erro ao consultar {st['name']}: {e}")
            continue

        store_updates = 0
        for lp in live_prods:
            handle = lp.get("handle")
            pid = str(lp.get("id"))
            live_images = _extract_dedup_images(lp)
            if not handle or not live_images:
                continue

            existing = by_handle.get(handle) or by_id.get(pid)
            raw_existing = raw_by_handle.get(handle) or raw_by_id.get(pid)
            live_body = (lp.get("body_html") or "").strip()

            if existing:
                curr_images = existing.get("cdn_images") or existing.get("gallery") or []
                curr_body = (existing.get("original_body_html") or existing.get("body_html") or "").strip()
                images_changed = (live_images != curr_images)
                body_changed = (live_body != curr_body)

                if images_changed or body_changed:
                    existing["cdn_images"] = live_images
                    existing["gallery"] = live_images
                    existing["image"] = live_images[0]
                    existing["body_html"] = live_body

                    status, is_out, w_count = _evaluate_status(live_body)
                    existing["status"] = status
                    existing["is_out_of_standard"] = is_out
                    existing["word_count"] = w_count

                    title = existing.get("title", "")
                    tags = existing.get("tags", [])
                    vendor = existing.get("vendor", "")
                    sku_code = existing.get("master_sku") or existing.get("sku") or ""
                    arch_id = engine.detect_archetype(title, existing.get("category", ""), tags, vendor=vendor, sku=sku_code)
                    cat_name = engine.classify_store_category(title, arch_id, store_key=st["key"], tags=tags, sku=sku_code)
                    existing["archetype_id"] = arch_id
                    existing["category"] = cat_name

                    narrative = engine.generate_narrative_from_template(existing, arch_id, live_images, store_key=st["key"])
                    existing["narrative_blocks"] = narrative["narrative_blocks"]
                    existing["specs"] = narrative["specs"]
                    existing["split_images"] = narrative.get("split_images")
                    existing["mode_a_html"] = replacer.replace_images_preserve_html(live_body, live_images, title)
                    if status == "SEM_DESCRICAO" or arch_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
                        existing["mode_b_html"] = builder.build_shopify_html(narrative)
                        existing["mode_b_markdown"] = builder.build_shopify_markdown(narrative)
                    else:
                        existing["mode_b_html"] = ""
                        existing["mode_b_markdown"] = ""

                    if raw_existing is not None:
                        raw_existing["gallery"] = live_images
                        raw_existing["cdn_images"] = live_images
                        raw_existing["image"] = live_images[0]
                        raw_existing["body_html"] = live_body
                        raw_existing["original_body_html"] = live_body
                        raw_existing["status"] = status
                        raw_existing["is_out_of_standard"] = is_out
                        raw_existing["category"] = cat_name

                    store_updates += 1
            else:
                # Novo produto detectado na Shopify! Inserir automaticamente no catálogo
                title = lp.get("title") or ""
                vendor = lp.get("vendor") or st["name"]
                raw_tags = lp.get("tags") or []
                tags = [t.strip() for t in raw_tags.split(",") if t.strip()] if isinstance(raw_tags, str) else list(raw_tags)
                variants = lp.get("variants") or []
                var_skus = [str(v.get("sku")).strip() for v in variants if v.get("sku") and str(v.get("sku")).strip()]
                master_sku = var_skus[0] if var_skus else f"BRK-{pid}"
                if len(master_sku) > 4 and any(c.isdigit() for c in master_sku):
                    m = re.match(r"^([A-Z0-9]+?)(PP|P|M|G|GG|G1|G2|G3|[0-9]{2})?$", master_sku)
                    base_sku = m.group(1) if m else master_sku
                else:
                    base_sku = master_sku
                total_skus = len(var_skus) if var_skus else max(1, len(variants))
                status, is_out, w_count = _evaluate_status(live_body)
                arch_id = engine.detect_archetype(title, lp.get("product_type") or "", tags, vendor=vendor, sku=base_sku)
                arch_info = engine.templates.get(arch_id, engine.templates["uv_performance"])
                cat_name = engine.classify_store_category(title, arch_id, store_key=st["key"], tags=tags, sku=base_sku)

                base_prod = {
                    "id": lp.get("id"),
                    "title": title,
                    "handle": handle,
                    "vendor": vendor,
                    "url": f"{st['url']}/products/{handle}",
                    "master_sku": base_sku,
                    "variants_skus": var_skus,
                    "total_skus_count": total_skus,
                    "affected_skus_count": total_skus if is_out else 0,
                    "is_out_of_standard": is_out,
                    "category": cat_name,
                    "tags": tags,
                    "image": live_images[0],
                    "gallery": live_images,
                    "cdn_images": live_images,
                    "status": status,
                    "word_count": w_count,
                    "body_html": live_body,
                }
                narrative = engine.generate_narrative_from_template(base_prod, arch_id, live_images, store_key=st["key"])
                new_dist_prod = dict(base_prod)
                new_dist_prod["archetype_id"] = arch_id
                new_dist_prod["archetype_name"] = arch_info["name"]
                new_dist_prod["store_key"] = st["key"]
                new_dist_prod["formatted_title"] = narrative.get("formatted_title", title)
                new_dist_prod["brand_name"] = narrative.get("brand_name", "BRK")
                new_dist_prod["origin_type"] = narrative.get("origin_type", "producao_propria")
                new_dist_prod["show_copyright"] = narrative.get("show_copyright", False)
                new_dist_prod["theme_color"] = narrative["theme_color"]
                new_dist_prod["theme_bg"] = narrative["theme_bg"]
                new_dist_prod["care_icon"] = narrative["care_icon"]
                new_dist_prod["narrative_blocks"] = narrative.get("narrative_blocks", [])
                new_dist_prod["care_tips"] = narrative.get("care_tips", "")
                new_dist_prod["specs"] = narrative.get("specs", [])
                new_dist_prod["mode_a_html"] = replacer.replace_images_preserve_html(live_body, live_images, title)
                new_dist_prod["mode_b_html"] = builder.build_shopify_html(narrative) if status == "SEM_DESCRICAO" else ""
                new_dist_prod["mode_b_markdown"] = builder.build_shopify_markdown(narrative) if status == "SEM_DESCRICAO" else ""

                products.insert(0, new_dist_prod)
                by_handle[handle] = new_dist_prod
                by_id[pid] = new_dist_prod

                if raw_data is not None:
                    raw_prod = dict(base_prod)
                    raw_prod["original_body_html"] = live_body
                    raw_data.setdefault("products", []).insert(0, raw_prod)
                    raw_by_handle[handle] = raw_prod
                    raw_by_id[pid] = raw_prod

                store_updates += 1

        if store_updates > 0:
            print(f"  -> {st['name']}: {store_updates} produto(s) novo(s)/atualizado(s)!")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(store_data, f, ensure_ascii=False)
            with open(js_path, "w", encoding="utf-8") as jf:
                jf.write(f"window.{st['js_var']} = " + json.dumps(store_data, ensure_ascii=False) + ";\n")
            if raw_data is not None:
                with open(raw_path, "w", encoding="utf-8") as rf:
                    json.dump(raw_data, rf, ensure_ascii=False, indent=2)
            total_updated += store_updates
        else:
            print(f"  -> {st['name']}: Catálogo e fotos 100% sincronizados.")

    print(f"[CONCLUÍDO] Total de produtos novos/atualizados: {total_updated}")
    return total_updated


if __name__ == "__main__":
    count = sync_recent()
    if count > 0:
        print("[TRIGGER] Produtos sincronizados e recompilados nos catálogos fonte e lojas.")
