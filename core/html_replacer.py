"""
Módulo de Substituição Cirúrgica de Imagens e Preservação de HTML (Modo A).
Preserva 100% do texto original, parágrafos e tabelas do produto,
substituindo apenas as imagens mortas/antigas por fotos oficiais do CDN Shopify
com encapsulamento responsivo e seguro.
"""

import re
from typing import List, Dict, Any

class HTMLReplacer:
    def __init__(self):
        # Padrões de hosts problemáticos/mortos
        self.dead_hosts = [
            r"use-brk-images-s3\.s3\.us-east-1\.amazonaws\.com",
            r"s3\.amazonaws\.com/use-brk-images",
            r"photobucket\.com",
            r"imageshack\.us",
            r"imgur\.com",
            r"postimg\.cc",
            r"placeholder",
            r"sem-foto",
            r"no-image"
        ]
        self.dead_regex = re.compile("|".join(self.dead_hosts), re.IGNORECASE)

    def is_dead_image(self, src: str) -> bool:
        if not src:
            return True
        return bool(self.dead_regex.search(src))

    def create_responsive_image_tag(self, cdn_url: str, alt_text: str) -> str:
        """
        Gera uma tag de imagem responsiva encapsulada no padrão Shopify que não quebra layout.
        """
        return (
            f'<div class="brk-preserved-media" style="margin: 24px auto; text-align: center; max-width: 850px;">'
            f'<img src="{cdn_url}" alt="{alt_text}" '
            f'style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 14px rgba(15,23,42,0.08); display: inline-block;" '
            f'loading="lazy" />'
            f'</div>'
        )

    def replace_images_preserve_html(self, original_html: str, cdn_images: List[str], product_title: str) -> str:
        """
        Substitui imagens quebradas/externas pelas fotos oficiais do CDN Shopify.
        Mantém todo o texto original, listas, tabelas e cabeçalhos intactos.
        """
        if not original_html or not original_html.strip():
            # Se não havia HTML, gera estrutura básica com as fotos CDN
            img_blocks = [self.create_responsive_image_tag(img, f"{product_title} - Foto {i+1}") for i, img in enumerate(cdn_images[:3])]
            return "\n".join(img_blocks)

        html = original_html.strip()
        
        # Encontrar todas as tags <img>
        img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
        
        all_cdn = list(cdn_images) if cdn_images else []
        assigned_cdn = list(cdn_images[:3]) if cdn_images else []
        cdn_idx = 0
        seen_roots = set()

        def img_sub_callback(match):
            nonlocal cdn_idx
            original_src = match.group(1).strip()
            orig_root = original_src.split("?")[0].lower()
            
            # Se a imagem é morta ou externa fora do CDN Shopify
            if self.is_dead_image(original_src) or ("cdn.shopify.com" not in original_src):
                while cdn_idx < len(all_cdn):
                    new_src = all_cdn[cdn_idx]
                    cdn_idx += 1
                    new_root = new_src.split("?")[0].lower()
                    if new_root in seen_roots:
                        continue
                    seen_roots.add(new_root)
                    return self.create_responsive_image_tag(new_src, f"{product_title} - Detalhe Oficial")
                # Sem foto CDN substituta disponível, remove a tag quebrada/externa para não dar 404
                return ""
            
            # Se já for uma imagem válida no texto original, verificar duplicata
            if orig_root in seen_roots:
                return ""  # Remove duplicatas existentes no HTML original
            seen_roots.add(orig_root)
            return match.group(0)

        # 1. Substituir tags <img> encontradas
        updated_html = img_pattern.sub(img_sub_callback, html)

        # 2. Se sobrou alguma imagem CDN não usada das 3 principais e havia poucas imagens no texto original
        # Adiciona no final de forma harmônica garantindo que não foi usada antes
        remaining_cdn = assigned_cdn[cdn_idx:] if cdn_idx < len(assigned_cdn) else []
        if remaining_cdn:
            extra_imgs = []
            for i, img in enumerate(remaining_cdn):
                img_root = img.split("?")[0].lower()
                if img_root not in seen_roots:
                    seen_roots.add(img_root)
                    extra_imgs.append(self.create_responsive_image_tag(img, f"{product_title} - Galeria {i+1}"))
            if extra_imgs:
                updated_html += "\n" + "\n".join(extra_imgs)

        # 3. Limpeza de parágrafos vazios deixados por remoção de imagens
        updated_html = re.sub(r'<p>\s*(?:&nbsp;|<br\s*/?>)?\s*</p>', '', updated_html, flags=re.IGNORECASE)
        
        # 4. Envolver com container seguro e isolado
        wrapper = f"""<!-- BRK MODO A: CONTEUDO ORIGINAL PRESERVADO COM FOTOS OFICIAIS CDN SHOPIFY -->
<div class="brk-original-preserved" style="max-width: 980px; margin: 0 auto; line-height: 1.6; color: #1e293b;">
{updated_html}
</div>"""
        return wrapper
