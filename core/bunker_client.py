"""
Módulo de Integração e Normalização de Mídias do BRK Bunker.
Suporta validação de URLs geradas pelo Cloudflare Worker (brk-bunker.allexadriel.workers.dev)
e autenticação HTTP Basic opcional caso credenciais sejam fornecidas.
"""

import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

class BunkerClient:
    def __init__(self, username: Optional[str] = "E-COMMERCE", password: Optional[str] = None):
        self.base_url = "https://brk-bunker.allexadriel.workers.dev"
        self.username = username
        self.password = password

    def is_bunker_url(self, url: str) -> bool:
        """Verifica se a URL pertence à infraestrutura do BRK Bunker."""
        if not url:
            return False
        return "brk-bunker" in url or "workers.dev" in url or "r2.dev" in url or "cloudflare" in url

    def parse_links_text(self, raw_text: str) -> List[str]:
        """
        Extrai URLs de um bloco de texto colado (suporta quebras de linha, vírgulas, espaços).
        """
        if not raw_text:
            return []
        
        # Regex para capturar URLs HTTP/HTTPS
        url_pattern = re.compile(r'https?://[^\s,;"\'<>]+', re.IGNORECASE)
        found = url_pattern.findall(raw_text)
        
        # Remove caracteres indesejados no final da URL
        cleaned = [u.rstrip('.,;)]}') for u in found]
        # Dedup preservando ordem
        seen = set()
        result = []
        for u in cleaned:
            if u not in seen:
                seen.add(u)
                result.append(u)
        return result

    def distribute_to_3_acts(self, urls: List[str]) -> Dict[str, str]:
        """
        Distribui ordenadamente as URLs nas 3 posições narrativas:
        - act1: Hero / Design & Visual
        - act2: Performance / Tecnologia UV & Conforto
        - act3: Durabilidade / Acabamento & Confiança
        """
        if not urls:
            return {"act1": "", "act2": "", "act3": ""}
        
        u1 = urls[0]
        u2 = urls[1] if len(urls) > 1 else u1
        u3 = urls[2] if len(urls) > 2 else (urls[1] if len(urls) > 1 else u1)

        return {
            "act1": u1,
            "act2": u2,
            "act3": u3
        }

    def generate_responsive_media_tag(self, url: str, alt_text: str = "Detalhe Oficial BRK Bunker") -> str:
        """
        Gera tag HTML responsiva blindada para as fotos do Bunker.
        """
        return (
            f'<div class="brk-bunker-media" style="margin: 24px auto; text-align: center; max-width: 850px;">'
            f'<img src="{url}" alt="{alt_text}" '
            f'style="max-width: 100%; height: auto; max-height: 520px; border-radius: 12px; box-shadow: 0 4px 14px rgba(15,23,42,0.08); object-fit: contain; display: inline-block;" '
            f'loading="lazy" />'
            f'</div>'
        )
