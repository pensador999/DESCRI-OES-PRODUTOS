"""
Script gerador de dados para a interface UI/UX do Catálogo BRK Fishing.
Varre produtos reais, categoriza em coleções visuais, executa a auditoria e salva em JSON estruturado.
"""

import sys
import os
import json
import re

# Assegura suporte UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.shopify_public_api import ShopifyPublicAPI
from core.auditor import CatalogAuditor
from core.template_engine import TemplateEngine

_ENGINE = TemplateEngine()

def categorize_product(prod: dict) -> str:
    title = prod.get("title", "")
    ptype = prod.get("product_type") or ""
    vendor = prod.get("vendor") or ""
    tags = prod.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    variants = prod.get("variants") or []
    sku = prod.get("master_sku") or (variants[0].get("sku") if variants and isinstance(variants[0], dict) else "") or ""
    arch_id = _ENGINE.detect_archetype(title, ptype, tags, vendor=vendor, sku=sku)
    return _ENGINE.classify_store_category(title, arch_id, store_key="brk_fishing", tags=tags, sku=sku)


def main():
    api = ShopifyPublicAPI("brk")
    auditor = CatalogAuditor()
    
    print("[*] Coletando catálogo COMPLETO da BRK Fishing (todas as páginas)...")
    raw_products = api.fetch_all_products(max_products=None)
    
    catalog_data = {
        "store": {
            "name": "BRK Fishing",
            "domain": "www.brkfishing.com.br",
            "logo": "https://www.brkfishing.com.br/cdn/shop/files/flaticon.png?crop=center&height=48&width=48",
            "total_scanned": len(raw_products)
        },
        "categories": {},
        "products": []
    }

    # Definir ícones e fotos de capa para as categorias circulares
    category_meta = {
        "Camisas ArmorX": {
            "title": "Linha ArmorX",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1770990241981-01MASC_48d1b69e-e65e-4d91-b900-b5e23a672747.jpg?v=1772135299&width=200",
            "badge": "Linhagem"
        },
        "Camisas de Pesca UV": {
            "title": "Camisas UV & Dry",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1770989069417-01MASC_f91bf971-daec-478a-a53c-a5749f7b11c6.jpg?v=1772134469&width=200",
            "badge": "Linhagem"
        },
        "Calçados & Sandálias": {
            "title": "Calçados & Sandálias",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1768480373262-01.jpg?v=1768480376&width=200",
            "badge": "Boaonda/BRK"
        },
        "Caixas & Organização": {
            "title": "Caixas & Estojos",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1768828062835-01.jpg?v=1768828066&width=200",
            "badge": "Tralha"
        },
        "Equipamentos & Iscas": {
            "title": "Equipamentos & Iscas",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1768828062835-01.jpg?v=1768828066&width=200",
            "badge": "Pesca"
        },
        "Térmicos & Camping": {
            "title": "Térmicos & Camping",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1768827986061-01.jpg?v=1768827990&width=200",
            "badge": "Térmicos"
        },
        "Cutelaria & Facas": {
            "title": "Facas & Cutelaria",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1769781878028-10.jpg?v=1769781879&width=200",
            "badge": "Artesanal"
        },
        "Óculos Polarizados": {
            "title": "Óculos Polarizados",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1764696147493-01.jpg?v=1764696150&width=200",
            "badge": "Proteção"
        },
        "Bonés & Chapéus": {
            "title": "Bonés & Chapéus",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1765377038930-01.jpg?v=1765377041&width=200",
            "badge": "Acessórios"
        },
        "Acessórios Diversos": {
            "title": "Acessórios Gerais",
            "thumb": "https://www.brkfishing.com.br/cdn/shop/files/1768827986061-01.jpg?v=1768827990&width=200",
            "badge": "Geral"
        }
    }

    for p in raw_products:
        diag = auditor.audit_product(p)
        cat_name = categorize_product(p)
        
        # Obter fotos da galeria
        images = [img["src"] for img in p.get("images", [])]
        main_img = images[0] if images else "https://via.placeholder.com/300?text=Sem+Foto"
        
        # Preço
        variants = p.get("variants", [])
        price = variants[0].get("price", "0.00") if variants else "0.00"
        try:
            formatted_price = f"R$ {float(price):.2f}".replace(".", ",")
        except Exception:
            formatted_price = f"R$ {price}"

        prod_item = {
            "id": p.get("id"),
            "title": p.get("title"),
            "handle": p.get("handle"),
            "url": f"https://www.brkfishing.com.br/products/{p.get('handle')}",
            "master_sku": diag["master_sku"],
            "variants_skus": diag["variants_skus"],
            "total_skus_count": diag["total_skus_count"],
            "affected_skus_count": diag["affected_skus_count"],
            "is_out_of_standard": diag["is_out_of_standard"],
            "standard_violations": diag["standard_violations"],
            "category": cat_name,
            "archetype": diag["archetype"],
            "price": formatted_price,
            "image": main_img,
            "gallery": images[:4],
            "status": diag["status"],
            "score": diag["score"],
            "word_count": diag["word_count"],
            "broken_images_count": diag["broken_images_count"],
            "broken_urls": diag["broken_urls"],
            "issues": diag["issues"],
            "recommendation": diag["recommendation"],
            "body_html": p.get("body_html") or ""
        }
        catalog_data["products"].append(prod_item)

    # Métricas Globais Agrupadas por SKU e Padrão
    total_skus = sum(p["total_skus_count"] for p in catalog_data["products"])
    broken_skus = sum(p["affected_skus_count"] for p in catalog_data["products"] if p["status"] == "IMAGENS_QUEBRADAS")
    out_of_standard_skus = sum(p["affected_skus_count"] for p in catalog_data["products"] if p["is_out_of_standard"])
    out_of_standard_prods = len([p for p in catalog_data["products"] if p["is_out_of_standard"]])

    catalog_data["store"]["total_skus"] = total_skus
    catalog_data["store"]["broken_skus"] = broken_skus
    catalog_data["store"]["out_of_standard_skus"] = out_of_standard_skus
    catalog_data["store"]["out_of_standard_prods"] = out_of_standard_prods

    # Contabilizar estatísticas por categoria
    for cat, meta in category_meta.items():
        cat_prods = [p for p in catalog_data["products"] if p["category"] == cat]
        if cat_prods:
            first_thumb = cat_prods[0]["image"]
            catalog_data["categories"][cat] = {
                "title": meta["title"],
                "badge": meta["badge"],
                "thumb": first_thumb,
                "count": len(cat_prods),
                "total_skus": sum(p["total_skus_count"] for p in cat_prods),
                "broken_skus": sum(p["affected_skus_count"] for p in cat_prods if p["status"] == "IMAGENS_QUEBRADAS"),
                "out_of_standard_skus": sum(p["affected_skus_count"] for p in cat_prods if p["is_out_of_standard"]),
                "broken_count": len([p for p in cat_prods if p["status"] == "IMAGENS_QUEBRADAS"]),
                "alert_count": len([p for p in cat_prods if p["status"] == "BAIXA_CONVERSAO"]),
                "empty_count": len([p for p in cat_prods if p["status"] == "SEM_DESCRICAO"])
            }

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "catalog_ui_data.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Dados estruturados com SKUs exportados: {out_file}")
    print(f"Total de produtos: {len(catalog_data['products'])} | Total de SKUs: {total_skus}")
    print(f"SKUs com fotos quebradas: {broken_skus} | SKUs fora do padrão: {out_of_standard_skus}")

if __name__ == "__main__":
    main()
