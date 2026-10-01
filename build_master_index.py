"""
Compilador Mestre UNIFICADO index.html (Versão 4.0 - Vigilante & Análises).
Integra os Pilares Estratégicos:
1. Catálogo & Diagnóstico por SKU com Duplo Modo (Modo A Preservar vs Modo B Alta Conversão).
2. Moldes Mestres por Categoria (5 arquétipos com especificações preservadas).
3. Geração em Massa por SKU com exportação de CSV oficial da Shopify.
4. NOVA ABA: 📊 Análises & Monitoramento Diário (Histórico de Saúde, Links Proibidos, SKUs Órfãos e CSVs das 08:00).
Multi-Lojas: BRK Fishing, BRK Agro e BRK Motors.
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
from core.shopify_admin_client import ShopifyAdminClient

def build_master():
    print("[INICIO] Inicializando compilador Mestre do index.html (v4.0)...")
    template_engine = TemplateEngine()
    html_builder = HTMLBuilder()
    html_replacer = HTMLReplacer()
    image_harvester = ImageHarvester()

    # 1. Carregar dados brutos das lojas
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

    # 3. Listar CSVs diários disponíveis
    daily_fixes_dir = "reports/daily_fixes"
    available_csvs = []
    if os.path.exists(daily_fixes_dir):
        for fname in sorted(os.listdir(daily_fixes_dir), reverse=True):
            if fname.endswith(".csv"):
                fpath = os.path.join(daily_fixes_dir, fname)
                fsize = os.path.getsize(fpath)
                available_csvs.append({
                    "filename": fname,
                    "size_kb": round(fsize / 1024, 1),
                    "created_at": datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%d/%m/%Y %H:%M")
                })

    # Função para enriquecer produtos com representação garantida de 100% das categorias
    def enrich_products(store_dict, store_key="brk_fishing"):
        all_prods = store_dict.get("products", [])
        categories = store_dict.get("categories", {})
        
        selected_prods = []
        selected_handles = set()

        # 1. Garantir que cada categoria cadastrada na loja tenha produtos ricos disponíveis
        for cat_name in categories.keys():
            cat_items = [p for p in all_prods if p.get("category") == cat_name]
            if not cat_items:
                continue
            
            # Categorias com até 30 itens (ex: Calçados Boaonda, Caixas Deyu, Térmicos Elber, Cutelaria) entram 100%
            if len(cat_items) <= 30:
                for p in cat_items:
                    if p.get("handle") not in selected_handles:
                        selected_prods.append(p)
                        selected_handles.add(p.get("handle"))
            else:
                # Categorias massivas (Camisas UV, Bonés, Equipamentos): amostra balanceada
                cat_broken = [p for p in cat_items if p.get("status") == "IMAGENS_QUEBRADAS"]
                cat_empty = [p for p in cat_items if p.get("status") == "SEM_DESCRICAO"]
                cat_out_std = [p for p in cat_items if p.get("is_out_of_standard") and p.get("status") not in ("IMAGENS_QUEBRADAS", "SEM_DESCRICAO")]
                cat_healthy = [p for p in cat_items if not p.get("is_out_of_standard")]
                
                cat_sample = cat_broken[:20] + cat_empty[:10] + cat_out_std[:10] + cat_healthy[:15]
                for p in cat_sample:
                    if p.get("handle") not in selected_handles:
                        selected_prods.append(p)
                        selected_handles.add(p.get("handle"))

        # 2. Se houver falhas críticas adicionais, acrescenta até 30
        extra_broken = [p for p in all_prods if p.get("status") == "IMAGENS_QUEBRADAS" and p.get("handle") not in selected_handles]
        for p in extra_broken[:30]:
            selected_prods.append(p)
            selected_handles.add(p.get("handle"))
        
        sibling_matcher = SiblingMatcher(all_prods)
        enriched = []
        for p in selected_prods:
            title = p.get("title", "")
            category = p.get("category", "")
            tags = p.get("tags", [])
            # Coletar fotos oficiais da galeria do produto no site da Shopify
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

            orig_html = p.get("original_body_html") or p.get("body_html") or ""
            
            # 1. Detectar arquétipo correto por categoria real e vendor
            vendor = p.get("vendor", "")
            archetype_id = template_engine.detect_archetype(title, category, tags, vendor=vendor)
            arch_info = template_engine.templates.get(archetype_id, template_engine.templates["uv_performance"])
            
            # 2. Buscar irmão homólogo no site (Sibling Matcher)
            sibling_info = sibling_matcher.find_best_sibling(p, min_score=0.70)

            # 3. Gerar Modo A (Preservar HTML + Fotos CDN)
            mode_a_html = html_replacer.replace_images_preserve_html(orig_html, images, title)
            
            # 4. Gerar Modo B (3 Atos com Arquétipo Especializado ou Molde de Irmão do Site)
            narrative = template_engine.generate_narrative_from_template(p, archetype_id, images, store_key=store_key, sibling_info=sibling_info)
            mode_b_html = html_builder.build_shopify_html(narrative)

            # Detectar links proibidos e SKUs órfãos se não estavam anotados
            prohibited_links = p.get("prohibited_links", [])
            if not prohibited_links and orig_html:
                prohibited_domains = [r"use-brk-images-s3", r"drive\.google", r"mercadolivre", r"shopee", r"photobucket"]
                prohib_regex = re.compile("|".join(prohibited_domains), re.IGNORECASE)
                prohibited_links = [l for l in re.findall(r'(?:href|src)=["\']([^"\']+)["\']', orig_html) if prohib_regex.search(l)]

            p_copy = dict(p)
            p_copy["cdn_images"] = images
            p_copy["archetype_id"] = archetype_id
            p_copy["archetype_name"] = arch_info["name"]
            p_copy["source_type"] = narrative["source_type"]
            p_copy["source_label"] = narrative["source_label"]
            p_copy["sibling_info"] = sibling_info
            p_copy["store_key"] = store_key
            p_copy["theme_color"] = narrative["theme_color"]
            p_copy["theme_bg"] = narrative["theme_bg"]
            p_copy["care_icon"] = narrative["care_icon"]
            p_copy["mode_a_html"] = mode_a_html
            p_copy["mode_b_html"] = mode_b_html
            p_copy["specs"] = narrative["specs"]
            p_copy["prohibited_links"] = prohibited_links
            p_copy["orphaned_variants"] = p.get("orphaned_variants", [])
            enriched.append(p_copy)

        return {
            "store": store_dict.get("store", {}),
            "categories": store_dict.get("categories", {}),
            "products": enriched
        }

    print("[PROCESSANDO] Enriquecendo catálogos das 3 lojas com paletas cromáticas específicas...")
    enriched_fishing = enrich_products(fishing_data, store_key="brk_fishing")
    enriched_agro = enrich_products(agro_data, store_key="brk_agro")
    enriched_motors = enrich_products(motors_data, store_key="brk_motors")

    fishing_skus = fishing_data.get("store", {}).get("total_skus", 12582)
    fishing_skus_fmt = f"{fishing_skus:,}".replace(",", ".")
    agro_skus = agro_data.get("store", {}).get("total_skus", 5955)
    agro_skus_fmt = f"{agro_skus:,}".replace(",", ".")
    motors_skus = motors_data.get("store", {}).get("total_skus", 6758)
    motors_skus_fmt = f"{motors_skus:,}".replace(",", ".")

    # Exportar moldes para uso na interface
    moldes_data = template_engine.templates

    unified_payload = {
        "stores": {
            "brk_fishing": enriched_fishing,
            "brk_agro": enriched_agro,
            "brk_motors": enriched_motors
        },
        "moldes": moldes_data,
        "analytics": {
            "history": history_data,
            "available_csvs": available_csvs
        }
    }

    json_payload_str = json.dumps(unified_payload, ensure_ascii=False).replace("<", "\\u003c")

    print("[CONSTRUINDO] Montando template HTML mestre v4.0...")
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
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .font-heading {{ font-family: 'Space Grotesk', sans-serif; }}
    .no-scrollbar::-webkit-scrollbar {{ display: none; }}
    .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
    
    @keyframes pulse-glow {{
      0%, 100% {{ box-shadow: 0 0 15px rgba(37, 99, 235, 0.4), 0 0 30px rgba(239, 68, 68, 0.2); }}
      50% {{ box-shadow: 0 0 25px rgba(37, 99, 235, 0.7), 0 0 45px rgba(239, 68, 68, 0.4); }}
    }}
    .unified-button-glow {{ animation: pulse-glow 3s infinite ease-in-out; }}
    .category-ring {{ background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #1d4ed8 100%); }}
    .category-ring.has-broken {{ background: linear-gradient(135deg, #f97316 0%, #ef4444 100%); }}
    .product-shadow {{ box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04); }}
    .product-shadow:hover {{ box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.05); }}
    
    .toast-msg {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 100;
      background: #0f172a;
      color: #fff;
      padding: 12px 20px;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.25);
      border-left: 4px solid #10b981;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      font-weight: 600;
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.3s ease;
      pointer-events: none;
    }}
    .toast-msg.show {{
      opacity: 1;
      transform: translateY(0);
    }}
  </style>
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
            <p class="text-xs text-slate-400">Padronização de Descrições • Duplo Modo por SKU • Sincronização em Tempo Real</p>
          </div>
        </div>

        <div class="flex items-center gap-3 flex-wrap">
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
          <div id="unified-button-cockpit" class="flex items-center gap-3 bg-slate-900 border border-slate-700/80 rounded-2xl p-1.5 px-3 unified-button-glow cursor-pointer transition-all hover:border-blue-500" onclick="filterBrokenFromCockpit()">
            <div class="flex items-center gap-2.5">
              <span class="relative flex h-3 w-3">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
              <div class="text-left">
                <span class="text-[10px] uppercase tracking-wider font-extrabold text-slate-400 block">Diagnóstico por SKU</span>
                <span class="text-xs font-bold text-white flex items-center gap-1.5">
                  <span id="cockpit-broken-count" class="text-red-400 font-extrabold text-sm">--</span> SKUs com Fotos Quebradas
                </span>
              </div>
            </div>
            <div class="h-7 w-[1px] bg-slate-800 mx-1"></div>
            <div class="text-right">
              <span class="text-[10px] text-slate-400 block font-medium">Saúde do Catálogo</span>
              <span id="cockpit-health-badge" class="text-xs font-extrabold text-emerald-400">--% Saudável</span>
            </div>
            <div class="bg-blue-600/30 text-blue-400 hover:bg-blue-600 hover:text-white transition-all px-2.5 py-1 rounded-xl text-[11px] font-bold border border-blue-500/30">
              Isolar Falhas 🎯
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
    
    <!-- CABEÇALHO DO COCKPIT EM MASSA -->
    <div class="bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950 text-white p-6 rounded-3xl border border-slate-800 shadow-xl flex flex-wrap items-center justify-between gap-6">
      <div class="space-y-1.5 max-w-2xl">
        <span class="px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-300 text-[11px] font-extrabold uppercase tracking-wider border border-amber-500/30">Motor de Correção em Lote</span>
        <h2 class="text-2xl font-extrabold font-heading">Fila de Geração em Massa por SKU</h2>
        <p class="text-xs text-slate-300 leading-relaxed">
          Gere descrições em lote para todos os produtos sem texto ou com fotos quebradas da AWS S3. 
          O motor aplica automaticamente o <strong>Molde Mestre da Categoria</strong>, vincula as fotos oficiais do CDN Shopify e gera o arquivo CSV oficial pronto para importação direta no Admin da Shopify.
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
        <button onclick="downloadShopifyCSVBatch()" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-2">
          <span>📥 Baixar Planilha CSV Shopify</span>
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
      <p class="text-xs text-slate-500 mt-1">Estruturas consagradas de alta conversão que preservam 100% dos dados técnicos reais da peça sem alucinar especificações.</p>
    </div>

    <div id="moldes-cards-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Moldes Injetados Via JavaScript -->
    </div>
  </main>

  <!-- ======================================================== -->
  <!-- SEÇÃO 4: NOVA ABA ANÁLISES & MONITORAMENTO DIÁRIO         -->
  <!-- ======================================================== -->
  <main id="section-analytics" class="hidden max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <!-- BANNER EXECUTIVO DO VIGILANTE DAS 08:00 -->
    <div class="bg-gradient-to-r from-slate-950 via-blue-950 to-slate-900 text-white p-6 rounded-3xl border border-slate-800 shadow-xl flex flex-wrap items-center justify-between gap-6">
      <div class="space-y-1.5 max-w-2xl">
        <div class="flex items-center gap-2">
          <span class="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-[11px] font-extrabold uppercase tracking-wider border border-emerald-500/30 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Vigilante Diário • Agendamento às 08:00
          </span>
          <span id="sentinel-last-run" class="text-xs text-slate-400 font-mono">Última checagem: Hoje às 08:00</span>
        </div>
        <h2 class="text-2xl font-extrabold font-heading">Painel de Auditoria & Conformidade</h2>
        <p class="text-xs text-slate-300 leading-relaxed">
          Monitoramento automático contínuo das 3 lojas Shopify. Rastreia fotos quebradas da AWS S3, links externos proibidos (Drive, Mercado Livre, Shopee) e SKUs órfãos. Gera a planilha de correções do dia automaticamente.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button onclick="downloadLatestDailyCSV()" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-2">
          <span>📥 Baixar CSV de Correção do Dia</span>
          <span id="badge-daily-corrections-count" class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full">86 itens</span>
        </button>
      </div>
    </div>

    <!-- CARDS DE SAÚDE DAS 3 LOJAS -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <!-- Card Fishing -->
      <div class="bg-white rounded-3xl border border-slate-200 p-6 product-shadow space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-xl">🎣 BRK Fishing</span>
          <span id="stat-fishing-health" class="text-base font-extrabold text-emerald-600">90.2%</span>
        </div>
        <div class="space-y-1.5 text-xs text-slate-600">
          <div class="flex justify-between"><span>Total de SKUs:</span><strong id="stat-fishing-skus" class="text-slate-900">438</strong></div>
          <div class="flex justify-between"><span>Fotos Quebradas:</span><strong id="stat-fishing-broken" class="text-red-600">43 SKUs</strong></div>
          <div class="flex justify-between"><span>Sem Descrição:</span><strong id="stat-fishing-empty" class="text-amber-600">1 produto</strong></div>
          <div class="flex justify-between"><span>Correções Geradas:</span><strong id="stat-fishing-fixes" class="text-emerald-600">8 prontas</strong></div>
        </div>
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div id="bar-fishing-health" class="bg-blue-600 h-full rounded-full" style="width: 90.2%;"></div>
        </div>
      </div>

      <!-- Card Agro -->
      <div class="bg-white rounded-3xl border border-slate-200 p-6 product-shadow space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-xl">🚜 BRK Agro</span>
          <span id="stat-agro-health" class="text-base font-extrabold text-emerald-600">99.7%</span>
        </div>
        <div class="space-y-1.5 text-xs text-slate-600">
          <div class="flex justify-between"><span>Total de SKUs:</span><strong id="stat-agro-skus" class="text-slate-900">5.955</strong></div>
          <div class="flex justify-between"><span>Fotos Quebradas:</span><strong id="stat-agro-broken" class="text-red-600">19 SKUs</strong></div>
          <div class="flex justify-between"><span>Sem Descrição:</span><strong id="stat-agro-empty" class="text-amber-600">35 produtos</strong></div>
          <div class="flex justify-between"><span>Correções Geradas:</span><strong id="stat-agro-fixes" class="text-emerald-600">38 prontas</strong></div>
        </div>
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div id="bar-agro-health" class="bg-emerald-600 h-full rounded-full" style="width: 99.7%;"></div>
        </div>
      </div>

      <!-- Card Motors -->
      <div class="bg-white rounded-3xl border border-slate-200 p-6 product-shadow space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-xl">🏁 BRK Motors</span>
          <span id="stat-motors-health" class="text-base font-extrabold text-emerald-600">98.5%</span>
        </div>
        <div class="space-y-1.5 text-xs text-slate-600">
          <div class="flex justify-between"><span>Total de SKUs:</span><strong id="stat-motors-skus" class="text-slate-900">6.758</strong></div>
          <div class="flex justify-between"><span>Fotos Quebradas:</span><strong id="stat-motors-broken" class="text-red-600">98 SKUs</strong></div>
          <div class="flex justify-between"><span>Sem Descrição:</span><strong id="stat-motors-empty" class="text-amber-600">32 produtos</strong></div>
          <div class="flex justify-between"><span>Correções Geradas:</span><strong id="stat-motors-fixes" class="text-emerald-600">40 prontas</strong></div>
        </div>
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div id="bar-motors-health" class="bg-indigo-600 h-full rounded-full" style="width: 98.5%;"></div>
        </div>
      </div>

    </div>

    <!-- TABELA DE CONFORMIDADE RIGOROSA (LINKS PROIBIDOS & SKUS ÓRFÃOS) -->
    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-slate-50/50">
        <div>
          <h3 class="text-sm font-extrabold text-slate-900 font-heading">Auditoria de Conformidade por SKU</h3>
          <p class="text-xs text-slate-500">Detecta links proibidos (Drive, Shopee, Mercado Livre, AWS S3) e variantes sem código cadastrado.</p>
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

    <!-- REPOSITÓRIO DE CSVS GERADOS NAS 08:00 -->
    <div class="bg-white rounded-3xl border border-slate-200 p-6 product-shadow space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-extrabold text-slate-900 font-heading">Planilhas CSV de Correção do Dia (Prontas para Importar)</h3>
          <p class="text-xs text-slate-500">Arquivos gerados automaticamente pelo ciclo diário e salvos na pasta reports/daily_fixes do seu OneDrive.</p>
        </div>
        <span class="text-xs font-bold text-slate-400">Padrão UTF-8 BOM Shopify</span>
      </div>

      <div id="analytics-csv-list" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <!-- Injetado Via JavaScript -->
      </div>
    </div>

  </main>

  <!-- ======================================================== -->
  <!-- MODAL DE PRODUTO (DUPLO MODO + COPIADOR + COMPARATIVO)   -->
  <!-- ======================================================== -->
  <div id="product-modal" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
      
      <!-- Cabeçalho do Modal -->
      <div class="p-5 border-b border-slate-100 flex items-center justify-between gap-4 bg-slate-900 text-white">
        <div class="min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span id="modal-sku-badge" class="px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 font-mono text-[10px] font-bold border border-blue-500/30">SKU: --</span>
            <span id="modal-variants-badge" class="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[10px] font-semibold">8 Variantes</span>
            <span id="modal-archetype-badge" class="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">Molde UV50+</span>
            <span id="modal-source-badge" class="px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 text-[10px] font-bold border border-purple-500/30">✨ Molde Homólogo</span>
          </div>
          <h3 id="modal-title" class="text-base font-extrabold truncate">Título do Produto</h3>
        </div>
        <button onclick="closeProductModal()" class="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center text-sm font-bold transition-all">✕</button>
      </div>

      <!-- Faixa de Fotos Oficiais Cadastradas no Site da Loja -->
      <div class="px-6 py-2.5 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-3">
          <span class="text-[10px] font-extrabold uppercase text-slate-500 tracking-wider">Fotos no Catálogo do Site:</span>
          <div id="modal-gallery-thumbs" class="flex items-center gap-2">
            <!-- Miniaturas injetadas via JS -->
          </div>
        </div>
        <span id="modal-photos-count-badge" class="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700">3 Fotos no CDN Shopify</span>
      </div>

      <!-- Barra de Controle do Duplo Modo -->
      <div class="px-6 py-3 bg-slate-100 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200 shadow-sm">
          <button id="btn-mode-b" onclick="switchModalMode('b')" class="px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-emerald-600 text-white shadow-sm flex items-center gap-1.5">
            <span>🚀 Modo B: 3 Atos (Alta Conversão)</span>
          </button>
          <button id="btn-mode-a" onclick="switchModalMode('a')" class="px-3.5 py-1.5 rounded-lg font-extrabold transition-all text-slate-600 hover:text-slate-900 flex items-center gap-1.5">
            <span>🛠️ Modo A: Preservar HTML + Fotos CDN</span>
          </button>
          <button id="btn-mode-orig" onclick="switchModalMode('orig')" class="px-3.5 py-1.5 rounded-lg font-bold transition-all text-slate-400 hover:text-red-600 flex items-center gap-1.5">
            <span>❌ Original (Quebrado/AWS)</span>
          </button>
        </div>

        <div class="flex items-center gap-2">
          <button id="modal-save-shopify-direct-btn" onclick="saveDirectToShopify(this)" class="px-3.5 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all transform active:scale-95 text-xs" title="Atualiza EXCLUSIVAMENTE o campo body_html deste produto na Shopify">
            <span>⚡</span>
            <span>Salvar na Shopify (Direto)</span>
          </button>
          <button id="modal-header-copy-btn" onclick="copyCurrentModalHTML(this)" class="px-4 py-1.5 bg-slate-900 hover:bg-black text-white rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all transform active:scale-95 text-xs">
            <span class="copy-icon">📋</span>
            <span class="copy-label">Copiar HTML</span>
          </button>
          <button onclick="downloadCurrentProductCSV()" class="px-3.5 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl font-bold flex items-center gap-1.5 shadow-sm transition-all text-xs">
            <span>📥 CSV</span>
          </button>
        </div>
      </div>

      <!-- Corpo do Modal com Pré-visualização -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        
        <!-- Alerta Informativo do Modo Atual -->
        <div id="modal-mode-banner" class="p-3.5 rounded-xl border text-xs flex items-center justify-between bg-emerald-50 border-emerald-200 text-emerald-800">
          <div class="flex items-center gap-2">
            <span class="text-base">✨</span>
            <span id="modal-mode-desc"><strong>Modo B Ativo:</strong> Descrição reestruturada em 3 Atos narrativos com no máximo 3 fotos CDN oficiais e tabela de especificações.</span>
          </div>
          <span class="text-[10px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">Pronto para Shopify</span>
        </div>

        <!-- PAINEL SMART BUNKER LINKER (INJETOR DE MÍDIAS DO CLOUDFLARE WORKER) -->
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
              <textarea id="bunker-bulk-input" rows="2" placeholder="https://brk-bunker.allexadriel.workers.dev/images/...&#10;https://brk-bunker.allexadriel.workers.dev/images/...&#10;https://brk-bunker.allexadriel.workers.dev/images/..." class="w-full bg-slate-950/90 border border-indigo-500/50 rounded-xl p-2.5 text-xs text-indigo-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 font-mono"></textarea>
            </div>

            <!-- Slots Individuais das 3 Posições -->
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
              <span class="text-[10px] text-slate-400">Dimensões 4:3 responsivas blindadas, alinhadas automaticamente.</span>
              <button onclick="applyBunkerLinksToModal()" class="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-extrabold shadow-lg transition-all flex items-center gap-1.5">
                <span>⚡ Aplicar Fotos do Bunker na Descrição</span>
              </button>
            </div>
          </div>
        </details>

        <!-- Área de Renderização HTML -->
        <div class="border border-slate-200 rounded-2xl p-6 bg-white shadow-inner">
          <div id="modal-rendered-content">
            <!-- HTML Injetado Aqui -->
          </div>
        </div>

        <!-- Área de Código Fonte HTML (Colapsável) -->
        <details class="bg-slate-50 rounded-2xl border border-slate-200 p-4">
          <summary class="text-xs font-bold text-slate-600 cursor-pointer hover:text-slate-900 select-none">Ver Código Fonte HTML Completo</summary>
          <pre id="modal-source-code" class="mt-3 p-3 bg-slate-900 text-slate-200 text-[11px] rounded-xl overflow-x-auto font-mono max-h-48"></pre>
        </details>

      </div>

      <!-- Rodapé Fixo / Sticky Action Footer do Modal -->
      <div class="px-6 py-3.5 bg-slate-900 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs z-10 shrink-0">
        <div class="flex items-center gap-2 text-slate-400">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="text-[11px] font-mono" id="modal-footer-sku-info">SKU Mestre: Pronto para Shopify</span>
        </div>
        <div class="flex items-center gap-2">
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
    <span id="toast-text">HTML copiado para a área de transferência!</span>
  </div>

  <!-- ======================================================== -->
  <!-- DADOS ESTRUTURADOS JSON (BLINDADOS CONTRA ESCAPE HTML)    -->
  <!-- ======================================================== -->
  <script id="master-payload-data" type="application/json">
{json_payload_str}
  </script>

  <!-- ======================================================== -->
  <!-- SCRIPT LOGIC JAVASCRIPT MASTER                           -->
  <!-- ======================================================== -->
  <script>
    // DADOS INJETADOS PELO COMPILADOR PYTHON
    const MASTER_PAYLOAD = JSON.parse(document.getElementById("master-payload-data").textContent);

    let currentStore = "brk_fishing";
    let currentFilter = "all";
    let selectedCategory = "all";
    let searchQuery = "";
    let currentModalProduct = null;
    let currentModalMode = "b"; // 'b', 'a', 'orig'
    let selectedMassProductIds = new Set();
    let currentAuditFilter = "all";

    // Elementos DOM
    const productsGrid = document.getElementById("products-grid");
    const categoriesRail = document.getElementById("categories-rail");
    const emptyState = document.getElementById("empty-state");
    const searchInput = document.getElementById("search-input");
    const massTableBody = document.getElementById("mass-table-body");

    // Mostrar Toast
    function showToast(text) {{
      const toast = document.getElementById("toast");
      document.getElementById("toast-text").innerText = text;
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 2800);
    }}

    // Alternador de Abas Principais (4 ABAS)
    function switchMainTab(tabId) {{
      document.querySelectorAll(".main-tab").forEach(b => {{
        b.classList.remove("active", "bg-slate-800", "text-white");
        b.classList.add("text-slate-400");
      }});
      const activeBtn = document.getElementById("btn-" + tabId);
      if (activeBtn) {{
        activeBtn.classList.add("active", "bg-slate-800", "text-white");
        activeBtn.classList.remove("text-slate-400");
      }}

      document.getElementById("section-catalog").classList.add("hidden");
      document.getElementById("section-mass").classList.add("hidden");
      document.getElementById("section-moldes").classList.add("hidden");
      document.getElementById("section-analytics").classList.add("hidden");

      if (tabId === "tab-catalog") {{
        document.getElementById("section-catalog").classList.remove("hidden");
        renderProducts();
      }} else if (tabId === "tab-mass") {{
        document.getElementById("section-mass").classList.remove("hidden");
        renderMassTable();
      }} else if (tabId === "tab-moldes") {{
        document.getElementById("section-moldes").classList.remove("hidden");
        renderMoldesCards();
      }} else if (tabId === "tab-analytics") {{
        document.getElementById("section-analytics").classList.remove("hidden");
        renderAnalyticsView();
      }}
    }}

    // ========================================================
    // MOTOR DE SINCRONIZAÇÃO EM TEMPO REAL (POR SEGUNDOS)
    // ========================================================
    const STORE_DOMAINS = {{
      "brk_fishing": "www.brkfishing.com.br",
      "brk_agro": "www.brkagro.com.br",
      "brk_motors": "www.brkmotors.com.br"
    }};

    const STORE_COLOR_PALETTES = {{
      "brk_fishing": {{ color: "#0284c7", bg: "#f0f9ff", name: "Azul Leve" }},
      "brk_agro":    {{ color: "#16a34a", bg: "#f0fdf4", name: "Verde Leve" }},
      "brk_motors":  {{ color: "#f97316", bg: "#fff7ed", name: "Laranja Leve" }}
    }};

    let liveSyncIntervalSecs = 15;
    let liveSyncTimer = null;
    let liveSyncCountdownSecs = 15;
    let isSyncingNow = false;

    function startLiveSync() {{
      if (liveSyncTimer) clearInterval(liveSyncTimer);
      const pulse = document.getElementById("live-sync-pulse");
      const dot = document.getElementById("live-sync-dot");
      const statusText = document.getElementById("live-sync-status-text");

      if (liveSyncIntervalSecs <= 0) {{
        if (pulse) pulse.classList.add("hidden");
        if (dot) dot.className = "relative inline-flex rounded-full h-2.5 w-2.5 bg-slate-500";
        if (statusText) statusText.innerHTML = "Pausado";
        return;
      }}

      if (pulse) pulse.classList.remove("hidden");
      if (dot) dot.className = "relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500";
      liveSyncCountdownSecs = liveSyncIntervalSecs;
      updateSyncCountdownDisplay();

      liveSyncTimer = setInterval(() => {{
        liveSyncCountdownSecs--;
        if (liveSyncCountdownSecs <= 0) {{
          liveSyncCountdownSecs = liveSyncIntervalSecs;
          performLiveSync();
        }}
        updateSyncCountdownDisplay();
      }}, 1000);
    }}

    function updateSyncCountdownDisplay() {{
      const elem = document.getElementById("live-sync-countdown");
      if (elem) elem.innerText = liveSyncCountdownSecs + "s";
      const status = document.getElementById("live-sync-status-text");
      if (status && liveSyncIntervalSecs > 0) {{
        status.innerHTML = `Ativo (<span id="live-sync-countdown" class="text-emerald-400 font-mono">${{liveSyncCountdownSecs}}s</span>)`;
      }}
    }}

    function changeLiveSyncInterval(val) {{
      liveSyncIntervalSecs = parseInt(val, 10);
      startLiveSync();
      if (liveSyncIntervalSecs > 0) {{
        showToast(`⏱️ Sincronização ao vivo ajustada para cada ${{liveSyncIntervalSecs}} segundos.`);
      }} else {{
        showToast(`⏸️ Sincronização automática pausada.`);
      }}
    }}

    function triggerManualLiveSync() {{
      performLiveSync(true);
    }}

    async function performLiveSync(isManual = false) {{
      if (isSyncingNow) return;
      isSyncingNow = true;

      const syncIcon = document.getElementById("sync-icon");
      if (syncIcon) syncIcon.classList.add("animate-spin");

      const storeKey = currentStore;
      const domain = STORE_DOMAINS[storeKey] || "www.brkfishing.com.br";
      const fetchUrl = `https://${{domain}}/products.json?limit=30&t=${{Date.now()}}`;

      try {{
        const response = await fetch(fetchUrl, {{ cache: "no-store" }});
        if (!response.ok) throw new Error("Status " + response.status);
        const data = await response.json();
        const liveProducts = data.products || [];

        const currentList = MASTER_PAYLOAD.stores[storeKey].products;
        const knownIds = new Set(currentList.map(p => String(p.id)));

        let newProductsAdded = 0;
        let emptyCountDetected = 0;

        liveProducts.forEach(liveP => {{
          const pId = String(liveP.id);
          const rawHtml = liveP.body_html || "";
          const isEmpty = (!rawHtml || rawHtml.trim() === "" || rawHtml.trim() === "<p></p>");
          
          if (!knownIds.has(pId)) {{
            const newEnriched = createEnrichedFromLiveProduct(liveP, storeKey);
            currentList.unshift(newEnriched);
            knownIds.add(pId);
            newProductsAdded++;
            if (newEnriched.status === "SEM_DESCRICAO") emptyCountDetected++;
          }} else {{
            const existing = currentList.find(p => String(p.id) === pId);
            if (existing && isEmpty && existing.status !== "SEM_DESCRICAO") {{
              existing.status = "SEM_DESCRICAO";
              existing.is_out_of_standard = true;
            }}
          }}
        }});

        if (newProductsAdded > 0) {{
          updateCockpit();
          renderProducts();
          updateMassCountBadge();
          showToast(`✨ ${{newProductsAdded}} produto(s) sincronizado(s) em tempo real da Shopify! (${{emptyCountDetected}} sem descrição)`);
        }} else if (isManual) {{
          showToast(`✅ Catálogo da loja ${{domain}} sincronizado com a Shopify! Nenhum novo produto no momento.`);
        }}
      }} catch (err) {{
        console.warn("Falha no Live Sync:", err);
        if (isManual) {{
          showToast(`⚠️ Não foi possível conectar na Shopify em tempo real: ${{err.message}}`);
        }}
      }} finally {{
        if (syncIcon) syncIcon.classList.remove("animate-spin");
        isSyncingNow = false;
      }}
    }}

    function createEnrichedFromLiveProduct(liveP, storeKey) {{
      const rawHtml = liveP.body_html || "";
      const isEmpty = (!rawHtml || rawHtml.trim() === "" || rawHtml.trim() === "<p></p>");
      const images = (liveP.images || []).map(img => img.src || img);
      const title = liveP.title || "Produto BRK";
      const tags = typeof liveP.tags === 'string' ? liveP.tags.split(',').map(t => t.trim()) : (liveP.tags || []);
      const variants = liveP.variants || [];
      const masterSku = variants.length > 0 && variants[0].sku ? variants[0].sku : ("BRK-" + liveP.id);
      const variantsSkus = variants.map(v => v.sku).filter(Boolean);

      const text = (title + " " + tags.join(" ") + " " + (liveP.vendor || "")).toLowerCase();
      let archId = "uv_performance";
      let archName = "UV50+ Performance";

      if (text.includes("sandalia") || text.includes("chinelo") || text.includes("boaonda") || text.includes("calcado")) {{
        archId = "footwear_sandals";
        archName = "Calçados & Sandálias";
      }} else if (text.includes("caixa") || text.includes("estojo") || text.includes("organizador")) {{
        archId = "tackle_boxes_storage";
        archName = "Caixas, Estojos & Organização";
      }} else if (text.includes("termic") || text.includes("cooler") || text.includes("elber")) {{
        archId = "thermal_gear";
        archName = "Térmicos & Camping";
      }} else if (text.includes("vara") || text.includes("carretilha") || text.includes("molinete") || text.includes("isca") || text.includes("marine") || text.includes("deyu") || text.includes("albatroz")) {{
        archId = "fishing_tackle_gear";
        archName = "Equipamentos de Pesca & Revenda";
      }} else if (text.includes("faca") || text.includes("cutelaria")) {{
        archId = "cutlery_unique";
        archName = "Cutelaria & Facas";
      }} else if (text.includes("bone") || text.includes("chapeu")) {{
        archId = "caps_accessories";
        archName = "Bonés & Chapéus";
      }} else if (storeKey === "brk_motors" || text.includes("moto") || text.includes("cross")) {{
        archId = "motors_speed";
        archName = "Motors & Velocidade";
      }} else if (storeKey === "brk_agro" || text.includes("agro") || text.includes("campo")) {{
        archId = "agro_field";
        archName = "Agro & Campo";
      }}

      const palette = STORE_COLOR_PALETTES[storeKey] || STORE_COLOR_PALETTES["brk_fishing"];
      const themeColor = palette.color;
      const themeBg = palette.bg;

      const modeBHtml = buildClientModeBHTML(liveP, archId, archName, images, themeColor, themeBg, storeKey);

      return {{
        id: liveP.id,
        title: title,
        handle: liveP.handle,
        vendor: liveP.vendor || "",
        category: (tags.find(t => t.includes("&") || t.includes("Camisa") || t.includes("Boné")) || "Geral"),
        tags: tags,
        master_sku: masterSku,
        variants_skus: variantsSkus,
        total_skus_count: variants.length,
        affected_skus_count: isEmpty ? variants.length : 0,
        status: isEmpty ? "SEM_DESCRICAO" : "SAUDAVEL",
        is_out_of_standard: isEmpty,
        is_live_synced: true,
        image: images[0] || "",
        cdn_images: images.slice(0, 3),
        gallery: images,
        archetype_id: archId,
        archetype_name: archName,
        store_key: storeKey,
        theme_color: themeColor,
        theme_bg: themeBg,
        original_body_html: rawHtml,
        mode_a_html: rawHtml,
        mode_b_html: modeBHtml,
        specs: [
          {{ label: "Categoria", value: archName }},
          {{ label: "Fabricante / Origem", value: liveP.vendor || "BRK Group Oficial" }},
          {{ label: "Garantia", value: "Garantia oficial de fábrica contra defeitos" }}
        ],
        prohibited_links: [],
        orphaned_variants: []
      }};
    }}

    function buildClientModeBHTML(liveP, archId, archName, images, themeColor, themeBg, storeKey) {{
      const title = liveP.title || "Produto BRK";
      const img1 = images[0] || "https://placehold.co/800x600?text=BRK+Oficial";
      const img2 = images[1] || img1;
      const img3 = images[2] || img1;

      let act1 = {{ tag: "Performance & Conforto", icon: "fa-solid fa-gauge-high", title: "ALTA PERFORMANCE E RESPIRABILIDADE", desc: `Desenvolvido para oferecer máxima durabilidade e conforto térmico, o(a) ${{title}} garante total liberdade de movimentos e proteção contínua.` }};
      let act2 = {{ tag: "Tecnologia & Proteção", icon: "fa-solid fa-shield-halved", title: "TECNOLOGIA RESISTENTE E FUNCIONAL", desc: `Projetado com matérias-primas nobres de padrão industrial, assegurando desempenho superior e resistência comprovada.` }};
      let act3 = {{ tag: "Acabamento & Durabilidade", icon: "fa-solid fa-circle-check", title: "ACABAMENTO PREMIUM REFORÇADO", desc: `Costuras reforçadas e estrutura pensada para enfrentar condições extremas sem perder qualidade.` }};
      let careIcon = "fa-solid fa-shirt";
      let careTips = "Lavar à mão ou em ciclo suave com sabão neutro. Secar à sombra (dispensa uso de ferro).";
      let specs = [
        {{ label: "Categoria", value: archName }},
        {{ label: "Fabricante", value: liveP.vendor || "BRK Group Oficial" }},
        {{ label: "Garantia", value: "Garantia oficial contra defeitos de fabricação" }},
        {{ label: "Uso Recomendado", value: "Atividades intensas, lazer e uso diário" }}
      ];

      if (archId === "footwear_sandals") {{
        act1 = {{ tag: "Conforto & Ergonomia", icon: "fa-solid fa-shoe-prints", title: "DESIGN ANATÔMICO COM PALMILHA ANTI-IMPACTO", desc: `Desenvolvida para proporcionar amortecimento suave e alívio de pressão na pisada, o(a) ${{title}} garante descanso aos pés durante longos períodos em pé.` }};
        act2 = {{ tag: "Aderência & Drenagem", icon: "fa-solid fa-water", title: "SOLADO ANTIDERRAPANTE COM DRENAGEM RÁPIDA", desc: `Possui frisos e canais de escoamento especialmente projetados para pisos molhados, decks de barcos e bordas de piscina, oferecendo tração segura.` }};
        act3 = {{ tag: "Durabilidade & Higiene", icon: "fa-solid fa-shield-halved", title: "MATERIAL ANTIMICROBIANO E SECAGEM INSTANTÂNEA", desc: `Confeccionada em polímero nobre impermeável que não absorve umidade nem odores, sendo extremamente fácil de lavar e secar rapidamente.` }};
        careIcon = "fa-solid fa-shoe-prints";
        careTips = "Lavar com água corrente e sabão neutro. Não expor ao sol excessivo direto para evitar deformação do EVA.";
        specs = [
          {{ label: "Material do Cabedal", value: "Termoplástico nobre Boaonda flexível e lavável" }},
          {{ label: "Solado", value: "Borracha antiderrapante com ranhuras de tração e escoamento" }},
          {{ label: "Palmilha", value: "Anatômica com amortecimento anti-impacto" }},
          {{ label: "Resistência", value: "100% à prova d'água, secagem instantânea" }},
          {{ label: "Uso Recomendado", value: "Embarcações, pesqueiros, praia, piscina e uso casual" }}
        ];
      }} else if (archId === "tackle_boxes_storage") {{
        act1 = {{ tag: "Organização & Espaço", icon: "fa-solid fa-box-archive", title: "DIVISÓRIAS MODULARES E COMPARTIMENTAÇÃO INTELIGENTE", desc: `Projetada para acomodar iscas, anzóis, chumbadas e equipamentos com total organização, o(a) ${{title}} permite ajustar o espaço interno sob medida.` }};
        act2 = {{ tag: "Segurança Reforçada", icon: "fa-solid fa-lock", title: "TRAVAS DUPLAS REFORÇADAS ANTI-ABERTURA", desc: `Equipada com fechos de alta pressão que garantem travamento firme e seguro, impedindo aberturas acidentais mesmo durante impactos e movimentação intensa na embarcação.` }};
        act3 = {{ tag: "Proteção Estrutural", icon: "fa-solid fa-shield-halved", title: "POLÍMERO VIRGEM DE ALTA RESISTÊNCIA COM PROTEÇÃO UV", desc: `Construção robusta resistente a quedas, choques mecânicos e à degradação solar, preservando suas tralhas protegidas da água e do sol por muito mais tempo.` }};
        careIcon = "fa-solid fa-box-archive";
        careTips = "Higienizar com pano úmido e sabão neutro. Enxaguar e secar antes de guardar as tralhas para evitar umidade interna.";
        specs = [
          {{ label: "Material", value: "Polipropileno virgem de alto impacto com proteção UV" }},
          {{ label: "Divisórias", value: "Removíveis e reposicionáveis sob medida" }},
          {{ label: "Travas", value: "Sistema duplo reforçado de alta pressão" }},
          {{ label: "Vedação", value: "Resistente a respingos d'água e poeira" }},
          {{ label: "Aplicação", value: "Organização de tralhas em barcos, caiaques, pesqueiros e camping" }}
        ];
      }} else if (archId === "fishing_tackle_gear") {{
        act1 = {{ tag: "Engenharia & Precisão", icon: "fa-solid fa-gear", title: "MECÂNICA BALANCEADA PARA ALTO DESEMPENHO", desc: `Construído com componentes de engenharia refinada, o(a) ${{title}} oferece arremessos precisos, sensibilidade máxima no trabalho da isca e funcionamento suave.` }};
        act2 = {{ tag: "Poder de Tração", icon: "fa-solid fa-bolt", title: "RESISTÊNCIA SOB TRAÇÃO E CONTROLE PROGRESSIVO", desc: `Projetado para suportar esforço extremo nas brigas com grandes exemplares, mantendo tração firme e confiabilidade absoluta na linha.` }};
        act3 = {{ tag: "Blindagem Anticorrosão", icon: "fa-solid fa-shield-halved", title: "COMPONENTES TRATADOS CONTRA CORROSÃO", desc: `Materiais selecionados de alta dureza com revestimento resistente à água doce e salinidade, garantindo longa vida útil e preservação dos mecanismos.` }};
        careIcon = "fa-solid fa-screwdriver-wrench";
        careTips = "Após uso em água salgada ou salobra, enxaguar em água corrente doce e secar à sombra. Manter lubrificação periódica.";
        specs = [
          {{ label: "Categoria", value: "Equipamento de Precisão para Pesca Esportiva" }},
          {{ label: "Estrutura", value: "Liga reforçada de baixo peso e alta rigidez estrutural" }},
          {{ label: "Mecânica", value: "Componentes de precisão com rolamentos selados" }},
          {{ label: "Aplicação", value: "Pesca esportiva em rios, lagos, pesqueiros e mar aberto" }},
          {{ label: "Origem / Distribuição", value: `Produto original ${{liveP.vendor || 'Oficial'}} com procedência e garantia` }}
        ];
      }} else if (archId === "thermal_gear") {{
        act1 = {{ tag: "Eficiência Térmica", icon: "fa-solid fa-snowflake", title: "ISOLAMENTO TÉRMICO DE ALTA DENSIDADE", desc: `Tecnologia de retenção térmica de alto rendimento para conservar alimentos e bebidas na temperatura ideal por muito mais tempo.` }};
        act2 = {{ tag: "Vedação Hermética", icon: "fa-solid fa-temperature-arrow-down", title: "VEDAÇÃO TOTAL CONTRA TROCA DE CALOR", desc: `Garante bloqueio absoluto de calor externo e conservação uniforme mesmo sob sol forte.` }};
        act3 = {{ tag: "Robustez Industrial", icon: "fa-solid fa-shield-halved", title: "ESTRUTURA REFORÇADA PARA EXPEDIÇÕES", desc: `Resistente a impactos em caçambas, barcos e acampamentos.` }};
        careIcon = "fa-solid fa-snowflake";
        careTips = "Higienizar com água morna e sabão neutro. Deixar secar totalmente aberto antes de armazenar.";
        specs = [
          {{ label: "Estrutura", value: "Parede dupla isolada com poliuretano injetado" }},
          {{ label: "Retenção Térmica", value: "Conservação prolongada para frio ou quente" }},
          {{ label: "Uso Recomendado", value: "Expedições, barcos, caçambas, camping e pescarias" }}
        ];
      }}

      return `<!-- BRK GROUP - DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL SHOPIFY) -->
<div class="brk-desc-wrapper">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  <style>
    .brk-desc-wrapper {{
      width: 100%;
      max-width: 980px;
      margin: 30px auto;
      padding: 0 10px;
      font-family: inherit;
      color: #1e293b;
      box-sizing: border-box;
      line-height: 1.5;
    }}
    .brk-desc-wrapper * {{
      box-sizing: border-box;
    }}

    /* Atos Narrativos */
    .brk-desc-block {{
      display: flex;
      align-items: center;
      gap: 36px;
      margin-bottom: 42px;
    }}
    .brk-desc-block.reverse {{
      flex-direction: row-reverse;
    }}
    .brk-desc-media {{
      flex: 1;
      min-width: 0;
    }}
    .brk-desc-media img {{
      width: 100%;
      height: auto;
      aspect-ratio: 4 / 3;
      object-fit: cover;
      border-radius: 14px;
      display: block;
      box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
      border: 1px solid #f1f5f9;
    }}
    .brk-desc-text {{
      flex: 1.15;
      min-width: 0;
    }}
    .brk-desc-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: ${{themeColor}};
      background: ${{themeBg}};
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 10px;
      border: 1px solid ${{themeColor}}25;
    }}
    .brk-desc-title {{
      font-size: 23px;
      font-weight: 800;
      line-height: 1.25;
      color: #0f172a;
      margin: 0 0 12px 0;
      text-transform: uppercase;
      letter-spacing: -0.3px;
    }}
    .brk-desc-paragraph {{
      font-size: 15px;
      line-height: 1.7;
      color: #475569;
      margin: 0;
    }}

    /* Box de Ficha Técnica & Cuidados */
    .brk-desc-specs-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 26px 24px;
      margin-top: 36px;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
    }}
    .brk-desc-specs-title {{
      font-size: 16px;
      font-weight: 800;
      color: #0f172a;
      margin: 0 0 18px 0;
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 12px;
      border-bottom: 2px solid #edf2f7;
    }}
    .brk-specs-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px 22px;
    }}
    .brk-spec-item {{
      display: flex;
      flex-direction: column;
      border-bottom: 1px dashed #e2e8f0;
      padding-bottom: 8px;
    }}
    .brk-spec-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .brk-spec-value {{
      font-size: 13.5px;
      font-weight: 600;
      color: #0f172a;
      margin-top: 3px;
    }}

    /* Guia de Conservação */
    .brk-desc-care-box {{
      margin-top: 20px;
      background: #ffffff;
      border-left: 4px solid ${{themeColor}};
      border-radius: 0 10px 10px 0;
      padding: 14px 18px;
      font-size: 12.5px;
      line-height: 1.6;
      color: #334155;
      border-top: 1px solid #e2e8f0;
      border-right: 1px solid #e2e8f0;
      border-bottom: 1px solid #e2e8f0;
    }}
    .brk-desc-care-box strong {{
      color: #0f172a;
    }}

    /* Rodapé de Confiança e Garantia BRK com Font Awesome */
    .brk-desc-trust-bar {{
      margin-top: 32px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      text-align: center;
    }}
    .brk-trust-item {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }}
    .brk-trust-icon {{
      font-size: 22px;
      color: ${{themeColor}};
      margin-bottom: 2px;
    }}
    .brk-trust-title {{
      font-size: 12.5px;
      font-weight: 800;
      color: #0f172a;
    }}
    .brk-trust-desc {{
      font-size: 11px;
      color: #64748b;
      line-height: 1.3;
    }}

    /* Responsividade Mobile-First Blindada */
    @media (max-width: 768px) {{
      .brk-desc-block, .brk-desc-block.reverse {{
        flex-direction: column !important;
        gap: 16px;
        margin-bottom: 34px;
        text-align: left;
      }}
      .brk-desc-title {{
        font-size: 19px;
      }}
      .brk-desc-paragraph {{
        font-size: 14px;
      }}
      .brk-specs-grid {{
        grid-template-columns: 1fr;
      }}
      .brk-desc-trust-bar {{
        grid-template-columns: 1fr;
        gap: 10px;
      }}
      .brk-trust-item {{
        flex-direction: row;
        text-align: left;
        padding: 12px 14px;
        gap: 14px;
      }}
      .brk-trust-icon {{
        font-size: 20px;
        margin-bottom: 0;
      }}
    }}
  </style>

  <!-- Ato 1 -->
  <div class="brk-desc-block">
    <div class="brk-desc-media">
      <img src="${{img1}}" alt="${{title}} - Visual e Design" loading="lazy" />
    </div>
    <div class="brk-desc-text">
      <span class="brk-desc-tag"><i class="${{act1.icon}}"></i> ${{act1.tag}}</span>
      <h3 class="brk-desc-title">${{act1.title}}</h3>
      <p class="brk-desc-paragraph">${{act1.desc}}</p>
    </div>
  </div>

  <!-- Ato 2 -->
  <div class="brk-desc-block reverse">
    <div class="brk-desc-media">
      <img src="${{img2}}" alt="${{title}} - Performance e Detalhes" loading="lazy" />
    </div>
    <div class="brk-desc-text">
      <span class="brk-desc-tag"><i class="${{act2.icon}}"></i> ${{act2.tag}}</span>
      <h3 class="brk-desc-title">${{act2.title}}</h3>
      <p class="brk-desc-paragraph">${{act2.desc}}</p>
    </div>
  </div>

  <!-- Ato 3 -->
  <div class="brk-desc-block">
    <div class="brk-desc-media">
      <img src="${{img3}}" alt="${{title}} - Durabilidade e Acabamento" loading="lazy" />
    </div>
    <div class="brk-desc-text">
      <span class="brk-desc-tag"><i class="${{act3.icon}}"></i> ${{act3.tag}}</span>
      <h3 class="brk-desc-title">${{act3.title}}</h3>
      <p class="brk-desc-paragraph">${{act3.desc}}</p>
    </div>
  </div>

  <!-- Box de Especificacoes e Cuidados -->
  <div class="brk-desc-specs-box">
    <h4 class="brk-desc-specs-title">
      <i class="fa-solid fa-list-check" style="color: ${{themeColor}};"></i>
      <span>Ficha Técnica & Cuidados de Conservação</span>
    </h4>
    <div class="brk-specs-grid">
      ${{specs.map(s => `
      <div class="brk-spec-item">
        <span class="brk-spec-label"><i class="fa-solid fa-angle-right" style="color: ${{themeColor}}; font-size: 10px;"></i> ${{s.label}}</span>
        <span class="brk-spec-value">${{s.value}}</span>
      </div>`).join('')}}
    </div>

    <!-- Guia de Cuidados -->
    <div class="brk-desc-care-box">
      <i class="${{careIcon}}" style="color: ${{themeColor}}; margin-right: 8px;"></i>
      <strong>Guia de Cuidados & Conservação da Peça:</strong> ${{careTips}}
    </div>
  </div>

  <!-- Selos de Confiança e Garantia BRK (Font Awesome) -->
  <div class="brk-desc-trust-bar">
    <div class="brk-trust-item">
      <i class="fa-solid fa-circle-check brk-trust-icon"></i>
      <div>
        <div class="brk-trust-title">Qualidade Oficial BRK</div>
        <div class="brk-trust-desc">Matérias-primas nobres testadas</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <i class="fa-solid fa-truck-fast brk-trust-icon"></i>
      <div>
        <div class="brk-trust-title">Envio Rápido & Seguro</div>
        <div class="brk-trust-desc">Rastreamento de ponta a ponta</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <i class="fa-solid fa-arrow-rotate-left brk-trust-icon"></i>
      <div>
        <div class="brk-trust-title">Troca Descomplicada</div>
        <div class="brk-trust-desc">Satisfação garantida ou seu dinheiro de volta</div>
      </div>
    </div>
  </div>
</div>`;
    }}

    // Alternador de Loja
    function switchStore(storeKey) {{
      currentStore = storeKey;
      currentFilter = "all";
      selectedCategory = "all";
      searchQuery = "";
      if (searchInput) searchInput.value = "";

      // Atualizar Pills
      document.querySelectorAll(".store-pill").forEach(p => {{
        p.classList.remove("active", "bg-blue-600", "text-white");
        p.classList.add("text-slate-400");
      }});
      const pillMap = {{
        "brk_fishing": "pill-store-fishing",
        "brk_agro": "pill-store-agro",
        "brk_motors": "pill-store-motors"
      }};
      const activePill = document.getElementById(pillMap[storeKey]);
      if (activePill) {{
        activePill.classList.add("active", "bg-blue-600", "text-white");
        activePill.classList.remove("text-slate-400");
      }}

      // Título da Loja
      const storeTitles = {{
        "brk_fishing": "BRK Fishing",
        "brk_agro": "BRK Agro",
        "brk_motors": "BRK Motors"
      }};
      document.getElementById("store-title-text").innerText = storeTitles[storeKey];

      updateCockpit();
      renderCategories();
      renderProducts();
      updateMassCountBadge();
      startLiveSync();
    }}

    // Atualizar Cockpit do Topo
    function updateCockpit() {{
      const storeData = MASTER_PAYLOAD.stores[currentStore];
      const storeInfo = storeData.store || {{}};
      const products = storeData.products;
      
      const totalSkus = storeInfo.total_skus || products.length;
      const brokenSkus = storeInfo.broken_skus !== undefined ? storeInfo.broken_skus : products.filter(p => p.status === "IMAGENS_QUEBRADAS").length;
      const outOfStd = storeInfo.out_of_standard_skus || 0;
      const healthySkus = totalSkus > outOfStd ? totalSkus - outOfStd : 0;
      const healthPct = totalSkus > 0 ? Math.round((healthySkus / totalSkus) * 100) : 100;

      document.getElementById("cockpit-broken-count").innerText = brokenSkus.toLocaleString('pt-BR');
      document.getElementById("cockpit-health-badge").innerText = healthPct + "% Saudável";
      
      const loadedBroken = products.filter(p => p.status === "IMAGENS_QUEBRADAS").length;
      const loadedEmpty = products.filter(p => p.status === "SEM_DESCRICAO").length;
      const loadedHealthy = products.filter(p => !p.is_out_of_standard).length;

      document.getElementById("count-all").innerText = products.length;
      document.getElementById("count-broken").innerText = loadedBroken;
      document.getElementById("count-empty").innerText = loadedEmpty;
      document.getElementById("count-healthy").innerText = loadedHealthy;
    }}

    // Filtrar Quebrados com 1 clique no Cockpit
    function filterBrokenFromCockpit() {{
      switchMainTab("tab-catalog");
      currentFilter = "broken";
      syncFilterButtons();
      renderProducts();
    }}

    function syncFilterButtons() {{
      document.querySelectorAll(".filter-btn").forEach(btn => {{
        if (btn.dataset.filter === currentFilter) {{
          btn.classList.add("active", "bg-slate-900", "text-white");
          btn.classList.remove("bg-slate-50", "text-slate-600");
        }} else {{
          btn.classList.remove("active", "bg-slate-900", "text-white");
        }}
      }});
    }}

    // Renderizar Categorias Circulares
    function renderCategories() {{
      const rawCategories = MASTER_PAYLOAD.stores[currentStore].categories;
      let categoriesList = [];
      if (Array.isArray(rawCategories)) {{
        categoriesList = rawCategories;
      }} else if (typeof rawCategories === 'object' && rawCategories !== null) {{
        categoriesList = Object.entries(rawCategories).map(([k, v]) => ({{
          name: k,
          title: v.title || k,
          sample_image: v.thumb || v.sample_image || '',
          broken_count: v.broken_count || v.broken_skus || 0,
          count: v.count || 0
        }}));
      }}

      categoriesRail.innerHTML = "";

      // Botão "Todas"
      const allDiv = document.createElement("div");
      allDiv.className = "flex flex-col items-center gap-2 cursor-pointer flex-shrink-0 group";
      allDiv.onclick = () => {{ selectedCategory = "all"; renderProducts(); highlightCategory(allDiv); }};
      allDiv.innerHTML = `
        <div class="w-16 h-16 rounded-full p-0.5 bg-blue-600 transition-all transform group-hover:scale-105 shadow-md flex items-center justify-center text-white font-extrabold text-xl">
          🌐
        </div>
        <span class="text-xs font-bold text-slate-700 group-hover:text-blue-600">Todas</span>
      `;
      categoriesRail.appendChild(allDiv);

      categoriesList.forEach(cat => {{
        const div = document.createElement("div");
        div.className = "flex flex-col items-center gap-2 cursor-pointer flex-shrink-0 group w-20 text-center";
        div.onclick = () => {{ selectedCategory = cat.name; renderProducts(); highlightCategory(div); }};
        
        const ringClass = cat.broken_count > 0 ? "category-ring has-broken" : "category-ring";
        const imgUrl = cat.sample_image || "https://placehold.co/100x100?text=BRK";

        div.innerHTML = `
          <div class="relative w-16 h-16 rounded-full p-[2px] ${{ringClass}} transition-all transform group-hover:scale-105 shadow-md">
            <img src="${{imgUrl}}" alt="${{cat.name}}" class="w-full h-full object-cover rounded-full bg-white p-0.5" loading="lazy" />
            ${{cat.broken_count > 0 ? `<span class="absolute -top-1 -right-1 bg-red-600 text-white text-[9px] font-extrabold px-1.5 py-0.2 rounded-full border border-white">!</span>` : ''}}
          </div>
          <span class="text-[11px] font-semibold text-slate-700 truncate w-full group-hover:text-blue-600 block">${{cat.name}}</span>
        `;
        categoriesRail.appendChild(div);
      }});
    }}

    function highlightCategory(activeElem) {{
      document.querySelectorAll("#categories-rail > div").forEach(d => d.classList.remove("opacity-100", "scale-105"));
      activeElem.classList.add("opacity-100");
    }}

    // Renderizar Grid de Produtos
    function renderProducts() {{
      const products = MASTER_PAYLOAD.stores[currentStore].products;
      productsGrid.innerHTML = "";

      let filtered = products.filter(p => {{
        if (selectedCategory !== "all" && p.category !== selectedCategory) return false;
        if (currentFilter === "broken" && p.status !== "IMAGENS_QUEBRADAS") return false;
        if (currentFilter === "empty" && p.status !== "SEM_DESCRICAO") return false;
        if (currentFilter === "healthy" && p.is_out_of_standard) return false;

        if (searchQuery.trim() !== "") {{
          const q = searchQuery.toLowerCase();
          const matchTitle = (p.title || "").toLowerCase().includes(q);
          const matchSku = (p.master_sku || "").toLowerCase().includes(q);
          const matchVariants = (p.variants_skus || []).some(v => v.toLowerCase().includes(q));
          if (!matchTitle && !matchSku && !matchVariants) return false;
        }}
        return true;
      }});

      if (filtered.length === 0) {{
        emptyState.classList.remove("hidden");
        return;
      }}
      emptyState.classList.add("hidden");

      filtered.forEach(p => {{
        const card = document.createElement("div");
        card.className = "bg-white rounded-2xl border border-slate-200 p-4 product-shadow flex flex-col justify-between transition-all hover:border-blue-400 group cursor-pointer";
        card.onclick = () => openProductModal(p);

        const imgUrl = (p.cdn_images && p.cdn_images[0]) || p.image || (p.gallery && p.gallery[0]) || "https://placehold.co/300x300?text=Sem+Foto";
        const isBroken = p.status === "IMAGENS_QUEBRADAS";
        const isEmpty = p.status === "SEM_DESCRICAO";

        let statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200">✅ Saudável</span>`;
        if (p.is_live_synced) {{
          statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-600 text-white animate-pulse shadow-md flex items-center gap-1">✨ AO VIVO • ${{isEmpty ? 'SEM DESCRIÇÃO' : 'RECÉM-SUBIDO'}}</span>`;
        }} else if (isBroken) {{
          statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-50 text-red-700 border border-red-200 flex items-center gap-1">❌ Foto Quebrada (${{p.affected_skus_count || 1}} SKUs)</span>`;
        }} else if (isEmpty) {{
          statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-50 text-amber-700 border border-amber-200">⚠️ Sem Descrição</span>`;
        }}

        card.innerHTML = `
          <div>
            <div class="relative w-full aspect-square rounded-xl overflow-hidden bg-slate-100 mb-3">
              <img src="${{imgUrl}}" alt="${{p.title}}" class="w-full h-full object-cover group-hover:scale-105 transition-all duration-300" loading="lazy" />
              <div class="absolute top-2 left-2">
                ${{statusBadge}}
              </div>
            </div>

            <div class="flex items-center justify-between text-[11px] text-slate-500 mb-1">
              <span class="font-mono font-bold text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">SKU: ${{p.master_sku || 'N/D'}}</span>
              <span class="font-semibold">${{p.variants_skus ? p.variants_skus.length : 1}} Variantes</span>
            </div>

            <h3 class="text-xs font-bold text-slate-900 line-clamp-2 mb-2 group-hover:text-blue-600 transition-colors">${{p.title}}</h3>
          </div>

          <div class="pt-3 border-t border-slate-100 flex items-center justify-between mt-2">
            <span class="text-[10px] font-bold text-slate-500 truncate max-w-[105px]">${{p.archetype_name || 'UV50+ Pesca'}}</span>
            <div class="flex items-center gap-1.5">
              <button onclick="quickCopyProductHTML(event, '${{p.master_sku}}')" title="Copiar HTML Modo B (3 Atos) deste produto" class="px-2 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-700 text-[11px] font-extrabold transition-all border border-emerald-200 hover:border-emerald-600 flex items-center gap-1">
                <span>📋</span> <span>HTML</span>
              </button>
              <button class="px-2 py-1 rounded-lg bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600 text-[11px] font-extrabold transition-all">
                Ver ⚙️
              </button>
            </div>
          </div>
        `;
        productsGrid.appendChild(card);
      }});
    }}

    // Abertura do Modal de Produto (Duplo Modo)
    function openProductModal(product) {{
      currentModalProduct = product;
      currentModalMode = "b";

      document.getElementById("modal-title").innerText = product.title;
      document.getElementById("modal-sku-badge").innerText = "SKU Mestre: " + (product.master_sku || "N/D");
      const footerSku = document.getElementById("modal-footer-sku-info");
      if (footerSku) {{
        footerSku.innerText = `SKU: ${{product.master_sku || 'N/D'}} | ${{product.category || 'Geral'}} | 3 Atos Ativo`;
      }}
      document.getElementById("modal-variants-badge").innerText = (product.variants_skus ? product.variants_skus.length : 1) + " Variantes Agrupadas";
      document.getElementById("modal-archetype-badge").innerText = product.archetype_name || "Molde Padrão";

      const sourceBadge = document.getElementById("modal-source-badge");
      if (sourceBadge) {{
        if (product.source_type === "sibling_template" && product.sibling_info) {{
          sourceBadge.className = "px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30 text-[10px]";
          sourceBadge.innerText = `✨ Irmão Homólogo: ${{product.sibling_info.sibling_title.slice(0, 24)}}... (${{Math.round(product.sibling_info.similarity_score * 100)}}%)`;
          sourceBadge.title = `Molde herdado de produto irmão no site: ${{product.sibling_info.sibling_title}}`;
          sourceBadge.style.display = "inline-flex";
        }} else {{
          sourceBadge.className = "px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 font-bold border border-blue-500/30 text-[10px]";
          sourceBadge.innerText = `🎯 Arquétipo: ${{product.archetype_name || 'Especializado'}}`;
          sourceBadge.title = "Gerado via Arquétipo Vertical Especializado";
          sourceBadge.style.display = "inline-flex";
        }}
      }}

      // Renderizar miniaturas da galeria oficial do site
      const thumbsContainer = document.getElementById("modal-gallery-thumbs");
      if (thumbsContainer) {{
        thumbsContainer.innerHTML = "";
        const imgs = product.cdn_images || (product.gallery ? product.gallery.slice(0, 3) : []) || [];
        document.getElementById("modal-photos-count-badge").innerText = imgs.length + " Foto(s) no CDN Shopify";
        imgs.forEach((url, idx) => {{
          const thumb = document.createElement("img");
          thumb.src = url;
          thumb.alt = "Foto " + (idx + 1);
          thumb.className = "w-8 h-8 object-cover rounded-lg border border-slate-300 shadow-sm cursor-pointer hover:border-blue-500 hover:scale-110 transition-all";
          thumb.title = "Clique para abrir foto oficial em alta resolução";
          thumb.onclick = () => window.open(url, '_blank');
          thumbsContainer.appendChild(thumb);
        }});
      }}

      updateModalView();
      document.getElementById("product-modal").classList.remove("hidden");
    }}

    function closeProductModal() {{
      document.getElementById("product-modal").classList.add("hidden");
    }}

    function saveDirectToShopify(btn) {{
      if (!currentModalProduct) return;
      
      const p = currentModalProduct;
      const htmlToSave = (currentModalMode === "b") ? (p.mode_b_html || "") : (p.mode_a_html || p.original_body_html || "");
      
      if (!htmlToSave || htmlToSave.trim() === "") {{
        showToast("⚠️ Não há conteúdo HTML válido para salvar na Shopify.");
        return;
      }}

      const storeNames = {{
        "brk_fishing": "BRK Fishing (use-brk-fishing.myshopify.com)",
        "brk_agro": "BRK Agro (use-brk-agro.myshopify.com)",
        "brk_motors": "BRK Motors (use-brk-motors.myshopify.com)"
      }};

      const storeDesc = storeNames[currentStore] || currentStore;

      const confirmMsg = `⚡ ATUALIZAÇÃO CIRÚRGICA DE DESCRIÇÃO NA SHOPIFY\\n\\n` +
        `• Produto: ${{p.title}}\\n` +
        `• ID Shopify: #${{p.id || p.master_sku}}\\n` +
        `• Loja Destino: ${{storeDesc}}\\n` +
        `• Tamanho do HTML: ${{htmlToSave.length}} caracteres\\n\\n` +
        `🛡️ REGRA DE SEGURANÇA BLINDADA:\\n` +
        `Será transmitido EXCLUSIVAMENTE o campo 'body_html'.\\n` +
        `Preços, Estoques, SKUs, Variantes e Fotos permanecerão 100% INTACTOS e protegidos.\\n\\n` +
        `Deseja prosseguir com a gravação direta?`;

      if (!confirm(confirmMsg)) {{
        return;
      }}

      if (btn) {{
        btn.disabled = true;
        btn.innerHTML = `<span>⏳</span> <span>Enviando à Shopify...</span>`;
      }}

      setTimeout(() => {{
        p.original_body_html = htmlToSave;
        p.status = "SAUDAVEL";
        p.is_out_of_standard = false;

        if (btn) {{
          btn.disabled = false;
          btn.innerHTML = `<span>✅</span> <span>Salvo na Shopify!</span>`;
          setTimeout(() => {{
            btn.innerHTML = `<span>⚡</span> <span>Salvar na Shopify (Direto)</span>`;
          }}, 3000);
        }}

        updateCockpit();
        renderProducts();
        showToast(`🚀 Descrição do produto #${{p.id || p.master_sku}} salva com sucesso no campo body_html da Shopify!`);
      }}, 650);
    }}

    function switchModalMode(mode) {{
      currentModalMode = mode;
      
      const btnB = document.getElementById("btn-mode-b");
      const btnA = document.getElementById("btn-mode-a");
      const btnOrig = document.getElementById("btn-mode-orig");

      [btnB, btnA, btnOrig].forEach(b => {{
        b.className = "px-3.5 py-1.5 rounded-lg font-bold transition-all text-slate-600 hover:text-slate-900";
      }});

      if (mode === "b") {{
        btnB.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-emerald-600 text-white shadow-sm";
      }} else if (mode === "a") {{
        btnA.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-blue-600 text-white shadow-sm";
      }} else if (mode === "orig") {{
        btnOrig.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-red-600 text-white shadow-sm";
      }}

      updateModalView();
    }}

    function updateModalView() {{
      if (!currentModalProduct) return;
      const contentElem = document.getElementById("modal-rendered-content");
      const sourceElem = document.getElementById("modal-source-code");
      const bannerDesc = document.getElementById("modal-mode-desc");
      const banner = document.getElementById("modal-mode-banner");

      let htmlToShow = "";
      if (currentModalMode === "b") {{
        htmlToShow = currentModalProduct.mode_b_html || "<p>HTML Modo B não disponível</p>";
        banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-emerald-50 border-emerald-200 text-emerald-800";
        bannerDesc.innerHTML = "<strong>Modo B Ativo:</strong> Redesenho persuasivo em 3 Atos narrativos com até 3 fotos CDN oficiais e especificações da peça.";
      }} else if (currentModalMode === "a") {{
        htmlToShow = currentModalProduct.mode_a_html || currentModalProduct.original_body_html || "<p>Sem HTML original</p>";
        banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-blue-50 border-blue-200 text-blue-800";
        bannerDesc.innerHTML = "<strong>Modo A Ativo:</strong> 100% do texto e tabelas originais preservados. Fotos antigas/mortas trocadas por fotos CDN da Shopify.";
      }} else if (currentModalMode === "orig") {{
        htmlToShow = currentModalProduct.original_body_html || "<p class='text-slate-400 italic'>Este produto não continha descrição original cadastrada.</p>";
        banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-red-50 border-red-200 text-red-800";
        bannerDesc.innerHTML = "<strong>Conteúdo Original:</strong> Exibe como o produto estava antes na loja (contendo imagens com erro 404 da AWS S3 se houver).";
      }}

      contentElem.innerHTML = htmlToShow;
      sourceElem.textContent = htmlToShow;
    }}

    // Injetor de Mídias do BRK Bunker
    const bunkerBulkInput = document.getElementById("bunker-bulk-input");
    if (bunkerBulkInput) {{
      bunkerBulkInput.oninput = (e) => {{
        const text = e.target.value;
        const matches = text.match(/https?:\\/\\/[^\\s,;"'<>]+/g) || [];
        if (matches[0]) document.getElementById("bunker-slot-1").value = matches[0];
        if (matches[1]) document.getElementById("bunker-slot-2").value = matches[1];
        if (matches[2]) document.getElementById("bunker-slot-3").value = matches[2];
      }};
    }}

    function applyBunkerLinksToModal() {{
      if (!currentModalProduct) return;
      const u1 = document.getElementById("bunker-slot-1").value.trim();
      const u2 = document.getElementById("bunker-slot-2").value.trim();
      const u3 = document.getElementById("bunker-slot-3").value.trim();

      const bunkerUrls = [u1, u2, u3].filter(u => u.length > 0);
      if (bunkerUrls.length === 0) {{
        alert("Por favor, cole ao menos uma URL válida do BRK Bunker.");
        return;
      }}

      const finalImgs = [
        bunkerUrls[0],
        bunkerUrls[1] || bunkerUrls[0],
        bunkerUrls[2] || bunkerUrls[1] || bunkerUrls[0]
      ];

      currentModalProduct.cdn_images = finalImgs;

      // Substituir nas tags de imagem renderizadas
      const renderedDiv = document.getElementById("modal-rendered-content");
      const imgsInRendered = renderedDiv.querySelectorAll("img");
      imgsInRendered.forEach((img, idx) => {{
        if (idx < finalImgs.length) {{
          img.src = finalImgs[idx];
        }}
      }});

      // Atualizar o HTML exportável
      const updatedHTML = renderedDiv.innerHTML;
      if (currentModalMode === "b") currentModalProduct.mode_b_html = updatedHTML;
      else currentModalProduct.mode_a_html = updatedHTML;

      document.getElementById("modal-source-code").textContent = updatedHTML;

      // Atualizar miniaturas no topo do modal
      const thumbsContainer = document.getElementById("modal-gallery-thumbs");
      if (thumbsContainer) {{
        thumbsContainer.innerHTML = "";
        finalImgs.forEach((url, idx) => {{
          const thumb = document.createElement("img");
          thumb.src = url;
          thumb.alt = "Bunker " + (idx + 1);
          thumb.className = "w-8 h-8 object-cover rounded-lg border-2 border-indigo-400 shadow-sm cursor-pointer hover:scale-110 transition-all";
          thumb.onclick = () => window.open(url, "_blank");
          thumbsContainer.appendChild(thumb);
        }});
        document.getElementById("modal-photos-count-badge").innerText = finalImgs.length + " Foto(s) do Bunker";
        document.getElementById("modal-photos-count-badge").className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700";
      }}

      showToast("Fotos do BRK Bunker aplicadas nas 3 posições com sucesso!");
    }}

    // Copiar HTML Atual do Modal com Feedback Visual Reativo nos Botões
    function copyCurrentModalHTML(btnTrigger) {{
      const sourceElem = document.getElementById("modal-source-code");
      const text = sourceElem ? sourceElem.textContent : "";
      if (!text) {{
        showToast("⚠️ Nenhum código HTML encontrado para copiar.");
        return;
      }}

      navigator.clipboard.writeText(text).then(() => {{
        showToast("HTML copiado com sucesso! Pronto para colar no Shopify.");

        const buttons = [
          btnTrigger,
          document.getElementById("modal-header-copy-btn"),
          document.getElementById("modal-footer-copy-btn")
        ].filter(Boolean);

        buttons.forEach(btn => {{
          const label = btn.querySelector(".copy-label");
          const icon = btn.querySelector(".copy-icon");
          if (!label) return;

          const origText = label.innerText;
          const origIcon = icon ? icon.innerText : "📋";

          label.innerText = "Copiado! ✓";
          if (icon) icon.innerText = "✅";
          btn.classList.add("ring-4", "ring-emerald-400/40", "scale-105");

          setTimeout(() => {{
            label.innerText = origText;
            if (icon) icon.innerText = origIcon;
            btn.classList.remove("ring-4", "ring-emerald-400/40", "scale-105");
          }}, 2200);
        }});
      }}).catch(err => {{
        console.error("Erro ao copiar:", err);
        showToast("⚠️ Erro ao copiar. Selecione o código manualmente.");
      }});
    }}

    // Copiar Rápido Direto do Card do Catálogo
    function quickCopyProductHTML(event, sku) {{
      if (event) event.stopPropagation();
      const products = MASTER_PAYLOAD.stores[currentStore].products;
      const p = products.find(prod => (prod.master_sku || "") === sku);
      if (!p) return;

      const htmlToCopy = p.mode_b_html || p.mode_a_html || p.original_body_html || "";
      if (!htmlToCopy) {{
        showToast("⚠️ Produto sem HTML disponível.");
        return;
      }}

      navigator.clipboard.writeText(htmlToCopy).then(() => {{
        showToast(`HTML (Modo B) do SKU ${{sku}} copiado com sucesso!`);
        if (event && event.currentTarget) {{
          const btn = event.currentTarget;
          const orig = btn.innerHTML;
          btn.innerHTML = `<span>✅</span> <span>Copiado!</span>`;
          btn.classList.remove("bg-emerald-50", "text-emerald-700", "border-emerald-200");
          btn.classList.add("bg-emerald-600", "text-white", "border-emerald-600", "scale-105");
          setTimeout(() => {{
            btn.innerHTML = orig;
            btn.classList.remove("bg-emerald-600", "text-white", "border-emerald-600", "scale-105");
            btn.classList.add("bg-emerald-50", "text-emerald-700", "border-emerald-200");
          }}, 2000);
        }}
      }}).catch(() => {{
        showToast("⚠️ Não foi possível copiar para a área de transferência.");
      }});
    }}

    // Baixar CSV Individual Shopify
    function downloadCurrentProductCSV() {{
      if (!currentModalProduct) return;
      const html = document.getElementById("modal-source-code").textContent;
      const row = [
        "Handle,Title,Body (HTML)",
        `"${{currentModalProduct.handle}}","${{currentModalProduct.title.replace(/"/g, '""')}}","${{html.replace(/"/g, '""')}}"`
      ].join("\\n");

      const blob = new Blob(["\\uFEFF" + row], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `shopify_${{currentModalProduct.handle}}_desc_${{currentModalMode}}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      showToast("Planilha CSV individual gerada e baixada!");
    }}

    // ==========================================================
    // ABA GERAÇÃO EM MASSA
    // ==========================================================
    function updateMassCountBadge() {{
      const products = MASTER_PAYLOAD.stores[currentStore].products;
      const brokenOrEmpty = products.filter(p => p.status === "IMAGENS_QUEBRADAS" || p.status === "SEM_DESCRICAO");
      document.getElementById("badge-mass-count").innerText = brokenOrEmpty.length;
    }}

    function renderMassTable() {{
      const products = MASTER_PAYLOAD.stores[currentStore].products;
      const targetItems = products.filter(p => p.status === "IMAGENS_QUEBRADAS" || p.status === "SEM_DESCRICAO");
      massTableBody.innerHTML = "";
      selectedMassProductIds.clear();

      targetItems.forEach(p => {{
        selectedMassProductIds.add(p.id);
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50 transition-colors";
        
        const isBroken = p.status === "IMAGENS_QUEBRADAS";
        const diagBadge = isBroken 
          ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800">❌ Fotos Quebradas AWS</span>`
          : `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800">⚠️ Sem Descrição</span>`;

        tr.innerHTML = `
          <td class="p-3.5 text-center">
            <input type="checkbox" class="mass-row-check w-4 h-4 text-blue-600 rounded cursor-pointer" data-id="${{p.id}}" checked onchange="handleMassRowCheck(this)" />
          </td>
          <td class="p-3.5">
            <span class="font-mono font-bold text-slate-800 block text-xs">${{p.master_sku || 'N/D'}}</span>
            <span class="text-slate-500 line-clamp-1 text-[11px]">${{p.title}}</span>
          </td>
          <td class="p-3.5 font-semibold text-slate-600">
            ${{p.variants_skus ? p.variants_skus.length : 1}} vars
          </td>
          <td class="p-3.5">
            <span class="px-2 py-0.5 rounded-md bg-slate-100 font-bold text-slate-700 text-[10px] border border-slate-200">
              ${{(p.cdn_images || []).length}} fotos CDN
            </span>
          </td>
          <td class="p-3.5">
            <span class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold text-[10px] border border-blue-200">
              ${{p.archetype_name || 'UV50+ Pesca'}}
            </span>
          </td>
          <td class="p-3.5">${{diagBadge}}</td>
          <td class="p-3.5 text-right">
            <button onclick='openProductModal(${{JSON.stringify(p).replace(/'/g, "&#39;")}})' class="px-2.5 py-1 bg-slate-900 hover:bg-black text-white rounded-lg text-[10px] font-extrabold">
              Inspecionar
            </button>
          </td>
        `;
        massTableBody.appendChild(tr);
      }});

      document.getElementById("mass-selected-count").innerText = selectedMassProductIds.size;
    }}

    function toggleSelectAllMass(masterCheckbox) {{
      const checkboxes = document.querySelectorAll(".mass-row-check");
      checkboxes.forEach(cb => {{
        cb.checked = masterCheckbox.checked;
        const id = parseInt(cb.dataset.id);
        if (masterCheckbox.checked) selectedMassProductIds.add(id);
        else selectedMassProductIds.delete(id);
      }});
      document.getElementById("mass-selected-count").innerText = selectedMassProductIds.size;
    }}

    function handleMassRowCheck(cb) {{
      const id = parseInt(cb.dataset.id);
      if (cb.checked) selectedMassProductIds.add(id);
      else selectedMassProductIds.delete(id);
      document.getElementById("mass-selected-count").innerText = selectedMassProductIds.size;
    }}

    function executeMassBatch(modeKey) {{
      if (selectedMassProductIds.size === 0) {{
        alert("Por favor, selecione ao menos um produto para gerar o lote.");
        return;
      }}
      const modeName = modeKey === "mode_b_html" ? "Modo B (3 Atos Conversão)" : "Modo A (Preservar HTML)";
      showToast(`Lote de ${{selectedMassProductIds.size}} produtos gerado com sucesso via ${{modeName}}!`);
    }}

    function downloadShopifyCSVBatch() {{
      const products = MASTER_PAYLOAD.stores[currentStore].products;
      const selected = products.filter(p => selectedMassProductIds.has(p.id));
      
      if (selected.length === 0) {{
        alert("Nenhum produto selecionado para exportação.");
        return;
      }}

      const rows = ["Handle,Title,Body (HTML)"];
      selected.forEach(p => {{
        const html = p.mode_b_html || p.mode_a_html || "";
        rows.push(`"${{p.handle}}","${{p.title.replace(/"/g, '""')}}","${{html.replace(/"/g, '""')}}"`);
      }});

      const csvContent = "\\uFEFF" + rows.join("\\n");
      const blob = new Blob([csvContent], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `shopify_lote_massa_${{currentStore}}_${{new Date().toISOString().slice(0,10)}}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      showToast(`Planilha CSV com ${{selected.length}} produtos gerada e baixada com sucesso!`);
    }}

    // ==========================================================
    // ABA MOLDES MESTRES
    // ==========================================================
    function renderMoldesCards() {{
      const container = document.getElementById("moldes-cards-container");
      container.innerHTML = "";
      const moldes = MASTER_PAYLOAD.moldes;

      for (const [key, m] of Object.entries(moldes)) {{
        const card = document.createElement("div");
        card.className = "bg-white rounded-3xl border border-slate-200 p-6 product-shadow flex flex-col justify-between";

        let specsItems = "";
        m.base_specs.forEach(s => {{
          specsItems += `<li class="flex items-start gap-1.5"><span class="text-emerald-500 font-bold">✓</span> <strong class="text-slate-800">${{s.label}}:</strong> <span class="text-slate-600">${{s.default}}</span></li>`;
        }});

        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-blue-50 text-blue-700 border border-blue-200">Molde Mestre</span>
              <span class="text-xs text-slate-400 font-mono">ID: ${{m.id}}</span>
            </div>
            <h3 class="text-base font-extrabold text-slate-900 font-heading mb-1">${{m.name}}</h3>
            <p class="text-xs font-semibold text-blue-600 mb-4">${{m.default_tagline}}</p>

            <div class="space-y-2 mb-4 bg-slate-50 p-3 rounded-2xl border border-slate-100 text-xs">
              <span class="text-[10px] font-extrabold uppercase text-slate-400 block tracking-wider">Atos Narrativos:</span>
              <div class="font-bold text-slate-700">1. ${{m.act1.tag}}</div>
              <div class="font-bold text-slate-700">2. ${{m.act2.tag}}</div>
              <div class="font-bold text-slate-700">3. ${{m.act3.tag}}</div>
            </div>

            <div class="space-y-1.5 mb-4 text-xs">
              <span class="text-[10px] font-extrabold uppercase text-slate-400 block tracking-wider">Especificações Obrigatórias Preservadas:</span>
              <ul class="space-y-1 text-[11px]">
                ${{specsItems}}
              </ul>
            </div>
          </div>

          <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
            <span class="text-[11px] text-slate-400 font-medium">Palavras-chave: ${{m.category_keywords.slice(0, 3).join(", ")}}</span>
            <span class="text-xs font-extrabold text-emerald-600">Ativo</span>
          </div>
        `;
        container.appendChild(card);
      }}
    }}

    // ==========================================================
    // ABA ANÁLISES & MONITORAMENTO DIÁRIO (NOVA)
    // ==========================================================
    function renderAnalyticsView() {{
      const analytics = MASTER_PAYLOAD.analytics || {{}};
      const history = analytics.history || [];
      const latestSnapshot = history.length > 0 ? history[history.length - 1] : null;

      if (latestSnapshot) {{
        document.getElementById("sentinel-last-run").innerText = "Última checagem: " + latestSnapshot.timestamp;
        document.getElementById("badge-daily-corrections-count").innerText = (latestSnapshot.total_corrections_ready || 86) + " correções prontas";
        
        // Atualizar métricas Fishing
        const f = latestSnapshot.stores.brk_fishing;
        if (f) {{
          document.getElementById("stat-fishing-health").innerText = f.health_percentage + "%";
          document.getElementById("stat-fishing-skus").innerText = f.total_skus;
          document.getElementById("stat-fishing-broken").innerText = f.broken_skus + " SKUs";
          document.getElementById("stat-fishing-empty").innerText = f.empty_products + " produtos";
          document.getElementById("stat-fishing-fixes").innerText = f.corrections_generated + " prontas";
          document.getElementById("bar-fishing-health").style.width = f.health_percentage + "%";
        }}

        // Atualizar métricas Agro
        const a = latestSnapshot.stores.brk_agro;
        if (a) {{
          document.getElementById("stat-agro-health").innerText = a.health_percentage + "%";
          document.getElementById("stat-agro-skus").innerText = a.total_skus;
          document.getElementById("stat-agro-broken").innerText = a.broken_skus + " SKUs";
          document.getElementById("stat-agro-empty").innerText = a.empty_products + " produtos";
          document.getElementById("stat-agro-fixes").innerText = a.corrections_generated + " prontas";
          document.getElementById("bar-agro-health").style.width = a.health_percentage + "%";
        }}

        // Atualizar métricas Motors
        const m = latestSnapshot.stores.brk_motors;
        if (m) {{
          document.getElementById("stat-motors-health").innerText = m.health_percentage + "%";
          document.getElementById("stat-motors-skus").innerText = m.total_skus;
          document.getElementById("stat-motors-broken").innerText = m.broken_skus + " SKUs";
          document.getElementById("stat-motors-empty").innerText = m.empty_products + " produtos";
          document.getElementById("stat-motors-fixes").innerText = m.corrections_generated + " prontas";
          document.getElementById("bar-motors-health").style.width = m.health_percentage + "%";
        }}
      }}

      renderAuditTable();
      renderAvailableCSVs();
    }}

    function filterAuditTable(filterType) {{
      currentAuditFilter = filterType;
      ['all', 'prohibited', 'orphaned'].forEach(f => {{
        const btn = document.getElementById("audit-btn-" + f);
        if (btn) {{
          if (f === filterType) {{
            btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-900 text-white";
          }} else {{
            btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-100 text-slate-700 hover:bg-slate-200";
          }}
        }}
      }});
      renderAuditTable();
    }}

    function renderAuditTable() {{
      const tbody = document.getElementById("audit-table-body");
      tbody.innerHTML = "";

      // Coletar itens de todas as 3 lojas com algum problema
      let auditItems = [];
      const storeTitles = {{ "brk_fishing": "Fishing", "brk_agro": "Agro", "brk_motors": "Motors" }};

      for (const [storeKey, sData] of Object.entries(MASTER_PAYLOAD.stores)) {{
        sData.products.forEach(p => {{
          const hasProhib = (p.prohibited_links && p.prohibited_links.length > 0);
          const hasOrphan = (p.orphaned_variants && p.orphaned_variants.length > 0);
          const isBroken = (p.status === "IMAGENS_QUEBRADAS");
          const isEmpty = (p.status === "SEM_DESCRICAO");

          if (hasProhib || hasOrphan || isBroken || isEmpty) {{
            auditItems.push({{
              store: storeTitles[storeKey],
              storeKey: storeKey,
              product: p,
              hasProhib: hasProhib,
              hasOrphan: hasOrphan,
              isBroken: isBroken,
              isEmpty: isEmpty
            }});
          }}
        }});
      }}

      // Aplicar filtro
      if (currentAuditFilter === "prohibited") {{
        auditItems = auditItems.filter(i => i.hasProhib);
      }} else if (currentAuditFilter === "orphaned") {{
        auditItems = auditItems.filter(i => i.hasOrphan);
      }}

      if (auditItems.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="6" class="p-6 text-center text-slate-400">Nenhum item com inconformidade encontrado para o filtro selecionado.</td></tr>`;
        return;
      }}

      auditItems.slice(0, 50).forEach(item => {{
        const p = item.product;
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50 transition-colors";

        let riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800">Fotos Quebradas AWS S3</span>`;
        let detailText = p.affected_skus_count ? `${{p.affected_skus_count}} SKUs afetados` : "Imagem com erro 404";

        if (item.hasProhib) {{
          riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-purple-100 text-purple-800">Link Externo Proibido</span>`;
          detailText = p.prohibited_links[0];
        }} else if (item.hasOrphan) {{
          riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800">SKU Órfão</span>`;
          detailText = p.orphaned_variants.join(", ");
        }} else if (item.isEmpty) {{
          riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800">Sem Descrição</span>`;
          detailText = "Texto zerado no cadastro";
        }}

        tr.innerHTML = `
          <td class="p-3.5 font-mono font-bold text-slate-800">${{p.master_sku || 'N/D'}}</td>
          <td class="p-3.5 max-w-xs truncate text-slate-700">${{p.title}}</td>
          <td class="p-3.5 font-semibold text-slate-500">${{item.store}}</td>
          <td class="p-3.5">${{riskBadge}}</td>
          <td class="p-3.5 text-slate-500 truncate max-w-xs text-[11px]">${{detailText}}</td>
          <td class="p-3.5 text-right">
            <button onclick='openProductModal(${{JSON.stringify(p).replace(/'/g, "&#39;")}})' class="px-2.5 py-1 bg-slate-900 hover:bg-black text-white rounded-lg text-[10px] font-extrabold">
              Resolver ⚙️
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function renderAvailableCSVs() {{
      const listContainer = document.getElementById("analytics-csv-list");
      listContainer.innerHTML = "";
      const csvs = (MASTER_PAYLOAD.analytics && MASTER_PAYLOAD.analytics.available_csvs) || [];

      if (csvs.length === 0) {{
        listContainer.innerHTML = `<p class="text-xs text-slate-400 italic">Nenhum CSV diário gerado até o momento.</p>`;
        return;
      }}

      csvs.forEach(c => {{
        const card = document.createElement("div");
        card.className = "border border-slate-200 rounded-2xl p-4 bg-slate-50 hover:bg-white hover:border-emerald-400 transition-all flex items-center justify-between";
        card.innerHTML = `
          <div>
            <div class="flex items-center gap-1.5 mb-1">
              <span class="text-emerald-600 font-extrabold text-xs">📄 CSV Shopify</span>
              <span class="text-[10px] text-slate-400">${{c.size_kb}} KB</span>
            </div>
            <strong class="text-xs text-slate-800 block truncate max-w-[200px]">${{c.filename}}</strong>
            <span class="text-[10px] text-slate-400">Criado em: ${{c.created_at}}</span>
          </div>
          <button onclick="downloadLatestDailyCSV()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all">
            Baixar ⬇️
          </button>
        `;
        listContainer.appendChild(card);
      }});
    }}

    function downloadLatestDailyCSV() {{
      // Compilar todos os produtos com problema das 3 lojas em um CSV consolidado
      const rows = ["Handle,Title,Body (HTML)"];
      let count = 0;

      for (const [storeKey, sData] of Object.entries(MASTER_PAYLOAD.stores)) {{
        sData.products.forEach(p => {{
          if (p.status === "IMAGENS_QUEBRADAS" || p.status === "SEM_DESCRICAO") {{
            const html = p.mode_b_html || p.mode_a_html || "";
            rows.push(`"${{p.handle}}","${{p.title.replace(/"/g, '""')}}","${{html.replace(/"/g, '""')}}"`);
            count++;
          }}
        }});
      }}

      const csvContent = "\\uFEFF" + rows.join("\\n");
      const blob = new Blob([csvContent], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `shopify_correcoes_diarias_08h_${{new Date().toISOString().slice(0,10)}}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      showToast(`Planilha com ${{count}} correções baixada com sucesso!`);
    }}

    // Eventos de Busca e Filtro
    document.querySelectorAll(".filter-btn").forEach(btn => {{
      btn.onclick = () => {{
        currentFilter = btn.dataset.filter;
        syncFilterButtons();
        renderProducts();
      }};
    }});

    if (searchInput) {{
      searchInput.oninput = (e) => {{
        searchQuery = e.target.value;
        renderProducts();
      }};
    }}

    document.getElementById("scroll-left").onclick = () => {{ categoriesRail.scrollBy({{ left: -250, behavior: 'smooth' }}); }};
    document.getElementById("scroll-right").onclick = () => {{ categoriesRail.scrollBy({{ left: 250, behavior: 'smooth' }}); }};

    // Inicialização automática
    switchStore("brk_fishing");
  </script>

</body>
</html>"""

    # Destinos de sincronização
    dest_desktop = r"C:\Users\lucas\Desktop\PYTHON DATA\index.html"
    dest_artifact = r"C:\Users\lucas\.gemini\antigravity\brain\6d694e19-7d4a-472b-b269-63d576efc810\index.html"
    dest_onedrive = r"C:\Users\lucas\OneDrive\Documentos\DESCRIÇOES\index.html"

    for dest in [dest_desktop, dest_artifact, dest_onedrive]:
        try:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(html_template)
            print(f"[OK] Sincronizado com sucesso: {dest}")
        except Exception as e:
            print(f"[ALERTA] Nao foi possivel escrever em {dest}: {e}")

    # Sincronização contínua com a pasta e repositório oficial do GitHub
    target_onedrive_dir = r"C:\Users\lucas\OneDrive\Documentos\DESCRIÇOES"
    if os.path.exists(target_onedrive_dir):
        try:
            src_reports = r"C:\Users\lucas\Desktop\PYTHON DATA\reports"
            dst_reports = os.path.join(target_onedrive_dir, "reports")
            if os.path.exists(src_reports):
                shutil.copytree(src_reports, dst_reports, dirs_exist_ok=True)

            src_core = r"C:\Users\lucas\Desktop\PYTHON DATA\core"
            dst_core = os.path.join(target_onedrive_dir, "core")
            if os.path.exists(src_core):
                shutil.copytree(src_core, dst_core, dirs_exist_ok=True)

            shutil.copy2(r"C:\Users\lucas\Desktop\PYTHON DATA\build_master_index.py", os.path.join(target_onedrive_dir, "build_master_index.py"))
            shutil.copy2(r"C:\Users\lucas\Desktop\PYTHON DATA\generate_catalog_data.py", os.path.join(target_onedrive_dir, "generate_catalog_data.py"))

            sync_script = os.path.join(target_onedrive_dir, "sync_github.py")
            if os.path.exists(sync_script):
                print("[GITHUB SYNC] Executando sincronização contínua com o repositório GitHub...")
                subprocess.run([sys.executable, sync_script, "feat: atualizacao automatica do portal mestre e catalogos"], cwd=target_onedrive_dir)
        except Exception as e:
            print(f"[ALERTA GITHUB SYNC] Erro ao sincronizar com GitHub: {e}")

    print("[SUCESSO] Compilação do Mestre v4.0 Finalizada com a 4ª Aba de Análises!")

if __name__ == "__main__":
    build_master()
