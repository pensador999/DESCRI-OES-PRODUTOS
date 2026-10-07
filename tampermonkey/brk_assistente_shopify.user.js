// ==UserScript==
// @name         BRK Assistente de Descrições Shopify (Conectado ao Banco Real)
// @namespace    https://1025-ten.vercel.app/
// @version      2.0.0
// @description  Automação assistida conectada diretamente ao banco de dados oficial BRK (Vercel API) para preenchimento de descrições Modo B no Shopify Admin.
// @author       BRK Group & DeepMind Pair
// @match        https://admin.shopify.com/store/*/products*
// @match        https://1025-ten.vercel.app/*
// @match        http://localhost:*/*
// @match        http://127.0.0.1:*/*
// @connect      1025-ten.vercel.app
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

  // Configuração da API do Banco de Dados BRK
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
    autoSave: false // Modo Assistido: o usuário confirma ou o script orienta
  };

  function getSettings() {
    const raw = GM_getValue(STORAGE_KEYS.SETTINGS, null);
    if (!raw) return DEFAULT_SETTINGS;
    try { return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) }; } catch(e) { return DEFAULT_SETTINGS; }
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
      product_id: productId,
      handle: handle,
      saved_at: new Date().toISOString(),
      body_html: originalHtml
    });
    if (arr.length > 50) arr = arr.slice(0, 50);
    GM_setValue(STORAGE_KEYS.BACKUP, JSON.stringify(arr));
  }

  // =========================================================================
  // COMUNICAÇÃO HTTP COM A API REAL DO BANCO DE DADOS BRK
  // =========================================================================
  function fetchFromBRKDatabase(endpoint) {
    return new Promise((resolve, reject) => {
      const url = `${API_BASE}${endpoint}`;
      console.log(`[BRK-DB] Requisitando: ${url}`);
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
          console.error("[BRK-DB] Falha de rede:", err);
          reject(new Error("Falha na conexão com a API da Vercel. Verifique a internet."));
        }
      });
    });
  }

  // =========================================================================
  // 1. LÓGICA NO PORTAL LOCAL OU VERCEL (1025-ten.vercel.app)
  // =========================================================================
  if (location.hostname === "1025-ten.vercel.app" || location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    console.log("[BRK-Tampermonkey] Conectado ao Portal de Descrições BRK.");
    window.__BRK_TAMPERMONKEY_INSTALLED = true;
    document.documentElement.setAttribute("data-tampermonkey-active", "true");

    const badge = document.createElement("div");
    badge.id = "brk-tm-portal-badge";
    badge.style.cssText = "position:fixed;bottom:16px;left:16px;z-index:99999;background:#0f172a;border:1px solid #0284c7;color:#38bdf8;padding:8px 14px;border-radius:9999px;font-size:12px;font-weight:800;display:flex;align-items:center;gap:8px;box-shadow:0 4px 16px rgba(0,0,0,0.4);cursor:pointer;font-family:sans-serif;";
    badge.innerHTML = "<span>🟢 Tampermonkey Conectado ao Banco BRK v2.0</span>";
    badge.onclick = () => {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      alert(`[Assistente BRK Status]\n\nFila no Tampermonkey: ${q.length} produtos\nÍndice Atual: ${idx + 1} de ${q.length}\nAutomação Ativa: ${active ? "SIM" : "NÃO"}`);
    };
    document.body.appendChild(badge);
    return;
  }

  // =========================================================================
  // 2. LÓGICA NO SHOPIFY ADMIN (admin.shopify.com/store/*/products*)
  // =========================================================================
  if (location.hostname === "admin.shopify.com") {
    const urlPath = location.pathname;
    const storeMatch = urlPath.match(/\/store\/([^\/]+)/);
    const shopifySlug = storeMatch ? storeMatch[1].toLowerCase() : "";
    const storeKey = STORE_SLUG_MAP[shopifySlug] || "brk_fishing";
    const storeName = STORE_NAMES[storeKey] || "BRK Fishing";

    const productMatch = urlPath.match(/\/products\/(\d+)/);
    const currentProductId = productMatch ? productMatch[1] : null;

    console.log(`[BRK-Tampermonkey] Shopify Admin Detectado | Loja: ${storeName} (${shopifySlug}) | Produto ID: ${currentProductId || 'Listagem'}`);

    // Injetar Estilos Visuais do HUD e Pulso do Botão Salvar
    const styleEl = document.createElement("style");
    styleEl.id = "brk-tm-styles";
    styleEl.textContent = `
      @keyframes brkSaveGlow {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.8); transform: scale(1); }
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
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        min-width: 360px;
        max-width: 480px;
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
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
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
    `;
    document.head.appendChild(styleEl);

    // Criar elemento do HUD
    const hud = document.createElement("div");
    hud.id = "brk-tm-hud";
    document.body.appendChild(hud);

    let activeLoadedProduct = null;
    let countdownTimer = null;

    // =========================================================================
    // INJEÇÃO COMPATÍVEL COM REACT NO EDITOR SHOPIFY POLARIS
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
    }

    function highlightSaveButton(onSaveCallback) {
      const buttons = Array.from(document.querySelectorAll("button"));
      const saveBtn = buttons.find(b => {
        const text = (b.innerText || b.textContent || "").trim().toLowerCase();
        return text === "salvar" || text === "save";
      });

      if (saveBtn) {
        saveBtn.classList.add("brk-pulse-save-button");
        saveBtn.scrollIntoView({ behavior: "smooth", block: "nearest" });

        const handler = () => {
          saveBtn.classList.remove("brk-pulse-save-button");
          saveBtn.removeEventListener("click", handler);
          if (onSaveCallback) onSaveCallback();
        };
        saveBtn.addEventListener("click", handler);
        return true;
      }
      return false;
    }

    function injectModoBIntoEditor(htmlContent) {
      if (!htmlContent) {
        alert("Conteúdo Modo B vazio no banco de dados.");
        return false;
      }

      // 1. Procurar o botão de alternar modo HTML (<>)
      const allButtons = Array.from(document.querySelectorAll("button"));
      const htmlBtn = allButtons.find(b => {
        const aria = (b.getAttribute("aria-label") || "").toLowerCase();
        const title = (b.getAttribute("title") || "").toLowerCase();
        const text = (b.innerText || "").trim();
        return aria.includes("html") || aria.includes("código") || title.includes("html") || text === "<>" || aria === "code";
      });

      // 2. Procurar o textarea do editor
      let textarea = document.querySelector("textarea[name*='description']") || 
                     document.querySelector("textarea[id*='description']") || 
                     document.querySelector(".Polaris-Textarea__Input") ||
                     document.querySelector("textarea");

      // Se achou o botão HTML e o textarea ainda não está visível, clica no botão HTML (<>)
      if (htmlBtn && (!textarea || textarea.offsetParent === null)) {
        console.log("[BRK-Tampermonkey] Clicando no botão '<>' para abrir modo HTML...");
        htmlBtn.click();
      }

      setTimeout(() => {
        textarea = document.querySelector("textarea[name*='description']") || 
                   document.querySelector("textarea[id*='description']") || 
                   document.querySelector(".Polaris-Textarea__Input") ||
                   document.querySelector("textarea");

        if (textarea) {
          appendBackup(currentProductId, location.pathname, textarea.value);
          setReactInputValue(textarea, htmlContent);
          console.log("[BRK-Tampermonkey] HTML Modo B injetado com sucesso no Textarea!");

          highlightSaveButton(() => {
            console.log("[BRK-Tampermonkey] Botão Salvar clicado pelo usuário!");
            handleAfterSave();
          });

          renderHudProductMode(activeLoadedProduct, "✨ Descrição Injetada com Sucesso!", "Clique em 'Salvar' (botão verde pulsando) no topo da página.");
        } else {
          // Fallback contenteditable
          const editable = document.querySelector("[contenteditable='true']");
          if (editable) {
            appendBackup(currentProductId, location.pathname, editable.innerHTML);
            editable.innerHTML = htmlContent;
            editable.dispatchEvent(new Event("input", { bubbles: true }));
            highlightSaveButton(() => handleAfterSave());
            renderHudProductMode(activeLoadedProduct, "✨ Injetado no Editor Visual!", "Clique em 'Salvar' no topo.");
          } else {
            alert("Não foi possível localizar o editor de descrição da Shopify. Por favor, clique no botão '<>' do editor e use 'Copiar HTML' no painel.");
          }
        }
      }, 600);

      return true;
    }

    function handleAfterSave() {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();

      if (active && q.length > 0 && idx < q.length - 1) {
        startCountdownToNext();
      } else if (active && idx >= q.length - 1) {
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

      if (countdownTimer) clearInterval(countdownTimer);

      countdownTimer = setInterval(() => {
        if (count <= 0) {
          clearInterval(countdownTimer);
          setQueueIndex(nextIdx);
          const nextUrl = `https://admin.shopify.com/store/${shopifySlug}/products/${nextItem.id}`;
          location.href = nextUrl;
        } else {
          renderHudProductMode(activeLoadedProduct, `⏱️ Salvo! Avançando em ${count}s...`, `Próximo: ${nextItem.master_sku || ''} - ${nextItem.title.slice(0, 35)}...`);
          count--;
        }
      }, 1000);
    }

    const injectDescriptionIntoShopify = injectModoBIntoEditor;
    const advanceToNextProduct = startCountdownToNext;

    // =========================================================================
    // RENDENRIZAÇÃO DO HUD NA PÁGINA DO PRODUTO (admin.shopify.com/.../products/{id})
    // =========================================================================
    function renderHudProductMode(prod, statusTitle, statusSub) {
      const q = getQueue();
      const idx = getQueueIndex();
      const inQueue = q.length > 0 && q[idx] && String(q[idx].id) === String(currentProductId);
      const active = isAutomationActive();

      let statusBadgeClass = "brk-badge-healthy";
      if (prod?.status === "SEM_DESCRICAO") statusBadgeClass = "brk-badge-empty";
      else if (prod?.status === "IMAGENS_QUEBRADAS") statusBadgeClass = "brk-badge-broken";

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">🟢</span>
            <strong style="color:#38bdf8;font-size:13px;">BANCO BRK CONECTADO</strong>
          </div>
          <span style="font-size:11px;color:#94a3b8;font-weight:700;">
            ${inQueue ? `Lote: Item ${idx + 1} de ${q.length}` : `${storeName}`}
          </span>
        </div>

        <div style="margin-bottom:12px;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
            <span style="font-weight:800;color:#f8fafc;font-size:14px;">${prod ? (prod.master_sku || 'Sem SKU') : 'Carregando...'}</span>
            ${prod ? `<span class="brk-badge-status ${statusBadgeClass}">${prod.status}</span>` : ''}
          </div>
          <div style="font-size:12px;color:#cbd5e1;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:400px;">
            ${prod ? prod.title : 'Consultando dados reais na API...'}
          </div>
        </div>

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:12px;">
          <div style="font-weight:700;color:#38bdf8;font-size:12px;">${statusTitle || "Pronto para Injeção"}</div>
          <div style="font-size:11px;color:#94a3b8;line-height:1.4;">${statusSub || "Clique em 'Injetar Modo B' para aplicar a descrição oficial."}</div>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          <button id="brk-btn-inject" class="brk-hud-btn brk-hud-btn-primary">
            ⚡ Injetar Modo B
          </button>
          <button id="brk-btn-copy" class="brk-hud-btn">
            📋 Copiar HTML
          </button>
          ${inQueue ? `
            <button id="brk-btn-next-now" class="brk-hud-btn">
              ⏭️ Pular/Próximo
            </button>
            <button id="brk-btn-pause-queue" class="brk-hud-btn brk-hud-btn-danger">
              ⏹️ Parar Lote
            </button>
          ` : `
            <button id="brk-btn-start-queue-25" class="brk-hud-btn brk-hud-btn-success">
              ▶️ Iniciar Lote 25
            </button>
          `}
        </div>
      `;

      // Eventos dos botões
      const btnInject = document.getElementById("brk-btn-inject");
      if (btnInject && prod) {
        btnInject.onclick = () => injectModoBIntoEditor(prod.mode_b_html);
      }

      const btnCopy = document.getElementById("brk-btn-copy");
      if (btnCopy && prod) {
        btnCopy.onclick = () => {
          GM_setClipboard(prod.mode_b_html);
          renderHudProductMode(prod, "📋 HTML Copiado!", "Cole diretamente com Ctrl+V no campo de código HTML (<>).");
        };
      }

      const btnNextNow = document.getElementById("brk-btn-next-now");
      if (btnNextNow) {
        btnNextNow.onclick = () => {
          if (countdownTimer) clearInterval(countdownTimer);
          const nextIdx = idx + 1;
          if (nextIdx < q.length) {
            setQueueIndex(nextIdx);
            location.href = `https://admin.shopify.com/store/${shopifySlug}/products/${q[nextIdx].id}`;
          } else {
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
    // RENDENRIZAÇÃO DO HUD NA LISTAGEM DE PRODUTOS (admin.shopify.com/.../products)
    // =========================================================================
    function renderHudListMode(stats) {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();

      hud.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">🟢</span>
            <strong style="color:#38bdf8;font-size:13px;">BANCO DE DADOS BRK</strong>
          </div>
          <span style="font-size:11px;color:#94a3b8;font-weight:700;">${storeName}</span>
        </div>

        <div style="margin-bottom:12px;font-size:12px;color:#cbd5e1;line-height:1.4;">
          ${stats ? `
            <div>📦 Total no Banco: <strong>${stats.total_products}</strong></div>
            <div style="color:#f87171;">⚠️ Sem Descrição: <strong>${stats.sem_descricao_count}</strong></div>
            <div style="color:#fbbf24;">🖼️ Imagens Quebradas: <strong>${stats.imagens_quebradas_count}</strong></div>
          ` : 'Conectado à API oficial Vercel.'}
        </div>

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:8px 12px;margin-bottom:12px;">
          ${q.length > 0 ? `
            <div style="font-weight:700;color:#38bdf8;font-size:12px;">Fila Ativa: Item ${idx + 1} de ${q.length}</div>
            <div style="font-size:11px;color:#94a3b8;">Status: ${active ? 'Em andamento' : 'Pausado'}</div>
          ` : `
            <div style="font-weight:700;color:#38bdf8;font-size:12px;">Nenhum Lote em Execução</div>
            <div style="font-size:11px;color:#94a3b8;">Clique abaixo para carregar 25 produtos reais sem descrição do banco.</div>
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
              ▶️ Iniciar Lote 25 (Sem Descrição)
            </button>
            <button id="brk-btn-fetch-broken-25" class="brk-hud-btn">
              🖼️ Puxar 25 (Imagens Quebradas)
            </button>
          `}
        </div>
      `;

      const btnResume = document.getElementById("brk-btn-resume-queue");
      if (btnResume) {
        btnResume.onclick = () => {
          setAutomationActive(true);
          const currentItem = q[idx] || q[0];
          location.href = `https://admin.shopify.com/store/${shopifySlug}/products/${currentItem.id}`;
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
    }

    // =========================================================================
    // INICIAR FILA REAL BUSCADA DIRETAMENTE DO BANCO DE DADOS
    // =========================================================================
    async function startQueueFromDatabase(statusFilter, limit = 25) {
      hud.innerHTML = `
        <div style="padding:10px;text-align:center;">
          <div style="font-size:18px;margin-bottom:8px;">⏳</div>
          <strong style="color:#38bdf8;">Consultando Banco de Dados BRK...</strong>
          <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Buscando ${limit} produtos com status '${statusFilter}' na loja ${storeName}...</div>
        </div>
      `;

      try {
        const res = await fetchFromBRKDatabase(`/api/product_db?store=${storeKey}&action=queue&status=${statusFilter}&limit=${limit}`);
        if (!res.success || !res.items || res.items.length === 0) {
          alert(`Nenhum produto encontrado com status '${statusFilter}' no banco da loja ${storeName}.`);
          initAdmin();
          return;
        }

        setQueue(res.items);
        setQueueIndex(0);
        setAutomationActive(true);

        const firstProduct = res.items[0];
        console.log(`[BRK-Tampermonkey] Lote de ${res.items.length} produtos carregado do banco. Primeiro: ID ${firstProduct.id} (${firstProduct.master_sku})`);

        hud.innerHTML = `
          <div style="padding:10px;text-align:center;">
            <div style="font-size:18px;margin-bottom:8px;">🚀</div>
            <strong style="color:#22c55e;">Lote de ${res.items.length} Produtos Carregado!</strong>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Abrindo primeiro produto: ${firstProduct.master_sku}...</div>
          </div>
        `;

        setTimeout(() => {
          location.href = `https://admin.shopify.com/store/${shopifySlug}/products/${firstProduct.id}`;
        }, 1200);

      } catch(err) {
        alert(`Erro ao buscar lote do banco de dados: ${err.message}`);
        initAdmin();
      }
    }

    // =========================================================================
    // INICIALIZAÇÃO NO SHOPIFY ADMIN
    // =========================================================================
    async function initAdmin() {
      // Caso 1: Estamos na página de edição de um produto específico
      if (currentProductId) {
        renderHudProductMode(null, "Consultando Banco BRK...", `Buscando produto ID ${currentProductId}...`);

        try {
          const res = await fetchFromBRKDatabase(`/api/product_db?store=${storeKey}&id=${currentProductId}`);
          if (res.success && res.product) {
            activeLoadedProduct = res.product;
            console.log("[BRK-Tampermonkey] Produto carregado com sucesso do banco:", activeLoadedProduct.master_sku);

            const q = getQueue();
            const idx = getQueueIndex();
            const inQueue = q.length > 0 && q[idx] && String(q[idx].id) === String(currentProductId);
            const active = isAutomationActive();

            if (inQueue && active) {
              renderHudProductMode(activeLoadedProduct, "⚡ Modo Assistido Ativo", "Injetando descrição automaticamente...");
              setTimeout(() => {
                injectModoBIntoEditor(activeLoadedProduct.mode_b_html);
              }, 1200);
            } else {
              renderHudProductMode(activeLoadedProduct, "Produto Identificado no Banco", "Clique em 'Injetar Modo B' ou 'Copiar HTML'.");
            }
          } else {
            renderHudProductMode(null, "Produto não encontrado", `O ID ${currentProductId} não foi localizado no banco da loja ${storeName}.`);
          }
        } catch(err) {
          console.error("[BRK-Tampermonkey] Erro ao carregar produto:", err);
          renderHudProductMode(null, "Erro de Conexão com a API", err.message);
        }
      } 
      // Caso 2: Estamos na listagem de produtos (/products)
      else {
        renderHudListMode(null);
        try {
          const stats = await fetchFromBRKDatabase(`/api/product_db?store=${storeKey}&action=stats`);
          if (stats.success) {
            renderHudListMode(stats);
          }
        } catch(e) {
          console.warn("[BRK-Tampermonkey] Não foi possível carregar estatísticas:", e);
        }
      }
    }

    // Iniciar após pequeno delay para o DOM do Shopify Admin estabilizar
    setTimeout(initAdmin, 1000);
  }

})();
