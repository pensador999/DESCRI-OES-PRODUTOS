"""
Corretor e Verticalizador Universal Multi-Lojas Shopify (BRK Fishing, BRK Agro, BRK Motors).
Localiza produtos com fotos quebradas ou fora do padrão,
extrai as top 3 fotos da CDN oficial da própria loja,
aplica o copywriting especializado do nicho e compila o CSV pronto para importação.
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

# UTF-8 para console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.shopify_public_api import ShopifyPublicAPI
from core.auditor import CatalogAuditor
from core.image_harvester import ImageHarvester
from core.copy_transformer import CopyTransformer
from core.html_builder import HTMLBuilder
from core.config import STORES

def run_fixer(store_key: str = "brk_motors", limit: int = None):
    store_info = STORES.get(store_key, STORES["brk_motors"])
    store_name = store_info["name"]
    base_url = store_info["base_url"]
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), store_info["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print(f"🔧 CORRETOR & VERTICALIZADOR UNIVERSAL - {store_name.upper()}")
    print(f"Ambiente Isolado: {output_dir}")
    print("=" * 80)

    # 1. Carregar dados da auditoria isolada
    data_path = os.path.join(output_dir, "catalog_ui_data.json")
    if not os.path.exists(data_path):
        print(f"[!] Arquivo de dados não encontrado em {data_path}. Execute multi_store_analyzer.py primeiro.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        catalog_data = json.load(f)

    # Identificar produtos prioritários para correção (Fotos Quebradas 404)
    target_prods = [p for p in catalog_data["products"] if p["status"] == "IMAGENS_QUEBRADAS"]
    if not target_prods:
        print("[!] Nenhum produto com fotos 404 encontrado. Selecionando itens fora do padrão...")
        target_prods = [p for p in catalog_data["products"] if p["is_out_of_standard"]]

    if limit and len(target_prods) > limit:
        target_prods = target_prods[:limit]

    print(f"[*] Total de produtos a corrigir e verticalizar: {len(target_prods)}")

    harvester = ImageHarvester()
    transformer = CopyTransformer()
    builder = HTMLBuilder()
    auditor = CatalogAuditor()

    csv_rows = []
    comparisons = []

    for idx, prod in enumerate(target_prods, 1):
        title = prod["title"]
        handle = prod["handle"]
        old_body = prod.get("body_html", "")

        # 1. Obter dados completos do produto para pegar galeria de imagens
        images = [{"src": src} for src in prod.get("gallery", [])]
        prod_data_full = {
            "title": title,
            "handle": handle,
            "images": images,
            "body_html": old_body
        }

        # 2. Selecionar até 3 fotos da CDN oficial
        selected_images = harvester.select_product_images(prod_data_full, max_images=3)

        # 3. Gerar Copywriting Especializado do Nicho (Agro, Motors ou Fishing)
        enriched_copy = transformer.generate_3_act_copy(prod_data_full, selected_images, store_key=store_key)

        # 4. Compilar HTML Blindado nos Padrões Shopify
        new_html = builder.build_shopify_html(enriched_copy)

        # 5. Re-auditar nova descrição
        temp = dict(prod)
        temp["body_html"] = new_html
        new_diag = auditor.audit_product(temp)

        csv_rows.append({
            "Handle": handle,
            "Title": title,
            "Body (HTML)": new_html,
            "Vendor": store_name,
            "Product Category": prod.get("category", "Vestuário"),
            "Type": prod.get("archetype", "Equipamento"),
            "Tags": "",
            "Published": "true"
        })

        comparisons.append({
            "id": prod["id"],
            "title": title,
            "handle": handle,
            "master_sku": prod["master_sku"],
            "url": prod["url"],
            "color": enriched_copy["color"],
            "old_score": prod["score"],
            "old_broken_count": prod["broken_images_count"],
            "old_broken_urls": prod["broken_urls"],
            "old_body_html": old_body,
            "new_score": new_diag["score"],
            "new_images_count": len(selected_images),
            "new_body_html": new_html
        })

        print(f"[{idx:02d}/{len(target_prods):02d}] {title[:40]}... (SKU: {prod['master_sku']})")
        print(f"       Antes:  Score {prod['score']:02d} ({prod['broken_images_count']} fotos 404)")
        print(f"       Depois: Score {new_diag['score']:02d} ([OK] {len(selected_images)} fotos CDN)")

    # Exportações
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(output_dir, f"shopify_{store_key}_correcao_import_{timestamp}.csv")
    df = pd.DataFrame(csv_rows)
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")

    preview_file = os.path.join(output_dir, f"preview_{store_key}_comparativo_{timestamp}.html")
    artifact_preview = os.path.join(r"C:\Users\lucas\.gemini\antigravity\brain\6d694e19-7d4a-472b-b269-63d576efc810", f"preview_{store_key}_comparativo.html")

    # Gerar HTML comparativo
    generate_comparison_html(comparisons, preview_file, store_name)
    generate_comparison_html(comparisons, artifact_preview, store_name)

    print("\n" + "=" * 80)
    print(f"[OK] LOTE CORRIGIDO COM SUCESSO ({store_name})")
    print(f"Planilha CSV Oficial: {csv_file}")
    print(f"Visualizador Comparativo: {artifact_preview}")
    print("=" * 80)

def generate_comparison_html(comparisons: list, output_path: str, store_name: str):
    json_data = json.dumps(comparisons, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Preview Comparativo: {store_name} (Antes vs Depois)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }} .font-heading {{ font-family: 'Space Grotesk', sans-serif; }}</style>
</head>
<body class="bg-slate-100 text-slate-800 p-4 sm:p-8 antialiased">
  <div class="max-w-7xl mx-auto space-y-8">
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
      <div>
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-blue-100 text-blue-700">{store_name}</span>
        <h1 class="font-heading font-extrabold text-2xl text-slate-900 mt-1">Correção em Lote: Antes vs Depois</h1>
        <p class="text-xs text-slate-500">Produtos que estavam com fotos 404 corrigidos para 3 fotos oficiais CDN da Shopify.</p>
      </div>
      <div class="px-4 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold">
        {len(comparisons)} Produtos Regularizados
      </div>
    </div>
    <div class="space-y-8" id="list"></div>
  </div>
  <script>
    const ITEMS = {json_data};
    const list = document.getElementById("list");
    ITEMS.forEach((item, idx) => {{
      const card = document.createElement("div");
      card.className = "bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm";
      card.innerHTML = `
        <div class="p-5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div>
            <span class="text-xs font-mono font-bold text-slate-500">SKU: ${{item.master_sku}} • PRODUTO #${{idx+1}}</span>
            <h3 class="font-heading font-bold text-base text-slate-900 mt-0.5">${{item.title}}</h3>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs font-bold text-slate-500">Score: ${{item.old_score}} → <span class="text-emerald-600 font-extrabold">${{item.new_score}}</span></span>
            <a href="${{item.url}}" target="_blank" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-blue-600 text-white text-xs font-semibold">Ver no Site</a>
          </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-slate-200">
          <div class="p-5 bg-rose-50/20">
            <span class="text-xs font-bold text-rose-700 block mb-2">❌ ANTES (${{item.old_broken_count}} fotos 404 no S3)</span>
            <div class="prose max-w-none text-xs border border-rose-200 rounded-xl p-4 bg-white max-h-[500px] overflow-y-auto">
              ${{item.old_body_html || '<p class="italic text-slate-400">Sem descrição.</p>'}}
            </div>
          </div>
          <div class="p-5 bg-emerald-50/20">
            <span class="text-xs font-bold text-emerald-700 block mb-2">✅ DEPOIS (${{item.new_images_count}} fotos CDN Oficial)</span>
            <div class="border border-emerald-200 rounded-xl p-4 bg-white max-h-[500px] overflow-y-auto">
              ${{item.new_body_html}}
            </div>
          </div>
        </div>
      `;
      list.appendChild(card);
    }});
  </script>
</body>
</html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    site = sys.argv[1] if len(sys.argv) > 1 else "brk_motors"
    run_fixer(site, limit=20)
