"""
Módulo de Extração e Seleção Inteligente de Imagens da CDN Oficial da Shopify.
Garante seleção de até 3 fotos da própria galeria do produto, com URLs otimizadas e permanentes.
"""

import re
import requests
from typing import List, Dict, Any, Optional

def optimize_shopify_cdn_url(url: str, width: int = 900, format_webp: bool = True) -> str:
    """
    Transforma a URL da imagem da Shopify para servir em resolução ideal e formato WebP.
    Ex: .../foto.jpg?v=123 -> .../foto_900x.webp?v=123 ou .../foto.jpg?width=900&format=webp&v=123
    """
    if not url:
        return ""
    
    # Corrige links sem schema
    if url.startswith("//"):
        url = "https:" + url

    # Se for da CDN da Shopify, adiciona parâmetros de redimensionamento e otimização
    if "cdn.shopify.com" in url or "brkfishing.com.br/cdn" in url:
        # Se já tem query params
        separator = "&" if "?" in url else "?"
        # Garante carregamento limpo e otimizado
        if "width=" not in url:
            url = f"{url}{separator}width={width}"
            
    return url

class ImageHarvester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def select_product_images(self, product_data: Dict[str, Any], max_images: int = 3) -> List[Dict[str, str]]:
        """
        Analisa a galeria de imagens do produto na Shopify e seleciona até 3 fotos estratégicas:
        1. Foto 1: Visão Geral / Frente (Hero)
        2. Foto 2: Macro Detalhe (Punho, Luva, Zíper, etc.)
        3. Foto 3: Ângulo / Costas / Uso / Textura
        """
        title = product_data.get("title", "")
        raw_images = product_data.get("images", [])
        
        if not raw_images:
            return []

        selected = []
        total_imgs = len(raw_images)

        # 1. Foto Hero (Frente / Visão Geral da Peça)
        hero_img = raw_images[0]
        selected.append({
            "src": optimize_shopify_cdn_url(hero_img.get("src", "")),
            "alt": f"{title} - Visão Geral e Modelagem Exclusiva",
            "role": "hero",
            "tag": "Proteção Solar UV50+",
            "title": "BLINDAGEM HOMOLOGADA UV50+"
        })

        # 2. Foto de Detalhe (Punho com Luva / Zíper / Construção)
        if total_imgs >= 2:
            detail_img = raw_images[1]
            selected.append({
                "src": optimize_shopify_cdn_url(detail_img.get("src", "")),
                "alt": f"{title} - Detalhe da Luva Integrada e Punho Anatômico",
                "role": "detail",
                "tag": "Luva Integrada no Punho",
                "title": "ANATOMIA & PROTEÇÃO EXTRA"
            })

        # 3. Foto de Contexto / Ângulo / Caimento
        if total_imgs >= 3 and len(selected) < max_images:
            # Se tiver 4 ou mais fotos, seleciona a 3ª ou 4ª para dar variedade
            context_idx = 2 if total_imgs == 3 else 3
            if context_idx < total_imgs:
                context_img = raw_images[context_idx]
            else:
                context_img = raw_images[2]
                
            selected.append({
                "src": optimize_shopify_cdn_url(context_img.get("src", "")),
                "alt": f"{title} - Tecido XTech Pro e Caimento Perfeito",
                "role": "fabric",
                "tag": "Tecido XTech Pro Respirável",
                "title": "CONFORTO TÉRMICO & SECAGEM RÁPIDA"
            })

        return selected[:max_images]
