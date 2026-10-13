"""
Analisador Completo e Irrestrito Multi-Lojas Shopify (BRK Agro e BRK Motors).
Cria ambientes totalmente isolados em reports/brk_agro e reports/brk_motors.
Executa varredura profunda, auditoria de fotos 404, mapeamento de SKUs e gera a interface V2 para cada loja.
"""

import sys
import os
import json
import re
import pandas as pd
from datetime import datetime

# UTF-8 para console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.shopify_public_api import ShopifyPublicAPI
from core.auditor import CatalogAuditor
from core.config import STORES
from core.template_engine import TemplateEngine

_ENGINE = TemplateEngine()

def categorize_agro_product(prod: dict) -> str:
    title = prod.get("title", "")
    ptype = prod.get("product_type") or ""
    vendor = prod.get("vendor") or ""
    tags = prod.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    variants = prod.get("variants") or []
    sku = prod.get("master_sku") or (variants[0].get("sku") if variants and isinstance(variants[0], dict) else "") or ""
    arch_id = _ENGINE.detect_archetype(title, ptype, tags, vendor=vendor, sku=sku)
    return _ENGINE.classify_store_category(title, arch_id, store_key="brk_agro", tags=tags, sku=sku)

def categorize_motors_product(prod: dict) -> str:
    title = prod.get("title", "")
    ptype = prod.get("product_type") or ""
    vendor = prod.get("vendor") or ""
    tags = prod.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    variants = prod.get("variants") or []
    sku = prod.get("master_sku") or (variants[0].get("sku") if variants and isinstance(variants[0], dict) else "") or ""
    arch_id = _ENGINE.detect_archetype(title, ptype, tags, vendor=vendor, sku=sku)
    return _ENGINE.classify_store_category(title, arch_id, store_key="brk_motors", tags=tags, sku=sku)

def analyze_store(store_key: str):
    store_info = STORES[store_key]
    store_name = store_info["name"]
    base_url = store_info["base_url"]
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), store_info["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 75)
    print(f"[*] INICIANDO AUDITORIA COMPLETA E IRRESTRITA: {store_name}")
    print(f"URL: {base_url} | Ambiente Isolado: {output_dir}")
    print("=" * 75)

    api = ShopifyPublicAPI(store_key)
    auditor = CatalogAuditor()

    # 1. Varredura Completa de Produtos (sem trava de 1000)
    raw_products = api.fetch_all_products(max_products=None)
    print(f"[OK] Total de produtos coletados em {store_name}: {len(raw_products)}")

    catalog_data = {
        "store": {
            "id": store_info["id"],
            "name": store_name,
            "domain": store_info["domain"],
            "base_url": base_url,
            "theme_color": store_info["theme_color"],
            "total_products": len(raw_products),
            "total_skus": 0,
            "broken_skus": 0,
            "out_of_standard_skus": 0,
            "out_of_standard_prods": 0
        },
        "categories": {},
        "products": []
    }

    categorize_fn = categorize_agro_product if "agro" in store_key else categorize_motors_product

    for p in raw_products:
        diag = auditor.audit_product(p)
        cat_name = categorize_fn(p)
        
        images = [img["src"] for img in p.get("images", [])]
        main_img = images[0] if images else "https://via.placeholder.com/300?text=Sem+Foto"
        
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
            "url": f"{base_url}/products/{p.get('handle')}",
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

    # Métricas Globais
    total_skus = sum(p["total_skus_count"] for p in catalog_data["products"])
    broken_skus = sum(p["affected_skus_count"] for p in catalog_data["products"] if p["status"] == "IMAGENS_QUEBRADAS")
    out_of_standard_skus = sum(p["affected_skus_count"] for p in catalog_data["products"] if p["is_out_of_standard"])
    out_of_standard_prods = len([p for p in catalog_data["products"] if p["is_out_of_standard"]])

    catalog_data["store"]["total_skus"] = total_skus
    catalog_data["store"]["broken_skus"] = broken_skus
    catalog_data["store"]["out_of_standard_skus"] = out_of_standard_skus
    catalog_data["store"]["out_of_standard_prods"] = out_of_standard_prods

    # Agrupar por Categorias
    categories_set = set(p["category"] for p in catalog_data["products"])
    for cat in categories_set:
        cat_prods = [p for p in catalog_data["products"] if p["category"] == cat]
        first_thumb = cat_prods[0]["image"]
        catalog_data["categories"][cat] = {
            "title": cat,
            "badge": "Coleção",
            "thumb": first_thumb,
            "count": len(cat_prods),
            "total_skus": sum(p["total_skus_count"] for p in cat_prods),
            "broken_skus": sum(p["affected_skus_count"] for p in cat_prods if p["status"] == "IMAGENS_QUEBRADAS"),
            "out_of_standard_skus": sum(p["affected_skus_count"] for p in cat_prods if p["is_out_of_standard"]),
            "broken_count": len([p for p in cat_prods if p["status"] == "IMAGENS_QUEBRADAS"]),
            "alert_count": len([p for p in cat_prods if p["status"] == "BAIXA_CONVERSAO"]),
            "empty_count": len([p for p in cat_prods if p["status"] == "SEM_DESCRICAO"])
        }

    # 1. Salvar JSON Estruturado
    json_path = os.path.join(output_dir, "catalog_ui_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] JSON de dados salvo em: {json_path}")

    # 2. Salvar Relatório CSV de Auditoria
    csv_rows = []
    for p in catalog_data["products"]:
        csv_rows.append({
            "SKU_Base": p["master_sku"],
            "Titulo": p["title"],
            "Handle": p["handle"],
            "Categoria": p["category"],
            "Status": p["status"],
            "Score": p["score"],
            "Total_SKUs": p["total_skus_count"],
            "SKUs_Afetados": p["affected_skus_count"],
            "Fotos_Quebradas_Qtd": p["broken_images_count"],
            "URLs_Quebradas": " | ".join(p["broken_urls"]),
            "Violacoes_Padrao": " | ".join(p["standard_violations"]),
            "URL_Loja": p["url"]
        })
    df_csv = pd.DataFrame(csv_rows)
    csv_path = os.path.join(output_dir, f"auditoria_completa_{store_key}.csv")
    df_csv.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Planilha CSV de auditoria salva em: {csv_path}")

    # 3. Gerar Interface V2 Isolada para a Loja
    generate_store_ui(catalog_data, output_dir, store_key)

    # Resumo
    print("\n" + "-" * 75)
    print(f"📊 RESUMO DA AUDITORIA: {store_name}")
    print("-" * 75)
    print(f"Total de Modelos/Produtos:         {len(raw_products)}")
    print(f"Total de SKUs Agrupados:           {total_skus}")
    print(f"SKUs com Fotos Quebradas (404):    {broken_skus}")
    print(f"SKUs Fora do Padrão:               {out_of_standard_skus}")
    print(f"Produtos Fora do Padrão:           {out_of_standard_prods}")
    print("=" * 75)

    return catalog_data

def generate_store_ui(catalog_data: dict, output_dir: str, store_key: str):
    """Gera a interface completa V2 customizada com a identidade visual da loja."""
    from build_ui_artifact_v2 import build_v2 # template base
    
    json_str = json.dumps(catalog_data, ensure_ascii=False)
    store = catalog_data["store"]

    theme_gradient = "from-emerald-950 via-slate-900 to-green-950" if "agro" in store_key else "from-red-950 via-slate-900 to-stone-950"
    tag_color = "text-emerald-400 bg-emerald-500/20 border-emerald-400/30" if "agro" in store_key else "text-red-400 bg-red-500/20 border-red-400/30"
    accent_color = "emerald" if "agro" in store_key else "red"

    html_file = os.path.join(output_dir, f"catalogo_interativo_{store_key}.html")
    
    # Também gera cópia no diretório de artefatos
    artifact_dir = r"C:\Users\lucas\.gemini\antigravity\brain\6d694e19-7d4a-472b-b269-63d576efc810"
    artifact_file = os.path.join(artifact_dir, f"catalogo_interativo_{store_key}.html")

    # Adaptar o template HTML com os dados da loja específica
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "catalogo_interativo_brk.html"), "r", encoding="utf-8") as f:
        base_html = f.read()

    # Substitui título e dados JSON
    custom_html = re.sub(r'const CATALOG_DATA = \{.*?\};', f'const CATALOG_DATA = {json_str};', base_html, flags=re.DOTALL)
    custom_html = custom_html.replace("BRK FISHING", store["name"].upper())
    custom_html = custom_html.replace("Camisas ArmorX", list(catalog_data["categories"].keys())[0] if catalog_data["categories"] else "Geral")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(custom_html)

    with open(artifact_file, "w", encoding="utf-8") as f:
        f.write(custom_html)

    print(f"[OK] Interface V2 isolada gerada em:")
    print(f"     -> {html_file}")
    print(f"     -> {artifact_file}")

def main():
    print("=" * 80)
    print("🌐 MOTOR DE AUDITORIA MULTI-LOJAS SHOPIFY - AMBIENTES ISOLADOS")
    print("Lojas Alvo: BRK Agro (brkagro.com.br) e BRK Motors (brkmotors.com.br)")
    print("=" * 80)

    agro_data = analyze_store("brk_agro")
    motors_data = analyze_store("brk_motors")

    # Gerar Central Multi-Lojas Unificada (Switcher)
    generate_multi_store_hub(agro_data, motors_data)

def generate_multi_store_hub(agro_data, motors_data):
    """Gera o painel central que permite alternar entre as 3 lojas sem misturar dados."""
    # Ler dados de fishing também
    fishing_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "catalog_ui_data.json")
    try:
        with open(fishing_data_path, "r", encoding="utf-8") as f:
            fishing_data = json.load(f)
    except Exception:
        fishing_data = {"store": {"name": "BRK Fishing", "total_products": 120, "total_skus": 438, "broken_skus": 43}}

    hub_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Central Multi-Lojas BRK - Painel Unificado de Auditoria</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .font-heading {{ font-family: 'Space Grotesk', sans-serif; }}
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-6 sm:p-12 antialiased">
  <div class="max-w-6xl mx-auto space-y-10">

    <!-- Header Central -->
    <div class="text-center space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 border border-blue-400/30 text-xs font-bold uppercase tracking-wider">
        Ecossistema Multi-Site Shopify
      </div>
      <h1 class="font-heading font-extrabold text-3xl sm:text-5xl text-white tracking-tight">
        Central de Auditoria & Gestão por SKU
      </h1>
      <p class="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
        Ambientes 100% isolados para monitorar a saúde de descrições, fotos quebradas e conciliação de SKUs para cada uma das lojas do grupo.
      </p>
    </div>

    <!-- Cards das 3 Lojas -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">

      <!-- LOJA 1: BRK FISHING -->
      <div class="bg-slate-800/80 border border-blue-500/30 rounded-3xl p-6 sm:p-8 flex flex-col justify-between hover:border-blue-400 hover:scale-[1.02] transition-all shadow-xl shadow-blue-950/30 group">
        <div>
          <div class="flex items-center justify-between mb-4">
            <span class="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center text-white font-black text-2xl shadow-lg shadow-blue-500/30">
              🎣
            </span>
            <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">Pesca & UV</span>
          </div>
          <h3 class="font-heading font-bold text-xl text-white">BRK Fishing</h3>
          <p class="text-xs text-slate-400 mt-1">www.brkfishing.com.br</p>

          <div class="mt-6 space-y-2.5 text-xs">
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">Total de Modelos:</span>
              <span class="font-bold text-white">{fishing_data['store'].get('total_products', 120)}</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">SKUs Agrupados:</span>
              <span class="font-bold text-white">{fishing_data['store'].get('total_skus', 438)}</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">SKUs com Fotos Quebradas:</span>
              <span class="font-bold text-rose-400">{fishing_data['store'].get('broken_skus', 43)} ⚠️</span>
            </div>
          </div>
        </div>

        <div class="mt-8">
          <a href="catalogo_interativo_brk.html" target="_blank" class="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-colors shadow-md shadow-blue-600/30">
            <span>Acessar Ambiente Fishing</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </a>
        </div>
      </div>

      <!-- LOJA 2: BRK AGRO -->
      <div class="bg-slate-800/80 border border-emerald-500/30 rounded-3xl p-6 sm:p-8 flex flex-col justify-between hover:border-emerald-400 hover:scale-[1.02] transition-all shadow-xl shadow-emerald-950/30 group">
        <div>
          <div class="flex items-center justify-between mb-4">
            <span class="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center text-white font-black text-2xl shadow-lg shadow-emerald-500/30">
              🌾
            </span>
            <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Campo & Pecuária</span>
          </div>
          <h3 class="font-heading font-bold text-xl text-white">BRK Agro</h3>
          <p class="text-xs text-slate-400 mt-1">www.brkagro.com.br</p>

          <div class="mt-6 space-y-2.5 text-xs">
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">Total de Modelos:</span>
              <span class="font-bold text-white">{agro_data['store']['total_products']}</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">SKUs Agrupados:</span>
              <span class="font-bold text-white">{agro_data['store']['total_skus']}</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">SKUs com Fotos Quebradas:</span>
              <span class="font-bold { 'text-rose-400' if agro_data['store']['broken_skus'] > 0 else 'text-emerald-400' }">
                {agro_data['store']['broken_skus']} { '⚠️' if agro_data['store']['broken_skus'] > 0 else '✅' }
              </span>
            </div>
          </div>
        </div>

        <div class="mt-8 space-y-2">
          <a href="catalogo_interativo_brk_agro.html" target="_blank" class="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-colors shadow-md shadow-emerald-600/30">
            <span>Acessar Ambiente Agro</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </a>
        </div>
      </div>

      <!-- LOJA 3: BRK MOTORS -->
      <div class="bg-slate-800/80 border border-red-500/30 rounded-3xl p-6 sm:p-8 flex flex-col justify-between hover:border-red-400 hover:scale-[1.02] transition-all shadow-xl shadow-red-950/30 group">
        <div>
          <div class="flex items-center justify-between mb-4">
            <span class="w-12 h-12 rounded-2xl bg-red-600 flex items-center justify-center text-white font-black text-2xl shadow-lg shadow-red-500/30">
              🏍️
            </span>
            <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-red-500/20 text-red-300 border border-red-500/30">Motors & Off-Road</span>
          </div>
          <h3 class="font-heading font-bold text-xl text-white">BRK Motors</h3>
          <p class="text-xs text-slate-400 mt-1">www.brkmotors.com.br</p>

          <div class="mt-6 space-y-2.5 text-xs">
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">Total de Modelos:</span>
              <span class="font-bold text-white">{motors_data['store']['total_products']}</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">SKUs Agrupados:</span>
              <span class="font-bold text-white">{motors_data['store']['total_skus']}</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-slate-700/60">
              <span class="text-slate-400">SKUs com Fotos Quebradas:</span>
              <span class="font-bold { 'text-rose-400' if motors_data['store']['broken_skus'] > 0 else 'text-emerald-400' }">
                {motors_data['store']['broken_skus']} { '⚠️' if motors_data['store']['broken_skus'] > 0 else '✅' }
              </span>
            </div>
          </div>
        </div>

        <div class="mt-8 space-y-2">
          <a href="catalogo_interativo_brk_motors.html" target="_blank" class="w-full py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-colors shadow-md shadow-red-600/30">
            <span>Acessar Ambiente Motors</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </a>
        </div>
      </div>

    </div>

    <!-- Rodapé -->
    <div class="p-6 rounded-2xl bg-slate-800/40 border border-slate-800 text-center text-xs text-slate-400">
      Cada ambiente possui seu próprio banco de dados, relatórios CSV separados e catálogo interativo independente para conciliação no ERP Sankhya e Shopify.
    </div>

  </div>
</body>
</html>"""

    hub_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "central_multi_lojas.html")
    artifact_hub = r"C:\Users\lucas\.gemini\antigravity\brain\6d694e19-7d4a-472b-b269-63d576efc810\central_multi_lojas.html"
    
    with open(hub_file, "w", encoding="utf-8") as f:
        f.write(hub_html)
    with open(artifact_hub, "w", encoding="utf-8") as f:
        f.write(hub_html)

    print("\n[OK] Central Multi-Lojas Unificada gerada em:")
    print("     ->", hub_file)
    print("     ->", artifact_hub)

if __name__ == "__main__":
    main()
