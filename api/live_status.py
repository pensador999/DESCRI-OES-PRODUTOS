"""
Vercel Serverless Function: Agente de Verificacao ao Vivo (somente leitura).

Le a VITRINE PUBLICA de cada loja (https://<dominio>/products.json) - sem token, sem Admin -
e classifica a descricao atual (body_html) de cada produto publicado:

  SEM_DESCRICAO           vazio / placeholder (ex.: "A")
  IMAGENS_QUEBRADAS       links de imagens mortas (S3 antigo / photobucket)
  COLADO_ATUAL            Modo B com marcador de rastreio na versao vigente
  COLADO_DESATUALIZADO    Modo B com marcador de versao anterior (precisa recolar)
  COLADO_SEM_MARCADOR     Modo B antigo (layout BRK) colado antes do rastreio existir
  SAUDAVEL                descricao legada sem erro critico

Uso: GET /api/live_status?store=brk_fishing|brk_agro|brk_motors&from=1&to=5  (&t=<n> ignora o cache)
`from`/`to` = intervalo de paginas de 250 produtos (o front pede 3 blocos em paralelo para caber no
limite de tempo da Vercel). Sem from/to, le todas as paginas (MAX_PAGES).
Nunca escreve na Shopify.
"""

from http.server import BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import json
import re
import urllib.request

# Deve ser igual a core/html_builder.py::MODO_B_VERSION (um teste garante a paridade).
MODO_B_VERSION = "2"

PUBLIC_DOMAINS = {
    "brk_fishing": "www.brkfishing.com.br",
    "brk_agro": "www.brkagro.com.br",
    "brk_motors": "www.brkmotors.com.br",
}

MAX_PAGES = 14          # 14 x 250 = 3.500 produtos por loja
PAGE_SIZE = 250
TIMEOUT = 9

MARKER_RE = re.compile(r"<!--\s*BRK-MODO-B\s+v(\d+)\s*\|\s*sku:([^|]*?)\s*\|\s*molde:([^\s>]*)\s*-->", re.I)
BROKEN_RE = re.compile(r"use-brk-images-s3|photobucket", re.I)
PROHIBITED_RE = re.compile(r"use-brk-images-s3|drive\.google|mercadolivre|shopee|photobucket", re.I)
PLACEHOLDERS = ("a", "p", "br", "-", ".", "none", "null", "undefined")


def classify(body_html: str) -> dict:
    """Classifica uma descricao. Funcao pura (testavel sem rede)."""
    body = (body_html or "").strip()
    text = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = len(text.split()) if text else 0
    low = body.lower()

    marker = MARKER_RE.search(body)
    out = {"w": words, "pl": sorted({m.lower() for m in PROHIBITED_RE.findall(body)})}
    if marker:
        out["v"] = marker.group(1)
        out["sku"] = marker.group(2).strip()
        out["molde"] = marker.group(3).strip()

    is_empty = (
        not body
        or words == 0
        or text.lower() in PLACEHOLDERS
        or (words < 20 and not any(t in low for t in ("<table", "<div", "<ul")))
        or words < 5
    )
    if is_empty:
        out["s"] = "SEM_DESCRICAO"
    elif BROKEN_RE.search(body):
        out["s"] = "IMAGENS_QUEBRADAS"
    elif marker:
        has_violation = (
            ("troca descomplicada" in low or "dinheiro de volta" in low)
            or ("tabela de medidas de luvas" in low and any(w in low for w in ("camisa", "armorx", "sku:cax")))
            or ("tabela de medidas adulto (p ao exg)" in low)
            or ("bainha" in low and any(w in low for w in ("mfk75t", "79081379076", "fillet knife")))
            or (any(w in low for w in ("fusionx", "sku:fusion", "sku:hyb", "brk hybrid")) and "sem contar" not in low)
            or ("eqxquy7.jpg" in low and "sku:ba09" not in low)
        )
        if marker.group(1) != MODO_B_VERSION or has_violation:
            out["s"] = "COLADO_DESATUALIZADO"
        else:
            out["s"] = "COLADO_ATUAL"
    elif "brk-desc-wrapper" in low:
        if "troca descomplicada" in low or "dinheiro de volta" in low:
            out["s"] = "COLADO_DESATUALIZADO"
        else:
            out["s"] = "COLADO_SEM_MARCADOR"
    else:
        out["s"] = "SAUDAVEL"
    return out


def _fetch_page(domain: str, page: int):
    url = f"https://{domain}/products.json?limit={PAGE_SIZE}&page={page}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (BRK-LiveStatus/1.0)", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8")).get("products", [])


def build_live_status(store_key: str, p_from: int = 1, p_to: int = MAX_PAGES) -> dict:
    domain = PUBLIC_DOMAINS[store_key]
    items, errors = {}, []
    p_from = max(1, p_from)
    p_to = min(MAX_PAGES, max(p_from, p_to))
    with ThreadPoolExecutor(max_workers=p_to - p_from + 1) as ex:
        futs = {p: ex.submit(_fetch_page, domain, p) for p in range(p_from, p_to + 1)}
        for page, fut in futs.items():
            try:
                for prod in fut.result():
                    c = classify(prod.get("body_html"))
                    c["u"] = prod.get("updated_at")
                    items[prod.get("handle")] = c
            except Exception as e:  # pagina falhou: reporta, nao derruba
                errors.append(f"page {page}: {e}")
    return {
        "store": store_key,
        "domain": domain,
        "pages": [p_from, p_to],
        "current_version": MODO_B_VERSION,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "errors": errors,
        "items": items,
    }


class handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict, cache: str = "no-store"):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        store = (qs.get("store") or [""])[0]
        if store not in PUBLIC_DOMAINS:
            return self._send(400, {"error": "Parametro 'store' invalido", "allowed": list(PUBLIC_DOMAINS)})
        try:
            p_from = int((qs.get("from") or ["1"])[0])
            p_to = int((qs.get("to") or [str(MAX_PAGES)])[0])
        except ValueError:
            return self._send(400, {"error": "'from'/'to' devem ser inteiros"})
        try:
            data = build_live_status(store, p_from, p_to)
        except Exception as e:
            return self._send(502, {"error": str(e)})
        # Blocos alem do fim do catalogo voltam vazios (count 0) - e valido; so erro de rede e 502.
        if data["count"] == 0 and data["errors"]:
            return self._send(502, {"error": "Vitrine inacessivel", "details": data["errors"]})
        self._send(200, data, cache="public, s-maxage=120, stale-while-revalidate=300")
