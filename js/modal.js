/**
 * BRK Master Portal - Modal Manager & Shopify Direct Sync (modal.js)
 * Gerencia inspeção detalhada de produtos, duplo modo (A vs B), bunker media linker,
 * cópia em Markdown/HTML e sincronização direta cirúrgica com a Shopify via /api/shopify_direct.
 */

let currentModalProduct = null;
let currentModalMode = "b"; // 'b', 'a', 'orig'

function openProductModal(product) {
  currentModalProduct = product;
  currentModalMode = "b";

  if (!product.mode_b_html && typeof getProductModeBHTML === "function") {
    product.mode_b_html = getProductModeBHTML(product);
  }
  if (!product.mode_b_markdown && typeof buildClientModeBMarkdown === "function") {
    product.mode_b_markdown = buildClientModeBMarkdown(product);
  }

  document.getElementById("modal-title").innerText = product.title;
  document.getElementById("modal-store-badge").innerText = product.store_key ? product.store_key.replace('_', ' ').toUpperCase() : "BRK";
  document.getElementById("modal-sku-badge").innerText = "SKU: " + (product.master_sku || product.id);
  document.getElementById("modal-variants-badge").innerText = (product.variants_skus ? product.variants_skus.length : 1) + " Variantes Agrupadas";
  document.getElementById("modal-archetype-badge").innerText = product.archetype_name || "Molde Padrão";

  const openAdminBtn = document.getElementById("modal-open-admin-btn");
  if (openAdminBtn) {
    const storeMap = {
      "brk_fishing": "use-brk-fishing.myshopify.com",
      "brk_agro": "use-brk-agro.myshopify.com",
      "brk_motors": "use-brk-motors.myshopify.com"
    };
    const domain = storeMap[product.store_key || currentStore] || "use-brk-fishing.myshopify.com";
    openAdminBtn.href = `https://${domain}/admin/products/${product.id}`;
  }

  const sourceBadge = document.getElementById("modal-source-badge");
  if (sourceBadge) {
    if (product.source_type === "sibling_template" && product.sibling_info) {
      sourceBadge.className = "px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30 text-[10px]";
      sourceBadge.innerText = `✨ Irmão Homólogo: ${product.sibling_info.sibling_title.slice(0, 24)}... (${Math.round(product.sibling_info.similarity_score * 100)}%)`;
      sourceBadge.title = `Molde herdado de produto irmão no site: ${product.sibling_info.sibling_title}`;
      sourceBadge.style.display = "inline-flex";
    } else {
      sourceBadge.className = "px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 font-bold border border-blue-500/30 text-[10px]";
      sourceBadge.innerText = `🎯 Arquétipo: ${product.archetype_name || 'Especializado'}`;
      sourceBadge.title = "Gerado via Arquétipo Vertical Especializado";
      sourceBadge.style.display = "inline-flex";
    }
  }

  // Miniaturas da galeria CDN
  const thumbsContainer = document.getElementById("modal-gallery-thumbs");
  if (thumbsContainer) {
    thumbsContainer.innerHTML = "";
    const rawImgs = product.cdn_images || product.gallery || (product.images || []).map(i => i.src || i) || [];
    const imgs = [...new Set(rawImgs.filter(u => typeof u === "string" && u.trim().length > 0))];
    const countBadge = document.getElementById("modal-photos-count-badge");
    if (countBadge) countBadge.innerText = imgs.length + " Foto(s) Oficiais";
    imgs.forEach((url, idx) => {
      const thumb = document.createElement("img");
      thumb.src = url;
      thumb.alt = "Foto " + (idx + 1);
      thumb.className = "w-8 h-8 object-cover rounded-lg border border-slate-300 shadow-sm cursor-pointer hover:border-blue-500 hover:scale-110 transition-all";
      thumb.title = "Clique para abrir foto oficial em alta resolução";
      thumb.onclick = () => window.open(url, '_blank');
      thumbsContainer.appendChild(thumb);
    });
  }

  updateModalView();
  document.getElementById("product-modal").classList.remove("hidden");
}

function closeProductModal() {
  document.getElementById("product-modal").classList.add("hidden");
}

function switchModalMode(mode) {
  currentModalMode = mode;
  
  const btnB = document.getElementById("btn-mode-b");
  const btnA = document.getElementById("btn-mode-a");
  const btnOrig = document.getElementById("btn-mode-orig");
  const btnDiff = document.getElementById("btn-mode-diff");

  [btnB, btnA, btnOrig, btnDiff].forEach(b => {
    if (b) b.className = "px-3.5 py-1.5 rounded-lg font-bold transition-all text-slate-600 hover:text-slate-900";
  });

  if (mode === "b" && btnB) {
    btnB.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-emerald-600 text-white shadow-sm";
  } else if (mode === "a" && btnA) {
    btnA.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-blue-600 text-white shadow-sm";
  } else if (mode === "orig" && btnOrig) {
    btnOrig.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-red-600 text-white shadow-sm";
  } else if (mode === "diff" && btnDiff) {
    btnDiff.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-indigo-600 text-white shadow-sm";
  }

  updateModalView();
}

function updateModalView() {
  if (!currentModalProduct) return;
  const contentElem = document.getElementById("modal-rendered-content");
  const sourceElem = document.getElementById("modal-source-code");
  const bannerDesc = document.getElementById("modal-mode-desc");
  const banner = document.getElementById("modal-mode-banner");

  let htmlToShow = "";
  if (currentModalMode === "b") {
    if (typeof getProductModeBHTML === "function") {
      currentModalProduct.mode_b_html = getProductModeBHTML(currentModalProduct);
    }
    htmlToShow = currentModalProduct.mode_b_html || "<p>HTML Modo B não disponível</p>";
    if (banner) banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-emerald-50 border-emerald-200 text-emerald-800";
    if (bannerDesc) bannerDesc.innerHTML = "<strong>⭐ Modo B Oficial (Novo Padrão BRK 100/100):</strong> Recomendado para colar na Shopify! Estrutura persuasiva em 3 Atos narrativos com Badges Rápidos no topo, Tabela de Medidas Expansível, Schema.org SEO e SVGs embutidos.";
  } else if (currentModalMode === "a") {
    htmlToShow = currentModalProduct.mode_a_html || currentModalProduct.original_body_html || "<p>Sem HTML original</p>";
    if (banner) banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-blue-50 border-blue-200 text-blue-800";
    if (bannerDesc) bannerDesc.innerHTML = "<strong>Modo A Ativo (Preservação):</strong> 100% do texto e tabelas originais preservados com fotos trocadas por CDN Shopify oficial.";
  } else if (currentModalMode === "orig") {
    htmlToShow = currentModalProduct.original_body_html || "<p class='text-slate-400 italic'>Este produto não continha descrição original cadastrada.</p>";
    if (banner) banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-amber-50 border-amber-200 text-amber-900";
    if (bannerDesc) bannerDesc.innerHTML = "<strong>⚠️ Conteúdo Legado Atual na Shopify:</strong> Exibe como a descrição está gravada hoje na loja (antiga, sem os novos badges, tabela expansível ou schema).";
  } else if (currentModalMode === "diff") {
    if (typeof getProductModeBHTML === "function") {
      currentModalProduct.mode_b_html = getProductModeBHTML(currentModalProduct);
    }
    const htmlB = currentModalProduct.mode_b_html || "<p>HTML Modo B não disponível</p>";
    const htmlA = currentModalProduct.mode_a_html || currentModalProduct.original_body_html || "<p class='text-slate-400 italic'>Sem descrição original prévia cadastrada.</p>";

    if (banner) banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-indigo-50 border-indigo-200 text-indigo-900";
    if (bannerDesc) bannerDesc.innerHTML = "<strong>Comparador Lado a Lado (Diff):</strong> Compare a versão original com a nova versão blindada 100/100 (com Badges Rápidos, 3 Atos, Tabela de Medidas e Schema SEO).";

    htmlToShow = `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
      <!-- Coluna Esquerda: Versao Original / Modo A -->
      <div class="border-2 border-slate-200 rounded-2xl p-4 bg-slate-50/50 shadow-sm flex flex-col">
        <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-200">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-1 rounded-md bg-slate-800 text-white text-[11px] font-extrabold uppercase tracking-wider">Original / Modo A</span>
            <span class="text-xs text-slate-500 font-medium">Estrutura Prévia</span>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">⚠️ Legado</span>
        </div>
        <div class="overflow-y-auto max-h-[680px] bg-white p-4 rounded-xl border border-slate-200 text-xs">
          ${htmlA}
        </div>
      </div>

      <!-- Coluna Direita: Modo B Otimizado BRK -->
      <div class="border-2 border-emerald-300 rounded-2xl p-4 bg-emerald-50/30 shadow-sm flex flex-col">
        <div class="flex items-center justify-between pb-3 mb-4 border-b border-emerald-200">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-1 rounded-md bg-emerald-600 text-white text-[11px] font-extrabold uppercase tracking-wider">Novo Padrão Oficial BRK</span>
            <span class="text-xs text-emerald-800 font-bold">Modo B Blindado</span>
          </div>
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
            <span>✓</span> Score 100/100
          </span>
        </div>
        <div class="overflow-y-auto max-h-[680px] bg-white p-4 rounded-xl border border-slate-200 text-xs">
          ${htmlB}
        </div>
      </div>
    </div>`;
  }

  if (contentElem) contentElem.innerHTML = htmlToShow;
  if (sourceElem) {
    if (currentModalMode === "diff") {
      sourceElem.textContent = currentModalProduct.mode_b_html || "";
    } else {
      sourceElem.textContent = htmlToShow;
    }
  }
}

// Salvar Direto na Shopify via API Serverless Vercel (/api/shopify_direct)
async function saveDirectToShopify(btn) {
  if (!currentModalProduct) return;
  const p = currentModalProduct;
  const htmlToSave = (currentModalMode === "b") ? (p.mode_b_html || "") : (p.mode_a_html || p.original_body_html || "");

  if (!htmlToSave || htmlToSave.trim() === "") {
    showToast("⚠️ Não há conteúdo HTML válido para salvar na Shopify.");
    return;
  }

  const storeNames = {
    "brk_fishing": "BRK Fishing (use-brk-fishing.myshopify.com)",
    "brk_agro": "BRK Agro (use-brk-agro.myshopify.com)",
    "brk_motors": "BRK Motors (use-brk-motors.myshopify.com)"
  };
  const storeDesc = storeNames[currentStore] || currentStore;

  const confirmMsg = `⚡ ATUALIZAÇÃO CIRÚRGICA DE DESCRIÇÃO NA SHOPIFY\n\n` +
    `• Produto: ${p.title}\n` +
    `• ID Shopify: #${p.id || p.master_sku}\n` +
    `• Loja Destino: ${storeDesc}\n` +
    `• Tamanho do HTML: ${htmlToSave.length} caracteres\n\n` +
    `🛡️ REGRA DE SEGURANÇA BLINDADA:\n` +
    `Será transmitido EXCLUSIVAMENTE o campo 'body_html'.\n` +
    `Preços, Estoques, SKUs, Variantes e Fotos permanecerão 100% INTACTOS.\n\n` +
    `Deseja prosseguir com a gravação direta?`;

  if (!confirm(confirmMsg)) return;

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span>⏳ Gravando na Shopify API...</span>`;
  }

  try {
    const resp = await fetch("/api/shopify_direct", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        store_key: currentStore,
        product_id: p.id,
        body_html: htmlToSave
      })
    });

    const result = await resp.json();
    if (resp.ok && result.success) {
      p.original_body_html = htmlToSave;
      p.status = "SAUDAVEL";
      p.is_out_of_standard = false;
      updateCockpit();
      renderProducts();
      showToast(`🚀 Descrição do produto #${p.id} salva diretamente na Shopify!`);
      if (btn) {
        btn.innerHTML = `<span>✅ Salvo na Shopify!</span>`;
        setTimeout(() => {
          btn.disabled = false;
          btn.innerHTML = `<span>⚡ Salvar Direto</span>`;
        }, 3000);
      }
    } else {
      console.warn("Retorno da API Shopify Direct:", result);
      alert(`Informação da Shopify API:\n${result.error || 'Não foi possível gravar online.'}\n\n(Dica: certifique-se de configurar a variável de ambiente SHOPIFY_${currentStore.toUpperCase()}_TOKEN no painel da Vercel).`);
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<span>⚡ Salvar Direto</span>`;
      }
    }
  } catch (netErr) {
    console.warn("Execução offline / erro de rede:", netErr);
    alert(`⚠️ Atenção: Não foi possível conectar ao endpoint /api/shopify_direct (${netErr.message}).\n\nO produto NÃO foi alterado na Shopify online.\n\nAlternativas seguras:\n1. Clique em 'Copiar HTML' e cole diretamente no Admin da Shopify.\n2. Baixe o CSV do produto ou da loja para importação em lote no Shopify Admin.`);
    showToast(`⚠️ Gravação online indisponível no momento. Use 'Copiar HTML' ou 'CSV'.`);
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>⚡ Salvar Direto</span>`;
    }
  }
}

// Injetor de Mídias do BRK Bunker
const bunkerBulkInput = document.getElementById("bunker-bulk-input");
if (bunkerBulkInput) {
  bunkerBulkInput.oninput = (e) => {
    const text = e.target.value;
    const matches = text.match(/https?:\/\/[^\s,;"'<>]+/g) || [];
    if (matches[0]) document.getElementById("bunker-slot-1").value = matches[0];
    if (matches[1]) document.getElementById("bunker-slot-2").value = matches[1];
    if (matches[2]) document.getElementById("bunker-slot-3").value = matches[2];
  };
}

function applyBunkerLinksToModal() {
  if (!currentModalProduct) return;
  const u1 = document.getElementById("bunker-slot-1").value.trim();
  const u2 = document.getElementById("bunker-slot-2").value.trim();
  const u3 = document.getElementById("bunker-slot-3").value.trim();

  const bunkerUrls = [u1, u2, u3].filter(u => u.length > 0);
  if (bunkerUrls.length === 0) {
    alert("Por favor, cole ao menos uma URL válida do BRK Bunker.");
    return;
  }

  const origList = currentModalProduct.cdn_images || [];
  const candidateImgs = [
    bunkerUrls[0] || origList[0] || "",
    bunkerUrls[1] || origList[1] || "",
    bunkerUrls[2] || origList[2] || ""
  ].filter(Boolean);

  const seenB = new Set();
  const finalImgs = [];
  candidateImgs.forEach(u => {
    const root = u.split("?")[0].toLowerCase();
    if (!seenB.has(root)) {
      seenB.add(root);
      finalImgs.push(u);
    }
  });

  currentModalProduct.cdn_images = finalImgs;
  // Recalcular HTML com as novas imagens
  currentModalProduct.mode_b_html = getProductModeBHTML(currentModalProduct);
  updateModalView();

  const thumbsContainer = document.getElementById("modal-gallery-thumbs");
  if (thumbsContainer) {
    thumbsContainer.innerHTML = "";
    finalImgs.forEach((url, idx) => {
      const thumb = document.createElement("img");
      thumb.src = url;
      thumb.alt = "Bunker " + (idx + 1);
      thumb.className = "w-8 h-8 object-cover rounded-lg border-2 border-indigo-400 shadow-sm cursor-pointer hover:scale-110 transition-all";
      thumb.onclick = () => window.open(url, "_blank");
      thumbsContainer.appendChild(thumb);
    });
    const cBadge = document.getElementById("modal-photos-count-badge");
    if (cBadge) {
      cBadge.innerText = finalImgs.length + " Foto(s) do Bunker";
      cBadge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700";
    }
  }

  showToast("Fotos do Bunker aplicadas com sucesso sem repetição!");
}

// Cópia em Markdown com Feedback Reativo
function copyCurrentModalMarkdown(btnTrigger) {
  if (!currentModalProduct) return;
  const p = currentModalProduct;
  const mdText = p.mode_b_markdown || buildClientModeBMarkdown(p);
  if (!mdText) {
    showToast("⚠️ Nenhum texto Markdown disponível.");
    return;
  }

  navigator.clipboard.writeText(mdText).then(() => {
    showToast("Markdown copiado com sucesso! Pronto para documentação ou Shopify.");

    const buttons = [
      btnTrigger,
      document.getElementById("modal-copy-markdown-btn"),
      document.getElementById("modal-footer-copy-md-btn")
    ].filter(Boolean);

    buttons.forEach(btn => {
      const label = btn.querySelector(".copy-label");
      const icon = btn.querySelector(".copy-icon");
      if (!label) return;

      const origText = label.innerText;
      const origIcon = icon ? icon.innerText : "📝";

      label.innerText = "Copiado! ✓";
      if (icon) icon.innerText = "✅";
      btn.classList.add("ring-4", "ring-emerald-400/40", "scale-105");

      setTimeout(() => {
        label.innerText = origText;
        if (icon) icon.innerText = origIcon;
        btn.classList.remove("ring-4", "ring-emerald-400/40", "scale-105");
      }, 2200);
    });
  }).catch(err => {
    console.error("Erro ao copiar markdown:", err);
    showToast("⚠️ Erro ao copiar Markdown.");
  });
}

// Cópia em HTML com Feedback Reativo
function copyCurrentModalHTML(btnTrigger) {
  const sourceElem = document.getElementById("modal-source-code");
  const text = sourceElem ? sourceElem.textContent : "";
  if (!text) {
    showToast("⚠️ Nenhum código HTML encontrado para copiar.");
    return;
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast("HTML copiado com sucesso! Pronto para colar no Shopify.");

    const buttons = [
      btnTrigger,
      document.getElementById("modal-header-copy-btn"),
      document.getElementById("modal-footer-copy-btn")
    ].filter(Boolean);

    buttons.forEach(btn => {
      const label = btn.querySelector(".copy-label");
      const icon = btn.querySelector(".copy-icon");
      if (!label) return;

      const origText = label.innerText;
      const origIcon = icon ? icon.innerText : "📋";

      label.innerText = "Copiado! ✓";
      if (icon) icon.innerText = "✅";
      btn.classList.add("ring-4", "ring-emerald-400/40", "scale-105");

      setTimeout(() => {
        label.innerText = origText;
        if (icon) icon.innerText = origIcon;
        btn.classList.remove("ring-4", "ring-emerald-400/40", "scale-105");
      }, 2200);
    });
  }).catch(err => {
    console.error("Erro ao copiar:", err);
    showToast("⚠️ Erro ao copiar.");
  });
}

// Baixar CSV Individual Shopify
function downloadCurrentProductCSV() {
  if (!currentModalProduct) return;
  const html = document.getElementById("modal-source-code").textContent;
  const row = [
    "Handle,Title,Body (HTML)",
    `"${currentModalProduct.handle}","${currentModalProduct.title.replace(/"/g, '""')}","${html.replace(/"/g, '""')}"`
  ].join("\n");

  const blob = new Blob(["\uFEFF" + row], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `shopify_${currentModalProduct.handle}_desc_${currentModalMode}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  showToast("Planilha CSV individual baixada com sucesso!");
}

// Helpers de Geração Dinâmica de Markdown e HTML no Cliente
function resolveClientOriginAndTitle(liveP) {
  const KNOWN_BRANDS = [
    'Rapala', 'Deyu', 'Marine Sports', 'Marine', 'Daisen', 'Albatroz', 
    'Boaonda', 'American Hat', 'Elber', 'Maruri', 'Daiwa', 'Shimano', 
    'Loomis', 'Monster 3X', 'Moriah', 'Kowalsky', 'VMC', 'Mustad', 
    'Crown', 'Ottoni', 'Pesca Brasil', 'Sumax', 'Saint', 'Jogá', 'Joga'
  ];
  const rawTitle = (liveP.title || "Produto BRK").trim();
  const vendor = (liveP.vendor || "").trim();
  const tags = Array.isArray(liveP.tags) ? liveP.tags.join(" ") : (liveP.tags || "");
  const fullInfo = `${rawTitle} ${vendor} ${tags}`.toLowerCase();

  let detectedBrand = null;
  for (const b of KNOWN_BRANDS) {
    const bLower = b.toLowerCase();
    if (new RegExp('\\b' + bLower + '\\b', 'i').test(fullInfo)) {
      detectedBrand = b;
      break;
    }
  }

  const isRevenda = detectedBrand !== null && detectedBrand.toLowerCase() !== "brk";
  let formattedTitle = rawTitle;
  let brandName = "BRK";
  let originType = "producao_propria";

  if (isRevenda) {
    originType = "revenda";
    brandName = detectedBrand;
    if (!new RegExp('\\b' + brandName + '\\b', 'i').test(formattedTitle)) {
      formattedTitle = `${formattedTitle} - ${brandName}`;
    }
  } else {
    originType = "producao_propria";
    brandName = "BRK";
    if (!/\b(BRK|ArmorX)\b/i.test(formattedTitle)) {
      formattedTitle = `BRK ${formattedTitle}`;
    }
  }

  const masterSku = (liveP.master_sku || liveP.sku || "").toUpperCase().trim();
  const varSkus = (liveP.variants_skus || []).map(v => String(v).toUpperCase().trim());
  const handleStr = (liveP.handle || "").toUpperCase().trim();
  const isC0 = masterSku.startsWith("C0") || varSkus.some(v => v.startsWith("C0")) || handleStr.startsWith("C0") || String(liveP.tags || "").toUpperCase().includes("C0");
  const isShirt = anyShirtWord(rawTitle);
  const showCopyright = (originType === "producao_propria") && isShirt && isC0;

  return { formattedTitle, brandName, originType, showCopyright };
}

function anyShirtWord(text) {
  const t = (text || "").toLowerCase();
  return t.includes("camisa") || t.includes("camiseta") || t.includes("jersey") || t.includes("baby look") || t.includes("regata") || t.includes("polo");
}

function buildClientModeBMarkdown(liveP) {
  const originInfo = resolveClientOriginAndTitle(liveP);
  const formattedTitle = originInfo.formattedTitle;
  const brandName = originInfo.brandName;
  const originType = originInfo.originType;
  const showCopyright = originInfo.showCopyright;
  const rawImgs = (liveP.cdn_images && liveP.cdn_images.length > 0)
    ? liveP.cdn_images
    : (liveP.gallery && liveP.gallery.length > 0)
      ? liveP.gallery
      : ((liveP.images || []).map(img => img.src || img));
  const images = [...new Set(rawImgs.filter(u => typeof u === "string" && u.trim().length > 0))];
  const img1 = images[0] || "";

  const lines = [];
  lines.push(`# ${formattedTitle}\n`);
  if (originType === "revenda") {
    lines.push(`> **PRODUTO ORIGINAL • MARCA ${brandName.toUpperCase()}**\n`);
  } else {
    lines.push(`> **PRODUTO ORIGINAL**\n`);
  }

  lines.push(`### Performance & Conforto`);
  if (img1) lines.push(`![${formattedTitle}](${img1})\n`);
  lines.push(`Desenvolvido para oferecer máxima durabilidade e conforto térmico, o(a) ${formattedTitle} garante total liberdade de movimentos e proteção contínua.\n`);

  if (liveP.specs && liveP.specs.length > 0) {
    lines.push(`### Ficha Técnica & Especificações`);
    lines.push(`| Característica | Especificação |`);
    lines.push(`| :--- | :--- |`);
    liveP.specs.forEach(s => {
      lines.push(`| **${s.label}** | ${s.value} |`);
    });
    lines.push(``);
  }

  lines.push(`### Guia de Cuidados & Conservação`);
  lines.push(`Lavar à mão ou em ciclo suave com sabão neutro. Secar à sombra (dispensa uso de ferro).\n`);

  lines.push(`---`);
  lines.push(`- **Qualidade Oficial BRK:** Matérias-primas nobres testadas`);
  lines.push(`- **Envio Rápido & Seguro:** Rastreamento de ponta a ponta`);
  lines.push(`- **Troca Descomplicada:** Satisfação garantida ou seu dinheiro de volta`);

  if (showCopyright) {
    lines.push(`\n> **Aviso de Propriedade Intelectual:** Nossas estampas são protegidas pela Lei de Direitos Autorais (Lei 9.610/98) a Reprodução não autorizada está sujeita às penalidades legais. Copiar é crime !\n`);
  }

  return lines.join("\n");
}

// Quick Badges por ARQUÉTIPO (espelho de core/html_builder.py::QUICK_BADGES_BY_ARCHETYPE).
// GERADO A PARTIR DO PYTHON - não editar à mão; o teste de paridade falha se divergir.
// REGRA DE OURO: o arquétipo decide os selos; palavras soltas do título (ex.: "pesca"
// em "Vara de Pesca") NUNCA ativam selos de outra categoria.
const QUICK_BADGES_BY_ARCHETYPE = {
  "uv_performance": [
    {
      "icon": "sun",
      "title": "FPU 50+ Certificado",
      "sub": "Bloqueia 98% Raios UV"
    },
    {
      "icon": "bolt",
      "title": "Tecnologia Dry Fit",
      "sub": "Secagem Ultra Rápida"
    },
    {
      "icon": "shield",
      "title": "Costura Reforçada",
      "sub": "Pesponto Duplo Anti-Atrito"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "agro_field": [
    {
      "icon": "care",
      "title": "Algodão Premium",
      "sub": "Toque Nobre Aveludado"
    },
    {
      "icon": "sparkle",
      "title": "Respirabilidade Natural",
      "sub": "Conforto no Campo"
    },
    {
      "icon": "shield",
      "title": "Costura Dupla Ombro",
      "sub": "Estrutura Anti-Deformação"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Procedência Garantida"
    }
  ],
  "motors_speed": [
    {
      "icon": "bolt",
      "title": "Ventilação Ativa",
      "sub": "Painéis Microperfurados"
    },
    {
      "icon": "gear",
      "title": "Aerodinâmica Pro",
      "sub": "Modelagem Anatômica"
    },
    {
      "icon": "shield",
      "title": "Costura Resistente",
      "sub": "Pronta para Off-Road"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Garantia Oficial BRK"
    }
  ],
  "shirts_button_work": [
    {
      "icon": "shield",
      "title": "Abotoamento Reforçado",
      "sub": "Botões com Costura em X"
    },
    {
      "icon": "box",
      "title": "Bolsos Utilitários",
      "sub": "Funcionais no Peito"
    },
    {
      "icon": "care",
      "title": "Colarinho Estruturado",
      "sub": "Postura o Dia Todo"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "pants_cargo_tactical": [
    {
      "icon": "shield",
      "title": "Ripstop Alta Tenacidade",
      "sub": "Resistente ao Atrito"
    },
    {
      "icon": "gear",
      "title": "Reforço Cavalo e Joelhos",
      "sub": "Modelagem Operacional"
    },
    {
      "icon": "box",
      "title": "Múltiplos Bolsos Cargo",
      "sub": "Compartimentação Prática"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "overalls_workwear": [
    {
      "icon": "shield",
      "title": "Costuras Duplas e Triplas",
      "sub": "Alta Tenacidade"
    },
    {
      "icon": "gear",
      "title": "Alças Reguláveis",
      "sub": "Engate Rápido"
    },
    {
      "icon": "box",
      "title": "Bolsos Reforçados",
      "sub": "Frontais, Laterais e Traseiros"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "sun_sleeves_manguitos": [
    {
      "icon": "sun",
      "title": "FPU 50+ Permanente",
      "sub": "Proteção Solar Certificada"
    },
    {
      "icon": "bolt",
      "title": "Tecnologia Dry Fit",
      "sub": "Evaporação do Suor"
    },
    {
      "icon": "shield",
      "title": "Silicone no Bíceps",
      "sub": "Fixação Antiderrapante"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "neck_gaiters_balaclavas": [
    {
      "icon": "sun",
      "title": "FPU 50+ Permanente",
      "sub": "Bloqueador de Radiação"
    },
    {
      "icon": "shield",
      "title": "Tubular Seamless",
      "sub": "Sem Costuras Anti-Atrito"
    },
    {
      "icon": "bolt",
      "title": "Elasticidade 4-Way",
      "sub": "Memória de Forma"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "gloves_tactical_fishing": [
    {
      "icon": "shield",
      "title": "Palma Antiderrapante",
      "sub": "Material Texturizado"
    },
    {
      "icon": "bolt",
      "title": "Dorso Respirável",
      "sub": "Secagem Ultra Rápida"
    },
    {
      "icon": "gear",
      "title": "Ajuste no Punho",
      "sub": "Fita Regulável"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "hats_safari_outdoor": [
    {
      "icon": "sun",
      "title": "Proteção Solar FPU 50+",
      "sub": "Barreira UV Térmica"
    },
    {
      "icon": "care",
      "title": "Tecido Respirável",
      "sub": "Ilhoses de Respiração"
    },
    {
      "icon": "shield",
      "title": "Ajuste Anatômico",
      "sub": "Segurança Anti-Vento"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação Garantida"
    }
  ],
  "hats_country_cowboy": [
    {
      "icon": "shield",
      "title": "Copa Estruturada",
      "sub": "Aba com Retenção de Formato"
    },
    {
      "icon": "sparkle",
      "title": "Bandinha em Couro",
      "sub": "Fivela Metálica"
    },
    {
      "icon": "care",
      "title": "Carneira Acolchoada",
      "sub": "Encaixe Macio e Estável"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "caps_trucker_snapback": [
    {
      "icon": "care",
      "title": "Tela Respirável",
      "sub": "Lateral e Traseira"
    },
    {
      "icon": "shield",
      "title": "Aba Curva Reforçada",
      "sub": "6 Costuras de Reforço"
    },
    {
      "icon": "gear",
      "title": "Fecho Snapback",
      "sub": "Tamanho Único Ajustável"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Satisfação 100% Garantida"
    }
  ],
  "eyewear_sunglasses": [
    {
      "icon": "sun",
      "title": "Lentes Polarizadas",
      "sub": "Filtro Anti-Reflexo"
    },
    {
      "icon": "shield",
      "title": "Proteção UV400",
      "sub": "Bloqueio UVA e UVB"
    },
    {
      "icon": "care",
      "title": "Armação Ultraleve",
      "sub": "Apoio Nasal Anatômico"
    },
    {
      "icon": "sparkle",
      "title": "Estojo Incluso",
      "sub": "Com Flanela de Microfibra"
    }
  ],
  "footwear_sandals_boaonda": [
    {
      "icon": "shoe",
      "title": "Palmilha Antiestresse",
      "sub": "Amortecimento Anatômico"
    },
    {
      "icon": "shield",
      "title": "Solado Antiderrapante",
      "sub": "Aderência em Solo Molhado"
    },
    {
      "icon": "care",
      "title": "Fácil Higienização",
      "sub": "Material Antibacteriano"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Ajuste Perfeito Garantido"
    }
  ],
  "closed_footwear_sneakers": [
    {
      "icon": "shoe",
      "title": "Palmilha Anatômica",
      "sub": "Espuma de Alta Densidade"
    },
    {
      "icon": "shield",
      "title": "Solado Antiderrapante",
      "sub": "Borracha de Alta Tração"
    },
    {
      "icon": "care",
      "title": "Cabedal Respirável",
      "sub": "Reforços Laterais"
    },
    {
      "icon": "return",
      "title": "Troca Fácil BRK",
      "sub": "Ajuste Perfeito Garantido"
    }
  ],
  "fishing_tackle_gear": [
    {
      "icon": "fish",
      "title": "Sensibilidade & Precisão",
      "sub": "Resposta Rápida ao Toque"
    },
    {
      "icon": "shield",
      "title": "Estrutura Reforçada",
      "sub": "Feita para Brigas Pesadas"
    },
    {
      "icon": "gear",
      "title": "Tratamento Anti-Corrosão",
      "sub": "Água Doce e Salgada"
    },
    {
      "icon": "sparkle",
      "title": "100% Original",
      "sub": "Procedência e Garantia"
    }
  ],
  "fishing_lures": [
    {
      "icon": "fish",
      "title": "Ação & Nado Realista",
      "sub": "Atratividade para Predadores"
    },
    {
      "icon": "shield",
      "title": "Pitões Reforçados",
      "sub": "Componentes em Aço Inox"
    },
    {
      "icon": "gear",
      "title": "Equilíbrio Hidrodinâmico",
      "sub": "Arremessos Precisos"
    },
    {
      "icon": "sparkle",
      "title": "Garantia de Procedência",
      "sub": "100% Original e Testado"
    }
  ],
  "tackle_boxes_storage": [
    {
      "icon": "box",
      "title": "Polipropileno Anti-Impacto",
      "sub": "Proteção UV"
    },
    {
      "icon": "shield",
      "title": "Travas de Alta Pressão",
      "sub": "Sistema Duplo Reforçado"
    },
    {
      "icon": "gear",
      "title": "Divisórias Removíveis",
      "sub": "Reposicionáveis sob Medida"
    },
    {
      "icon": "care",
      "title": "Vedação Anti-Respingos",
      "sub": "Contra Água e Poeira"
    }
  ],
  "drinkware_thermo": [
    {
      "icon": "shield",
      "title": "Inox 18/8 com Vácuo",
      "sub": "Parede Dupla Térmica"
    },
    {
      "icon": "bolt",
      "title": "Máximo Isolamento",
      "sub": "Bebida Gelada por Horas"
    },
    {
      "icon": "care",
      "title": "Livre de BPA",
      "sub": "Sem Condensação Externa"
    },
    {
      "icon": "return",
      "title": "Garantia BRK",
      "sub": "Qualidade Assegurada"
    }
  ],
  "cutlery_unique": [
    {
      "icon": "knife",
      "title": "Aço Especial Nobre",
      "sub": "Alta Retenção de Fio"
    },
    {
      "icon": "gear",
      "title": "Tratamento Térmico",
      "sub": "Dureza e Tenacidade"
    },
    {
      "icon": "shield",
      "title": "Acabamento Artesanal",
      "sub": "Cabo Anatômico Nobre"
    },
    {
      "icon": "sparkle",
      "title": "Garantia BRK",
      "sub": "Procedência Garantida"
    }
  ],
  "accessories_car_care": [
    {
      "icon": "sparkle",
      "title": "Fragrância Contínua",
      "sub": "Liberação Gradual"
    },
    {
      "icon": "care",
      "title": "Longa Duração",
      "sub": "Até 30 a 45 Dias"
    },
    {
      "icon": "gear",
      "title": "Fixação Prática",
      "sub": "Retrovisor ou Grade de Ar"
    },
    {
      "icon": "return",
      "title": "Troca Descomplicada",
      "sub": "Satisfação Garantida"
    }
  ],
  "accessories_general": [
    {
      "icon": "shield",
      "title": "Resistente à Água",
      "sub": "E à Exposição Solar"
    },
    {
      "icon": "care",
      "title": "Material Reforçado",
      "sub": "Alta Resistência"
    },
    {
      "icon": "sparkle",
      "title": "Item Original BRK",
      "sub": "Colecionável Oficial"
    },
    {
      "icon": "return",
      "title": "Troca Descomplicada",
      "sub": "Satisfação Garantida"
    }
  ],
  "books_publications": [
    {
      "icon": "sparkle",
      "title": "Impressão em Alta Definição",
      "sub": "Ilustrações Detalhadas"
    },
    {
      "icon": "care",
      "title": "Capa Colorida Laminada",
      "sub": "Papel Resistente"
    },
    {
      "icon": "box",
      "title": "Ideal para Presentear",
      "sub": "Para Todas as Idades"
    },
    {
      "icon": "truck",
      "title": "Envio Rápido & Seguro",
      "sub": "Rastreamento Completo"
    }
  ]
};

function buildClientQuickBadges(themeColor, themeBg, archetypeId, liveP) {
  const badges = QUICK_BADGES_BY_ARCHETYPE[archetypeId] || [
    { icon: "shield", title: "Qualidade Oficial", sub: "Matéria-Prima Selecionada" },
    { icon: "sparkle", title: "Acabamento Premium", sub: "Rigoroso Padrão BRK" },
    { icon: "truck", title: "Envio Rápido & Seguro", sub: "Rastreamento Completo" },
    { icon: "return", title: "Troca Descomplicada", sub: "Satisfação Garantida" }
  ];

  const itemsHtml = badges.map(b => `    <div class="brk-badge-item">
      <span class="brk-badge-icon">${getSvgIcon(b.icon, themeColor, 18)}</span>
      <div class="brk-badge-content">
        <strong class="brk-badge-title">${b.title}</strong>
        <span class="brk-badge-sub">${b.sub}</span>
      </div>
    </div>`).join("\n");

  return `  <!-- Selos Rapidos de Confianca e Tecnologia (Destaque Superior) -->
  <div class="brk-quick-badges">
${itemsHtml}
  </div>`;
}

function buildClientSizeGuide(themeColor, themeBg, archetypeId, isKids, isShortSleeve, liveP) {
  const tLow = (liveP.formatted_title || liveP.title || "").toLowerCase();
  const skuLow = (liveP.sku || liveP.master_sku || "").toLowerCase();

  // 0. Exclusão estrita de itens não-têxteis com UV ou termos ambíguos
  const nonTextiles = ["óculos", "oculos", "faca", "facas", "canivete", "alicate", "vara", "varas", "molinete", "carretilha", "isca", "iscas", "linha", "linhas", "anzol", "anzois", "estojo", "garrafa", "copo", "chaveiro", "adesivo", "carteira", "protetor solar"];
  if (nonTextiles.some(w => tLow.includes(w))) {
    return "";
  }

  let guideTitle = "";
  let tableHtml = "";

  // 1. Identificar se o produto é comprovadamente de vestuário superior / camisa
  const isShirt = (
    ["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archetypeId) ||
    /camisa|camiseta|jersey|baby look|babylook/i.test(tLow) ||
    /^(c0|ci|cadv|adv|hyb|cmb|raglan)/i.test(skuLow)
  ) && !/calça|calca|bermuda|shorts|macacão|macacao|jeans|sandália|sandalia|babuche|chinelo|sapato|tênis|tenis|bota|botina|boaonda|chapéu|chapeu|boné|bone|luva|manguito|bandana|tubeneck|buff|balaclava/i.test(tLow);

  let tipText = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura do ombro à barra | Manga do ombro ao punho). Dica: compare com uma peça sua estendida para escolher o caimento ideal.";

  if (isShirt) {
    // 1.1 Camisas de Botão / Utilitárias Work (CMB - Sarja/Algodão corte reto de trabalho)
    if (archetypeId === "shirts_button_work" || skuLow.includes("cmb") || (tLow.includes("work") && tLow.includes("camisa") && !tLow.includes("xtech") && !tLow.includes("dry"))) {
      guideTitle = "Tabela de Medidas - Camisas Work & Utilitárias de Botão (P ao G2)";
      tipText = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Comprimento da gola à barra | Manga). Modelagem confortável de trabalho.";
      const mHeader = isShortSleeve ? "Manga Curta" : "Manga Longa";
      const rows = [
        ["P", "102 cm", "68 cm", isShortSleeve ? "22 cm" : "75 cm"],
        ["M", "108 cm", "71 cm", isShortSleeve ? "23 cm" : "77 cm"],
        ["G", "114 cm", "74 cm", isShortSleeve ? "24 cm" : "79 cm"],
        ["GG", "120 cm", "77 cm", isShortSleeve ? "25 cm" : "81 cm"],
        ["XG", "126 cm", "80 cm", isShortSleeve ? "26 cm" : "83 cm"],
        ["EXG (G1)", "132 cm", "83 cm", isShortSleeve ? "27 cm" : "85 cm"],
        ["G2", "138 cm", "85 cm", isShortSleeve ? "28 cm" : "87 cm"],
      ];
      tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Tórax / Circunferência</th><th>Comprimento Total</th><th>${mHeader}</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
    }
    // 1.2 Camisas UV C0 Infantil (1 a 13 Anos)
    else if (isKids || /infantil|kids|juvenil|criança|crianca/i.test(tLow) || /kids|inf/i.test(skuLow)) {
      guideTitle = "Guia de Tamanhos Infantil (1 a 13 Anos)";
      const badgeTitle = "INFANTIL";
      const subtitle = "Camisa Manga Longa UV50 | *As medidas podem variar de 2cm a 3cm";
      const rows = [
        ["1 a 2 Anos (PP)", "31 cm", "41 cm", "31 cm"],
        ["2 a 3 Anos (P)", "33 cm", "45 cm", "35 cm"],
        ["4 a 5 Anos (M)", "35 cm", "49 cm", "37 cm"],
        ["6 a 7 Anos (G)", "38 cm", "52 cm", "39 cm"],
        ["8 a 9 Anos (GG)", "39 cm", "55 cm", "42 cm"],
        ["10 a 11 Anos (G1)", "41 cm", "58 cm", "44 cm"],
        ["12 a 13 Anos (G2)", "43 cm", "61 cm", "45 cm"],
      ];
      tableHtml = `<div class="brk-sg-card-header"><div class="brk-sg-card-title">${badgeTitle}</div><div class="brk-sg-subtitle">${subtitle}</div></div><table class="brk-sg-table"><thead><tr class="brk-sg-th-row"><th>TAMANHO</th><th>TÓRAX</th><th>ALTURA</th><th>MANGA</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
    }
    // 1.3 Camisas UV C0 Feminina / Baby Look (PP ao G2)
    else if (/feminina|feminino|baby look|fem|babylook/i.test(tLow) || skuLow.includes("bl")) {
      guideTitle = "Tabela de Medidas Feminina - Baby Look (PP ao G2)";
      const badgeTitle = "FEMININO";
      const subtitle = "Camisa Manga Longa UV50 | *As medidas podem variar de 2cm a 3cm";
      const rows = [
        ["Baby Look PP", "33 cm", "51 cm", "53 cm"],
        ["Baby Look P", "37 cm", "54 cm", "55 cm"],
        ["Baby Look M", "43 cm", "57 cm", "59 cm"],
        ["Baby Look G", "47 cm", "60 cm", "60 cm"],
        ["Baby Look GG", "47 cm", "60 cm", "61 cm"],
        ["Baby Look G1", "50 cm", "62 cm", "61 cm"],
        ["Baby Look G2", "55 cm", "64 cm", "63 cm"],
      ];
      tableHtml = `<div class="brk-sg-card-header"><div class="brk-sg-card-title">${badgeTitle}</div><div class="brk-sg-subtitle">${subtitle}</div></div><table class="brk-sg-table"><thead><tr class="brk-sg-th-row"><th>TAMANHO</th><th>TÓRAX</th><th>ALTURA</th><th>MANGA</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
    }
    // 1.4 Camisas UV C0 Masculino / Unissex Padrão (PP ao G2)
    else {
      guideTitle = "Tabela de Medidas Masculino / Unissex (PP ao G2)";
      const badgeTitle = "MASCULINO";
      const subtitle = "Camisa Manga Longa UV50 | *As medidas podem variar de 2cm a 3cm";
      const rows = [
        ["PP", "49,5 cm", "67 cm", "56 cm"],
        ["P", "51,5 cm", "69 cm", "59,5 cm"],
        ["M", "54 cm", "71 cm", "62 cm"],
        ["G", "56 cm", "72 cm", "64 cm"],
        ["GG", "59 cm", "74 cm", "64 cm"],
        ["G1", "62 cm", "75 cm", "66 cm"],
        ["G2", "65 cm", "76,5 cm", "66 cm"],
      ];
      tableHtml = `<div class="brk-sg-card-header"><div class="brk-sg-card-title">${badgeTitle}</div><div class="brk-sg-subtitle">${subtitle}</div></div><table class="brk-sg-table"><thead><tr class="brk-sg-th-row"><th>TAMANHO</th><th>TÓRAX</th><th>ALTURA</th><th>MANGA</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
    }
  }
  else if (["pants_cargo_tactical", "overalls_workwear"].includes(archetypeId) || /calça|calca|bermuda|shorts|macacão|macacao|jeans/i.test(tLow)) {
    guideTitle = "Tabela de Medidas - Calças & Bermudas (38 ao 52)";
    tipText = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Cintura na altura do cós | Quadril na parte mais larga | Comprimento da cintura até a barra). Dica: compare com uma peça sua estendida.";
    const rows = [
      ["38", "78 - 82 cm", "98 cm", "104 cm"],
      ["40", "82 - 86 cm", "102 cm", "105 cm"],
      ["42", "86 - 90 cm", "106 cm", "106 cm"],
      ["44", "90 - 94 cm", "110 cm", "107 cm"],
      ["46", "94 - 98 cm", "114 cm", "108 cm"],
      ["48", "98 - 102 cm", "118 cm", "109 cm"],
      ["50", "102 - 106 cm", "122 cm", "110 cm"],
      ["52", "106 - 110 cm", "126 cm", "111 cm"],
    ];
    tableHtml = `<table class="brk-sg-table"><thead><tr><th>Numeração</th><th>Cintura</th><th>Quadril</th><th>Comprimento</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
  } else if (["hats_safari_outdoor", "caps_trucker_snapback"].includes(archetypeId) || /chapéu|chapeu|boné|bone/i.test(tLow)) {
    guideTitle = "Guia de Dimensões - Chapéus & Bonés";
    tipText = "<strong>Como medir com precisão:</strong> Passe uma fita métrica ao redor da cabeça, cerca de 1 dedo acima das orelhas e sobrancelhas.";
    tableHtml = `<table class="brk-sg-table"><thead><tr><th>Modelo</th><th>Circunferência da Cabeça</th><th>Aba / Profundidade</th><th>Regulagem & Ajuste</th></tr></thead><tbody><tr><td><strong>Chapéu Safári / Australiano</strong></td><td>56 cm a 60 cm (Veste P ao GG)</td><td>Aba 7,5 cm de proteção 360°</td><td>Cordão jugular com trava anti-vento</td></tr><tr><td><strong>Boné Trucker / Snapback</strong></td><td>54 cm a 61 cm (Ajustável)</td><td>Aba 7,0 cm estruturada curvada</td><td>Fecho regulador traseiro de alta pressão</td></tr></tbody></table>`;
  } else if (["footwear_sandals_boaonda", "closed_footwear_sneakers", "calcados_botinas"].includes(archetypeId) || /sandália|sandalia|babuche|chinelo|sapato|tênis|tenis|bota|botina|boaonda/i.test(tLow)) {
    guideTitle = "Guia de Tamanhos de Calçados (Medida da Palmilha)";
    tipText = "<strong>Como medir com precisão:</strong> Meça a palmilha interna de um calçado confortável do calcanhar até a ponta do dedão para escolher a numeração perfeita.";
    const rows = [
      ["34", "23,0 cm"], ["35", "23,7 cm"], ["36", "24,3 cm"],
      ["37", "25,0 cm"], ["38", "25,7 cm"], ["39", "26,3 cm"],
      ["40", "27,0 cm"], ["41", "27,7 cm"], ["42", "28,3 cm"],
      ["43", "29,0 cm"], ["44", "29,7 cm"], ["45", "30,3 cm"]
    ];
    tableHtml = `<table class="brk-sg-table"><thead><tr><th>Numeração BR</th><th>Comprimento da Palmilha (cm)</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td></tr>`).join("")}</tbody></table>`;
  } else if (archetypeId === "gloves_tactical_fishing" || tLow.includes("luva")) {
    guideTitle = "Tabela de Medidas de Luvas (Largura da Palma)";
    tipText = "<strong>Como medir com precisão:</strong> Meça a largura da palma da mão na parte mais larga (logo abaixo das articulações dos dedos).";
    const rows = [
      ["P", "8,0 a 8,5 cm", "19 cm"],
      ["M", "8,5 a 9,0 cm", "20 cm"],
      ["G", "9,0 a 9,5 cm", "21 cm"],
      ["GG", "9,5 a 10,5 cm", "22 cm"]
    ];
    tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Largura da Palma</th><th>Comprimento da Mão</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join("")}</tbody></table>`;
  } else if (archetypeId === "sun_sleeves_manguitos" || tLow.includes("manguito")) {
    guideTitle = "Tabela de Medidas - Manguitos de Proteção Solar";
    tipText = "<strong>Como medir com precisão:</strong> Meça a circunferência do bíceps e punho com o braço em repouso.";
    const rows = [
      ["P / M", "24 a 30 cm", "16 a 20 cm", "45 cm"],
      ["G / GG", "30 a 38 cm", "18 a 24 cm", "48 cm"]
    ];
    tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Circunferência Bíceps</th><th>Circunferência Punho</th><th>Comprimento Total</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
  } else if (archetypeId === "neck_gaiters_balaclavas" || /bandana|tubeneck|buff|balaclava/i.test(tLow)) {
    guideTitle = "Dimensões - Bandana Tubular Seamless Multifuncional";
    tipText = "<strong>Dimensões do produto:</strong> Microfibra tubular seamless de alta elasticidade com proteção UV50+ e memória anatômica.";
    tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Largura (Plana)</th><th>Comprimento</th><th>Elasticidade</th></tr></thead><tbody><tr><td><strong>Tamanho Único</strong></td><td>Aprox. 24 cm</td><td>Aprox. 48 cm</td><td>Microfibra tubular elástica seamless com memória anatômica</td></tr></tbody></table>`;
  } else {
    return "";
  }

  return `  <!-- Tabela de Medidas Inteligente Integrada (Accordion Nativo) -->
  <details class="brk-size-guide">
    <summary class="brk-sg-summary">
      <span class="brk-sg-title-wrap">
        <span class="brk-sg-icon">${getSvgIcon('ruler', themeColor, 18)}</span>
        <strong class="brk-sg-heading">${guideTitle}</strong>
      </span>
      <span class="brk-sg-trigger">Ver Medidas em cm ▾</span>
    </summary>
    <div class="brk-sg-body">
      <div class="brk-sg-tip">
        <span>📏</span>
        <span>${tipText}</span>
      </div>
      ${tableHtml}
    </div>
  </details>`;
}

// Versao do padrao Modo B (espelha core/html_builder.py::MODO_B_VERSION; teste de paridade garante).
const MODO_B_VERSION = "1";

function buildClientTrackingMarker(sku, archetypeId) {
  const clean = (v) => String(v || "").replace(/[^A-Za-z0-9_.\-]/g, "").slice(0, 60).replace(/--/g, "-");
  return `<!-- BRK-MODO-B v${MODO_B_VERSION} | sku:${clean(sku)} | molde:${clean(archetypeId)} -->`;
}

function buildClientSchemaJsonLd(liveP) {
  const originInfo = resolveClientOriginAndTitle(liveP);
  const formattedTitle = liveP.formatted_title || originInfo.formattedTitle;
  const brandName = liveP.brand_name || originInfo.brandName;
  const sku = liveP.master_sku || liveP.sku || liveP.id || "";
  const price = liveP.price || (liveP.variants && liveP.variants[0] && liveP.variants[0].price) || "0.00";

  const rawImgs = (liveP.cdn_images && liveP.cdn_images.length > 0)
    ? liveP.cdn_images
    : (liveP.gallery && liveP.gallery.length > 0)
      ? liveP.gallery
      : ((liveP.images || []).map(img => (typeof img === "object" ? img.src : img)));
  const images = [...new Set(rawImgs.filter(u => typeof u === "string" && u.startsWith("http")))].slice(0, 3);

  const schemaObj = {
    "@context": "https://schema.org/",
    "@type": "Product",
    "name": formattedTitle,
    "description": `${formattedTitle} oficial com garantia e qualidade oficial BRK.`,
    "sku": String(sku),
    "brand": {
      "@type": "Brand",
      "name": brandName
    },
    "offers": {
      "@type": "Offer",
      "priceCurrency": "BRL",
      "price": String(price),
      "availability": "https://schema.org/InStock",
      "itemCondition": "https://schema.org/NewCondition"
    }
  };
  if (images.length > 0) {
    schemaObj["image"] = images;
  }

  return `  <!-- Schema.org Microdata JSON-LD para Google Search & Merchant Center -->
  <script type="application/ld+json">
${JSON.stringify(schemaObj, null, 2)}
  </script>`;
}

function getProductModeBHTML(liveP) {
  if (!liveP) return "";
  const originInfo = resolveClientOriginAndTitle(liveP);
  const formattedTitle = liveP.formatted_title || originInfo.formattedTitle;
  const brandName = liveP.brand_name || originInfo.brandName;
  const originType = liveP.origin_type || originInfo.originType;
  const showCopyright = (liveP.show_copyright !== undefined) ? liveP.show_copyright : originInfo.showCopyright;

  const themeColor = liveP.theme_color || (liveP.store_key === "brk_agro" ? "#16a34a" : liveP.store_key === "brk_motors" ? "#f97316" : "#0284c7");
  const themeBg = liveP.theme_bg || (liveP.store_key === "brk_agro" ? "#f0fdf4" : liveP.store_key === "brk_motors" ? "#fff7ed" : "#f0f9ff");

  // Coleta oficial e desduplicação estrita de fotos da galeria da Shopify
  const rawSources = (liveP.cdn_images && liveP.cdn_images.length > 0)
    ? liveP.cdn_images
    : (liveP.gallery && liveP.gallery.length > 0)
      ? liveP.gallery
      : ((liveP.images || []).map(img => (typeof img === "object" ? img.src : img)));

  const seenRoots = new Set();
  const images = [];
  rawSources.forEach(u => {
    if (!u || typeof u !== "string") return;
    const cleanU = u.trim();
    if (!cleanU) return;
    const root = cleanU.split("?")[0].toLowerCase();
    if (!seenRoots.has(root)) {
      seenRoots.add(root);
      images.push(cleanU);
    }
  });

  const isLure = (liveP.archetype_id === "fishing_lures") || /isca|plug|popper|stick|crankbait|minnow|frog|soft/i.test(liveP.title || "");
  const hasMultipleVariations = liveP.has_multiple_variations || (isLure && (images.length >= 2 || (liveP.variants && liveP.variants.length > 1)));
  let splitImages = liveP.split_images || null;
  if (!splitImages && hasMultipleVariations && images.length >= 2) {
    splitImages = [images[0], images[1]];
  }
  let variationsSummary = liveP.variations_summary || "";
  if (!variationsSummary && hasMultipleVariations) {
    variationsSummary = "Múltiplas variações e opções de cores disponíveis para escolha no anúncio.";
  }

  // Atribuição de imagens exclusivas por ato - ZERO DUPLICAÇÃO
  let img1 = images[0] || "";
  let img2 = images[1] || "";
  let img3 = images[2] || "";

  if (hasMultipleVariations && images.length >= 2) {
    img2 = images[2] || "";
    img3 = images[3] || "";
  }

  let blocks = liveP.narrative_blocks;
  if (!blocks || blocks.length === 0) {
    const moldes = window.__STORE_MOLDES || {};
    let archKey = liveP.archetype_id;
    if (!archKey || archKey === "uv_performance") {
      if (typeof detectClientArchetype === "function") {
        archKey = detectClientArchetype(liveP.title, liveP.category, liveP.tags).id;
      }
    }
    const tmpl = moldes[archKey] || moldes["uv_performance"];

    if (tmpl && tmpl.act1 && tmpl.act2 && tmpl.act3) {
      const tLow = (liveP.title || "").toLowerCase();
      const isHooded = /\b(capuz|hood|hoodie)\b/i.test(tLow);
      const isKids = /\b(infantil|kids|juvenil|mini)\b/i.test(tLow) && !/\b(adulto|unissex adulto)\b/i.test(tLow);
      const isShortSleeve = /\b(manga curta|manga-curta)\b/i.test(tLow) && !/\b(manga longa|manga-longa)\b/i.test(tLow);
      const isRoundNeck = /\b(gola careca|gola redonda|sem zíper|sem ziper)\b/i.test(tLow) || (/\bcamiseta\b/i.test(tLow) && !/\b(ziper|zíper)\b/i.test(tLow));

      let act1Title = tmpl.act1.title || "QUALIDADE E DESEMPENHO";
      let act1Desc = (tmpl.act1.desc_tmpl || "").replace(/\{title\}/g, formattedTitle);
      let act2Title = tmpl.act2.title || "CONFORTO E TECNOLOGIA";
      let act2Desc = (tmpl.act2.desc_tmpl || "").replace(/\{title\}/g, formattedTitle);
      let act3Title = tmpl.act3.title || "DURABILIDADE E ACABAMENTO";
      let act3Desc = (tmpl.act3.desc_tmpl || "").replace(/\{title\}/g, formattedTitle);

      if (isKids) {
        act1Title = "CONFORTO E PROTEÇÃO SOLAR TOTAL PARA OS PEQUENOS AVENTUREIROS";
        act1Desc = `Desenvolvida especialmente para crianças e jovens exploradores, o(a) ${formattedTitle} oferece proteção solar máxima FPU 50+ com toque extra suave na pele, garantindo segurança e liberdade total para brincar ao ar livre.`;
        act2Title = "TECNOLOGIA DRY FIT QUE MANTÉM AS CRIANÇAS FRESCAS E SECAS";
        act2Desc = "Tecido respirável de secagem ultra rápida que evapora o suor rapidamente, mantendo o corpo seco durante todas as brincadeiras e pescarias em família.";
        if (!isHooded) {
          act3Title = "COSTURAS PLANAS ANTI-ATRITO E MÁXIMA DURABILIDADE";
          act3Desc = "Construída com acabamento elástico de alta resistência que não pinica nem irrita a pele sensível das crianças, oferecendo caimento confortável que aguenta todas as aventuras infantis.";
        }
      }

      if (isHooded) {
        act3Title = "CAPUZ ANATÔMICO INTEGRADO E COSTURA REFORÇADA";
        act3Desc = "Equipada com capuz anatômico integrado que oferece proteção solar 360° para nuca, orelhas e laterais do rosto contra o sol forte e vento, dispensando o uso de acessórios extras.";
      } else if (isShortSleeve) {
        act3Desc = act3Desc.replace(/punhos anatômicos[^,;.]*/gi, "mangas curtas com barra reforçada em costura dupla");
      } else if (isRoundNeck) {
        act3Title = "COSTURA REFORÇADA E GOLA REDONDA ANATÔMICA";
        act3Desc = "Acabamento de alto padrão com costuras planas anti-atrito, gola careca canelada que não deforma e ajuste confortável para uso contínuo.";
      }

      blocks = [
        {
          tag: isKids ? "Proteção Infantil & Conforto" : (tmpl.act1.tag || "Destaque"),
          title: act1Title,
          description: act1Desc,
          image: img1,
          split_images: splitImages,
          variations_summary: variationsSummary
        },
        {
          tag: isKids ? "Respirabilidade & Frescor" : (tmpl.act2.tag || "Destaque"),
          title: act2Title,
          description: act2Desc,
          image: img2
        },
        {
          tag: isHooded ? "Capuz Anatômico & Proteção 360°" : (tmpl.act3.tag || "Destaque"),
          title: act3Title,
          description: act3Desc,
          image: img3
        }
      ];
    } else {
      blocks = [
        {
          tag: "Performance & Conforto",
          title: "MODELAGEM ANATÔMICA E MÁXIMO CONFORTO",
          description: `Desenvolvido para oferecer máxima durabilidade e conforto térmico, o(a) ${formattedTitle} garante total liberdade de movimentos.`,
          image: img1,
          split_images: splitImages,
          variations_summary: variationsSummary
        },
        {
          tag: "Design & Identidade",
          title: "ACABAMENTO PREMIUM E IDENTIDADE VISUAL",
          description: `Design exclusivo e caimento equilibrado, unindo estilo marcante a matérias-primas de alta qualidade para qualquer ocasião.`,
          image: img2
        },
        {
          tag: "Durabilidade & Proteção",
          title: "ALTA RESISTÊNCIA E VIDA ÚTIL PROLONGADA",
          description: `Estrutura reforçada desenvolvida para suportar uso contínuo, mantendo suas propriedades originais mesmo após repetidas utilizações.`,
          image: img3
        }
      ];
    }
  }

  let specs = liveP.specs || [];
  if (specs.length === 0 && window.__STORE_MOLDES) {
    const archKey = liveP.archetype_id || "uv_performance";
    const tmpl = window.__STORE_MOLDES[archKey] || window.__STORE_MOLDES["uv_performance"];
    if (tmpl && tmpl.base_specs) {
      specs = tmpl.base_specs.map(s => ({ label: s.label, value: s.default }));
    }
  }

  let careTips = liveP.care_tips;
  if (!careTips && window.__STORE_MOLDES) {
    const archKey = liveP.archetype_id || "uv_performance";
    careTips = window.__STORE_MOLDES[archKey]?.care_tips;
  }
  if (!careTips) {
    careTips = "Lavar à mão ou em ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar).";
  }

  // 1. Cabeçalho de Origem e Título
  let originBadge = "";
  if (originType === "revenda") {
    originBadge = `<span class="brk-desc-origin-badge revenda">${getSvgIcon("sparkle", "#b45309", 12)} PRODUTO ORIGINAL • MARCA ${brandName.toUpperCase()}</span>`;
  } else {
    originBadge = `<span class="brk-desc-origin-badge propria">${getSvgIcon("shield", themeColor, 12)} PRODUTO ORIGINAL</span>`;
  }

  const headerHtml = `  <!-- Cabecalho Oficial com Origem e Marca -->
  <div class="brk-desc-header">
    ${originBadge}
    <h2 class="brk-desc-main-title">${formattedTitle}</h2>
  </div>`;

  const archetypeId = liveP.archetype_id || (typeof detectClientArchetype === "function" ? detectClientArchetype(liveP.title, liveP.category, liveP.tags).id : "uv_performance");
  const tLowTitle = (formattedTitle || liveP.title || "").toLowerCase();
  const isKids = ["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archetypeId) && (liveP.is_kids !== undefined ? liveP.is_kids : (/\b(infantil|kids|juvenil|mini)\b/i.test(tLowTitle) && !/\b(adulto|unissex adulto)\b/i.test(tLowTitle)));
  const isShortSleeve = liveP.is_short_sleeve !== undefined ? liveP.is_short_sleeve : (/\b(manga curta|manga-curta)\b/i.test(tLowTitle) && !/\b(manga longa|manga-longa)\b/i.test(tLowTitle));

  const quickBadgesHtml = buildClientQuickBadges(themeColor, themeBg, archetypeId, liveP);
  const sizeGuideHtml = buildClientSizeGuide(themeColor, themeBg, archetypeId, isKids, isShortSleeve, liveP);
  const schemaJsonLd = buildClientSchemaJsonLd(liveP);

  // 2. Blocos Narrativos
  const blocksHtml = [];
  blocks.forEach((block, idx) => {
    const isReverse = (idx % 2 === 1);
    const reverseClass = isReverse ? " reverse" : "";
    
    // Obter imagem única do bloco sem nunca duplicar
    const blockImg = (idx === 0) ? img1 : (idx === 1) ? img2 : (idx === 2 ? img3 : "");

    const tagText = block.tag || "Destaque";
    const tagIcon = getTagIconName(tagText);
    const actTitle = (block.title || "").toUpperCase();
    const actDesc = block.description || "";
    const blockSplitImgs = block.split_images || (idx === 0 ? splitImages : null);

    let mediaHtml = "";
    if (blockSplitImgs && blockSplitImgs.length >= 2) {
      mediaHtml = `<div class="brk-desc-media brk-desc-media-split">
        <div class="brk-split-item"><img src="${blockSplitImgs[0]}" alt="${formattedTitle} - Opção 1" loading="lazy" referrerpolicy="no-referrer" /></div>
        <div class="brk-split-item"><img src="${blockSplitImgs[1]}" alt="${formattedTitle} - Opção 2" loading="lazy" referrerpolicy="no-referrer" /></div>
      </div>`;
    } else if (blockImg) {
      mediaHtml = `<div class="brk-desc-media">
        <img src="${blockImg}" alt="${block.alt || formattedTitle}" loading="lazy" referrerpolicy="no-referrer" />
      </div>`;
    }

    let varNoticeHtml = "";
    if (idx === 0 && hasMultipleVariations && variationsSummary) {
      varNoticeHtml = `
      <div class="brk-variations-notice">
        <span class="brk-var-icon">${getSvgIcon('palette', themeColor, 15)}</span>
        <span class="brk-var-text">${variationsSummary}</span>
      </div>`;
    }

    if (mediaHtml) {
      blocksHtml.push(`
  <!-- Ato ${idx + 1}: ${tagText} -->
  <div class="brk-desc-block${reverseClass}">
    ${mediaHtml}
    <div class="brk-desc-text">
      <span class="brk-desc-tag">${getSvgIcon(tagIcon, themeColor, 12)} ${tagText}</span>
      <h3 class="brk-desc-title">${actTitle}</h3>
      <p class="brk-desc-paragraph">${actDesc}</p>${varNoticeHtml}
    </div>
  </div>`);
    } else {
      blocksHtml.push(`
  <!-- Ato ${idx + 1}: ${tagText} (Destaque Conceitual) -->
  <div class="brk-desc-block brk-desc-block-text-only">
    <div class="brk-desc-text" style="width: 100%; max-width: 100%;">
      <span class="brk-desc-tag">${getSvgIcon(tagIcon, themeColor, 12)} ${tagText}</span>
      <h3 class="brk-desc-title">${actTitle}</h3>
      <p class="brk-desc-paragraph">${actDesc}</p>${varNoticeHtml}
    </div>
  </div>`);
    }
  });

  // 3. Especificações Técnicas (Omitido para Camisas Agro e Motors)
  let specsSection = "";
  if (specs && specs.length > 0) {
    const specsRows = specs.map(s => `
      <div class="brk-spec-item">
        <span class="brk-spec-label"><span class="brk-bullet">${getSvgIcon('chevron', themeColor, 9)}</span> ${s.label}</span>
        <span class="brk-spec-value">${s.value}</span>
      </div>`).join("");

    specsSection = `  <!-- Box de Especificacoes e Cuidados -->
  <div class="brk-desc-specs-box">
    <h4 class="brk-desc-specs-title">
      <span class="brk-title-icon">${getSvgIcon('clipboard', themeColor, 16)}</span>
      <span>Detalhes Técnicos & Cuidados de Conservação</span>
    </h4>
    <div class="brk-specs-grid">${specsRows}
    </div>

    <!-- Guia de Cuidados -->
    <div class="brk-desc-care-box">
      <span class="brk-care-icon">${getSvgIcon('care', themeColor, 18)}</span>
      <div class="brk-care-text">
        <strong>Guia de Cuidados & Conservação da Peça:</strong> ${careTips}
      </div>
    </div>
  </div>`;
  } else {
    specsSection = `  <!-- Guia de Cuidados (Ficha Técnica Descartada para Camisas Agro e Motors) -->
  <div class="brk-desc-care-box" style="margin-top: 36px;">
    <span class="brk-care-icon">${getSvgIcon('care', themeColor, 18)}</span>
    <div class="brk-care-text">
      <strong>Guia de Cuidados & Conservação da Peça:</strong> ${careTips}
    </div>
  </div>`;
  }

  // 4. Aviso de Propriedade Intelectual (Camisas C0 - Fica no Final da Descrição, Amarelo sem Balança)
  let copyrightHtml = "";
  if (showCopyright) {
    copyrightHtml = `
  <!-- Aviso de Protecao de Estampas e Direitos Autorais (Camisas C0 - Final da Descricao) -->
  <div class="brk-desc-copyright-box">
    <div class="brk-copyright-text">
      <strong>Aviso de Propriedade Intelectual:</strong> Nossas estampas são protegidas pela Lei de Direitos Autorais (Lei 9.610/98) a Reprodução não autorizada está sujeita às penalidades legais. Copiar é crime !
    </div>
  </div>`;
  }

  // 5. Estrutura HTML Completa com CSS Embutido Responsivo
  return `${buildClientTrackingMarker(liveP.master_sku || liveP.sku || liveP.id, archetypeId)}
<!-- BRK GROUP - DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL SHOPIFY) -->
<div class="brk-desc-wrapper">
  <style>
    .brk-desc-wrapper {
      width: 100%;
      max-width: 980px;
      margin: 30px auto;
      padding: 0 10px;
      font-family: inherit;
      color: #1e293b;
      box-sizing: border-box;
      line-height: 1.5;
    }
    .brk-desc-wrapper * {
      box-sizing: border-box;
    }
    .brk-desc-header {
      margin-bottom: 32px;
      text-align: center;
      padding-bottom: 20px;
      border-bottom: 2px solid #e2e8f0;
    }
    .brk-desc-origin-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 5px 14px;
      border-radius: 9999px;
      margin-bottom: 12px;
    }
    .brk-desc-origin-badge.propria {
      color: ${themeColor};
      background: ${themeBg};
      border: 1px solid ${themeColor}35;
    }
    .brk-desc-origin-badge.revenda {
      color: #b45309;
      background: #fef3c7;
      border: 1px solid #fde68a;
    }
    .brk-desc-main-title {
      font-size: 26px;
      font-weight: 800;
      line-height: 1.25;
      color: #0f172a;
      margin: 0;
      letter-spacing: -0.4px;
    }

    /* Selos Rapidos de Confianca e Tecnologia (Destaque Superior) */
    .brk-quick-badges {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 34px;
    }
    .brk-badge-item {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 12px 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }
    .brk-badge-icon {
      width: 34px;
      height: 34px;
      border-radius: 10px;
      background: ${themeBg};
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .brk-badge-content {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .brk-badge-title {
      font-size: 12px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.25;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .brk-badge-sub {
      font-size: 10.5px;
      color: #64748b;
      line-height: 1.25;
      margin-top: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .brk-desc-copyright-box {
      background: #fffbeb;
      border-left: 4px solid #f59e0b;
      border-radius: 0 10px 10px 0;
      padding: 14px 18px;
      margin-top: 28px;
      border-top: 1px solid #fef3c7;
      border-right: 1px solid #fef3c7;
      border-bottom: 1px solid #fef3c7;
    }
    .brk-copyright-text {
      font-size: 12.5px;
      line-height: 1.55;
      color: #92400e;
    }
    .brk-copyright-text strong {
      color: #78350f;
    }
    .brk-desc-block {
      display: flex;
      align-items: center;
      gap: 36px;
      margin-bottom: 42px;
    }
    .brk-desc-block.reverse {
      flex-direction: row-reverse;
    }
    .brk-desc-block.brk-desc-block-text-only {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 24px 28px;
      margin-bottom: 34px;
    }
    .brk-desc-media {
      flex: 1;
      min-width: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .brk-desc-media img {
      width: 100%;
      height: auto;
      max-height: 520px;
      object-fit: contain;
      border-radius: 14px;
      display: block;
      margin: 0 auto;
      box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
      border: 1px solid #f1f5f9;
      background: #ffffff;
    }
    .brk-desc-media-split {
      display: flex;
      gap: 12px;
    }
    .brk-desc-media-split .brk-split-item {
      flex: 1;
      min-width: 0;
    }
    .brk-desc-media-split .brk-split-item img {
      max-height: 380px;
    }
    .brk-desc-text {
      flex: 1.15;
      min-width: 0;
    }
    .brk-desc-tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: ${themeColor};
      background: ${themeBg};
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 10px;
      border: 1px solid ${themeColor}25;
    }
    .brk-desc-title {
      font-size: 22px;
      font-weight: 800;
      line-height: 1.25;
      color: #0f172a;
      margin: 0 0 12px 0;
      text-transform: uppercase;
      letter-spacing: -0.3px;
    }
    .brk-desc-paragraph {
      font-size: 15px;
      line-height: 1.7;
      color: #475569;
      margin: 0;
    }
    .brk-variations-notice {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 14px;
      padding: 8px 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      color: #334155;
    }
    .brk-var-icon {
      font-size: 16px;
    }
    .brk-desc-specs-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 26px 24px;
      margin-top: 36px;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
    }
    .brk-desc-specs-title {
      font-size: 16px;
      font-weight: 800;
      color: #0f172a;
      margin: 0 0 18px 0;
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 12px;
      border-bottom: 2px solid #edf2f7;
    }
    .brk-title-icon {
      font-size: 18px;
    }
    .brk-specs-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px 22px;
    }
    .brk-spec-item {
      display: flex;
      flex-direction: column;
      border-bottom: 1px dashed #e2e8f0;
      padding-bottom: 8px;
    }
    .brk-spec-label {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .brk-bullet {
      font-weight: 900;
      font-size: 13px;
    }
    .brk-spec-value {
      font-size: 13.5px;
      font-weight: 600;
      color: #0f172a;
      margin-top: 3px;
    }
    .brk-desc-care-box {
      margin-top: 20px;
      background: #ffffff;
      border-left: 4px solid ${themeColor};
      border-radius: 0 10px 10px 0;
      padding: 14px 18px;
      font-size: 12.5px;
      line-height: 1.6;
      color: #334155;
      border-top: 1px solid #e2e8f0;
      border-right: 1px solid #e2e8f0;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }
    .brk-care-icon {
      font-size: 20px;
      line-height: 1.2;
    }
    .brk-care-text strong {
      color: #0f172a;
    }

    /* Tabela de Medidas Inteligente (Accordion Nativo) */
    .brk-size-guide {
      margin-top: 32px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
    }
    .brk-sg-summary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      background: #f8fafc;
      cursor: pointer;
      user-select: none;
      font-weight: 700;
      font-size: 14px;
      color: #0f172a;
      border-bottom: 1px solid transparent;
      transition: all 0.2s ease;
      list-style: none;
    }
    .brk-sg-summary::-webkit-details-marker {
      display: none;
    }
    .brk-size-guide[open] .brk-sg-summary {
      border-bottom-color: #e2e8f0;
      background: ${themeBg};
    }
    .brk-sg-title-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .brk-sg-icon {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .brk-sg-heading {
      font-size: 14px;
      font-weight: 800;
      color: #0f172a;
    }
    .brk-sg-trigger {
      font-size: 11px;
      font-weight: 700;
      color: ${themeColor};
      background: #ffffff;
      padding: 4px 10px;
      border-radius: 9999px;
      border: 1px solid ${themeColor}40;
    }
    .brk-sg-body {
      padding: 20px;
    }
    .brk-sg-tip {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      background: #f8fafc;
      border-left: 3px solid ${themeColor};
      padding: 10px 14px;
      border-radius: 0 8px 8px 0;
      font-size: 12px;
      color: #475569;
      margin-bottom: 16px;
      line-height: 1.5;
    }
    .brk-sg-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      text-align: left;
    }
    .brk-sg-table th {
      background: #f1f5f9;
      color: #334155;
      font-weight: 800;
      text-transform: uppercase;
      font-size: 10.5px;
      letter-spacing: 0.5px;
      padding: 10px 12px;
      border-bottom: 2px solid #e2e8f0;
    }
    .brk-sg-table td {
      padding: 9px 12px;
      border-bottom: 1px solid #f1f5f9;
      color: #1e293b;
    }
    .brk-sg-table tr:nth-child(even) td {
      background: #f8fafc;
    }
    .brk-sg-table tr:hover td {
      background: ${themeBg};
    }
    .brk-sg-card-header {
      background: #2e7d32;
      color: #ffffff;
      padding: 12px 16px;
      border-radius: 10px 10px 0 0;
      text-align: center;
      margin-bottom: 0;
    }
    .brk-sg-card-title {
      font-size: 15px;
      font-weight: 900;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: #ffffff;
      margin: 0;
    }
    .brk-sg-subtitle {
      font-size: 11.5px;
      color: #ffffff;
      opacity: 0.95;
      margin-top: 3px;
      font-style: italic;
    }
    .brk-sg-th-row th {
      background: #1e293b !important;
      color: #ffffff !important;
    }

    .brk-desc-trust-bar {
      margin-top: 32px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      text-align: center;
    }
    .brk-svg-icon {
      display: inline-block;
      vertical-align: -0.15em;
      flex-shrink: 0;
    }
    .brk-trust-svg {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 2px;
      height: 28px;
    }
    .brk-trust-item {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }
    .brk-trust-title {
      font-size: 12.5px;
      font-weight: 800;
      color: #0f172a;
    }
    .brk-trust-desc {
      font-size: 11px;
      color: #64748b;
      line-height: 1.3;
    }
    @media (max-width: 768px) {
      .brk-desc-main-title {
        font-size: 20px;
      }
      .brk-desc-block, .brk-desc-block.reverse {
        flex-direction: column !important;
        gap: 16px;
        margin-bottom: 34px;
        text-align: left;
      }
      .brk-desc-media-split {
        flex-direction: row;
        gap: 8px;
      }
      .brk-desc-title {
        font-size: 18px;
      }
      .brk-desc-paragraph {
        font-size: 14px;
      }
      .brk-quick-badges {
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-bottom: 26px;
      }
      .brk-badge-item {
        padding: 10px;
        gap: 8px;
      }
      .brk-badge-title {
        font-size: 11px;
      }
      .brk-badge-sub {
        font-size: 9.5px;
      }
      .brk-sg-table {
        font-size: 11px;
      }
      .brk-sg-table th, .brk-sg-table td {
        padding: 8px 6px;
      }
      .brk-specs-grid {
        grid-template-columns: 1fr;
      }
      .brk-desc-trust-bar {
        grid-template-columns: 1fr;
        gap: 8px;
      }
      .brk-trust-item {
        flex-direction: row;
        text-align: left;
        padding: 12px 14px;
        gap: 12px;
      }
    }
  </style>

${headerHtml}

${quickBadgesHtml}

  <!-- 3 Atos Narrativos de Alta Conversão -->
  ${blocksHtml.join("")}

${specsSection}

${sizeGuideHtml}

  <!-- Selos de Confiança e Garantia BRK -->
  <div class="brk-desc-trust-bar">
    <div class="brk-trust-item">
      <span class="brk-trust-svg">${getSvgIcon('shield', themeColor, 24)}</span>
      <div>
        <div class="brk-trust-title">Qualidade Oficial BRK</div>
        <div class="brk-trust-desc">Matérias-primas nobres testadas</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <span class="brk-trust-svg">${getSvgIcon('truck', themeColor, 24)}</span>
      <div>
        <div class="brk-trust-title">Envio Rápido & Seguro</div>
        <div class="brk-trust-desc">Rastreamento de ponta a ponta</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <span class="brk-trust-svg">${getSvgIcon('return', themeColor, 24)}</span>
      <div>
        <div class="brk-trust-title">Troca Descomplicada</div>
        <div class="brk-trust-desc">Satisfação garantida ou seu dinheiro de volta</div>
      </div>
    </div>
  </div>

${copyrightHtml}

</div>

${schemaJsonLd}`;

  // Guarda Final de Segurança: Eliminação rigorosa de qualquer tag <img> com URL raiz repetida
  const seenImgRoots = new Set();
  return fullHtml.replace(/<img[^>]+src=["']([^"']+)["'][^>]*>/gi, (match, src) => {
    const root = src.split("?")[0].toLowerCase();
    if (seenImgRoots.has(root)) {
      return "";
    }
    seenImgRoots.add(root);
    return match;
  });
}
