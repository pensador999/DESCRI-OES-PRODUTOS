// ==UserScript==
// @name         BRK Assistente de Descrições Shopify (Conectado ao Banco Real v4.0 Completo)
// @namespace    https://1025-ten.vercel.app/
// @version      4.0.0
// @description  Automação assistida e em lote conectada diretamente ao banco de dados oficial BRK (6.242 produtos auditados nas 3 Lojas: Fishing Azul, Agro Verde, Motors Laranja) para preenchimento e auditoria de descrições Modo B (3 Atos + Molde D2C Bonés/Chapéus + Ficha Técnica + Guias Adulto/Feminino/Infantil 2-13 Anos) no Shopify Admin.
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

  // Configuração da API do Banco de Dados BRK (6.242 produtos auditados nas 3 lojas)
  const API_BASE = "https://1025-ten.vercel.app";
  const SCRIPT_VERSION = "4.0.0";

  const STORAGE_KEYS = {
    QUEUE: "BRK_AUTOSYNC_QUEUE",
    INDEX: "BRK_AUTOSYNC_INDEX",
    ACTIVE: "BRK_AUTOSYNC_ACTIVE",
    BACKUP: "BRK_AUTOSYNC_BACKUP",
    SETTINGS: "BRK_AUTOSYNC_SETTINGS",
    LAST_STORE: "BRK_LAST_STORE"
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

  // Paletas Visuais Oficiais de cada Loja (Fase 5 & 6)
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
      markers: ["#15803d", "#22c55e"]
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
    autoSave: false,             // Se true, clica automaticamente no botão "Salvar" da Shopify após injetar
    skipAlreadyModeB: true,      // Se true, avança automaticamente quando o produto já está 100% atualizado no Modo B v4
    upgradeOutdatedModeB: true,  // Se true, atualiza produtos que têm Modo B antigo (S3 quebrado, boné com foto repetida, cor de outra loja, guia infantil antigo)
    batchCategory: "ALL",
    batchStatus: "SEM_DESCRICAO",
    batchLimit: 25
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
        ? `<span>🟢 Tampermonkey v${SCRIPT_VERSION} | Fila: ${idx + 1}/${q.length} (${active ? 'Ativa' : 'Pausada'})</span>`
        : `<span>🟢 Tampermonkey Conectado ao Banco BRK v${SCRIPT_VERSION} (6.242 itens auditados)</span>`;
    }
    updatePortalBadge();

    badge.onclick = () => {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      alert(`[Assistente BRK v${SCRIPT_VERSION} Status]\n\nFila no Tampermonkey: ${q.length} produtos\nÍndice Atual: ${q.length ? (idx + 1) : 0} de ${q.length}\nAutomação Ativa: ${active ? "SIM" : "NÃO"}\n\nFases 5 e 6 Ativas:\n• Fishing (Azul #0284c7) | Agro (Verde #15803d) | Motors (Laranja #ea580c)\n• Bonés e Chapéus com 4 fotos reais da própria galeria + CDN 200 OK\n• Tabelas de Medidas Masculino, Feminino Baby Look e Infantil por Idade (2 a 13 Anos | PP ao G2)`);
    };
    document.body.appendChild(badge);

    // Ponte Bidirecional: Receber Fila enviada pelo Portal (Botões "Enviar Lote" / "Enviar Selecionados")
    window.addEventListener("message", (event) => {
      const data = event.data;
      if (!data || data.type !== "BRK_LOAD_QUEUE" || !data.payload) return;
      const { items, storeKey, storeSlug, autoStart } = data.payload;
      if (!Array.isArray(items) || items.length === 0) return;

      setQueue(items);
      setQueueIndex(0);
      setAutomationActive(autoStart !== false);
      if (storeKey) GM_setValue(STORAGE_KEYS.LAST_STORE, storeKey);
      updatePortalBadge();

      const slug = storeSlug || (storeKey === "brk_agro" ? "brkagro" : storeKey === "brk_motors" ? "brkmotors25" : "brkfishing");
      const firstId = items[0].id;
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
    let countdownTimer = null;

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

    // Injetar Estilos Visuais do HUD, Modal de Preview e Pulso do Botão Salvar
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
        bottom: 20px;
        right: 20px;
        z-index: 999998;
        background: #090d16;
        color: #f1f5f9;
        border: 2px solid #0284c7;
        border-radius: 16px;
        padding: 15px 18px;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.7);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        min-width: 390px;
        max-width: 510px;
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
        color: #94a3b8;
        cursor: pointer;
        user-select: none;
      }
      .brk-hud-toggle input {
        accent-color: #0284c7;
        cursor: pointer;
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

    function isAlreadyModeBInEditor() {
      const currentHtml = getCurrentEditorHtml();
      return currentHtml.includes("<!-- BRK-MODO-B") || currentHtml.includes("brk-cap-description") || currentHtml.includes("brk-size-guide");
    }

    // Diagnóstico Inteligente Fase 5/6 do HTML atual no editor da Shopify
    function inspectEditorHealth(prod) {
      const currentHtml = getCurrentEditorHtml();
      if (!currentHtml || currentHtml.trim().length < 30) {
        return { state: "EMPTY", badge: "🔴 SEM DESCRIÇÃO NO EDITOR", reason: "Editor da Shopify está vazio." };
      }
      const hasModeB = currentHtml.includes("<!-- BRK-MODO-B") || currentHtml.includes("brk-cap-description") || currentHtml.includes("brk-size-guide");
      if (!hasModeB) {
        if (currentHtml.includes("use-brk-images-s3")) {
          return { state: "LEGACY_BROKEN", badge: "🔴 S3 QUEBRADO NO EDITOR", reason: "Descrição antiga com imagens AWS S3 (Erro 404)." };
        }
        return { state: "LEGACY", badge: "🟡 DESCRIÇÃO LEGADA", reason: "Ainda não possui o padrão oficial Modo B." };
      }

      // Já tem Modo B, mas vamos verificar se precisa de upgrade da Fase 5/6!
      const reasons = [];
      if (currentHtml.includes("use-brk-images-s3")) {
        reasons.push("Links AWS S3 404 (13-Tags/CAIXA)");
      }
      if (currentHtml.includes("eQxQuY7.jpg") && prod && prod.mode_b_html && !prod.mode_b_html.includes("eQxQuY7.jpg")) {
        reasons.push("Foto genérica repetida de boné");
      }
      if (currentHtml.includes("1 a 2 Anos")) {
        reasons.push("Tabela Infantil antiga (sem idade 2 a 13 Anos)");
      }
      // Contingência Anti-Duplicação da 1ª Foto na Descrição
      const editorImgMatches = Array.from(currentHtml.matchAll(/<img[^>]+src=["']([^"']+)["']/gi)).map(m => m[1].split("?")[0].toLowerCase());
      if (editorImgMatches.length > new Set(editorImgMatches).size) {
        reasons.push("Foto repetida na descrição");
      } else if (prod && Array.isArray(prod.cdn_images) && prod.cdn_images.length > 0 && editorImgMatches.length >= 2) {
        const officialRoots = new Set(prod.cdn_images.map(u => String(u).split("?")[0].toLowerCase()));
        const hasPurgedDup = editorImgMatches.some(u => u.includes("productonchannel") && !officialRoots.has(u));
        if (hasPurgedDup) {
          reasons.push("1ª foto duplicada pela Shopify no Ato 2 (corrigida pelo Modo B)");
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
          badge: "⚠️ MODO B DESATUALIZADO",
          reason: `Re-injeção Fase 6 recomendada: ${reasons.join(", ")}.`
        };
      }

      return {
        state: "UP_TO_DATE",
        badge: "✅ MODO B v4 ATUALIZADO",
        reason: `Descrição oficial sincronizada (${currentTheme.label}).`
      };
    }

    // =========================================================================
    // INJEÇÃO COMPATÍVEL COM REACT & TINYMCE NO EDITOR SHOPIFY POLARIS
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

    function highlightSaveButton(onSaveCallback) {
      const settings = getSettings();
      let attempts = 0;

      const tryHighlight = () => {
        const saveBtn = findSaveButton();
        if (saveBtn) {
          saveBtn.classList.add("brk-pulse-save-button");
          saveBtn.scrollIntoView({ behavior: "smooth", block: "nearest" });

          const handler = () => {
            saveBtn.classList.remove("brk-pulse-save-button");
            saveBtn.removeEventListener("click", handler);
            if (onSaveCallback) onSaveCallback();
          };
          saveBtn.addEventListener("click", handler);

          // Se Auto-Salvar estiver ativo nas configurações do HUD, clica automaticamente após 900ms
          if (settings.autoSave) {
            setTimeout(() => {
              if (!saveBtn.disabled) {
                console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Auto-Save ativo: clicando em Salvar automaticamente!`);
                saveBtn.click();
              }
            }, 900);
          }
          return true;
        }
        attempts++;
        if (attempts < 8) {
          setTimeout(tryHighlight, 350);
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

      const htmlBtn = findShowHtmlButton();
      let textarea = findDescriptionTextarea();

      // Se o textarea do modo HTML ainda não está visível e achamos o botão (<>), clicamos nele para abrir o modo HTML puro
      if (htmlBtn && (!textarea || textarea.offsetParent === null)) {
        console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Alternando editor para Modo Código HTML (<>)...`);
        htmlBtn.click();
      }

      setTimeout(() => {
        textarea = findDescriptionTextarea();

        if (textarea && textarea.offsetParent !== null) {
          appendBackup(currentProductId, location.pathname, textarea.value);
          setReactInputValue(textarea, htmlContent);
          console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] HTML Modo B injetado com sucesso no Textarea HTML!`);

          setTimeout(() => {
            highlightSaveButton(() => {
              console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Produto salvo!`);
              handleAfterSave();
            });
          }, 250);

          renderHudProductMode(
            activeLoadedProduct,
            "✨ Modo B v4 Injetado com Sucesso!",
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres (${currentTheme.label}). ${getSettings().autoSave ? 'Salvando automaticamente...' : "Clique em 'Salvar' (verde pulsando)."}`
          );
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
          console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] HTML Modo B injetado direto no iframe TinyMCE!`);

          highlightSaveButton(() => handleAfterSave());
          renderHudProductMode(
            activeLoadedProduct,
            "✨ Injetado no Editor Visual (TinyMCE)!",
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres (${currentTheme.label}). ${getSettings().autoSave ? 'Salvando automaticamente...' : "Clique em 'Salvar' no topo."}`
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
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres no editor visual. Clique em 'Salvar' no topo.`
          );
        } else {
          try { GM_setClipboard(htmlContent); } catch(e) {}
          alert("O HTML oficial já foi copiado para sua área de transferência! Clique no ícone '<>' do editor da Shopify e pressione Ctrl+V.");
        }
      }, 650);

      return true;
    }

    function handleAfterSave() {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();

      if (active && q.length > 0 && idx < q.length - 1) {
        startCountdownToNext();
      } else if (active && q.length > 0 && idx >= q.length - 1) {
        setAutomationActive(false);
        setQueueIndex(0);
        alert(`🎉 Parabéns! O lote de ${q.length} produtos da ${currentStoreName} foi completamente finalizado com sucesso!`);
        renderHudListMode();
      }
    }

    function startCountdownToNext() {
      const settings = getSettings();
      let count = settings.delaySeconds || 4;
      const q = getQueue();
      const nextIdx = getQueueIndex() + 1;
      const nextItem = q[nextIdx];

      if (!nextItem) {
        setAutomationActive(false);
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
            `⏱️ Salvo! Avançando em ${count}s...`,
            `Próximo (${nextIdx + 1}/${q.length}): ${nextItem.master_sku || ''} - ${(nextItem.title || '').slice(0, 35)}...`
          );
          count--;
        }
      }, 1000);
    }

    const injectDescriptionIntoShopify = injectModoBIntoEditor;
    const advanceToNextProduct = startCountdownToNext;

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
      if (prod?.status === "SEM_DESCRICAO") statusBadgeClass = "brk-badge-empty";
      else if (prod?.status === "IMAGENS_QUEBRADAS") statusBadgeClass = "brk-badge-broken";

      const imgCount = prod ? (prod.gallery || prod.cdn_images || []).length : 0;

      let editorBadgeStyle = "background:#1e293b;color:#cbd5e1;";
      if (editorHealth.state === "UP_TO_DATE") editorBadgeStyle = "background:#065f46;color:#6ee7b7;";
      else if (editorHealth.state === "OUTDATED_MODE_B") editorBadgeStyle = "background:#92400e;color:#fde68a;";
      else if (editorHealth.state === "EMPTY" || editorHealth.state === "LEGACY_BROKEN") editorBadgeStyle = "background:#7f1d1d;color:#fecaca;";

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;">
            <span style="font-size:15px;">🟢</span>
            <strong style="color:${currentTheme.light};font-size:13px;">BANCO BRK v${SCRIPT_VERSION}</strong>
            <span style="${editorBadgeStyle}font-size:10px;font-weight:800;padding:2px 7px;border-radius:9999px;">${editorHealth.badge}</span>
          </div>
          <span style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};font-size:10px;font-weight:800;padding:2px 8px;border-radius:9999px;">
            ${inQueue ? `Fila ${idx + 1}/${q.length} • ${currentStoreName}` : `${currentStoreName} (${currentTheme.label})`}
          </span>
        </div>

        <div style="margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;flex-wrap:wrap;">
            <span style="font-weight:800;color:#f8fafc;font-size:14px;">${prod ? (prod.master_sku || 'Sem SKU') : 'Carregando...'}</span>
            ${prod ? `<span class="brk-badge-status ${statusBadgeClass}">${prod.status}</span>` : ''}
            ${prod ? `<span class="brk-badge-meta">📂 ${prod.category || 'Geral'}</span>` : ''}
            ${prod ? `<span class="brk-badge-meta">📸 ${imgCount} fotos CDN</span>` : ''}
            ${prod && prod.delivery_time ? `<span class="brk-badge-meta">🚚 ${prod.delivery_time}</span>` : ''}
          </div>
          <div style="font-size:12px;color:#cbd5e1;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:460px;">
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

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:10px;">
          <div style="font-weight:700;color:${currentTheme.light};font-size:12px;">${statusTitle || "Pronto para Injeção"}</div>
          <div style="font-size:11px;color:#94a3b8;line-height:1.4;">${statusSub || editorHealth.reason}</div>
          ${prod && prod.mode_b_html ? `
            <div style="margin-top:6px;font-size:11px;color:#4ade80;font-weight:700;display:flex;align-items:center;justify-content:space-between;border-top:1px solid #1e293b;padding-top:4px;">
              <span>⭐ Modo B Oficial: ${(prod.mode_b_html.length).toLocaleString('pt-BR')} chars</span>
              <span style="color:#94a3b8;font-weight:600;">${prod.archetype_name || '3 Atos + Ficha Técnica'}</span>
            </div>
          ` : ''}
        </div>

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;padding:0 2px;flex-wrap:wrap;gap:6px;">
          <label class="brk-hud-toggle" title="Clica automaticamente no botão Salvar da Shopify 1s após injetar o Modo B">
            <input type="checkbox" id="brk-chk-autosave" ${settings.autoSave ? 'checked' : ''} style="accent-color:${currentTheme.primary};" />
            <span>Auto-Salvar</span>
          </label>
          <label class="brk-hud-toggle" title="Durante um lote, pula produtos que já têm Modo B v4 100% atualizado">
            <input type="checkbox" id="brk-chk-skip-done" ${settings.skipAlreadyModeB ? 'checked' : ''} style="accent-color:${currentTheme.primary};" />
            <span>Pular v4 OK</span>
          </label>
          <label class="brk-hud-toggle" title="Durante um lote, re-injeta automaticamente se detectar Modo B antigo (S3 404, boné repetido, cor errada ou guia infantil antigo)">
            <input type="checkbox" id="brk-chk-upgrade-legacy" ${settings.upgradeOutdatedModeB ? 'checked' : ''} style="accent-color:${currentTheme.primary};" />
            <span>Atualizar Antigos</span>
          </label>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          <button id="brk-btn-inject" class="brk-hud-btn brk-hud-btn-primary" style="background:${currentTheme.primary};border-color:${currentTheme.primaryHover};" title="Injeta a narrativa completa Modo B v4 no editor HTML">
            ⚡ Injetar Modo B
          </button>
          <button id="brk-btn-preview" class="brk-hud-btn" title="Abre uma janela visual dentro do Shopify Admin mostrando como a descrição Modo B ficará na loja">
            👁️ Preview
          </button>
          <button id="brk-btn-copy" class="brk-hud-btn" title="Copia o HTML oficial para a área de transferência">
            📋 Copiar HTML
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
            <button id="brk-btn-start-queue-25" class="brk-hud-btn brk-hud-btn-success">
              ▶️ Lote 25
            </button>
          `}
        </div>
      `;

      // Toggles de configuração
      const chkAutoSave = document.getElementById("brk-chk-autosave");
      if (chkAutoSave) chkAutoSave.onchange = (e) => saveSettings({ autoSave: e.target.checked });

      const chkSkipDone = document.getElementById("brk-chk-skip-done");
      if (chkSkipDone) chkSkipDone.onchange = (e) => saveSettings({ skipAlreadyModeB: e.target.checked });

      const chkUpgradeLegacy = document.getElementById("brk-chk-upgrade-legacy");
      if (chkUpgradeLegacy) chkUpgradeLegacy.onchange = (e) => saveSettings({ upgradeOutdatedModeB: e.target.checked });

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
          renderHudProductMode(prod, "📋 HTML Modo B Copiado!", `Copiados ${(html.length).toLocaleString('pt-BR')} caracteres da narrativa oficial (${currentTheme.label}). Cole com Ctrl+V no campo <> do editor.`);
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
                `Galeria atualizada (${newCount} fotos únicas) e Modo B recompilado (${currentTheme.label}). Clique em 'Injetar Modo B'!`
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
          renderHudProductMode(prod, "⏹️ Lote Cancelado", "Fila esvaziada. Você pode operar individualmente.");
        };
      }

      const btnStart25 = document.getElementById("brk-btn-start-queue-25");
      if (btnStart25) {
        btnStart25.onclick = () => startQueueFromDatabase("SEM_DESCRICAO", 25, "ALL");
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

      hud.style.borderColor = currentTheme.primary;

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">🟢</span>
            <strong style="color:${currentTheme.light};font-size:13px;">BANCO DE DADOS BRK v${SCRIPT_VERSION}</strong>
          </div>
          <span style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};font-size:10px;font-weight:800;padding:2px 8px;border-radius:9999px;">
            ${currentStoreName} • ${currentTheme.label}
          </span>
        </div>

        <div style="margin-bottom:10px;font-size:12px;color:#cbd5e1;line-height:1.5;">
          ${stats ? `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;">
              <div>📦 Catálogo Loja: <strong>${stats.total_products}</strong></div>
              <div style="color:#4ade80;">✅ Saudáveis: <strong>${stats.healthy_count}</strong></div>
              <div style="color:#f87171;">⚠️ Sem Descrição: <strong>${stats.sem_descricao_count}</strong></div>
              <div style="color:#fbbf24;">🖼️ Fotos Quebradas: <strong>${stats.imagens_quebradas_count}</strong></div>
            </div>
          ` : 'Conectando à API oficial Vercel (6.242 produtos auditados)...'}
        </div>

        ${q.length > 0 ? `
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:10px;">
            <div style="font-weight:700;color:${currentTheme.light};font-size:12px;">Fila Ativa: Item ${idx + 1} de ${q.length}</div>
            <div style="font-size:11px;color:#94a3b8;">Status: ${active ? 'Em andamento' : 'Pausado'}</div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
            <button id="brk-btn-resume-queue" class="brk-hud-btn brk-hud-btn-primary" style="background:${currentTheme.primary};border-color:${currentTheme.primaryHover};">
              ▶️ Continuar Lote (${idx + 1}/${q.length})
            </button>
            <button id="brk-btn-clear-queue" class="brk-hud-btn brk-hud-btn-danger">
              ⏹️ Limpar Fila
            </button>
          </div>
        ` : `
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:9px 11px;margin-bottom:10px;">
            <div style="font-weight:700;color:${currentTheme.light};font-size:11px;margin-bottom:6px;">🎯 Seletor de Lote por Coleção & Status (Fase 6)</div>
            <div style="display:grid;grid-template-columns:1.2fr 1fr 0.6fr;gap:6px;margin-bottom:8px;">
              <select id="brk-sel-category" class="brk-hud-select" title="Filtrar por Coleção/Categoria">
                <option value="ALL" ${settings.batchCategory === 'ALL' ? 'selected' : ''}>📂 Todas as Coleções</option>
                <option value="bones_chapeus" ${settings.batchCategory === 'bones_chapeus' ? 'selected' : ''}>🧢 Bonés & Chapéus</option>
                <option value="camisas" ${settings.batchCategory === 'camisas' ? 'selected' : ''}>👕 Camisas (UV/Algodão/Botão)</option>
                <option value="calcas" ${settings.batchCategory === 'calcas' ? 'selected' : ''}>👖 Calças & Bermudas</option>
                <option value="corta_vento" ${settings.batchCategory === 'corta_vento' ? 'selected' : ''}>🧥 Corta-Vento & Jaquetas</option>
                <option value="infantil" ${settings.batchCategory === 'infantil' ? 'selected' : ''}>🧒 Linha Infantil (2 a 13 Anos)</option>
                <option value="feminino" ${settings.batchCategory === 'feminino' ? 'selected' : ''}>👚 Linha Feminina (Baby Look)</option>
              </select>
              <select id="brk-sel-status" class="brk-hud-select" title="Filtrar por Status">
                <option value="SEM_DESCRICAO" ${settings.batchStatus === 'SEM_DESCRICAO' ? 'selected' : ''}>⚠️ Sem Descrição</option>
                <option value="IMAGENS_QUEBRADAS" ${settings.batchStatus === 'IMAGENS_QUEBRADAS' ? 'selected' : ''}>🖼️ Fotos Quebradas</option>
                <option value="TODOS" ${settings.batchStatus === 'TODOS' ? 'selected' : ''}>🔄 Todos (Atualizar v4)</option>
              </select>
              <select id="brk-sel-limit" class="brk-hud-select" title="Quantidade de Produtos no Lote">
                <option value="25" ${Number(settings.batchLimit) === 25 ? 'selected' : ''}>25 itens</option>
                <option value="50" ${Number(settings.batchLimit) === 50 ? 'selected' : ''}>50 itens</option>
                <option value="100" ${Number(settings.batchLimit) === 100 ? 'selected' : ''}>100 itens</option>
              </select>
            </div>
            <button id="brk-btn-start-custom-batch" class="brk-hud-btn brk-hud-btn-primary" style="width:100%;justify-content:center;background:${currentTheme.primary};border-color:${currentTheme.primaryHover};">
              🚀 Iniciar Lote Filtrado na ${currentStoreName}
            </button>
          </div>

          <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
            <button id="brk-btn-fetch-empty-25" class="brk-hud-btn" title="Inicia lote rápido de 25 produtos sem descrição">
              ▶️ Lote 25 (Sem Descrição)
            </button>
            <button id="brk-btn-fetch-caps-50" class="brk-hud-btn" title="Inicia lote com todos os Bonés e Chapéus para atualizar com as 4 fotos reais da galeria">
              🧢 Lote Bonés & Chapéus
            </button>
            <button id="brk-btn-fetch-broken-25" class="brk-hud-btn" title="Inicia lote de 25 produtos com fotos quebradas">
              🖼️ Lote 25 (Quebradas)
            </button>
          </div>
        `}
      `;

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
          const st = document.getElementById("brk-sel-status")?.value || "SEM_DESCRICAO";
          const lim = parseInt(document.getElementById("brk-sel-limit")?.value || "25", 10);
          saveSettings({ batchCategory: cat, batchStatus: st, batchLimit: lim });
          startQueueFromDatabase(st, lim, cat);
        };
      }

      const btnFetchEmpty = document.getElementById("brk-btn-fetch-empty-25");
      if (btnFetchEmpty) {
        btnFetchEmpty.onclick = () => startQueueFromDatabase("SEM_DESCRICAO", 25, "ALL");
      }

      const btnFetchCaps = document.getElementById("brk-btn-fetch-caps-50");
      if (btnFetchCaps) {
        btnFetchCaps.onclick = () => startQueueFromDatabase("TODOS", 50, "bones_chapeus");
      }

      const btnFetchBroken = document.getElementById("brk-btn-fetch-broken-25");
      if (btnFetchBroken) {
        btnFetchBroken.onclick = () => startQueueFromDatabase("IMAGENS_QUEBRADAS", 25, "ALL");
      }
    }

    // =========================================================================
    // INICIAR FILA REAL BUSCADA DIRETAMENTE DO BANCO DE DADOS
    // =========================================================================
    async function startQueueFromDatabase(statusFilter, limit = 25, categoryFilter = "ALL") {
      hud.innerHTML = `
        <div style="padding:10px;text-align:center;">
          <div style="font-size:18px;margin-bottom:8px;">⏳</div>
          <strong style="color:${currentTheme.light};">Consultando Banco de Dados BRK...</strong>
          <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Buscando até ${limit} produtos (Status: ${statusFilter} | Coleção: ${categoryFilter}) na loja ${currentStoreName}...</div>
        </div>
      `;

      try {
        const queryUrl = `/api/product_db?store=${currentStoreKey}&action=queue&status=${encodeURIComponent(statusFilter)}&category=${encodeURIComponent(categoryFilter)}&limit=${limit}`;
        const res = await fetchFromBRKDatabase(queryUrl);
        if (!res.success || !res.items || res.items.length === 0) {
          alert(`Nenhum produto encontrado para o filtro selecionado (Status: ${statusFilter}, Coleção: ${categoryFilter}) na loja ${currentStoreName}.`);
          initAdmin();
          return;
        }

        setQueue(res.items);
        setQueueIndex(0);
        setAutomationActive(true);

        const firstProduct = res.items[0];
        console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Lote de ${res.items.length} produtos carregado. Primeiro: ID ${firstProduct.id} (${firstProduct.master_sku})`);

        hud.innerHTML = `
          <div style="padding:10px;text-align:center;">
            <div style="font-size:18px;margin-bottom:8px;">🚀</div>
            <strong style="color:#22c55e;">Lote de ${res.items.length} Produtos Carregado!</strong>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Abrindo primeiro produto: ${firstProduct.master_sku}...</div>
          </div>
        `;

        setTimeout(() => {
          location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${firstProduct.id}`;
        }, 900);

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
        renderHudProductMode(null, "Consultando Banco BRK...", `Buscando produto ID ${currentProductId} (${currentStoreName})...`);

        try {
          const hints = extractPageHints();
          const query = `/api/product_db?store=${currentStoreKey}&id=${currentProductId}` +
            (hints.handle ? `&handle=${encodeURIComponent(hints.handle)}` : "") +
            (hints.sku ? `&sku=${encodeURIComponent(hints.sku)}` : "");

          const res = await fetchFromBRKDatabase(query);
          if (res.success && res.product) {
            activeLoadedProduct = res.product;
            console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Produto carregado do banco:`, activeLoadedProduct.master_sku);

            const q = getQueue();
            const idx = getQueueIndex();
            const inQueue = q.length > 0 && q[idx] && String(q[idx].id) === String(currentProductId);
            const active = isAutomationActive();
            const settings = getSettings();
            const editorHealth = inspectEditorHealth(activeLoadedProduct);

            if (inQueue && active) {
              // Se o produto já possui Modo B v4 100% atualizado (sem S3 quebrado, sem foto de boné repetida, com a cor certa da loja) e skipAlreadyModeB está ativo, pula!
              const shouldSkip = settings.skipAlreadyModeB && (
                editorHealth.state === "UP_TO_DATE" ||
                (editorHealth.state === "OUTDATED_MODE_B" && !settings.upgradeOutdatedModeB)
              );

              if (shouldSkip) {
                renderHudProductMode(
                  activeLoadedProduct,
                  "✅ Produto Já Atualizado no Modo B v4!",
                  "Pulando automaticamente para o próximo item da fila..."
                );
                setTimeout(() => startCountdownToNext(), 800);
                return;
              }

              renderHudProductMode(
                activeLoadedProduct,
                editorHealth.state === "OUTDATED_MODE_B" ? "🔄 Atualizando Modo B Antigo para v4..." : "⚡ Modo Assistido Ativo",
                editorHealth.state === "OUTDATED_MODE_B" ? editorHealth.reason : "Injetando descrição Modo B oficial automaticamente..."
              );
              setTimeout(() => {
                injectModoBIntoEditor(activeLoadedProduct.mode_b_html);
              }, 1100);
            } else {
              let titleMsg = "Produto Identificado no Banco";
              if (editorHealth.state === "UP_TO_DATE") titleMsg = "✅ Modo B v4 Sincronizado neste Produto";
              else if (editorHealth.state === "OUTDATED_MODE_B") titleMsg = "⚠️ Atualização Fase 6 Disponível!";
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
          const stats = await fetchFromBRKDatabase(`/api/product_db?store=${currentStoreKey}&action=stats`);
          if (stats.success) {
            renderHudListMode(stats);
          }
        } catch(e) {
          console.warn(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Não foi possível carregar estatísticas:`, e);
        }
      }
    }

    // Observador de rota SPA do Shopify Admin (detecta cliques entre produtos sem reload de página)
    setInterval(() => {
      if (location.pathname !== lastObservedPath) {
        if (countdownTimer) clearInterval(countdownTimer);
        lastObservedPath = location.pathname;
        setTimeout(initAdmin, 500);
      }
    }, 500);

    // Iniciar após pequeno delay para o DOM do Shopify Admin estabilizar
    setTimeout(initAdmin, 1000);
  }

})();
