"""
Sincronizador Automático de Produtos Recentes (BRK Fishing, Agro, Motors).
Consulta /products.json?limit=50 das 3 lojas, detecta novas fotos ou alterações
e atualiza tanto os catálogos fonte (reports/.../catalog_ui_data.json) quanto
os bancos compilados (data/stores/*.json), recompilando narrative_blocks e mode_b_html.
"""

import urllib.request
import json
import os
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
        "raw_file": os.path.join(BASE_DIR, "reports", "catalog_ui_data.json"),
    },
    {
        "key": "brk_agro",
        "name": "BRK Agro",
        "url": "https://www.brkagro.com.br",
        "file": os.path.join(BASE_DIR, "data", "stores", "brk_agro.json"),
        "raw_file": os.path.join(BASE_DIR, "reports", "brk_agro", "catalog_ui_data.json"),
    },
    {
        "key": "brk_motors",
        "name": "BRK Motors",
        "url": "https://www.brkmotors.com.br",
        "file": os.path.join(BASE_DIR, "data", "stores", "brk_motors.json"),
        "raw_file": os.path.join(BASE_DIR, "reports", "brk_motors", "catalog_ui_data.json"),
    },
]


def sync_recent():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando varredura de produtos recentes na vitrine...")
    total_updated = 0
    engine = TemplateEngine()
    builder = HTMLBuilder()
    replacer = HTMLReplacer()

    for st in STORES:
        file_path = st["file"]
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

        # Buscar últimos 50 produtos alterados na Shopify
        url = f"{st['url']}/products.json?limit=50"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                live_prods = json.loads(resp.read().decode("utf-8")).get("products", [])
        except Exception as e:
            print(f"  [!] Erro ao consultar {st['name']}: {e}")
            continue

        store_updates = 0
        for lp in live_prods:
            handle = lp.get("handle")
            pid = str(lp.get("id"))
            existing = by_handle.get(handle) or by_id.get(pid)
            raw_existing = raw_by_handle.get(handle) or raw_by_id.get(pid)

            if not existing:
                continue

            live_images = [img.get("src") if isinstance(img, dict) else img for img in lp.get("images", []) if img]
            curr_images = existing.get("cdn_images") or existing.get("gallery") or []

            # Se a lista de fotos mudou ou foi reordenada na Shopify
            if live_images and live_images != curr_images:
                existing["images"] = live_images
                existing["cdn_images"] = live_images
                existing["gallery"] = live_images
                existing["image"] = live_images[0]

                # Recompilar narrativa e HTML imediatamente
                title = existing.get("title", "")
                category = existing.get("category", "")
                tags = existing.get("tags", [])
                vendor = existing.get("vendor", "")
                sku_code = existing.get("master_sku") or existing.get("sku") or ""
                arch_id = existing.get("archetype_id") or engine.detect_archetype(title, category, tags, vendor=vendor, sku=sku_code)
                orig_html = existing.get("original_body_html") or existing.get("body_html") or ""

                narrative = engine.generate_narrative_from_template(existing, arch_id, live_images, store_key=st["key"])
                existing["narrative_blocks"] = narrative["narrative_blocks"]
                existing["specs"] = narrative["specs"]
                existing["split_images"] = narrative.get("split_images")
                existing["mode_a_html"] = replacer.replace_images_preserve_html(orig_html, live_images, title)
                existing["mode_b_html"] = builder.build_shopify_html(narrative)
                existing["mode_b_markdown"] = builder.build_shopify_markdown(narrative)

                if raw_existing is not None:
                    raw_existing["gallery"] = live_images
                    raw_existing["cdn_images"] = live_images
                    raw_existing["image"] = live_images[0]
                    raw_existing["images_count"] = len(live_images)

                store_updates += 1

        if store_updates > 0:
            print(f"  -> {st['name']}: {store_updates} produto(s) com fotos atualizadas!")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(store_data, f, ensure_ascii=False, indent=2)
            if raw_data is not None:
                with open(raw_path, "w", encoding="utf-8") as rf:
                    json.dump(raw_data, rf, ensure_ascii=False, indent=2)
            total_updated += store_updates
        else:
            print(f"  -> {st['name']}: Todas as fotos já sincronizadas.")

    print(f"[CONCLUÍDO] Total de produtos atualizados com fotos novas: {total_updated}")
    return total_updated


if __name__ == "__main__":
    count = sync_recent()
    if count > 0:
        print("[TRIGGER] Produtos atualizados e recompilados nos catálogos fonte e lojas.")
