// ==UserScript==
// @name         BRK Assistente de Descrições Shopify (Conectado ao Banco Real v5.1 Coleções & Pente Fino)
// @namespace    https://1025-ten.vercel.app/
// @version      5.1.0
// @description  Automação 100% automática e assistida por Lote e por Coleções Shopify (incluindo Super Ofertas 🔥 BRK Fishing) conectada ao banco de dados oficial BRK (6.408 produtos nas 3 Lojas). Inclui Piloto Automático Modo B v5 e Pente Fino Visual de Variantes sem Foto (image_id=null), Fotos Duplicadas e Fotos de Baixa Resolução.
// @author       BRK Group & DeepMind Pair
// @match        https://admin.shopify.com/store/*/products*
// @match        https://1025-ten.vercel.app/*
// @match        http://localhost:*/*
// @match        http://127.0.0.1:*/*
// @connect      1025-ten.vercel.app
// @connect      www.brkfishing.com.br
// @connect      www.brkagro.com.br
// @connect      www.brkmotors.com.br
// @connect      localhost
// @connect      127.0.0.1
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_notification
// @grant        GM_setClipboard
// @run-at       document-idle
// ==/UserScript==

(function() {
  'use strict';

  // Configuração da API do Banco de Dados BRK (6.408 produtos auditados nas 3 lojas)
  const API_BASE = "https://1025-ten.vercel.app";
  const SCRIPT_VERSION = "5.1.0";

  const STORAGE_KEYS = {
    QUEUE: "BRK_AUTOSYNC_QUEUE",
    INDEX: "BRK_AUTOSYNC_INDEX",
    ACTIVE: "BRK_AUTOSYNC_ACTIVE",
    BACKUP: "BRK_AUTOSYNC_BACKUP",
    SETTINGS: "BRK_AUTOSYNC_SETTINGS",
    LAST_STORE: "BRK_LAST_STORE",
    COMPLIANT_IDS: "BRK_COMPLIANT_IDS"
  };

  const STORE_SLUG_MAP = {
    "brkfishing": "brk_fishing",
    "brkagro": "brk_agro",
    "brkmotors25": "brk_motors"
  };

  const STORE_NAMES = {
    "brk_fishing": "BRK Fishing",
    "brk_agro": "BRK Agro",
    "brk_motors": "BRK Motors"
  };

  // Paletas Visuais Oficiais de cada Loja
  const STORE_THEMES = {
    "brk_fishing": {
      name: "BRK Fishing",
      label: "Azul Náutico",
      primary: "#0284c7",
      primaryHover: "#0369a1",
      light: "#38bdf8",
      badgeBg: "#0c4a6e",
      badgeText: "#bae6fd",
      markers: ["#0284c7", "#00a8ff"]
    },
    "brk_agro": {
      name: "BRK Agro",
      label: "Verde Campo",
      primary: "#15803d",
      primaryHover: "#166534",
      light: "#4ade80",
      badgeBg: "#14532d",
      badgeText: "#bbf7d0",
      markers: ["#15803d", "#22c55e", "#16a34a"]
    },
    "brk_motors": {
      name: "BRK Motors",
      label: "Laranja Racing",
      primary: "#ea580c",
      primaryHover: "#c2410c",
      light: "#fb923c",
      badgeBg: "#7c2d12",
      badgeText: "#fed7aa",
      markers: ["#ea580c", "#f97316"]
    }
  };

  const DEFAULT_SETTINGS = {
    delaySeconds: 4,
    autoPilot: true,             // Modo Automático Total: injeta, clica em Salvar e avança sozinho para o próximo código fora das diretrizes
    autoSave: true,              // Clica automaticamente no botão "Salvar" da Shopify após injetar
    skipAlreadyModeB: true,      // Avança automaticamente quando o produto já está 100% conforme as Diretrizes Modo B v5
    upgradeOutdatedModeB: true,  // Atualiza produtos que têm Modo B com violação (Faca Marine c/ bainha, ArmorX c/ luva, Fusion/Hybrid s/ nota de capuz, P ao EXG)
    pauseOnMediaError: false,    // Se true, pausa o Auto-Save quando o produto tiver variante sem foto (image_id=null) ou foto duplicada para ajuste manual
    batchCategory: "super_ofertas",
    batchStatus: "FORA_DIRETRIZES",
    batchLimit: 100,
    customCollection: ""
  };

  function getSettings() {
    const raw = GM_getValue(STORAGE_KEYS.SETTINGS, null);
    if (!raw) return { ...DEFAULT_SETTINGS };
    try { return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) }; } catch(e) { return { ...DEFAULT_SETTINGS }; }
  }

  function saveSettings(partial) {
    const merged = { ...getSettings(), ...partial };
    GM_setValue(STORAGE_KEYS.SETTINGS, JSON.stringify(merged));
    return merged;
  }

  // Registro local de códigos/IDs já conformes (para nunca exibir nem enfileirar itens já dentro das diretrizes)
  function getCompliantIds() {
    const raw = GM_getValue(STORAGE_KEYS.COMPLIANT_IDS, "[]");
    try { return JSON.parse(raw) || []; } catch(e) { return []; }
  }

  function markProductAsCompliant(productId, sku) {
    const current = new Set(getCompliantIds().map(x => String(x).toUpperCase()));
    if (productId) current.add(String(productId).trim().toUpperCase());
    if (sku) current.add(String(sku).trim().toUpperCase());
    const arr = Array.from(current).slice(-1500);
    GM_setValue(STORAGE_KEYS.COMPLIANT_IDS, JSON.stringify(arr));
  }

  function isProductMarkedCompliant(productId, sku) {
    const set = new Set(getCompliantIds().map(x => String(x).toUpperCase()));
    if (productId && set.has(String(productId).trim().toUpperCase())) return true;
    if (sku && set.has(String(sku).trim().toUpperCase())) return true;
    return false;
  }

  function getQueue() {
    const raw = GM_getValue(STORAGE_KEYS.QUEUE, "[]");
    try { return JSON.parse(raw) || []; } catch(e) { return []; }
  }

  function setQueue(q) {
    GM_setValue(STORAGE_KEYS.QUEUE, JSON.stringify(q || []));
  }

  function getQueueIndex() {
    return parseInt(GM_getValue(STORAGE_KEYS.INDEX, 0), 10) || 0;
  }

  function setQueueIndex(idx) {
    GM_setValue(STORAGE_KEYS.INDEX, idx);
  }

  function isAutomationActive() {
    return GM_getValue(STORAGE_KEYS.ACTIVE, false) === true;
  }

  function setAutomationActive(bool) {
    GM_setValue(STORAGE_KEYS.ACTIVE, bool === true);
  }

  function appendBackup(productId, handle, originalHtml) {
    const raw = GM_getValue(STORAGE_KEYS.BACKUP, "[]");
    let arr = [];
    try { arr = JSON.parse(raw) || []; } catch(e) { arr = []; }
    arr.unshift({
      product_id: String(productId || ""),
      handle: handle || "",
      saved_at: new Date().toISOString(),
      body_html: originalHtml || ""
    });
    if (arr.length > 50) arr = arr.slice(0, 50);
    GM_setValue(STORAGE_KEYS.BACKUP, JSON.stringify(arr));
  }

  function getLastBackupForProduct(productId) {
    const raw = GM_getValue(STORAGE_KEYS.BACKUP, "[]");
    try {
      const arr = JSON.parse(raw) || [];
      return arr.find(b => String(b.product_id) === String(productId)) || null;
    } catch(e) {
      return null;
    }
  }

  // =========================================================================
  // COMUNICAÇÃO HTTP COM A API REAL DO BANCO DE DADOS BRK
  // =========================================================================
  function fetchFromBRKDatabase(endpoint) {
    return new Promise((resolve, reject) => {
      const url = `${API_BASE}${endpoint}`;
      console.log(`[BRK-DB v${SCRIPT_VERSION}] Requisitando: ${url}`);
      GM_xmlhttpRequest({
        method: "GET",
        url: url,
        headers: {
          "Accept": "application/json"
        },
        onload: function(response) {
          if (response.status >= 200 && response.status < 300) {
            try {
              const data = JSON.parse(response.responseText);
              resolve(data);
            } catch(e) {
              reject(new Error("Resposta da API BRK não é um JSON válido."));
            }
          } else {
            try {
              const errData = JSON.parse(response.responseText);
              reject(new Error(errData.error || `Erro HTTP ${response.status}`));
            } catch(e) {
              reject(new Error(`Erro HTTP ${response.status}: ${response.statusText}`));
            }
          }
        },
        onerror: function(err) {
          console.error(`[BRK-DB v${SCRIPT_VERSION}] Falha de rede:`, err);
          reject(new Error("Falha na conexão com a API da Vercel. Verifique a internet."));
        }
      });
    });
  }

  // =========================================================================
  // 1. LÓGICA NO PORTAL LOCAL OU VERCEL (1025-ten.vercel.app)
  // =========================================================================
  if (location.hostname === "1025-ten.vercel.app" || location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Conectado ao Portal de Descrições BRK.`);
    window.__BRK_TAMPERMONKEY_INSTALLED = true;
    document.documentElement.setAttribute("data-tampermonkey-active", "true");

    const badge = document.createElement("div");
    badge.id = "brk-tm-portal-badge";
    badge.style.cssText = "position:fixed;bottom:16px;left:16px;z-index:99999;background:#0f172a;border:1px solid #0284c7;color:#38bdf8;padding:8px 14px;border-radius:9999px;font-size:12px;font-weight:800;display:flex;align-items:center;gap:8px;box-shadow:0 4px 16px rgba(0,0,0,0.4);cursor:pointer;font-family:sans-serif;transition:all 0.2s;";

    function updatePortalBadge() {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      badge.innerHTML = q.length > 0
        ? `<span>🤖 Tampermonkey v${SCRIPT_VERSION} | Fila Não-Conformes: ${idx + 1}/${q.length} (${active ? 'Piloto Automático Ativo' : 'Pausada'})</span>`
        : `<span>🟢 Tampermonkey v${SCRIPT_VERSION} Conectado (Filtro Estrito de Diretrizes + Piloto Automático)</span>`;
    }
    updatePortalBadge();

    badge.onclick = () => {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      alert(`[Assistente BRK v${SCRIPT_VERSION} — Piloto Automático & Filtro de Diretrizes]\n\nFila Atual (Apenas Fora das Diretrizes): ${q.length} produtos\nÍndice Atual: ${q.length ? (idx + 1) : 0} de ${q.length}\nPiloto Automático Ativo: ${active ? "SIM" : "NÃO"}\n\nDiretrizes Modo B v5 Ativas:\n• Exibe e enfileira APENAS códigos (SKUs) fora das diretrizes\n• Faca Marine MFK75T sem bainha (revestimento Teflon + olhal para fiel)\n• Tabelas de Medidas com orientação explícita para Camisas com Capuz/Bandana Embutida (FusionX/Hybrid) e Luva Integrada (ArmorX)`);
    };
    document.body.appendChild(badge);

    // Ponte Bidirecional: Receber Fila enviada pelo Portal (filtrando itens já conformes)
    window.addEventListener("message", (event) => {
      const data = event.data;
      if (!data || data.type !== "BRK_LOAD_QUEUE" || !data.payload) return;
      const { items, storeKey, storeSlug, autoStart } = data.payload;
      if (!Array.isArray(items) || items.length === 0) return;

      const filteredItems = items.filter(it => !it.is_mode_b_compliant && !isProductMarkedCompliant(it.id, it.master_sku || it.sku));
      const finalItems = filteredItems.length > 0 ? filteredItems : items;

      setQueue(finalItems);
      setQueueIndex(0);
      setAutomationActive(autoStart !== false);
      if (storeKey) GM_setValue(STORAGE_KEYS.LAST_STORE, storeKey);
      updatePortalBadge();

      const slug = storeSlug || (storeKey === "brk_agro" ? "brkagro" : storeKey === "brk_motors" ? "brkmotors25" : "brkfishing");
      const firstId = finalItems[0].id;
      if (firstId && autoStart !== false) {
        const targetUrl = `https://admin.shopify.com/store/${slug}/products/${firstId}`;
        window.open(targetUrl, "_blank");
      }
    });

    return;
  }

  // =========================================================================
  // 2. LÓGICA NO SHOPIFY ADMIN (admin.shopify.com/store/*/products*)
  // =========================================================================
  if (location.hostname === "admin.shopify.com") {
    let currentShopifySlug = "";
    let currentStoreKey = "brk_fishing";
    let currentStoreName = "BRK Fishing";
    let currentTheme = STORE_THEMES["brk_fishing"];
    let currentProductId = null;
    let lastObservedPath = "";
    let activeLoadedProduct = null;
    let cachedNonCompliantCodes = [];
    let countdownTimer = null;
    let saveCompletionTimer = null;
    let hasTriggeredSaveForCurrentProduct = false;

    function parseCurrentRoute() {
      const urlPath = location.pathname;
      const storeMatch = urlPath.match(/\/store\/([^\/]+)/);
      currentShopifySlug = storeMatch ? storeMatch[1].toLowerCase() : "";
      currentStoreKey = STORE_SLUG_MAP[currentShopifySlug] || "brk_fishing";
      currentStoreName = STORE_NAMES[currentStoreKey] || "BRK Fishing";
      currentTheme = STORE_THEMES[currentStoreKey] || STORE_THEMES["brk_fishing"];

      const productMatch = urlPath.match(/\/products\/(\d+)/);
      currentProductId = productMatch ? productMatch[1] : null;
    }

    parseCurrentRoute();
    console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Shopify Admin | Loja: ${currentStoreName} (${currentShopifySlug}) | Produto ID: ${currentProductId || 'Listagem'}`);

    // Injetar Estilos Visuais do HUD, Mapa de Códigos Não-Conformes, Modal de Preview e Pulso do Botão Salvar
    const styleEl = document.createElement("style");
    styleEl.id = "brk-tm-styles";
    styleEl.textContent = `
      @keyframes brkSaveGlow {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.85); transform: scale(1); }
        50% { box-shadow: 0 0 0 12px rgba(34, 197, 94, 0); transform: scale(1.04); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); transform: scale(1); }
      }
      .brk-pulse-save-button {
        animation: brkSaveGlow 1.2s infinite !important;
        background-color: #16a34a !important;
        border-color: #15803d !important;
        color: #ffffff !important;
        font-weight: 800 !important;
      }
      #brk-tm-hud {
        position: fixed;
        bottom: 18px;
        right: 18px;
        z-index: 999998;
        background: #090d16;
        color: #f1f5f9;
        border: 2px solid #0284c7;
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.75);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        min-width: 410px;
        max-width: 530px;
        backdrop-filter: blur(12px);
        transition: border-color 0.25s ease;
      }
      .brk-badge-status {
        font-size: 10px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 9999px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }
      .brk-badge-empty { background: #991b1b; color: #fee2e2; }
      .brk-badge-broken { background: #b45309; color: #fef3c7; }
      .brk-badge-outdated { background: #92400e; color: #fde68a; }
      .brk-badge-legacy { background: #3730a3; color: #e0e7ff; }
      .brk-badge-healthy { background: #166534; color: #dcfce7; }
      .brk-badge-meta {
        font-size: 10px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        background: #1e293b;
        color: #cbd5e1;
        border: 1px solid #334155;
      }
      .brk-hud-btn {
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 6px 11px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        transition: all 0.18s;
      }
      .brk-hud-btn:hover {
        background: #334155;
        color: #ffffff;
      }
      .brk-hud-btn-primary {
        background: #0284c7;
        border-color: #0369a1;
        color: #ffffff;
      }
      .brk-hud-btn-primary:hover {
        filter: brightness(1.1);
      }
      .brk-hud-btn-success {
        background: #16a34a;
        border-color: #15803d;
        color: #ffffff;
      }
      .brk-hud-btn-success:hover {
        background: #15803d;
      }
      .brk-hud-btn-danger {
        background: #7f1d1d;
        border-color: #991b1b;
        color: #fecaca;
      }
      .brk-hud-btn-danger:hover {
        background: #991b1b;
      }
      .brk-hud-select {
        background: #0f172a;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 11px;
        font-weight: 600;
        outline: none;
        width: 100%;
      }
      .brk-hud-toggle {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        color: #cbd5e1;
        cursor: pointer;
        user-select: none;
      }
      .brk-hud-toggle input {
        accent-color: #0284c7;
        cursor: pointer;
      }
      .brk-codes-scroll {
        max-height: 155px;
        overflow-y: auto;
        background: #060911;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 6px;
        margin-top: 6px;
      }
      .brk-code-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        padding: 4px 6px;
        border-bottom: 1px solid #0f172a;
        font-size: 11px;
        border-radius: 5px;
        cursor: pointer;
        transition: background 0.15s;
      }
      .brk-code-row:hover {
        background: #1e293b;
      }
      #brk-tm-preview-modal {
        position: fixed;
        inset: 0;
        z-index: 999999;
        background: rgba(9, 13, 22, 0.82);
        backdrop-filter: blur(6px);
        display: none;
        align-items: center;
        justify-content: center;
        padding: 24px;
      }
      #brk-tm-preview-card {
        background: #ffffff;
        color: #1e293b;
        border-radius: 18px;
        max-width: 980px;
        width: 100%;
        max-height: 88vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.65);
        overflow: hidden;
      }
    `;
    document.head.appendChild(styleEl);

    const hud = document.createElement("div");
    hud.id = "brk-tm-hud";
    document.body.appendChild(hud);

    const previewModal = document.createElement("div");
    previewModal.id = "brk-tm-preview-modal";
    document.body.appendChild(previewModal);

    function openPreviewModal(prod) {
      if (!prod || !prod.mode_b_html) {
        alert("Descrição Modo B ainda não carregada para este produto.");
        return;
      }
      previewModal.style.display = "flex";
      previewModal.innerHTML = `
        <div id="brk-tm-preview-card">
          <div style="background:#090d16;color:#f8fafc;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid ${currentTheme.primary};">
            <div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};font-size:10px;font-weight:800;padding:2px 8px;border-radius:9999px;">${currentStoreName} • ${currentTheme.label}</span>
                <strong style="font-size:14px;color:#ffffff;">${prod.master_sku || 'SKU'} — ${prod.title}</strong>
              </div>
              <div style="font-size:11px;color:#94a3b8;margin-top:3px;">
                Molde: <strong>${prod.layout_type || prod.archetype_name}</strong> | Público: <strong>${prod.audience_badge || 'Adulto'}</strong> | Prazo: <strong>${prod.delivery_time || 'Pronta entrega'}</strong> | ${(prod.mode_b_html.length).toLocaleString('pt-BR')} caracteres
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <button id="brk-modal-inject-btn" class="brk-hud-btn brk-hud-btn-primary" style="background:${currentTheme.primary};border-color:${currentTheme.primaryHover};">
                ⚡ Injetar no Editor Agora
              </button>
              <button id="brk-modal-close-btn" class="brk-hud-btn">
                ✕ Fechar
              </button>
            </div>
          </div>
          <div style="padding:24px;overflow-y:auto;max-height:calc(88vh - 75px);background:#ffffff;">
            ${prod.mode_b_html}
          </div>
        </div>
      `;

      const closeBtn = document.getElementById("brk-modal-close-btn");
      if (closeBtn) closeBtn.onclick = () => { previewModal.style.display = "none"; };
      previewModal.onclick = (e) => {
        if (e.target === previewModal) previewModal.style.display = "none";
      };
      const injectNowBtn = document.getElementById("brk-modal-inject-btn");
      if (injectNowBtn) {
        injectNowBtn.onclick = () => {
          previewModal.style.display = "none";
          injectModoBIntoEditor(prod.mode_b_html);
        };
      }
    }

    // =========================================================================
    // EXTRAÇÃO DE METADADOS DO DOM DO SHOPIFY ADMIN (HANDLE, SKU E CONTEÚDO ATUAL)
    // =========================================================================
    function extractPageHints() {
      let handle = "";
      let sku = "";
      try {
        const links = Array.from(document.querySelectorAll("a[href*='/products/']"));
        for (const a of links) {
          const href = a.getAttribute("href") || "";
          if (!href.includes("admin.shopify.com")) {
            const m = href.match(/\/products\/([^/?#]+)/);
            if (m && m[1] && !/^\d+$/.test(m[1])) {
              handle = m[1].trim().toLowerCase();
              break;
            }
          }
        }
        if (!handle) {
          const bodyText = document.body.innerText || "";
          const seoMatch = bodyText.match(/\/products\/([a-z0-9][a-z0-9-_]{3,120})/i);
          if (seoMatch && seoMatch[1] && !/^\d+$/.test(seoMatch[1])) {
            handle = seoMatch[1].trim().toLowerCase();
          }
        }
        const skuInput = document.querySelector("input[name='sku'], input[id*='sku'], input[id*='SKU']");
        if (skuInput && skuInput.value) {
          sku = skuInput.value.trim().split("-")[0].toUpperCase();
        }
      } catch(e) {}
      return { handle, sku };
    }

    function getCurrentEditorHtml() {
      // 1. Textarea do modo HTML (<>)
      const textarea = document.querySelector("textarea[name*='description']") ||
                       document.querySelector("textarea[id*='description']") ||
                       document.querySelector(".Polaris-Textarea__Input");
      if (textarea && typeof textarea.value === "string" && textarea.value.trim()) {
        return textarea.value;
      }
      // 2. TinyMCE iframe do Shopify Admin
      const iframes = Array.from(document.querySelectorAll("iframe"));
      for (const ifr of iframes) {
        try {
          if (ifr.contentDocument && ifr.contentDocument.body && ifr.contentDocument.body.innerHTML) {
            const inner = ifr.contentDocument.body.innerHTML;
            if (inner && inner.length > 5) return inner;
          }
        } catch(e) {}
      }
      // 3. Contenteditable
      const editable = document.querySelector("[contenteditable='true']");
      if (editable && editable.innerHTML) {
        return editable.innerHTML;
      }
      return "";
    }

    // Espera resiliente até o editor da Shopify montar no DOM (essencial para o Piloto Automático)
    function waitForEditorReady(maxWaitMs = 8000) {
      return new Promise((resolve) => {
        const start = Date.now();
        const check = () => {
          const hasTa = !!findDescriptionTextarea();
          const hasTiny = !!findTinyMceBody();
          const hasHtmlBtn = !!findShowHtmlButton();
          const hasEditable = !!document.querySelector("[contenteditable='true']");
          if (hasTa || hasTiny || hasHtmlBtn || hasEditable || (Date.now() - start >= maxWaitMs)) {
            resolve(true);
          } else {
            setTimeout(check, 250);
          }
        };
        check();
      });
    }

    // Diagnóstico Inteligente Fase 8 (Diretrizes Modo B v5) do HTML atual no editor da Shopify
    function inspectEditorHealth(prod) {
      const currentHtml = getCurrentEditorHtml();
      const titleAndSku = `${prod?.title || ""} ${prod?.master_sku || ""}`.toLowerCase();

      if (!currentHtml || currentHtml.trim().length < 30) {
        return { state: "EMPTY", badge: "🔴 SEM DESCRIÇÃO NO EDITOR", reason: "Editor da Shopify está vazio." };
      }
      const hasModeB = currentHtml.includes("<!-- BRK-MODO-B") || currentHtml.includes("brk-cap-description") || currentHtml.includes("brk-size-guide") || currentHtml.includes("brk-desc-wrapper");
      if (!hasModeB) {
        if (currentHtml.includes("use-brk-images-s3")) {
          return { state: "LEGACY_BROKEN", badge: "🔴 S3 QUEBRADO NO EDITOR", reason: "Descrição antiga com imagens AWS S3 (Erro 404)." };
        }
        return { state: "LEGACY", badge: "🟡 FORA DO PADRÃO MODO B", reason: "Descrição legada fora das diretrizes Modo B (sem 3 Atos / D2C)." };
      }

      // Já tem estrutura Modo B, mas verificamos rigorosamente cada diretriz Modo B v5:
      const reasons = [];
      if (currentHtml.includes("use-brk-images-s3")) {
        reasons.push("Links AWS S3 404 (13-Tags/CAIXA)");
      }
      if (currentHtml.includes("eQxQuY7.jpg") && prod && prod.mode_b_html && !prod.mode_b_html.includes("eQxQuY7.jpg")) {
        reasons.push("Foto genérica repetida de boné");
      }
      if (currentHtml.includes("Tabela de Medidas Adulto (P ao EXG)")) {
        reasons.push("Tabela Adulto antiga (P ao EXG em vez de PP ao G2)");
      }
      if (currentHtml.includes("Tabela de Medidas de Luvas") && /camisa|camiseta|armorx|cax|hyb|fusion/i.test(titleAndSku)) {
        reasons.push("Camisa ArmorX/UV com Tabela de Luvas (corrigir para Tabela de Camisa PP ao G2)");
      }
      if (/(fillet|mfk75t|79081379076)/i.test(titleAndSku) && /bainha/i.test(currentHtml) && !/bainha/i.test(prod?.title || "")) {
        reasons.push("Faca Marine MFK75T com menção indevida a bainha (modelo não acompanha bainha)");
      }
      if (/(fusion|hyb)/i.test(titleAndSku) && /\b(zíper|ziper)\b/i.test(currentHtml)) {
        reasons.push("Modelo Fusion/Hybrid com menção indevida a zíper");
      }
      if (/(fusion|hyb)/i.test(titleAndSku) && !currentHtml.toLowerCase().includes("sem contar")) {
        reasons.push("Tabela de Medidas sem orientação de Capuz/Bandana Embutida (medir do ombro à barra sem contar o capuz)");
      }
      if (currentHtml.includes("Bandana Tubular Seamless")) {
        reasons.push("Nomenclatura antiga de Bandana (Seamless)");
      }
      // Contingência Anti-Duplicação da 1ª Foto na Descrição
      const editorImgMatches = Array.from(currentHtml.matchAll(/<img[^>]+src=["']([^"']+)["']/gi))
        .map(m => m[1].split("?")[0].toLowerCase())
        .filter(u => !u.endsWith(".svg"));
      if (editorImgMatches.length > new Set(editorImgMatches).size) {
        reasons.push("Foto repetida nos Atos/Cards da descrição");
      } else if (prod && Array.isArray(prod.cdn_images) && prod.cdn_images.length > 0 && editorImgMatches.length >= 2) {
        const officialRoots = new Set(prod.cdn_images.map(u => String(u).split("?")[0].toLowerCase()));
        const hasPurgedDup = editorImgMatches.some(u => u.includes("productonchannel") && !officialRoots.has(u));
        if (hasPurgedDup) {
          reasons.push("1ª foto duplicada pela Shopify no Ato 2");
        }
      }
      // Verificar se a cor da loja está correta no HTML do editor
      const themeMarkers = currentTheme.markers || ["#0284c7"];
      const hasStoreColor = themeMarkers.some(color => currentHtml.toLowerCase().includes(color.toLowerCase()));
      if (!hasStoreColor && (currentHtml.includes("#0284c7") || currentHtml.includes("#15803d") || currentHtml.includes("#ea580c"))) {
        reasons.push(`Cor de outra loja (esperado ${currentTheme.label})`);
      }

      if (reasons.length > 0) {
        return {
          state: "OUTDATED_MODE_B",
          badge: "⚠️ FORA DAS DIRETRIZES v5",
          reason: `Correção obrigatória: ${reasons.join(" | ")}.`
        };
      }

      // Produto está 100% dentro das diretrizes no editor! Marcar como conforme para nunca mais listar como pendente.
      if (currentProductId) {
        markProductAsCompliant(currentProductId, prod?.master_sku);
      }

      return {
        state: "UP_TO_DATE",
        badge: "✅ 100% CONFORME DIRETRIZES v5",
        reason: `Descrição oficial sincronizada e dentro de todas as regras (${currentTheme.label}).`
      };
    }

    // =========================================================================
    // INJEÇÃO COMPATÍVEL COM REACT & TINYMCE + SALVAMENTO AUTOMÁTICO REFORÇADO
    // =========================================================================
    function setReactInputValue(element, value) {
      if (!element) return;
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
      if (nativeSetter) {
        nativeSetter.call(element, value);
      } else {
        element.value = value;
      }
      element.dispatchEvent(new Event("input", { bubbles: true }));
      element.dispatchEvent(new Event("change", { bubbles: true }));
      element.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));
      element.dispatchEvent(new Event("blur", { bubbles: true }));
    }

    function findSaveButton() {
      const buttons = Array.from(document.querySelectorAll("button"));
      return buttons.find(b => {
        if (b.disabled || b.getAttribute("aria-disabled") === "true") return false;
        const text = (b.innerText || b.textContent || "").trim().toLowerCase();
        const aria = (b.getAttribute("aria-label") || "").trim().toLowerCase();
        return text === "salvar" || text === "save" || aria === "salvar" || aria === "save";
      }) || null;
    }

    // Aguarda a Shopify concluir a requisição de salvamento antes de avançar para o próximo produto
    function waitForShopifySaveComplete(onComplete) {
      if (saveCompletionTimer) clearInterval(saveCompletionTimer);
      let checks = 0;
      saveCompletionTimer = setInterval(() => {
        checks++;
        const activeSaveBtn = findSaveButton();
        const bodyText = document.body.innerText || "";
        const hasToast = /produto salvo|product saved|alterações salvas/i.test(bodyText);
        // Se o botão Salvar desabilitou/sumiu após o clique ou apareceu o toast da Shopify (ou após 2.4s)
        if ((!activeSaveBtn && checks >= 2) || hasToast || checks >= 8) {
          clearInterval(saveCompletionTimer);
          saveCompletionTimer = null;
          if (onComplete) onComplete();
        }
      }, 350);
    }

    function highlightSaveButton(onSaveCallback) {
      const settings = getSettings();
      const ma = activeLoadedProduct?.media_audit || {};
      const shouldPauseForMedia = settings.pauseOnMediaError && (ma.has_unlinked_variants || ma.has_duplicate_images);
      let attempts = 0;
      let callbackFired = false;

      const fireOnce = () => {
        if (callbackFired) return;
        callbackFired = true;
        if (currentProductId) {
          markProductAsCompliant(currentProductId, activeLoadedProduct?.master_sku);
        }
        if (onSaveCallback) onSaveCallback();
      };

      const tryHighlight = () => {
        const saveBtn = findSaveButton();
        if (saveBtn) {
          saveBtn.classList.add("brk-pulse-save-button");
          saveBtn.scrollIntoView({ behavior: "smooth", block: "nearest" });

          const handler = () => {
            saveBtn.classList.remove("brk-pulse-save-button");
            saveBtn.removeEventListener("click", handler);
            waitForShopifySaveComplete(fireOnce);
          };
          saveBtn.addEventListener("click", handler);

          if (shouldPauseForMedia) {
            renderHudProductMode(
              activeLoadedProduct,
              "⏸️ Modo B Injetado • Pausado para Ajuste de Foto/Cor",
              "Vincule a foto da variante (ou remova a duplicata) na tabela abaixo e clique em 'Salvar' para avançar."
            );
            return true;
          }

          // Modo Automático (autoPilot ou autoSave): clica automaticamente em Salvar e aguarda confirmação
          if ((settings.autoPilot || settings.autoSave) && !hasTriggeredSaveForCurrentProduct) {
            hasTriggeredSaveForCurrentProduct = true;
            setTimeout(() => {
              const liveSaveBtn = findSaveButton() || saveBtn;
              if (liveSaveBtn && !liveSaveBtn.disabled) {
                console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] 🤖 Piloto Automático: clicando em Salvar automaticamente!`);
                liveSaveBtn.click();
                waitForShopifySaveComplete(fireOnce);
              } else {
                // Se o botão já foi salvo/desabilitado
                waitForShopifySaveComplete(fireOnce);
              }
            }, 700);
          }
          return true;
        }
        attempts++;
        if (attempts < 14) {
          setTimeout(tryHighlight, 300);
        } else if (settings.autoPilot && isAutomationActive() && !shouldPauseForMedia) {
          // Se o botão Salvar não habilitou porque o HTML já era idêntico no editor, marca como conforme e avança!
          console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] 🤖 Botão Salvar permaneceu inativo (HTML já idêntico). Avançando...`);
          fireOnce();
        }
        return false;
      };

      return tryHighlight();
    }

    function findShowHtmlButton() {
      const allButtons = Array.from(document.querySelectorAll("button"));
      return allButtons.find(b => {
        const aria = (b.getAttribute("aria-label") || "").toLowerCase();
        const title = (b.getAttribute("title") || "").toLowerCase();
        const text = (b.innerText || "").trim();
        return (
          aria.includes("mostrar html") ||
          aria.includes("exibir html") ||
          aria.includes("show html") ||
          aria.includes("html") ||
          aria.includes("código") ||
          title.includes("mostrar html") ||
          title.includes("show html") ||
          title.includes("html") ||
          text === "<>"
        );
      }) || null;
    }

    function findDescriptionTextarea() {
      return (
        document.querySelector("textarea[name*='description']") ||
        document.querySelector("textarea[id*='description']") ||
        document.querySelector(".Polaris-Textarea__Input") ||
        Array.from(document.querySelectorAll("textarea")).find(ta => ta.offsetParent !== null && (ta.offsetHeight > 80 || ta.rows > 4)) ||
        null
      );
    }

    function findTinyMceBody() {
      const iframes = Array.from(document.querySelectorAll("iframe"));
      for (const ifr of iframes) {
        try {
          const doc = ifr.contentDocument;
          if (doc && doc.body && (doc.body.getAttribute("contenteditable") === "true" || ifr.id.includes("tiny") || ifr.className.includes("tox"))) {
            return { iframe: ifr, body: doc.body };
          }
        } catch(e) {}
      }
      return null;
    }

    function injectModoBIntoEditor(htmlContent) {
      if (!htmlContent) {
        alert("Conteúdo Modo B vazio no banco de dados.");
        return false;
      }

      hasTriggeredSaveForCurrentProduct = false;
      const htmlBtn = findShowHtmlButton();
      let textarea = findDescriptionTextarea();

      // Se o textarea do modo HTML ainda não está visível e achamos o botão (<>), clicamos nele para abrir o modo HTML puro
      if (htmlBtn && (!textarea || textarea.offsetParent === null)) {
        console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Alternando editor para Modo Código HTML (<>)...`);
        htmlBtn.click();
      }

      let pollCount = 0;
      const tryInject = () => {
        pollCount++;
        textarea = findDescriptionTextarea();

        if (textarea && textarea.offsetParent !== null) {
          appendBackup(currentProductId, location.pathname, textarea.value);
          setReactInputValue(textarea, htmlContent);
          console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] HTML Modo B v5 injetado com sucesso no Textarea HTML!`);

          setTimeout(() => {
            highlightSaveButton(() => {
              console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Produto salvo com sucesso!`);
              handleAfterSave();
            });
          }, 250);

          const isAuto = getSettings().autoPilot || getSettings().autoSave;
          renderHudProductMode(
            activeLoadedProduct,
            "✨ Modo B v5 Injetado com Sucesso!",
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres (${currentTheme.label}). ${isAuto ? '🤖 Salvando e avançando automaticamente...' : "Clique em 'Salvar' (verde pulsando)."}`
          );
          return;
        }

        if (pollCount < 6 && htmlBtn) {
          setTimeout(tryInject, 220);
          return;
        }

        // Fallback 2: Injetar direto no TinyMCE iframe (Editor Visual do Shopify Admin)
        const tiny = findTinyMceBody();
        if (tiny && tiny.body) {
          appendBackup(currentProductId, location.pathname, tiny.body.innerHTML);
          tiny.body.focus();
          tiny.body.innerHTML = htmlContent;
          tiny.body.dispatchEvent(new Event("input", { bubbles: true }));
          tiny.body.dispatchEvent(new Event("change", { bubbles: true }));
          tiny.body.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));
          tiny.body.dispatchEvent(new Event("blur", { bubbles: true }));
          console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] HTML Modo B v5 injetado direto no iframe TinyMCE!`);

          highlightSaveButton(() => handleAfterSave());
          const isAuto = getSettings().autoPilot || getSettings().autoSave;
          renderHudProductMode(
            activeLoadedProduct,
            "✨ Injetado no Editor Visual (TinyMCE)!",
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres (${currentTheme.label}). ${isAuto ? '🤖 Salvando e avançando automaticamente...' : "Clique em 'Salvar' no topo."}`
          );
          return;
        }

        // Fallback 3: Contenteditable padrão
        const editable = document.querySelector("[contenteditable='true']");
        if (editable) {
          appendBackup(currentProductId, location.pathname, editable.innerHTML);
          editable.focus();
          editable.innerHTML = htmlContent;
          editable.dispatchEvent(new Event("input", { bubbles: true }));
          editable.dispatchEvent(new Event("change", { bubbles: true }));
          highlightSaveButton(() => handleAfterSave());
          renderHudProductMode(
            activeLoadedProduct,
            "✨ Injetado no Editor Visual!",
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres no editor visual.`
          );
        } else {
          try { GM_setClipboard(htmlContent); } catch(e) {}
          alert("O HTML oficial já foi copiado para sua área de transferência! Clique no ícone '<>' do editor da Shopify e pressione Ctrl+V.");
        }
      };

      setTimeout(tryInject, 450);
      return true;
    }

    function handleAfterSave() {
      if (currentProductId) {
        markProductAsCompliant(currentProductId, activeLoadedProduct?.master_sku);
      }
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();

      if (active && q.length > 0 && idx < q.length - 1) {
        startCountdownToNext();
      } else if (active && q.length > 0 && idx >= q.length - 1) {
        setAutomationActive(false);
        setQueueIndex(0);
        setQueue([]);
        alert(`🎉 Parabéns! O lote de ${q.length} códigos fora das diretrizes da ${currentStoreName} foi 100% atualizado e salvo!`);
        renderHudProductMode(activeLoadedProduct, "🎉 Lote 100% Concluído!", "Todos os produtos da fila foram atualizados para o Modo B v5.");
      }
    }

    function startCountdownToNext() {
      const settings = getSettings();
      let count = settings.autoPilot ? Math.min(settings.delaySeconds || 4, 2) : (settings.delaySeconds || 4);
      const q = getQueue();
      let nextIdx = getQueueIndex() + 1;

      // Pular quaisquer códigos que já tenham sido marcados como conformes na sessão
      while (nextIdx < q.length && isProductMarkedCompliant(q[nextIdx].id, q[nextIdx].master_sku)) {
        nextIdx++;
      }

      const nextItem = q[nextIdx];
      if (!nextItem) {
        setAutomationActive(false);
        setQueue([]);
        setQueueIndex(0);
        renderHudProductMode(activeLoadedProduct, "🎉 Fila Concluída!", "Todos os códigos fora das diretrizes deste lote foram corrigidos.");
        return;
      }

      if (countdownTimer) clearInterval(countdownTimer);

      countdownTimer = setInterval(() => {
        if (count <= 0) {
          clearInterval(countdownTimer);
          setQueueIndex(nextIdx);
          const nextUrl = `https://admin.shopify.com/store/${currentShopifySlug}/products/${nextItem.id}`;
          location.href = nextUrl;
        } else {
          renderHudProductMode(
            activeLoadedProduct,
            `🤖 Piloto Automático: Avançando em ${count}s...`,
            `Próximo código fora das diretrizes (${nextIdx + 1}/${q.length}): ${nextItem.master_sku || ''} — ${(nextItem.title || '').slice(0, 35)}...`
          );
          count--;
        }
      }, 900);
    }

    const injectDescriptionIntoShopify = injectModoBIntoEditor;
    const advanceToNextProduct = startCountdownToNext;

    // Renderizador do Mapa de Códigos (SKUs) Fora das Diretrizes (oculta 100% os códigos já conformes)
    function renderNonCompliantCodesBox(codesList) {
      const activeCodes = (codesList || []).filter(c => !isProductMarkedCompliant(c.id, c.sku));
      if (activeCodes.length === 0) {
        return "";
      }
      const rowsHtml = activeCodes.slice(0, 40).map(c => {
        let badgeCls = "brk-badge-legacy";
        let badgeLabel = "FORA MODO B";
        if (c.guideline_status === "MODO_B_DESATUALIZADO") { badgeCls = "brk-badge-outdated"; badgeLabel = "VIOLAÇÃO REGRA"; }
        else if (c.guideline_status === "SEM_DESCRICAO") { badgeCls = "brk-badge-empty"; badgeLabel = "SEM DESCRIÇÃO"; }
        else if (c.guideline_status === "IMAGENS_QUEBRADAS") { badgeCls = "brk-badge-broken"; badgeLabel = "S3 QUEBRADO"; }

        return `
          <div class="brk-code-row" data-prod-id="${c.id}" title="${(c.guideline_reason || c.title || '').replace(/"/g, '&quot;')}">
            <div style="display:flex;align-items:center;gap:6px;min-width:0;flex:1;">
              <strong style="color:#38bdf8;font-family:monospace;font-size:11px;flex-shrink:0;">${c.sku || c.id}</strong>
              <span class="brk-badge-status ${badgeCls}" style="font-size:8.5px;padding:1px 5px;flex-shrink:0;">${badgeLabel}</span>
              <span style="color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${c.guideline_reason || c.title}</span>
            </div>
            <span style="color:#4ade80;font-weight:700;font-size:10px;flex-shrink:0;">Abrir ➔</span>
          </div>
        `;
      }).join("");

      return `
        <details style="margin-bottom:10px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:6px 10px;">
          <summary style="cursor:pointer;font-size:11px;font-weight:800;color:#fbbf24;user-select:none;">
            🎯 Mapa de Códigos Fora das Diretrizes (${activeCodes.length} códigos mapeados — clique para ver)
          </summary>
          <div style="font-size:10px;color:#94a3b8;margin-top:4px;">
            Exibindo <strong>apenas</strong> códigos cujas descrições estão fora das regras Modo B v5 (itens já conformes são ocultados automaticamente):
          </div>
          <div class="brk-codes-scroll">
            ${rowsHtml}
          </div>
        </details>
      `;
    }

    function bindCodeRowClicks() {
      const rows = Array.from(hud.querySelectorAll(".brk-code-row[data-prod-id]"));
      for (const r of rows) {
        r.onclick = () => {
          const pid = r.getAttribute("data-prod-id");
          if (pid) {
            location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${pid}`;
          }
        };
      }
    }

    // Renderizador do Painel de Pente Fino Visual (Variantes sem Foto, Fotos Duplicadas e Baixa Qualidade)
    function renderMediaAuditAlertBox(prod) {
      const ma = prod?.media_audit;
      if (!ma || !ma.needs_media_fix) return "";

      const rows = [];
      if (ma.has_unlinked_variants && Array.isArray(ma.unlinked_variants) && ma.unlinked_variants.length > 0) {
        rows.push(`
          <div style="color:#fecaca;font-size:11px;line-height:1.35;margin-bottom:4px;">
            🔴 <strong>Cor(es) Sem Foto Vinculada (${ma.unlinked_variants.length}):</strong>
            <span style="color:#ffffff;font-family:monospace;background:#7f1d1d;padding:1px 5px;border-radius:4px;">${ma.unlinked_variants.join(", ")}</span>
            <span style="color:#fca5a5;display:block;font-size:10px;">➔ Vincule a miniatura na tabela de Variantes abaixo (evita foto congelada/duplicada ao trocar de cor).</span>
          </div>
        `);
      }
      if (ma.has_duplicate_images && Array.isArray(ma.duplicate_images) && ma.duplicate_images.length > 0) {
        const dupLabels = ma.duplicate_images.slice(0, 3).map(d => d.summary || `Pos ${d.pos1} == Pos ${d.pos2}`).join(" | ");
        rows.push(`
          <div style="color:#fed7aa;font-size:11px;line-height:1.35;margin-bottom:4px;">
            🟠 <strong>Fotos Duplicadas na Galeria (${ma.duplicate_images.length}):</strong>
            <span style="color:#ffedd5;">${dupLabels}${ma.duplicate_images.length > 3 ? '...' : ''}</span>
          </div>
        `);
      }
      if (ma.has_low_res_images && Array.isArray(ma.low_res_images) && ma.low_res_images.length > 0) {
        const lowLabels = ma.low_res_images.slice(0, 3).map(l => `Pos ${l.pos} (${l.w}x${l.h}px, ${l.kb}KB)`).join(", ");
        rows.push(`
          <div style="color:#fef08a;font-size:10.5px;line-height:1.35;">
            🟡 <strong>Baixa Qualidade/Borradas (${ma.low_res_images.length} fotos):</strong>
            <span style="color:#fef9c3;">${lowLabels}${ma.low_res_images.length > 3 ? ` +${ma.low_res_images.length - 3} fotos` : ''}</span>
          </div>
        `);
      }

      return `
        <div style="background:#450a0a;border:1px solid #ef4444;border-radius:8px;padding:8px 10px;margin-bottom:10px;">
          <div style="font-size:11px;font-weight:800;color:#fca5a5;margin-bottom:4px;display:flex;align-items:center;justify-content:space-between;">
            <span>🔍 PENTE FINO DE FOTOS & CORES ${prod.in_super_ofertas ? '(SUPER OFERTAS 🔥)' : ''}</span>
            <span style="background:#991b1b;color:#fff;padding:1px 6px;border-radius:9999px;font-size:9.5px;">AJUSTE VISUAL</span>
          </div>
          ${rows.join("")}
        </div>
      `;
    }

    // =========================================================================
    // RENDERIZAÇÃO DO HUD NA PÁGINA DO PRODUTO (admin.shopify.com/.../products/{id})
    // =========================================================================
    function renderHudProductMode(prod, statusTitle, statusSub) {
      const q = getQueue();
      const idx = getQueueIndex();
      const inQueue = q.length > 0 && q[idx] && String(q[idx].id) === String(currentProductId);
      const settings = getSettings();
      const editorHealth = inspectEditorHealth(prod);
      const hasBackup = !!getLastBackupForProduct(currentProductId);

      hud.style.borderColor = currentTheme.primary;

      let statusBadgeClass = "brk-badge-healthy";
      const gStatus = prod?.guideline_status || prod?.status || "SAUDAVEL";
      if (gStatus === "SEM_DESCRICAO") statusBadgeClass = "brk-badge-empty";
      else if (gStatus === "IMAGENS_QUEBRADAS") statusBadgeClass = "brk-badge-broken";
      else if (gStatus === "MODO_B_DESATUALIZADO") statusBadgeClass = "brk-badge-outdated";
      else if (gStatus === "FORA_PADRAO_MODO_B") statusBadgeClass = "brk-badge-legacy";

      const imgCount = prod ? (prod.gallery || prod.cdn_images || []).length : 0;

      let editorBadgeStyle = "background:#1e293b;color:#cbd5e1;";
      if (editorHealth.state === "UP_TO_DATE") editorBadgeStyle = "background:#065f46;color:#6ee7b7;";
      else if (editorHealth.state === "OUTDATED_MODE_B") editorBadgeStyle = "background:#92400e;color:#fde68a;";
      else if (editorHealth.state === "EMPTY" || editorHealth.state === "LEGACY_BROKEN") editorBadgeStyle = "background:#7f1d1d;color:#fecaca;";

      const queueCodes = q.length > 0
        ? q.slice(idx).map(item => ({
            id: item.id,
            sku: item.master_sku || item.sku || item.id,
            title: item.title,
            guideline_status: item.guideline_status || item.status,
            guideline_reason: item.guideline_reason || ""
          }))
        : cachedNonCompliantCodes;

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;">
            <span style="font-size:15px;">${settings.autoPilot ? '🤖' : '🟢'}</span>
            <strong style="color:${currentTheme.light};font-size:13px;">BANCO BRK v${SCRIPT_VERSION}</strong>
            <span style="${editorBadgeStyle}font-size:10px;font-weight:800;padding:2px 7px;border-radius:9999px;">${editorHealth.badge}</span>
          </div>
          <span style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};font-size:10px;font-weight:800;padding:2px 8px;border-radius:9999px;">
            ${inQueue ? `Fila ${idx + 1}/${q.length} • ${currentStoreName}` : `${currentStoreName} (${currentTheme.label})`}
          </span>
        </div>

        <div style="margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;flex-wrap:wrap;">
            <span style="font-weight:800;color:#f8fafc;font-size:14px;font-family:monospace;">${prod ? (prod.master_sku || 'Sem SKU') : 'Carregando...'}</span>
            ${prod ? `<span class="brk-badge-status ${statusBadgeClass}">${gStatus}</span>` : ''}
            ${prod && prod.in_super_ofertas ? `<span class="brk-badge-meta" style="background:#7c2d12;color:#fed7aa;">🔥 Super Ofertas</span>` : ''}
            ${prod ? `<span class="brk-badge-meta">📂 ${prod.category || 'Geral'}</span>` : ''}
            ${prod ? `<span class="brk-badge-meta">📸 ${imgCount} fotos únicas</span>` : ''}
            ${prod && prod.delivery_time ? `<span class="brk-badge-meta">🚚 ${prod.delivery_time}</span>` : ''}
          </div>
          <div style="font-size:12px;color:#cbd5e1;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:480px;">
            ${prod ? prod.title : 'Consultando dados reais na API...'}
          </div>
          ${prod ? `
            <div style="display:flex;align-items:center;gap:6px;margin-top:5px;flex-wrap:wrap;">
              <span style="font-size:10px;color:${currentTheme.light};font-weight:700;">🧩 ${prod.layout_type || prod.archetype_name || 'Modo B'}</span>
              <span style="font-size:10px;color:#94a3b8;">•</span>
              <span style="font-size:10px;color:#e2e8f0;font-weight:700;">👤 ${prod.audience_badge || 'ADULTO'}</span>
            </div>
          ` : ''}
        </div>

        ${renderMediaAuditAlertBox(prod)}

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:10px;">
          <div style="font-weight:700;color:${currentTheme.light};font-size:12px;">${statusTitle || "Pronto para Injeção"}</div>
          <div style="font-size:11px;color:#94a3b8;line-height:1.4;">${statusSub || editorHealth.reason}</div>
          ${prod && prod.mode_b_html ? `
            <div style="margin-top:6px;font-size:11px;color:#4ade80;font-weight:700;display:flex;align-items:center;justify-content:space-between;border-top:1px solid #1e293b;padding-top:4px;">
              <span>⭐ Modo B v5 Compilado: ${(prod.mode_b_html.length).toLocaleString('pt-BR')} chars</span>
              <span style="color:#94a3b8;font-weight:600;">${prod.archetype_name || '3 Atos + Ficha Técnica'}</span>
            </div>
          ` : ''}
        </div>

        ${renderNonCompliantCodesBox(queueCodes)}

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;padding:4px 8px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;flex-wrap:wrap;gap:6px;">
          <label class="brk-hud-toggle" title="Piloto Automático Total: injeta a descrição no editor, clica em Salvar automaticamente e avança sozinho">
            <input type="checkbox" id="brk-chk-autopilot" ${settings.autoPilot ? 'checked' : ''} style="accent-color:#22c55e;" />
            <strong style="color:#4ade80;">🤖 Piloto Automático</strong>
          </label>
          <label class="brk-hud-toggle" title="Clica automaticamente no botão Salvar da Shopify após injetar o Modo B">
            <input type="checkbox" id="brk-chk-autosave" ${settings.autoSave ? 'checked' : ''} style="accent-color:${currentTheme.primary};" />
            <span>Auto-Salvar</span>
          </label>
          <label class="brk-hud-toggle" title="Pausa antes de clicar em Salvar quando o produto tiver cor sem foto vinculada (image_id=null) ou foto duplicada">
            <input type="checkbox" id="brk-chk-pause-media" ${settings.pauseOnMediaError ? 'checked' : ''} style="accent-color:#f59e0b;" />
            <span style="color:#fbbf24;">⏸️ Pausar se Cor s/ Foto</span>
          </label>
          <label class="brk-hud-toggle" title="Durante um lote, pula produtos que já estão 100% conformes com as diretrizes Modo B v5">
            <input type="checkbox" id="brk-chk-skip-done" ${settings.skipAlreadyModeB ? 'checked' : ''} style="accent-color:${currentTheme.primary};" />
            <span>Pular Conformes</span>
          </label>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          <button id="brk-btn-inject" class="brk-hud-btn brk-hud-btn-primary" style="background:${currentTheme.primary};border-color:${currentTheme.primaryHover};" title="Injeta a narrativa completa Modo B v5 no editor HTML e salva se Auto-Salvar estiver ativo">
            ⚡ Injetar Modo B
          </button>
          <button id="brk-btn-preview" class="brk-hud-btn" title="Abre uma janela visual dentro do Shopify Admin mostrando como a descrição Modo B v5 ficará na loja">
            👁️ Preview
          </button>
          <button id="brk-btn-copy" class="brk-hud-btn" title="Copia o HTML oficial para a área de transferência">
            📋 Copiar
          </button>
          <button id="brk-btn-live-sync" class="brk-hud-btn" title="Trocou as fotos agora na Shopify? Clique para buscar as fotos novas ao vivo e recompilar a descrição!">
            🔄 Fotos Live
          </button>
          ${hasBackup ? `
            <button id="brk-btn-restore" class="brk-hud-btn" title="Restaura o HTML original salvo antes da injeção">
              ↩️ Desfazer
            </button>
          ` : ''}
          ${inQueue ? `
            <button id="brk-btn-next-now" class="brk-hud-btn">
              ⏭️ Próximo
            </button>
            <button id="brk-btn-pause-queue" class="brk-hud-btn brk-hud-btn-danger">
              ⏹️ Parar
            </button>
          ` : `
            <button id="brk-btn-start-super-ofertas" class="brk-hud-btn brk-hud-btn-success" title="Inicia o lote da Coleção Super Ofertas 🔥 (91 itens)">
              🔥 Lote Super Ofertas
            </button>
            <button id="brk-btn-start-autopilot-25" class="brk-hud-btn" title="Busca apenas os códigos fora das diretrizes e aplica tudo automaticamente!">
              🤖 Auto-Lote Geral
            </button>
          `}
        </div>
      `;

      bindCodeRowClicks();

      // Toggles de configuração
      const chkAutoPilot = document.getElementById("brk-chk-autopilot");
      if (chkAutoPilot) {
        chkAutoPilot.onchange = (e) => {
          saveSettings({ autoPilot: e.target.checked, autoSave: e.target.checked ? true : getSettings().autoSave });
          renderHudProductMode(prod, statusTitle, statusSub);
        };
      }

      const chkAutoSave = document.getElementById("brk-chk-autosave");
      if (chkAutoSave) chkAutoSave.onchange = (e) => saveSettings({ autoSave: e.target.checked });

      const chkPauseMedia = document.getElementById("brk-chk-pause-media");
      if (chkPauseMedia) chkPauseMedia.onchange = (e) => saveSettings({ pauseOnMediaError: e.target.checked });

      const chkSkipDone = document.getElementById("brk-chk-skip-done");
      if (chkSkipDone) chkSkipDone.onchange = (e) => saveSettings({ skipAlreadyModeB: e.target.checked });

      // Eventos dos botões
      const btnInject = document.getElementById("brk-btn-inject");
      if (btnInject && prod) {
        btnInject.onclick = () => injectModoBIntoEditor(prod.mode_b_html);
      }

      const btnPreview = document.getElementById("brk-btn-preview");
      if (btnPreview && prod) {
        btnPreview.onclick = () => openPreviewModal(prod);
      }

      const btnCopy = document.getElementById("brk-btn-copy");
      if (btnCopy && prod) {
        btnCopy.onclick = () => {
          const html = prod.mode_b_html || "";
          try { GM_setClipboard(html); } catch(e) {}
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(html).catch(() => {});
          }
          renderHudProductMode(prod, "📋 HTML Modo B v5 Copiado!", `Copiados ${(html.length).toLocaleString('pt-BR')} caracteres da narrativa oficial (${currentTheme.label}).`);
        };
      }

      const btnLiveSync = document.getElementById("brk-btn-live-sync");
      if (btnLiveSync) {
        btnLiveSync.onclick = async () => {
          renderHudProductMode(prod, "🔄 Sincronizando Fotos ao Vivo...", "Buscando galeria atualizada na vitrine da Shopify e recompilando...");
          try {
            const hints = extractPageHints();
            const handleParam = (prod && prod.handle) || hints.handle || "";
            const res = await fetchFromBRKDatabase(
              `/api/product_db?store=${currentStoreKey}&id=${currentProductId}&handle=${encodeURIComponent(handleParam)}&sync_live=1`
            );
            if (res.success && res.product) {
              activeLoadedProduct = res.product;
              const newCount = (activeLoadedProduct.gallery || []).length;
              renderHudProductMode(
                activeLoadedProduct,
                "✅ Fotos Sincronizadas ao Vivo!",
                `Galeria atualizada (${newCount} fotos únicas) e Modo B v5 recompilado (${currentTheme.label}).`
              );
            }
          } catch(err) {
            renderHudProductMode(prod, "⚠️ Erro no Sync Live", err.message);
          }
        };
      }

      const btnRestore = document.getElementById("brk-btn-restore");
      if (btnRestore) {
        btnRestore.onclick = () => {
          const bkp = getLastBackupForProduct(currentProductId);
          if (bkp && confirm("Deseja restaurar o HTML anterior deste produto no editor?")) {
            injectModoBIntoEditor(bkp.body_html || "");
          }
        };
      }

      const btnNextNow = document.getElementById("brk-btn-next-now");
      if (btnNextNow) {
        btnNextNow.onclick = () => {
          if (countdownTimer) clearInterval(countdownTimer);
          const nextIdx = idx + 1;
          if (nextIdx < q.length) {
            setQueueIndex(nextIdx);
            location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${q[nextIdx].id}`;
          } else {
            setAutomationActive(false);
            alert("Fim da fila de produtos!");
          }
        };
      }

      const btnPauseQueue = document.getElementById("brk-btn-pause-queue");
      if (btnPauseQueue) {
        btnPauseQueue.onclick = () => {
          if (countdownTimer) clearInterval(countdownTimer);
          setAutomationActive(false);
          setQueue([]);
          setQueueIndex(0);
          renderHudProductMode(prod, "⏹️ Lote Pausado", "Fila encerrada. Você pode operar individualmente.");
        };
      }

      const btnStartSO = document.getElementById("brk-btn-start-super-ofertas");
      if (btnStartSO) {
        btnStartSO.onclick = () => {
          saveSettings({ batchCategory: "super_ofertas", batchStatus: "FORA_DIRETRIZES", batchLimit: 100, autoPilot: true, autoSave: true });
          startQueueFromDatabase("FORA_DIRETRIZES", 100, "super_ofertas", "super-ofertas-🔥");
        };
      }

      const btnStartAuto25 = document.getElementById("brk-btn-start-autopilot-25");
      if (btnStartAuto25) {
        btnStartAuto25.onclick = () => {
          saveSettings({ autoPilot: true, autoSave: true });
          startQueueFromDatabase("FORA_DIRETRIZES", 25, "ALL");
        };
      }
    }

    // =========================================================================
    // RENDERIZAÇÃO DO HUD NA LISTAGEM DE PRODUTOS (admin.shopify.com/.../products)
    // =========================================================================
    function renderHudListMode(stats) {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      const settings = getSettings();
      const soStats = stats?.super_ofertas_stats || { total: 91, needs_media_fix: 83, unlinked_variants: 38, duplicate_images: 26, low_res_images: 75 };

      hud.style.borderColor = currentTheme.primary;
      if (stats && Array.isArray(stats.non_compliant_codes)) {
        cachedNonCompliantCodes = stats.non_compliant_codes;
      }

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">🤖</span>
            <strong style="color:${currentTheme.light};font-size:13px;">BANCO BRK v${SCRIPT_VERSION} • LOTE & COLEÇÕES</strong>
          </div>
          <span style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};font-size:10px;font-weight:800;padding:2px 8px;border-radius:9999px;">
            ${currentStoreName} • ${currentTheme.label}
          </span>
        </div>

        <div style="margin-bottom:10px;font-size:12px;color:#cbd5e1;line-height:1.5;">
          ${stats ? `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;background:#0f172a;padding:8px 10px;border-radius:8px;border:1px solid #1e293b;">
              <div style="color:#4ade80;">✅ Já Conformes (Ocultos): <strong>${stats.compliant_count || 0}</strong></div>
              <div style="color:#38bdf8;">🎯 Total Fora Diretrizes: <strong>${stats.non_compliant_count || stats.total_products}</strong></div>
              <div style="color:#fbbf24;">⚠️ Modo B c/ Violação: <strong>${stats.modo_b_desatualizado_count || 0}</strong></div>
              <div style="color:#fb923c;">🔥 Super Ofertas Auditados: <strong>${soStats.total} itens (${soStats.needs_media_fix} c/ ajuste)</strong></div>
            </div>
          ` : 'Mapeando conformidade de todos os códigos e coleções da loja nas diretrizes Modo B v5...'}
        </div>

        ${renderNonCompliantCodesBox(cachedNonCompliantCodes)}

        ${q.length > 0 ? `
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:10px;">
            <div style="font-weight:700;color:${currentTheme.light};font-size:12px;">Fila Ativa: Código ${idx + 1} de ${q.length} (${q[idx]?.master_sku || ''})</div>
            <div style="font-size:11px;color:#94a3b8;">Status: ${active ? '🤖 Piloto Automático Ativo' : 'Pausado'}</div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
            <button id="brk-btn-resume-queue" class="brk-hud-btn brk-hud-btn-success" style="flex:1;justify-content:center;">
              🤖 Retomar Piloto Automático (${idx + 1}/${q.length})
            </button>
            <button id="brk-btn-clear-queue" class="brk-hud-btn brk-hud-btn-danger">
              ⏹️ Limpar Fila
            </button>
          </div>
        ` : `
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:9px 11px;margin-bottom:10px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;flex-wrap:wrap;gap:6px;">
              <span style="font-weight:700;color:${currentTheme.light};font-size:11px;">🎯 Configurar Lote por Coleção ou Categoria</span>
              <div style="display:flex;align-items:center;gap:8px;">
                <label class="brk-hud-toggle" title="Injeta, clica em Salvar e avança sozinho">
                  <input type="checkbox" id="brk-list-chk-autopilot" ${settings.autoPilot ? 'checked' : ''} style="accent-color:#22c55e;" />
                  <strong style="color:#4ade80;font-size:10.5px;">🤖 Auto-Save</strong>
                </label>
                <label class="brk-hud-toggle" title="Pausa o Auto-Save quando o produto tiver cor sem foto vinculada ou foto duplicada">
                  <input type="checkbox" id="brk-list-chk-pause-media" ${settings.pauseOnMediaError ? 'checked' : ''} style="accent-color:#f59e0b;" />
                  <span style="color:#fbbf24;font-size:10.5px;">⏸️ Pausar em Cor s/ Foto</span>
                </label>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1.1fr 1.1fr 0.55fr;gap:6px;margin-bottom:6px;">
              <select id="brk-sel-category" class="brk-hud-select" title="Filtrar por Coleção/Categoria">
                <option value="super_ofertas" ${settings.batchCategory === 'super_ofertas' ? 'selected' : ''}>🔥 Coleção: Super Ofertas Fishing (91 itens)</option>
                <option value="ALL" ${settings.batchCategory === 'ALL' ? 'selected' : ''}>📂 Todas as Coleções da Loja</option>
                <option value="iscas_artificiais" ${settings.batchCategory === 'iscas_artificiais' ? 'selected' : ''}>🎣 Iscas Artificiais</option>
                <option value="equipamentos_pesca" ${settings.batchCategory === 'equipamentos_pesca' ? 'selected' : ''}>⚙️ Varas, Carretilhas, Molinetes & Alicates</option>
                <option value="linhas_pesca" ${settings.batchCategory === 'linhas_pesca' ? 'selected' : ''}>🧵 Linhas de Pesca</option>
                <option value="bones_chapeus" ${settings.batchCategory === 'bones_chapeus' ? 'selected' : ''}>🧢 Bonés & Chapéus</option>
                <option value="camisas" ${settings.batchCategory === 'camisas' ? 'selected' : ''}>👕 Camisas (Fusion/Hybrid/ArmorX/C0)</option>
                <option value="calcas" ${settings.batchCategory === 'calcas' ? 'selected' : ''}>👖 Calças & Bermudas</option>
                <option value="corta_vento" ${settings.batchCategory === 'corta_vento' ? 'selected' : ''}>🧥 Corta-Vento & Jaquetas</option>
                <option value="infantil" ${settings.batchCategory === 'infantil' ? 'selected' : ''}>🧒 Linha Infantil (2 a 13 Anos)</option>
                <option value="feminino" ${settings.batchCategory === 'feminino' ? 'selected' : ''}>👚 Linha Feminina (Baby Look)</option>
                <option value="CUSTOM_COLLECTION" ${settings.batchCategory === 'CUSTOM_COLLECTION' ? 'selected' : ''}>🔗 Outra Coleção (Digitar URL/Handle abaixo)</option>
              </select>
              <select id="brk-sel-status" class="brk-hud-select" title="Filtrar por Modo de Triagem (Diretrizes Modo B ou Pente Fino de Fotos)">
                <option value="FORA_DIRETRIZES" ${settings.batchStatus === 'FORA_DIRETRIZES' ? 'selected' : ''}>🎯 Todos Fora das Diretrizes Modo B</option>
                <option value="AJUSTE_FOTOS_GERAL" ${settings.batchStatus === 'AJUSTE_FOTOS_GERAL' ? 'selected' : ''}>🔥 Pente Fino: Todos c/ Ajuste de Foto/Cor</option>
                <option value="CRITICOS_FOTOS_CORES" ${settings.batchStatus === 'CRITICOS_FOTOS_CORES' ? 'selected' : ''}>🚨 Críticos: Cor sem Foto + Fotos Duplicadas</option>
                <option value="COR_SEM_FOTO" ${settings.batchStatus === 'COR_SEM_FOTO' ? 'selected' : ''}>🧩 Apenas Cores Sem Foto (image_id=null)</option>
                <option value="FOTOS_DUPLICADAS" ${settings.batchStatus === 'FOTOS_DUPLICADAS' ? 'selected' : ''}>👯 Apenas Fotos Duplicadas na Galeria/Cores</option>
                <option value="FOTOS_BAIXA_QUALIDADE" ${settings.batchStatus === 'FOTOS_BAIXA_QUALIDADE' ? 'selected' : ''}>📉 Apenas Fotos de Baixa Qualidade (<800px)</option>
                <option value="COLECAO_COMPLETA" ${settings.batchStatus === 'COLECAO_COMPLETA' ? 'selected' : ''}>📦 Coleção Completa (Todos os Itens)</option>
                <option value="MODO_B_DESATUALIZADO" ${settings.batchStatus === 'MODO_B_DESATUALIZADO' ? 'selected' : ''}>⚠️ Violação Regra (Faca/ArmorX/Fusion)</option>
                <option value="SEM_DESCRICAO" ${settings.batchStatus === 'SEM_DESCRICAO' ? 'selected' : ''}>🔴 Sem Descrição</option>
                <option value="IMAGENS_QUEBRADAS" ${settings.batchStatus === 'IMAGENS_QUEBRADAS' ? 'selected' : ''}>🖼️ Fotos S3 Quebradas</option>
              </select>
              <select id="brk-sel-limit" class="brk-hud-select" title="Quantidade de Produtos no Lote">
                <option value="25" ${Number(settings.batchLimit) === 25 ? 'selected' : ''}>25 códigos</option>
                <option value="50" ${Number(settings.batchLimit) === 50 ? 'selected' : ''}>50 códigos</option>
                <option value="100" ${Number(settings.batchLimit) === 100 ? 'selected' : ''}>100 códigos</option>
              </select>
            </div>
            <div style="margin-bottom:8px;">
              <input id="brk-inp-collection" type="text" value="${(settings.customCollection || '').replace(/"/g, '&quot;')}" placeholder="Opcional: Cole aqui a URL ou handle de qualquer coleção Shopify (ex: super-ofertas-🔥 ou iscas-artificiais)" style="width:100%;background:#1e293b;color:#f8fafc;border:1px solid #334155;border-radius:6px;padding:5px 8px;font-size:11px;box-sizing:border-box;" />
            </div>
            <button id="brk-btn-start-custom-batch" class="brk-hud-btn brk-hud-btn-success" style="width:100%;justify-content:center;padding:8px 12px;font-size:12.5px;">
              🚀 Iniciar Lote da Coleção / Categoria Selecionada
            </button>
          </div>

          <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
            <button id="brk-btn-so-criticos" class="brk-hud-btn" style="background:#7c2d12;border-color:#ea580c;color:#ffedd5;" title="Abre os produtos críticos da coleção Super Ofertas 🔥 (Cores sem foto vinculada + Fotos duplicadas) pausando para ajuste visual + Modo B">
              🔥 Super Ofertas: Críticos Cor/Duplicada
            </button>
            <button id="brk-btn-so-all80" class="brk-hud-btn" style="background:#0c4a6e;border-color:#0284c7;color:#bae6fd;" title="Roda o lote em todos os produtos da coleção Super Ofertas 🔥 que precisam de ajuste">
              🔥 Super Ofertas: Lote Completo (${soStats.needs_media_fix || 83})
            </button>
            <button id="brk-btn-fix-violations" class="brk-hud-btn" title="Corrige prioritariamente os códigos colados com violação (Faca Marine MFK75T, ArmorX com Tabela de Luvas, Fusion/Hybrid)">
              ⚡ Violações (${stats?.modo_b_desatualizado_count || 21})
            </button>
          </div>
        `}
      `;

      bindCodeRowClicks();

      const chkListAuto = document.getElementById("brk-list-chk-autopilot");
      if (chkListAuto) {
        chkListAuto.onchange = (e) => {
          saveSettings({ autoPilot: e.target.checked, autoSave: e.target.checked ? true : getSettings().autoSave });
        };
      }

      const chkListPauseMedia = document.getElementById("brk-list-chk-pause-media");
      if (chkListPauseMedia) {
        chkListPauseMedia.onchange = (e) => {
          saveSettings({ pauseOnMediaError: e.target.checked });
        };
      }

      const btnResume = document.getElementById("brk-btn-resume-queue");
      if (btnResume) {
        btnResume.onclick = () => {
          setAutomationActive(true);
          const currentItem = q[idx] || q[0];
          location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${currentItem.id}`;
        };
      }

      const btnClear = document.getElementById("brk-btn-clear-queue");
      if (btnClear) {
        btnClear.onclick = () => {
          setQueue([]);
          setQueueIndex(0);
          setAutomationActive(false);
          renderHudListMode(stats);
        };
      }

      const btnCustomBatch = document.getElementById("brk-btn-start-custom-batch");
      if (btnCustomBatch) {
        btnCustomBatch.onclick = () => {
          const cat = document.getElementById("brk-sel-category")?.value || "ALL";
          const st = document.getElementById("brk-sel-status")?.value || "FORA_DIRETRIZES";
          const lim = parseInt(document.getElementById("brk-sel-limit")?.value || "100", 10);
          const colInput = (document.getElementById("brk-inp-collection")?.value || "").trim();
          const finalCol = colInput || (cat === "super_ofertas" ? "super-ofertas-🔥" : "");
          saveSettings({ batchCategory: cat, batchStatus: st, batchLimit: lim, customCollection: colInput });
          startQueueFromDatabase(st, lim, cat === "CUSTOM_COLLECTION" ? "ALL" : cat, finalCol);
        };
      }

      const btnSoCriticos = document.getElementById("brk-btn-so-criticos");
      if (btnSoCriticos) {
        btnSoCriticos.onclick = () => {
          saveSettings({ batchCategory: "super_ofertas", batchStatus: "CRITICOS_FOTOS_CORES", batchLimit: 100, pauseOnMediaError: true, autoPilot: true, autoSave: true });
          startQueueFromDatabase("CRITICOS_FOTOS_CORES", 100, "super_ofertas", "super-ofertas-🔥");
        };
      }

      const btnSoAll80 = document.getElementById("brk-btn-so-all80");
      if (btnSoAll80) {
        btnSoAll80.onclick = () => {
          saveSettings({ batchCategory: "super_ofertas", batchStatus: "AJUSTE_FOTOS_GERAL", batchLimit: 100, autoPilot: true, autoSave: true });
          startQueueFromDatabase("AJUSTE_FOTOS_GERAL", 100, "super_ofertas", "super-ofertas-🔥");
        };
      }

      const btnFixViolations = document.getElementById("brk-btn-fix-violations");
      if (btnFixViolations) {
        btnFixViolations.onclick = () => {
          saveSettings({ autoPilot: true, autoSave: true });
          startQueueFromDatabase("MODO_B_DESATUALIZADO", 30, "ALL");
        };
      }
    }

    // =========================================================================
    // INICIAR FILA REAL BUSCADA DIRETAMENTE DO BANCO (SUPORTA COLEÇÕES & PENTE FINO)
    // =========================================================================
    async function startQueueFromDatabase(statusFilter = "FORA_DIRETRIZES", limit = 25, categoryFilter = "ALL", collectionHandle = "") {
      hud.innerHTML = `
        <div style="padding:10px;text-align:center;">
          <div style="font-size:18px;margin-bottom:8px;">🤖</div>
          <strong style="color:${currentTheme.light};">Carregando Lote da Coleção / Banco BRK...</strong>
          <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Buscando até ${limit} produtos (${statusFilter} | ${collectionHandle || categoryFilter}) em ${currentStoreName}...</div>
        </div>
      `;

      try {
        const isMediaAuditMode = [
          "COLECAO_COMPLETA",
          "AJUSTE_FOTOS_GERAL",
          "CRITICOS_FOTOS_CORES",
          "COR_SEM_FOTO",
          "FOTOS_DUPLICADAS",
          "FOTOS_BAIXA_QUALIDADE"
        ].includes(statusFilter);

        const excludeParam = isMediaAuditMode ? "" : encodeURIComponent(getCompliantIds().slice(-300).join(","));
        const queryUrl = `/api/product_db?store=${currentStoreKey}&action=queue&status=${encodeURIComponent(statusFilter)}&category=${encodeURIComponent(categoryFilter)}&collection=${encodeURIComponent(collectionHandle || "")}&limit=${limit}&exclude_ids=${excludeParam}`;
        const res = await fetchFromBRKDatabase(queryUrl);
        const queueItems = isMediaAuditMode
          ? (res.items || [])
          : (res.items || []).filter(it => !it.is_mode_b_compliant && !isProductMarkedCompliant(it.id, it.master_sku));

        if (!res.success || queueItems.length === 0) {
          alert(`✅ Nenhum produto pendente encontrado para este filtro (${statusFilter} / ${collectionHandle || categoryFilter}) na loja ${currentStoreName}!`);
          initAdmin();
          return;
        }

        if (Array.isArray(res.non_compliant_codes)) {
          cachedNonCompliantCodes = res.non_compliant_codes;
        }

        setQueue(queueItems);
        setQueueIndex(0);
        setAutomationActive(true);

        const firstProduct = queueItems[0];
        console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Lote de ${queueItems.length} produtos carregado. Primeiro: ID ${firstProduct.id} (${firstProduct.master_sku})`);

        hud.innerHTML = `
          <div style="padding:10px;text-align:center;">
            <div style="font-size:18px;margin-bottom:8px;">🚀</div>
            <strong style="color:#22c55e;">${queueItems.length} Produtos da Coleção Enfileirados!</strong>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Abrindo primeiro produto: <strong>${firstProduct.master_sku || firstProduct.id}</strong>...</div>
          </div>
        `;

        setTimeout(() => {
          location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${firstProduct.id}`;
        }, 750);

      } catch(err) {
        alert(`Erro ao buscar lote do banco de dados: ${err.message}`);
        initAdmin();
      }
    }

    // =========================================================================
    // INICIALIZAÇÃO NO SHOPIFY ADMIN + OBSERVADOR DE NAVEGAÇÃO SPA
    // =========================================================================
    async function initAdmin() {
      parseCurrentRoute();
      lastObservedPath = location.pathname;

      // Caso 1: Estamos na página de edição de um produto específico
      if (currentProductId) {
        renderHudProductMode(null, "Consultando Banco BRK...", `Auditando diretrizes e fotos do produto ID ${currentProductId} (${currentStoreName})...`);

        try {
          const hints = extractPageHints();
          const query = `/api/product_db?store=${currentStoreKey}&id=${currentProductId}` +
            (hints.handle ? `&handle=${encodeURIComponent(hints.handle)}` : "") +
            (hints.sku ? `&sku=${encodeURIComponent(hints.sku)}` : "");

          const res = await fetchFromBRKDatabase(query);
          if (res.success && res.product) {
            activeLoadedProduct = res.product;
            console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Produto carregado do banco:`, activeLoadedProduct.master_sku);

            // Aguarda o editor da Shopify montar antes de inspecionar e injetar automaticamente
            await waitForEditorReady(6500);

            const q = getQueue();
            const idx = getQueueIndex();
            const inQueue = q.length > 0 && q[idx] && String(q[idx].id) === String(currentProductId);
            const active = isAutomationActive();
            const settings = getSettings();
            const editorHealth = inspectEditorHealth(activeLoadedProduct);
            const ma = activeLoadedProduct?.media_audit || {};
            const hasCriticalMedia = ma.has_unlinked_variants || ma.has_duplicate_images;

            if (inQueue && active) {
              // Se o produto já está 100% dentro das diretrizes Modo B v5 e não precisa pausar por erro de foto/cor, marca e pula!
              const shouldSkip = settings.skipAlreadyModeB && !(settings.pauseOnMediaError && hasCriticalMedia) && (
                editorHealth.state === "UP_TO_DATE" ||
                (editorHealth.state === "OUTDATED_MODE_B" && !settings.upgradeOutdatedModeB)
              );

              if (shouldSkip) {
                markProductAsCompliant(currentProductId, activeLoadedProduct.master_sku);
                renderHudProductMode(
                  activeLoadedProduct,
                  "✅ Código Já Está 100% Dentro das Diretrizes!",
                  "Pulando automaticamente para o próximo produto da fila..."
                );
                setTimeout(() => startCountdownToNext(), 650);
                return;
              }

              renderHudProductMode(
                activeLoadedProduct,
                editorHealth.state === "OUTDATED_MODE_B" ? "🤖 Piloto Automático: Corrigindo Violação de Diretriz..." : "🤖 Piloto Automático: Aplicando Modo B v5...",
                editorHealth.state === "OUTDATED_MODE_B" ? editorHealth.reason : "Injetando descrição oficial da coleção..."
              );
              setTimeout(() => {
                injectModoBIntoEditor(activeLoadedProduct.mode_b_html);
              }, 600);
            } else {
              let titleMsg = "Produto Auditado no Banco BRK";
              if (editorHealth.state === "UP_TO_DATE") titleMsg = "✅ Código 100% Dentro das Diretrizes v5";
              else if (editorHealth.state === "OUTDATED_MODE_B") titleMsg = "⚠️ Código Fora das Diretrizes (Correção Pronta)";
              renderHudProductMode(
                activeLoadedProduct,
                titleMsg,
                editorHealth.reason
              );
            }
          } else {
            renderHudProductMode(null, "Produto não encontrado", `O ID ${currentProductId} não foi localizado no banco da loja ${currentStoreName}.`);
          }
        } catch(err) {
          console.error(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Erro ao carregar produto:`, err);
          renderHudProductMode(null, "Erro de Conexão com a API", err.message);
        }
      }
      // Caso 2: Estamos na listagem de produtos (/products)
      else {
        activeLoadedProduct = null;
        renderHudListMode(null);
        try {
          const excludeParam = encodeURIComponent(getCompliantIds().slice(-300).join(","));
          const stats = await fetchFromBRKDatabase(`/api/product_db?store=${currentStoreKey}&action=stats&exclude_ids=${excludeParam}`);
          if (stats.success) {
            renderHudListMode(stats);
          }
        } catch(e) {
          console.warn(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Não foi possível carregar estatísticas:`, e);
        }
      }
    }

    // Observador de rota SPA do Shopify Admin (detecta navegação entre produtos sem reload completo)
    setInterval(() => {
      if (location.pathname !== lastObservedPath) {
        if (countdownTimer) clearInterval(countdownTimer);
        if (saveCompletionTimer) clearInterval(saveCompletionTimer);
        lastObservedPath = location.pathname;
        setTimeout(initAdmin, 450);
      }
    }, 450);

    // Iniciar após pequeno delay para o DOM do Shopify Admin estabilizar
    setTimeout(initAdmin, 800);
  }

})();
