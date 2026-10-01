"""
Configurações para o ecossistema de Auditoria e Automação Shopify.
Suporta múltiplos sites com foco inicial na BRK Fishing.
"""

from typing import Dict, Any

# Configurações dos Sites Monitorados (Ambientes Isolados)
STORES: Dict[str, Dict[str, Any]] = {
    "brk_fishing": {
        "id": "brk_fishing",
        "name": "BRK Fishing",
        "domain": "www.brkfishing.com.br",
        "base_url": "https://www.brkfishing.com.br",
        "products_endpoint": "https://www.brkfishing.com.br/products.json",
        "category_focus": "vestuario_pesca",
        "output_dir": "reports/brk_fishing",
        "theme_color": "#0284c7"
    },
    "brk_agro": {
        "id": "brk_agro",
        "name": "BRK Agro",
        "domain": "www.brkagro.com.br",
        "base_url": "https://www.brkagro.com.br",
        "products_endpoint": "https://www.brkagro.com.br/products.json",
        "category_focus": "agro_pecuaria",
        "output_dir": "reports/brk_agro",
        "theme_color": "#16a34a"
    },
    "brk_motors": {
        "id": "brk_motors",
        "name": "BRK Motors",
        "domain": "www.brkmotors.com.br",
        "base_url": "https://www.brkmotors.com.br",
        "products_endpoint": "https://www.brkmotors.com.br/products.json",
        "category_focus": "motors_offroad",
        "output_dir": "reports/brk_motors",
        "theme_color": "#dc2626"
    },
    # Alias de compatibilidade
    "brk": {
        "id": "brk_fishing",
        "name": "BRK Fishing",
        "domain": "www.brkfishing.com.br",
        "base_url": "https://www.brkfishing.com.br",
        "products_endpoint": "https://www.brkfishing.com.br/products.json",
        "category_focus": "vestuario_pesca",
        "output_dir": "reports/brk_fishing",
        "theme_color": "#0284c7"
    }
}

# Parâmetros de Requisição e Rate Limiting
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
}

REQUEST_TIMEOUT = 15  # segundos
REQUEST_DELAY = 0.5   # delay entre páginas para não sobrecarregar o servidor

# Critérios do Algoritmo de Score de Conversão (0 a 100)
SCORE_WEIGHTS = {
    "missing_body": -100,         # Sem descrição = nota 0
    "broken_image_penalty": -30,  # Cada imagem com link quebrado (404/inacessível)
    "external_host_penalty": -15, # Imagens fora do CDN Shopify (risco de quebra)
    "min_word_count": 50,         # Menos de 50 palavras = penalização
    "short_text_penalty": -25,
    "missing_tech_specs": -15,    # Ausência de especificações técnicas / tecido
    "missing_sizing": -10,        # Roupas sem guia de medidas
}
