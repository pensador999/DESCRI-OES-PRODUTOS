"""
Módulo de Sincronização em Tempo Real (Por Segundos) para Shopify BRK Group.
Monitora os endpoints públicos da Shopify das 3 lojas a cada X segundos:
- Detecta produtos recém-criados que estão sem descrição (SEM_DESCRICAO) ou com links quebrados da AWS.
- Injeta automaticamente nos arquivos de cache locais (reports/catalog_ui_data.json, etc.).
- Permite execução sob demanda (--once) ou contínua como daemon (--daemon).
"""

import os
import sys
import json
import time
import urllib.request
from typing import Dict, Any, List

STORES_CONFIG = {
    "brk_fishing": {
        "name": "BRK Fishing",
        "domain": "www.brkfishing.com.br",
        "color": "#0284c7",
        "cache_file": "reports/catalog_ui_data.json"
    },
    "brk_agro": {
        "name": "BRK Agro",
        "domain": "www.brkagro.com.br",
        "color": "#16a34a",
        "cache_file": "reports/brk_agro/catalog_ui_data.json"
    },
    "brk_motors": {
        "name": "BRK Motors",
        "domain": "www.brkmotors.com.br",
        "color": "#f97316",
        "cache_file": "reports/brk_motors/catalog_ui_data.json"
    }
}

class RealtimeSync:
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def fetch_recent_products(self, domain: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Busca os produtos mais recentes da Shopify via API JSON pública."""
        url = f"https://{domain}/products.json?limit={limit}&t={int(time.time())}"
        headers = {
            "User-Agent": "BRK-RealtimeSentinel/2.0",
            "Accept": "application/json"
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data.get("products", [])
        except Exception as e:
            print(f"[ALERTA] Erro ao consultar {domain}: {e}")
        return []

    def sync_store(self, store_key: str, limit: int = 30) -> Dict[str, Any]:
        """Sincroniza produtos recentes de uma loja com o cache local."""
        cfg = STORES_CONFIG.get(store_key)
        if not cfg:
            return {"error": "Loja inválida"}

        domain = cfg["domain"]
        cache_path = os.path.join(self.base_dir, cfg["cache_file"])
        
        # Carregar cache existente
        catalog_data = {"store": {}, "categories": {}, "products": []}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    catalog_data = json.load(f)
            except Exception:
                pass

        known_ids = {p.get("id") for p in catalog_data.get("products", []) if p.get("id")}
        recent_prods = self.fetch_recent_products(domain, limit=limit)

        new_items = []
        updated_items = 0

        for p in recent_prods:
            pid = p.get("id")
            raw_html = p.get("body_html") or ""
            is_empty = not raw_html or raw_html.strip() in ("", "<p></p>", "<p>&nbsp;</p>")
            
            if pid not in known_ids:
                # Novo produto adicionado na Shopify!
                images = [img["src"] for img in p.get("images", []) if img.get("src")]
                variants = p.get("variants", [])
                master_sku = variants[0].get("sku") if variants else f"BRK-{pid}"
                variant_skus = [v.get("sku") for v in variants if v.get("sku")]

                new_entry = {
                    "id": pid,
                    "title": p.get("title", ""),
                    "handle": p.get("handle", ""),
                    "vendor": p.get("vendor", ""),
                    "url": f"https://{domain}/products/{p.get('handle', '')}",
                    "master_sku": master_sku,
                    "variants_skus": variant_skus,
                    "total_skus_count": len(variants),
                    "affected_skus_count": len(variants) if is_empty else 0,
                    "status": "SEM_DESCRICAO" if is_empty else "SAUDAVEL",
                    "is_out_of_standard": is_empty,
                    "image": images[0] if images else "",
                    "gallery": images,
                    "cdn_images": images[:3],
                    "body_html": raw_html,
                    "original_body_html": raw_html,
                    "category": "Recém-Adicionados" if is_empty else "Geral",
                    "tags": p.get("tags", []),
                    "created_at": p.get("created_at", "")
                }
                catalog_data["products"].insert(0, new_entry)
                new_items.append(new_entry)
                known_ids.add(pid)
            else:
                # Verificar se produto existente estava sem descrição e agora foi atualizado
                for existing in catalog_data["products"]:
                    if existing.get("id") == pid:
                        if is_empty and existing.get("status") != "SEM_DESCRICAO":
                            existing["status"] = "SEM_DESCRICAO"
                            existing["is_out_of_standard"] = True
                            updated_items += 1
                        break

        if new_items or updated_items:
            # Salvar cache
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(catalog_data, f, ensure_ascii=False, indent=2)
            print(f"[SYNC] {cfg['name']}: {len(new_items)} novo(s) produto(s) adicionados ao cache!")

        return {
            "store": store_key,
            "domain": domain,
            "new_count": len(new_items),
            "updated_count": updated_items,
            "total_cached": len(catalog_data["products"])
        }

    def sync_all_stores(self) -> Dict[str, Any]:
        """Sincroniza as 3 lojas simultaneamente."""
        results = {}
        for s_key in STORES_CONFIG.keys():
            results[s_key] = self.sync_store(s_key)
        return results

    def run_daemon(self, interval_seconds: int = 15):
        """Executa loop de sincronização por segundos."""
        print(f"[*] Vigilante de Tempo Real iniciado. Checagem a cada {interval_seconds}s...")
        try:
            while True:
                results = self.sync_all_stores()
                total_new = sum(r.get("new_count", 0) for r in results.values())
                if total_new > 0:
                    print(f"[REBUILD] {total_new} novos produtos detectados! Recompilando portal...")
                    from build_master_index import build_master
                    build_master()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[STOP] Vigilante de Tempo Real finalizado.")

def main():
    sync = RealtimeSync()
    if "--daemon" in sys.argv:
        interval = 15
        for arg in sys.argv:
            if arg.startswith("--interval="):
                try:
                    interval = int(arg.split("=")[1])
                except ValueError:
                    pass
        sync.run_daemon(interval_seconds=interval)
    else:
        print("[*] Executando sincronização pontual das 3 lojas...")
        res = sync.sync_all_stores()
        for k, v in res.items():
            print(f" - {k}: {v['new_count']} novos produtos detectados ({v['total_cached']} totais no cache)")

if __name__ == "__main__":
    main()
