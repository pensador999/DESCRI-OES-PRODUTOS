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
    const imgs = product.cdn_images || (product.gallery ? product.gallery.slice(0, 3) : []) || [];
    const countBadge = document.getElementById("modal-photos-count-badge");
    if (countBadge) countBadge.innerText = imgs.length + " Foto(s) no CDN Shopify";
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
    p.original_body_html = htmlToSave;
    p.status = "SAUDAVEL";
    p.is_out_of_standard = false;
    updateCockpit();
    renderProducts();
    showToast(`✅ Atualizado localmente! No deploy da Vercel, o endpoint /api/shopify_direct gravará automaticamente na Shopify.`);
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

  const finalImgs = [
    bunkerUrls[0],
    bunkerUrls[1] || bunkerUrls[0],
    bunkerUrls[2] || bunkerUrls[1] || bunkerUrls[0]
  ];

  currentModalProduct.cdn_images = finalImgs;

  const renderedDiv = document.getElementById("modal-rendered-content");
  const imgsInRendered = renderedDiv.querySelectorAll("img");
  imgsInRendered.forEach((img, idx) => {
    if (idx < finalImgs.length) {
      img.src = finalImgs[idx];
    }
  });

  const updatedHTML = renderedDiv.innerHTML;
  if (currentModalMode === "b") currentModalProduct.mode_b_html = updatedHTML;
  else currentModalProduct.mode_a_html = updatedHTML;

  document.getElementById("modal-source-code").textContent = updatedHTML;

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

  showToast("Fotos do BRK Bunker aplicadas com sucesso!");
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
  const isC0 = masterSku.startsWith("C0");
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
  const images = liveP.cdn_images || (liveP.images || []).map(img => img.src || img);
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
