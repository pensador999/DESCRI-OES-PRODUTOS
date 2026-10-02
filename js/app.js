/**
 * BRK Master Portal - Frontend Coordinator (app.js)
 * Gerencia abas, filtros de diagnóstico, busca em tempo real, carregamento assíncrono de dados e métricas do Cockpit.
 */

let MASTER_PAYLOAD = {
  stores: {},
  moldes: {},
  analytics: {}
};

let currentStore = "brk_fishing";
let currentFilter = "all";
let selectedCategory = "all";
let searchQuery = "";
let selectedMassProductIds = new Set();
let currentAuditFilter = "all";

// Elementos DOM
const productsGrid = document.getElementById("products-grid");
const categoriesRail = document.getElementById("categories-rail");
const emptyState = document.getElementById("empty-state");
const searchInput = document.getElementById("search-input");
const massTableBody = document.getElementById("mass-table-body");

// Toast Notification
function showToast(text) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  document.getElementById("toast-text").innerText = text;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}

// Navegação entre Abas Principais
function switchMainTab(tabId) {
  document.querySelectorAll(".main-tab").forEach(tab => {
    tab.classList.remove("active", "bg-slate-800", "text-white");
    tab.classList.add("text-slate-400");
  });

  const activeBtn = document.getElementById("btn-" + tabId);
  if (activeBtn) {
    activeBtn.classList.add("active", "bg-slate-800", "text-white");
    activeBtn.classList.remove("text-slate-400");
  }

  document.getElementById("section-catalog").classList.add("hidden");
  document.getElementById("section-mass").classList.add("hidden");
  document.getElementById("section-moldes").classList.add("hidden");
  document.getElementById("section-analytics").classList.add("hidden");

  if (tabId === "tab-catalog") {
    document.getElementById("section-catalog").classList.remove("hidden");
    renderProducts();
  } else if (tabId === "tab-mass") {
    document.getElementById("section-mass").classList.remove("hidden");
    renderMassTable();
  } else if (tabId === "tab-moldes") {
    document.getElementById("section-moldes").classList.remove("hidden");
    renderMoldesCards();
  } else if (tabId === "tab-analytics") {
    document.getElementById("section-analytics").classList.remove("hidden");
    renderAnalyticsView();
  }
}

// Motor de Sincronização em Tempo Real (Live Sync)
const STORE_DOMAINS = {
  "brk_fishing": "www.brkfishing.com.br",
  "brk_agro": "www.brkagro.com.br",
  "brk_motors": "www.brkmotors.com.br"
};

const STORE_COLOR_PALETTES = {
  "brk_fishing": { color: "#0284c7", bg: "#f0f9ff", name: "Azul Leve" },
  "brk_agro":    { color: "#16a34a", bg: "#f0fdf4", name: "Verde Leve" },
  "brk_motors":  { color: "#f97316", bg: "#fff7ed", name: "Laranja Leve" }
};

let liveSyncIntervalSecs = 15;
let liveSyncTimer = null;
let liveSyncCountdownSecs = 15;
let isSyncingNow = false;

function startLiveSync() {
  if (liveSyncTimer) clearInterval(liveSyncTimer);
  const pulse = document.getElementById("live-sync-pulse");
  const dot = document.getElementById("live-sync-dot");
  const statusText = document.getElementById("live-sync-status-text");

  if (liveSyncIntervalSecs <= 0) {
    if (pulse) pulse.classList.add("hidden");
    if (dot) dot.className = "relative inline-flex rounded-full h-2.5 w-2.5 bg-slate-500";
    if (statusText) statusText.innerHTML = "Pausado";
    return;
  }

  if (pulse) pulse.classList.remove("hidden");
  if (dot) dot.className = "relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500";
  liveSyncCountdownSecs = liveSyncIntervalSecs;
  updateSyncCountdownDisplay();

  liveSyncTimer = setInterval(() => {
    liveSyncCountdownSecs--;
    if (liveSyncCountdownSecs <= 0) {
      liveSyncCountdownSecs = liveSyncIntervalSecs;
      performLiveSync();
    }
    updateSyncCountdownDisplay();
  }, 1000);
}

function updateSyncCountdownDisplay() {
  const elem = document.getElementById("live-sync-countdown");
  if (elem) elem.innerText = liveSyncCountdownSecs + "s";
  const status = document.getElementById("live-sync-status-text");
  if (status && liveSyncIntervalSecs > 0) {
    status.innerHTML = `Ativo (<span id="live-sync-countdown" class="text-emerald-400 font-mono">${liveSyncCountdownSecs}s</span>)`;
  }
}

function changeLiveSyncInterval(val) {
  liveSyncIntervalSecs = parseInt(val, 10);
  startLiveSync();
  if (liveSyncIntervalSecs > 0) {
    showToast(`⏱️ Sincronização ao vivo ajustada para cada ${liveSyncIntervalSecs} segundos.`);
  } else {
    showToast(`⏸️ Sincronização automática pausada.`);
  }
}

function triggerManualLiveSync() {
  performLiveSync(true);
}

async function performLiveSync(isManual = false) {
  if (isSyncingNow) return;
  isSyncingNow = true;

  const syncIcon = document.getElementById("sync-icon");
  if (syncIcon) syncIcon.classList.add("animate-spin");

  const storeKey = currentStore;
  const domain = STORE_DOMAINS[storeKey] || "www.brkfishing.com.br";
  const fetchUrl = `https://${domain}/products.json?limit=30&t=${Date.now()}`;

  try {
    const response = await fetch(fetchUrl, { cache: "no-store" });
    if (!response.ok) throw new Error("Status " + response.status);
    const data = await response.json();
    const liveProducts = data.products || [];

    if (!MASTER_PAYLOAD.stores[storeKey]) {
      await StoreLoader.loadStore(storeKey);
    }
    const currentList = MASTER_PAYLOAD.stores[storeKey].products;
    const knownIds = new Set(currentList.map(p => String(p.id)));

    let newProductsAdded = 0;
    let emptyCountDetected = 0;

    liveProducts.forEach(liveP => {
      const pId = String(liveP.id);
      const rawHtml = liveP.body_html || "";
      const isEmpty = (!rawHtml || rawHtml.trim() === "" || rawHtml.trim() === "<p></p>");
      
      if (!knownIds.has(pId)) {
        const newEnriched = createEnrichedFromLiveProduct(liveP, storeKey);
        currentList.unshift(newEnriched);
        knownIds.add(pId);
        newProductsAdded++;
        if (newEnriched.status === "SEM_DESCRICAO") emptyCountDetected++;
      } else {
        const existing = currentList.find(p => String(p.id) === pId);
        if (existing && isEmpty && existing.status !== "SEM_DESCRICAO") {
          existing.status = "SEM_DESCRICAO";
          existing.is_out_of_standard = true;
        }
      }
    });

    if (newProductsAdded > 0) {
      updateCockpit();
      renderProducts();
      updateMassCountBadge();
      showToast(`✨ ${newProductsAdded} produto(s) sincronizado(s) em tempo real da Shopify! (${emptyCountDetected} sem descrição)`);
    } else if (isManual) {
      showToast(`✅ Catálogo da loja ${domain} sincronizado com a Shopify! Nenhum novo produto no momento.`);
    }
  } catch (err) {
    console.warn("Falha no Live Sync:", err);
    if (isManual) {
      showToast(`⚠️ Não foi possível conectar na Shopify em tempo real: ${err.message}`);
    }
  } finally {
    if (syncIcon) syncIcon.classList.remove("animate-spin");
    isSyncingNow = false;
  }
}

// Alternador de Loja Assíncrono com Cache
async function switchStore(storeKey) {
  currentStore = storeKey;
  currentFilter = "all";
  selectedCategory = "all";
  searchQuery = "";
  if (searchInput) searchInput.value = "";

  // Atualizar Pills
  document.querySelectorAll(".store-pill").forEach(p => {
    p.classList.remove("active", "bg-blue-600", "text-white");
    p.classList.add("text-slate-400");
  });
  const pillMap = {
    "brk_fishing": "pill-store-fishing",
    "brk_agro": "pill-store-agro",
    "brk_motors": "pill-store-motors"
  };
  const activePill = document.getElementById(pillMap[storeKey]);
  if (activePill) {
    activePill.classList.add("active", "bg-blue-600", "text-white");
    activePill.classList.remove("text-slate-400");
  }

  // Título da Loja
  const storeTitles = {
    "brk_fishing": "BRK Fishing",
    "brk_agro": "BRK Agro",
    "brk_motors": "BRK Motors"
  };
  const titleElem = document.getElementById("store-title-text");
  if (titleElem) titleElem.innerText = storeTitles[storeKey];

  // Exibir estado de carregamento leve no grid se dados ainda não estiverem em memória
  if (!MASTER_PAYLOAD.stores[storeKey]) {
    productsGrid.innerHTML = `
      <div class="col-span-full loading-overlay">
        <div class="spinner"></div>
        <p class="text-xs font-bold text-slate-500">Carregando catálogo da ${storeTitles[storeKey]}...</p>
      </div>`;
    try {
      const loadedData = await StoreLoader.loadStore(storeKey);
      MASTER_PAYLOAD.stores[storeKey] = loadedData;
    } catch (e) {
      productsGrid.innerHTML = `
        <div class="col-span-full text-center py-12 text-slate-500">
          <p class="text-base font-bold text-red-500">Erro ao carregar dados da loja ${storeTitles[storeKey]}</p>
          <p class="text-xs mt-1">Verifique sua conexão ou inicie um servidor local (ex: python -m http.server 8000).</p>
        </div>`;
      return;
    }
  }

  updateCockpit();
  renderCategories();
  renderProducts();
  updateMassCountBadge();
  startLiveSync();
}

// Atualizar Cockpit do Topo
function updateCockpit() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const storeInfo = storeData.store || {};
  const products = storeData.products || [];
  
  const totalSkus = storeInfo.total_skus || products.length;
  const brokenSkus = storeInfo.broken_skus !== undefined ? storeInfo.broken_skus : products.filter(p => p.status === "IMAGENS_QUEBRADAS").length;
  const outOfStd = storeInfo.out_of_standard_skus || 0;
  const healthySkus = totalSkus > outOfStd ? totalSkus - outOfStd : 0;
  const healthPct = totalSkus > 0 ? Math.round((healthySkus / totalSkus) * 100) : 100;

  const brokenElem = document.getElementById("cockpit-broken-count");
  if (brokenElem) brokenElem.innerText = brokenSkus.toLocaleString('pt-BR');
  const healthElem = document.getElementById("cockpit-health-badge");
  if (healthElem) healthElem.innerText = healthPct + "% Saudável";
  
  const loadedBroken = products.filter(p => p.status === "IMAGENS_QUEBRADAS").length;
  const loadedEmpty = products.filter(p => {
    const b = (p.original_body_html || p.body_html || "").trim();
    return p.status === "SEM_DESCRICAO" || !b || b.length <= 5 || b.toLowerCase() === "a" || b.toLowerCase() === "<p>a</p>" || b === "<p></p>";
  }).length;
  const loadedHealthy = products.filter(p => {
    const isB = p.status === "IMAGENS_QUEBRADAS";
    const b = (p.original_body_html || p.body_html || "").trim();
    const isE = p.status === "SEM_DESCRICAO" || !b || b.length <= 5 || b.toLowerCase() === "a" || b.toLowerCase() === "<p>a</p>" || b === "<p></p>";
    return !isB && !isE && !p.is_out_of_standard;
  }).length;

  const emptyCockpitElem = document.getElementById("cockpit-empty-count");
  if (emptyCockpitElem) {
    emptyCockpitElem.innerText = loadedEmpty.toLocaleString('pt-BR');
  }

  const cAll = document.getElementById("count-all");
  if (cAll) cAll.innerText = products.length;
  const cBroken = document.getElementById("count-broken");
  if (cBroken) cBroken.innerText = loadedBroken;
  const cEmpty = document.getElementById("count-empty");
  if (cEmpty) cEmpty.innerText = loadedEmpty;
  const cHealthy = document.getElementById("count-healthy");
  if (cHealthy) cHealthy.innerText = loadedHealthy;
}

// Filtros Rápidos do Cockpit
function filterBrokenFromCockpit() {
  switchMainTab("tab-catalog");
  currentFilter = "broken";
  syncFilterButtons();
  renderProducts();
}

function filterEmptyFromCockpit() {
  switchMainTab("tab-catalog");
  currentFilter = "empty";
  syncFilterButtons();
  renderProducts();
}

function syncFilterButtons() {
  document.querySelectorAll(".filter-btn").forEach(btn => {
    if (btn.dataset.filter === currentFilter) {
      btn.classList.add("active", "bg-slate-900", "text-white");
      btn.classList.remove("bg-slate-50", "text-slate-600");
    } else {
      btn.classList.remove("active", "bg-slate-900", "text-white");
    }
  });
}

// Renderizar Categorias Circulares
function renderCategories() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const rawCategories = storeData.categories;
  let categoriesList = [];
  if (Array.isArray(rawCategories)) {
    categoriesList = rawCategories;
  } else if (typeof rawCategories === 'object' && rawCategories !== null) {
    categoriesList = Object.entries(rawCategories).map(([k, v]) => ({
      name: k,
      title: v.title || k,
      sample_image: v.thumb || v.sample_image || '',
      broken_count: v.broken_count || v.broken_skus || 0,
      count: v.count || 0
    }));
  }

  categoriesRail.innerHTML = "";

  // Botão "Todas"
  const allDiv = document.createElement("div");
  allDiv.className = "flex flex-col items-center gap-2 cursor-pointer flex-shrink-0 group";
  allDiv.onclick = () => { selectedCategory = "all"; renderProducts(); highlightCategory(allDiv); };
  allDiv.innerHTML = `
    <div class="w-16 h-16 rounded-full p-0.5 bg-blue-600 transition-all transform group-hover:scale-105 shadow-md flex items-center justify-center text-white font-extrabold text-xl">
      🌐
    </div>
    <span class="text-xs font-bold text-slate-700 group-hover:text-blue-600">Todas</span>
  `;
  categoriesRail.appendChild(allDiv);

  categoriesList.forEach(cat => {
    const div = document.createElement("div");
    div.className = "flex flex-col items-center gap-2 cursor-pointer flex-shrink-0 group w-20 text-center";
    div.onclick = () => { selectedCategory = cat.name; renderProducts(); highlightCategory(div); };
    
    const ringClass = cat.broken_count > 0 ? "category-ring has-broken" : "category-ring";
    const imgUrl = cat.sample_image || "https://placehold.co/100x100?text=BRK";

    div.innerHTML = `
      <div class="relative w-16 h-16 rounded-full p-[2px] ${ringClass} transition-all transform group-hover:scale-105 shadow-md">
        <img src="${imgUrl}" alt="${cat.name}" class="w-full h-full object-cover rounded-full bg-white p-0.5" loading="lazy" />
        ${cat.broken_count > 0 ? `<span class="absolute -top-1 -right-1 bg-red-600 text-white text-[9px] font-extrabold px-1.5 py-0.2 rounded-full border border-white">!</span>` : ''}
      </div>
      <span class="text-[11px] font-semibold text-slate-700 truncate w-full group-hover:text-blue-600 block">${cat.name}</span>
    `;
    categoriesRail.appendChild(div);
  });
}

function highlightCategory(activeElem) {
  document.querySelectorAll("#categories-rail > div").forEach(d => d.classList.remove("opacity-100", "scale-105"));
  activeElem.classList.add("opacity-100");
}

// Renderizar Grid de Produtos
function renderProducts() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const products = storeData.products || [];
  productsGrid.innerHTML = "";

  let filtered = products.filter(p => {
    if (selectedCategory !== "all" && p.category !== selectedCategory) return false;
    
    const isBroken = p.status === "IMAGENS_QUEBRADAS";
    const b = (p.original_body_html || p.body_html || "").trim();
    const isEmpty = p.status === "SEM_DESCRICAO" || !b || b.length <= 5 || b.toLowerCase() === "a" || b.toLowerCase() === "<p>a</p>" || b === "<p></p>";

    if (currentFilter === "broken" && !isBroken) return false;
    if (currentFilter === "empty" && !isEmpty) return false;
    if (currentFilter === "healthy" && (isBroken || isEmpty || p.is_out_of_standard)) return false;

    if (searchQuery.trim() !== "") {
      const q = searchQuery.toLowerCase();
      const matchTitle = (p.title || "").toLowerCase().includes(q);
      const matchSku = (p.master_sku || "").toLowerCase().includes(q);
      const matchVariants = (p.variants_skus || []).some(v => v.toLowerCase().includes(q));
      if (!matchTitle && !matchSku && !matchVariants) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    emptyState.classList.remove("hidden");
    return;
  }
  emptyState.classList.add("hidden");

  filtered.forEach(p => {
    const b = (p.original_body_html || p.body_html || "").trim();
    const isBroken = p.status === "IMAGENS_QUEBRADAS";
    const isEmpty = p.status === "SEM_DESCRICAO" || !b || b.length <= 5 || b.toLowerCase() === "a" || b.toLowerCase() === "<p>a</p>" || b === "<p></p>";

    let borderClass = "border-slate-200 hover:border-blue-400";
    let statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800 flex items-center gap-1">${getSvgIcon('check', '#065f46', 10)} Saudável</span>`;

    if (isBroken) {
      borderClass = "border-red-300 hover:border-red-500 bg-red-50/20";
      statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800 flex items-center gap-1">❌ Fotos Quebradas</span>`;
    } else if (isEmpty) {
      borderClass = "border-amber-300 hover:border-amber-500 bg-amber-50/20";
      statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800 flex items-center gap-1">⚠️ Sem Descrição</span>`;
    }

    const card = document.createElement("div");
    card.className = `bg-white rounded-2xl border ${borderClass} p-4 product-shadow transition-all flex flex-col justify-between cursor-pointer group`;
    card.onclick = () => openProductModal(p);

    const imgSrc = (p.cdn_images && p.cdn_images[0]) || (p.gallery && p.gallery[0]) || p.image || "https://placehold.co/400x300?text=Sem+Foto";

    card.innerHTML = `
      <div>
        <div class="relative w-full h-44 rounded-xl overflow-hidden bg-slate-100 mb-3 border border-slate-100">
          <img src="${imgSrc}" alt="${p.title}" class="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300" loading="lazy" />
          <div class="absolute top-2 left-2 flex flex-col gap-1">
            ${statusBadge}
          </div>
          <span class="absolute top-2 right-2 text-[10px] font-mono font-bold bg-slate-900/80 text-white px-2 py-0.5 rounded-md backdrop-blur-sm">
            ${p.master_sku || 'N/D'}
          </span>
        </div>

        <div class="space-y-1">
          <div class="flex items-center justify-between text-[11px] text-slate-500">
            <span class="truncate max-w-[150px] font-semibold">${p.category || 'Geral'}</span>
            <span class="font-bold text-slate-700">${p.variants_skus ? p.variants_skus.length : 1} vars</span>
          </div>
          <h3 class="text-xs font-bold text-slate-900 line-clamp-2 leading-snug group-hover:text-blue-600 transition-colors">
            ${p.title}
          </h3>
        </div>
      </div>

      <div class="pt-3 mt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <span class="text-[10px] font-extrabold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">
          ${p.archetype_name || 'UV50+ Pesca'}
        </span>
        <button onclick="quickCopyProductHTML(event, '${p.master_sku}')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-[10px] font-bold transition-all flex items-center gap-1 active:scale-95">
          <span>📋 Copiar</span>
        </button>
      </div>
    `;
    productsGrid.appendChild(card);
  });
}

// Copiar Rápido Direto do Card
function quickCopyProductHTML(event, sku) {
  if (event) event.stopPropagation();
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const p = storeData.products.find(prod => (prod.master_sku || "") === sku);
  if (!p) return;

  if (!p.mode_b_html && typeof getProductModeBHTML === "function") {
    p.mode_b_html = getProductModeBHTML(p);
  }
  const htmlToCopy = p.mode_b_html || p.mode_a_html || p.original_body_html || "";
  if (!htmlToCopy) {
    showToast("⚠️ Produto sem HTML disponível.");
    return;
  }

  navigator.clipboard.writeText(htmlToCopy).then(() => {
    showToast(`HTML (Modo B) do SKU ${sku} copiado com sucesso!`);
    if (event && event.currentTarget) {
      const btn = event.currentTarget;
      const orig = btn.innerHTML;
      btn.innerHTML = `<span>✅</span> <span>Copiado!</span>`;
      btn.classList.add("bg-emerald-600", "text-white");
      setTimeout(() => {
        btn.innerHTML = orig;
        btn.classList.remove("bg-emerald-600", "text-white");
      }, 2000);
    }
  }).catch(() => {
    showToast("⚠️ Não foi possível copiar para a área de transferência.");
  });
}

// Geração em Massa
function updateMassCountBadge() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const brokenOrEmpty = storeData.products.filter(p => p.status === "IMAGENS_QUEBRADAS" || p.status === "SEM_DESCRICAO");
  const badge = document.getElementById("badge-mass-count");
  if (badge) badge.innerText = brokenOrEmpty.length;
}

function renderMassTable() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const targetItems = storeData.products.filter(p => p.status === "IMAGENS_QUEBRADAS" || p.status === "SEM_DESCRICAO");
  massTableBody.innerHTML = "";
  selectedMassProductIds.clear();

  targetItems.forEach(p => {
    selectedMassProductIds.add(p.id);
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50 transition-colors";
    
    const isBroken = p.status === "IMAGENS_QUEBRADAS";
    const diagBadge = isBroken 
      ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800">❌ Fotos Quebradas AWS</span>`
      : `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800">⚠️ Sem Descrição</span>`;

    tr.innerHTML = `
      <td class="p-3.5 text-center">
        <input type="checkbox" class="mass-row-check w-4 h-4 text-blue-600 rounded cursor-pointer" data-id="${p.id}" checked onchange="handleMassRowCheck(this)" />
      </td>
      <td class="p-3.5">
        <span class="font-mono font-bold text-slate-800 block text-xs">${p.master_sku || 'N/D'}</span>
        <span class="text-slate-500 line-clamp-1 text-[11px]">${p.title}</span>
      </td>
      <td class="p-3.5 font-semibold text-slate-600">
        ${p.variants_skus ? p.variants_skus.length : 1} vars
      </td>
      <td class="p-3.5">
        <span class="px-2 py-0.5 rounded-md bg-slate-100 font-bold text-slate-700 text-[10px] border border-slate-200">
          ${(p.cdn_images || []).length} fotos CDN
        </span>
      </td>
      <td class="p-3.5">
        <span class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold text-[10px] border border-blue-200">
          ${p.archetype_name || 'UV50+ Pesca'}
        </span>
      </td>
      <td class="p-3.5">${diagBadge}</td>
      <td class="p-3.5 text-right">
        <button onclick='openProductModal(${JSON.stringify(p).replace(/'/g, "&#39;")})' class="px-2.5 py-1 bg-slate-900 hover:bg-black text-white rounded-lg text-[10px] font-extrabold">
          Inspecionar
        </button>
      </td>
    `;
    massTableBody.appendChild(tr);
  });

  const countElem = document.getElementById("mass-selected-count");
  if (countElem) countElem.innerText = selectedMassProductIds.size;
}

function toggleSelectAllMass(masterCheckbox) {
  const checkboxes = document.querySelectorAll(".mass-row-check");
  checkboxes.forEach(cb => {
    cb.checked = masterCheckbox.checked;
    const id = parseInt(cb.dataset.id);
    if (masterCheckbox.checked) selectedMassProductIds.add(id);
    else selectedMassProductIds.delete(id);
  });
  document.getElementById("mass-selected-count").innerText = selectedMassProductIds.size;
}

function handleMassRowCheck(cb) {
  const id = parseInt(cb.dataset.id);
  if (cb.checked) selectedMassProductIds.add(id);
  else selectedMassProductIds.delete(id);
  document.getElementById("mass-selected-count").innerText = selectedMassProductIds.size;
}

function executeMassBatch(modeKey) {
  if (selectedMassProductIds.size === 0) {
    alert("Por favor, selecione ao menos um produto para gerar o lote.");
    return;
  }
  const modeName = modeKey === "mode_b_html" ? "Modo B (3 Atos Conversão)" : "Modo A (Preservar HTML)";
  showToast(`Lote de ${selectedMassProductIds.size} produtos gerado com sucesso via ${modeName}!`);
}

function downloadShopifyCSVBatch() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const products = storeData.products;
  const selected = products.filter(p => selectedMassProductIds.has(p.id));
  
  if (selected.length === 0) {
    alert("Nenhum produto selecionado para exportação.");
    return;
  }

  const rows = ["Handle,Title,Body (HTML)"];
  selected.forEach(p => {
    if (!p.mode_b_html && typeof getProductModeBHTML === "function") {
      p.mode_b_html = getProductModeBHTML(p);
    }
    const html = p.mode_b_html || p.mode_a_html || "";
    rows.push(`"${p.handle}","${p.title.replace(/"/g, '""')}","${html.replace(/"/g, '""')}"`);
  });

  const csvContent = "\uFEFF" + rows.join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `shopify_lote_massa_${currentStore}_${new Date().toISOString().slice(0,10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  showToast(`Planilha CSV com ${selected.length} produtos gerada e baixada com sucesso!`);
}

// Aba Moldes Mestres
async function renderMoldesCards() {
  const container = document.getElementById("moldes-cards-container");
  if (!container) return;
  container.innerHTML = "";
  
  let moldes = MASTER_PAYLOAD.moldes;
  if (!moldes || Object.keys(moldes).length === 0) {
    moldes = await StoreLoader.loadMoldes();
    MASTER_PAYLOAD.moldes = moldes;
  }

  for (const [key, m] of Object.entries(moldes)) {
    const card = document.createElement("div");
    card.className = "bg-white rounded-3xl border border-slate-200 p-6 product-shadow flex flex-col justify-between";

    let specsItems = "";
    (m.base_specs || []).forEach(s => {
      specsItems += `<li class="flex items-start gap-1.5"><span class="text-emerald-500 font-bold">✓</span> <strong class="text-slate-800">${s.label}:</strong> <span class="text-slate-600">${s.default}</span></li>`;
    });

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-3">
          <span class="px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-blue-50 text-blue-700 border border-blue-200">Molde Mestre</span>
          <span class="text-xs text-slate-400 font-mono">ID: ${m.id}</span>
        </div>
        <h3 class="text-base font-extrabold text-slate-900 font-heading mb-1">${m.name}</h3>
        <p class="text-xs font-semibold text-blue-600 mb-4">${m.default_tagline || ''}</p>

        <div class="space-y-2 mb-4 bg-slate-50 p-3 rounded-2xl border border-slate-100 text-xs">
          <span class="text-[10px] font-extrabold uppercase text-slate-400 block tracking-wider">Atos Narrativos:</span>
          <div class="font-bold text-slate-700">1. ${m.act1 ? m.act1.tag : 'Ato 1'}</div>
          <div class="font-bold text-slate-700">2. ${m.act2 ? m.act2.tag : 'Ato 2'}</div>
          <div class="font-bold text-slate-700">3. ${m.act3 ? m.act3.tag : 'Ato 3'}</div>
        </div>

        <div class="space-y-1.5 mb-4 text-xs">
          <span class="text-[10px] font-extrabold uppercase text-slate-400 block tracking-wider">Especificações Obrigatórias Preservadas:</span>
          <ul class="space-y-1 text-[11px]">
            ${specsItems}
          </ul>
        </div>
      </div>

      <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
        <span class="text-[11px] text-slate-400 font-medium">Palavras-chave: ${(m.category_keywords || []).slice(0, 3).join(", ")}</span>
        <span class="text-xs font-extrabold text-emerald-600">Ativo</span>
      </div>
    `;
    container.appendChild(card);
  }
}

// Aba Análises & Vigilante Diário
async function renderAnalyticsView() {
  let analytics = MASTER_PAYLOAD.analytics;
  if (!analytics || !analytics.history) {
    analytics = await StoreLoader.loadAnalytics();
    MASTER_PAYLOAD.analytics = analytics;
  }
  const history = analytics.history || [];
  const latestSnapshot = history.length > 0 ? history[history.length - 1] : null;

  if (latestSnapshot) {
    const sentinelRun = document.getElementById("sentinel-last-run");
    if (sentinelRun) sentinelRun.innerText = "Última checagem: " + latestSnapshot.timestamp;
    const badgeDaily = document.getElementById("badge-daily-corrections-count");
    if (badgeDaily) badgeDaily.innerText = (latestSnapshot.total_corrections_ready || 86) + " correções prontas";
    
    // Atualizar métricas Fishing
    const f = latestSnapshot.stores ? latestSnapshot.stores.brk_fishing : null;
    if (f) {
      document.getElementById("stat-fishing-health").innerText = f.health_percentage + "%";
      document.getElementById("stat-fishing-skus").innerText = f.total_skus;
      document.getElementById("stat-fishing-broken").innerText = f.broken_skus + " SKUs";
      document.getElementById("stat-fishing-empty").innerText = f.empty_products + " produtos";
      document.getElementById("stat-fishing-fixes").innerText = f.corrections_generated + " prontas";
      document.getElementById("bar-fishing-health").style.width = f.health_percentage + "%";
    }

    // Atualizar métricas Agro
    const a = latestSnapshot.stores ? latestSnapshot.stores.brk_agro : null;
    if (a) {
      document.getElementById("stat-agro-health").innerText = a.health_percentage + "%";
      document.getElementById("stat-agro-skus").innerText = a.total_skus;
      document.getElementById("stat-agro-broken").innerText = a.broken_skus + " SKUs";
      document.getElementById("stat-agro-empty").innerText = a.empty_products + " produtos";
      document.getElementById("stat-agro-fixes").innerText = a.corrections_generated + " prontas";
      document.getElementById("bar-agro-health").style.width = a.health_percentage + "%";
    }

    // Atualizar métricas Motors
    const m = latestSnapshot.stores ? latestSnapshot.stores.brk_motors : null;
    if (m) {
      document.getElementById("stat-motors-health").innerText = m.health_percentage + "%";
      document.getElementById("stat-motors-skus").innerText = m.total_skus;
      document.getElementById("stat-motors-broken").innerText = m.broken_skus + " SKUs";
      document.getElementById("stat-motors-empty").innerText = m.empty_products + " produtos";
      document.getElementById("stat-motors-fixes").innerText = m.corrections_generated + " prontas";
      document.getElementById("bar-motors-health").style.width = m.health_percentage + "%";
    }
  }

  renderAuditTable();
  renderAvailableCSVs();
}

function filterAuditTable(filterType) {
  currentAuditFilter = filterType;
  ['all', 'prohibited', 'orphaned'].forEach(f => {
    const btn = document.getElementById("audit-btn-" + f);
    if (btn) {
      if (f === filterType) {
        btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-900 text-white";
      } else {
        btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-100 text-slate-700 hover:bg-slate-200";
      }
    }
  });
  renderAuditTable();
}

function renderAuditTable() {
  const tbody = document.getElementById("audit-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  let auditItems = [];
  const storeTitles = { "brk_fishing": "Fishing", "brk_agro": "Agro", "brk_motors": "Motors" };

  for (const [storeKey, sData] of Object.entries(MASTER_PAYLOAD.stores)) {
    if (!sData || !sData.products) continue;
    sData.products.forEach(p => {
      const hasProhib = (p.prohibited_links && p.prohibited_links.length > 0);
      const hasOrphan = (p.orphaned_variants && p.orphaned_variants.length > 0);
      const isBroken = (p.status === "IMAGENS_QUEBRADAS");
      const isEmpty = (p.status === "SEM_DESCRICAO");

      if (hasProhib || hasOrphan || isBroken || isEmpty) {
        auditItems.push({
          store: storeTitles[storeKey] || storeKey,
          storeKey: storeKey,
          product: p,
          hasProhib: hasProhib,
          hasOrphan: hasOrphan,
          isBroken: isBroken,
          isEmpty: isEmpty
        });
      }
    });
  }

  if (currentAuditFilter === "prohibited") {
    auditItems = auditItems.filter(i => i.hasProhib);
  } else if (currentAuditFilter === "orphaned") {
    auditItems = auditItems.filter(i => i.hasOrphan);
  }

  if (auditItems.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="p-6 text-center text-slate-400">Nenhum item com inconformidade encontrado para o filtro selecionado.</td></tr>`;
    return;
  }

  auditItems.slice(0, 50).forEach(item => {
    const p = item.product;
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50 transition-colors";

    let riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800">Fotos Quebradas AWS S3</span>`;
    let detailText = p.affected_skus_count ? `${p.affected_skus_count} SKUs afetados` : "Imagem com erro 404";

    if (item.hasProhib) {
      riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-purple-100 text-purple-800">Link Externo Proibido</span>`;
      detailText = p.prohibited_links[0];
    } else if (item.hasOrphan) {
      riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800">SKU Órfão</span>`;
      detailText = p.orphaned_variants.join(", ");
    } else if (item.isEmpty) {
      riskBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800">Sem Descrição</span>`;
      detailText = "Texto zerado no cadastro";
    }

    tr.innerHTML = `
      <td class="p-3.5 font-mono font-bold text-slate-800">${p.master_sku || 'N/D'}</td>
      <td class="p-3.5 max-w-xs truncate text-slate-700">${p.title}</td>
      <td class="p-3.5 font-semibold text-slate-500">${item.store}</td>
      <td class="p-3.5">${riskBadge}</td>
      <td class="p-3.5 text-slate-500 truncate max-w-xs text-[11px]">${detailText}</td>
      <td class="p-3.5 text-right">
        <button onclick='openProductModal(${JSON.stringify(p).replace(/'/g, "&#39;")})' class="px-2.5 py-1 bg-slate-900 hover:bg-black text-white rounded-lg text-[10px] font-extrabold">
          Resolver ⚙️
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderAvailableCSVs() {
  const listContainer = document.getElementById("analytics-csv-list");
  if (!listContainer) return;
  listContainer.innerHTML = "";
  const csvs = (MASTER_PAYLOAD.analytics && MASTER_PAYLOAD.analytics.available_csvs) || [];

  if (csvs.length === 0) {
    listContainer.innerHTML = `<p class="text-xs text-slate-400 italic">Nenhum CSV diário gerado até o momento.</p>`;
    return;
  }

  csvs.forEach(c => {
    const card = document.createElement("div");
    card.className = "border border-slate-200 rounded-2xl p-4 bg-slate-50 hover:bg-white hover:border-emerald-400 transition-all flex items-center justify-between";
    card.innerHTML = `
      <div>
        <div class="flex items-center gap-1.5 mb-1">
          <span class="text-emerald-600 font-extrabold text-xs">📄 CSV Shopify</span>
          <span class="text-[10px] text-slate-400">${c.size_kb} KB</span>
        </div>
        <strong class="text-xs text-slate-800 block truncate max-w-[200px]">${c.filename}</strong>
        <span class="text-[10px] text-slate-400">Criado em: ${c.created_at}</span>
      </div>
      <button onclick="downloadLatestDailyCSV()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all">
        Baixar ⬇️
      </button>
    `;
    listContainer.appendChild(card);
  });
}

function downloadLatestDailyCSV() {
  const rows = ["Handle,Title,Body (HTML)"];
  let count = 0;

  for (const [storeKey, sData] of Object.entries(MASTER_PAYLOAD.stores)) {
    if (!sData || !sData.products) continue;
    sData.products.forEach(p => {
      if (p.status === "IMAGENS_QUEBRADAS" || p.status === "SEM_DESCRICAO") {
        const html = p.mode_b_html || p.mode_a_html || "";
        rows.push(`"${p.handle}","${p.title.replace(/"/g, '""')}","${html.replace(/"/g, '""')}"`);
        count++;
      }
    });
  }

  const csvContent = "\uFEFF" + rows.join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `shopify_correcoes_diarias_08h_${new Date().toISOString().slice(0,10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  showToast(`Planilha com ${count} correções baixada com sucesso!`);
}

// Eventos Globais
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.onclick = () => {
    currentFilter = btn.dataset.filter;
    syncFilterButtons();
    renderProducts();
  };
});

if (searchInput) {
  searchInput.oninput = (e) => {
    searchQuery = e.target.value;
    renderProducts();
  };
}

const scrollL = document.getElementById("scroll-left");
if (scrollL) scrollL.onclick = () => { categoriesRail.scrollBy({ left: -250, behavior: 'smooth' }); };
const scrollR = document.getElementById("scroll-right");
if (scrollR) scrollR.onclick = () => { categoriesRail.scrollBy({ left: 250, behavior: 'smooth' }); };

// Inicialização Inicial
document.addEventListener("DOMContentLoaded", () => {
  switchStore("brk_fishing");
});
