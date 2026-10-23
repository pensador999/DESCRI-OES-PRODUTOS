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
let currentActiveTab = "tab-catalog";

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
  currentActiveTab = tabId;
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

function detectClientArchetype(title, category, tags, sku = "") {
  const t = (title || "").toLowerCase();
  const cat = (category || "").toLowerCase();
  const text = `${t} ${cat} ${Array.isArray(tags) ? tags.join(" ") : tags || ""}`.toLowerCase();

  // 1. Aromatizantes & Perfumaria Automotiva (Prioridade Máxima)
  if (/\b(aromatizante|cheirinho|difusor|aromatizador|odorizador|little trees|odor)\b/i.test(t)) {
    return { id: "accessories_car_care", name: "Aromatizantes Automotivos & Cuidados" };
  }

  // 2. Óculos de Sol & Polarizados UV400 (se não for camisa, lenço, adesivo ou chaveiro)
  if ((/\b(oculos|óculos|sunglasses)\b/i.test(t) || /\b(polarizado|polarizada|aviador|uv400|lente polarizada)\b/i.test(t)) && !/\b(camisa|camiseta|adesivo|chaveiro|lenço|lenco|bandana)\b/i.test(t)) {
    return { id: "eyewear_sunglasses", name: "Óculos de Sol & Polarizados UV400" };
  }

  // 3. Luvas de Pesca, Táticas & Esportivas (se não for camisa)
  if (/\b(luva|luvas)\b/i.test(t) && !/\b(camisa|camiseta)\b/i.test(t)) {
    return { id: "gloves_tactical_fishing", name: "Luvas de Pesca, Táticas & Esportivas" };
  }

  // 4. Bandanas, Tubenecks, Lenços & Balaclavas (se não for camisa)
  if (/\b(bandana|balaclava|tubeneck|buff|mascara facial|máscara facial|protetor de pescoço|lenço|lenco|lenços|lencos)\b/i.test(t) && !/\b(camisa|camiseta)\b/i.test(t)) {
    return { id: "neck_gaiters_balaclavas", name: "Bandanas, Tubenecks & Balaclavas" };
  }

  // 5. Chaveiros, Adesivos, Camping & Acessórios Gerais
  if (/\b(chaveiro|adesivo|adesivos|sticker|stickers|patch|emblema|capa de caiaque|caiaque|barraca|fogareiro|mesa dobrável|mesa dobravel|coleira|suporte magnético|suporte magnetico)\b/i.test(t) && !/\b(camisa|camiseta)\b/i.test(t)) {
    return { id: "accessories_general", name: "Acessórios, Chaveiros & Adesivos" };
  }

  // 6. Calças & Bermudas (Evita cair em camisa)
  if (/\b(calca|calça|calcas|calças|bermuda|bermudas|shorts|short|calcao|calção)\b/i.test(t) && !/\b(camisa|camiseta)\b/i.test(t)) {
    return { id: "pants_cargo_tactical", name: "Calças & Bermudas Táticas / Cargo / Pesca" };
  }

  // 7. Chapéus: Country/Feltro/Pralana vs Safári/Outdoor/Pescador
  if (/\b(chapeu|chapéu|chapeus|chapéus)\b/i.test(t)) {
    if (/\b(feltro|pralana|american hat|karanda|karandá|country|cowboy|pantaneiro|lã|veludo|liso|marcatto|eldorado|cury)\b/i.test(t)) {
      return { id: "hats_country_cowboy", name: "Chapéus Country, Feltro, Pralana & Cowboy" };
    }
    return { id: "hats_safari_outdoor", name: "Chapéus de Pesca, Safári & Outdoor" };
  }
  if (/\b(pralana|american hat|karanda|karandá|feltro country)\b/i.test(t)) {
    return { id: "hats_country_cowboy", name: "Chapéus Country, Feltro, Pralana & Cowboy" };
  }

  // 8. Camisas: Work/Botão vs Agro vs Motors vs UV50+
  if (/\b(camisa|camiseta|baby look|regata|t-shirt|polo)\b/i.test(t)) {
    const hasUvOrVest = /\b(uv|uv50|fpu|fps|xtech|solar|colete|sublimad|segunda pele|termica|térmica)\b/i.test(t) || /^(c0|ci|cadv|adv|hyb|raglan)/i.test(sku || "");
    if (
      (
        /\b(work|safari sarja|manga longa sarja|manga curta sarja|sarja|militar|operacional|botao|botão|de botao|de botão)\b/i.test(t) ||
        (/\bxadrez\b/i.test(t) && !hasUvOrVest) ||
        (/\b(lisa|sem estampa)\b/i.test(t) && !hasUvOrVest)
      ) && !/\b(ziper|zíper)\b/i.test(t)
    ) {
      return { id: "shirts_button_work", name: "Camisas Work, Botão & Sarja Utilitária" };
    }
    if ((/\b(algodao|algodão|cotton)\b/i.test(t) && !/algod[aã]o sombreado/i.test(t) && !hasUvOrVest) || (/\bcamiseta\b/i.test(t) && /\b(agro|campo|fazenda|trator)\b/i.test(t) && !hasUvOrVest)) {
      return { id: "agro_field", name: "Força, Campo & Tradição" };
    }
    if (/\b(jersey|moto|cross|off-road|trilha|speed|motors)\b/i.test(t) && !/\b(uv|uv50|fpu|xtech|segunda pele|termica|térmica)\b/i.test(t)) {
      return { id: "motors_speed", name: "Trilha, Velocidade & Off-Road" };
    }
    return { id: "uv_performance", name: "Camisas UV50+ Performance & Pesca" };
  }

  if (/\bjersey\b/i.test(t)) return { id: "motors_speed", name: "Trilha, Velocidade & Off-Road" };
  if (/\b(faca|facas|cutelo|cutelaria|canivete|chaira|afiador)\b/i.test(t)) return { id: "cutlery_unique", name: "Cutelaria & Peças Artesanais" };
  if (/\b(tenis|tênis|botina|bota|sneaker|sapato)\b/i.test(t)) return { id: "closed_footwear_sneakers", name: "Tênis & Calçados Fechados" };
  if (/\b(sandalia|sandália|chinelo|boaonda|babuche|clog|slide|pantufa)\b/i.test(t)) return { id: "footwear_sandals_boaonda", name: "Sandálias, Chinelos & Babuches Boaonda" };
  if (/\b(safari|safári|australiano|palha|pescador)\b/i.test(t)) return { id: "hats_safari_outdoor", name: "Chapéus de Pesca, Safári & Outdoor" };
  if (/\b(bone|boné|trucker|snapback|viseira)\b/i.test(t)) return { id: "caps_trucker_snapback", name: "Bonés Trucker & Snapback" };
  if (/\b(manguito|manguitos)\b/i.test(t)) return { id: "sun_sleeves_manguitos", name: "Manguitos de Proteção Solar UV50+" };
  if (/\b(bandana|balaclava|tubeneck|buff)\b/i.test(t)) return { id: "neck_gaiters_balaclavas", name: "Bandanas, Tubenecks & Balaclavas" };
  if (/\b(macacao|macacão|jardineira|jardineiras|salopete)\b/i.test(t)) return { id: "overalls_workwear", name: "Macacões, Jardineiras & Operacional" };
  if (/\b(isca|iscas|plug|jig|frog|soft|popper|stick|crankbait|minnow)\b/i.test(t)) return { id: "fishing_lures", name: "Iscas Artificiais & Alta Atratividade" };
  if (/\b(vara|carretilha|molinete|linha|anzol|alicate|passagua|passaguá|girador|giradores|snap|snaps|empate|chumbada|chumbo)\b/i.test(t)) return { id: "fishing_tackle_gear", name: "Equipamentos de Pesca & Revenda" };
  if (/\b(caixa de pesca|caixa pesca|estojo|maleta|bolsa de pesca|organizador|multicase|zmc)\b/i.test(t)) return { id: "tackle_boxes_storage", name: "Caixas, Estojos & Organização" };
  if (/\b(copo|garrafa|caneca|cantil|cooler|termico|térmico|elber)\b/i.test(t)) return { id: "drinkware_thermo", name: "Copos, Garrafas & Térmicos" };
  if (/\b(livro|livros|cartilha|guia)\b/i.test(t)) return { id: "books_publications", name: "Livros, Guias & Publicações" };

  // Fallback Secundário via texto completo
  if (/\b(aromatizante|cheirinho|difusor)\b/i.test(text)) return { id: "accessories_car_care", name: "Aromatizantes Automotivos & Cuidados" };
  if (/\b(oculos|óculos|polarizado|uv400)\b/i.test(text)) return { id: "eyewear_sunglasses", name: "Óculos de Sol & Polarizados UV400" };
  if (/\b(luva|luvas)\b/i.test(text) && !/\b(camisa|camiseta)\b/i.test(text)) return { id: "gloves_tactical_fishing", name: "Luvas de Pesca, Táticas & Esportivas" };
  if (/\b(lenço|lenco|bandana|balaclava)\b/i.test(text)) return { id: "neck_gaiters_balaclavas", name: "Bandanas, Tubenecks & Balaclavas" };
  if (/\b(chaveiro|adesivo)\b/i.test(text)) return { id: "accessories_general", name: "Acessórios, Chaveiros & Adesivos" };
  if (/\b(calca|calça|bermuda|shorts)\b/i.test(text)) return { id: "pants_cargo_tactical", name: "Calças & Bermudas Táticas / Cargo / Pesca" };
  if (/\b(pralana|american hat|karanda|karandá|feltro|country)\b/i.test(text)) return { id: "hats_country_cowboy", name: "Chapéus Country, Feltro, Pralana & Cowboy" };
  if (/\b(jersey|moto|cross|off-road|trilha|speed)\b/i.test(text)) return { id: "motors_speed", name: "Trilha, Velocidade & Off-Road" };
  if (/\b(agro|campo|fazenda|trator)\b/i.test(text)) return { id: "agro_field", name: "Força, Campo & Tradição" };

  return { id: "uv_performance", name: "Camisas UV50+ Performance & Pesca" };
}

function classifyClientStoreCategory(title, archId, storeKey) {
  const t = (title || "").toLowerCase();
  const s = (storeKey || "brk_fishing").toLowerCase();

  if (s === "brk_agro") {
    if (["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archId)) return "Camisas Agro & Campo";
    if (["caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"].includes(archId)) return "Bonés & Chapéus Agro";
    if (["closed_footwear_sneakers", "footwear_sandals_boaonda"].includes(archId)) return "Botinas & Calçados";
    if (archId === "cutlery_unique") return "Cutelaria & Facas Campo";
    if (archId === "drinkware_thermo") return "Térmicos & Tereré";
    if (archId === "eyewear_sunglasses") return "Óculos Polarizados Agro";
    if (["neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"].includes(archId)) return "Bandanas, Luvas & Manguitos";
    if (["pants_cargo_tactical", "overalls_workwear"].includes(archId)) return "Calças & Vestuário Campo";
    return "Acessórios Agro & Fazenda";
  }

  if (s === "brk_motors") {
    if (["uv_performance", "motors_speed", "agro_field", "shirts_button_work"].includes(archId)) {
      if (/\b(jaqueta|corta vento|moletom|segunda pele)\b/i.test(t)) return "Jaquetas & Corta Vento";
      return "Jerseys & Camisas Motors";
    }
    if (["neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"].includes(archId)) return "Proteção & Luvas Motors";
    if (["caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"].includes(archId)) return "Bonés & Street Motors";
    if (archId === "eyewear_sunglasses") return "Óculos & Goggles";
    return "Acessórios & Equipamentos";
  }

  if (["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archId)) {
    if (t.includes("armorx") || t.includes("armor")) return "Camisas ArmorX";
    return "Camisas de Pesca UV";
  }
  if (["caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"].includes(archId)) return "Bonés & Chapéus";
  if (["neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"].includes(archId)) return "Bandanas, Luvas & Manguitos";
  if (archId === "eyewear_sunglasses") return "Óculos Polarizados";
  if (["fishing_lures", "fishing_tackle_gear"].includes(archId)) return "Equipamentos & Iscas";
  if (archId === "tackle_boxes_storage") return "Caixas & Organização";
  if (["footwear_sandals_boaonda", "closed_footwear_sneakers", "overalls_workwear", "pants_cargo_tactical"].includes(archId)) return "Calçados & Sandálias";
  if (archId === "cutlery_unique") return "Cutelaria & Facas";
  if (archId === "drinkware_thermo") return "Térmicos & Camping";
  return "Acessórios Diversos";
}

function createEnrichedFromLiveProduct(liveP, storeKey) {
  const rawImgs = liveP.images || [];
  const rawSources = [];
  if (Array.isArray(rawImgs)) {
    rawImgs.forEach(img => {
      const src = typeof img === "string" ? img : (img && img.src);
      if (src) rawSources.push(src);
    });
  }
  if (rawSources.length === 0 && liveP.image) {
    const s = typeof liveP.image === "string" ? liveP.image : liveP.image.src;
    if (s) rawSources.push(s);
  }

  // Deduplicar URLs estritamente pela raiz
  const seenRoots = new Set();
  const dedupImages = [];
  rawSources.forEach(u => {
    if (!u || typeof u !== "string") return;
    const clean = u.trim();
    if (!clean) return;
    const root = clean.split("?")[0].toLowerCase();
    if (!seenRoots.has(root)) {
      seenRoots.add(root);
      dedupImages.push(clean);
    }
  });

  const rawHtml = liveP.body_html || "";
  const isEmpty = (!rawHtml || rawHtml.trim() === "" || rawHtml.trim() === "<p></p>");
  const tags = Array.isArray(liveP.tags) ? liveP.tags : (liveP.tags ? liveP.tags.split(",").map(t => t.trim()) : []);
  const title = liveP.title || "";
  const isC0 = title.toUpperCase().includes("C0") || (liveP.handle || "").toUpperCase().includes("C0");
  const arch = detectClientArchetype(title, liveP.product_type || "", tags);
  const category = classifyClientStoreCategory(title, arch.id, storeKey);

  return {
    id: liveP.id,
    title: title,
    handle: liveP.handle || "",
    store_key: storeKey || "brk_fishing",
    vendor: liveP.vendor || (storeKey === "brk_agro" ? "BRK Agro" : storeKey === "brk_motors" ? "BRK Motors" : "BRK Fishing"),
    category: category,
    tags: tags,
    images: dedupImages,
    gallery: dedupImages,
    cdn_images: dedupImages,
    image: dedupImages[0] || "",
    original_body_html: rawHtml,
    body_html: rawHtml,
    status: isEmpty ? "SEM_DESCRICAO" : "SAUDAVEL",
    is_out_of_standard: isEmpty,
    is_c0: isC0,
    archetype_id: arch.id,
    archetype_name: arch.name,
    mode_a_html: rawHtml,
    mode_b_html: "",
    mode_b_markdown: ""
  };
}

// Alternador de Loja Assíncrono com Cache Universal e Reatividade Multi-Abas
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

  // Exibir feedback de carregamento no container da aba ATUALMENTE VISÍVEL
  if (!MASTER_PAYLOAD.stores[storeKey]) {
    if (currentActiveTab === "tab-mass" && massTableBody) {
      massTableBody.innerHTML = `
        <tr>
          <td colspan="7" class="py-12 text-center text-slate-500">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent mb-3"></div>
            <p class="text-sm font-bold text-slate-700">Carregando fila de produtos da ${storeTitles[storeKey]}...</p>
          </td>
        </tr>`;
    } else if (currentActiveTab === "tab-moldes") {
      const moldesContainer = document.getElementById("moldes-cards-container");
      if (moldesContainer) {
        moldesContainer.innerHTML = `
          <div class="col-span-full py-12 text-center text-slate-500">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent mb-3"></div>
            <p class="text-sm font-bold text-slate-700">Carregando moldes da ${storeTitles[storeKey]}...</p>
          </div>`;
      }
    } else if (currentActiveTab === "tab-analytics") {
      const auditTbody = document.getElementById("audit-table-body");
      if (auditTbody) {
        auditTbody.innerHTML = `
          <tr>
            <td colspan="6" class="py-12 text-center text-slate-500">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent mb-3"></div>
              <p class="text-sm font-bold text-slate-700">Carregando análises da ${storeTitles[storeKey]}...</p>
            </td>
          </tr>`;
      }
    } else {
      if (productsGrid) {
        productsGrid.innerHTML = `
          <div class="col-span-full loading-overlay">
            <div class="spinner"></div>
            <p class="text-xs font-bold text-slate-500">Carregando catálogo da ${storeTitles[storeKey]}...</p>
          </div>`;
      }
    }

    try {
      const loadedData = await StoreLoader.loadStore(storeKey);
      MASTER_PAYLOAD.stores[storeKey] = loadedData;
    } catch (e) {
      const errMsg = `
        <div class="col-span-full text-center py-12 text-slate-500">
          <p class="text-base font-bold text-red-500">Erro ao carregar dados da loja ${storeTitles[storeKey]}</p>
          <p class="text-xs mt-1">Verifique os arquivos da loja em data/stores/.</p>
        </div>`;
      if (productsGrid) productsGrid.innerHTML = errMsg;
      showToast(`❌ Falha ao carregar dados da loja ${storeTitles[storeKey]}`);
      return;
    }
  }

  // 1. Atualizar métricas globais do Cockpit e Badges
  updateCockpit();
  updateMassCountBadge();

  // 2. Sempre atualizar o catálogo em background
  renderCategories();
  renderProducts();

  // 3. ATUALIZAR REATIVAMENTE A ABA QUE ESTIVER VISÍVEL NO MOMENTO
  if (currentActiveTab === "tab-mass") {
    renderMassTable();
  } else if (currentActiveTab === "tab-moldes") {
    renderMoldesCards();
  } else if (currentActiveTab === "tab-analytics") {
    renderAnalyticsView();
  }

  startLiveSync();

  // Agente ao vivo: confere na vitrine publica o estado real das descricoes desta loja
  if (typeof LiveAgent !== "undefined") LiveAgent.onStoreReady(storeKey);
}

// Atualizar Cockpit do Topo e Contadores dos Filtros (Escopados pela Categoria Selecionada)
function updateCockpit() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const products = storeData.products || [];

  const loadedBroken = products.filter(p => p.status === "IMAGENS_QUEBRADAS").length;
  const loadedEmpty = products.filter(p => p.status === "SEM_DESCRICAO").length;
  const loadedHealthy = products.filter(p => p.status === "SAUDAVEL" || (!p.is_out_of_standard && p.status !== "IMAGENS_QUEBRADAS" && p.status !== "SEM_DESCRICAO")).length;
  const totalProds = products.length;
  const healthPct = totalProds > 0 ? Math.round((loadedHealthy / totalProds) * 100) : 100;

  const brokenElem = document.getElementById("cockpit-broken-count");
  if (brokenElem) brokenElem.innerText = loadedBroken.toLocaleString('pt-BR');
  const healthElem = document.getElementById("cockpit-health-badge");
  if (healthElem) healthElem.innerText = healthPct + "% Saudável";

  const emptyCockpitElem = document.getElementById("cockpit-empty-count");
  if (emptyCockpitElem) {
    emptyCockpitElem.innerText = loadedEmpty.toLocaleString('pt-BR');
  }

  // Escopar contadores das pílulas de filtro pela categoria selecionada (ou loja inteira se "all")
  const scopedProducts = selectedCategory === "all"
    ? products
    : products.filter(p => p.category === selectedCategory);

  const scopedBroken = scopedProducts.filter(p => p.status === "IMAGENS_QUEBRADAS").length;
  const scopedEmpty = scopedProducts.filter(p => p.status === "SEM_DESCRICAO").length;
  const scopedHealthy = scopedProducts.filter(p => p.status === "SAUDAVEL" || (!p.is_out_of_standard && p.status !== "IMAGENS_QUEBRADAS" && p.status !== "SEM_DESCRICAO")).length;

  const cAll = document.getElementById("count-all");
  if (cAll) cAll.innerText = scopedProducts.length;
  const cBroken = document.getElementById("count-broken");
  if (cBroken) cBroken.innerText = scopedBroken;
  const cEmpty = document.getElementById("count-empty");
  if (cEmpty) cEmpty.innerText = scopedEmpty;
  const cHealthy = document.getElementById("count-healthy");
  if (cHealthy) cHealthy.innerText = scopedHealthy;
  const cColado = document.getElementById("count-colado");
  if (cColado) cColado.innerText = scopedProducts.filter(p => p.live && ["COLADO_ATUAL", "COLADO_DESATUALIZADO", "COLADO_SEM_MARCADOR"].includes(p.live.s)).length;
  const cRecolar = document.getElementById("count-recolar");
  if (cRecolar) cRecolar.innerText = scopedProducts.filter(p => p.live && ["COLADO_DESATUALIZADO", "COLADO_SEM_MARCADOR"].includes(p.live.s)).length;
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
  const products = storeData.products || [];
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
  allDiv.onclick = () => {
    selectedCategory = "all";
    currentFilter = "all";
    syncFilterButtons();
    updateCockpit();
    renderProducts();
    highlightCategory(allDiv);
  };
  allDiv.innerHTML = `
    <div class="relative w-16 h-16 rounded-full p-0.5 bg-blue-600 transition-all transform group-hover:scale-105 shadow-md flex items-center justify-center text-white font-extrabold text-xl">
      🌐
      <span class="absolute -bottom-1 right-0 bg-slate-900 text-white text-[9px] font-extrabold px-1.5 py-0.2 rounded-full border border-white">${products.length}</span>
    </div>
    <span class="text-xs font-bold text-slate-700 group-hover:text-blue-600">Todas</span>
  `;
  categoriesRail.appendChild(allDiv);

  categoriesList.forEach(cat => {
    const div = document.createElement("div");
    div.className = "flex flex-col items-center gap-2 cursor-pointer flex-shrink-0 group w-20 text-center";
    div.onclick = () => {
      selectedCategory = cat.name;
      currentFilter = "all";
      syncFilterButtons();
      updateCockpit();
      renderProducts();
      highlightCategory(div);
    };
    
    const catCount = cat.count || products.filter(p => p.category === cat.name).length;
    const ringClass = cat.broken_count > 0 ? "category-ring has-broken" : "category-ring";
    const imgUrl = cat.sample_image || cat.thumb || "https://placehold.co/100x100?text=BRK";

    div.innerHTML = `
      <div class="relative w-16 h-16 rounded-full p-[2px] ${ringClass} transition-all transform group-hover:scale-105 shadow-md">
        <img src="${imgUrl}" alt="${cat.name}" class="w-full h-full object-cover rounded-full bg-white p-0.5" loading="lazy" />
        ${cat.broken_count > 0 ? `<span class="absolute -top-1 -right-1 bg-red-600 text-white text-[9px] font-extrabold px-1.5 py-0.2 rounded-full border border-white">!</span>` : ''}
        <span class="absolute -bottom-1 right-0 bg-slate-900 text-white text-[9px] font-extrabold px-1.5 py-0.2 rounded-full border border-white" title="${catCount} produto(s) nesta categoria">${catCount}</span>
      </div>
      <span class="text-[11px] font-semibold text-slate-700 truncate w-full group-hover:text-blue-600 block" title="${cat.name} (${catCount})">${cat.name}</span>
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
    const isEmpty = p.status === "SEM_DESCRICAO";
    const isHealthy = !isBroken && !isEmpty;

    if (currentFilter === "broken" && !isBroken) return false;
    if (currentFilter === "empty" && !isEmpty) return false;
    if (currentFilter === "healthy" && !isHealthy) return false;
    if (currentFilter === "colado" && !(p.live && ["COLADO_ATUAL", "COLADO_DESATUALIZADO", "COLADO_SEM_MARCADOR"].includes(p.live.s))) return false;
    if (currentFilter === "recolar" && !(p.live && ["COLADO_DESATUALIZADO", "COLADO_SEM_MARCADOR"].includes(p.live.s))) return false;

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
    const isEmpty = p.status === "SEM_DESCRICAO";

    let borderClass = "border-slate-200 hover:border-blue-400";
    let statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800 flex items-center gap-1" title="Status na Loja Shopify: Sem fotos quebradas e com texto existente">${getSvgIcon('check', '#065f46', 10)} Na Loja: Sem Erro Crítico</span>`;

    if (isBroken) {
      borderClass = "border-red-300 hover:border-red-500 bg-red-50/20";
      statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800 flex items-center gap-1" title="Status na Loja Shopify: Contém imagens da AWS S3 com erro 404">❌ Fotos Quebradas AWS</span>`;
    } else if (isEmpty) {
      borderClass = "border-amber-300 hover:border-amber-500 bg-amber-50/20";
      statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-800 flex items-center gap-1" title="Status na Loja Shopify: Produto sem descrição cadastrada">⚠️ Sem Descrição</span>`;
    }

    if (!isBroken && !isEmpty && typeof LiveAgent !== "undefined") {
      const lb = LiveAgent.badgeFor(p.live);
      if (lb) {
        statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold ${lb.cls} flex items-center gap-1" title="${lb.title}">${lb.text}</span>`;
      }
    }

    const card = document.createElement("div");
    card.className = `bg-white rounded-2xl border ${borderClass} p-4 product-shadow transition-all flex flex-col justify-between cursor-pointer group`;
    card.onclick = () => openProductModal(p);

    const allImages = (p.cdn_images && p.cdn_images.length ? p.cdn_images : (p.gallery && p.gallery.length ? p.gallery : (p.image ? [p.image] : []))).filter(Boolean);
    const imgSrc = allImages[0] || "https://placehold.co/400x300?text=Sem+Foto";
    const fallbacksJson = JSON.stringify(allImages.slice(1)).replace(/"/g, '&quot;');
    const safeTitle = (p.title || '').replace(/"/g, '&quot;');

    card.innerHTML = `
      <div>
        <div class="relative w-full h-44 rounded-xl overflow-hidden bg-slate-100 mb-3 border border-slate-100">
          <img src="${imgSrc}" 
               alt="${safeTitle}" 
               data-fallbacks="${fallbacksJson}"
               data-fallback-idx="0"
               onerror="try { const fbs = JSON.parse(this.getAttribute('data-fallbacks') || '[]'); const idx = parseInt(this.getAttribute('data-fallback-idx') || '0'); if (idx < fbs.length) { this.setAttribute('data-fallback-idx', idx + 1); this.src = fbs[idx]; } else { this.onerror = null; this.src = 'https://placehold.co/400x300?text=Foto+Indisponivel'; } } catch(e) { this.onerror = null; this.src = 'https://placehold.co/400x300?text=Foto+Indisponivel'; }"
               referrerpolicy="no-referrer"
               class="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300" 
               loading="lazy" />
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
        <span class="text-[10px] font-extrabold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md flex items-center gap-1" title="Molde de alta conversão pronto para este produto">
          <span>✨</span> ${p.archetype_name || 'Modo B Oficial'}
        </span>
        <button onclick="quickCopyProductHTML(event, '${p.master_sku}')" title="Copia o Novo Padrão Oficial Modo B (3 Atos + Badges + Tabela de Medidas + Schema SEO) pronto para colar no Admin da Shopify" class="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-700 border border-emerald-300 rounded-lg text-[10px] font-extrabold transition-all flex items-center gap-1 active:scale-95 shadow-sm">
          <span>📋 Copiar Modo B</span>
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
    showToast(`✅ Modo B (Novo Padrão Oficial) copiado! Cole no Admin da Shopify.`);
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
    selectedMassProductIds.add(String(p.id));
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

let currentMassBatchMode = "mode_b_html";

function toggleSelectAllMass(masterCheckbox) {
  const checkboxes = document.querySelectorAll(".mass-row-check");
  checkboxes.forEach(cb => {
    cb.checked = masterCheckbox.checked;
    const id = String(cb.dataset.id);
    if (masterCheckbox.checked) selectedMassProductIds.add(id);
    else selectedMassProductIds.delete(id);
  });
  document.getElementById("mass-selected-count").innerText = selectedMassProductIds.size;
}

function handleMassRowCheck(cb) {
  const id = String(cb.dataset.id);
  if (cb.checked) selectedMassProductIds.add(id);
  else selectedMassProductIds.delete(id);
  document.getElementById("mass-selected-count").innerText = selectedMassProductIds.size;
}

function executeMassBatch(modeKey) {
  if (selectedMassProductIds.size === 0) {
    alert("Por favor, selecione ao menos um produto para gerar o lote.");
    return;
  }
  currentMassBatchMode = modeKey;
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (storeData && storeData.products) {
    storeData.products.forEach(p => {
      if (selectedMassProductIds.has(String(p.id))) {
        if (modeKey === "mode_b_html" && !p.mode_b_html && typeof getProductModeBHTML === "function") {
          p.mode_b_html = getProductModeBHTML(p);
        }
      }
    });
  }
  const modeName = modeKey === "mode_b_html" ? "Modo B (3 Atos Conversão)" : "Modo A (Preservar HTML)";
  showToast(`✨ Lote configurado: ${selectedMassProductIds.size} produtos gerados via ${modeName}! Clique em 'Baixar Planilha CSV' para exportar.`);
}

function downloadShopifyCSVBatch() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData) return;
  const products = storeData.products;
  const selected = products.filter(p => selectedMassProductIds.has(String(p.id)));
  
  if (selected.length === 0) {
    alert("Nenhum produto selecionado para exportação.");
    return;
  }

  const rows = ["Handle,Title,Body (HTML)"];
  selected.forEach(p => {
    let html = "";
    if (currentMassBatchMode === "mode_b_html") {
      if (!p.mode_b_html && typeof getProductModeBHTML === "function") {
        p.mode_b_html = getProductModeBHTML(p);
      }
      html = p.mode_b_html || "";
    } else {
      html = p.mode_a_html || p.original_body_html || "";
    }
    rows.push(`"${p.handle}","${p.title.replace(/"/g, '""')}","${html.replace(/"/g, '""')}"`);
  });

  const csvContent = "\uFEFF" + rows.join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  const modeLabel = currentMassBatchMode === "mode_b_html" ? "modo_b" : "modo_a";
  link.download = `shopify_lote_${modeLabel}_${currentStore}_${new Date().toISOString().slice(0,10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  showToast(`Planilha CSV com ${selected.length} produtos gerada e baixada com sucesso (${modeLabel.toUpperCase()})!`);
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

    const isD2C = m.layout_format === "d2c_headwear" || (m.details_grid && m.details_grid.length > 0);
    const badgeHtml = isD2C 
      ? `<span class="px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-300">Novo Formato D2C Oficial</span>`
      : `<span class="px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-blue-50 text-blue-700 border border-blue-200">Molde Mestre</span>`;

    let structureBlockHtml = "";
    if (isD2C && m.details_grid) {
      const gridItems = m.details_grid.map(d => `<li class="flex items-start gap-1"><span class="text-emerald-500 font-bold">✓</span> <strong class="text-slate-800">${d.title}:</strong> <span class="text-slate-600">${d.desc.slice(0, 60)}...</span></li>`).join("");
      structureBlockHtml = `
        <div class="space-y-2 mb-4 bg-emerald-50/60 p-3 rounded-2xl border border-emerald-100 text-xs">
          <span class="text-[10px] font-extrabold uppercase text-emerald-800 block tracking-wider">Estrutura D2C (Grid 4x + Split + Caixa BRK):</span>
          <ul class="space-y-1 text-[11px]">
            ${gridItems}
          </ul>
          <div class="mt-2 pt-2 border-t border-emerald-200/60 text-[10px] text-emerald-700 font-semibold flex items-center gap-1.5">
            <span>📦 Seções Split: Selo Produto Premium (Tags) + Entrega Segura na Caixa BRK</span>
          </div>
        </div>
      `;
    } else {
      structureBlockHtml = `
        <div class="space-y-2 mb-4 bg-slate-50 p-3 rounded-2xl border border-slate-100 text-xs">
          <span class="text-[10px] font-extrabold uppercase text-slate-400 block tracking-wider">Atos Narrativos:</span>
          <div class="font-bold text-slate-700">1. ${m.act1 ? m.act1.tag : 'Ato 1'}</div>
          <div class="font-bold text-slate-700">2. ${m.act2 ? m.act2.tag : 'Ato 2'}</div>
          <div class="font-bold text-slate-700">3. ${m.act3 ? m.act3.tag : 'Ato 3'}</div>
        </div>
      `;
    }

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-3">
          ${badgeHtml}
          <span class="text-xs text-slate-400 font-mono">ID: ${m.id}</span>
        </div>
        <h3 class="text-base font-extrabold text-slate-900 font-heading mb-1">${m.name}</h3>
        <p class="text-xs font-semibold ${isD2C ? 'text-emerald-700' : 'text-blue-600'} mb-4">${m.default_tagline || ''}</p>

        ${structureBlockHtml}

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

// Aba Análises & Auditoria 360
async function renderAnalyticsView() {
  for (const sk of ["brk_fishing", "brk_agro", "brk_motors"]) {
    if (!MASTER_PAYLOAD.stores[sk]) {
      try {
        MASTER_PAYLOAD.stores[sk] = await StoreLoader.loadStore(sk);
      } catch (e) {}
    }
  }

  const mapIds = [
    { key: "brk_fishing", prefix: "fishing" },
    { key: "brk_agro", prefix: "agro" },
    { key: "brk_motors", prefix: "motors" }
  ];

  mapIds.forEach(({ key, prefix }) => {
    const sData = MASTER_PAYLOAD.stores[key];
    if (!sData || !sData.products) return;
    const prods = sData.products;
    const totalP = prods.length;
    const totalSkus = (sData.store && sData.store.total_skus) || totalP;
    const brokenP = prods.filter(p => p.status === "IMAGENS_QUEBRADAS").length;
    const emptyP = prods.filter(p => p.status === "SEM_DESCRICAO").length;
    const healthyP = totalP - brokenP - emptyP;
    const pct = totalP > 0 ? ((healthyP / totalP) * 100).toFixed(1) : "100.0";

    const elHealth = document.getElementById(`stat-${prefix}-health`);
    if (elHealth) elHealth.innerText = `${pct}%`;
    const elSkus = document.getElementById(`stat-${prefix}-skus`);
    if (elSkus) elSkus.innerText = `${totalP.toLocaleString('pt-BR')} produtos (${totalSkus.toLocaleString('pt-BR')} SKUs)`;
    const elBroken = document.getElementById(`stat-${prefix}-broken`);
    if (elBroken) elBroken.innerText = `${brokenP.toLocaleString('pt-BR')} ${brokenP === 1 ? 'produto' : 'produtos'}`;
    const elEmpty = document.getElementById(`stat-${prefix}-empty`);
    if (elEmpty) elEmpty.innerText = `${emptyP.toLocaleString('pt-BR')} ${emptyP === 1 ? 'produto' : 'produtos'}`;
    const elFixes = document.getElementById(`stat-${prefix}-fixes`);
    if (elFixes) elFixes.innerText = `${healthyP.toLocaleString('pt-BR')} saudáveis (100% Modo B)`;
    const elBar = document.getElementById(`bar-${prefix}-health`);
    if (elBar) elBar.style.width = `${pct}%`;
  });

  renderAuditTable();
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
      <button onclick="downloadDailyCSVByName('${c.filename}')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all">
        Baixar ⬇️
      </button>
    `;
    listContainer.appendChild(card);
  });
}

async function downloadDailyCSVByName(filename) {
  try {
    const res = await fetch(`./reports/daily_fixes/${filename}`);
    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast(`Planilha ${filename} baixada com sucesso!`);
      return;
    }
  } catch(e) {
    console.warn("Download local fallback...", e);
  }
  downloadLatestDailyCSV();
}

function downloadLatestDailyCSV() {
  const rows = ["Handle,Title,Body (HTML)"];
  let count = 0;

  for (const [storeKey, sData] of Object.entries(MASTER_PAYLOAD.stores)) {
    if (!sData || !sData.products) continue;
    sData.products.forEach(p => {
      if (p.status === "IMAGENS_QUEBRADAS" || p.status === "SEM_DESCRICAO") {
        const html = p.mode_b_html || (typeof getProductModeBHTML === "function" ? getProductModeBHTML(p) : "") || p.mode_a_html || "";
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


// =========================================================================
// INTEGRAÇÃO COM USERSCRIPT TAMPERMONKEY (MODO ASSISTIDO SHOPIFY)
// =========================================================================

function buildQueueItem(p) {
  let html = p.mode_b_html;
  if (!html && typeof getProductModeBHTML === "function") {
    html = getProductModeBHTML(p);
  }
  return {
    id: String(p.id),
    handle: p.handle,
    master_sku: p.master_sku || p.sku || "",
    title: p.title || "Sem Título",
    is_mode_b_compliant: !!p.is_mode_b_compliant,
    guideline_status: p.guideline_status || p.status || "FORA_PADRAO_MODO_B",
    guideline_reason: p.guideline_reason || "",
    mode_b_html: html || p.body_html || ""
  };
}

function sendBatchToTampermonkey(limit = 25) {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData || !storeData.products) {
    showToast("⚠️ Aguarde o carregamento do catálogo...");
    return;
  }

  // Filtrar estritamente apenas produtos fora das diretrizes (excluindo CONFORME_MODO_B)
  const nonCompliant = storeData.products.filter(p => !p.is_mode_b_compliant);
  const outdated = nonCompliant.filter(p => p.guideline_status === "MODO_B_DESATUALIZADO");
  const empty = nonCompliant.filter(p => p.guideline_status === "SEM_DESCRICAO" || p.status === "SEM_DESCRICAO");
  const broken = nonCompliant.filter(p => p.guideline_status === "IMAGENS_QUEBRADAS" || p.status === "IMAGENS_QUEBRADAS");
  const legacy = nonCompliant.filter(p => p.guideline_status === "FORA_PADRAO_MODO_B");

  // Ordem prioritária: Violações em Modo B já colado -> Sem Descrição -> Imagens Quebradas -> Legados fora do Modo B
  const seenIds = new Set();
  const candidates = [];
  for (const p of [...outdated, ...empty, ...broken, ...legacy]) {
    const pid = String(p.id);
    if (!seenIds.has(pid)) {
      seenIds.add(pid);
      candidates.push(p);
    }
  }
  const label = "fora das diretrizes Modo B v5";

  const batch = candidates.slice(0, limit);
  if (batch.length === 0) {
    alert("✅ Todos os produtos desta loja já estão 100% dentro das diretrizes Modo B v5!");
    return;
  }

  const items = batch.map(buildQueueItem);
  const storeSlugMap = {
    "brk_fishing": "brkfishing",
    "brk_agro": "brkagro",
    "brk_motors": "brkmotors25"
  };
  const storeSlug = storeSlugMap[currentStore] || "brkfishing";

  // Enviar postMessage para o Tampermonkey caso esteja rodando na página
  window.postMessage({
    type: "BRK_LOAD_QUEUE",
    payload: {
      items: items,
      storeKey: currentStore,
      storeSlug: storeSlug,
      autoStart: true
    }
  }, "*");

  // Salvar no localStorage como fallback
  localStorage.setItem("BRK_TM_ACTIVE_QUEUE", JSON.stringify(items));
  localStorage.setItem("BRK_TM_STORE_SLUG", storeSlug);

  showToast(`⚡ Lote de ${items.length} produtos ${label} preparado para o Tampermonkey!`);

  // Se o Tampermonkey não responder em 800ms, abre o modal de assistência
  setTimeout(() => {
    if (!window.__BRK_TAMPERMONKEY_INSTALLED) {
      openTampermonkeyModal(items, storeSlug);
    }
  }, 600);
}

// Dispara lote 100% automático de uma Coleção específica (ex: Super Ofertas 🔥 91 itens ou 32 Camisas/Outros Rastreados) direto da API para o Tampermonkey
async function sendCollectionToTampermonkey(categoryFilter = "super_ofertas", statusFilter = "COLECAO_COMPLETA", limit = 100, customCollectionUrl = "") {
  const targetStore = (categoryFilter === "super_ofertas" || categoryFilter === "rastreados_camisas" || (customCollectionUrl && customCollectionUrl.includes("brkfishing")))
    ? "brk_fishing"
    : currentStore;

  const storeSlugMap = {
    "brk_fishing": "brkfishing",
    "brk_agro": "brkagro",
    "brk_motors": "brkmotors25"
  };
  const storeSlug = storeSlugMap[targetStore] || "brkfishing";
  const collectionParam = customCollectionUrl || (categoryFilter === "super_ofertas" ? "super-ofertas-🔥" : "");

  showToast(`🔥 Carregando lote (${collectionParam || categoryFilter}) no Piloto Automático...`);

  try {
    const apiUrl = `/api/product_db?store=${encodeURIComponent(targetStore)}&action=queue&category=${encodeURIComponent(categoryFilter)}&collection=${encodeURIComponent(collectionParam)}&status=${encodeURIComponent(statusFilter)}&limit=${encodeURIComponent(limit)}`;
    const resp = await fetch(apiUrl);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    if (!data.success || !Array.isArray(data.items) || data.items.length === 0) {
      alert(`⚠️ Nenhum produto retornado para o filtro (${statusFilter} / ${collectionParam || categoryFilter}).`);
      return;
    }

    // Força is_mode_b_compliant=false no payload de coleção completa ou rastreados para que qualquer versão do Tampermonkey processe todos os itens automaticamente
    const forceProcessAll = ["COLECAO_COMPLETA", "RASTREADOS_TROCA_DESCOMPLICADA", "AJUSTE_FOTOS_GERAL", "CRITICOS_FOTOS_CORES", "COR_SEM_FOTO", "FOTOS_DUPLICADAS", "FOTOS_BAIXA_QUALIDADE"].includes(statusFilter) || categoryFilter === "rastreados_camisas";
    const items = data.items.map(it => ({
      ...it,
      is_mode_b_compliant: forceProcessAll ? false : Boolean(it.is_mode_b_compliant)
    }));

    window.postMessage({
      type: "BRK_LOAD_QUEUE",
      payload: {
        items: items,
        storeKey: targetStore,
        storeSlug: storeSlug,
        autoStart: true,
        autoPilot: true,
        autoSave: true,
        forceAll: forceProcessAll,
        collectionName: collectionParam || categoryFilter,
        statusFilter: statusFilter
      }
    }, "*");

    localStorage.setItem("BRK_TM_ACTIVE_QUEUE", JSON.stringify(items));
    localStorage.setItem("BRK_TM_STORE_SLUG", storeSlug);

    showToast(`🚀 Coleção carregada (${items.length} produtos)! Abrindo Piloto Automático no Shopify Admin...`);

    setTimeout(() => {
      if (!window.__BRK_TAMPERMONKEY_INSTALLED) {
        openTampermonkeyModal(items, storeSlug);
      }
    }, 600);
  } catch (err) {
    console.error("Erro ao carregar lote da coleção:", err);
    alert(`Erro ao carregar fila da coleção: ${err.message}`);
  }
}

function sendCustomCollectionFromPortal() {
  const selEl = document.getElementById("portal-collection-select");
  const urlEl = document.getElementById("portal-collection-url");
  const rawChoice = selEl ? selEl.value : "super_ofertas|COLECAO_COMPLETA";
  const customUrl = urlEl ? urlEl.value.trim() : "";

  const [cat, st] = rawChoice.split("|");
  const effectiveStatus = st || (cat === "rastreados_camisas" ? "RASTREADOS_TROCA_DESCOMPLICADA" : "COLECAO_COMPLETA");
  if (customUrl) {
    sendCollectionToTampermonkey("ALL", effectiveStatus, 100, customUrl);
  } else {
    sendCollectionToTampermonkey(cat || "super_ofertas", effectiveStatus, 100, "");
  }
}

function sendSelectedMassToTampermonkey() {
  const storeData = MASTER_PAYLOAD.stores[currentStore];
  if (!storeData || !storeData.products) return;
  const selected = storeData.products.filter(p => selectedMassProductIds.has(String(p.id)));

  if (selected.length === 0) {
    alert("Nenhum produto selecionado na tabela de massa.");
    return;
  }

  const items = selected.map(buildQueueItem);
  const storeSlugMap = {
    "brk_fishing": "brkfishing",
    "brk_agro": "brkagro",
    "brk_motors": "brkmotors25"
  };
  const storeSlug = storeSlugMap[currentStore] || "brkfishing";

  window.postMessage({
    type: "BRK_LOAD_QUEUE",
    payload: {
      items: items,
      storeKey: currentStore,
      storeSlug: storeSlug,
      autoStart: true
    }
  }, "*");

  localStorage.setItem("BRK_TM_ACTIVE_QUEUE", JSON.stringify(items));
  localStorage.setItem("BRK_TM_STORE_SLUG", storeSlug);

  showToast(`⚡ ${items.length} produtos selecionados enviados para o Tampermonkey!`);

  setTimeout(() => {
    if (!window.__BRK_TAMPERMONKEY_INSTALLED) {
      openTampermonkeyModal(items, storeSlug);
    }
  }, 600);
}

function openTampermonkeyModal(items = null, storeSlug = "brkfishing") {
  let modal = document.getElementById("brk-tm-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "brk-tm-modal";
    modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm";
    document.body.appendChild(modal);
  }

  const activeQueue = items || JSON.parse(localStorage.getItem("BRK_TM_ACTIVE_QUEUE") || "[]");
  const count = activeQueue.length;
  const firstId = count > 0 ? activeQueue[0].id : null;
  const firstUrl = firstId ? `https://admin.shopify.com/store/${storeSlug}/products/${firstId}` : "#";

  modal.innerHTML = `
    <div class="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-xl w-full p-6 text-slate-800 space-y-5 animate-scale-in">
      <div class="flex items-center justify-between border-b border-slate-100 pb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white text-xl shadow-md">
            ⚡
          </div>
          <div>
            <h3 class="text-base font-extrabold text-slate-900 font-heading">Assistente Tampermonkey BRK v6.0 (Mini-Dashboard Cockpit)</h3>
            <p class="text-xs text-slate-500">Painel Executivo dentro do Shopify Admin com KPIs, Barra de Progresso, Abas e Piloto Automático</p>
          </div>
        </div>
        <button onclick="closeTampermonkeyModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold flex items-center justify-center transition-all">✕</button>
      </div>

      <div class="space-y-3 text-xs leading-relaxed">
        <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-700">Status da Fila Carregada:</span>
            <span class="font-mono font-extrabold px-2 py-0.5 rounded-full ${count > 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'}">
              ${count} produtos prontos
            </span>
          </div>
          ${count > 0 ? `
            <p class="text-slate-600 text-[11px]">Primeiro produto: <strong class="text-slate-900">${activeQueue[0].master_sku || ''}</strong> - ${(activeQueue[0].title || '').slice(0, 48)}...</p>
          ` : ''}
        </div>

        <div class="p-4 bg-red-50 rounded-2xl border border-red-200 space-y-2 text-red-950">
          <h4 class="font-bold flex items-center gap-1.5 text-xs">
            <span>🚨</span> Prioridades de Aplicação Automática (v6.0):
          </h4>
          <div class="flex flex-wrap gap-2 pt-1">
            <button onclick="sendCollectionToTampermonkey('ALL', 'PRIORIDADE_CRITICA', 50)" class="px-3.5 py-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-xl text-xs font-extrabold shadow-sm transition-all">
              🚨 1º Críticos (S3 404 + Sem Descrição)
            </button>
            <button onclick="sendCollectionToTampermonkey('camisas', 'FORA_DIRETRIZES', 50)" class="px-3 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold shadow-sm transition-all">
              👕 Lote Camisas UV
            </button>
            <button onclick="sendCollectionToTampermonkey('bones_chapeus', 'FORA_DIRETRIZES', 50)" class="px-3 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold shadow-sm transition-all">
              🧢 Lote Bonés D2C
            </button>
          </div>
        </div>

        <div class="p-4 bg-purple-50 rounded-2xl border border-purple-200 space-y-2 text-purple-900">
          <h4 class="font-bold flex items-center gap-1.5 text-xs text-purple-950">
            <span>🎛️</span> Instalar ou Atualizar Mini-Dashboard Tampermonkey v6.1.0:
          </h4>
          <ol class="list-decimal pl-4 space-y-1 text-[11px] text-purple-800">
            <li>Clique para instalar/atualizar o script v6.1.0 no seu Tampermonkey: <a href="tampermonkey/brk_assistente_shopify.user.js?v=6.1.0" target="_blank" class="font-bold underline text-purple-700 hover:text-purple-900">Instalar / Atualizar Userscript v6.1.0</a>.</li>
            <li>O novo <strong>Mini-Dashboard Cockpit v6.1.0</strong> traz alocação inteligente de <strong>Capa Humanizada ([0], [1], [3] sem foto de costas no Ato 3)</strong>, 4 Cards KPI clicáveis, barra de progresso, busca rápida por SKU e botão <strong>Minimizar (—)</strong>.</li>
          </ol>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
        <button onclick="copyTampermonkeyQueueJson()" class="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5">
          <span>📋 Copiar Fila JSON</span>
        </button>
        <div class="flex items-center gap-2">
          <button onclick="closeTampermonkeyModal()" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all">
            Fechar
          </button>
          ${firstId ? `
            <a href="${firstUrl}" target="_blank" class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-extrabold shadow-md transition-all flex items-center gap-1.5">
              <span>🚀 Abrir 1º Produto no Shopify Admin</span>
            </a>
          ` : ''}
        </div>
      </div>
    </div>
  `;
  modal.classList.remove("hidden");
}

function closeTampermonkeyModal() {
  const modal = document.getElementById("brk-tm-modal");
  if (modal) modal.classList.add("hidden");
}

function copyTampermonkeyQueueJson() {
  const activeQueue = localStorage.getItem("BRK_TM_ACTIVE_QUEUE") || "[]";
  navigator.clipboard.writeText(activeQueue).then(() => {
    showToast("📋 Fila JSON copiada para a área de transferência!");
  }).catch(() => {
    alert("Não foi possível copiar automaticamente.");
  });
}

// Autenticação por Senha do Sistema BRK (acesso liberado para qualquer IP mediante senha)
const BRK_AUTH_TOKEN_KEY = "BRK_PORTAL_PASSWORD_AUTH_V2";
const BRK_AUTH_TOKEN_VAL = "BRK_REX123_AUTHORIZED";
const BRK_SYSTEM_PASSWORD = "rex123";

function renderPasswordLoginScreen() {
  Array.from(document.body.children).forEach(el => {
    if (el.id !== "brk-ip-lock-overlay") el.style.display = "none";
  });

  let overlay = document.getElementById("brk-ip-lock-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "brk-ip-lock-overlay";
    overlay.className = "fixed inset-0 z-[9999] bg-slate-950 flex items-center justify-center p-4 text-white";
    document.body.appendChild(overlay);
  }

  overlay.innerHTML = `
    <div class="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-7 shadow-2xl text-center space-y-5">
      <div class="w-14 h-14 mx-auto rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-2xl">
        🔐
      </div>
      <div class="space-y-1.5">
        <span class="px-2.5 py-0.5 rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/30 text-[10px] font-extrabold uppercase tracking-wider">
          Central Mestre BRK
        </span>
        <h1 class="text-lg font-extrabold text-white pt-1">Acesso ao Sistema de Descrições</h1>
        <p class="text-xs text-slate-400 leading-relaxed">
          Digite a senha de acesso da equipe BRK para entrar no portal.
        </p>
      </div>
      <div class="pt-2 border-t border-slate-800/80 space-y-3 text-left">
        <label class="block text-[11px] font-bold text-slate-300">
          Senha de Acesso:
        </label>
        <div class="flex gap-2">
          <input id="brk-ip-unlock-input" type="password" placeholder="Digite a senha..." onkeydown="if(event.key==='Enter') unlockCurrentMachineByPin()" class="flex-1 px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-blue-500" autofocus />
          <button onclick="unlockCurrentMachineByPin()" class="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-extrabold text-white transition-all shadow-lg shadow-blue-600/20">
            Entrar
          </button>
        </div>
        <p id="brk-ip-unlock-err" class="text-[11px] text-red-400 font-bold hidden">Senha incorreta. Tente novamente.</p>
      </div>
    </div>
  `;

  setTimeout(() => {
    const inp = document.getElementById("brk-ip-unlock-input");
    if (inp) inp.focus();
  }, 80);
}

function unlockCurrentMachineByPin() {
  const inp = document.getElementById("brk-ip-unlock-input");
  const err = document.getElementById("brk-ip-unlock-err");
  const val = (inp ? inp.value : "").trim();
  if (val.toLowerCase() === BRK_SYSTEM_PASSWORD) {
    localStorage.setItem(BRK_AUTH_TOKEN_KEY, BRK_AUTH_TOKEN_VAL);
    const overlay = document.getElementById("brk-ip-lock-overlay");
    if (overlay) overlay.remove();
    Array.from(document.body.children).forEach(el => {
      el.style.display = "";
    });
    switchStore("brk_fishing");
  } else if (err) {
    err.classList.remove("hidden");
  }
}

function logoutBrkPortal() {
  localStorage.removeItem(BRK_AUTH_TOKEN_KEY);
  localStorage.removeItem("BRK_MACHINE_AUTHORIZED_TOKEN");
  renderPasswordLoginScreen();
}

async function verifyMachineIPAccess() {
  // Se já autenticou com a senha rex123 neste navegador, entra direto
  if (localStorage.getItem(BRK_AUTH_TOKEN_KEY) === BRK_AUTH_TOKEN_VAL) {
    switchStore("brk_fishing");
    return;
  }
  renderPasswordLoginScreen();
}

// Inicialização Inicial Protegida por Senha
document.addEventListener("DOMContentLoaded", () => {
  verifyMachineIPAccess();
});

