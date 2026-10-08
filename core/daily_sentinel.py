"""
Orquestrador do Vigilante Diário de Catálogo (Execução das 08:00).
Varre as 3 lojas (BRK Fishing, BRK Agro, BRK Motors),
detecta fotos quebradas, textos ausentes, links externos proibidos e SKUs órfãos,
atualiza o histórico de saúde temporal, gera a planilha diária de correções
e regera o painel central sincronizado no OneDrive.
"""

import os
import sys
import json
import csv
from datetime import datetime
from typing import Dict, Any, List

# Garantir UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.shopify_public_api import ShopifyPublicAPI
from core.auditor import CatalogAuditor
from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder
from core.image_harvester import ImageHarvester

class DailySentinel:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.api = ShopifyPublicAPI()
        self.auditor = CatalogAuditor()
        self.template_engine = TemplateEngine()
        self.html_builder = HTMLBuilder()
        self.image_harvester = ImageHarvester()
        self.reports_dir = os.path.join(base_dir, "reports")
        self.daily_fixes_dir = os.path.join(self.reports_dir, "daily_fixes")
        os.makedirs(self.daily_fixes_dir, exist_ok=True)

    def run_daily_cycle(self) -> Dict[str, Any]:
        """
        Executa o ciclo diário completo de auditoria e correção preventiva.
        """
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[SENTINEL] Iniciando ciclo do Vigilante Diário: {timestamp_str}")

        stores = [
            {"key": "brk_fishing", "name": "BRK Fishing", "data_file": "data/stores/brk_fishing.json"},
            {"key": "brk_agro", "name": "BRK Agro", "data_file": "data/stores/brk_agro.json"},
            {"key": "brk_motors", "name": "BRK Motors", "data_file": "data/stores/brk_motors.json"}
        ]

        stores_summary = {}
        all_daily_corrections = []
        corrections_by_category = {
            "fishing_quebradas": [],
            "fishing_sem_descricao": [],
            "agro_todas": [],
            "motors_todas": []
        }

        for st in stores:
            print(f"  -> Auditando loja: {st['name']}...")
            data_path = os.path.join(self.base_dir, st["data_file"])
            if not os.path.exists(data_path):
                print(f"     [AVISO] Arquivo {data_path} não encontrado, pulando...")
                continue

            with open(data_path, "r", encoding="utf-8") as f:
                store_data = json.load(f)

            products = store_data.get("products", [])
            total_prods = len(products)
            
            broken_prods = [p for p in products if p.get("status") == "IMAGENS_QUEBRADAS"]
            empty_prods = [p for p in products if p.get("status") == "SEM_DESCRICAO"]
            
            # Checar links proibidos e SKUs órfãos
            prohibited_items = [p for p in products if p.get("prohibited_links")]
            orphaned_items = [p for p in products if p.get("orphaned_variants")]

            total_skus = sum(len(p.get("variants_skus", [])) or 1 for p in products)
            broken_skus = sum(p.get("affected_skus_count", 0) for p in broken_prods)
            healthy_skus = total_skus - broken_skus
            health_pct = round((healthy_skus / total_skus * 100), 1) if total_skus > 0 else 100.0

            # Gerar correções para itens com problema nesta loja (sem limite artificial)
            store_corrections = []
            for p in (broken_prods + empty_prods):
                gallery = p.get("gallery") or []
                if not gallery and p.get("cdn_images"):
                    gallery = p.get("cdn_images")
                if not gallery and p.get("images"):
                    raw_imgs = p.get("images")
                    if raw_imgs and isinstance(raw_imgs, list) and isinstance(raw_imgs[0], dict):
                        gallery = [img["src"] for img in raw_imgs if img.get("src")]
                    elif raw_imgs and isinstance(raw_imgs, list) and isinstance(raw_imgs[0], str):
                        gallery = raw_imgs
                if not gallery and p.get("image"):
                    gallery = [p.get("image")]
                images = [img for img in gallery if img][:3]

                vendor = p.get("vendor", "")
                sku_code = p.get("master_sku") or p.get("sku") or (p.get("variants_skus") and p.get("variants_skus")[0]) or ""
                archetype_id = self.template_engine.detect_archetype(p.get("title", ""), p.get("category", ""), p.get("tags", []), vendor=vendor, sku=sku_code)
                narrative = self.template_engine.generate_narrative_from_template(p, archetype_id, images, store_key=st["key"])
                new_html = self.html_builder.build_shopify_html(narrative)

                corr_item = {
                    "Loja": st["name"],
                    "Handle": p.get("handle", ""),
                    "Title": p.get("title", ""),
                    "Body (HTML)": new_html,
                    "SKU Mestre": p.get("master_sku", ""),
                    "Motivo": "Fotos Quebradas AWS S3" if p.get("status") == "IMAGENS_QUEBRADAS" else "Sem Descrição"
                }
                store_corrections.append(corr_item)
                all_daily_corrections.append(corr_item)

                if st["key"] == "brk_fishing":
                    if p.get("status") == "IMAGENS_QUEBRADAS":
                        corrections_by_category["fishing_quebradas"].append(corr_item)
                    else:
                        corrections_by_category["fishing_sem_descricao"].append(corr_item)
                elif st["key"] == "brk_agro":
                    corrections_by_category["agro_todas"].append(corr_item)
                elif st["key"] == "brk_motors":
                    corrections_by_category["motors_todas"].append(corr_item)

            stores_summary[st["key"]] = {
                "name": st["name"],
                "total_products": total_prods,
                "total_skus": total_skus,
                "broken_products": len(broken_prods),
                "broken_skus": broken_skus,
                "empty_products": len(empty_prods),
                "prohibited_links_products": len(prohibited_items),
                "prohibited_links_total": sum(len(p.get("prohibited_links", [])) for p in prohibited_items),
                "orphaned_skus_products": len(orphaned_items),
                "orphaned_variants_total": sum(len(p.get("orphaned_variants", [])) for p in orphaned_items),
                "health_percentage": health_pct,
                "corrections_generated": len(store_corrections)
            }

        # 1. Salvar Planilhas Diárias de Correções (Segmentadas e Particionadas < 15 MB)
        # Dividir fishing_quebradas em 2 lotes seguros para importação sem timeout na Shopify e compatível com Vercel
        fq = corrections_by_category["fishing_quebradas"]
        mid_fq = len(fq) // 2
        fq_p1 = fq[:mid_fq]
        fq_p2 = fq[mid_fq:]

        csv_filename = "shopify_correcoes_fishing_quebradas_parte1.csv"
        csv_path = os.path.join(self.daily_fixes_dir, csv_filename)
        csv_files_to_save = {
            "shopify_correcoes_fishing_quebradas_parte1.csv": fq_p1,
            "shopify_correcoes_fishing_quebradas_parte2.csv": fq_p2,
            "shopify_correcoes_fishing_sem_descricao.csv": corrections_by_category["fishing_sem_descricao"],
            "shopify_correcoes_agro.csv": corrections_by_category["agro_todas"],
            "shopify_correcoes_motors.csv": corrections_by_category["motors_todas"]
        }

        for filename, data_rows in csv_files_to_save.items():
            f_path = os.path.join(self.daily_fixes_dir, filename)
            with open(f_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Handle", "Title", "Body (HTML)"])
                writer.writeheader()
                for c in data_rows:
                    writer.writerow({
                        "Handle": c["Handle"],
                        "Title": c["Title"],
                        "Body (HTML)": c["Body (HTML)"]
                    })
            print(f"  -> Planilha gerada: {f_path} ({len(data_rows)} produtos)")

        # 2. Atualizar Histórico de Saúde Temporal
        history_path = os.path.join(self.reports_dir, "historico_saude.json")
        history = []
        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        snapshot_entry = {
            "date": date_str,
            "timestamp": timestamp_str,
            "total_corrections_ready": len(all_daily_corrections),
            "csv_file": csv_filename,
            "stores": stores_summary
        }

        # Atualiza se já existir o dia de hoje ou adiciona
        history = [h for h in history if h.get("date") != date_str]
        history.append(snapshot_entry)
        # Manter últimos 30 dias de histórico
        history = history[-30:]

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"  -> Histórico de saúde atualizado: {history_path}")

        return {
            "date": date_str,
            "timestamp": timestamp_str,
            "csv_path": csv_path,
            "csv_filename": csv_filename,
            "total_corrections": len(all_daily_corrections),
            "stores": stores_summary,
            "history": history
        }

if __name__ == "__main__":
    sentinel = DailySentinel()
    result = sentinel.run_daily_cycle()
    print("\n[VIGILANTE DIÁRIO CONCLUÍDO COM SUCESSO]")
    print(f"Data: {result['date']} | Total de Correções Prontas: {result['total_corrections']}")
