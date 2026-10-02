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

  [btnB, btnA, btnOrig].forEach(b => {
    if (b) b.className = "px-3.5 py-1.5 rounded-lg font-bold transition-all text-slate-600 hover:text-slate-900";
  });

  if (mode === "b" && btnB) {
    btnB.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-emerald-600 text-white shadow-sm";
  } else if (mode === "a" && btnA) {
    btnA.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-blue-600 text-white shadow-sm";
  } else if (mode === "orig" && btnOrig) {
    btnOrig.className = "px-3.5 py-1.5 rounded-lg font-extrabold transition-all bg-red-600 text-white shadow-sm";
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
    if (bannerDesc) bannerDesc.innerHTML = "<strong>Modo B Ativo:</strong> Redesenho persuasivo em 3 Atos narrativos com ícones vetoriais SVG estilo Font Awesome, layout sem corte e aviso legal no final.";
  } else if (currentModalMode === "a") {
    htmlToShow = currentModalProduct.mode_a_html || currentModalProduct.original_body_html || "<p>Sem HTML original</p>";
    if (banner) banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-blue-50 border-blue-200 text-blue-800";
    if (bannerDesc) bannerDesc.innerHTML = "<strong>Modo A Ativo:</strong> 100% do texto e tabelas originais preservados. Fotos antigas/mortas trocadas por fotos CDN da Shopify.";
  } else if (currentModalMode === "orig") {
    htmlToShow = currentModalProduct.original_body_html || "<p class='text-slate-400 italic'>Este produto não continha descrição original cadastrada.</p>";
    if (banner) banner.className = "p-3.5 rounded-xl border text-xs flex items-center justify-between bg-red-50 border-red-200 text-red-800";
    if (bannerDesc) bannerDesc.innerHTML = "<strong>Conteúdo Original:</strong> Exibe como o produto estava antes na loja (contendo imagens com erro 404 da AWS S3 se houver).";
  }

  if (contentElem) contentElem.innerHTML = htmlToShow;
  if (sourceElem) sourceElem.textContent = htmlToShow;
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

function getProductModeBHTML(liveP) {
  if (!liveP) return "";
  const originInfo = resolveClientOriginAndTitle(liveP);
  const formattedTitle = liveP.formatted_title || originInfo.formattedTitle;
  const brandName = liveP.brand_name || originInfo.brandName;
  const originType = liveP.origin_type || originInfo.originType;
  const showCopyright = (liveP.show_copyright !== undefined) ? liveP.show_copyright : originInfo.showCopyright;
  const hasMultipleVariations = liveP.has_multiple_variations || false;
  const splitImages = liveP.split_images || null;
  const variationsSummary = liveP.variations_summary || "";

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
    const archKey = liveP.archetype_id || (isLure ? "fishing_lures" : "uv_performance");
    const tmpl = moldes[archKey] || moldes["uv_performance"];

    if (tmpl && tmpl.act1 && tmpl.act2 && tmpl.act3) {
      blocks = [
        {
          tag: tmpl.act1.tag || "Destaque",
          title: tmpl.act1.title || "QUALIDADE E DESEMPENHO",
          description: (tmpl.act1.desc_tmpl || "").replace(/\{title\}/g, formattedTitle),
          image: img1,
          split_images: splitImages,
          variations_summary: variationsSummary
        },
        {
          tag: tmpl.act2.tag || "Destaque",
          title: tmpl.act2.title || "CONFORTO E TECNOLOGIA",
          description: (tmpl.act2.desc_tmpl || "").replace(/\{title\}/g, formattedTitle),
          image: img2
        },
        {
          tag: tmpl.act3.tag || "Destaque",
          title: tmpl.act3.title || "DURABILIDADE E ACABAMENTO",
          description: (tmpl.act3.desc_tmpl || "").replace(/\{title\}/g, formattedTitle),
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
  const isShirt = anyShirtWord(formattedTitle);
  const isAgroOrMotors = (liveP.store_key === "brk_agro" || liveP.store_key === "brk_motors" || (typeof currentStore !== "undefined" && (currentStore === "brk_agro" || currentStore === "brk_motors")));
  if (isShirt && isAgroOrMotors) {
    specs = [];
  } else if (specs.length === 0 && window.__STORE_MOLDES) {
    const archKey = liveP.archetype_id || "uv_performance";
    const tmpl = window.__STORE_MOLDES[archKey];
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
        <div class="brk-split-item"><img src="${blockSplitImgs[0]}" alt="${formattedTitle} - Opção 1" loading="lazy" /></div>
        <div class="brk-split-item"><img src="${blockSplitImgs[1]}" alt="${formattedTitle} - Opção 2" loading="lazy" /></div>
      </div>`;
    } else if (blockImg) {
      mediaHtml = `<div class="brk-desc-media">
        <img src="${blockImg}" alt="${block.alt || formattedTitle}" loading="lazy" />
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
      <span>Ficha Técnica & Cuidados de Conservação</span>
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
  return `<!-- BRK GROUP - DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL SHOPIFY) -->
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

  <!-- 3 Atos Narrativos de Alta Conversão -->
  ${blocksHtml.join("")}

${specsSection}

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

</div>`;

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
