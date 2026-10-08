"""
BRK Studio - Garment Processor (services/studio/garment_processor.py)

Processa e padroniza as imagens dos produtos (mockups e fotos planas) da Shopify
para ingestão nos motores de Virtual Try-On e Difusão de Imagens.
"""

import os
import urllib.request
import hashlib
from typing import Dict, Optional

class GarmentProcessor:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cache_dir = os.path.join(base_dir, "data", "studio_cache", "garments")
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def extract_primary_image_url(self, product: dict) -> Optional[str]:
        """Obtém a melhor foto frontal da peça a partir das listas de imagens da Shopify"""
        sources = product.get("gallery") or product.get("cdn_images") or product.get("images") or []
        if isinstance(sources, list) and sources:
            first = sources[0]
            if isinstance(first, dict):
                return first.get("src")
            elif isinstance(first, str):
                return first
        if product.get("image"):
            img = product.get("image")
            return img if isinstance(img, str) else img.get("src")
        return None

    def download_and_prepare_garment(self, product: dict) -> Dict:
        """
        Baixa e prepara o mockup da peça para o estúdio.
        Retorna dicionário com caminho local, URL original e metadados.
        """
        image_url = self.extract_primary_image_url(product)
        if not image_url:
            raise ValueError(f"Produto {product.get('master_sku')} não possui nenhuma imagem na galeria.")

        # Gerar nome de arquivo determinístico baseado no hash da URL
        url_hash = hashlib.md5(image_url.encode("utf-8")).hexdigest()[:12]
        sku = str(product.get("master_sku") or product.get("sku") or "ITEM").replace("/", "_").replace("\\", "_")
        filename = f"{sku}_{url_hash}.jpg"
        local_path = os.path.join(self.cache_dir, filename)

        # Se já existe no cache local, reaproveita
        if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
            req = urllib.request.Request(image_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(local_path, "wb") as f:
                    f.write(resp.read())

        file_size = os.path.getsize(local_path)

        return {
            "sku": sku,
            "title": product.get("title", ""),
            "original_url": image_url,
            "local_path": local_path,
            "filename": filename,
            "file_size_bytes": file_size,
            "archetype_id": product.get("archetype_id", "uv_performance"),
            "category": "upper_body" # VTON category: upper_body, lower_body, dresses
        }

garment_processor = GarmentProcessor()
