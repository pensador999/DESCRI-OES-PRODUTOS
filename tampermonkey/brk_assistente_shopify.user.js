// ==UserScript==
// @name         BRK Assistente de Descrições Shopify (Modo Assistido)
// @namespace    https://1025-ten.vercel.app/
// @version      1.0.0
// @description  Automação assistida para preenchimento de descrições comerciais Modo B no Admin da Shopify (BRK Fishing, Agro, Motors)
// @author       BRK Group & DeepMind Pair
// @match        https://admin.shopify.com/store/*/products*
// @match        https://1025-ten.vercel.app/*
// @match        http://localhost:*/*
// @match        http://127.0.0.1:*/*
// @match        file://*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_notification
// @grant        GM_setClipboard
// @run-at       document-idle
// ==/UserScript==

(function() {
  'use strict';

  const STORAGE_KEYS = {
    QUEUE: "BRK_AUTOSYNC_QUEUE",
    INDEX: "BRK_AUTOSYNC_INDEX",
    ACTIVE: "BRK_AUTOSYNC_ACTIVE",
    BACKUP: "BRK_AUTOSYNC_BACKUP",
    SETTINGS: "BRK_AUTOSYNC_SETTINGS"
  };

  const DEFAULT_SETTINGS = {
    delaySeconds: 4,
    autoSave: false, // false = Modo Assistido (você clica em Salvar)
    storeSlugMap: {
      "brk_fishing": "brkfishing",
      "brk_agro": "brkagro",
      "brk_motors": "brkmotors25"
    }
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
    if (arr.length > 100) arr = arr.slice(0, 100);
    GM_setValue(STORAGE_KEYS.BACKUP, JSON.stringify(arr));
  }

  // =========================================================================
  // 1. LÓGICA NO PORTAL (Vercel ou Local)
  // =========================================================================
  if (location.hostname === "1025-ten.vercel.app" || location.hostname === "localhost" || location.hostname === "127.0.0.1" || location.protocol === "file:") {
    console.log("[BRK-Tampermonkey] Conectado ao Portal de Descrições BRK.");

    // Avisar o portal que o Tampermonkey está presente e ativo
    window.__BRK_TAMPERMONKEY_INSTALLED = true;
    document.documentElement.setAttribute("data-tampermonkey-active", "true");

    // Escutar comandos enviados pelo portal via postMessage
    window.addEventListener("message", (event) => {
      if (!event.data || typeof event.data !== "object") return;
      const { type, payload } = event.data;

      if (type === "BRK_LOAD_QUEUE") {
        const items = payload.items || [];
        const storeKey = payload.storeKey || "brk_fishing";
        const autoStart = payload.autoStart !== false;

        if (items.length === 0) {
          alert("A fila enviada está vazia.");
          return;
        }

        setQueue(items);
        setQueueIndex(0);
        setAutomationActive(autoStart);

        console.log(`[BRK-Tampermonkey] Fila carregada com ${items.length} produtos.`);

        const settings = getSettings();
        const slug = settings.storeSlugMap[storeKey] || "brkfishing";
        const firstId = items[0].id;
        const targetUrl = `https://admin.shopify.com/store/${slug}/products/${firstId}`;

        if (confirm(`⚡ Fila com ${items.length} produtos da ${storeKey.toUpperCase()} pronta no Tampermonkey!\n\nDeseja abrir o primeiro produto no Shopify Admin agora?\nURL: ${targetUrl}`)) {
          window.open(targetUrl, "_blank");
        }
      }
    });

    // Badge visual no portal
    const badge = document.createElement("div");
    badge.id = "brk-tm-portal-badge";
    badge.style.cssText = "position:fixed;bottom:12px;left:12px;z-index:99999;background:#0f172a;border:1px solid #334155;color:#38bdf8;padding:6px 12px;border-radius:9999px;font-size:11px;font-weight:800;display:flex;align-items:center;gap:6px;box-shadow:0 4px 12px rgba(0,0,0,0.3);cursor:pointer;font-family:sans-serif;";
    badge.innerHTML = "<span>🤖 Tampermonkey Conectado</span>";
    badge.title = "Clique para inspecionar a fila atual do Tampermonkey";
    badge.onclick = () => {
      const q = getQueue();
      const idx = getQueueIndex();
      const active = isAutomationActive();
      alert(`[Tampermonkey BRK Status]\n\nProdutos na Fila: ${q.length}\nÍndice Atual: ${idx + 1} de ${q.length}\nAutomação Ativa: ${active ? "SIM" : "NÃO"}`);
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
    const currentStoreSlug = storeMatch ? storeMatch[1] : "";
    const productMatch = urlPath.match(/\/products\/(\d+)/);
    const currentProductId = productMatch ? productMatch[1] : null;

    console.log(`[BRK-Tampermonkey] Shopify Admin detectado: Loja '${currentStoreSlug}' | Produto '${currentProductId || 'Listagem'}'`);

    // Injetar CSS de animação para destacar o botão Salvar
    const styleEl = document.createElement("style");
    styleEl.id = "brk-tm-styles";
    styleEl.textContent = `
      @keyframes brkSaveGlow {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); transform: scale(1); }
        50% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); transform: scale(1.03); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); transform: scale(1); }
      }
      .brk-pulse-save-button {
        animation: brkSaveGlow 1.4s infinite !important;
        background-color: #15803d !important;
        border-color: #166534 !important;
        color: #ffffff !important;
        font-weight: 800 !important;
      }
      #brk-tm-hud {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 999999;
        background: #0f172a;
        color: #f8fafc;
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        min-width: 320px;
        max-width: 440px;
        transition: all 0.3s ease;
      }
      #brk-tm-hud-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
      }
      .brk-hud-btn {
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
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
      .brk-hud-btn-danger {
        background: #991b1b;
        border-color: #7f1d1d;
        color: #fee2e2;
      }
      .brk-hud-btn-danger:hover {
        background: #b91c1c;
      }
    `;
    document.head.appendChild(styleEl);

    // =========================================================================
    // HUD FLUTUANTE DE CONTROLE
    // =========================================================================
    const hud = document.createElement("div");
    hud.id = "brk-tm-hud";
    document.body.appendChild(hud);

    function updateHud(statusText, subText, options = {}) {
      const q = getQueue();
      const idx = getQueueIndex();
      const total = q.length;
      const active = isAutomationActive();
      const currentItem = q[idx] || null;

      hud.innerHTML = `
        <div id="brk-tm-hud-header">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:16px;">⚡</span>
            <strong style="color:#38bdf8;font-size:13px;">Assistente BRK</strong>
            <span style="background:${active ? '#166534' : '#475569'};color:#ffffff;font-size:10px;padding:2px 8px;border-radius:9999px;font-weight:800;">
              ${active ? 'ATIVO' : 'PAUSADO'}
            </span>
          </div>
          <span style="font-size:11px;color:#94a3b8;font-weight:700;">
            ${total > 0 ? `Item ${idx + 1} de ${total}` : 'Fila Vazia'}
          </span>
        </div>
        <div style="margin-bottom:10px;">
          <div style="font-weight:700;color:#ffffff;margin-bottom:2px;">${statusText}</div>
          <div style="font-size:11px;color:#94a3b8;line-height:1.4;">${subText || (currentItem ? `${currentItem.master_sku || ''} - ${currentItem.title.slice(0, 45)}...` : 'Aguardando lote')}</div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          ${active ? `<button id="brk-btn-pause" class="brk-hud-btn">⏸️ Pausar</button>` : `<button id="brk-btn-resume" class="brk-hud-btn brk-hud-btn-primary">▶️ Iniciar Lote</button>`}
          <button id="brk-btn-next" class="brk-hud-btn">⏭️ Próximo</button>
          <button id="brk-btn-paste-raw" class="brk-hud-btn" title="Inserir HTML manualmente se necessário">📋 Colar Aqui</button>
          <button id="brk-btn-stop" class="brk-hud-btn brk-hud-btn-danger" title="Limpar fila atual">⏹️ Limpar Fila</button>
        </div>
      `;

      // Eventos dos botões do HUD
      const btnPause = document.getElementById("brk-btn-pause");
      if (btnPause) btnPause.onclick = () => { setAutomationActive(false); updateHud("Pausado pelo usuário", "Clique em Iniciar para continuar de onde parou."); };

      const btnResume = document.getElementById("brk-btn-resume");
      if (btnResume) btnResume.onclick = () => {
        setAutomationActive(true);
        if (total > 0 && currentItem) {
          const targetUrl = `https://admin.shopify.com/store/${currentStoreSlug}/products/${currentItem.id}`;
          if (location.href !== targetUrl) {
            location.href = targetUrl;
          } else {
            processCurrentProductPage();
          }
        } else {
          alert("Fila vazia. Envie um lote pelo portal ou clique em Limpar Fila.");
        }
      };

      const btnNext = document.getElementById("brk-btn-next");
      if (btnNext) btnNext.onclick = () => advanceToNextProduct(0);

      const btnPasteRaw = document.getElementById("brk-btn-paste-raw");
      if (btnPasteRaw) btnPasteRaw.onclick = () => {
        if (!currentItem) { alert("Nenhum produto selecionado."); return; }
        injectDescriptionIntoShopify(currentItem.mode_b_html || currentItem.html);
      };

      const btnStop = document.getElementById("brk-btn-stop");
      if (btnStop) btnStop.onclick = () => {
        if (confirm("Deseja realmente limpar a fila atual do Tampermonkey?")) {
          setQueue([]);
          setQueueIndex(0);
          setAutomationActive(false);
          updateHud("Fila Limpa", "Nenhum produto em processamento.");
        }
      };
    }

    // =========================================================================
    // NAVEGAÇÃO E PROCESSAMENTO DE PRODUTO
    // =========================================================================
    function advanceToNextProduct(delaySecs = 4) {
      const q = getQueue();
      const currentIdx = getQueueIndex();
      const nextIdx = currentIdx + 1;

      if (nextIdx >= q.length) {
        setAutomationActive(false);
        setQueueIndex(0);
        updateHud("🎉 Lote Concluído!", `Todos os ${q.length} produtos foram processados com sucesso.`);
        alert(`🎉 Parabéns! Lote de ${q.length} produtos concluído no Shopify Admin.`);
        return;
      }

      setQueueIndex(nextIdx);
      const nextItem = q[nextIdx];
      const targetUrl = `https://admin.shopify.com/store/${currentStoreSlug}/products/${nextItem.id}`;

      let count = delaySecs;
      if (count <= 0) {
        location.href = targetUrl;
        return;
      }

      const countdownInterval = setInterval(() => {
        updateHud(`Avançando em ${count}s...`, `Próximo: ${nextItem.master_sku || ''} - ${nextItem.title.slice(0, 40)}`);
        count--;
        if (count < 0) {
          clearInterval(countdownInterval);
          location.href = targetUrl;
        }
      }, 1000);
    }

    // Localizar e destacar o botão Salvar da Shopify
    function highlightSaveButton() {
      // Procurar botões com texto 'Salvar' ou 'Save'
      const buttons = Array.from(document.querySelectorAll("button"));
      const saveBtn = buttons.find(b => {
        const text = (b.innerText || b.textContent || "").trim().toLowerCase();
        return text === "salvar" || text === "save";
      });

      if (saveBtn) {
        saveBtn.classList.add("brk-pulse-save-button");
        saveBtn.scrollIntoView({ behavior: "smooth", block: "nearest" });

        // Escutar o clique no botão salvar para avançar automaticamente
        const onSaveClick = () => {
          saveBtn.classList.remove("brk-pulse-save-button");
          saveBtn.removeEventListener("click", onSaveClick);
          console.log("[BRK-Tampermonkey] Botão Salvar clicado pelo usuário! Iniciando contagem de avanço...");

          const settings = getSettings();
          advanceToNextProduct(settings.delaySeconds || 4);
        };
        saveBtn.addEventListener("click", onSaveClick);
      }
    }

    // Injetar HTML no editor de texto da Shopify
    function injectDescriptionIntoShopify(htmlContent) {
      if (!htmlContent) {
        alert("Erro: Conteúdo HTML vazio.");
        return false;
      }

      // 1. Procurar o botão de alternar HTML (<>)
      // Polaris rich text editor geralmente tem botões com aria-label="Show HTML" ou "Exibir código HTML"
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

      // Se encontrou botão HTML e o textarea ainda não está visível, clica no botão HTML
      if (htmlBtn && (!textarea || textarea.offsetParent === null)) {
        console.log("[BRK-Tampermonkey] Clicando no botão '<>' (Exibir HTML)...");
        htmlBtn.click();
      }

      setTimeout(() => {
        textarea = document.querySelector("textarea[name*='description']") || 
                   document.querySelector("textarea[id*='description']") || 
                   document.querySelector(".Polaris-Textarea__Input") ||
                   document.querySelector("textarea");

        if (textarea) {
          // Backup do valor anterior
          appendBackup(currentProductId, location.pathname, textarea.value);

          console.log("[BRK-Tampermonkey] Textarea do HTML encontrado. Inserindo Modo B...");
          textarea.value = htmlContent;

          // Disparar eventos nativos para o React reconhecer o dirty state
          textarea.dispatchEvent(new Event("input", { bubbles: true }));
          textarea.dispatchEvent(new Event("change", { bubbles: true }));
          textarea.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));

          updateHud("✨ Modo B Inserido!", "Clique no botão verde SALVAR no topo para concluir.", { waitingSave: true });
          highlightSaveButton();
        } else {
          // Fallback para contenteditable / iframe
          const editableDiv = document.querySelector("[contenteditable='true']") || document.querySelector(".tox-edit-area iframe");
          if (editableDiv) {
            console.log("[BRK-Tampermonkey] Injetando no contenteditable...");
            if (editableDiv.tagName === "IFRAME") {
              editableDiv.contentDocument.body.innerHTML = htmlContent;
            } else {
              editableDiv.innerHTML = htmlContent;
            }
            editableDiv.dispatchEvent(new Event("input", { bubbles: true }));
            updateHud("✨ Modo B Inserido no Editor!", "Clique no botão SALVAR para concluir.");
            highlightSaveButton();
          } else {
            console.warn("[BRK-Tampermonkey] Editor da Shopify não encontrado automaticamente.");
            updateHud("⚠️ Editor não detectado", "Clique no botão '<>' manualmente e use o botão 'Colar Aqui' do painel.");
          }
        }
      }, 500);

      return true;
    }

    function processCurrentProductPage() {
      const q = getQueue();
      const idx = getQueueIndex();
      const currentItem = q[idx];

      if (!currentItem) {
        updateHud("Fila Finalizada", "Todos os itens deste lote foram concluídos.");
        return;
      }

      // Validar se o ID da página bate com o item atual
      if (String(currentItem.id) !== String(currentProductId)) {
        updateHud("Aguardando Produto Correto", `Página atual (${currentProductId}) difere da fila (${currentItem.id}). Redirecionando...`);
        const targetUrl = `https://admin.shopify.com/store/${currentStoreSlug}/products/${currentItem.id}`;
        setTimeout(() => { location.href = targetUrl; }, 1000);
        return;
      }

      updateHud("Injetando Modo B...", `Produto: ${currentItem.title.slice(0, 45)}`);

      // Aguardar 1.2 segundos para garantir que os componentes React do Polaris terminaram de montar
      setTimeout(() => {
        injectDescriptionIntoShopify(currentItem.mode_b_html || currentItem.html);
      }, 1200);
    }

    // Inicialização na página
    const queue = getQueue();
    const active = isAutomationActive();

    if (currentProductId && queue.length > 0 && active) {
      processCurrentProductPage();
    } else {
      updateHud(
        queue.length > 0 ? `${queue.length} produtos na fila` : "Assistente Pronto",
        queue.length > 0 ? (active ? "Pronto para processar" : "Pausado. Clique em Iniciar Lote para começar.") : "Gere uma fila no Portal BRK para começar."
      );
    }
  }

})();
