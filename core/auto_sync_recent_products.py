"""
Sincronizador Automático de Produtos Recentes (BRK Fishing, Agro, Motors).
Consulta /products.json?limit=50&order=updated_at+desc das 3 lojas,
detecta novas fotos ou alterações e atualiza data/stores/*.json.
"""

import urllib.request
import json
import os
import sys
from datetime import datetime

STORES = [
    {"key": "brk_fishing", "name": "BRK Fishing", "url": "https://www.brkfishing.com.br", "file": "data/stores/brk_fishing.json"},
    {"key": "brk_agro", "name": "BRK Agro", "url": "https://www.brkagro.com.br", "file": "data/stores/brk_agro.json"},
    {"key": "brk_motors", "name": "BRK Motors", "url": "https://www.brkmotors.com.br", "file": "data/stores/brk_motors.json"}
]

def sync_recent():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando varredura de produtos recentes na vitrine...")
    total_updated = 0

    for st in STORES:
        file_path = st["file"]
        if not os.path.exists(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            store_data = json.load(f)

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

            if not existing:
                continue

            live_images = [img.get("src") if isinstance(img, dict) else img for img in lp.get("images", []) if img]
            curr_images = existing.get("cdn_images") or existing.get("gallery") or []

            # Se a lista de fotos mudou ou foi reordenada na Shopify
            if live_images and live_images != curr_images:
                existing["images"] = lp.get("images", [])
                existing["cdn_images"] = live_images
                existing["gallery"] = live_images
                existing["split_images"] = live_images
                existing["mode_b_html"] = ""  # Re-gerar na próxima compilação
                store_updates += 1

        if store_updates > 0:
            print(f"  -> {st['name']}: {store_updates} produto(s) com fotos atualizadas!")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(store_data, f, ensure_ascii=False)
            total_updated += store_updates
        else:
            print(f"  -> {st['name']}: Todas as fotos já sincronizadas.")

    print(f"[CONCLUÍDO] Total de produtos atualizados com fotos novas: {total_updated}")
    return total_updated

if __name__ == "__main__":
    count = sync_recent()
    if count > 0:
        print("[TRIGGER] Produtos atualizados. Recompilar com build_modular_dist.py se necessário.")
