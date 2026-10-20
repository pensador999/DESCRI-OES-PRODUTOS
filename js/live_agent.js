/**
 * BRK Live Agent + Busca Global de SKU (js/live_agent.js)
 *
 * 1) LiveAgent: consulta /api/live_status (Vercel) que le a VITRINE PUBLICA de cada loja
 *    (somente leitura, sem token/Admin) e sobrepoe o status do snapshot do build com o
 *    estado REAL das descricoes: Sem descricao / Fotos quebradas / Colado (Modo B atual,
 *    desatualizado ou sem rastreio) / Saudavel.
 * 2) SkuSearch: busca global de SKU (mestre ou de variante) nas 3 lojas; ao escolher um
 *    resultado troca de loja automaticamente e abre o produto.
 */

const LiveAgent = (() => {
  const isLocalHost = /^(localhost|127\.|\[::1\])/.test(location.hostname);
  const API_BASE = (location.protocol.startsWith("http") && !isLocalHost) ? "" : "https://1025-ten.vercel.app";
  // Blocos de paginas (250 produtos/pagina) pedidos em paralelo para caber no limite de tempo da Vercel
  const CHUNKS = [[1, 5], [6, 10], [11, 14]];
  const AUTO_REFRESH_MS = 5 * 60 * 1000;

  const state = {};       // storeKey -> { fetchedAt, items, version, partial }
  let busy = false;
  let autoTimer = null;

  const COLADO = ["COLADO_ATUAL", "COLADO_DESATUALIZADO", "COLADO_SEM_MARCADOR"];
  const RECOLAR = ["COLADO_DESATUALIZADO", "COLADO_SEM_MARCADOR"];

  function el(id) { return document.getElementById(id); }

  async function fetchChunk(storeKey, from, to, force) {
    const t = force ? `&t=${Date.now()}` : "";
    const url = `${API_BASE}/api/live_status?store=${storeKey}&from=${from}&to=${to}${t}`;
    const resp = await fetch(url, { cache: force ? "no-store" : "default" });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }

  async function fetchStore(storeKey, force) {
    const results = await Promise.allSettled(CHUNKS.map(([a, b]) => fetchChunk(storeKey, a, b, force)));
    const ok = results.filter(r => r.status === "fulfilled").map(r => r.value);
    if (ok.length === 0) throw new Error(results[0].reason ? results[0].reason.message : "API indisponivel");
    const items = {};
    let version = null;
    ok.forEach(d => { Object.assign(items, d.items || {}); version = d.current_version || version; });
    return { fetchedAt: new Date(), items, version, partial: ok.length < CHUNKS.length };
  }

  /** Sobrepoe o status do snapshot com o estado real da vitrine (e restaura se o produto nao estiver publicado). */
  function applyToCatalog(storeKey) {
    const data = MASTER_PAYLOAD.stores[storeKey];
    const live = state[storeKey];
    if (!data || !live) return null;
    const c = { total: 0, live: 0, colado: 0, recolar: 0, empty: 0, broken: 0 };
    (data.products || []).forEach(p => {
      c.total++;
      if (!p._snap) p._snap = { status: p.status, out: p.is_out_of_standard };
      const it = live.items[p.handle];
      if (!it) {                       // nao publicado/nao encontrado: volta ao snapshot do build
        p.live = null; p.status = p._snap.status; p.is_out_of_standard = p._snap.out;
        return;
      }
      c.live++;
      p.live = { s: it.s, v: it.v || null, molde: it.molde || null, u: it.u || null };
      if (it.s === "SEM_DESCRICAO") { p.status = "SEM_DESCRICAO"; p.is_out_of_standard = true; c.empty++; }
      else if (it.s === "IMAGENS_QUEBRADAS") { p.status = "IMAGENS_QUEBRADAS"; p.is_out_of_standard = true; c.broken++; }
      else { p.status = "SAUDAVEL"; p.is_out_of_standard = false; }
      if (COLADO.includes(it.s)) c.colado++;
      if (RECOLAR.includes(it.s)) c.recolar++;
    });
    return c;
  }

  function repaint() {
    if (typeof updateCockpit === "function") updateCockpit();
    if (typeof renderProducts === "function") renderProducts();
    if (typeof updateMassCountBadge === "function") updateMassCountBadge();
    if (typeof currentActiveTab !== "undefined" && currentActiveTab === "tab-mass" && typeof renderMassTable === "function") renderMassTable();
    updateCounters();
  }

  function updateCounters() {
    const data = MASTER_PAYLOAD.stores[currentStore];
    if (!data) return;
    const allProds = data.products || [];
    const prods = (typeof selectedCategory !== "undefined" && selectedCategory !== "all")
      ? allProds.filter(p => p.category === selectedCategory)
      : allProds;
    const colado = prods.filter(p => p.live && COLADO.includes(p.live.s)).length;
    const recolar = prods.filter(p => p.live && RECOLAR.includes(p.live.s)).length;
    const a = el("count-colado"); if (a) a.innerText = colado;
    const b = el("count-recolar"); if (b) b.innerText = recolar;
  }

  function setStatus(html, tone) {
    const s = el("live-agent-status");
    if (!s) return;
    const tones = { ok: "text-emerald-700", warn: "text-amber-700", err: "text-red-600", idle: "text-slate-500" };
    s.className = "text-[11px] font-semibold " + (tones[tone] || tones.idle);
    s.innerHTML = html;
  }

  async function refresh(force) {
    if (busy) return;
    const storeKey = currentStore;
    busy = true;
    const btn = el("btn-live-agent");
    if (btn) { btn.disabled = true; btn.classList.add("opacity-60"); }
    setStatus("🛰️ Verificando descrições na vitrine…", "idle");
    try {
      if (!MASTER_PAYLOAD.stores[storeKey]) await StoreLoader.loadStore(storeKey).then(d => { MASTER_PAYLOAD.stores[storeKey] = d; });
      state[storeKey] = await fetchStore(storeKey, !!force);
      const c = applyToCatalog(storeKey);
      if (storeKey === currentStore) repaint();
      const hh = state[storeKey].fetchedAt.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
      const partial = state[storeKey].partial ? " ⚠️ leitura parcial" : "";
      setStatus(`🛰️ Vitrine verificada às ${hh} • ${c.live}/${c.total} publicados • ✅ ${c.colado} colados • 🔁 ${c.recolar} para recolar • ⚠️ ${c.empty} sem descrição${partial}`, state[storeKey].partial ? "warn" : "ok");
      if (force && typeof showToast === "function") showToast(`🛰️ Status ao vivo atualizado: ${c.colado} colados, ${c.empty} sem descrição.`);
    } catch (e) {
      console.warn("[LiveAgent]", e);
      setStatus(`🛰️ Agente indisponível (${e.message}). Exibindo o último build.`, "err");
      if (force && typeof showToast === "function") showToast("⚠️ Não foi possível consultar a vitrine agora.");
    } finally {
      busy = false;
      if (btn) { btn.disabled = false; btn.classList.remove("opacity-60"); }
    }
  }

  /** Chamado por switchStore() ao terminar de renderizar a loja. */
  function onStoreReady(storeKey) {
    if (state[storeKey]) {            // ja verificado nesta sessao: reaplica na hora e atualiza em segundo plano
      applyToCatalog(storeKey);
      repaint();
      const hh = state[storeKey].fetchedAt.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
      setStatus(`🛰️ Vitrine verificada às ${hh} (cache da sessão)`, "ok");
    }
    refresh(false);
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = setInterval(() => refresh(true), AUTO_REFRESH_MS);
  }

  /** Metadados de exibicao do selo da vitrine (usado nos cards e na busca). */
  function badgeFor(live) {
    if (!live) return null;
    switch (live.s) {
      case "COLADO_ATUAL": return { cls: "bg-emerald-100 text-emerald-800", text: "✅ Colado — Modo B atual", title: "Descrição Modo B (v" + live.v + ") confirmada na vitrine da loja" };
      case "COLADO_DESATUALIZADO": return { cls: "bg-orange-100 text-orange-800", text: "🔁 Colado desatualizado (v" + live.v + ")", title: "O padrão Modo B evoluiu: copie e cole novamente" };
      case "COLADO_SEM_MARCADOR": return { cls: "bg-sky-100 text-sky-800", text: "✅ Modo B colado (sem rastreio)", title: "Layout BRK detectado, porém sem o marcador de rastreio. Cole novamente o Modo B atual para habilitar o rastreio." };
      default: return null;
    }
  }

  return { refresh, onStoreReady, badgeFor, state, COLADO, RECOLAR };
})();

const SkuSearch = (() => {
  let index = null;
  let building = null;
  let lastResults = [];

  const STORE_LABEL = { brk_fishing: "🎣 Fishing", brk_agro: "🚜 Agro", brk_motors: "🏁 Motors" };
  const STORE_CLS = { brk_fishing: "bg-sky-100 text-sky-800", brk_agro: "bg-green-100 text-green-800", brk_motors: "bg-orange-100 text-orange-800" };

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));

  async function ensureIndex() {
    if (index) return index;
    if (building) return building;
    building = (async () => {
      const idx = [];
      for (const storeKey of Object.keys(STORE_LABEL)) {
        try {
          const data = MASTER_PAYLOAD.stores[storeKey] || await StoreLoader.loadStore(storeKey);
          if (!MASTER_PAYLOAD.stores[storeKey]) MASTER_PAYLOAD.stores[storeKey] = data;
          (data.products || []).forEach(p => {
            idx.push({
              store: storeKey, handle: p.handle, title: p.title || "",
              sku: String(p.master_sku || "").toUpperCase(),
              vars: (p.variants_skus || []).map(v => String(v).toUpperCase())
            });
          });
        } catch (e) { console.warn("[SkuSearch] loja indisponivel:", storeKey, e); }
      }
      index = idx;
      return idx;
    })();
    return building;
  }

  function score(entry, q) {
    if (entry.sku === q) return 100;
    if (entry.vars.includes(q)) return 95;
    if (entry.sku.startsWith(q)) return 80;
    if (entry.vars.some(v => v.startsWith(q))) return 70;
    if (entry.sku.includes(q)) return 50;
    if (entry.vars.some(v => v.includes(q))) return 40;
    return 0;
  }

  function search(raw) {
    const q = String(raw || "").trim().toUpperCase();
    if (q.length < 2 || !index) return [];
    const out = [];
    for (const e of index) {
      const s = score(e, q);
      if (s > 0) out.push({ e, s, matchedVar: e.sku !== q ? (e.vars.find(v => v === q) || e.vars.find(v => v.startsWith(q)) || e.vars.find(v => v.includes(q)) || null) : null });
    }
    out.sort((a, b) => b.s - a.s || a.e.sku.localeCompare(b.e.sku));
    return out.slice(0, 30);
  }

  function closeResults() {
    const box = document.getElementById("sku-global-results");
    if (box) box.classList.add("hidden");
  }

  function render(results, q) {
    const box = document.getElementById("sku-global-results");
    if (!box) return;
    lastResults = results;
    if (!q || q.trim().length < 2) { box.classList.add("hidden"); return; }
    if (results.length === 0) {
      box.innerHTML = `<div class="p-3 text-xs text-slate-500">Nenhum SKU encontrado para <b>${esc(q)}</b> nas 3 lojas.</div>`;
      box.classList.remove("hidden");
      return;
    }
    box.innerHTML = results.map((r, i) => {
      const prod = (MASTER_PAYLOAD.stores[r.e.store] && MASTER_PAYLOAD.stores[r.e.store].products || []).find(p => p.handle === r.e.handle);
      const lb = LiveAgent.badgeFor(prod && prod.live);
      const stat = prod ? (prod.status === "SEM_DESCRICAO" ? "⚠️ Sem descrição" : prod.status === "IMAGENS_QUEBRADAS" ? "❌ Fotos quebradas" : "") : "";
      return `<button type="button" data-i="${i}" class="sku-result w-full text-left px-3 py-2 hover:bg-slate-100 border-b border-slate-100 flex items-start gap-2">
        <span class="shrink-0 px-1.5 py-0.5 rounded-md text-[10px] font-extrabold ${STORE_CLS[r.e.store]}">${STORE_LABEL[r.e.store]}</span>
        <span class="min-w-0 flex-1">
          <span class="block text-[11px] font-mono font-bold text-slate-900">${esc(r.e.sku)}${r.matchedVar ? ` <span class="text-blue-600">↳ ${esc(r.matchedVar)}</span>` : ""}</span>
          <span class="block text-[11px] text-slate-600 truncate">${esc(r.e.title)}</span>
        </span>
        ${lb ? `<span class="shrink-0 px-1.5 py-0.5 rounded-full text-[9px] font-extrabold ${lb.cls}">${esc(lb.text)}</span>` : (stat ? `<span class="shrink-0 text-[9px] font-extrabold text-amber-700">${stat}</span>` : "")}
      </button>`;
    }).join("");
    box.classList.remove("hidden");
    box.querySelectorAll(".sku-result").forEach(b => b.onclick = () => pick(parseInt(b.dataset.i, 10)));
  }

  async function pick(i) {
    const r = lastResults[i];
    if (!r) return;
    closeResults();
    const storeKey = r.e.store;
    if (currentStore !== storeKey) await switchStore(storeKey);
    if (typeof switchMainTab === "function" && currentActiveTab !== "tab-catalog") switchMainTab("tab-catalog");
    currentFilter = "all"; selectedCategory = "all";
    if (typeof syncFilterButtons === "function") syncFilterButtons();
    searchQuery = r.e.sku;
    if (searchInput) searchInput.value = r.e.sku;
    renderProducts();
    const prod = (MASTER_PAYLOAD.stores[storeKey].products || []).find(p => p.handle === r.e.handle);
    if (prod && typeof openProductModal === "function") openProductModal(prod);
    const inp = document.getElementById("sku-global-input");
    if (inp) inp.value = "";
  }

  function init() {
    const inp = document.getElementById("sku-global-input");
    if (!inp) return;
    let timer = null;
    const run = async () => { await ensureIndex(); render(search(inp.value), inp.value); };
    inp.addEventListener("focus", () => { ensureIndex(); if (inp.value.trim().length >= 2) run(); });
    inp.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(run, 120); });
    inp.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape") { closeResults(); inp.blur(); }
      if (ev.key === "Enter") { ev.preventDefault(); if (lastResults.length) pick(0); }
    });
    document.addEventListener("click", (ev) => {
      const wrap = document.getElementById("sku-global-wrap");
      if (wrap && !wrap.contains(ev.target)) closeResults();
    });
  }

  return { init, search, ensureIndex };
})();

document.addEventListener("DOMContentLoaded", () => SkuSearch.init());
