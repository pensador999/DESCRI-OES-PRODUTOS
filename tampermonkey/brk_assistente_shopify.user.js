// ==UserScript==
// @name         BRK Assistente de Descrições Shopify (Mini-Dashboard v6.4.0 Cockpit)
// @namespace    https://1025-ten.vercel.app/
// @version      6.4.0
// @description  Mini-Dashboard Profissional in-screen para Shopify Admin com KPIs em tempo real, diversidade cromática RGB de iscas artificiais (zero 2-capa ou mesma cor repetida), distinção Estúdio 1..4 vs Capa Humanizada e Piloto Automático sem avisos legados.
// @author       BRK Group & DeepMind Pair
// @updateURL    https://1025-ten.vercel.app/tampermonkey/brk_assistente_shopify.user.js
// @downloadURL  https://1025-ten.vercel.app/tampermonkey/brk_assistente_shopify.user.js
// @match        https://admin.shopify.com/store/*/products*
// @match        https://admin.shopify.com/store/*
// @match        https://1025-ten.vercel.app/*
// @match        https://descricoes.vercel.app/*
// @match        https://www.brkfishing.com.br/collections/*
// @match        https://www.brkagro.com.br/collections/*
// @match        https://www.brkmotors.com.br/collections/*
// @match        http://localhost:*/*
// @match        http://127.0.0.1:*/*
// @connect      1025-ten.vercel.app
// @connect      descricoes.vercel.app
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
// @grant        unsafeWindow
// @run-at       document-idle
// ==/UserScript==

(function() {
  'use strict';

  // Configuração da API do Banco de Dados BRK (6.409 produtos auditados nas 3 lojas)
  const API_BASE = "https://1025-ten.vercel.app";
  const SCRIPT_VERSION = "6.4.0";

  const STORAGE_KEYS = {
    QUEUE: "BRK_AUTOSYNC_QUEUE",
    INDEX: "BRK_AUTOSYNC_INDEX",
    ACTIVE: "BRK_AUTOSYNC_ACTIVE",
    BACKUP: "BRK_AUTOSYNC_BACKUP",
    SETTINGS: "BRK_AUTOSYNC_SETTINGS",
    LAST_STORE: "BRK_LAST_STORE",
    COMPLIANT_IDS: "BRK_COMPLIANT_IDS_V64"
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
    upgradeOutdatedModeB: true,  // Atualiza produtos que têm Modo B com violação residual
    pauseOnMediaError: false,    // Se true, pausa o Auto-Save quando o produto tiver variante sem foto (image_id=null) ou foto duplicada para ajuste manual
    batchCategory: "ALL",
    batchStatus: "PRIORIDADE_CRITICA",
    batchLimit: 50,
    customCollection: "",
    minimized: false,
    activeTab: "priorities"
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
  // 1. LÓGICA NO PORTAL (1025-ten.vercel.app) E NAS PÁGINAS DE COLEÇÃO DAS LOJAS
  // =========================================================================
  const isStorefrontCollection = (
    location.hostname.includes("brkfishing.com.br") ||
    location.hostname.includes("brkagro.com.br") ||
    location.hostname.includes("brkmotors.com.br")
  ) && location.pathname.includes("/collections/");

  if (location.hostname === "1025-ten.vercel.app" || location.hostname === "descricoes.vercel.app" || location.hostname === "localhost" || location.hostname === "127.0.0.1" || isStorefrontCollection) {
    console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Conectado silenciosamente ao Portal BRK.`);
    window.__BRK_TAMPERMONKEY_INSTALLED = true;
    document.documentElement.setAttribute("data-tampermonkey-active", "true");

    // Garante que qualquer aviso flutuante antigo (#brk-tm-portal-badge) seja removido da tela
    const oldBadge = document.getElementById("brk-tm-portal-badge");
    if (oldBadge) oldBadge.remove();

    // Ponte Bidirecional Silenciosa: Receber Fila enviada pelo Portal
    window.addEventListener("message", (event) => {
      const data = event.data;
      if (!data || data.type !== "BRK_LOAD_QUEUE" || !data.payload) return;
      const { items, storeKey, storeSlug, autoStart, forceAll, statusFilter } = data.payload;
      if (!Array.isArray(items) || items.length === 0) return;

      let finalItems = items;
      if (forceAll) {
        GM_setValue(STORAGE_KEYS.COMPLIANT_IDS, "[]");
        saveSettings({
          autoPilot: true,
          autoSave: true,
          skipAlreadyModeB: false,
          pauseOnMediaError: statusFilter === "CRITICOS_FOTOS_CORES"
        });
      } else {
        const filteredItems = items.filter(it => !it.is_mode_b_compliant && !isProductMarkedCompliant(it.id, it.master_sku || it.sku));
        finalItems = filteredItems.length > 0 ? filteredItems : items;
        saveSettings({ autoPilot: true, autoSave: true });
      }

      setQueue(finalItems);
      setQueueIndex(0);
      setAutomationActive(autoStart !== false);
      if (storeKey) GM_setValue(STORAGE_KEYS.LAST_STORE, storeKey);

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
  // 2. LÓGICA NO SHOPIFY ADMIN (admin.shopify.com/store/*)
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

    // Neutralizador Definitivo de 'beforeunload' via unsafeWindow + Nonce CSP ("Sair do site? É possível que as alterações feitas não sejam salvas.")
    function disarmBeforeUnload() {
      const targets = [window];
      try {
        if (typeof unsafeWindow !== "undefined" && unsafeWindow && unsafeWindow !== window) {
          targets.push(unsafeWindow);
        }
      } catch (e) {}

      for (const w of targets) {
        try {
          w.onbeforeunload = null;
          Object.defineProperty(w, "onbeforeunload", {
            configurable: true,
            get: function() { return null; },
            set: function() {}
          });
        } catch (e) {}

        try {
          w.addEventListener("beforeunload", function(e) {
            e.stopImmediatePropagation();
          }, true);
        } catch (e) {}

        try {
          if (w.Event && w.Event.prototype && !w.Event.prototype.__brkPatchedBeforeUnload) {
            const origPrevent = w.Event.prototype.preventDefault;
            w.Event.prototype.preventDefault = function() {
              if (this && this.type === "beforeunload") return;
              return origPrevent.apply(this, arguments);
            };
            w.Event.prototype.__brkPatchedBeforeUnload = true;
          }
        } catch (e) {}

        try {
          if (w.EventTarget && w.EventTarget.prototype && !w.EventTarget.prototype.__brkPatchedAddListener) {
            const origAdd = w.EventTarget.prototype.addEventListener;
            w.EventTarget.prototype.addEventListener = function(type, listener, options) {
              if (String(type).toLowerCase() === "beforeunload") return;
              return origAdd.call(this, type, listener, options);
            };
            w.EventTarget.prototype.__brkPatchedAddListener = true;
          }
        } catch (e) {}

        try {
          const protos = [w.BeforeUnloadEvent && w.BeforeUnloadEvent.prototype, w.Event && w.Event.prototype].filter(Boolean);
          for (const proto of protos) {
            const desc = Object.getOwnPropertyDescriptor(proto, "returnValue");
            if (desc && desc.set) {
              Object.defineProperty(proto, "returnValue", {
                configurable: true,
                get: function() {
                  if (this && this.type === "beforeunload") return "";
                  return desc.get ? desc.get.call(this) : undefined;
                },
                set: function(val) {
                  if (this && this.type === "beforeunload") return;
                  if (desc.set) desc.set.call(this, val);
                }
              });
            }
          }
        } catch (e) {}
      }

      try {
        if (!document.getElementById("brk-disarm-beforeunload-script")) {
          const s = document.createElement("script");
          s.id = "brk-disarm-beforeunload-script";
          const nonceEl = document.querySelector("script[nonce]");
          if (nonceEl && (nonceEl.nonce || nonceEl.getAttribute("nonce"))) {
            s.setAttribute("nonce", nonceEl.nonce || nonceEl.getAttribute("nonce"));
          }
          s.textContent = `
            (function() {
              try {
                window.onbeforeunload = null;
                Object.defineProperty(window, 'onbeforeunload', { configurable: true, get: function() { return null; }, set: function() {} });
                const origPrevent = Event.prototype.preventDefault;
                Event.prototype.preventDefault = function() {
                  if (this && this.type === 'beforeunload') return;
                  return origPrevent.apply(this, arguments);
                };
                const origAdd = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {
                  if (String(type).toLowerCase() === 'beforeunload') return;
                  return origAdd.call(this, type, listener, options);
                };
                const protos = [window.BeforeUnloadEvent && window.BeforeUnloadEvent.prototype, Event.prototype].filter(Boolean);
                for (const proto of protos) {
                  const desc = Object.getOwnPropertyDescriptor(proto, 'returnValue');
                  if (desc && desc.set) {
                    Object.defineProperty(proto, 'returnValue', {
                      configurable: true,
                      get: function() { return (this && this.type === 'beforeunload') ? '' : (desc.get ? desc.get.call(this) : undefined); },
                      set: function(val) { if (this && this.type === 'beforeunload') return; if (desc.set) desc.set.call(this, val); }
                    });
                  }
                }
                window.addEventListener('beforeunload', function(e) { e.stopImmediatePropagation(); }, true);
              } catch (err) {}
            })();
          `;
          (document.head || document.documentElement).appendChild(s);
        }
      } catch (e) {}
    }

    disarmBeforeUnload();

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
        background: rgba(9, 13, 22, 0.96);
        color: #f1f5f9;
        border: 1.5px solid #0284c7;
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.06) inset;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
        font-size: 12.5px;
        min-width: 430px;
        max-width: 520px;
        backdrop-filter: blur(16px);
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      }
      #brk-tm-hud.brk-hud-minimized {
        min-width: auto !important;
        max-width: 390px !important;
        padding: 8px 13px !important;
        border-radius: 9999px !important;
      }
      .brk-icon-btn {
        background: #1e293b;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        width: 24px;
        height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 800;
        cursor: pointer;
        transition: all 0.15s;
      }
      .brk-icon-btn:hover {
        background: #334155;
        color: #ffffff;
      }
      .brk-progress-track {
        width: 100%;
        height: 6px;
        background: #1e293b;
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 5px;
      }
      .brk-progress-fill {
        height: 100%;
        border-radius: 9999px;
        transition: width 0.4s ease;
      }
      .brk-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        margin-bottom: 10px;
      }
      .brk-kpi-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 7px 8px;
        cursor: pointer;
        transition: all 0.16s ease;
        text-align: left;
      }
      .brk-kpi-card:hover {
        background: #162036;
        border-color: #475569;
        transform: translateY(-1px);
      }
      .brk-kpi-val {
        font-size: 15px;
        font-weight: 800;
        line-height: 1.15;
        font-variant-numeric: tabular-nums;
      }
      .brk-kpi-lbl {
        font-size: 9.5px;
        font-weight: 700;
        color: #94a3b8;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .brk-tab-bar {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 4px;
        background: #060911;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        margin-bottom: 10px;
      }
      .brk-tab-btn {
        background: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 7px;
        padding: 6px 8px;
        font-size: 11px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
      }
      .brk-tab-btn:hover {
        color: #e2e8f0;
      }
      .brk-tab-btn.active {
        background: #1e293b;
        color: #ffffff;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
      }
      .brk-priority-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
      }
      .brk-priority-btn {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 9px;
        padding: 8px 10px;
        color: #f1f5f9;
        font-size: 11px;
        font-weight: 700;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        transition: all 0.16s;
        text-align: left;
      }
      .brk-priority-btn:hover {
        background: #1e293b;
        border-color: #475569;
      }
      .brk-priority-count {
        background: #1e293b;
        color: #cbd5e1;
        font-size: 10px;
        font-weight: 800;
        padding: 1px 6px;
        border-radius: 9999px;
        flex-shrink: 0;
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
        font-size: 11.5px;
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
        max-height: 165px;
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
        padding: 5px 7px;
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
      if (/troca descomplicada|dinheiro de volta/i.test(currentHtml)) {
        reasons.push("Rodapé antigo com 'Troca Descomplicada / Satisfação garantida ou seu dinheiro de volta'");
      }
      if (/troca fácil/i.test(currentHtml) || currentHtml.includes('<div class="brk-desc-trust-bar"></div>')) {
        reasons.push("Selo antigo 'Troca Fácil BRK' / barra vazia (atualizar para Qualidade Oficial BRK)");
      }
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
      // Contingência Anti-Duplicação da 1ª Foto na Descrição e Validação Cirúrgica do Ato 3 contra o HTML Oficial
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

      // Verificar se o Ato 3 está com imagem divergente da seleção oficial compilada em prod.mode_b_html
      const isApparelProd = /camisa|camiseta|fusion|hyb|armorx|cax|segunda pele|raglan|cortavento|jaqueta/i.test(titleAndSku);
      if (isApparelProd && prod && prod.mode_b_html && editorImgMatches.length >= 3) {
        const expectedImgs = Array.from(prod.mode_b_html.matchAll(/<img[^>]+src=["']([^"']+)["']/gi))
          .map(m => m[1].split("?")[0].toLowerCase())
          .filter(u => !u.endsWith(".svg"));
        if (expectedImgs.length >= 3 && editorImgMatches[2] !== expectedImgs[2]) {
          reasons.push("Imagem de Costas/Perspectiva Traseira no Ato 3 (atualizar para imagem 3/4 Frontal oficial)");
        }
      }

      // Verificar se a Isca Artificial ou Equipamento está com 2-capa ou variações de cores repetidas em relação ao prod.mode_b_html oficial
      const isLureOrEquip = /isca|jig|frog|sapinho|vara|caixa de pesca/i.test(titleAndSku) && !/boné|bone|copo|bandana|faca|camisa/i.test(titleAndSku);
      if (isLureOrEquip && prod && prod.mode_b_html && editorImgMatches.length >= 2) {
        const expectedImgs = Array.from(prod.mode_b_html.matchAll(/<img[^>]+src=["']([^"']+)["']/gi))
          .map(m => m[1].split("?")[0].toLowerCase())
          .filter(u => !u.endsWith(".svg"));
        if (expectedImgs.length >= 2 && editorImgMatches.slice(0, expectedImgs.length).join("|") !== expectedImgs.join("|")) {
          reasons.push("Isca/Equipamento com foto da mesma cor repetida (2-capa / variação similar) — atualizar para variações de cores distintas");
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
      element.focus();
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
      try { element.blur(); } catch (e) {}
    }

    function collectAllCandidateButtons() {
      const list = Array.from(document.querySelectorAll("button, [role='button'], ui-save-bar button"));
      const customBars = Array.from(document.querySelectorAll("ui-save-bar, s-button"));
      for (const el of customBars) {
        if (el.shadowRoot) {
          list.push(...Array.from(el.shadowRoot.querySelectorAll("button, [role='button']")));
        }
      }
      return list;
    }

    function findSaveButton() {
      const buttons = collectAllCandidateButtons();
      return buttons.find(b => {
        if (b.disabled || b.getAttribute("aria-disabled") === "true" || b.getAttribute("aria-busy") === "true") return false;
        const text = (b.innerText || b.textContent || "").trim().toLowerCase();
        const aria = (b.getAttribute("aria-label") || "").trim().toLowerCase();
        return text === "salvar" || text === "save" || aria === "salvar" || aria === "save";
      }) || null;
    }

    function findBusySaveButton() {
      const buttons = collectAllCandidateButtons();
      return buttons.find(b => {
        const text = (b.innerText || b.textContent || "").trim().toLowerCase();
        const aria = (b.getAttribute("aria-label") || "").trim().toLowerCase();
        const isSaveLabel = text === "salvar" || text === "save" || aria === "salvar" || aria === "save";
        const isBusy = b.getAttribute("aria-busy") === "true" || b.className.includes("loading") || b.className.includes("Spinner");
        return isSaveLabel && isBusy;
      }) || null;
    }

    function hasUnsavedChangesBanner() {
      const bodyText = document.body.innerText || "";
      return /alterações não salvas|unsaved changes/i.test(bodyText);
    }

    // Aguarda a Shopify concluir 100% a requisição de salvamento antes de avançar para o próximo produto
    function waitForShopifySaveComplete(onComplete) {
      if (saveCompletionTimer) clearInterval(saveCompletionTimer);
      let checks = 0;
      let retriedClick = false;

      saveCompletionTimer = setInterval(() => {
        checks++;
        const activeSaveBtn = findSaveButton();
        const busySaveBtn = findBusySaveButton();
        const unsavedBanner = hasUnsavedChangesBanner();
        const bodyText = document.body.innerText || "";
        const hasToast = /produto salvo|product saved|alterações salvas/i.test(bodyText);

        // Se após ~1.6s o botão Salvar ainda estiver habilitado (ex: React demorou a sincronizar o blur), clica novamente!
        if (activeSaveBtn && checks >= 5 && !retriedClick) {
          retriedClick = true;
          try {
            if (document.activeElement && document.activeElement !== document.body) {
              document.activeElement.blur();
            }
            console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] 🔄 Reforçando clique no botão Salvar...`);
            activeSaveBtn.click();
          } catch (e) {}
          return;
        }

        // Critério real de salvamento concluído:
        // 1) Apareceu o Toast "Produto salvo" E não há botão em loading (busySaveBtn)
        // 2) Ou já passaram pelo menos 4 checagens (1.4s) e não há botão Salvar ativo, nem botão ocupando spinner, nem barra "Alterações não salvas"
        // 3) Timeout máximo de segurança após 22 checagens (~7.7s)
        const isCleanlySaved = (!activeSaveBtn && !busySaveBtn && !unsavedBanner && checks >= 4);
        if ((hasToast && !busySaveBtn && checks >= 2) || isCleanlySaved || checks >= 22) {
          clearInterval(saveCompletionTimer);
          saveCompletionTimer = null;
          disarmBeforeUnload();
          try {
            if (document.activeElement && document.activeElement !== document.body) {
              document.activeElement.blur();
            }
          } catch (e) {}
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
        disarmBeforeUnload();
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

          // Modo Automático (autoPilot ou autoSave): clica automaticamente em Salvar e aguarda confirmação real
          if ((settings.autoPilot || settings.autoSave) && !hasTriggeredSaveForCurrentProduct) {
            hasTriggeredSaveForCurrentProduct = true;
            setTimeout(() => {
              try {
                if (document.activeElement && document.activeElement !== document.body) {
                  document.activeElement.blur();
                }
              } catch (e) {}
              const liveSaveBtn = findSaveButton() || saveBtn;
              if (liveSaveBtn && !liveSaveBtn.disabled) {
                console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] 🤖 Piloto Automático: clicando em Salvar automaticamente!`);
                liveSaveBtn.click();
                waitForShopifySaveComplete(fireOnce);
              } else {
                waitForShopifySaveComplete(fireOnce);
              }
            }, 650);
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

    function normalizeShopifyCdnUrl(rawUrl) {
      if (!rawUrl || typeof rawUrl !== "string") return "";
      let u = rawUrl.trim();
      if (u.startsWith("//")) u = "https:" + u;
      const parts = u.split("?");
      let base = parts[0];
      const qs = parts[1] || "";
      // Remove sufixos de miniatura da Shopify (_200x200, _300x300_crop_center, _small, _compact, etc.)
      base = base.replace(/_(?:\d+x\d*|\d*x\d+|small|compact|medium|large|grande|thumb|icon|pico)(?:_crop_[a-z]+)?(?=\.[a-z0-9]+$)/i, "");
      const vMatch = qs.match(/(?:^|&)(v=\d+)/);
      return vMatch ? `${base}?${vMatch[1]}` : base;
    }

    function extractLiveShopifyMediaGallery() {
      try {
        const imgs = Array.from(document.querySelectorAll("img"));
        const mediaUrls = [];
        const seenRoots = new Set();

        for (const img of imgs) {
          if (
            img.closest("#brk-tm-hud") ||
            img.closest("#brk-tm-preview-modal") ||
            img.closest("[contenteditable='true']") ||
            img.closest("table") ||
            img.closest(".Polaris-IndexTable") ||
            img.closest("[role='grid']") ||
            img.closest("[role='table']")
          ) {
            continue;
          }
          const src = img.currentSrc || img.src || "";
          if (!src.includes("cdn.shopify.com/s/files/") || src.toLowerCase().endsWith(".svg")) continue;
          const rect = img.getBoundingClientRect();
          // Miniaturas da seção Mídias têm pelo menos 44px de largura/altura; ícones de variantes têm <= 40px
          if (rect.width > 0 && rect.width < 44) continue;

          const cleanUrl = normalizeShopifyCdnUrl(src);
          const root = cleanUrl.split("?")[0].toLowerCase();
          if (root && !seenRoots.has(root)) {
            seenRoots.add(root);
            mediaUrls.push(cleanUrl);
          }
        }
        return mediaUrls;
      } catch (e) {
        return [];
      }
    }

    function syncModeBImagesWithLiveShopifyGallery(htmlContent, prod) {
      try {
        if (!htmlContent || !prod) return htmlContent;
        const titleAndSku = `${prod.title || ""} ${prod.master_sku || ""}`.toLowerCase();
        const isApparel = /camisa|camiseta|fusion|hyb|armorx|cax|segunda pele|raglan|cortavento|jaqueta/i.test(titleAndSku);
        if (!isApparel) return htmlContent;

        const liveGallery = extractLiveShopifyMediaGallery();
        if (liveGallery.length < 4) return htmlContent;

        const dbGallery = Array.isArray(prod.cdn_images) ? prod.cdn_images : [];
        const liveRoots = liveGallery.slice(0, 4).map(u => u.split("?")[0].toLowerCase());
        const dbRoots = dbGallery.slice(0, 4).map(u => String(u).split("?")[0].toLowerCase());

        // Se a galeria ao vivo na Shopify for idêntica à do banco, preserva a seleção cirúrgica da API Python
        if (liveRoots.length === dbRoots.length && liveRoots.every((r, idx) => r === dbRoots[idx])) {
          return htmlContent;
        }

        const fnames = liveGallery.slice(0, 4).map(u => (u.split("?")[0].split("/").pop() || "").toLowerCase());
        const matchStudioNum = (fn) => {
          const m = fn.match(/(?:^|\d{10,14}[-_]|[-_])0?([1234])(?:_(?:masc|fem|inf)|masc|fem|inf)?(?:_[0-9a-f]{8}-[0-9a-f-]{27})?\.[a-z0-9]+$/i);
          return m ? parseInt(m[1], 10) : null;
        };

        const studioNums = fnames.map(matchStudioNum);
        const isPureStudio1to4 = [1, 2, 3, 4].every(n => studioNums.includes(n));
        const isAllPoc = fnames.every(fn => fn.includes("productonchannel")) && !/raglan|segunda pele/i.test(titleAndSku);
        const isF3Back = /costas|costa|verso|tras|02_|-02\.|02masc|02fem|02inf/i.test(fnames[3]);

        // Série pura de estúdio (1=Frente, 2=Costas, 3=3/4 Frontal, 4=3/4 Costas) -> usa [0, 1, 2]
        // Galeria com Capa Humanizada em [0] -> usa [0, 1, 3] (pulando [2]=Costas)
        const targetActs = (isPureStudio1to4 || isAllPoc || isF3Back)
          ? [liveGallery[0], liveGallery[1], liveGallery[2]]
          : [liveGallery[0], liveGallery[1], liveGallery[3]];

        let actIdx = 0;
        return htmlContent.replace(/(<div class="brk-(?:desc|act)-media">\s*<img[^>]+src=["'])([^"']+)(["'])/gi, (full, p1, oldSrc, p3) => {
          if (actIdx < 3 && targetActs[actIdx]) {
            const replacement = targetActs[actIdx];
            actIdx++;
            return `${p1}${replacement}${p3}`;
          }
          actIdx++;
          return full;
        });
      } catch (e) {
        return htmlContent;
      }
    }

    function injectModoBIntoEditor(htmlContent) {
      if (!htmlContent) {
        alert("Conteúdo Modo B vazio no banco de dados.");
        return false;
      }

      // Sincroniza em tempo real as fotos dos 3 Atos com a galeria "Mídias" atual da Shopify ([0]=Capa Humanizada, [1]=Frente, [3]=3/4 Frontal)
      htmlContent = syncModeBImagesWithLiveShopifyGallery(htmlContent, activeLoadedProduct);

      disarmBeforeUnload();
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

          // Fecha o modo Código HTML (<>) de volta para o Modo Visual para a Shopify comitar o estado imediatamente
          setTimeout(() => {
            const toggleBackBtn = findShowHtmlButton();
            if (toggleBackBtn && findDescriptionTextarea()?.offsetParent !== null) {
              try { toggleBackBtn.click(); } catch (e) {}
            }
          }, 160);

          setTimeout(() => {
            highlightSaveButton(() => {
              console.log(`[BRK-Tampermonkey v${SCRIPT_VERSION}] Produto salvo com sucesso!`);
              handleAfterSave();
            });
          }, 380);

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
          try { tiny.body.blur(); } catch (e) {}
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
          editable.dispatchEvent(new Event("blur", { bubbles: true }));
          try { editable.blur(); } catch (e) {}
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
      let count = settings.autoPilot ? Math.min(settings.delaySeconds || 4, 1) : (settings.delaySeconds || 4);
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
        // Se ainda estiver salvando na Shopify, aguarda mais um ciclo antes de trocar de URL
        if (findBusySaveButton()) {
          renderHudProductMode(
            activeLoadedProduct,
            `⏳ Concluindo salvamento na Shopify...`,
            `Aguardando confirmação final para avançar (${nextIdx + 1}/${q.length})...`
          );
          return;
        }
        if (count <= 0) {
          clearInterval(countdownTimer);
          setQueueIndex(nextIdx);
          disarmBeforeUnload();
          try {
            if (document.activeElement && document.activeElement !== document.body) {
              document.activeElement.blur();
            }
          } catch (e) {}
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
      }, 850);
    }

    const injectDescriptionIntoShopify = injectModoBIntoEditor;
    const advanceToNextProduct = startCountdownToNext;

    let currentSearchSkuTerm = "";

    // Renderizador do Mapa de Códigos (SKUs) Fora das Diretrizes com filtro de busca instantânea
    function renderNonCompliantCodesBox(codesList, alwaysExpanded = false) {
      const activeCodes = (codesList || []).filter(c => !isProductMarkedCompliant(c.id, c.sku));
      if (activeCodes.length === 0) {
        return `
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:10px;text-align:center;color:#4ade80;font-size:11.5px;font-weight:700;">
            🎉 Todos os produtos mapeados nesta visão estão 100% conformes!
          </div>
        `;
      }
      const term = (currentSearchSkuTerm || "").trim().toLowerCase();
      const filteredCodes = term
        ? activeCodes.filter(c =>
            String(c.sku || "").toLowerCase().includes(term) ||
            String(c.id || "").toLowerCase().includes(term) ||
            String(c.title || "").toLowerCase().includes(term) ||
            String(c.guideline_reason || "").toLowerCase().includes(term)
          )
        : activeCodes;

      const rowsHtml = filteredCodes.slice(0, 50).map(c => {
        let badgeCls = "brk-badge-legacy";
        let badgeLabel = "ANTIGO";
        if (c.guideline_status === "MODO_B_DESATUALIZADO") { badgeCls = "brk-badge-outdated"; badgeLabel = "VIOLAÇÃO"; }
        else if (c.guideline_status === "SEM_DESCRICAO") { badgeCls = "brk-badge-empty"; badgeLabel = "SEM DESC"; }
        else if (c.guideline_status === "IMAGENS_QUEBRADAS") { badgeCls = "brk-badge-broken"; badgeLabel = "S3 404"; }

        return `
          <div class="brk-code-row" data-prod-id="${c.id}" title="${(c.guideline_reason || c.title || '').replace(/"/g, '&quot;')}">
            <div style="display:flex;align-items:center;gap:6px;min-width:0;flex:1;">
              <strong style="color:#38bdf8;font-family:monospace;font-size:11px;flex-shrink:0;">${c.sku || c.id}</strong>
              <span class="brk-badge-status ${badgeCls}" style="font-size:8.5px;padding:1px 5px;flex-shrink:0;">${badgeLabel}</span>
              <span style="color:#cbd5e1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${c.title || c.guideline_reason}</span>
            </div>
            <span style="color:#4ade80;font-weight:700;font-size:10px;flex-shrink:0;">Abrir ➔</span>
          </div>
        `;
      }).join("");

      const innerContent = `
        <div style="margin-top:4px;margin-bottom:6px;">
          <input id="brk-inp-sku-search" type="text" value="${(currentSearchSkuTerm || '').replace(/"/g, '&quot;')}" placeholder="🔍 Buscar por SKU, ID ou nome do produto..." style="width:100%;background:#060911;color:#f8fafc;border:1px solid #334155;border-radius:6px;padding:5px 8px;font-size:11px;box-sizing:border-box;outline:none;" />
        </div>
        <div class="brk-codes-scroll">
          ${rowsHtml || '<div style="padding:8px;text-align:center;color:#64748b;font-size:11px;">Nenhum SKU encontrado para esta busca.</div>'}
        </div>
      `;

      if (alwaysExpanded) {
        return `
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:8px 10px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
              <span style="font-size:11px;font-weight:800;color:#fbbf24;">🎯 Mapa de SKUs Pendentes (${filteredCodes.length}/${activeCodes.length})</span>
              <span style="font-size:9.5px;color:#64748b;">Clique para abrir</span>
            </div>
            ${innerContent}
          </div>
        `;
      }

      return `
        <details style="margin-bottom:8px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:6px 10px;">
          <summary style="cursor:pointer;font-size:11px;font-weight:800;color:#fbbf24;user-select:none;">
            🎯 Próximos SKUs da Fila / Pendentes (${activeCodes.length})
          </summary>
          ${innerContent}
        </details>
      `;
    }

    function bindCodeRowClicks(rerenderCallback) {
      const rows = Array.from(hud.querySelectorAll(".brk-code-row[data-prod-id]"));
      for (const r of rows) {
        r.onclick = () => {
          const pid = r.getAttribute("data-prod-id");
          if (pid) {
            location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${pid}`;
          }
        };
      }
      const inpSearch = document.getElementById("brk-inp-sku-search");
      if (inpSearch && rerenderCallback) {
        inpSearch.oninput = (e) => {
          currentSearchSkuTerm = e.target.value || "";
          const pos = inpSearch.selectionStart || currentSearchSkuTerm.length;
          rerenderCallback();
          const newInp = document.getElementById("brk-inp-sku-search");
          if (newInp) {
            newInp.focus();
            try { newInp.setSelectionRange(pos, pos); } catch (err) {}
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
            <span>🔍 AUDITORIA VISUAL DE FOTOS & CORES</span>
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

      // Modo Minimizado (Pílula Compacta)
      if (settings.minimized) {
        hud.classList.add("brk-hud-minimized");
        hud.innerHTML = `
          <div style="display:flex;align-items:center;gap:8px;justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="font-size:14px;">${settings.autoPilot ? '🤖' : '🟢'}</span>
              <strong style="color:${currentTheme.light};font-size:12px;">BRK v${SCRIPT_VERSION}</strong>
              <span style="color:#f8fafc;font-family:monospace;font-size:11.5px;font-weight:800;">${prod ? (prod.master_sku || 'SKU') : '...'}</span>
              ${inQueue ? `<span style="background:#065f46;color:#6ee7b7;font-size:10px;font-weight:800;padding:1px 6px;border-radius:9999px;">${idx + 1}/${q.length}</span>` : ''}
            </div>
            <div style="display:flex;align-items:center;gap:5px;">
              <button id="brk-btn-inject-mini" class="brk-hud-btn brk-hud-btn-primary" style="padding:4px 8px;font-size:10.5px;background:${currentTheme.primary};">⚡ Injetar</button>
              <button id="brk-btn-toggle-min" class="brk-icon-btn" title="Expandir Mini-Dashboard">▢</button>
            </div>
          </div>
        `;
        const btnInjMini = document.getElementById("brk-btn-inject-mini");
        if (btnInjMini && prod) btnInjMini.onclick = () => injectModoBIntoEditor(prod.mode_b_html);
        const btnExp = document.getElementById("brk-btn-toggle-min");
        if (btnExp) btnExp.onclick = () => {
          saveSettings({ minimized: false });
          renderHudProductMode(prod, statusTitle, statusSub);
        };
        return;
      }
      hud.classList.remove("brk-hud-minimized");

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
            <strong style="color:${currentTheme.light};font-size:12.5px;">BRK COCKPIT v${SCRIPT_VERSION}</strong>
            <span style="${editorBadgeStyle}font-size:10px;font-weight:800;padding:2px 7px;border-radius:9999px;">${editorHealth.badge}</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;">
            <span style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};font-size:10px;font-weight:800;padding:2px 8px;border-radius:9999px;">
              ${inQueue ? `Fila ${idx + 1}/${q.length}` : currentStoreName}
            </span>
            <button id="brk-btn-toggle-min" class="brk-icon-btn" title="Minimizar painel">—</button>
          </div>
        </div>

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:9px 11px;margin-bottom:9px;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;flex-wrap:wrap;">
            <span style="font-weight:800;color:#f8fafc;font-size:14px;font-family:monospace;">${prod ? (prod.master_sku || 'Sem SKU') : 'Carregando...'}</span>
            ${prod ? `<span class="brk-badge-status ${statusBadgeClass}">${gStatus}</span>` : ''}
            ${prod ? `<span class="brk-badge-meta">📂 ${prod.category || 'Geral'}</span>` : ''}
            ${prod ? `<span class="brk-badge-meta">📸 ${imgCount} fotos</span>` : ''}
            ${prod && prod.delivery_time ? `<span class="brk-badge-meta">🚚 ${prod.delivery_time}</span>` : ''}
          </div>
          <div style="font-size:12px;color:#e2e8f0;font-weight:600;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:470px;">
            ${prod ? prod.title : 'Consultando dados reais na API...'}
          </div>
          ${prod ? `
            <div style="display:flex;align-items:center;justify-content:space-between;margin-top:6px;padding-top:5px;border-top:1px solid #1e293b;font-size:10.5px;">
              <span style="color:${currentTheme.light};font-weight:700;">🧩 ${prod.layout_type || prod.archetype_name || 'Modo B'} (${prod.audience_badge || 'ADULTO'})</span>
              ${prod.mode_b_html ? `<span style="color:#4ade80;font-weight:700;">⭐ ${(prod.mode_b_html.length).toLocaleString('pt-BR')} chars</span>` : ''}
            </div>
          ` : ''}
        </div>

        ${renderMediaAuditAlertBox(prod)}

        <div style="background:#0b1120;border-left:3px solid ${currentTheme.primary};border-radius:6px;padding:7px 10px;margin-bottom:9px;">
          <div style="font-weight:700;color:${currentTheme.light};font-size:11.5px;">${statusTitle || "Pronto para Injeção"}</div>
          <div style="font-size:10.5px;color:#94a3b8;line-height:1.35;">${statusSub || editorHealth.reason}</div>
        </div>

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:9px;padding:5px 9px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;flex-wrap:wrap;gap:6px;">
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
            <span style="color:#fbbf24;">⏸️ Pausar Cor s/ Foto</span>
          </label>
          <label class="brk-hud-toggle" title="Durante um lote, pula produtos que já estão 100% conformes com as diretrizes Modo B v5">
            <input type="checkbox" id="brk-chk-skip-done" ${settings.skipAlreadyModeB ? 'checked' : ''} style="accent-color:${currentTheme.primary};" />
            <span>Pular Conformes</span>
          </label>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:${inQueue ? '8px' : '4px'};">
          <button id="brk-btn-inject" class="brk-hud-btn brk-hud-btn-primary" style="flex:1;justify-content:center;background:${currentTheme.primary};border-color:${currentTheme.primaryHover};padding:7px 12px;" title="Injeta a narrativa completa Modo B v5 no editor HTML e salva se Auto-Salvar estiver ativo">
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
        </div>

        ${inQueue ? `
          <div style="background:#06130e;border:1px solid #16a34a;border-radius:8px;padding:6px 10px;display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:11px;font-weight:700;color:#4ade80;">🚀 Lote Ativo: Produto ${idx + 1} de ${q.length}</span>
            <div style="display:flex;gap:5px;">
              <button id="brk-btn-next-now" class="brk-hud-btn" style="padding:4px 8px;font-size:10.5px;">
                ⏭️ Pular (${idx + 1}/${q.length})
              </button>
              <button id="brk-btn-pause-queue" class="brk-hud-btn brk-hud-btn-danger" style="padding:4px 8px;font-size:10.5px;">
                ⏹️ Parar Fila
              </button>
            </div>
          </div>
        ` : ''}

        ${renderNonCompliantCodesBox(queueCodes, false)}
      `;

      bindCodeRowClicks(() => renderHudProductMode(prod, statusTitle, statusSub));

      const btnMin = document.getElementById("brk-btn-toggle-min");
      if (btnMin) {
        btnMin.onclick = () => {
          saveSettings({ minimized: true });
          renderHudProductMode(prod, statusTitle, statusSub);
        };
      }

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
    }

    // =========================================================================
    // RENDERIZAÇÃO DO MINI-DASHBOARD NA LISTAGEM (admin.shopify.com/.../products)
    // =========================================================================
    let lastLoadedStats = null;

    function renderHudListMode(stats) {
      if (stats) lastLoadedStats = stats;
      else stats = lastLoadedStats;

      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      const settings = getSettings();
      const activeTab = settings.activeTab || "priorities";

      hud.style.borderColor = currentTheme.primary;
      if (stats && Array.isArray(stats.non_compliant_codes)) {
        cachedNonCompliantCodes = stats.non_compliant_codes;
      }

      const totalProds = stats?.total_products || 2148;
      const compCount = stats?.compliant_count || 0;
      const brkCount = stats?.imagens_quebradas_count || 0;
      const empCount = stats?.sem_descricao_count || 0;
      const legCount = stats?.fora_padrao_modo_b_count || 0;
      const outCount = stats?.modo_b_desatualizado_count || 0;
      const critCount = stats?.criticos_loja_count ?? (brkCount + empCount + outCount);
      const pct = stats?.progress_pct ?? Math.round((compCount / Math.max(1, totalProds)) * 1000) / 10;
      const pg = stats?.pending_by_group || {};

      // Modo Minimizado na Listagem
      if (settings.minimized) {
        hud.classList.add("brk-hud-minimized");
        hud.innerHTML = `
          <div style="display:flex;align-items:center;gap:10px;justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="font-size:14px;">🎛️</span>
              <strong style="color:${currentTheme.light};font-size:12px;">BRK v${SCRIPT_VERSION}</strong>
              <span style="background:#065f46;color:#6ee7b7;font-size:10px;font-weight:800;padding:1px 7px;border-radius:9999px;">✅ ${compCount} (${pct}%)</span>
              ${q.length > 0 ? `<span style="background:#1e293b;color:#38bdf8;font-size:10px;font-weight:800;padding:1px 7px;border-radius:9999px;">Fila ${idx + 1}/${q.length}</span>` : ''}
            </div>
            <button id="brk-btn-toggle-min-list" class="brk-icon-btn" title="Expandir Mini-Dashboard">▢</button>
          </div>
        `;
        const btnExp = document.getElementById("brk-btn-toggle-min-list");
        if (btnExp) btnExp.onclick = () => {
          saveSettings({ minimized: false });
          renderHudListMode(stats);
        };
        return;
      }
      hud.classList.remove("brk-hud-minimized");

      // Renderização do Conteúdo da Aba Selecionada
      let tabContentHtml = "";

      if (activeTab === "priorities") {
        tabContentHtml = `
          <!-- PRIORIDADE 1: URGÊNCIAS VISUAIS DA LOJA (S3 404 + SEM DESCRIÇÃO) -->
          <div style="background:linear-gradient(135deg,rgba(127,29,29,0.35),rgba(15,23,42,0.95));border:1px solid #dc2626;border-radius:11px;padding:9px 11px;margin-bottom:8px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
              <span style="font-size:11px;font-weight:800;color:#fca5a5;">🚨 PRIORIDADE 1 — URGÊNCIAS DA VITRINE</span>
              <span style="background:#991b1b;color:#fee2e2;font-size:9.5px;font-weight:800;padding:1px 7px;border-radius:9999px;">${critCount} pendentes</span>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
              <button id="brk-prio-criticos-all" class="brk-hud-btn" style="flex:1.3;justify-content:center;background:linear-gradient(90deg,#dc2626,#b91c1c);border-color:#ef4444;color:#fff;padding:7px 10px;">
                ⚡ Corrigir Críticos (S3 + Vazios)
              </button>
              <button id="brk-prio-empty-only" class="brk-hud-btn" style="flex:0.85;justify-content:center;background:#1e293b;border-color:#f59e0b;color:#fde68a;padding:7px 8px;" title="Apenas produtos sem nenhuma descrição (${empCount})">
                📝 Sem Desc (${empCount})
              </button>
              <button id="brk-prio-s3-only" class="brk-hud-btn" style="flex:0.85;justify-content:center;background:#1e293b;border-color:#f97316;color:#fed7aa;padding:7px 8px;" title="Apenas produtos com imagens AWS S3 404 quebradas (${brkCount})">
                🖼️ S3 404 (${brkCount})
              </button>
            </div>
          </div>

          ${outCount > 0 ? `
            <div style="background:#2e1905;border:1px solid #d97706;border-radius:9px;padding:6px 10px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">
              <span style="font-size:11px;color:#fde68a;font-weight:700;">⚠️ ${outCount} produto(s) com versão Modo B v1 restante</span>
              <button id="brk-prio-outdated" class="brk-hud-btn" style="background:#d97706;border-color:#f59e0b;color:#fff;padding:4px 9px;font-size:10.5px;">
                ⚡ Finalizar (${outCount})
              </button>
            </div>
          ` : ''}

          <!-- PRIORIDADE 2: LOTES RÁPIDOS POR CATEGORIA COMERCIAL -->
          <div style="margin-bottom:4px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
              <span style="font-size:10.5px;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:0.04em;">📦 Prioridade 2 — Padronizar por Categoria (1-Clique)</span>
              <label class="brk-hud-toggle" title="Injeta, clica em Salvar e avança sozinho">
                <input type="checkbox" id="brk-list-chk-autopilot" ${settings.autoPilot ? 'checked' : ''} style="accent-color:#22c55e;" />
                <strong style="color:#4ade80;font-size:10.5px;">🤖 Auto-Save Ativo</strong>
              </label>
            </div>
            <div class="brk-priority-grid">
              <button class="brk-priority-btn" data-quick-cat="camisas">
                <span>👕 Camisas UV & Perf.</span>
                <span class="brk-priority-count">${pg.camisas ?? '...'}</span>
              </button>
              <button class="brk-priority-btn" data-quick-cat="bones_chapeus">
                <span>🧢 Bonés & Chapéus D2C</span>
                <span class="brk-priority-count">${pg.bones_chapeus ?? '...'}</span>
              </button>
              <button class="brk-priority-btn" data-quick-cat="iscas_artificiais">
                <span>🎣 Iscas Artificiais</span>
                <span class="brk-priority-count">${pg.iscas_artificiais ?? '...'}</span>
              </button>
              <button class="brk-priority-btn" data-quick-cat="equipamentos_pesca">
                <span>⚙️ Equipamentos & Caixas</span>
                <span class="brk-priority-count">${pg.equipamentos_pesca ?? '...'}</span>
              </button>
              <button class="brk-priority-btn" data-quick-cat="calcas">
                <span>👖 Calças & Bermudas</span>
                <span class="brk-priority-count">${pg.calcas ?? '...'}</span>
              </button>
              <button class="brk-priority-btn" data-quick-cat="infantil">
                <span>🧒 Linha Infantil / Kids</span>
                <span class="brk-priority-count">${pg.infantil ?? '...'}</span>
              </button>
            </div>
          </div>
        `;
      } else if (activeTab === "categories") {
        tabContentHtml = `
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:10px 11px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;flex-wrap:wrap;gap:6px;">
              <span style="font-weight:800;color:${currentTheme.light};font-size:11px;">📂 Construtor de Lote Personalizado / Coleções</span>
              <div style="display:flex;align-items:center;gap:8px;">
                <label class="brk-hud-toggle">
                  <input type="checkbox" id="brk-list-chk-autopilot" ${settings.autoPilot ? 'checked' : ''} style="accent-color:#22c55e;" />
                  <strong style="color:#4ade80;font-size:10.5px;">🤖 Auto-Save</strong>
                </label>
                <label class="brk-hud-toggle">
                  <input type="checkbox" id="brk-list-chk-pause-media" ${settings.pauseOnMediaError ? 'checked' : ''} style="accent-color:#f59e0b;" />
                  <span style="color:#fbbf24;font-size:10.5px;">⏸️ Pausar Cor s/ Foto</span>
                </label>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1.1fr 1.1fr 0.55fr;gap:6px;margin-bottom:6px;">
              <select id="brk-sel-category" class="brk-hud-select" title="Filtrar por Categoria ou Coleção">
                <option value="ALL" ${settings.batchCategory === 'ALL' ? 'selected' : ''}>📂 Todas as Categorias da Loja</option>
                <option value="camisas" ${settings.batchCategory === 'camisas' ? 'selected' : ''}>👕 Camisas (Fusion/Hybrid/ArmorX/C0)</option>
                <option value="bones_chapeus" ${settings.batchCategory === 'bones_chapeus' ? 'selected' : ''}>🧢 Bonés & Chapéus (Molde D2C)</option>
                <option value="iscas_artificiais" ${settings.batchCategory === 'iscas_artificiais' ? 'selected' : ''}>🎣 Iscas Artificiais</option>
                <option value="equipamentos_pesca" ${settings.batchCategory === 'equipamentos_pesca' ? 'selected' : ''}>⚙️ Varas, Carretilhas, Molinetes & Alicates</option>
                <option value="linhas_pesca" ${settings.batchCategory === 'linhas_pesca' ? 'selected' : ''}>🧵 Linhas de Pesca</option>
                <option value="calcas" ${settings.batchCategory === 'calcas' ? 'selected' : ''}>👖 Calças & Bermudas</option>
                <option value="corta_vento" ${settings.batchCategory === 'corta_vento' ? 'selected' : ''}>🧥 Corta-Vento & Jaquetas</option>
                <option value="infantil" ${settings.batchCategory === 'infantil' ? 'selected' : ''}>🧒 Linha Infantil (2 a 13 Anos)</option>
                <option value="feminino" ${settings.batchCategory === 'feminino' ? 'selected' : ''}>👚 Linha Feminina (Baby Look)</option>
                <option value="super_ofertas" ${settings.batchCategory === 'super_ofertas' ? 'selected' : ''}>🔥 Coleção: Super Ofertas Fishing</option>
                <option value="CUSTOM_COLLECTION" ${settings.batchCategory === 'CUSTOM_COLLECTION' ? 'selected' : ''}>🔗 Outra Coleção (URL/Handle abaixo)</option>
              </select>
              <select id="brk-sel-status" class="brk-hud-select" title="Filtrar por Prioridade ou Status">
                <option value="PRIORIDADE_CRITICA" ${settings.batchStatus === 'PRIORIDADE_CRITICA' ? 'selected' : ''}>🚨 Prioridade Crítica (S3 404 + Sem Desc)</option>
                <option value="FORA_DIRETRIZES" ${settings.batchStatus === 'FORA_DIRETRIZES' ? 'selected' : ''}>🎯 Todos Fora do Padrão Modo B v2</option>
                <option value="SEM_DESCRICAO" ${settings.batchStatus === 'SEM_DESCRICAO' ? 'selected' : ''}>📝 Apenas Sem Descrição</option>
                <option value="IMAGENS_QUEBRADAS" ${settings.batchStatus === 'IMAGENS_QUEBRADAS' ? 'selected' : ''}>🖼️ Apenas Fotos AWS S3 404</option>
                <option value="FORA_PADRAO_MODO_B" ${settings.batchStatus === 'FORA_PADRAO_MODO_B' ? 'selected' : ''}>🔄 Apenas Descrição Antiga (Legado)</option>
                <option value="MODO_B_DESATUALIZADO" ${settings.batchStatus === 'MODO_B_DESATUALIZADO' ? 'selected' : ''}>⚠️ Apenas Violação Residual v1</option>
                <option value="CRITICOS_FOTOS_CORES" ${settings.batchStatus === 'CRITICOS_FOTOS_CORES' ? 'selected' : ''}>🔍 Auditoria: Cor s/ Foto + Duplicadas</option>
                <option value="COLECAO_COMPLETA" ${settings.batchStatus === 'COLECAO_COMPLETA' ? 'selected' : ''}>📦 Reaplicar em Toda a Coleção</option>
              </select>
              <select id="brk-sel-limit" class="brk-hud-select" title="Quantidade de Produtos no Lote">
                <option value="25" ${Number(settings.batchLimit) === 25 ? 'selected' : ''}>25 itens</option>
                <option value="50" ${Number(settings.batchLimit) === 50 ? 'selected' : ''}>50 itens</option>
                <option value="100" ${Number(settings.batchLimit) === 100 ? 'selected' : ''}>100 itens</option>
              </select>
            </div>
            <div style="margin-bottom:8px;">
              <input id="brk-inp-collection" type="text" value="${(settings.customCollection || '').replace(/"/g, '&quot;')}" placeholder="Opcional: Cole aqui a URL ou handle de qualquer coleção Shopify (ex: lancamentos ou camisas-uv)" style="width:100%;background:#060911;color:#f8fafc;border:1px solid #334155;border-radius:6px;padding:6px 8px;font-size:11px;box-sizing:border-box;" />
            </div>
            <button id="brk-btn-start-custom-batch" class="brk-hud-btn brk-hud-btn-success" style="width:100%;justify-content:center;padding:8px 12px;font-size:12px;">
              🚀 Iniciar Piloto Automático com Este Filtro
            </button>
          </div>
        `;
      } else {
        tabContentHtml = renderNonCompliantCodesBox(cachedNonCompliantCodes, true);
      }

      hud.innerHTML = `
        <!-- TOPO DO MINI-DASHBOARD COCKPIT -->
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">🎛️</span>
            <div>
              <div style="display:flex;align-items:center;gap:6px;">
                <strong style="color:${currentTheme.light};font-size:13px;letter-spacing:0.01em;">BRK MINI-DASHBOARD v${SCRIPT_VERSION}</strong>
                <span style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};font-size:9.5px;font-weight:800;padding:1px 7px;border-radius:9999px;">
                  ${currentStoreName}
                </span>
              </div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:5px;">
            <button id="brk-btn-refresh-stats" class="brk-icon-btn" title="Atualizar contadores do banco">↻</button>
            <button id="brk-btn-toggle-min-list" class="brk-icon-btn" title="Minimizar painel para pílula compacta">—</button>
          </div>
        </div>

        <!-- BARRA DE PROGRESSO DA LOJA -->
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:7px 10px;margin-bottom:8px;">
          <div style="display:flex;align-items:center;justify-content:space-between;font-size:11px;">
            <span style="color:#cbd5e1;font-weight:700;">📈 Cobertura Oficial Modo B v2</span>
            <span style="color:#4ade80;font-weight:800;">${compCount.toLocaleString('pt-BR')} / ${totalProds.toLocaleString('pt-BR')} produtos (${pct}%)</span>
          </div>
          <div class="brk-progress-track">
            <div class="brk-progress-fill" style="width:${Math.min(100, Math.max(2, pct))}%;background:linear-gradient(90deg,${currentTheme.primary},#22c55e);"></div>
          </div>
        </div>

        <!-- 4 KPI CARDS EXECUTIVOS (CLICÁVEIS) -->
        <div class="brk-kpi-grid">
          <div class="brk-kpi-card" id="brk-kpi-compliant" title="Produtos 100% atualizados com Modo B v2 sem 'Troca Descomplicada'">
            <div class="brk-kpi-val" style="color:#4ade80;">${stats ? compCount.toLocaleString('pt-BR') : '...'}</div>
            <div class="brk-kpi-lbl">✅ Conformes</div>
          </div>
          <div class="brk-kpi-card" id="brk-kpi-broken" title="Clique para iniciar lote de correção de Imagens AWS S3 Quebradas (404)">
            <div class="brk-kpi-val" style="color:#f87171;">${stats ? brkCount.toLocaleString('pt-BR') : '...'}</div>
            <div class="brk-kpi-lbl">🖼️ S3 404 ➔</div>
          </div>
          <div class="brk-kpi-card" id="brk-kpi-empty" title="Clique para iniciar lote nos produtos Sem Descrição">
            <div class="brk-kpi-val" style="color:#fbbf24;">${stats ? empCount.toLocaleString('pt-BR') : '...'}</div>
            <div class="brk-kpi-lbl">📝 Sem Desc ➔</div>
          </div>
          <div class="brk-kpi-card" id="brk-kpi-legacy" title="Clique para atualizar descrições antigas para os 3 Atos Modo B v2">
            <div class="brk-kpi-val" style="color:#38bdf8;">${stats ? legCount.toLocaleString('pt-BR') : '...'}</div>
            <div class="brk-kpi-lbl">🔄 Antigos ➔</div>
          </div>
        </div>

        <!-- CONTROLE DE FILA EM ANDAMENTO (SEMPRE VISÍVEL QUANDO HÁ FILA) -->
        ${q.length > 0 ? `
          <div style="background:#06130e;border:1px solid #22c55e;border-radius:10px;padding:7px 11px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">
            <div>
              <div style="font-weight:800;color:#4ade80;font-size:11.5px;">🚀 Fila Ativa: ${idx + 1} de ${q.length} (${q[idx]?.master_sku || ''})</div>
              <div style="font-size:10px;color:#94a3b8;">${active ? '🤖 Piloto Automático pronto para continuar' : '⏸️ Fila pausada'}</div>
            </div>
            <div style="display:flex;gap:5px;">
              <button id="brk-btn-resume-queue" class="brk-hud-btn brk-hud-btn-success" style="padding:5px 10px;font-size:11px;">
                ▶️ Retomar (${idx + 1}/${q.length})
              </button>
              <button id="brk-btn-clear-queue" class="brk-hud-btn brk-hud-btn-danger" style="padding:5px 8px;font-size:11px;" title="Encerrar e limpar fila atual">
                ⏹️
              </button>
            </div>
          </div>
        ` : ''}

        <!-- BARRA DE NAVEGAÇÃO EM 3 ABAS -->
        <div class="brk-tab-bar">
          <button class="brk-tab-btn ${activeTab === 'priorities' ? 'active' : ''}" data-tab="priorities">
            🚀 Prioridades
          </button>
          <button class="brk-tab-btn ${activeTab === 'categories' ? 'active' : ''}" data-tab="categories">
            📂 Lote & Coleções
          </button>
          <button class="brk-tab-btn ${activeTab === 'queue' ? 'active' : ''}" data-tab="queue">
            🎯 Busca SKU (${cachedNonCompliantCodes.length})
          </button>
        </div>

        <!-- CONTEÚDO DA ABA ATIVA -->
        ${tabContentHtml}
      `;

      bindCodeRowClicks(() => renderHudListMode(stats));

      // Minimizar / Atualizar
      const btnMinList = document.getElementById("brk-btn-toggle-min-list");
      if (btnMinList) {
        btnMinList.onclick = () => {
          saveSettings({ minimized: true });
          renderHudListMode(stats);
        };
      }
      const btnRefresh = document.getElementById("brk-btn-refresh-stats");
      if (btnRefresh) {
        btnRefresh.onclick = async () => {
          btnRefresh.textContent = "⏳";
          try {
            const excludeParam = encodeURIComponent(getCompliantIds().slice(-300).join(","));
            const fresh = await fetchFromBRKDatabase(`/api/product_db?store=${currentStoreKey}&action=stats&exclude_ids=${excludeParam}`);
            if (fresh.success) renderHudListMode(fresh);
          } catch (e) {
            renderHudListMode(stats);
          }
        };
      }

      // Alternância de Abas
      for (const tabBtn of Array.from(hud.querySelectorAll(".brk-tab-btn[data-tab]"))) {
        tabBtn.onclick = () => {
          saveSettings({ activeTab: tabBtn.getAttribute("data-tab") });
          renderHudListMode(stats);
        };
      }

      // Cliques nos KPI Cards Executivos
      const kpiBroken = document.getElementById("brk-kpi-broken");
      if (kpiBroken) {
        kpiBroken.onclick = () => {
          saveSettings({ batchCategory: "ALL", batchStatus: "IMAGENS_QUEBRADAS", autoPilot: true, autoSave: true, skipAlreadyModeB: true });
          startQueueFromDatabase("IMAGENS_QUEBRADAS", 50, "ALL");
        };
      }
      const kpiEmpty = document.getElementById("brk-kpi-empty");
      if (kpiEmpty) {
        kpiEmpty.onclick = () => {
          saveSettings({ batchCategory: "ALL", batchStatus: "SEM_DESCRICAO", autoPilot: true, autoSave: true, skipAlreadyModeB: true });
          startQueueFromDatabase("SEM_DESCRICAO", 50, "ALL");
        };
      }
      const kpiLegacy = document.getElementById("brk-kpi-legacy");
      if (kpiLegacy) {
        kpiLegacy.onclick = () => {
          saveSettings({ batchCategory: "ALL", batchStatus: "FORA_PADRAO_MODO_B", autoPilot: true, autoSave: true, skipAlreadyModeB: true });
          startQueueFromDatabase("FORA_PADRAO_MODO_B", 50, "ALL");
        };
      }

      // Botões da Aba 1: Prioridades
      const btnCritAll = document.getElementById("brk-prio-criticos-all");
      if (btnCritAll) {
        btnCritAll.onclick = () => {
          saveSettings({ batchCategory: "ALL", batchStatus: "PRIORIDADE_CRITICA", batchLimit: 50, autoPilot: true, autoSave: true, skipAlreadyModeB: true });
          startQueueFromDatabase("PRIORIDADE_CRITICA", 50, "ALL");
        };
      }
      const btnEmptyOnly = document.getElementById("brk-prio-empty-only");
      if (btnEmptyOnly) {
        btnEmptyOnly.onclick = () => {
          saveSettings({ batchCategory: "ALL", batchStatus: "SEM_DESCRICAO", batchLimit: 50, autoPilot: true, autoSave: true, skipAlreadyModeB: true });
          startQueueFromDatabase("SEM_DESCRICAO", 50, "ALL");
        };
      }
      const btnS3Only = document.getElementById("brk-prio-s3-only");
      if (btnS3Only) {
        btnS3Only.onclick = () => {
          saveSettings({ batchCategory: "ALL", batchStatus: "IMAGENS_QUEBRADAS", batchLimit: 50, autoPilot: true, autoSave: true, skipAlreadyModeB: true });
          startQueueFromDatabase("IMAGENS_QUEBRADAS", 50, "ALL");
        };
      }
      const btnOutdated = document.getElementById("brk-prio-outdated");
      if (btnOutdated) {
        btnOutdated.onclick = () => {
          saveSettings({ batchCategory: "ALL", batchStatus: "MODO_B_DESATUALIZADO", batchLimit: 50, autoPilot: true, autoSave: true, skipAlreadyModeB: false });
          startQueueFromDatabase("MODO_B_DESATUALIZADO", 50, "ALL");
        };
      }

      for (const qBtn of Array.from(hud.querySelectorAll(".brk-priority-btn[data-quick-cat]"))) {
        qBtn.onclick = () => {
          const catKey = qBtn.getAttribute("data-quick-cat") || "ALL";
          saveSettings({
            batchCategory: catKey,
            batchStatus: "FORA_DIRETRIZES",
            batchLimit: 50,
            autoPilot: true,
            autoSave: true,
            skipAlreadyModeB: true
          });
          startQueueFromDatabase("FORA_DIRETRIZES", 50, catKey, "");
        };
      }

      // Checkboxes e Fila
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

      // Botão da Aba 2: Construtor de Lote Personalizado
      const btnCustomBatch = document.getElementById("brk-btn-start-custom-batch");
      if (btnCustomBatch) {
        btnCustomBatch.onclick = () => {
          const cat = document.getElementById("brk-sel-category")?.value || "ALL";
          const st = document.getElementById("brk-sel-status")?.value || "PRIORIDADE_CRITICA";
          const lim = parseInt(document.getElementById("brk-sel-limit")?.value || "50", 10);
          const colInput = (document.getElementById("brk-inp-collection")?.value || "").trim();
          const finalCol = colInput || (cat === "super_ofertas" ? "super-ofertas-🔥" : "");
          saveSettings({
            batchCategory: cat,
            batchStatus: st,
            batchLimit: lim,
            customCollection: colInput,
            autoPilot: true,
            autoSave: true,
            skipAlreadyModeB: st !== "COLECAO_COMPLETA"
          });
          startQueueFromDatabase(st, lim, cat === "CUSTOM_COLLECTION" ? "ALL" : cat, finalCol);
        };
      }
    }

    // =========================================================================
    // INICIAR FILA REAL BUSCADA DIRETAMENTE DO BANCO (SUPORTA PRIORIDADES & COLEÇÕES)
    // =========================================================================
    async function startQueueFromDatabase(statusFilter = "PRIORIDADE_CRITICA", limit = 50, categoryFilter = "ALL", collectionHandle = "") {
      hud.classList.remove("brk-hud-minimized");
      hud.innerHTML = `
        <div style="padding:12px;text-align:center;">
          <div style="font-size:18px;margin-bottom:8px;">🎛️</div>
          <strong style="color:${currentTheme.light};">Preparando Lote Inteligente no Banco BRK...</strong>
          <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Filtrando até ${limit} produtos (${statusFilter} | ${collectionHandle || categoryFilter}) em ${currentStoreName}...</div>
        </div>
      `;

      try {
        const forceReopenAll = statusFilter === "COLECAO_COMPLETA" || [
          "AJUSTE_FOTOS_GERAL",
          "CRITICOS_FOTOS_CORES",
          "COR_SEM_FOTO",
          "FOTOS_DUPLICADAS",
          "FOTOS_BAIXA_QUALIDADE"
        ].includes(statusFilter);

        const excludeParam = forceReopenAll ? "" : encodeURIComponent(getCompliantIds().slice(-300).join(","));
        const queryUrl = `/api/product_db?store=${currentStoreKey}&action=queue&status=${encodeURIComponent(statusFilter)}&category=${encodeURIComponent(categoryFilter)}&collection=${encodeURIComponent(collectionHandle || "")}&limit=${limit}&exclude_ids=${excludeParam}`;
        const res = await fetchFromBRKDatabase(queryUrl);
        const queueItems = forceReopenAll
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
          <div style="padding:12px;text-align:center;">
            <div style="font-size:18px;margin-bottom:8px;">🚀</div>
            <strong style="color:#22c55e;">${queueItems.length} Produtos Pendentes Enfileirados!</strong>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Abrindo 1º produto: <strong>${firstProduct.master_sku || firstProduct.id}</strong>...</div>
          </div>
        `;

        setTimeout(() => {
          location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${firstProduct.id}`;
        }, 700);

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
