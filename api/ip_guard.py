"""
Guardião de Acesso por Senha do Sistema BRK (api/ip_guard.py).
O bloqueio por IP foi substituído pela autenticação por senha ('rex123').
"""

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler

SYSTEM_PASSWORD = "rex123"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        pwd = (params.get("password", [""])[0] or "").strip().lower()

        authorized = (pwd == SYSTEM_PASSWORD)

        payload = {
            "auth_mode": "password",
            "authorized": authorized,
            "message": "Autenticado via senha BRK" if authorized else "Digite a senha de acesso para entrar"
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
