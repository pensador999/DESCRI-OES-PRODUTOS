// ==UserScript==
// @name         BRK Assistente de Descrições Shopify (Conectado ao Banco Real v3.0)
// @namespace    https://1025-ten.vercel.app/
// @version      3.0.0
// @description  Automação assistida e em lote conectada diretamente ao banco de dados oficial BRK (Vercel API + Live Sync das 3 Lojas) para preenchimento de descrições Modo B (3 Atos + Ficha Técnica + Guia C0) no Shopify Admin.
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

  // Configuração da API do Banco de Dados BRK (6.408 produtos sincronizados nas 3 lojas)
  const API_BASE = "https://1025-ten.vercel.app";

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

  const DEFAULT_SETTINGS = {
    delaySeconds: 4,
    autoSave: false,      // Se true, clica automaticamente no botão "Salvar" da Shopify após injetar
    skipAlreadyModeB: true // Se true, avança automaticamente quando detecta que o produto já tem <!-- BRK-MODO-B
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
      console.log(`[BRK-DB v3.0] Requisitando: ${url}`);
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
          console.error("[BRK-DB v3.0] Falha de rede:", err);
          reject(new Error("Falha na conexão com a API da Vercel. Verifique a internet."));
        }
      });
    });
  }

  // =========================================================================
  // 1. LÓGICA NO PORTAL LOCAL OU VERCEL (1025-ten.vercel.app)
  // =========================================================================
  if (location.hostname === "1025-ten.vercel.app" || location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    console.log("[BRK-Tampermonkey v3.0] Conectado ao Portal de Descrições BRK.");
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
        ? `<span>🟢 Tampermonkey v3.0 | Fila: ${idx + 1}/${q.length} (${active ? 'Ativa' : 'Pausada'})</span>`
        : `<span>🟢 Tampermonkey Conectado ao Banco BRK v3.0 (6.408 itens)</span>`;
    }
    updatePortalBadge();

    badge.onclick = () => {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      alert(`[Assistente BRK v3.0 Status]\n\nFila no Tampermonkey: ${q.length} produtos\nÍndice Atual: ${q.length ? (idx + 1) : 0} de ${q.length}\nAutomação Ativa: ${active ? "SIM" : "NÃO"}`);
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

      const productMatch = urlPath.match(/\/products\/(\d+)/);
      currentProductId = productMatch ? productMatch[1] : null;
    }

    parseCurrentRoute();
    console.log(`[BRK-Tampermonkey v3.0] Shopify Admin | Loja: ${currentStoreName} (${currentShopifySlug}) | Produto ID: ${currentProductId || 'Listagem'}`);

    // Injetar Estilos Visuais do HUD e Pulso do Botão Salvar
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
        bottom: 24px;
        right: 24px;
        z-index: 999999;
        background: #090d16;
        color: #f1f5f9;
        border: 2px solid #0284c7;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.65);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        min-width: 375px;
        max-width: 490px;
        backdrop-filter: blur(12px);
      }
      .brk-badge-status {
        font-size: 10px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 9999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
      }
      .brk-badge-empty { background: #991b1b; color: #fee2e2; }
      .brk-badge-broken { background: #b45309; color: #fef3c7; }
      .brk-badge-healthy { background: #166534; color: #dcfce7; }
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
        transition: all 0.2s;
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
        background: #0369a1;
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
    `;
    document.head.appendChild(styleEl);

    const hud = document.createElement("div");
    hud.id = "brk-tm-hud";
    document.body.appendChild(hud);

    // =========================================================================
    // EXTRAÇÃO DE METADADOS DO DOM DO SHOPIFY ADMIN (HANDLE, SKU E CONTEÚDO ATUAL)
    // =========================================================================
    function extractPageHints() {
      let handle = "";
      let sku = "";
      try {
        // Procurar link de visualização ou bloco de SEO com /products/{handle}
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
        // Fallback: procurar texto de URL no preview de SEO
        if (!handle) {
          const bodyText = document.body.innerText || "";
          const seoMatch = bodyText.match(/\/products\/([a-z0-9][a-z0-9-_]{3,120})/i);
          if (seoMatch && seoMatch[1] && !/^\d+$/.test(seoMatch[1])) {
            handle = seoMatch[1].trim().toLowerCase();
          }
        }
        // Procurar campo SKU se visível
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
                console.log("[BRK-Tampermonkey v3.0] Auto-Save ativo: clicando em Salvar automaticamente!");
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
        console.log("[BRK-Tampermonkey v3.0] Alternando editor para Modo Código HTML (<>)...");
        htmlBtn.click();
      }

      setTimeout(() => {
        textarea = findDescriptionTextarea();

        if (textarea && textarea.offsetParent !== null) {
          appendBackup(currentProductId, location.pathname, textarea.value);
          setReactInputValue(textarea, htmlContent);
          console.log("[BRK-Tampermonkey v3.0] HTML Modo B injetado com sucesso no Textarea HTML!");

          // Se clicamos em (<>) antes, podemos clicar novamente após 250ms para sincronizar o estado visual do TinyMCE/Polaris
          setTimeout(() => {
            highlightSaveButton(() => {
              console.log("[BRK-Tampermonkey v3.0] Produto salvo!");
              handleAfterSave();
            });
          }, 250);

          renderHudProductMode(
            activeLoadedProduct,
            "✨ Modo B Injetado com Sucesso!",
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres oficiais no editor. ${getSettings().autoSave ? 'Salvando automaticamente...' : "Clique em 'Salvar' (verde pulsando)."}`
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
          console.log("[BRK-Tampermonkey v3.0] HTML Modo B injetado direto no iframe TinyMCE!");

          highlightSaveButton(() => handleAfterSave());
          renderHudProductMode(
            activeLoadedProduct,
            "✨ Injetado no Editor Visual (TinyMCE)!",
            `Inseridos ${(htmlContent.length).toLocaleString('pt-BR')} caracteres oficiais. ${getSettings().autoSave ? 'Salvando automaticamente...' : "Clique em 'Salvar' no topo."}`
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
          // Copiar automaticamente para o clipboard como segurança
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
        alert(`🎉 Parabéns! O lote de ${q.length} produtos foi completamente finalizado com sucesso!`);
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
      const alreadyHasModeB = isAlreadyModeBInEditor();
      const hasBackup = !!getLastBackupForProduct(currentProductId);

      let statusBadgeClass = "brk-badge-healthy";
      if (prod?.status === "SEM_DESCRICAO") statusBadgeClass = "brk-badge-empty";
      else if (prod?.status === "IMAGENS_QUEBRADAS") statusBadgeClass = "brk-badge-broken";

      const imgCount = prod ? (prod.gallery || prod.cdn_images || []).length : 0;

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">🟢</span>
            <strong style="color:#38bdf8;font-size:13px;">BANCO BRK v3.0</strong>
            ${alreadyHasModeB ? `<span style="background:#065f46;color:#6ee7b7;font-size:10px;font-weight:800;padding:2px 7px;border-radius:9999px;">✅ MODO B ATIVO</span>` : ''}
          </div>
          <span style="font-size:11px;color:#94a3b8;font-weight:700;">
            ${inQueue ? `Fila: ${idx + 1} de ${q.length}` : `${currentStoreName}`}
          </span>
        </div>

        <div style="margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;flex-wrap:wrap;">
            <span style="font-weight:800;color:#f8fafc;font-size:14px;">${prod ? (prod.master_sku || 'Sem SKU') : 'Carregando...'}</span>
            ${prod ? `<span class="brk-badge-status ${statusBadgeClass}">${prod.status}</span>` : ''}
            ${prod ? `<span style="font-size:10px;color:#94a3b8;background:#1e293b;padding:2px 7px;border-radius:9999px;">📸 ${imgCount} fotos CDN</span>` : ''}
          </div>
          <div style="font-size:12px;color:#cbd5e1;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:440px;">
            ${prod ? prod.title : 'Consultando dados reais na API...'}
          </div>
        </div>

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:10px;">
          <div style="font-weight:700;color:#38bdf8;font-size:12px;">${statusTitle || "Pronto para Injeção"}</div>
          <div style="font-size:11px;color:#94a3b8;line-height:1.4;">${statusSub || "Clique em 'Injetar Modo B' para aplicar a descrição oficial."}</div>
          ${prod && prod.mode_b_html ? `
            <div style="margin-top:6px;font-size:11px;color:#4ade80;font-weight:700;display:flex;align-items:center;justify-content:space-between;border-top:1px solid #1e293b;padding-top:4px;">
              <span>⭐ Modo B: ${(prod.mode_b_html.length).toLocaleString('pt-BR')} chars</span>
              <span style="color:#94a3b8;font-weight:600;">${prod.archetype_name || '3 Atos + Ficha Técnica'}</span>
            </div>
          ` : ''}
        </div>

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;padding:0 2px;">
          <label class="brk-hud-toggle" title="Clica automaticamente no botão Salvar da Shopify 1s após injetar o Modo B">
            <input type="checkbox" id="brk-chk-autosave" ${settings.autoSave ? 'checked' : ''} />
            <span>Auto-Salvar na Shopify</span>
          </label>
          <label class="brk-hud-toggle" title="Durante um lote, pula automaticamente produtos que já têm <!-- BRK-MODO-B">
            <input type="checkbox" id="brk-chk-skip-done" ${settings.skipAlreadyModeB ? 'checked' : ''} />
            <span>Pular Já Atualizados</span>
          </label>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          <button id="brk-btn-inject" class="brk-hud-btn brk-hud-btn-primary" title="Injeta a narrativa completa Modo B no editor HTML">
            ⚡ Injetar Modo B
          </button>
          <button id="brk-btn-copy" class="brk-hud-btn" title="Copia o HTML oficial para a área de transferência">
            📋 Copiar HTML
          </button>
          <button id="brk-btn-live-sync" class="brk-hud-btn" title="Trocou as fotos agora na Shopify? Clique para buscar as fotos novas ao vivo e recompilar os 3 Atos!">
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
      if (chkAutoSave) {
        chkAutoSave.onchange = (e) => saveSettings({ autoSave: e.target.checked });
      }
      const chkSkipDone = document.getElementById("brk-chk-skip-done");
      if (chkSkipDone) {
        chkSkipDone.onchange = (e) => saveSettings({ skipAlreadyModeB: e.target.checked });
      }

      // Eventos dos botões
      const btnInject = document.getElementById("brk-btn-inject");
      if (btnInject && prod) {
        btnInject.onclick = () => injectModoBIntoEditor(prod.mode_b_html);
      }

      const btnCopy = document.getElementById("brk-btn-copy");
      if (btnCopy && prod) {
        btnCopy.onclick = () => {
          const html = prod.mode_b_html || "";
          try { GM_setClipboard(html); } catch(e) {}
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(html).catch(() => {});
          }
          renderHudProductMode(prod, "📋 HTML Modo B Copiado!", `Copiados ${(html.length).toLocaleString('pt-BR')} caracteres da narrativa oficial Modo B. Cole com Ctrl+V no campo <> do editor.`);
        };
      }

      const btnLiveSync = document.getElementById("brk-btn-live-sync");
      if (btnLiveSync) {
        btnLiveSync.onclick = async () => {
          renderHudProductMode(prod, "🔄 Sincronizando Fotos ao Vivo...", "Buscando galeria atualizada na vitrine da Shopify e recompilando os 3 Atos...");
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
                `Galeria atualizada (${newCount} fotos únicas) e Modo B recompilado. Clique em 'Injetar Modo B'!`
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
        btnStart25.onclick = () => startQueueFromDatabase("SEM_DESCRICAO", 25);
      }
    }

    // =========================================================================
    // RENDERIZAÇÃO DO HUD NA LISTAGEM DE PRODUTOS (admin.shopify.com/.../products)
    // =========================================================================
    function renderHudListMode(stats) {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">🟢</span>
            <strong style="color:#38bdf8;font-size:13px;">BANCO DE DADOS BRK v3.0</strong>
          </div>
          <span style="font-size:11px;color:#94a3b8;font-weight:700;">${currentStoreName}</span>
        </div>

        <div style="margin-bottom:12px;font-size:12px;color:#cbd5e1;line-height:1.5;">
          ${stats ? `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
              <div>📦 Total: <strong>${stats.total_products}</strong></div>
              <div style="color:#4ade80;">✅ Saudáveis: <strong>${stats.healthy_count}</strong></div>
              <div style="color:#f87171;">⚠️ Sem Descrição: <strong>${stats.sem_descricao_count}</strong></div>
              <div style="color:#fbbf24;">🖼️ Fotos Quebradas: <strong>${stats.imagens_quebradas_count}</strong></div>
            </div>
          ` : 'Conectando à API oficial Vercel (6.408 produtos)...'}
        </div>

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:12px;">
          ${q.length > 0 ? `
            <div style="font-weight:700;color:#38bdf8;font-size:12px;">Fila Ativa: Item ${idx + 1} de ${q.length}</div>
            <div style="font-size:11px;color:#94a3b8;">Status: ${active ? 'Em andamento' : 'Pausado'}</div>
          ` : `
            <div style="font-weight:700;color:#38bdf8;font-size:12px;">Pronto para Automação em Lote</div>
            <div style="font-size:11px;color:#94a3b8;">Escolha abaixo para puxar produtos sem descrição ou com imagens quebradas da ${currentStoreName}.</div>
          `}
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          ${q.length > 0 ? `
            <button id="brk-btn-resume-queue" class="brk-hud-btn brk-hud-btn-primary">
              ▶️ Continuar Lote (${idx + 1}/${q.length})
            </button>
            <button id="brk-btn-clear-queue" class="brk-hud-btn brk-hud-btn-danger">
              ⏹️ Limpar Fila
            </button>
          ` : `
            <button id="brk-btn-fetch-empty-25" class="brk-hud-btn brk-hud-btn-primary">
              ▶️ Lote 25 (Sem Descrição)
            </button>
            <button id="brk-btn-fetch-broken-25" class="brk-hud-btn">
              🖼️ Lote 25 (Fotos Quebradas)
            </button>
            <button id="brk-btn-fetch-broken-50" class="brk-hud-btn">
              ⚡ Lote 50 (Quebradas)
            </button>
          `}
        </div>
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

      const btnFetchEmpty = document.getElementById("brk-btn-fetch-empty-25");
      if (btnFetchEmpty) {
        btnFetchEmpty.onclick = () => startQueueFromDatabase("SEM_DESCRICAO", 25);
      }

      const btnFetchBroken = document.getElementById("brk-btn-fetch-broken-25");
      if (btnFetchBroken) {
        btnFetchBroken.onclick = () => startQueueFromDatabase("IMAGENS_QUEBRADAS", 25);
      }

      const btnFetchBroken50 = document.getElementById("brk-btn-fetch-broken-50");
      if (btnFetchBroken50) {
        btnFetchBroken50.onclick = () => startQueueFromDatabase("IMAGENS_QUEBRADAS", 50);
      }
    }

    // =========================================================================
    // INICIAR FILA REAL BUSCADA DIRETAMENTE DO BANCO DE DADOS
    // =========================================================================
    async function startQueueFromDatabase(statusFilter, limit = 25) {
      hud.innerHTML = `
        <div style="padding:10px;text-align:center;">
          <div style="font-size:18px;margin-bottom:8px;">⏳</div>
          <strong style="color:#38bdf8;">Consultando Banco de Dados BRK...</strong>
          <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Buscando ${limit} produtos com status '${statusFilter}' na loja ${currentStoreName}...</div>
        </div>
      `;

      try {
        const res = await fetchFromBRKDatabase(`/api/product_db?store=${currentStoreKey}&action=queue&status=${statusFilter}&limit=${limit}`);
        if (!res.success || !res.items || res.items.length === 0) {
          alert(`Nenhum produto encontrado com status '${statusFilter}' no banco da loja ${currentStoreName}.`);
          initAdmin();
          return;
        }

        setQueue(res.items);
        setQueueIndex(0);
        setAutomationActive(true);

        const firstProduct = res.items[0];
        console.log(`[BRK-Tampermonkey v3.0] Lote de ${res.items.length} produtos carregado. Primeiro: ID ${firstProduct.id} (${firstProduct.master_sku})`);

        hud.innerHTML = `
          <div style="padding:10px;text-align:center;">
            <div style="font-size:18px;margin-bottom:8px;">🚀</div>
            <strong style="color:#22c55e;">Lote de ${res.items.length} Produtos Carregado!</strong>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Abrindo primeiro produto: ${firstProduct.master_sku}...</div>
          </div>
        `;

        setTimeout(() => {
          location.href = `https://admin.shopify.com/store/${currentShopifySlug}/products/${firstProduct.id}`;
        }, 1000);

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
            console.log("[BRK-Tampermonkey v3.0] Produto carregado com sucesso do banco:", activeLoadedProduct.master_sku);

            const q = getQueue();
            const idx = getQueueIndex();
            const inQueue = q.length > 0 && q[idx] && String(q[idx].id) === String(currentProductId);
            const active = isAutomationActive();
            const settings = getSettings();

            if (inQueue && active) {
              // Se o produto já possui Modo B aplicado no editor da Shopify e skipAlreadyModeB está ativo, avança!
              if (settings.skipAlreadyModeB && isAlreadyModeBInEditor()) {
                renderHudProductMode(
                  activeLoadedProduct,
                  "✅ Produto Já Possui Modo B!",
                  "Pulando automaticamente para o próximo item da fila..."
                );
                setTimeout(() => startCountdownToNext(), 800);
                return;
              }

              renderHudProductMode(activeLoadedProduct, "⚡ Modo Assistido Ativo", "Injetando descrição Modo B automaticamente...");
              setTimeout(() => {
                injectModoBIntoEditor(activeLoadedProduct.mode_b_html);
              }, 1100);
            } else {
              renderHudProductMode(
                activeLoadedProduct,
                alreadyHasModeBInDom() ? "✅ Modo B Já Aplicado neste Produto" : "Produto Identificado no Banco",
                "Clique em '⚡ Injetar Modo B', '📋 Copiar HTML' ou '🔄 Fotos Live'."
              );
            }
          } else {
            renderHudProductMode(null, "Produto não encontrado", `O ID ${currentProductId} não foi localizado no banco da loja ${currentStoreName}.`);
          }
        } catch(err) {
          console.error("[BRK-Tampermonkey v3.0] Erro ao carregar produto:", err);
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
          console.warn("[BRK-Tampermonkey v3.0] Não foi possível carregar estatísticas:", e);
        }
      }
    }

    function alreadyHasModeBInDom() {
      try { return isAlreadyModeBInEditor(); } catch(e) { return false; }
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
