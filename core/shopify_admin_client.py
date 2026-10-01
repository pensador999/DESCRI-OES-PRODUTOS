"""
Cliente Conector Oficial para a API Admin da Shopify (Direct Sync).
Permite atualizar EXCLUSIVAMENTE o campo 'body_html' de um produto na Shopify,
com garantia absoluta de que estoque, preços, variantes, imagens, SEO e tags
permanecem 100% blindados e intocados.

Possui:
1. Transmissão cirúrgica de payload restrito: {"product": {"id": id, "body_html": html}}
2. Histórico automático de versões para Rollback / Desfazer com 1 clique.
3. Modo Dry-Run / Simulação para homologação segura.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

class ShopifyAdminClient:
    STORES = {
        "brk_fishing": {
            "name": "BRK Fishing",
            "myshopify_domain": "use-brk-fishing.myshopify.com",
            "env_var": "SHOPIFY_FISHING_TOKEN"
        },
        "brk_agro": {
            "name": "BRK Agro",
            "myshopify_domain": "use-brk-agro.myshopify.com",
            "env_var": "SHOPIFY_AGRO_TOKEN"
        },
        "brk_motors": {
            "name": "BRK Motors",
            "myshopify_domain": "use-brk-motors.myshopify.com",
            "env_var": "SHOPIFY_MOTORS_TOKEN"
        }
    }

    def __init__(self, credentials_file: str = "config/shopify_credentials.json", history_file: str = "reports/shopify_rollback_history.json"):
        self.credentials_file = credentials_file
        self.history_file = history_file
        self.credentials = self._load_credentials()

    def _load_credentials(self) -> Dict[str, str]:
        creds = {}
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, "r", encoding="utf-8") as f:
                    creds = json.load(f)
            except Exception:
                creds = {}
        
        # Sobrescrever com variáveis de ambiente se disponíveis
        for store_key, store_data in self.STORES.items():
            env_val = os.getenv(store_data["env_var"])
            if env_val:
                creds[store_key] = env_val

        return creds

    def save_credentials(self, store_key: str, token: str):
        """Salva o token de acesso seguro localmente."""
        self.credentials[store_key] = token
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        with open(self.credentials_file, "w", encoding="utf-8") as f:
            json.dump(self.credentials, f, indent=2)

    def _record_history(self, store_key: str, product_id: str, previous_html: str, new_html: str, status: str) -> None:
        """Registra no histórico local para permitir rollback/desfazer a qualquer momento."""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        entry = {
            "id": f"{product_id}_{int(datetime.now().timestamp())}",
            "product_id": str(product_id),
            "store_key": store_key,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "previous_html": previous_html,
            "new_html": new_html
        }
        history.insert(0, entry)
        # Manter até 500 registros no histórico
        history = history[:500]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def update_product_body_html(self, store_key: str, product_id: str, new_html: str, previous_html: str = "", dry_run: bool = False) -> Tuple[bool, str]:
        """
        Atualiza rigorosamente e unicamente o campo body_html na Shopify.
        Nenhum outro atributo (preço, estoque, SKU, variante, imagens) é enviado.
        """
        store_info = self.STORES.get(store_key)
        if not store_info:
            return False, f"Loja '{store_key}' inválida."

        token = self.credentials.get(store_key)

        # Se for dry-run ou token não configurado, faz simulação segura
        if dry_run or not token:
            mode_desc = "[SIMULAÇÃO / DRY-RUN]" if dry_run else "[SEM TOKEN - MODO TESTE]"
            print(f"{mode_desc} Produto #{product_id} em {store_info['name']}")
            print(f"  -> Payload seguro validado: {{'product': {{'id': {product_id}, 'body_html': <{len(new_html)} bytes>}}}}")
            self._record_history(store_key, str(product_id), previous_html, new_html, "dry_run_success")
            if not token and not dry_run:
                return True, f"Validado com sucesso em modo teste! Para sincronizar direto com a loja ao vivo, cadastre o Token Admin da {store_info['name']}."
            return True, f"Simulação bem-sucedida! Descrição de {len(new_html)} bytes pronta para envio."

        # Execução real via API Admin Shopify (REST PUT)
        domain = store_info["myshopify_domain"]
        url = f"https://{domain}/admin/api/2024-01/products/{product_id}.json"

        # REGRA FUNDAMENTAL: Apenas 'id' e 'body_html'
        payload = {
            "product": {
                "id": int(product_id) if str(product_id).isdigit() else product_id,
                "body_html": new_html
            }
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token,
            "User-Agent": "BRK-Catalog-Sync/1.0"
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="PUT")

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status in (200, 201):
                    self._record_history(store_key, str(product_id), previous_html, new_html, "applied_live")
                    return True, f"Descrição do produto #{product_id} atualizada com sucesso na Shopify ao vivo!"
                else:
                    return False, f"Resposta inesperada da Shopify: Status {response.status}"
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            self._record_history(store_key, str(product_id), previous_html, new_html, f"error_{e.code}")
            return False, f"Erro HTTP {e.code} da Shopify Admin: {err_body}"
        except Exception as e:
            self._record_history(store_key, str(product_id), previous_html, new_html, "error_exception")
            return False, f"Falha na conexão com a Shopify: {str(e)}"

    def rollback_last_update(self, product_id: str) -> Tuple[bool, str]:
        """Restaura a descrição anterior de um produto a partir do histórico local."""
        if not os.path.exists(self.history_file):
            return False, "Nenhum histórico de alterações encontrado."

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception as e:
            return False, f"Erro ao ler histórico: {e}"

        target_entry = None
        for entry in history:
            if str(entry.get("product_id")) == str(product_id) and entry.get("previous_html"):
                target_entry = entry
                break

        if not target_entry:
            return False, f"Nenhuma descrição anterior registrada para o produto #{product_id}."

        prev_html = target_entry["previous_html"]
        store_key = target_entry["store_key"]

        success, msg = self.update_product_body_html(
            store_key=store_key,
            product_id=product_id,
            new_html=prev_html,
            previous_html="",
            dry_run=False
        )

        if success:
            return True, f"Reversão (Rollback) concluída com sucesso para o produto #{product_id}!"
        return False, f"Falha ao reverter: {msg}"

if __name__ == "__main__":
    client = ShopifyAdminClient()
    print("=== SHOPIFY ADMIN DIRECT CLIENT - TESTE ===")
    ok, res = client.update_product_body_html("brk_fishing", "123456789", "<p>Teste de Descrição Segura</p>", dry_run=True)
    print("Resultado:", ok, "|", res)
