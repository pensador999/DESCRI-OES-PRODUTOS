import urllib.request
import json
import os
import sys

from core.auditor import CatalogAuditor
from generate_catalog_data import categorize_product

auditor = CatalogAuditor()

handles = [
    'camisa-fusionx-brk-feminina-eua-vermelha-com-protecao-uv50',
    'camisa-fusionx-brk-feminina-eua-azul-com-protecao-uv50',
    'camisa-fusionx-feminina-brasil-verde-com-protecao-uv50',
    'camisa-fusionx-feminina-brasil-amarelo-com-protecao-uv50',
    'camisa-fusionx-feminina-brasil-azul-com-protecao-uv50',
    'camisa-fusionx-feminina-brk-barkeiro-azul-e-amarelo-com-protecao-uv50',
    'camisa-fusionx-feminina-brk-barkeiro-chumbo-e-detalhes-em-amarelo-com-protecao-uv50',
    'camisa-de-pesca-brk-com-capuz-hybrid-pescaiaque-azul-com-detalhe-amarelo-com-protecao-solar-uv50',
    'camisa-de-pesca-feminina-brk-com-capuz-hybrid-pescaiaque-azul-com-detalhe-amarelo-com-protecao-solar-uv50',
    'camisa-de-pesca-brk-com-capuz-hybrid-pescaiaque-chumbo-com-detalhe-amarelo-com-protecao-solar-uv50',
    'camisa-de-pesca-feminina-brk-com-capuz-hybrid-pescaiaque-chumbo-com-detalhe-amarelo-com-protecao-solar-uv50'
]

ui_data_path = 'reports/catalog_ui_data.json'
with open(ui_data_path, 'r', encoding='utf-8') as f:
    catalog_data = json.load(f)

existing_ids = {str(p.get('id')) for p in catalog_data.get('products', [])}
added = 0

for h in handles:
    url = f"https://www.brkfishing.com.br/products/{h}.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            p = data['product']
            pid = str(p['id'])
            if pid not in existing_ids:
                diag = auditor.audit_product(p)
                cat_name = categorize_product(p)
                images = [img['src'] for img in p.get('images', [])]
                main_img = images[0] if images else 'https://via.placeholder.com/300?text=Sem+Foto'
                variants = p.get('variants', [])
                price = variants[0].get('price', '0.00') if variants else '0.00'
                try:
                    formatted_price = f"R$ {float(price):.2f}".replace('.', ',')
                except Exception:
                    formatted_price = f"R$ {price}"
                
                handle_val = p.get('handle')
                prod_item = {
                    'id': p.get('id'),
                    'title': p.get('title'),
                    'handle': handle_val,
                    'url': f"https://www.brkfishing.com.br/products/{handle_val}",
                    'master_sku': diag['master_sku'],
                    'variants_skus': diag['variants_skus'],
                    'total_skus_count': diag['total_skus_count'],
                    'affected_skus_count': diag['affected_skus_count'],
                    'is_out_of_standard': diag['is_out_of_standard'],
                    'standard_violations': diag['standard_violations'],
                    'category': cat_name,
                    'archetype': diag['archetype'],
                    'price': formatted_price,
                    'image': main_img,
                    'gallery': images[:4],
                    'status': diag['status'],
                    'score': diag['score'],
                    'word_count': diag['word_count'],
                    'broken_images_count': diag['broken_images_count'],
                    'broken_urls': diag['broken_urls'],
                    'issues': diag['issues'],
                    'recommendation': diag['recommendation'],
                    'body_html': p.get('body_html') or ''
                }
                catalog_data['products'].append(prod_item)
                existing_ids.add(pid)
                added += 1
                print(f"Added {pid}: {p.get('title')}")
    except Exception as e:
        print(f"Err {h}: {e}")

print(f"Total added: {added}")
if added > 0:
    catalog_data['store']['total_scanned'] = len(catalog_data['products'])
    with open(ui_data_path, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
    print("reports/catalog_ui_data.json successfully updated!")
