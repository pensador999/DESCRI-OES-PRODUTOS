"""
Vercel Serverless Function: Proxy Seguro para Shopify Admin API.
Permite atualizar EXCLUSIVAMENTE o campo 'body_html' (descrição) de um produto na loja Shopify correta.
Elimina problemas de CORS e mantém os tokens de acesso 100% seguros nas variáveis de ambiente da Vercel.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

# Mapeamento estrito de lojas permitidas
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

class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def _respond_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Status health-check do endpoint"""
        configured_stores = {}
        for s_key, env_var in ENV_TOKEN_KEYS.items():
            configured_stores[s_key] = bool(os.getenv(env_var))

        self._respond_json(200, {
            "service": "BRK Shopify Direct API",
            "status": "online",
            "configured_stores": configured_stores,
            "instruction": "Envie um POST com {'store_key': '...', 'product_id': '...', 'body_html': '...'}"
        })

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._respond_json(400, {"success": False, "error": "Corpo da requisição vazio."})
                return

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))

            store_key = payload.get("store_key")
            product_id = payload.get("product_id")
            body_html = payload.get("body_html")

            # 1. Validação de Parâmetros
            if not store_key or store_key not in STORE_DOMAINS:
                self._respond_json(400, {
                    "success": False,
                    "error": f"Loja inválida: '{store_key}'. Lojas permitidas: {list(STORE_DOMAINS.keys())}"
                })
                return

            if not product_id:
                self._respond_json(400, {"success": False, "error": "Campo 'product_id' obrigatório."})
                return

            if body_html is None:
                self._respond_json(400, {"success": False, "error": "Campo 'body_html' obrigatório."})
                return

            # 2. Obtenção do Token de Acesso Seguro via Variáveis de Ambiente
            env_var_name = ENV_TOKEN_KEYS[store_key]
            access_token = os.getenv(env_var_name)
            if not access_token:
                self._respond_json(503, {
                    "success": False,
                    "error": (
                        f"Variável de ambiente '{env_var_name}' não configurada na Vercel. "
                        f"Configure o token de acesso da loja {store_key} no painel da Vercel (Project Settings > Environment Variables)."
                    )
                })
                return

            domain = STORE_DOMAINS[store_key]
            clean_product_id = str(product_id).strip()

            # 3. Blindagem de Escopo: Apenas o campo body_html é alterado (Shopify REST API)
            shopify_url = f"https://{domain}/admin/api/2024-01/products/{clean_product_id}.json"
            update_payload = {
                "product": {
                    "id": int(clean_product_id),
                    "body_html": body_html
                }
            }

            req = urllib.request.Request(
                shopify_url,
                data=json.dumps(update_payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "X-Shopify-Access-Token": access_token,
                    "User-Agent": "BRK-Catalog-Sync/1.0"
                },
                method="PUT"
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                resp_body = response.read().decode('utf-8')
                resp_json = json.loads(resp_body)
                product_data = resp_json.get("product", {})

                self._respond_json(200, {
                    "success": True,
                    "message": f"Descrição do produto {clean_product_id} atualizada com sucesso na loja {store_key}!",
                    "product_id": product_data.get("id"),
                    "title": product_data.get("title"),
                    "updated_at": product_data.get("updated_at")
                })

        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8') if hasattr(he, 'read') else str(he)
            self._respond_json(he.code, {
                "success": False,
                "error": f"Erro retornado pela Shopify API ({he.code}): {err_body}"
            })
        except Exception as e:
            self._respond_json(500, {
                "success": False,
                "error": f"Erro interno ao processar sincronização: {str(e)}"
            })
