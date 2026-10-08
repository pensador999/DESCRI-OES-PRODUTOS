"""
Ponte de Sincronizacao Direta com o Admin da Shopify (core/shopify_direct_sync.py).
Permite atualizar cirurgicamente e em lote as descricoes dos produtos nas 3 lojas BRK:
- BRK Fishing (use-brk-fishing.myshopify.com)
- BRK Agro (use-brk-agro.myshopify.com)
- BRK Motors (use-brk-motors.myshopify.com)

Suporta execucao em Dry-Run, controle estrito de rate-limiting (leaky bucket da Shopify),
e compilacao automatica do Padrao Oficial Modo B (com Badges Rapidos, 3 Atos, Tabela de Medidas e Schema SEO).
"""

import os
import sys
import json
import time
import re
import argparse
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from datetime import datetime

# Assegurar UTF-8 no terminal Windows para evitar UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Assegurar path do projeto para importacao dos modulos core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder

STORE_DOMAINS = {
    "brk_fishing": "use-brk-fishing.myshopify.com",
    "brk_agro": "use-brk-agro.myshopify.com",
    "brk_motors": "use-brk-motors.myshopify.com"
}

ENV_TOKEN_KEYS = {
    "brk_fishing": "SHOPIFY_FISHING_TOKEN",
    "brk_agro": "SHOPIFY_AGRO_TOKEN",
    "brk_motors": "SHOPIFY_MOTORS_TOKEN"
}

class ShopifyDirectSync:
    def __init__(self, dry_run: bool = True, delay: float = 0.5):
        self.dry_run = dry_run
        self.delay = delay
        self.template_engine = TemplateEngine()
        self.html_builder = HTMLBuilder()

    def get_token(self, store_key: str, token_override: Optional[str] = None) -> Optional[str]:
        if token_override:
            return token_override
        env_key = ENV_TOKEN_KEYS.get(store_key, "")
        return os.getenv(env_key)

    def load_store_products_from_js(self, store_key: str) -> List[Dict[str, Any]]:
        """Carrega os produtos do arquivo JS modularizado em data/stores/{store_key}.js"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        js_path = os.path.join(base_dir, "data", "stores", f"{store_key}.js")
        if not os.path.exists(js_path):
            print(f"[-] Arquivo de dados nao encontrado: {js_path}")
            return []

        try:
            with open(js_path, "r", encoding="utf-8") as f:
                content = f.read()

            raw_json = content.split("=", 1)[1].strip()
            if raw_json.endswith(";"):
                raw_json = raw_json[:-1].strip()

            parsed = json.loads(raw_json)
            if isinstance(parsed, dict) and "products" in parsed:
                return parsed["products"]
            elif isinstance(parsed, list):
                return parsed
            else:
                print(f"[-] Estrutura inesperada em {js_path}")
                return []
        except Exception as e:
            print(f"[-] Erro ao carregar produtos de {store_key}: {e}")
            return []

    def update_product_body_html(self, store_key: str, product_id: Any, new_html: str, access_token: str, max_retries: int = 3) -> Dict[str, Any]:
        """Executa a requisicao PUT REST para atualizar body_html na Shopify Admin API com protecao contra rate-limit (429)"""
        if self.dry_run:
            return {"success": True, "dry_run": True, "product_id": product_id}

        domain = STORE_DOMAINS[store_key]
        clean_id = str(product_id).replace("gid://shopify/Product/", "")
        endpoint = f"https://{domain}/admin/api/2024-01/products/{clean_id}.json"

        payload = {
            "product": {
                "id": int(clean_id),
                "body_html": new_html
            }
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": access_token
            },
            method="PUT"
        )

        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    return {"success": True, "data": resp_data, "product_id": product_id}
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    retry_after = float(e.headers.get("Retry-After", 2.0 * (attempt + 1)))
                    print(f"      [!] Rate-limit 429 atingido na Shopify API. Pausando {retry_after}s antes da tentativa {attempt+2}/{max_retries}...")
                    time.sleep(retry_after)
                    continue
                err_body = e.read().decode("utf-8") if e.fp else ""
                return {"success": False, "status_code": e.code, "error": err_body, "product_id": product_id}
            except Exception as e:
                return {"success": False, "error": str(e), "product_id": product_id}

        return {"success": False, "status_code": 429, "error": "Excedido limite de tentativas por Rate Limit (429)", "product_id": product_id}

    def sync_store(self, store_key: str, limit: Optional[int] = None, token_override: Optional[str] = None) -> Dict[str, Any]:
        """Sincroniza um catalogo completo ou limitado de uma loja"""
        print(f"\n=======================================================")
        print(f"[*] INICIANDO SINCRONIZACAO DIRETA: {store_key.upper()}")
        print(f"[*] Modo: {'DRY-RUN (Simulacao sem alteracao)' if self.dry_run else 'PRODUCAO (Gravacao ativa na Shopify)'}")
        print(f"=======================================================")

        token = self.get_token(store_key, token_override)
        if not self.dry_run and not token:
            print(f"[!] ERRO: Token de acesso para '{store_key}' nao configurado!")
            print(f"    Defina a variavel de ambiente {ENV_TOKEN_KEYS.get(store_key)} ou passe via --token")
            return {"success": False, "error": "Token ausente"}

        products = self.load_store_products_from_js(store_key)
        if not products:
            print(f"[-] Nenhum produto carregado para {store_key}")
            return {"success": False, "error": "Nenhum produto encontrado"}

        if limit and limit > 0:
            products = products[:limit]
            print(f"[*] Limite aplicado: {limit} produto(s)")

        total = len(products)
        updated_count = 0
        error_count = 0
        results = []

        start_time = time.time()

        for idx, prod in enumerate(products, 1):
            p_id = prod.get("id")
            p_title = prod.get("title", "Sem Titulo")
            p_handle = prod.get("handle", "")

            # 1. Compilar Modo B Oficial (com Badges Rapidos, Tabela de Medidas e Schema)
            try:
                vendor = prod.get("vendor", "")
                sku_code = prod.get("master_sku") or prod.get("sku") or (prod.get("variants_skus") and prod.get("variants_skus")[0]) or ""
                arch_id = prod.get("archetype_id") or self.template_engine.detect_archetype(
                    p_title, str(prod.get("product_type", "")), str(prod.get("tags", "")), vendor=vendor, sku=sku_code
                )
                raw_imgs = prod.get("cdn_images") or prod.get("gallery") or [img.get("src", img) if isinstance(img, dict) else img for img in prod.get("images", [])]
                cdn_imgs = [u for u in raw_imgs if isinstance(u, str) and u.startswith("http")]

                enriched = self.template_engine.generate_narrative_from_template(
                    prod, arch_id, cdn_imgs, store_key=store_key
                )
                mode_b_html = self.html_builder.build_shopify_html(enriched)

                # 2. Executar sincronizacao
                res = self.update_product_body_html(store_key, p_id, mode_b_html, token or "")
                if res.get("success"):
                    updated_count += 1
                    status_icon = "🧪 [DRY-RUN]" if self.dry_run else "✅ [OK]"
                    print(f"[{idx}/{total}] {status_icon} ID {p_id} | {p_title[:45]}...")
                else:
                    error_count += 1
                    print(f"[{idx}/{total}] ❌ [ERRO] ID {p_id} | {res.get('error')}")

                results.append(res)

                # Rate-limiting pause
                if not self.dry_run:
                    time.sleep(self.delay)

            except Exception as e:
                error_count += 1
                print(f"[{idx}/{total}] ❌ [FALHA] ID {p_id}: {e}")
                results.append({"success": False, "product_id": p_id, "error": str(e)})

        elapsed = time.time() - start_time
        summary = {
            "store_key": store_key,
            "dry_run": self.dry_run,
            "total_processed": total,
            "success_count": updated_count,
            "error_count": error_count,
            "elapsed_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat()
        }

        print(f"\n[+] Sincronizacao de {store_key} finalizada em {elapsed:.1f}s.")
        print(f"    Sucesso: {updated_count}/{total} | Erros: {error_count}/{total}")
        return summary

def main():
    parser = argparse.ArgumentParser(description="Ponte de Sincronizacao Direta de Descricoes com Shopify Admin API")
    parser.add_argument("--store", type=str, default="brk_fishing", choices=["brk_fishing", "brk_agro", "brk_motors", "all"], help="Loja alvo")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Executar em modo simulacao sem alterar produtos")
    parser.add_argument("--production", action="store_true", default=False, help="Executar alteracoes reais na Shopify")
    parser.add_argument("--limit", type=int, default=None, help="Limite de produtos para processar")
    parser.add_argument("--delay", type=float, default=0.5, help="Intervalo em segundos entre chamadas API (padrao: 0.5s)")
    parser.add_argument("--token", type=str, default=None, help="Token de acesso Shopify para sobrescrever variavel de ambiente")

    args = parser.parse_args()

    # Por seguranca, se nao especificar --production, roda em dry-run
    is_dry_run = not args.production

    syncer = ShopifyDirectSync(dry_run=is_dry_run, delay=args.delay)

    stores_to_sync = list(STORE_DOMAINS.keys()) if args.store == "all" else [args.store]

    reports = []
    for s in stores_to_sync:
        report = syncer.sync_store(s, limit=args.limit, token_override=args.token)
        reports.append(report)

    # Salvar log da sessao
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file = os.path.join(reports_dir, f"sync_report_{int(time.time())}.json")

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Relatorio completo salvo em: {report_file}")

if __name__ == "__main__":
    main()
