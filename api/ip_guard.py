"""
Guardiao de Acesso por IP da Maquina Autorizada (api/ip_guard.py).
Verifica se o IP publico do visitante (via x-forwarded-for / x-real-ip na Vercel)
pertence a maquina autorizada do projeto BRK.
"""

import json
import os
from http.server import BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHITELIST_PATH = os.path.join(BASE_DIR, "data", "stores", "ip_whitelist.json")

DEFAULT_WHITELIST = {
    "allowed_ips": [
        "104.28.199.94",
        "104.28.199.96",
        "2a09:bac5:779:2555::3b8:7a",
        "127.0.0.1",
        "::1"
    ],
    "allowed_prefixes": [
        "104.28.199.",
        "104.28.",
        "2a09:bac5:779:2555:"
    ]
}


def load_whitelist():
    if os.path.exists(WHITELIST_PATH):
        try:
            with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return DEFAULT_WHITELIST


def is_ip_authorized(client_ip: str, wl: dict) -> bool:
    if not client_ip:
        return False
    ip_clean = client_ip.strip().lower()
    allowed_ips = [str(x).strip().lower() for x in wl.get("allowed_ips", [])]
    allowed_prefixes = [str(x).strip().lower() for x in wl.get("allowed_prefixes", [])]

    if ip_clean in allowed_ips:
        return True
    for pfx in allowed_prefixes:
        if pfx and ip_clean.startswith(pfx):
            return True
    return False


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        wl = load_whitelist()
        xff = self.headers.get("x-forwarded-for", "")
        x_real = self.headers.get("x-real-ip", "")
        raw_ip = (xff.split(",")[0].strip() if xff else "") or x_real.strip() or self.client_address[0]

        authorized = is_ip_authorized(raw_ip, wl)

        payload = {
            "authorized": authorized,
            "client_ip": raw_ip,
            "machine": "BRK Master Workstation (Lucas Lima)" if authorized else "Unauthorized Host"
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
