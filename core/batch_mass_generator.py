"""
Gerador em Massa por SKU e Código de Família (Pilar 3).
Varre todos os produtos sem descrição ou com imagens quebradas,
agrupa rigorosamente por SKU Mestre e família de variantes,
aplica o Molde Mestre correspondente com fotos oficiais do CDN Shopify
e gera os arquivos CSV oficiais para importação direta no Shopify.
"""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any

from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder
from core.html_replacer import HTMLReplacer
from core.image_harvester import ImageHarvester

class BatchMassGenerator:
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.html_builder = HTMLBuilder()
        self.html_replacer = HTMLReplacer()
        self.image_harvester = ImageHarvester()

    def process_store_mass(self, 
                           store_key: str, 
                           catalog_data_path: str, 
                           output_dir: str, 
                           mode: str = "mode_b_conversion",
                           target_filter: str = "broken_or_empty") -> Dict[str, Any]:
        """
        Processa em lote todos os produtos da loja alvo.
        mode: 'mode_a_preserve' (mantém HTML original e troca fotos) ou 'mode_b_conversion' (redesenha 3 atos com molde)
        target_filter: 'broken_or_empty', 'empty_only', 'broken_only', 'all'
        """
        if not os.path.exists(catalog_data_path):
            raise FileNotFoundError(f"Arquivo de catálogo não encontrado: {catalog_data_path}")

        with open(catalog_data_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)

        products = catalog.get("products", [])
        
        # Filtragem de produtos alvo
        target_products = []
        for p in products:
            status = p.get("status", "")
            is_broken = (status == "IMAGENS_QUEBRADAS")
            body_str = (p.get("original_body_html") or p.get("body_html") or "").strip()
            is_empty = (
                status == "SEM_DESCRICAO" 
                or not body_str 
                or len(body_str) <= 5 
                or body_str.lower() in ("a", "<p>a</p>", "<p></p>")
            )
            
            if target_filter == "broken_or_empty" and (is_broken or is_empty):
                target_products.append(p)
            elif target_filter == "empty_only" and is_empty:
                target_products.append(p)
            elif target_filter == "broken_only" and is_broken:
                target_products.append(p)
            elif target_filter == "all":
                target_products.append(p)

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        processed_items = []
        csv_rows = []

        for p in target_products:
            title = p.get("title", "")
            handle = p.get("handle", "")
            master_sku = p.get("master_sku", "SKU-N/D")
            variants_skus = p.get("variants_skus", [])
            category = p.get("category", "")
            tags = p.get("tags", [])
            # 1. Coleta das fotos oficiais do CDN Shopify (da galeria cadastrada no site)
            images = p.get("gallery") or []
            if not images and p.get("cdn_images"):
                images = p.get("cdn_images")
            if not images and p.get("images"):
                raw_imgs = p.get("images")
                if raw_imgs and isinstance(raw_imgs, list) and isinstance(raw_imgs[0], dict):
                    images = [img["src"] for img in raw_imgs if img.get("src")]
                elif raw_imgs and isinstance(raw_imgs, list) and isinstance(raw_imgs[0], str):
                    images = raw_imgs
            if not images and p.get("image"):
                images = [p.get("image")]
            images = [img for img in images if img][:3]

            original_html = p.get("original_body_html") or p.get("body_html") or ""

            # 2. Detecção de arquétipo
            archetype_id = self.template_engine.detect_archetype(title, category, tags)

            # 3. Geração conforme o modo escolhido
            if mode == "mode_a_preserve" and original_html and original_html.strip():
                # Modo A: Preservar HTML original substituindo imagens mortas por fotos CDN
                generated_html = self.html_replacer.replace_images_preserve_html(original_html, images, title)
                generation_mode_used = "Preservar HTML Original + Fotos CDN"
            else:
                # Modo B: Redesenho completo em 3 Atos com Molde Mestre
                narrative_data = self.template_engine.generate_narrative_from_template(p, archetype_id, images, store_key=store_key)
                generated_html = self.html_builder.build_shopify_html(narrative_data)
                arch_name = narrative_data.get("source_label") or archetype_id
                generation_mode_used = f"3 Atos Alta Conversão ({arch_name})"

            item_result = {
                "id": p.get("id"),
                "handle": handle,
                "title": title,
                "master_sku": master_sku,
                "variants_count": len(variants_skus),
                "variants_skus": variants_skus,
                "category": category,
                "archetype_id": archetype_id,
                "generation_mode": generation_mode_used,
                "images_count": len(images),
                "cdn_images": images,
                "original_html": original_html,
                "generated_html": generated_html
            }
            processed_items.append(item_result)

            # Formato oficial do CSV de importação Shopify:
            # Handle, Title, Body (HTML)
            csv_rows.append({
                "Handle": handle,
                "Title": title,
                "Body (HTML)": generated_html
            })

        # Salvar CSV Shopify
        csv_filename = f"shopify_massa_{store_key}_{mode}_{timestamp}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Handle", "Title", "Body (HTML)"])
            writer.writeheader()
            writer.writerows(csv_rows)

        # Salvar JSON com comparativos e auditoria do lote
        json_filename = f"batch_massa_results_{store_key}_{timestamp}.json"
        json_path = os.path.join(output_dir, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "store_key": store_key,
                "timestamp": timestamp,
                "mode": mode,
                "total_processed": len(processed_items),
                "csv_file": csv_path,
                "items": processed_items
            }, f, ensure_ascii=False, indent=2)

        return {
            "store_key": store_key,
            "total_processed": len(processed_items),
            "csv_path": csv_path,
            "json_path": json_path,
            "items": processed_items
        }
