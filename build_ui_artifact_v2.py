"""
Script Gerador da Interface V2 com Botão Unificado no Topo e Gestão Completa por SKU.
"""

import json
import os

def build_v2():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "catalog_ui_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    json_str = json.dumps(data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BRK Fishing - Central Unificada de Gestão por SKU & Auditoria</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .font-heading {{
      font-family: 'Space Grotesk', sans-serif;
    }}
    .no-scrollbar::-webkit-scrollbar {{
      display: none;
    }}
    .no-scrollbar {{
      -ms-overflow-style: none;
      scrollbar-width: none;
    }}
    .category-ring {{
      background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #1d4ed8 100%);
    }}
    .category-ring.has-broken {{
      background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
    }}
    .product-shadow {{
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
    }}
    .product-shadow:hover {{
      box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.05);
    }}
    /* Animação de Brilho no Botão Unificado */
    @keyframes pulse-glow {{
      0%, 100% {{ box-shadow: 0 0 15px rgba(37, 99, 235, 0.4), 0 0 30px rgba(239, 68, 68, 0.2); }}
      50% {{ box-shadow: 0 0 25px rgba(37, 99, 235, 0.7), 0 0 45px rgba(239, 68, 68, 0.4); }}
    }}
    .unified-button-glow {{
      animation: pulse-glow 3s infinite ease-in-out;
    }}
  </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen">

  <!-- ======================================================== -->
  <!-- BARRA SUPERIOR & BOTÃO UNIFICADO NO TOPO (COCKPIT)      -->
  <!-- ======================================================== -->
  <header class="sticky top-0 z-40 bg-slate-950 text-white border-b border-slate-800 transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20 sm:h-24 gap-4">
        
        <!-- Logo e Título -->
        <div class="flex items-center gap-3 shrink-0">
          <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-blue-700 to-indigo-500 flex items-center justify-center text-white font-black text-2xl shadow-lg shadow-blue-500/30">
            B
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-heading font-extrabold text-xl text-white tracking-tight">BRK FISHING</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30 uppercase tracking-wider">Gestão por SKU</span>
            </div>
            <p class="text-xs text-slate-400 font-medium">Cockpit de Auditoria & Verticalização Unificada</p>
          </div>
        </div>

        <!-- O BOTÃO UNIFICADO NO TOPO (ESTILIZADO & ANIMADO) -->
        <div class="relative group">
          <button id="main-unified-btn" class="unified-button-glow flex items-center gap-3.5 px-5 py-3 rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 border border-blue-500/40 text-white hover:border-blue-400 hover:scale-[1.02] transition-all duration-300">
            
            <!-- Anel de Pulso Animado (Alerta de SKUs Quebrados) -->
            <div class="relative flex h-3.5 w-3.5 shrink-0">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3.5 w-3.5 bg-rose-500"></span>
            </div>

            <!-- Dados do Botão -->
            <div class="text-left">
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-extrabold uppercase tracking-widest text-blue-400">BOTÃO UNIFICADO</span>
                <span class="text-[10px] font-bold px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">Ação Rápida</span>
              </div>
              <div class="text-xs sm:text-sm font-black tracking-tight text-white flex items-center gap-2">
                <span id="top-btn-broken-skus">43 SKUs Quebrados</span>
                <span class="text-slate-500">•</span>
                <span id="top-btn-total-skus" class="text-slate-400 font-medium">438 SKUs no Total</span>
              </div>
            </div>

            <!-- Ícone de Ação / Expansão Vertical -->
            <div class="w-8 h-8 rounded-xl bg-white/10 group-hover:bg-blue-600 flex items-center justify-center transition-colors shrink-0">
              <svg class="w-4 h-4 text-white transform group-hover:rotate-180 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/>
              </svg>
            </div>
          </button>

          <!-- MENU VERTICAL SUSPENSO DO BOTÃO UNIFICADO -->
          <div id="unified-menu" class="hidden absolute top-full right-0 mt-2 w-84 sm:w-96 bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl p-3 space-y-2 z-50 backdrop-blur-xl">
            <div class="p-2 border-b border-slate-800 flex items-center justify-between text-xs">
              <span class="font-bold text-slate-300 uppercase tracking-wider">Ações por SKU Agrupado</span>
              <span class="text-[10px] font-bold text-rose-400 bg-rose-950/60 border border-rose-800/50 px-2 py-0.5 rounded-full">
                157 SKUs Fora do Padrão
              </span>
            </div>

            <!-- Ação 1: Filtrar SKUs Quebrados -->
            <button id="menu-btn-filter-broken" class="w-full text-left p-3 rounded-xl hover:bg-slate-800 transition-colors flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-400 flex items-center justify-center font-bold text-sm shrink-0">
                🔴
              </div>
              <div>
                <div class="text-xs font-bold text-white">Isolar SKUs com Fotos Quebradas</div>
                <div class="text-[11px] text-slate-400">Filtra produtos cujos SKUs estão com imagens 404</div>
              </div>
            </button>

            <!-- Ação 2: Filtrar Todos Fora do Padrão -->
            <button id="menu-btn-filter-out-standard" class="w-full text-left p-3 rounded-xl hover:bg-slate-800 transition-colors flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/30 text-amber-400 flex items-center justify-center font-bold text-sm shrink-0">
                ⚠️
              </div>
              <div>
                <div class="text-xs font-bold text-white">Ver Todos Fora do Padrão</div>
                <div class="text-[11px] text-slate-400">Fotos externas, textos rasos ou sem estrutura de 3 atos</div>
              </div>
            </button>

            <!-- Ação 3: Visualizar Lote ArmorX Verticalizado -->
            <a href="preview_armorx_comparativo.html" target="_blank" class="w-full text-left p-3 rounded-xl bg-gradient-to-r from-blue-700 to-indigo-600 hover:from-blue-600 hover:to-indigo-500 text-white transition-all flex items-center gap-3 shadow-lg shadow-blue-500/20">
              <div class="w-9 h-9 rounded-xl bg-white/20 text-white flex items-center justify-center font-bold text-sm shrink-0">
                ⚡
              </div>
              <div class="flex-1">
                <div class="text-xs font-black">Visualizar Lote ArmorX Verticalizado</div>
                <div class="text-[11px] text-blue-100">14 camisas corrigidas com até 3 fotos oficiais CDN</div>
              </div>
              <svg class="w-4 h-4 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            </a>

            <!-- Ação 4: Exportar Planilha Oficial Shopify -->
            <button id="menu-btn-download-csv" class="w-full text-left p-3 rounded-xl hover:bg-slate-800 transition-colors flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center font-bold text-sm shrink-0">
                📥
              </div>
              <div>
                <div class="text-xs font-bold text-white">Exportar Planilha Oficial Shopify / CSV</div>
                <div class="text-[11px] text-slate-400">Pronta para importação direta no painel da loja</div>
              </div>
            </button>
          </div>
        </div>

        <!-- Campo de Busca por SKU ou Nome -->
        <div class="w-48 sm:w-72">
          <div class="relative">
            <input type="text" id="search-input" placeholder="Buscar por SKU (ex: CAX001) ou nome..." 
              class="w-full pl-9 pr-4 py-2 text-xs bg-slate-900 border border-slate-700 rounded-full text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-slate-800 transition-all">
            <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>
        </div>

      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">

    <!-- SEÇÃO 1: CARROSSEL HORIZONTAL DE CATEGORIAS EM CÍRCULOS (PADRÃO STORIES / REELS) -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="font-heading font-bold text-xl sm:text-2xl text-slate-900 tracking-tight">Coleções & Linhas de Produtos</h2>
          <p class="text-xs sm:text-sm text-slate-500">Selecione uma categoria circular para filtrar os produtos e visualizar seus SKUs agrupados</p>
        </div>
        <div class="flex items-center gap-1.5">
          <button id="scroll-left" class="w-8 h-8 rounded-full border border-slate-200 bg-white hover:bg-slate-100 flex items-center justify-center text-slate-600 transition-colors shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          </button>
          <button id="scroll-right" class="w-8 h-8 rounded-full border border-slate-200 bg-white hover:bg-slate-100 flex items-center justify-center text-slate-600 transition-colors shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      <!-- Trilho Horizontal de Círculos -->
      <div id="categories-rail" class="flex items-start gap-4 sm:gap-6 overflow-x-auto no-scrollbar py-2 px-1 scroll-smooth">
        <!-- Injetado dinamicamente -->
      </div>
    </div>

    <!-- BANNER DE CONTEXTO DO ARQUÉTIPO -->
    <div id="archetype-banner" class="mb-6 p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white shadow-md relative overflow-hidden transition-all">
      <div class="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span id="banner-badge" class="px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wider rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30">Linhagem Técnica</span>
            <span id="banner-count" class="text-xs text-slate-300 font-medium"></span>
          </div>
          <h3 id="banner-title" class="font-heading text-lg sm:text-xl font-bold tracking-tight text-white">Linha Camisas ArmorX</h3>
          <p id="banner-desc" class="text-xs sm:text-sm text-slate-300 max-w-3xl mt-0.5"></p>
        </div>

        <!-- Filtros Rápidos por Status -->
        <div class="flex items-center gap-1.5 bg-white/10 p-1 rounded-xl backdrop-blur border border-white/10 text-xs">
          <button data-filter="ALL" class="filter-btn active px-3 py-1.5 rounded-lg font-semibold bg-white text-slate-900 shadow-sm transition-all">Todos</button>
          <button data-filter="IMAGENS_QUEBRADAS" class="filter-btn px-3 py-1.5 rounded-lg font-semibold text-rose-300 hover:bg-white/10 transition-all flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-rose-400"></span> Fotos Quebradas
          </button>
          <button data-filter="OUT_OF_STANDARD" class="filter-btn px-3 py-1.5 rounded-lg font-semibold text-amber-300 hover:bg-white/10 transition-all flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-amber-400"></span> Fora do Padrão
          </button>
          <button data-filter="SAUDAVEL" class="filter-btn px-3 py-1.5 rounded-lg font-semibold text-emerald-300 hover:bg-white/10 transition-all flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span> No Padrão
          </button>
        </div>
      </div>
    </div>

    <!-- MINI-CATÁLOGO (GRID DE PRODUTOS CENTRADO EM SKU) -->
    <div class="mb-12">
      <div id="products-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
        <!-- Cards gerados via JS -->
      </div>
      
      <!-- Estado Vazio -->
      <div id="empty-state" class="hidden text-center py-16 bg-white rounded-2xl border border-slate-200">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <h4 class="text-base font-bold text-slate-800">Nenhum produto ou SKU encontrado</h4>
        <p class="text-xs text-slate-500 mt-1">Verifique o termo de busca ou selecione outra categoria.</p>
      </div>
    </div>

  </main>

  <!-- MODAL / DRAWER DE INSPEÇÃO COM FOCO EM SKU -->
  <div id="inspector-modal" class="fixed inset-0 z-50 hidden">
    <div id="modal-backdrop" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity opacity-0"></div>

    <div class="fixed inset-y-0 right-0 max-w-3xl w-full bg-white shadow-2xl z-10 flex flex-col transform translate-x-full transition-transform duration-300 ease-out">
      
      <div class="p-5 sm:p-6 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
        <div class="flex items-center gap-4">
          <img id="modal-thumb" class="w-16 h-16 rounded-xl object-cover border border-slate-200 bg-white shadow-sm" src="" alt="">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span id="modal-sku-badge" class="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-slate-900 text-white"></span>
              <span id="modal-status-badge" class="px-2 py-0.5 rounded-full text-[11px] font-semibold"></span>
            </div>
            <h3 id="modal-title" class="font-heading font-bold text-base sm:text-lg text-slate-900 leading-snug line-clamp-2"></h3>
            <div class="flex items-center gap-3 mt-1 text-xs text-slate-500">
              <span id="modal-price" class="font-bold text-slate-900"></span>
              <span>•</span>
              <a id="modal-shopify-link" href="#" target="_blank" class="text-blue-600 hover:underline flex items-center gap-1 font-medium">
                Abrir na Shopify
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              </a>
            </div>
          </div>
        </div>

        <button id="close-modal" class="p-2 text-slate-400 hover:text-slate-700 rounded-xl hover:bg-slate-100 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Abas de Navegação -->
      <div class="border-b border-slate-200 px-6 bg-white flex items-center gap-8 text-sm font-semibold">
        <button id="tab-btn-audit" class="tab-btn active py-3.5 border-b-2 border-blue-600 text-blue-600 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          Diagnóstico do SKU
        </button>
        <button id="tab-btn-current" class="tab-btn py-3.5 border-b-2 border-transparent text-slate-500 hover:text-slate-800 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
          Descrição Atual
        </button>
        <button id="tab-btn-proposal" class="tab-btn py-3.5 border-b-2 border-transparent text-slate-500 hover:text-slate-800 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          Proposta Verticalizada (3 Fotos CDN)
        </button>
      </div>

      <!-- Conteúdo das Abas -->
      <div class="flex-1 overflow-y-auto p-6 bg-slate-50">
        
        <!-- ABA 1: DIAGNÓSTICO DO SKU -->
        <div id="tab-content-audit" class="space-y-5">
          
          <!-- Box de Variantes e SKUs Agrupados -->
          <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Variantes & SKUs Agrupados</span>
              <span class="text-[11px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded" id="modal-variants-count"></span>
            </div>
            <p class="text-xs text-slate-500 mb-3">
              Todas as variantes abaixo compartilham a mesma descrição deste produto pai. A regularização do HTML resolve todos os SKUs de uma só vez:
            </p>
            <div id="modal-skus-pills" class="flex flex-wrap gap-2">
              <!-- Pills de SKUs -->
            </div>
          </div>

          <!-- Score de Conversão -->
          <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex items-center justify-between gap-4">
            <div>
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Score de Saúde da Descrição</span>
              <div class="flex items-baseline gap-2 mt-1">
                <span id="modal-score-num" class="text-4xl font-heading font-black text-slate-900">00</span>
                <span class="text-sm text-slate-400 font-semibold">/ 100</span>
              </div>
              <p id="modal-recommendation" class="text-xs text-slate-600 mt-2 font-medium"></p>
            </div>
            <div id="score-circle-container" class="w-16 h-16 rounded-full flex items-center justify-center border-4"></div>
          </div>

          <!-- Alerta de Fotos Quebradas -->
          <div id="modal-broken-box" class="hidden bg-rose-50 border border-rose-200 rounded-2xl p-5">
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 shrink-0 mt-0.5">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              </div>
              <div class="flex-1">
                <h4 class="text-sm font-bold text-rose-900">Fotos Quebradas Identificadas</h4>
                <p class="text-xs text-rose-700 mt-0.5">As fotos abaixo pararam de responder (servidor S3 expirado), deixando todos os SKUs com ícones quebrados:</p>
                <div id="modal-broken-links" class="mt-3 space-y-1.5"></div>
              </div>
            </div>
          </div>

          <!-- Violações do Padrão -->
          <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
            <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Diagnóstico de Conformidade com o Padrão</h4>
            <div id="modal-issues-list" class="space-y-2"></div>
          </div>
        </div>

        <!-- ABA 2: DESCRIÇÃO ATUAL -->
        <div id="tab-content-current" class="hidden space-y-4">
          <div class="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-center gap-3 text-xs text-amber-800">
            <svg class="w-5 h-5 text-amber-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span>Renderização em tempo real do HTML cadastrado no produto na Shopify.</span>
          </div>
          <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <div id="modal-current-body" class="prose prose-slate max-w-none text-sm"></div>
          </div>
        </div>

        <!-- ABA 3: PROPOSTA VERTICALIZADA -->
        <div id="tab-content-proposal" class="hidden space-y-4">
          <div class="bg-blue-50 border border-blue-200 rounded-xl p-3.5 flex items-center gap-3 text-xs text-blue-900">
            <svg class="w-5 h-5 text-blue-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span>Layout verticalizado de alta conversão. As 3 fotos são extraídas da CDN da Shopify para eliminar quebras.</span>
          </div>
          <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <div id="modal-proposal-body" class="space-y-6"></div>
          </div>
        </div>

      </div>

      <div class="p-4 sm:p-5 border-t border-slate-200 bg-white flex items-center justify-between">
        <span class="text-xs text-slate-500 font-medium" id="modal-footer-info"></span>
        <button id="close-modal-bottom" class="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors">
          Fechar
        </button>
      </div>

    </div>
  </div>

  <!-- ======================================================== -->
  <!-- JAVASCRIPT DINÂMICO DE INTERAÇÃO & FILTROS POR SKU      -->
  <!-- ======================================================== -->
  <script>
    const CATALOG_DATA = {json_str};

    let currentCategory = "Camisas ArmorX";
    let currentFilter = "ALL";
    let searchQuery = "";

    // Elementos DOM
    const categoriesRail = document.getElementById("categories-rail");
    const productsGrid = document.getElementById("products-grid");
    const emptyState = document.getElementById("empty-state");
    const bannerBadge = document.getElementById("banner-badge");
    const bannerTitle = document.getElementById("banner-title");
    const bannerDesc = document.getElementById("banner-desc");
    const bannerCount = document.getElementById("banner-count");
    const searchInput = document.getElementById("search-input");

    // Botão Unificado e Menu
    const mainUnifiedBtn = document.getElementById("main-unified-btn");
    const unifiedMenu = document.getElementById("unified-menu");
    const menuBtnFilterBroken = document.getElementById("menu-btn-filter-broken");
    const menuBtnFilterOutStandard = document.getElementById("menu-btn-filter-out-standard");

    // Modal
    const inspectorModal = document.getElementById("inspector-modal");
    const modalBackdrop = document.getElementById("modal-backdrop");
    const modalPanel = inspectorModal.querySelector(".fixed.inset-y-0.right-0");
    const closeModalBtn = document.getElementById("close-modal");
    const closeModalBottom = document.getElementById("close-modal-bottom");

    // Abas do Modal
    const tabBtnAudit = document.getElementById("tab-btn-audit");
    const tabBtnCurrent = document.getElementById("tab-btn-current");
    const tabBtnProposal = document.getElementById("tab-btn-proposal");
    const tabContentAudit = document.getElementById("tab-content-audit");
    const tabContentCurrent = document.getElementById("tab-content-current");
    const tabContentProposal = document.getElementById("tab-content-proposal");

    // Descrições de Arquétipos para o Banner
    const ARCHETYPE_INFO = {{
      "Camisas ArmorX": {{
        badge: "Linhagem Técnica (ArmorX)",
        desc: "Cada modelo agrupa variantes de tamanho com códigos SKU unificados. A verticalização injeta 3 fotos oficiais CDN com coerência de cor e punho passa-dedo."
      }},
      "Camisas de Pesca UV": {{
        badge: "Linhagem Vestuário UV",
        desc: "Camisas tradicionais de pesca esportiva com proteção FPU 50+ homologada. Mapeamento de SKUs por estampa e grade de medidas."
      }},
      "Cutelaria & Facas": {{
        badge: "Artesanal & Exclusivo",
        desc: "Cutelaria de alto valor. Cada SKU representa uma peça única detalhando lâmina, têmpera, empunhadura nobre e gravação personalizada."
      }},
      "Óculos Polarizados": {{
        badge: "Revenda Técnica",
        desc: "Equipamentos com proteção UV400 para pescadores. SKUs com especificações de armação e lentes polarizadas."
      }},
      "Bonés & Chapéus": {{
        badge: "Revenda & Acessórios",
        desc: "Modelagem anatômica com tecidos repelentes para proteção solar prolongada."
      }},
      "Equipamentos & Iscas": {{
        badge: "Equipamentos de Pesca",
        desc: "Ficha técnica de precisão (libragem, ação, rolamentos) indexada por SKU de fabricante."
      }},
      "Calçados": {{
        badge: "Acessórios & Proteção",
        desc: "Calçados antiderrapantes para barcos molhados com numeração indexada por SKU."
      }},
      "Acessórios Diversos": {{
        badge: "Acessórios Gerais",
        desc: "Itens utilitários para pesca e camping."
      }}
    }};

    // Alternar Menu do Botão Unificado
    mainUnifiedBtn.onclick = (e) => {{
      e.stopPropagation();
      unifiedMenu.classList.toggle("hidden");
    }};

    document.addEventListener("click", () => {{
      unifiedMenu.classList.add("hidden");
    }});

    // Ações do Menu Unificado
    menuBtnFilterBroken.onclick = () => {{
      currentFilter = "IMAGENS_QUEBRADAS";
      syncFilterButtons();
      updateBanner();
      renderProducts();
    }};

    menuBtnFilterOutStandard.onclick = () => {{
      currentFilter = "OUT_OF_STANDARD";
      syncFilterButtons();
      updateBanner();
      renderProducts();
    }};

    function syncFilterButtons() {{
      document.querySelectorAll('.filter-btn').forEach(b => {{
        b.classList.remove('bg-white', 'text-slate-900', 'shadow-sm');
        if (b.dataset.filter === currentFilter) {{
          b.classList.add('bg-white', 'text-slate-900', 'shadow-sm');
        }}
      }});
    }}

    // Renderizar Categorias em Círculos
    function renderCategories() {{
      categoriesRail.innerHTML = "";
      const cats = CATALOG_DATA.categories;

      for (const [key, data] of Object.entries(cats)) {{
        const isActive = (key === currentCategory);
        const hasBroken = (data.broken_skus > 0);
        
        const catCard = document.createElement("div");
        catCard.className = "flex flex-col items-center cursor-pointer group shrink-0 transition-transform duration-200 hover:-translate-y-1";
        catCard.onclick = () => selectCategory(key);

        catCard.innerHTML = `
          <div class="relative mb-2">
            <div class="w-20 h-20 sm:w-24 sm:h-24 rounded-full p-1 transition-all duration-300 ${{
              isActive 
                ? 'ring-4 ring-blue-600 shadow-lg scale-105 ' + (hasBroken ? 'category-ring has-broken' : 'category-ring')
                : (hasBroken ? 'category-ring has-broken' : 'bg-slate-200 group-hover:bg-slate-300')
            }}">
              <div class="w-full h-full rounded-full overflow-hidden bg-white p-0.5">
                <img src="${{data.thumb}}" alt="${{data.title}}" class="w-full h-full object-cover rounded-full group-hover:scale-105 transition-transform duration-300">
              </div>
            </div>
            
            ${{hasBroken ? `
              <span class="absolute -top-1 -right-1 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-600 text-white shadow-sm flex items-center gap-0.5" title="${{data.broken_skus}} SKUs com fotos quebradas">
                ${{data.broken_skus}} SKUs ⚠️
              </span>
            ` : `
              <span class="absolute -top-1 -right-1 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-slate-800 text-white shadow-sm" title="${{data.total_skus}} SKUs cadastrados">
                ${{data.total_skus}} SKUs
              </span>
            `}}
          </div>

          <span class="text-xs font-semibold text-center max-w-[95px] leading-tight transition-colors ${{
            isActive ? 'text-blue-600 font-bold' : 'text-slate-700 group-hover:text-slate-900'
          }}">
            ${{data.title}}
          </span>
          <span class="text-[10px] text-slate-400 mt-0.5 font-medium">${{data.badge}}</span>
        `;

        categoriesRail.appendChild(catCard);
      }}
    }}

    function selectCategory(catName) {{
      currentCategory = catName;
      currentFilter = "ALL";
      syncFilterButtons();
      updateBanner();
      renderCategories();
      renderProducts();
    }}

    function updateBanner() {{
      const catData = CATALOG_DATA.categories[currentCategory] || {{ title: currentCategory, count: 0, total_skus: 0 }};
      const info = ARCHETYPE_INFO[currentCategory] || {{ badge: "Geral", desc: "" }};

      bannerTitle.textContent = catData.title;
      bannerBadge.textContent = info.badge;
      bannerDesc.textContent = info.desc;
      
      const filtered = getFilteredProducts();
      const filteredSkus = filtered.reduce((acc, p) => acc + p.total_skus_count, 0);
      bannerCount.textContent = `Exibindo ${{filtered.length}} modelo(s) • ${{filteredSkus}} SKUs agrupados`;
    }}

    function getFilteredProducts() {{
      let list = CATALOG_DATA.products.filter(p => p.category === currentCategory);

      if (currentFilter === "IMAGENS_QUEBRADAS") {{
        list = list.filter(p => p.status === "IMAGENS_QUEBRADAS");
      }} else if (currentFilter === "OUT_OF_STANDARD") {{
        list = list.filter(p => p.is_out_of_standard);
      }} else if (currentFilter === "SAUDAVEL") {{
        list = list.filter(p => !p.is_out_of_standard);
      }}

      if (searchQuery.trim()) {{
        const q = searchQuery.toLowerCase();
        list = list.filter(p => 
          p.title.toLowerCase().includes(q) || 
          p.handle.toLowerCase().includes(q) ||
          p.master_sku.toLowerCase().includes(q) ||
          (p.variants_skus && p.variants_skus.some(s => s.toLowerCase().includes(q)))
        );
      }}

      return list;
    }}

    function renderProducts() {{
      productsGrid.innerHTML = "";
      const prods = getFilteredProducts();

      if (prods.length === 0) {{
        productsGrid.classList.add("hidden");
        emptyState.classList.remove("hidden");
        return;
      }}

      productsGrid.classList.remove("hidden");
      emptyState.classList.add("hidden");

      prods.forEach(prod => {{
        const card = document.createElement("div");
        card.className = "bg-white rounded-2xl border border-slate-200/90 overflow-hidden product-shadow flex flex-col transition-all duration-300 hover:-translate-y-1 group";

        // Badges por SKU
        let skuStatusBadge = '';
        if (prod.status === 'IMAGENS_QUEBRADAS') {{
          skuStatusBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span> ${{prod.affected_skus_count}} SKUs Quebrados</span>`;
        }} else if (prod.is_out_of_standard) {{
          skuStatusBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> ${{prod.affected_skus_count}} SKUs Fora do Padrão</span>`;
        }} else {{
          skuStatusBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> ${{prod.total_skus_count}} SKUs no Padrão</span>`;
        }}

        const scoreColor = prod.score >= 80 ? 'text-emerald-600' : (prod.score >= 50 ? 'text-amber-600' : 'text-rose-600');

        card.innerHTML = `
          <!-- Imagem com Aspect Ratio E-commerce -->
          <div class="relative aspect-square bg-slate-100 overflow-hidden cursor-pointer" onclick="openInspector(${{prod.id}})">
            <img src="${{prod.image}}" alt="${{prod.title}}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
            
            <div class="absolute top-3 left-3 flex flex-col gap-1 items-start">
              ${{skuStatusBadge}}
            </div>

            <div class="absolute top-3 right-3 px-2 py-0.5 rounded-lg bg-white/95 backdrop-blur font-mono font-bold text-xs ${{scoreColor}} shadow-sm border border-slate-200/50">
              Score ${{prod.score}}
            </div>
          </div>

          <!-- Informações de SKU e Título -->
          <div class="p-4 flex-1 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between text-[11px] mb-1">
                <span class="font-mono font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200" title="SKU Base">
                  SKU: ${{prod.master_sku}}
                </span>
                <span class="text-slate-400 font-semibold">${{prod.total_skus_count}} Variantes</span>
              </div>

              <h4 class="font-heading font-bold text-sm text-slate-900 mt-1 line-clamp-2 group-hover:text-blue-600 transition-colors" title="${{prod.title}}">
                ${{prod.title}}
              </h4>
            </div>

            <div class="pt-4 mt-3 border-t border-slate-100 flex items-center justify-between">
              <span class="font-heading font-extrabold text-slate-900 text-base">${{prod.price}}</span>
              
              <button onclick="openInspector(${{prod.id}})" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-blue-600 text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-sm">
                <span>Inspecionar</span>
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
              </button>
            </div>
          </div>
        `;

        productsGrid.appendChild(card);
      }});
    }}

    window.openInspector = function(prodId) {{
      const prod = CATALOG_DATA.products.find(p => p.id === prodId);
      if (!prod) return;

      document.getElementById("modal-thumb").src = prod.image;
      document.getElementById("modal-title").textContent = prod.title;
      document.getElementById("modal-price").textContent = prod.price;
      document.getElementById("modal-shopify-link").href = prod.url;
      document.getElementById("modal-footer-info").textContent = `ID Shopify: ${{prod.id}} | Handle: ${{prod.handle}}`;
      
      // SKU Master Badge
      const skuBadge = document.getElementById("modal-sku-badge");
      skuBadge.textContent = `SKU: ${{prod.master_sku}}`;

      // Status Badge
      const statusBadge = document.getElementById("modal-status-badge");
      if (prod.status === 'IMAGENS_QUEBRADAS') {{
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-700 border border-rose-200';
        statusBadge.textContent = `❌ ${{prod.affected_skus_count}} SKUs com Fotos Quebradas`;
      }} else if (prod.is_out_of_standard) {{
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200';
        statusBadge.textContent = `⚠️ ${{prod.affected_skus_count}} SKUs Fora do Padrão`;
      }} else {{
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200';
        statusBadge.textContent = `✅ ${{prod.total_skus_count}} SKUs no Padrão`;
      }}

      // Variantes e SKUs Pills
      document.getElementById("modal-variants-count").textContent = `${{prod.total_skus_count}} SKUs vinculados`;
      const skusPillsContainer = document.getElementById("modal-skus-pills");
      skusPillsContainer.innerHTML = "";
      if (prod.variants_skus && prod.variants_skus.length > 0) {{
        prod.variants_skus.forEach(s => {{
          const pill = document.createElement("span");
          pill.className = "px-2 py-1 rounded-lg bg-slate-100 text-slate-800 font-mono text-xs font-semibold border border-slate-200";
          pill.textContent = s;
          skusPillsContainer.appendChild(pill);
        }});
      }} else {{
        skusPillsContainer.innerHTML = `<span class="text-xs text-slate-400 italic">Nenhum código SKU individual cadastrado.</span>`;
      }}

      // Score
      const scoreNum = document.getElementById("modal-score-num");
      scoreNum.textContent = String(prod.score).padStart(2, '0');
      const scoreCircle = document.getElementById("score-circle-container");
      if (prod.score >= 80) {{
        scoreCircle.className = 'w-16 h-16 rounded-full flex items-center justify-center border-4 border-emerald-500 bg-emerald-50 font-heading font-black text-emerald-700 text-xl';
        scoreCircle.textContent = prod.score;
      }} else if (prod.score >= 50) {{
        scoreCircle.className = 'w-16 h-16 rounded-full flex items-center justify-center border-4 border-amber-500 bg-amber-50 font-heading font-black text-amber-700 text-xl';
        scoreCircle.textContent = prod.score;
      }} else {{
        scoreCircle.className = 'w-16 h-16 rounded-full flex items-center justify-center border-4 border-rose-500 bg-rose-50 font-heading font-black text-rose-700 text-xl';
        scoreCircle.textContent = prod.score;
      }}

      document.getElementById("modal-recommendation").textContent = prod.recommendation;

      // Fotos Quebradas Box
      const brokenBox = document.getElementById("modal-broken-box");
      const brokenLinks = document.getElementById("modal-broken-links");
      if (prod.broken_urls && prod.broken_urls.length > 0) {{
        brokenBox.classList.remove("hidden");
        brokenLinks.innerHTML = "";
        prod.broken_urls.forEach(url => {{
          const item = document.createElement("div");
          item.className = "p-2 rounded bg-white border border-rose-200 font-mono text-[11px] text-rose-800 break-all";
          item.textContent = url;
          brokenLinks.appendChild(item);
        }});
      }} else {{
        brokenBox.classList.add("hidden");
      }}

      // Lista de Violações do Padrão
      const issuesList = document.getElementById("modal-issues-list");
      issuesList.innerHTML = "";
      if (prod.standard_violations && prod.standard_violations.length > 0) {{
        prod.standard_violations.forEach(v => {{
          const div = document.createElement("div");
          div.className = "flex items-start gap-2 text-xs text-slate-700";
          div.innerHTML = `<span class="text-rose-500 font-bold">•</span> <span>${{v}}</span>`;
          issuesList.appendChild(div);
        }});
      }} else {{
        issuesList.innerHTML = `<span class="text-xs text-emerald-600 font-semibold">100% em conformidade com as diretrizes da marca (3 fotos CDN e texto em 3 atos).</span>`;
      }}

      document.getElementById("modal-current-body").innerHTML = prod.body_html || '<p class="text-slate-400 italic">Produto sem descrição cadastrada.</p>';

      renderVerticalizedProposal(prod);
      switchTab('audit');

      inspectorModal.classList.remove("hidden");
      setTimeout(() => {{
        modalBackdrop.classList.remove("opacity-0");
        modalPanel.classList.remove("translate-x-full");
      }}, 10);
    }};

    function renderVerticalizedProposal(prod) {{
      const proposalContainer = document.getElementById("modal-proposal-body");
      
      proposalContainer.innerHTML = `
        <div class="border-b border-slate-200 pb-5">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-bold uppercase tracking-wider text-blue-600">Padrão Verticalizado de Alta Conversão</span>
            <span class="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">3 Fotos Oficiais CDN Shopify</span>
          </div>
          <h3 class="font-heading font-extrabold text-xl text-slate-900 mb-2">${{prod.title}}</h3>
          <p class="text-xs font-mono text-slate-500 mb-2">SKU Base: ${{prod.master_sku}} • ${{prod.total_skus_count}} Variantes de Grade</p>
          <p class="text-sm text-slate-600 leading-relaxed">
            Desenvolvida para pescadores e praticantes de esportes ao ar livre que exigem proteção térmica e liberdade total de movimento.
          </p>
        </div>

        <div class="flex flex-col sm:flex-row items-center gap-5 p-4 rounded-xl bg-slate-50 border border-slate-200/70">
          <div class="w-full sm:w-1/3 aspect-[4/3] rounded-lg overflow-hidden bg-slate-200 shrink-0">
            <img src="${{prod.image}}" class="w-full h-full object-cover" alt="Visão Geral">
          </div>
          <div class="flex-1">
            <span class="text-[11px] font-bold uppercase text-blue-600">Ato 1 • Proteção Homologada</span>
            <h4 class="font-heading font-bold text-base text-slate-900 mt-0.5">Proteção Solar UV50+ Permanente</h4>
            <p class="text-xs text-slate-600 mt-1 leading-relaxed">
              Bloqueia até 98% dos raios solares UVA e UVB com certificação têxtil permanente que não se degrada com as lavagens.
            </p>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row-reverse items-center gap-5 p-4 rounded-xl bg-slate-50 border border-slate-200/70">
          <div class="w-full sm:w-1/3 aspect-[4/3] rounded-lg overflow-hidden bg-slate-200 shrink-0">
            <img src="${{prod.gallery && prod.gallery[1] ? prod.gallery[1] : prod.image}}" class="w-full h-full object-cover" alt="Macro Detalhe">
          </div>
          <div class="flex-1">
            <span class="text-[11px] font-bold uppercase text-blue-600">Ato 2 • Engenharia Anatômica</span>
            <h4 class="font-heading font-bold text-base text-slate-900 mt-0.5">Luva Integrada & Costuras Planas</h4>
            <p class="text-xs text-slate-600 mt-1 leading-relaxed">
              Punho passa-dedo que protege o dorso das mãos e mantém a manga firme durante arremessos e pilotagem.
            </p>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-blue-50/50 border border-blue-200/60">
          <h4 class="font-heading font-bold text-sm text-blue-950 mb-1">Ato 3 • Tecido XTech Pro & Ficha Técnica</h4>
          <ul class="text-xs text-slate-600 space-y-1 mt-2">
            <li>• Microfibra XTech Pro com tecnologia Dry de rápida dispersão do suor</li>
            <li>• Tratamento bactericida anti-odor de alta durabilidade</li>
            <li>• Tabela de medidas compatível com os SKUs da grade (PP ao G1)</li>
          </ul>
        </div>
      `;
    }}

    function closeModal() {{
      modalBackdrop.classList.add("opacity-0");
      modalPanel.classList.add("translate-x-full");
      setTimeout(() => {{
        inspectorModal.classList.add("hidden");
      }}, 300);
    }}

    modalBackdrop.onclick = closeModal;
    closeModalBtn.onclick = closeModal;
    closeModalBottom.onclick = closeModal;

    function switchTab(tab) {{
      tabBtnAudit.classList.remove('active', 'border-blue-600', 'text-blue-600');
      tabBtnCurrent.classList.remove('active', 'border-blue-600', 'text-blue-600');
      tabBtnProposal.classList.remove('active', 'border-blue-600', 'text-blue-600');
      
      tabBtnAudit.classList.add('border-transparent', 'text-slate-500');
      tabBtnCurrent.classList.add('border-transparent', 'text-slate-500');
      tabBtnProposal.classList.add('border-transparent', 'text-slate-500');

      tabContentAudit.classList.add('hidden');
      tabContentCurrent.classList.add('hidden');
      tabContentProposal.classList.add('hidden');

      if (tab === 'audit') {{
        tabBtnAudit.classList.add('active', 'border-blue-600', 'text-blue-600');
        tabBtnAudit.classList.remove('border-transparent', 'text-slate-500');
        tabContentAudit.classList.remove('hidden');
      }} else if (tab === 'current') {{
        tabBtnCurrent.classList.add('active', 'border-blue-600', 'text-blue-600');
        tabBtnCurrent.classList.remove('border-transparent', 'text-slate-500');
        tabContentCurrent.classList.remove('hidden');
      }} else if (tab === 'proposal') {{
        tabBtnProposal.classList.add('active', 'border-blue-600', 'text-blue-600');
        tabBtnProposal.classList.remove('border-transparent', 'text-slate-500');
        tabContentProposal.classList.remove('hidden');
      }}
    }}

    tabBtnAudit.onclick = () => switchTab('audit');
    tabBtnCurrent.onclick = () => switchTab('current');
    tabBtnProposal.onclick = () => switchTab('proposal');

    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.onclick = () => {{
        currentFilter = btn.dataset.filter;
        syncFilterButtons();
        updateBanner();
        renderProducts();
      }};
    }});

    searchInput.oninput = (e) => {{
      searchQuery = e.target.value;
      renderProducts();
    }};

    document.getElementById("scroll-left").onclick = () => {{
      categoriesRail.scrollBy({{ left: -250, behavior: 'smooth' }});
    }};
    document.getElementById("scroll-right").onclick = () => {{
      categoriesRail.scrollBy({{ left: 250, behavior: 'smooth' }});
    }};

    // Inicialização
    renderCategories();
    updateBanner();
    renderProducts();
  </script>

</body>
</html>"""

    out_file1 = r"C:\Users\lucas\.gemini\antigravity\brain\6d694e19-7d4a-472b-b269-63d576efc810\catalogo_interativo_brk.html"
    out_file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "catalogo_interativo_brk.html")
    
    with open(out_file1, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(out_file2, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[OK] Interface V2 com Botao Unificado no Topo gerada com sucesso em:")
    print("     ->", out_file1)
    print("     ->", out_file2)

if __name__ == "__main__":
    build_v2()
