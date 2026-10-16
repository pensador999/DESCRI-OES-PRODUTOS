"""
Compilador Mestre Modular & Otimizado para Deploy na Vercel (v5.0).
Desacopla index.html (< 50 KB), distribui dados JSON por loja em data/stores/,
gera ícones vetoriais SVG estilo Font Awesome e sincroniza automaticamente com o repositório GitHub.
"""

import json
import os
import re
import sys
import shutil
import subprocess
from datetime import datetime

from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder
from core.html_replacer import HTMLReplacer
from core.image_harvester import ImageHarvester
from core.sibling_matcher import SiblingMatcher
from core.svg_icons import get_svg_icon

def build_dist():
    print("[INICIO] Inicializando compilador modular v5.0 (Vercel & SVG Font Awesome)...")
    template_engine = TemplateEngine()
    html_builder = HTMLBuilder()
    html_replacer = HTMLReplacer()
    image_harvester = ImageHarvester()
    sibling_matcher = SiblingMatcher()

    # 1. Carregar dados brutos das lojas
    print("[1/5] Carregando dados brutos dos relatórios das 3 lojas...")
    with open("reports/catalog_ui_data.json", "r", encoding="utf-8") as f:
        fishing_data = json.load(f)

    with open("reports/brk_agro/catalog_ui_data.json", "r", encoding="utf-8") as f:
        agro_data = json.load(f)

    with open("reports/brk_motors/catalog_ui_data.json", "r", encoding="utf-8") as f:
        motors_data = json.load(f)

    # 2. Carregar histórico de saúde do Vigilante Diário
    history_file = "reports/historico_saude.json"
    history_data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception:
            history_data = []

    # 3. CSVs diários desativados (substituídos por automação direta Tampermonkey / API)
    available_csvs = []

    # Função de enriquecimento de produtos
    def enrich_products(store_dict, store_key="brk_fishing"):
        all_prods = store_dict.get("products", [])
        dead_body_re = re.compile(r"use-brk-images-s3|photobucket|imageshack|tinytake|yampi", re.IGNORECASE)

        # Normalizar status de todos os produtos: classificação estrita e sem falso-positivo de ícone SVG
        for p in all_prods:
            body = (p.get("original_body_html") or p.get("body_html") or "").strip()
            clean_b = re.sub(r'<style.*?</style>', ' ', body, flags=re.S | re.I)
            clean_b = re.sub(r'<[^>]+>', ' ', clean_b).strip()
            clean_b = re.sub(r'\s+', ' ', clean_b)
            w_count = len(clean_b.split()) if clean_b else 0
            is_empty_or_placeholder = (
                not body
                or w_count == 0
                or clean_b.lower() in ("a", "p", "br", "-", ".", "none", "null", "undefined")
                or (w_count < 20 and not any(tag in body.lower() for tag in ["<table", "<div", "<ul"]))
                or w_count < 5
            )
            # Extrair apenas imagens reais (ignorando ícones .svg decorativos antigos como uv_protection.svg)
            img_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', body, flags=re.I)
            broken_photo_urls = [
                u for u in img_urls
                if dead_body_re.search(u) and not u.split("?")[0].strip().lower().endswith(".svg")
            ]
            has_broken_s3_photos = len(broken_photo_urls) > 0

            if has_broken_s3_photos:
                p["status"] = "IMAGENS_QUEBRADAS"
                p["is_out_of_standard"] = True
                p["broken_images_count"] = len(broken_photo_urls)
                p["broken_urls"] = broken_photo_urls
            elif is_empty_or_placeholder:
                p["status"] = "SEM_DESCRICAO"
                p["is_out_of_standard"] = True
                p["broken_images_count"] = 0
                p["broken_urls"] = []
            else:
                p["status"] = "SAUDAVEL"
                p["is_out_of_standard"] = False
                p["broken_images_count"] = 0
                p["broken_urls"] = []

        # Incluir 100% de todos os produtos do catálogo (sem descarte de produtos saudáveis)
        selected_prods = []
        selected_handles = set()
        for p in all_prods:
            h = p.get("handle")
            if h and h not in selected_handles:
                p_title = p.get("title", "")
                p_cat = p.get("category", "")
                p_tags = p.get("tags", [])
                p_vendor = p.get("vendor", "")
                p_sku = p.get("master_sku") or p.get("sku") or (p.get("variants_skus") and p.get("variants_skus")[0]) or ""
                p["archetype_id"] = template_engine.detect_archetype(p_title, p_cat, p_tags, vendor=p_vendor, sku=p_sku)
                selected_prods.append(p)
                selected_handles.add(h)

        # Indexar catálogo desta loja no sibling_matcher já com archetype_id populado
        sibling_matcher.set_catalog(selected_prods)

        enriched = []
        for idx, p in enumerate(selected_prods):
            title = p.get("title", "")
            category = p.get("category", "")
            tags = p.get("tags", [])
            
            # Coleta oficial e desduplicação estrita de fotos da galeria da Shopify
            raw_sources = p.get("gallery") or []
            if not raw_sources and p.get("cdn_images"):
                raw_sources = p.get("cdn_images")
            if not raw_sources and p.get("images"):
                raw_imgs = p.get("images", [])
                if raw_imgs and isinstance(raw_imgs, list) and isinstance(raw_imgs[0], dict):
                    raw_sources = [img["src"] for img in raw_imgs if img.get("src")]
                elif raw_imgs and isinstance(raw_imgs, list) and isinstance(raw_imgs[0], str):
                    raw_sources = raw_imgs
            if not raw_sources and p.get("image"):
                raw_sources = [p.get("image")]

            seen_roots = set()
            images = []
            for u in raw_sources:
                if not u or not isinstance(u, str):
                    continue
                clean_u = u.strip()
                if not clean_u:
                    continue
                root = clean_u.split("?")[0].lower()
                if root not in seen_roots:
                    seen_roots.add(root)
                    images.append(clean_u)

            orig_html = p.get("original_body_html") or p.get("body_html") or ""
            vendor = p.get("vendor", "")
            sku_code = p.get("master_sku") or p.get("sku") or (p.get("variants_skus") and p.get("variants_skus")[0]) or ""
            archetype_id = p.get("archetype_id") or template_engine.detect_archetype(title, category, tags, vendor=vendor, sku=sku_code)
            images = template_engine._sanitize_and_dedup_images(images, archetype_id=archetype_id, title=title)
            canonical_cat = template_engine.classify_store_category(title, archetype_id, store_key=store_key, tags=tags, sku=sku_code)
            arch_info = template_engine.templates.get(archetype_id, template_engine.templates["uv_performance"])
            
            # Busca de irmão homólogo com trava estrita de arquétipo para produtos sem descrição ou com placeholder
            needs_sibling = (p.get("status") == "SEM_DESCRICAO") or (len(orig_html.strip()) < 80)
            sibling_info = sibling_matcher.find_best_sibling(p, min_score=0.70, target_archetype=archetype_id) if needs_sibling else None
            mode_a_html = html_replacer.replace_images_preserve_html(orig_html, images, title)
            narrative = template_engine.generate_narrative_from_template(p, archetype_id, images, store_key=store_key, sibling_info=sibling_info)
            
            is_headwear = archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy")
            # Salvar mode_b_html pré-compilado nos itens SEM_DESCRICAO (lote inicial), bonés/chapéus D2C e amostra inicial;
            # os demais produtos possuem narrative_blocks/specs completos e compilam mode_b_html em <2ms no cliente e na API,
            # mantendo cada loja bem abaixo do limite de 100 MB do GitHub e 250 MB da Vercel.
            save_mode_b = (p.get("status") == "SEM_DESCRICAO" and idx < 250) or (idx < 15) or is_headwear
            mode_b_html = html_builder.build_shopify_html(narrative) if save_mode_b else ""
            mode_b_markdown = html_builder.build_shopify_markdown(narrative) if save_mode_b else ""

            prohibited_links = p.get("prohibited_links", [])
            if not prohibited_links and orig_html:
                prohibited_domains = [r"use-brk-images-s3", r"drive\.google", r"mercadolivre", r"shopee", r"photobucket"]
                prohib_regex = re.compile("|".join(prohibited_domains), re.IGNORECASE)
                prohibited_links = [l for l in re.findall(r'(?:href|src)=["\']([^"\']+)["\']', orig_html) if prohib_regex.search(l)]

            # Mapeamento estrito de conformidade da descrição atual (orig_html) com as Diretrizes Modo B v5
            t_low_g = title.lower()
            sku_low_g = str(sku_code or "").lower()
            has_mode_b_structure = any(m in orig_html for m in ["<!-- BRK-MODO-B", "brk-desc-wrapper", "brk-cap-description"])
            expected_colors = {
                "brk_fishing": ("#0284c7", "#00a8ff"),
                "brk_agro": ("#15803d", "#22c55e", "#16a34a"),
                "brk_motors": ("#ea580c", "#f97316"),
            }.get(store_key, ("#0284c7", "#00a8ff"))

            if p.get("status") == "SEM_DESCRICAO":
                is_mode_b_compliant = False
                guideline_status = "SEM_DESCRICAO"
                guideline_reason = "Sem descrição cadastrada na Shopify"
            elif p.get("status") == "IMAGENS_QUEBRADAS":
                is_mode_b_compliant = False
                guideline_status = "IMAGENS_QUEBRADAS"
                guideline_reason = "Contém imagens quebradas (AWS S3 404)"
            elif not has_mode_b_structure:
                is_mode_b_compliant = False
                guideline_status = "FORA_PADRAO_MODO_B"
                guideline_reason = "Descrição legada fora do padrão oficial Modo B (sem 3 Atos / D2C)"
            else:
                violations = []
                if "Tabela de Medidas de Luvas" in orig_html and any(w in t_low_g or w in sku_low_g for w in ["camisa", "camiseta", "armorx", "cax", "hyb", "fusion"]):
                    violations.append("Camisa com Tabela de Luvas (corrigir para Tabela de Camisa PP ao G2)")
                if "Tabela de Medidas Adulto (P ao EXG)" in orig_html:
                    violations.append("Tabela Adulto antiga (P ao EXG em vez de PP ao G2)")
                if ("fillet" in t_low_g or "mfk75t" in t_low_g) and "bainha" in orig_html.lower() and "bainha" not in t_low_g:
                    violations.append("Faca Marine MFK75T com menção indevida a bainha")
                if ("fusion" in t_low_g or "fusion" in sku_low_g or "hybrid" in t_low_g or sku_low_g.startswith("hyb")) and re.search(r'\b(zíper|ziper)\b', orig_html, re.I):
                    violations.append("Modelo Fusion/Hybrid com menção indevida a zíper")
                if ("fusion" in t_low_g or "fusion" in sku_low_g or "hybrid" in t_low_g or sku_low_g.startswith("hyb")) and "sem contar" not in orig_html.lower():
                    violations.append("Tabela de Medidas sem orientação de Capuz/Bandana Embutida (medir do ombro à barra sem contar o capuz)")
                if "eQxQuY7.jpg" in orig_html and "ba09" not in sku_low_g:
                    violations.append("Boné com foto genérica repetida")
                orig_img_srcs = [u.split("?")[0].lower() for u in re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', orig_html, re.I) if not u.split("?")[0].lower().endswith(".svg")]
                if len(orig_img_srcs) != len(set(orig_img_srcs)):
                    violations.append("Fotos repetidas nos Atos/Cards")
                if not any(c in orig_html.lower() for c in expected_colors) and any(c in orig_html.lower() for c in ("#0284c7", "#15803d", "#ea580c", "#f97316")):
                    violations.append("Cor de outra loja no HTML")
                if violations:
                    is_mode_b_compliant = False
                    guideline_status = "MODO_B_DESATUALIZADO"
                    guideline_reason = "; ".join(violations)
                else:
                    is_mode_b_compliant = True
                    guideline_status = "CONFORME_MODO_B"
                    guideline_reason = "100% dentro das diretrizes oficiais Modo B"

            p_copy = dict(p)
            p_copy.pop("images", None)
            p_copy.pop("original_body_html", None)
            p_copy["body_html"] = orig_html
            p_copy["is_mode_b_compliant"] = is_mode_b_compliant
            p_copy["guideline_status"] = guideline_status
            p_copy["guideline_reason"] = guideline_reason
            p_copy["category"] = canonical_cat
            p_copy["cdn_images"] = images
            p_copy["gallery"] = images
            p_copy["image"] = images[0] if images else (p.get("image") or "")
            p_copy["archetype_id"] = archetype_id
            p_copy["archetype_name"] = arch_info["name"]
            p_copy["is_kids"] = narrative.get("is_kids", False)
            p_copy["is_short_sleeve"] = narrative.get("is_short_sleeve", False)
            p_copy["source_type"] = narrative["source_type"]
            p_copy["source_label"] = narrative["source_label"]
            p_copy["sibling_info"] = sibling_info
            p_copy["store_key"] = store_key
            p_copy["formatted_title"] = narrative.get("formatted_title", title)
            p_copy["brand_name"] = narrative.get("brand_name", "BRK")
            p_copy["origin_type"] = narrative.get("origin_type", "producao_propria")
            p_copy["show_copyright"] = narrative.get("show_copyright", False)
            p_copy["has_multiple_variations"] = narrative.get("has_multiple_variations", False)
            p_copy["split_images"] = narrative.get("split_images")
            p_copy["variations_summary"] = narrative.get("variations_summary", "")
            p_copy["theme_color"] = narrative["theme_color"]
            p_copy["theme_bg"] = narrative["theme_bg"]
            p_copy["care_icon"] = narrative["care_icon"]
            p_copy["narrative_blocks"] = narrative.get("narrative_blocks", [])
            p_copy["care_tips"] = narrative.get("care_tips", "")
            p_copy["specs"] = narrative.get("specs", [])
            p_copy["mode_a_html"] = mode_a_html
            p_copy["layout_format"] = narrative.get("layout_format", "standard_3act")
            if is_headwear:
                p_copy["details_grid"] = narrative.get("details_grid")
                p_copy["info_characteristics"] = narrative.get("info_characteristics")
                p_copy["info_care"] = narrative.get("info_care")
                p_copy["split_sections"] = narrative.get("split_sections")
            p_copy["mode_b_html"] = mode_b_html
            p_copy["mode_b_markdown"] = mode_b_markdown
            p_copy["prohibited_links"] = prohibited_links
            p_copy["orphaned_variants"] = p.get("orphaned_variants", [])
            enriched.append(p_copy)

        # Reconstruir categorias e métricas globais da loja com base nos produtos enriquecidos
        category_order = {
            "brk_fishing": [
                "Camisas ArmorX",
                "Camisas de Pesca UV",
                "Bonés & Chapéus",
                "Bandanas, Luvas & Manguitos",
                "Óculos Polarizados",
                "Equipamentos & Iscas",
                "Caixas & Organização",
                "Calçados & Sandálias",
                "Térmicos & Camping",
                "Cutelaria & Facas",
                "Acessórios Diversos",
            ],
            "brk_agro": [
                "Camisas Agro & Campo",
                "Bonés & Chapéus Agro",
                "Botinas & Calçados",
                "Calças & Vestuário Campo",
                "Bandanas, Luvas & Manguitos",
                "Óculos Polarizados Agro",
                "Cutelaria & Facas Campo",
                "Térmicos & Tereré",
                "Acessórios Agro & Fazenda",
            ],
            "brk_motors": [
                "Jerseys & Camisas Motors",
                "Jaquetas & Corta Vento",
                "Proteção & Luvas Motors",
                "Bonés & Street Motors",
                "Óculos & Goggles",
                "Acessórios & Equipamentos",
            ],
        }
        ordered_cats = list(category_order.get(store_key, []))
        for ep in enriched:
            c = ep.get("category", "Acessórios Diversos")
            if c not in ordered_cats:
                ordered_cats.append(c)

        rebuilt_categories = {}
        for cat in ordered_cats:
            cat_prods = [ep for ep in enriched if ep.get("category") == cat]
            if not cat_prods:
                continue
            thumb_url = ""
            for cp in cat_prods:
                img_c = cp.get("image") or ""
                if "cdn.shopify.com" in img_c:
                    thumb_url = img_c
                    break
            if not thumb_url:
                thumb_url = cat_prods[0].get("image", "")
            rebuilt_categories[cat] = {
                "name": cat,
                "title": cat,
                "badge": "Coleção",
                "thumb": thumb_url,
                "sample_image": thumb_url,
                "count": len(cat_prods),
                "total_skus": sum(ep.get("total_skus_count") or len(ep.get("variants_skus", [])) or 1 for ep in cat_prods),
                "broken_skus": sum((ep.get("total_skus_count") or len(ep.get("variants_skus", [])) or 1) for ep in cat_prods if ep.get("status") == "IMAGENS_QUEBRADAS"),
                "out_of_standard_skus": sum((ep.get("total_skus_count") or len(ep.get("variants_skus", [])) or 1) for ep in cat_prods if ep.get("is_out_of_standard")),
                "broken_count": sum(1 for ep in cat_prods if ep.get("status") == "IMAGENS_QUEBRADAS"),
                "alert_count": 0,
                "empty_count": sum(1 for ep in cat_prods if ep.get("status") == "SEM_DESCRICAO"),
            }

        rebuilt_store = dict(store_dict.get("store", {}))
        total_skus = sum(ep.get("total_skus_count") or len(ep.get("variants_skus", [])) or 1 for ep in enriched)
        broken_skus = sum((ep.get("total_skus_count") or len(ep.get("variants_skus", [])) or 1) for ep in enriched if ep.get("status") == "IMAGENS_QUEBRADAS")
        out_of_std_skus = sum((ep.get("total_skus_count") or len(ep.get("variants_skus", [])) or 1) for ep in enriched if ep.get("is_out_of_standard"))
        out_of_std_prods = sum(1 for ep in enriched if ep.get("is_out_of_standard"))
        rebuilt_store["total_products"] = len(enriched)
        rebuilt_store["total_scanned"] = len(enriched)
        rebuilt_store["total_skus"] = total_skus
        rebuilt_store["broken_skus"] = broken_skus
        rebuilt_store["out_of_standard_skus"] = out_of_std_skus
        rebuilt_store["out_of_standard_prods"] = out_of_std_prods

        return {
            "store": rebuilt_store,
            "categories": rebuilt_categories,
            "products": enriched
        }

    print("[2/5] Processando e enriquecendo produtos das 3 lojas...", flush=True)
    print("  -> Enriquecendo BRK Fishing...", flush=True)
    enriched_fishing = enrich_products(fishing_data, store_key="brk_fishing")
    print("  -> Enriquecendo BRK Agro...", flush=True)
    enriched_agro = enrich_products(agro_data, store_key="brk_agro")
    print("  -> Enriquecendo BRK Motors...", flush=True)
    enriched_motors = enrich_products(motors_data, store_key="brk_motors")

    # 4. Salvar arquivos particionados em data/stores/ (.json e .js para duplo clique file:// sem CORS)
    print("[3/5] Gravando arquivos JSON e JS particionados em data/stores/...")
    base_repo_dir = os.path.dirname(os.path.abspath(__file__))
    target_dirs = [base_repo_dir]
    if os.name == "nt" and os.path.exists(r"C:\Users\lucas\Desktop\PYTHON DATA"):
        target_dirs.append(r"C:\Users\lucas\Desktop\PYTHON DATA")
    analytics_data = {
        "history": history_data,
        "available_csvs": available_csvs
    }

    for base_p in target_dirs:
        if not os.path.exists(base_p):
            continue
        store_p = os.path.join(base_p, "data", "stores")
        os.makedirs(store_p, exist_ok=True)

        with open(os.path.join(store_p, "brk_fishing.json"), "w", encoding="utf-8") as f:
            json.dump(enriched_fishing, f, ensure_ascii=False)
        with open(os.path.join(store_p, "brk_fishing.js"), "w", encoding="utf-8") as f:
            f.write("window.__STORE_BRK_FISHING = " + json.dumps(enriched_fishing, ensure_ascii=False) + ";\n")

        with open(os.path.join(store_p, "brk_agro.json"), "w", encoding="utf-8") as f:
            json.dump(enriched_agro, f, ensure_ascii=False)
        with open(os.path.join(store_p, "brk_agro.js"), "w", encoding="utf-8") as f:
            f.write("window.__STORE_BRK_AGRO = " + json.dumps(enriched_agro, ensure_ascii=False) + ";\n")

        with open(os.path.join(store_p, "brk_motors.json"), "w", encoding="utf-8") as f:
            json.dump(enriched_motors, f, ensure_ascii=False)
        with open(os.path.join(store_p, "brk_motors.js"), "w", encoding="utf-8") as f:
            f.write("window.__STORE_BRK_MOTORS = " + json.dumps(enriched_motors, ensure_ascii=False) + ";\n")

        with open(os.path.join(store_p, "moldes.json"), "w", encoding="utf-8") as f:
            json.dump(template_engine.templates, f, ensure_ascii=False)
        with open(os.path.join(store_p, "moldes.js"), "w", encoding="utf-8") as f:
            f.write("window.__STORE_MOLDES = " + json.dumps(template_engine.templates, ensure_ascii=False) + ";\n")

        with open(os.path.join(store_p, "analytics.json"), "w", encoding="utf-8") as f:
            json.dump(analytics_data, f, ensure_ascii=False)
        with open(os.path.join(store_p, "analytics.js"), "w", encoding="utf-8") as f:
            f.write("window.__STORE_ANALYTICS = " + json.dumps(analytics_data, ensure_ascii=False) + ";\n")

        # Atualizar whitelist de IP da máquina autorizada
        ip_wl_path = os.path.join(store_p, "ip_whitelist.json")
        allowed_ips = ["104.28.199.94", "104.28.199.96", "2a09:bac5:779:2555::3b8:7a", "127.0.0.1", "::1"]
        allowed_prefixes = ["104.28.199.", "104.28.", "2a09:bac5:779:2555:"]
        if os.path.exists(ip_wl_path):
            try:
                with open(ip_wl_path, "r", encoding="utf-8") as f:
                    old_wl = json.load(f)
                for ip_item in old_wl.get("allowed_ips", []):
                    if ip_item not in allowed_ips:
                        allowed_ips.append(ip_item)
                for pfx_item in old_wl.get("allowed_prefixes", []):
                    if pfx_item not in allowed_prefixes:
                        allowed_prefixes.append(pfx_item)
            except Exception:
                pass
        try:
            import urllib.request
            for probe_url in ("https://api.ipify.org", "https://api64.ipify.org"):
                try:
                    req = urllib.request.Request(probe_url, headers={"User-Agent": "BRK-IP-Sync/1.0"})
                    with urllib.request.urlopen(req, timeout=2.5) as resp:
                        cur_ip = resp.read().decode("utf-8").strip()
                        if cur_ip and cur_ip not in allowed_ips:
                            allowed_ips.append(cur_ip)
                        if "." in cur_ip:
                            pfx24 = ".".join(cur_ip.split(".")[:3]) + "."
                            if pfx24 not in allowed_prefixes:
                                allowed_prefixes.append(pfx24)
                        elif ":" in cur_ip:
                            pfx64 = ":".join(cur_ip.split(":")[:4]) + ":"
                            if pfx64 not in allowed_prefixes:
                                allowed_prefixes.append(pfx64)
                except Exception:
                    pass
        except Exception:
            pass
        ip_wl_data = {
            "allowed_ips": allowed_ips,
            "allowed_prefixes": allowed_prefixes,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(ip_wl_path, "w", encoding="utf-8") as f:
            json.dump(ip_wl_data, f, ensure_ascii=False, indent=2)

    print("  -> data/stores/ gravados com sucesso.")

    fishing_skus = enriched_fishing.get("store", {}).get("total_skus", 12582)
    fishing_skus_fmt = f"{fishing_skus:,}".replace(",", ".")
    agro_skus = enriched_agro.get("store", {}).get("total_skus", 5955)
    agro_skus_fmt = f"{agro_skus:,}".replace(",", ".")
    motors_skus = enriched_motors.get("store", {}).get("total_skus", 6758)
    motors_skus_fmt = f"{motors_skus:,}".replace(",", ".")

    # 5. Gerar index.html enxuto (< 50 KB) com links para css/main.css e js/*.js com cache-busting
    print("[4/5] Gerando index.html modular e ultra leve (< 50 KB)...")
    build_ver = datetime.now().strftime("%Y%m%d%H%M%S")
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Central Mestre BRK - Gestão de Descrições & Vigilante Diário Shopify</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/main.css?v={build_ver}">
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen">

  <!-- ======================================================== -->
  <!-- BARRA SUPERIOR MESTRE                                    -->
  <!-- ======================================================== -->
  <header class="sticky top-0 z-40 bg-slate-950 text-white border-b border-slate-800 shadow-xl">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Linha 1: Seletor de Loja & Abas Principais -->
      <div class="py-2.5 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-2">
          <span class="text-slate-400 font-bold uppercase tracking-wider text-[10px]">Loja Ativa:</span>
          <div class="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button onclick="switchStore('brk_fishing')" id="pill-store-fishing" class="store-pill active px-3 py-1 rounded-lg font-bold flex items-center gap-1.5 transition-all bg-blue-600 text-white">
              <span>🎣 Fishing</span>
              <span id="header-skus-fishing" class="text-[10px] px-1.5 py-0.2 rounded-full bg-white/20">{fishing_skus_fmt} SKUs</span>
            </button>
            <button onclick="switchStore('brk_agro')" id="pill-store-agro" class="store-pill px-3 py-1 rounded-lg font-bold flex items-center gap-1.5 transition-all text-slate-400 hover:text-white">
              <span>🚜 Agro</span>
              <span id="header-skus-agro" class="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300">{agro_skus_fmt} SKUs</span>
            </button>
            <button onclick="switchStore('brk_motors')" id="pill-store-motors" class="store-pill px-3 py-1 rounded-lg font-bold flex items-center gap-1.5 transition-all text-slate-400 hover:text-white">
              <span>🏁 Motors</span>
              <span id="header-skus-motors" class="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300">{motors_skus_fmt} SKUs</span>
            </button>
          </div>
        </div>

        <!-- Abas de Navegação Principal (4 ABAS) -->
        <div class="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-xs">
          <button onclick="switchMainTab('tab-catalog')" id="btn-tab-catalog" class="main-tab active px-3 py-1.5 rounded-lg font-bold transition-all bg-slate-800 text-white flex items-center gap-1.5">
            <span>🛍️ Catálogo & Diagnóstico</span>
          </button>
          <button onclick="switchMainTab('tab-mass')" id="btn-tab-mass" class="main-tab px-3 py-1.5 rounded-lg font-bold transition-all text-slate-400 hover:text-white flex items-center gap-1.5">
            <span>⚡ Geração em Massa</span>
            <span id="badge-mass-count" class="bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded-full text-[10px] font-extrabold">0</span>
          </button>
          <button onclick="switchMainTab('tab-moldes')" id="btn-tab-moldes" class="main-tab px-3 py-1.5 rounded-lg font-bold transition-all text-slate-400 hover:text-white flex items-center gap-1.5">
            <span>📐 Moldes Mestres</span>
          </button>
          <button onclick="switchMainTab('tab-analytics')" id="btn-tab-analytics" class="main-tab px-3 py-1.5 rounded-lg font-bold transition-all text-slate-400 hover:text-white flex items-center gap-1.5">
            <span>📊 Análises & Monitoramento</span>
            <span class="bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded-full text-[10px] font-extrabold">08:00</span>
          </button>
        </div>
      </div>

      <!-- Linha 2: Header Principal com Cockpit e Monitor de Sincronização em Tempo Real (Por Segundos) -->
      <div class="py-3 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-xl shadow-lg shadow-blue-500/20">
            ⚡
          </div>
          <div>
            <h1 class="text-lg font-extrabold tracking-tight font-heading flex items-center gap-2">
              <span id="store-title-text">BRK Fishing</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold uppercase">Vigilante Diário Ativo</span>
            </h1>
            <p class="text-xs text-slate-400">Padronização de Descrições • Duplo Modo por SKU • Vercel Ready</p>
          </div>
        </div>

        <div class="flex items-center gap-3 flex-wrap">
          <!-- BUSCA GLOBAL DE SKU (3 LOJAS) -->
          <div id="sku-global-wrap" class="relative">
            <div class="flex items-center gap-2 bg-slate-900 border border-slate-700/80 rounded-2xl p-1.5 px-3 shadow-md">
              <span class="text-sm">🔎</span>
              <input type="text" id="sku-global-input" autocomplete="off" spellcheck="false" placeholder="Buscar SKU nas 3 lojas (ex: C02846BL)" class="bg-transparent text-white placeholder-slate-500 text-[11px] font-bold w-56 focus:outline-none" />
            </div>
            <div id="sku-global-results" class="hidden absolute right-0 mt-2 w-[26rem] max-h-96 overflow-y-auto bg-white text-slate-900 rounded-2xl border border-slate-200 shadow-2xl z-50"></div>
          </div>

          <!-- LIVE SYNC CONTROL CENTER (MONITOR POR SEGUNDOS) -->
          <div id="live-sync-panel" class="flex items-center gap-2 bg-slate-900 border border-slate-700/80 rounded-2xl p-1.5 px-3 shadow-md transition-all">
            <div class="flex items-center gap-2">
              <span class="relative flex h-2.5 w-2.5">
                <span id="live-sync-pulse" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span id="live-sync-dot" class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <div class="text-left">
                <span class="text-[9px] uppercase tracking-wider font-extrabold text-slate-400 block">Sincronização ao Vivo</span>
                <span id="live-sync-status-text" class="text-[11px] font-bold text-white flex items-center gap-1">
                  Ativo (<span id="live-sync-countdown" class="text-emerald-400 font-mono">15s</span>)
                </span>
              </div>
            </div>
            <div class="h-6 w-[1px] bg-slate-800 mx-1"></div>
            <select id="live-sync-interval" onchange="changeLiveSyncInterval(this.value)" class="bg-slate-800 text-slate-200 text-[11px] font-bold rounded-lg px-2 py-1 border border-slate-700 focus:outline-none cursor-pointer">
              <option value="10">A cada 10s</option>
              <option value="15" selected>A cada 15s</option>
              <option value="30">A cada 30s</option>
              <option value="60">A cada 60s</option>
              <option value="0">Pausado</option>
            </select>
            <button id="btn-sync-now" onclick="triggerManualLiveSync()" title="Verificar produtos novos na Shopify agora" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-[11px] font-extrabold shadow-sm transition-all flex items-center gap-1 active:scale-95">
              <span id="sync-icon" class="inline-block transition-transform duration-500">🔄</span>
              <span>Sincronizar</span>
            </button>
          </div>

          <!-- O BOTÃO UNIFICADO ANIMADO NO TOPO (COCKPIT) -->
          <div id="unified-button-cockpit" class="flex items-center gap-3 bg-slate-900 border border-slate-700/80 rounded-2xl p-1.5 px-3 unified-button-glow transition-all">
            <!-- Falha 1: Fotos Quebradas -->
            <div class="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-all" onclick="filterBrokenFromCockpit()" title="Filtrar produtos com fotos quebradas no corpo da descrição">
              <span class="relative flex h-2.5 w-2.5">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
              </span>
              <div class="text-left">
                <span class="text-[9px] uppercase tracking-wider font-extrabold text-slate-400 block">Fotos Quebradas</span>
                <span class="text-xs font-bold text-white flex items-center gap-1">
                  <span id="cockpit-broken-count" class="text-red-400 font-extrabold text-sm">--</span> Itens
                </span>
              </div>
            </div>

            <div class="h-6 w-[1px] bg-slate-800"></div>

            <!-- Falha 2: Alerta Sem Descrição -->
            <div class="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-all" onclick="filterEmptyFromCockpit()" title="Filtrar produtos sem descrição">
              <span class="relative flex h-2.5 w-2.5">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
              </span>
              <div class="text-left">
                <span class="text-[9px] uppercase tracking-wider font-extrabold text-amber-400 block">⚠️ Sem Descrição</span>
                <span class="text-xs font-bold text-white flex items-center gap-1">
                  <span id="cockpit-empty-count" class="text-amber-400 font-extrabold text-sm">--</span> Itens
                </span>
              </div>
            </div>

            <div class="h-6 w-[1px] bg-slate-800"></div>

            <div class="text-right">
              <span class="text-[9px] text-slate-400 block font-medium">Saúde</span>
              <span id="cockpit-health-badge" class="text-xs font-extrabold text-emerald-400">--%</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </header>

  <!-- ======================================================== -->
  <!-- SEÇÃO 1: ABA CATÁLOGO & DIAGNÓSTICO                      -->
  <!-- ======================================================== -->
  <main id="section-catalog" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <!-- CARROSSEL HORIZONTAL DE COLEÇÕES -->
    <section>
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-bold text-slate-900 font-heading">Coleções & Linhagens de Produtos</h2>
          <p class="text-xs text-slate-500">Selecione uma coleção para filtrar o catálogo</p>
        </div>
        <div class="flex gap-1.5">
          <button id="scroll-left" class="w-8 h-8 rounded-full border border-slate-200 bg-white hover:bg-slate-50 flex items-center justify-center text-slate-600 shadow-sm text-sm font-bold">‹</button>
          <button id="scroll-right" class="w-8 h-8 rounded-full border border-slate-200 bg-white hover:bg-slate-50 flex items-center justify-center text-slate-600 shadow-sm text-sm font-bold">›</button>
        </div>
      </div>
      <div id="categories-rail" class="flex gap-6 overflow-x-auto no-scrollbar py-2 scroll-smooth">
        <!-- Coleções Injetadas Via JavaScript -->
      </div>
    </section>

    <!-- BARRA DE PESQUISA E FILTROS DE DIAGNÓSTICO -->
    <section class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
      <div class="flex-1 min-w-[280px] relative">
        <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 text-sm">🔍</span>
        <input type="text" id="search-input" placeholder="Buscar por título, SKU Mestre (ex: BRK-), variantes ou tag..." class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium" />
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button data-filter="all" class="filter-btn active px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-900 text-white">Todos (<span id="count-all">0</span>)</button>
        <button data-filter="broken" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-red-50 text-red-700 hover:bg-red-100 border border-red-200">❌ Fotos Quebradas (<span id="count-broken">0</span>)</button>
        <button data-filter="empty" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200">⚠️ Sem Descrição (<span id="count-empty">0</span>)</button>
        <button data-filter="healthy" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200">✅ Saudáveis (<span id="count-healthy">0</span>)</button>
        <button data-filter="colado" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200" title="Descrições Modo B já coladas e confirmadas na vitrine">🛰️ Colados (<span id="count-colado">0</span>)</button>
        <button data-filter="recolar" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-orange-50 text-orange-700 hover:bg-orange-100 border border-orange-200" title="Modo B colado desatualizado ou sem marcador de rastreio: cole novamente">🔁 Recolar (<span id="count-recolar">0</span>)</button>
      </div>
      <div class="w-full flex flex-wrap items-center gap-3 pt-2 border-t border-slate-100">
        <button id="btn-live-agent" onclick="LiveAgent.refresh(true)" title="Lê a vitrine pública da loja (somente leitura) e atualiza o status real das descrições" class="px-3 py-1.5 bg-slate-900 hover:bg-slate-700 text-white rounded-xl text-[11px] font-extrabold transition-all active:scale-95">🛰️ Verificar descrições ao vivo</button>
        <span id="live-agent-status" class="text-[11px] font-semibold text-slate-500">🛰️ Aguardando verificação da vitrine…</span>
        <div class="h-4 w-[1px] bg-slate-200 hidden sm:block"></div>
        <button id="btn-tm-queue" onclick="sendBatchToTampermonkey(25)" title="Envia os próximos 25 produtos sem descrição para o Assistente Tampermonkey no Chrome" class="px-3 py-1.5 bg-gradient-to-r from-purple-700 to-indigo-700 hover:from-purple-600 hover:to-indigo-600 text-white rounded-xl text-[11px] font-extrabold shadow-sm transition-all flex items-center gap-1.5 active:scale-95">
          <span>⚡ Fila Tampermonkey (25)</span>
        </button>
        <button id="btn-tm-settings" onclick="openTampermonkeyModal()" title="Instruções e status do Userscript Tampermonkey" class="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-[11px] font-bold transition-all">
          <span>⚙️ Script</span>
        </button>
      </div>
    </section>

    <!-- GRID DE PRODUTOS -->
    <section>
      <div id="products-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <!-- Cards Injetados Via JavaScript -->
      </div>
      <div id="empty-state" class="hidden text-center py-16">
        <div class="text-4xl mb-3">🔍</div>
        <h3 class="text-base font-bold text-slate-800">Nenhum produto encontrado</h3>
        <p class="text-xs text-slate-500 mt-1">Tente ajustar seus termos de pesquisa ou filtros de diagnóstico.</p>
      </div>
    </section>

  </main>

  <!-- ======================================================== -->
  <!-- SEÇÃO 2: ABA GERAÇÃO EM MASSA POR SKU                    -->
  <!-- ======================================================== -->
  <main id="section-mass" class="hidden max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
    <div class="bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950 text-white p-6 rounded-3xl border border-slate-800 shadow-xl flex flex-wrap items-center justify-between gap-6">
      <div class="space-y-1.5 max-w-2xl">
        <span class="px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-300 text-[11px] font-extrabold uppercase tracking-wider border border-amber-500/30">Motor de Correção em Lote</span>
        <h2 class="text-2xl font-extrabold font-heading">Fila de Geração em Massa por SKU</h2>
        <p class="text-xs text-slate-300 leading-relaxed">
          Gere descrições em lote para todos os produtos sem texto ou com fotos quebradas da AWS S3. 
          O motor aplica automaticamente o <strong>Molde Mestre da Categoria</strong>, vincula as fotos oficiais do CDN Shopify e envia diretamente para o Assistente Tampermonkey v4.0 no Shopify Admin.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button onclick="executeMassBatch('mode_a_html')" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-2">
          <span>🛠️ Gerar Lote: Modo A</span>
          <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full">Preservar HTML</span>
        </button>
        <button onclick="executeMassBatch('mode_b_html')" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-2">
          <span>🚀 Gerar Lote: Modo B</span>
          <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full">3 Atos Conversão</span>
        </button>
        <button onclick="sendSelectedMassToTampermonkey()" class="px-4 py-2.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-2" title="Enviar os produtos selecionados diretamente para o Assistente Tampermonkey no Chrome">
          <span>⚡ Fila Tampermonkey</span>
        </button>
      </div>
    </div>

    <!-- TABELA DE PRODUTOS ALVO -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="p-4 border-b border-slate-100 flex items-center justify-between gap-4 bg-slate-50/50">
        <div class="flex items-center gap-2 text-xs font-bold text-slate-700">
          <input type="checkbox" id="check-all-mass" class="w-4 h-4 text-blue-600 rounded cursor-pointer" checked onchange="toggleSelectAllMass(this)" />
          <label for="check-all-mass" class="cursor-pointer">Selecionar Todos (<span id="mass-selected-count">0</span> selecionados)</label>
        </div>
        <div class="text-xs text-slate-500">
          Mostrando produtos com fotos quebradas ou sem descrição
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 text-slate-500 uppercase font-bold text-[10px] border-b border-slate-200">
            <tr>
              <th class="p-3.5 w-10 text-center">Sel</th>
              <th class="p-3.5">SKU Mestre / Produto</th>
              <th class="p-3.5">Variantes</th>
              <th class="p-3.5">Fotos CDN</th>
              <th class="p-3.5">Molde Mestre Recomendado</th>
              <th class="p-3.5">Diagnóstico</th>
              <th class="p-3.5 text-right">Ação</th>
            </tr>
          </thead>
          <tbody id="mass-table-body" class="divide-y divide-slate-100 font-medium">
            <!-- Linhas Injetadas Via JavaScript -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- ======================================================== -->
  <!-- SEÇÃO 3: ABA MOLDES MESTRES POR CATEGORIA                 -->
  <!-- ======================================================== -->
  <main id="section-moldes" class="hidden max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
    <div class="border-b border-slate-200 pb-4">
      <h2 class="text-xl font-extrabold text-slate-900 font-heading">Biblioteca de Moldes Mestres por Categoria</h2>
      <p class="text-xs text-slate-500 mt-1">Estruturas consagradas de alta conversão com ícones vetoriais SVG estilo Font Awesome, preservando 100% dos dados técnicos confirmados.</p>
    </div>

    <div id="moldes-cards-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Moldes Injetados Via JavaScript -->
    </div>
  </main>

  <!-- ======================================================== -->
  <!-- SEÇÃO 4: ABA ANÁLISES & MONITORAMENTO DIÁRIO              -->
  <!-- ======================================================== -->
  <main id="section-analytics" class="hidden max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <div class="bg-gradient-to-r from-slate-950 via-blue-950 to-slate-900 text-white p-6 rounded-3xl border border-slate-800 shadow-xl flex flex-wrap items-center justify-between gap-6">
      <div class="space-y-1.5 max-w-2xl">
        <div class="flex items-center gap-2">
          <span class="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-[11px] font-extrabold uppercase tracking-wider border border-emerald-500/30 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Auditoria 360° em Tempo Real • 3 Lojas
          </span>
          <span id="sentinel-last-run" class="text-xs text-slate-400 font-mono">Catálogo Oficial Auditado (6.242 Produtos)</span>
        </div>
        <h2 class="text-2xl font-extrabold font-heading">Painel de Auditoria & Conformidade</h2>
        <p class="text-xs text-slate-300 leading-relaxed">
          Diagnóstico preciso das 3 lojas Shopify (Fishing, Agro e Motors). Separa fotos reais de produto quebradas no S3 antigo (excluindo falsos-positivos de ícones SVG), produtos sem descrição, links externos proibidos e variantes órfãs.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button onclick="sendBatchToTampermonkey(25)" class="px-4 py-2.5 bg-purple-700 hover:bg-purple-600 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-2">
          <span>⚡ Enviar Lote para Tampermonkey (25)</span>
        </button>
      </div>
    </div>

    <!-- CARDS DE SAÚDE DAS 3 LOJAS -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white rounded-3xl border border-slate-200 p-6 product-shadow space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-xl">🎣 BRK Fishing</span>
          <span id="stat-fishing-health" class="text-base font-extrabold text-emerald-600">75.4%</span>
        </div>
        <div class="space-y-1.5 text-xs text-slate-600">
          <div class="flex justify-between"><span>Total de Produtos:</span><strong id="stat-fishing-skus" class="text-slate-900">2.148 produtos (11.799 SKUs)</strong></div>
          <div class="flex justify-between"><span>Fotos de Produto Quebradas:</span><strong id="stat-fishing-broken" class="text-red-600">339 produtos</strong></div>
          <div class="flex justify-between"><span>Sem Descrição:</span><strong id="stat-fishing-empty" class="text-amber-600">190 produtos</strong></div>
          <div class="flex justify-between"><span>Saudáveis / Modo B Pronto:</span><strong id="stat-fishing-fixes" class="text-emerald-600">1.619 saudáveis (100% Modo B)</strong></div>
        </div>
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div id="bar-fishing-health" class="bg-blue-600 h-full rounded-full" style="width: 75.4%;"></div>
        </div>
      </div>

      <div class="bg-white rounded-3xl border border-slate-200 p-6 product-shadow space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-xl">🚜 BRK Agro</span>
          <span id="stat-agro-health" class="text-base font-extrabold text-emerald-600">94.5%</span>
        </div>
        <div class="space-y-1.5 text-xs text-slate-600">
          <div class="flex justify-between"><span>Total de Produtos:</span><strong id="stat-agro-skus" class="text-slate-900">2.647 produtos (17.058 SKUs)</strong></div>
          <div class="flex justify-between"><span>Fotos de Produto Quebradas:</span><strong id="stat-agro-broken" class="text-red-600">1 produto</strong></div>
          <div class="flex justify-between"><span>Sem Descrição:</span><strong id="stat-agro-empty" class="text-amber-600">145 produtos</strong></div>
          <div class="flex justify-between"><span>Saudáveis / Modo B Pronto:</span><strong id="stat-agro-fixes" class="text-emerald-600">2.501 saudáveis (100% Modo B)</strong></div>
        </div>
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div id="bar-agro-health" class="bg-emerald-600 h-full rounded-full" style="width: 94.5%;"></div>
        </div>
      </div>

      <div class="bg-white rounded-3xl border border-slate-200 p-6 product-shadow space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold text-orange-600 bg-orange-50 px-2.5 py-1 rounded-xl">🏁 BRK Motors</span>
          <span id="stat-motors-health" class="text-base font-extrabold text-emerald-600">79.5%</span>
        </div>
        <div class="space-y-1.5 text-xs text-slate-600">
          <div class="flex justify-between"><span>Total de Produtos:</span><strong id="stat-motors-skus" class="text-slate-900">1.447 produtos (9.218 SKUs)</strong></div>
          <div class="flex justify-between"><span>Fotos de Produto Quebradas:</span><strong id="stat-motors-broken" class="text-red-600">100 produtos</strong></div>
          <div class="flex justify-between"><span>Sem Descrição:</span><strong id="stat-motors-empty" class="text-amber-600">196 produtos</strong></div>
          <div class="flex justify-between"><span>Saudáveis / Modo B Pronto:</span><strong id="stat-motors-fixes" class="text-emerald-600">1.151 saudáveis (100% Modo B)</strong></div>
        </div>
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div id="bar-motors-health" class="bg-orange-600 h-full rounded-full" style="width: 79.5%;"></div>
        </div>
      </div>
    </div>

    <!-- TABELA DE CONFORMIDADE RIGOROSA -->
    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-slate-50/50">
        <div>
          <h3 class="text-sm font-extrabold text-slate-900 font-heading">Auditoria de Conformidade por SKU</h3>
          <p class="text-xs text-slate-500">Detecta fotos de produto quebradas no S3 antigo, produtos sem descrição, links proibidos e variantes sem código.</p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button onclick="filterAuditTable('all')" id="audit-btn-all" class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-900 text-white">Todos</button>
          <button onclick="filterAuditTable('prohibited')" id="audit-btn-prohibited" class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-red-50 text-red-700 hover:bg-red-100 border border-red-200">Links Proibidos</button>
          <button onclick="filterAuditTable('orphaned')" id="audit-btn-orphaned" class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200">SKUs Órfãos</button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 text-slate-500 uppercase font-bold text-[10px] border-b border-slate-200">
            <tr>
              <th class="p-3.5">SKU Mestre</th>
              <th class="p-3.5">Produto</th>
              <th class="p-3.5">Loja</th>
              <th class="p-3.5">Diagnóstico de Risco</th>
              <th class="p-3.5">Detalhe da Ocorrência</th>
              <th class="p-3.5 text-right">Ação</th>
            </tr>
          </thead>
          <tbody id="audit-table-body" class="divide-y divide-slate-100 font-medium">
            <!-- Injetado Via JavaScript -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- ======================================================== -->
  <!-- MODAL DE PRODUTO                                         -->
  <!-- ======================================================== -->
  <div id="product-modal" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200">
      
      <!-- Cabeçalho do Modal -->
      <div class="p-5 border-b border-slate-100 flex items-center justify-between gap-4 bg-slate-900 text-white">
        <div class="min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span id="modal-store-badge" class="px-2 py-0.5 rounded-md bg-blue-600 text-white font-bold text-[10px] uppercase tracking-wider">BRK Fishing</span>
            <span id="modal-sku-badge" class="px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 font-mono text-[10px] font-bold border border-blue-500/30">SKU: --</span>
            <span id="modal-variants-badge" class="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[10px] font-semibold">8 Variantes</span>
            <span id="modal-archetype-badge" class="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">Molde UV50+</span>
            <span id="modal-source-badge" class="px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 text-[10px] font-bold border border-purple-500/30">✨ Molde Homólogo</span>
          </div>
          <h3 id="modal-title" class="text-base font-extrabold truncate">Título do Produto</h3>
        </div>
        <button onclick="closeProductModal()" class="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center text-sm font-bold transition-all">✕</button>
      </div>

      <!-- Faixa de Fotos Oficiais -->
      <div class="px-6 py-2.5 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-3">
          <span class="text-[10px] font-extrabold uppercase text-slate-500 tracking-wider">Fotos no Catálogo do Site:</span>
          <div id="modal-gallery-thumbs" class="flex items-center gap-2"></div>
        </div>
        <div class="flex items-center gap-2">
          <button id="btn-sync-live-photos" onclick="syncLiveProductImages(this)" class="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 font-bold text-[11px] flex items-center gap-1.5 transition-all shadow-sm cursor-pointer" title="Consultar a Shopify em tempo real e atualizar as fotos agora">
            <span>🔄</span> Sincronizar Fotos da Loja
          </button>
          <span id="modal-photos-count-badge" class="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700">3 Fotos no CDN Shopify</span>
        </div>
      </div>

      <!-- Barra de Controle do Duplo Modo e Ações -->
      <div class="px-6 py-3 bg-slate-100 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200 shadow-sm">
          <button id="btn-mode-b" onclick="switchModalMode('b')" class="px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-emerald-600 text-white shadow-sm flex items-center gap-1.5">
            <span>🚀 Modo B: 3 Atos (SVG Font Awesome)</span>
          </button>
          <button id="btn-mode-a" onclick="switchModalMode('a')" class="px-3.5 py-1.5 rounded-lg font-extrabold transition-all text-slate-600 hover:text-slate-900 flex items-center gap-1.5">
            <span>🛠️ Modo A: Preservar HTML</span>
          </button>
          <button id="btn-mode-orig" onclick="switchModalMode('orig')" class="px-3.5 py-1.5 rounded-lg font-bold transition-all text-slate-400 hover:text-red-600 flex items-center gap-1.5">
            <span>❌ Original (Quebrado)</span>
          </button>
          <button id="btn-mode-diff" onclick="switchModalMode('diff')" class="px-3.5 py-1.5 rounded-lg font-bold transition-all text-indigo-700 hover:text-indigo-900 hover:bg-indigo-50 flex items-center gap-1.5" title="Comparador visual lado a lado (Original vs Novo)">
            <span>⚖️ Comparador (Diff)</span>
          </button>
        </div>

        <div class="flex items-center gap-2">
          <a id="modal-open-admin-btn" href="#" target="_blank" class="px-3.5 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all text-xs" title="Abrir produto diretamente no Admin da Shopify desta loja específica">
            <span>🔗</span>
            <span>Admin Shopify ↗</span>
          </a>
          <button id="modal-save-shopify-direct-btn" onclick="saveDirectToShopify(this)" class="px-3.5 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all transform active:scale-95 text-xs" title="Atualiza EXCLUSIVAMENTE o campo body_html deste produto na Shopify">
            <span>⚡</span>
            <span>Salvar Direto</span>
          </button>
          <button id="modal-copy-markdown-btn" onclick="copyCurrentModalMarkdown(this)" class="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-300 rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all transform active:scale-95 text-xs" title="Copiar descrição completa em formato Markdown limpo">
            <span class="copy-icon">📝</span>
            <span class="copy-label">Copiar Markdown</span>
          </button>
          <button id="modal-header-copy-btn" onclick="copyCurrentModalHTML(this)" class="px-3.5 py-1.5 bg-slate-900 hover:bg-black text-white rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all transform active:scale-95 text-xs">
            <span class="copy-icon">📋</span>
            <span class="copy-label">Copiar HTML</span>
          </button>
          <button onclick="downloadCurrentProductCSV()" class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all text-xs">
            <span>📥 CSV</span>
          </button>
        </div>
      </div>

      <!-- Corpo do Modal -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <div id="modal-mode-banner" class="p-3.5 rounded-xl border text-xs flex items-center justify-between bg-emerald-50 border-emerald-200 text-emerald-800">
          <div class="flex items-center gap-2">
            <span class="text-base">✨</span>
            <span id="modal-mode-desc"><strong>Modo B Ativo:</strong> Descrição reestruturada em 3 Atos narrativos com no máximo 3 fotos CDN oficiais e tabela de especificações.</span>
          </div>
          <span class="text-[10px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">Pronto para Shopify</span>
        </div>

        <!-- PAINEL SMART BUNKER LINKER -->
        <details id="bunker-linker-details" class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-4 border border-indigo-500/40 shadow-lg">
          <summary class="text-xs font-bold text-indigo-300 cursor-pointer hover:text-white select-none flex items-center justify-between">
            <span class="flex items-center gap-2">
              <span class="text-base">⚡</span>
              <span>Injetor de Mídias do BRK Bunker (Cloudflare Worker)</span>
              <span class="px-2 py-0.5 rounded-full bg-indigo-500/30 text-[10px] font-mono border border-indigo-400/30 text-indigo-200">Smart Linker</span>
            </span>
            <span class="text-[11px] text-slate-400 font-normal">Clique para colar links do Bunker ▾</span>
          </summary>
          
          <div class="mt-4 pt-3 border-t border-indigo-900/60 space-y-3">
            <div class="space-y-1">
              <label class="text-[11px] font-extrabold uppercase tracking-wider text-indigo-200 block">
                Colar Links do Bunker (Cole 1, 2 ou 3 links separados por linha ou espaço):
              </label>
              <textarea id="bunker-bulk-input" rows="2" placeholder="https://brk-bunker.allexadriel.workers.dev/images/...&#10;https://brk-bunker.allexadriel.workers.dev/images/..." class="w-full bg-slate-950/90 border border-indigo-500/50 rounded-xl p-2.5 text-xs text-indigo-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 font-mono"></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div class="space-y-1">
                <span class="text-[10px] font-bold text-emerald-400 block">Posição 1 (Hero / Design):</span>
                <input type="text" id="bunker-slot-1" placeholder="URL da Foto 1..." class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-[11px] text-slate-200 font-mono focus:border-indigo-400 focus:outline-none" />
              </div>
              <div class="space-y-1">
                <span class="text-[10px] font-bold text-blue-400 block">Posição 2 (Performance / UV):</span>
                <input type="text" id="bunker-slot-2" placeholder="URL da Foto 2..." class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-[11px] text-slate-200 font-mono focus:border-indigo-400 focus:outline-none" />
              </div>
              <div class="space-y-1">
                <span class="text-[10px] font-bold text-amber-400 block">Posição 3 (Durabilidade):</span>
                <input type="text" id="bunker-slot-3" placeholder="URL da Foto 3..." class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-[11px] text-slate-200 font-mono focus:border-indigo-400 focus:outline-none" />
              </div>
            </div>

            <div class="flex items-center justify-between pt-1">
              <span class="text-[10px] text-slate-400">Dimensões 4:3 responsivas blindadas, alinhadas automaticamente sem cortes.</span>
              <button onclick="applyBunkerLinksToModal()" class="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-1.5">
                <span>⚡ Aplicar Fotos do Bunker na Descrição</span>
              </button>
            </div>
          </div>
        </details>

        <!-- Área de Renderização HTML -->
        <div class="border border-slate-200 rounded-2xl p-6 bg-white shadow-inner">
          <div id="modal-rendered-content"></div>
        </div>

        <!-- Código Fonte HTML -->
        <details class="bg-slate-50 rounded-2xl border border-slate-200 p-4">
          <summary class="text-xs font-bold text-slate-600 cursor-pointer hover:text-slate-900 select-none">Ver Código Fonte HTML Completo</summary>
          <pre id="modal-source-code" class="mt-3 p-3 bg-slate-900 text-slate-200 text-[11px] rounded-xl overflow-x-auto font-mono max-h-48"></pre>
        </details>

      </div>

      <!-- Rodapé Fixo do Modal -->
      <div class="px-6 py-3.5 bg-slate-900 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs z-10 shrink-0">
        <div class="flex items-center gap-2 text-slate-400">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="text-[11px] font-mono" id="modal-footer-sku-info">SKU Mestre: Pronto para Shopify</span>
        </div>
        <div class="flex items-center gap-2">
          <button id="modal-footer-copy-md-btn" onclick="copyCurrentModalMarkdown(this)" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-emerald-500/40 rounded-xl font-bold flex items-center gap-2 transition-all transform active:scale-95 text-xs">
            <span class="copy-icon">📝</span>
            <span class="copy-label">Copiar Markdown</span>
          </button>
          <button id="modal-footer-copy-btn" onclick="copyCurrentModalHTML(this)" class="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl font-extrabold flex items-center gap-2 shadow-lg shadow-emerald-950/40 transition-all transform active:scale-95 text-xs">
            <span class="copy-icon">📋</span>
            <span class="copy-label">Copiar Código HTML Shopify</span>
          </button>
          <button onclick="downloadCurrentProductCSV()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl font-bold flex items-center gap-1.5 transition-all text-xs">
            <span>📥 Baixar CSV</span>
          </button>
        </div>
      </div>

    </div>
  </div>

  <!-- TOAST NOTIFICATION -->
  <div id="toast" class="toast-msg">
    <span>✅</span>
    <span id="toast-text">Ação concluída com sucesso!</span>
  </div>

  <!-- ======================================================== -->
  <!-- SCRIPTS MODULARES DISTRIBUÍDOS                           -->
  <!-- ======================================================== -->
  <script src="js/svg_icons.js?v={build_ver}"></script>
  <script src="data/stores/brk_fishing.js?v={build_ver}"></script>
  <script defer src="data/stores/brk_agro.js?v={build_ver}"></script>
  <script defer src="data/stores/brk_motors.js?v={build_ver}"></script>
  <script src="data/stores/moldes.js?v={build_ver}"></script>
  <script src="data/stores/analytics.js?v={build_ver}"></script>
  <script src="js/store_loader.js?v={build_ver}"></script>
  <script src="js/modal.js?v={build_ver}"></script>
  <script src="js/app.js?v={build_ver}"></script>
  <script src="js/live_agent.js?v={build_ver}"></script>

</body>
</html>"""

    # Destinos de sincronização de index.html
    dest_onedrive = os.path.join(base_repo_dir, "index.html")
    dest_list = [dest_onedrive]

    for dest in dest_list:
        try:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(html_template)
            f_size = os.path.getsize(dest)
            print(f"  -> {dest} gravado ({round(f_size/1024, 1)} KB).")
        except Exception as e:
            print(f"  -> Alerta ao gravar {dest}: {e}")

    # 6. Sincronização com repositório GitHub (com proteção anti-travamento)
    skip_sync = any(arg in ("--no-push", "--skip-sync") for arg in sys.argv[1:])
    if skip_sync:
        print("[5/5] Sincronização GitHub ignorada via flag (--no-push / --skip-sync).")
    else:
        print("[5/5] Sincronizando estrutura modular com repositório GitHub...")
        target_onedrive_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            sync_script = os.path.join(target_onedrive_dir, "sync_github.py")
            if os.path.exists(sync_script):
                print("[GITHUB SYNC] Executando sync_github.py...")
                cli_args = [a for a in sys.argv[1:] if not a.startswith("--")]
                commit_msg = cli_args[0] if cli_args else f"fix: auditoria 360 e otimizacao de compilacao [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                env = os.environ.copy()
                env["GIT_TERMINAL_PROMPT"] = "0"
                env["GCM_INTERACTIVE"] = "never"
                res = subprocess.run(
                    [sys.executable, sync_script, commit_msg],
                    cwd=target_onedrive_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=60,
                    env=env
                )
                print("  -> Saída do Git Sync:\n" + (res.stdout or "").strip())
                if res.stderr:
                    print("  -> Avisos Git Sync:\n" + res.stderr.strip())
        except subprocess.TimeoutExpired:
            print("  -> [AVISO] Git push excedeu o tempo limite de 60s (compilação local concluída normalmente).")
        except Exception as e:
            print(f"  -> Erro na sincronização com GitHub: {e}")

    print("[CONCLUÍDO] Compilação modular v5.0 finalizada com sucesso absoluto!")

if __name__ == "__main__":
    build_dist()
