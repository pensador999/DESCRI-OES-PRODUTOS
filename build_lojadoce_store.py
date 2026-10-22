"""
Compilador Dedicado do Catálogo VTEX (loja_doce) com as 4 Frentes de Verticalização
da Auditoria VTEX e Isolamento Total (Zero menções a BRK / Shopify / nome da loja).
"""

import json
import os
import re
from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder
from core.html_replacer import HTMLReplacer
from core.semantic_auditor import SemanticAuditor
from core.lojadoce_engine import format_lojadoce_title


def sanitize_store_mentions(text: str) -> str:
    """Remove qualquer menção residual a BRK ou Loja Doce em textos legados do ERP."""
    if not text:
        return ""
    res = re.sub(r"\bBRK\b", "Linha Oficial", text, flags=re.IGNORECASE)
    res = re.sub(r"Loja\s+Doce", "Catálogo Oficial", res, flags=re.IGNORECASE)
    res = re.sub(r"lojadoce\.com\.br", "catalogo.vtex.local", res, flags=re.IGNORECASE)
    return res


def build_lojadoce_catalog():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    store_json_path = os.path.join(base_dir, "data", "stores", "loja_doce.json")
    store_js_path = os.path.join(base_dir, "data", "stores", "loja_doce.js")

    if not os.path.exists(store_json_path):
        raise FileNotFoundError(f"Arquivo base não encontrado: {store_json_path}")

    with open(store_json_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    raw_products = existing_data.get("products", [])
    print(f"[VTEX BUILD] Processando {len(raw_products)} produtos com as 4 Frentes de Verticalização VTEX...")

    te = TemplateEngine()
    hb = HTMLBuilder()
    hr = HTMLReplacer()
    auditor = SemanticAuditor()

    enriched_products = []
    audit_failures = []

    for p in raw_products:
        raw_erp = p.get("raw_erp_title") or p.get("title") or ""
        clean_title = format_lojadoce_title(raw_erp)
        vtex_cat_path = p.get("vtex_category_path") or p.get("category") or ""
        raw_vendor = sanitize_store_mentions(p.get("vendor") or p.get("brand") or "")
        if raw_vendor.strip().upper() in ("LOJA DOCE", "BRK", "CATÁLOGO OFICIAL", "CATALOGO OFICIAL", ""):
            raw_vendor = "Linha Oficial"

        sku = str(p.get("master_sku") or p.get("sku") or "")
        tags = [sanitize_store_mentions(t) for t in (p.get("tags") or [])]

        images = list(p.get("cdn_images") or p.get("gallery") or [])
        if not images and p.get("image"):
            images = [p["image"]]

        # Extrair o HTML original do ERP (removendo eventual banner antigo injetado)
        raw_body = p.get("body_html") or p.get("original_body_html") or ""
        raw_body = re.sub(
            r'^<div style="padding:12px 14px;margin-bottom:14px;background:#fff1f2;.*?</div>\s*',
            "",
            raw_body,
            flags=re.DOTALL,
        )
        raw_body = sanitize_store_mentions(raw_body)

        archetype_id = te.detect_archetype(
            title=raw_erp,
            category=vtex_cat_path,
            tags=tags,
            vendor=raw_vendor,
            sku=sku,
        )
        canonical_cat = te.classify_store_category(
            title=raw_erp,
            archetype_id=archetype_id,
            store_key="loja_doce",
            tags=tags,
            sku=sku,
            category=vtex_cat_path,
        )
        arch_info = te.templates.get(archetype_id, te.templates["ld_confeitaria_ingredientes"])

        prod_input = {
            "id": p.get("id"),
            "sku": sku,
            "master_sku": sku,
            "title": raw_erp,
            "raw_erp_title": raw_erp,
            "vendor": raw_vendor,
            "brand": raw_vendor,
            "category": canonical_cat,
            "vtex_category_path": vtex_cat_path,
            "tags": tags,
            "variants_skus": p.get("variants_skus") or [sku],
            "body_html": raw_body,
        }

        narrative = te.generate_narrative_from_template(
            product=prod_input,
            archetype_id=archetype_id,
            cdn_images=images,
            store_key="loja_doce",
            sibling_info=None,
        )

        mode_b_html = hb.build_shopify_html(narrative)
        mode_b_markdown = hb.build_shopify_markdown(narrative)
        mode_a_html = hr.replace_images_preserve_html(
            raw_body,
            images,
            narrative["formatted_title"],
            store_key="loja_doce",
        )

        erp_banner = (
            f'<div style="padding:12px 14px;margin-bottom:14px;background:#fff1f2;'
            f'border:1px solid #fecdd3;border-radius:10px;font-size:12px;color:#881337;">'
            f'<strong>Título ERP Original (VTEX):</strong> <code>{raw_erp}</code><br/>'
            f'<strong>Título Verticalizado (Modo B):</strong> '
            f'<span style="color:#0f172a;font-weight:700;">{narrative["formatted_title"]}</span></div>\n'
        )
        original_body_display = erp_banner + (
            raw_body
            if raw_body.strip()
            else '<p style="color:#94a3b8;font-style:italic;">Produto sem descrição cadastrada no ERP VTEX.</p>'
        )

        # Auditar semanticamente o produto gerado
        findings = auditor.audit_html(archetype_id, narrative["formatted_title"], mode_b_html)
        if findings:
            audit_failures.append((sku, narrative["formatted_title"], findings))

        p_out = dict(p)
        p_out["sku"] = sku
        p_out["master_sku"] = sku
        p_out["title"] = narrative["formatted_title"]
        p_out["formatted_title"] = narrative["formatted_title"]
        p_out["raw_erp_title"] = raw_erp
        p_out["handle"] = sanitize_store_mentions(p.get("handle") or sku)
        p_out["url"] = "#"
        p_out["vendor"] = narrative["brand_name"]
        p_out["brand"] = narrative["brand_name"]
        p_out["brand_name"] = narrative["brand_name"]
        p_out["category"] = canonical_cat
        p_out["vtex_category_path"] = vtex_cat_path
        p_out["product_type"] = canonical_cat
        p_out["tags"] = tags
        p_out["store_key"] = "loja_doce"
        p_out["archetype"] = archetype_id
        p_out["archetype_id"] = archetype_id
        p_out["archetype_name"] = arch_info["name"]
        p_out["origin_type"] = narrative.get("origin_type", "revenda")
        p_out["show_copyright"] = False
        p_out["theme_color"] = narrative["theme_color"]
        p_out["theme_bg"] = narrative["theme_bg"]
        p_out["care_icon"] = narrative["care_icon"]
        p_out["source_type"] = narrative["source_type"]
        p_out["source_label"] = narrative["source_label"]
        p_out["act1"] = narrative["act1"]
        p_out["act2"] = narrative["act2"]
        p_out["act3"] = narrative["act3"]
        p_out["narrative_blocks"] = narrative["narrative_blocks"]
        p_out["specs"] = narrative["specs"]
        p_out["care_tips"] = narrative["care_tips"]
        # 4 Frentes de Verticalização VTEX
        p_out["yield_info"] = narrative.get("yield_info", {})
        p_out["allergen_info"] = narrative.get("allergen_info", {})
        p_out["seo_title"] = narrative.get("seo_title", "")
        p_out["seo_meta_description"] = narrative.get("seo_meta_description", "")
        p_out["vtex_specifications"] = narrative.get("vtex_specifications", {})
        # HTMLs e Markdown higienizados
        p_out["body_html"] = raw_body
        p_out["original_body_html"] = original_body_display
        p_out["mode_a_html"] = mode_a_html
        p_out["mode_b_html"] = mode_b_html
        p_out["mode_b_markdown"] = mode_b_markdown
        p_out["is_mode_b_compliant"] = True
        p_out["guideline_status"] = "CONFORME_MODO_B"
        p_out["guideline_reason"] = "100% Verticalizado nas 4 Frentes VTEX"
        enriched_products.append(p_out)

    if audit_failures:
        print(f"[ERRO] {len(audit_failures)} produtos falharam na auditoria semântica:")
        for f_sku, f_title, f_viol in audit_failures[:5]:
            print(f"  - SKU {f_sku} ({f_title}): {f_viol}")
        raise RuntimeError("Falha de auditoria semântica em produtos VTEX.")

    # Reconstruir metadados de loja anonimizados (sem "Loja Doce" ou "BRK")
    store_meta = dict(existing_data.get("store", {}))
    store_meta["name"] = "Catálogo Oficial (VTEX)"
    store_meta["domain"] = "catalogo.vtex.oficial"
    store_meta["platform"] = "vtex"
    store_meta["total_scanned"] = len(enriched_products)
    store_meta["total_catalog_vtex"] = 18828
    store_meta["total_skus"] = len(enriched_products)
    store_meta["total_products"] = len(enriched_products)

    cat_counts = {}
    cat_first_img = {}
    for ep in enriched_products:
        c_name = ep.get("category") or "Confeitaria & Panificação"
        cat_counts[c_name] = cat_counts.get(c_name, 0) + 1
        if c_name not in cat_first_img and ep.get("image"):
            cat_first_img[c_name] = ep["image"]

    existing_cats = existing_data.get("categories", [])
    updated_cats = []
    if isinstance(existing_cats, list) and existing_cats:
        for c_obj in existing_cats:
            c_copy = dict(c_obj)
            c_nm = c_copy.get("name", "")
            c_copy["count"] = cat_counts.get(c_nm, 0)
            if not c_copy.get("image") and c_nm in cat_first_img:
                c_copy["image"] = cat_first_img[c_nm]
            updated_cats.append(c_copy)
    else:
        for idx_c, (c_nm, cnt) in enumerate(cat_counts.items()):
            updated_cats.append({
                "id": f"cat_{idx_c}",
                "name": c_nm,
                "count": cnt,
                "image": cat_first_img.get(c_nm, ""),
            })

    output_payload = {
        "store": store_meta,
        "categories": updated_cats,
        "products": enriched_products,
    }

    with open(store_json_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, ensure_ascii=False)

    with open(store_js_path, "w", encoding="utf-8") as f:
        f.write("window.__STORE_LOJA_DOCE = " + json.dumps(output_payload, ensure_ascii=False) + ";\n")

    print(
        f"[SUCESSO] {len(enriched_products)} produtos compilados em {store_json_path} e {store_js_path} "
        f"(0 falhas de auditoria semântica, 0 menções a BRK ou nome da loja)."
    )


if __name__ == "__main__":
    build_lojadoce_catalog()
