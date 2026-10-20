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
    const rawImgs = (product.images && product.images.length > 0) ? product.images : (product.cdn_images || product.gallery || []);
    const imgs = sanitizeAndDedupClientImages(rawImgs, product.archetype_id, product.title);
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

async function syncLiveProductImages(btn) {
  if (!currentModalProduct) return;
  const p = currentModalProduct;
  const originalHtml = btn ? btn.innerHTML : "";
  if (btn) {
    btn.disabled = true;
    btn.classList.add("opacity-70");
    btn.innerHTML = `<span class="inline-block animate-spin">⏳</span> Buscando na Shopify...`;
  }

  try {
    const storeDomains = {
      "brk_fishing": "https://www.brkfishing.com.br",
      "brk_agro": "https://www.brkagro.com.br",
      "brk_motors": "https://www.brkmotors.com.br"
    };
    const storeBase = storeDomains[p.store_key || currentStore] || "https://www.brkfishing.com.br";
    const handle = p.handle;
    if (!handle) throw new Error("Produto sem handle cadastrado para consulta.");

    let newImgs = [];
    try {
      const url = `${storeBase}/products/${handle}.json?t=${Date.now()}`;
      const resp = await fetch(url, { cache: "no-store" });
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.product && data.product.images) {
          newImgs = sanitizeAndDedupClientImages(data.product.images, p.archetype_id, data.product.title || p.title);
        }
      }
    } catch (netErr) {
      console.warn("[syncLiveProductImages] Falha direta na vitrine, tentando proxy Vercel:", netErr);
    }

    if (newImgs.length === 0) {
      // Fallback via API serverless da Vercel
      const apiUrl = `/api/product_db?store=${p.store_key || currentStore}&id=${p.id}&sync_live=1&t=${Date.now()}`;
      const apiResp = await fetch(apiUrl, { cache: "no-store" });
      if (apiResp.ok) {
        const apiData = await apiResp.json();
        if (apiData && apiData.product) {
          const apiProd = apiData.product;
          newImgs = apiProd.cdn_images || apiProd.gallery || (apiProd.images || []).map(i => (typeof i === "object" ? i.src : i)).filter(Boolean);
          if (apiProd.mode_b_html) p.mode_b_html = apiProd.mode_b_html;
        }
      }
    }

    if (newImgs.length === 0) {
      throw new Error("Nenhuma foto encontrada na vitrine online da Shopify.");
    }

    // Desduplicar fotos com contingência anti-duplicação da 1ª foto na Shopify
    const uniqueImgs = sanitizeAndDedupClientImages(newImgs, p.archetype_id, p.title);
    p.images = uniqueImgs.map((src, i) => ({ id: i, src: src }));
    p.cdn_images = uniqueImgs;
    p.gallery = uniqueImgs;
    delete p.split_images;
    delete p.narrative_blocks;
    delete p.mode_b_markdown;

    // Atualiza miniaturas da galeria no modal
    const thumbsContainer = document.getElementById("modal-gallery-thumbs");
    if (thumbsContainer) {
      thumbsContainer.innerHTML = "";
      uniqueImgs.forEach((url, idx) => {
        const thumb = document.createElement("img");
        thumb.src = url;
        thumb.alt = "Foto " + (idx + 1);
        thumb.className = "w-8 h-8 object-cover rounded-lg border border-slate-300 shadow-sm cursor-pointer hover:border-blue-500 hover:scale-110 transition-all";
        thumb.title = "Foto " + (idx + 1) + " oficial atualizada da Shopify";
        thumb.onclick = () => window.open(url, '_blank');
        thumbsContainer.appendChild(thumb);
      });
    }

    const countBadge = document.getElementById("modal-photos-count-badge");
    if (countBadge) {
      countBadge.innerText = `${uniqueImgs.length} Fotos (Ao Vivo da Shopify)`;
      countBadge.className = "text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300";
    }

    // Regera o Modo B oficial com as novas fotos
    delete p.mode_b_html;
    if (typeof getProductModeBHTML === "function") {
      p.mode_b_html = getProductModeBHTML(p);
    }
    if (typeof buildClientModeBMarkdown === "function") {
      p.mode_b_markdown = buildClientModeBMarkdown(p);
    }
    updateModalView();

    if (typeof showToast === "function") {
      showToast(`✅ ${uniqueImgs.length} fotos oficiais sincronizadas diretamente da vitrine da Shopify!`);
    } else {
      alert(`✅ ${uniqueImgs.length} fotos sincronizadas com sucesso da Shopify!`);
    }
  } catch (err) {
    console.error("[syncLiveProductImages] Erro:", err);
    if (typeof showToast === "function") {
      showToast(`⚠️ Não foi possível sincronizar fotos da Shopify (${err.message}).`);
    } else {
      alert(`⚠️ Erro ao sincronizar fotos: ${err.message}`);
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.classList.remove("opacity-70");
      btn.innerHTML = originalHtml;
    }
  }
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
    if (bannerDesc) {
      const arch = currentModalProduct.archetype_id || "";
      const isHeadwear = ["caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"].includes(arch);
      if (isHeadwear) {
        bannerDesc.innerHTML = "<strong>⭐ Modo B Oficial (Novo Formato D2C Bonés & Chapéus):</strong> Grid de Detalhes 4x, Características & Cuidados, Seções Split (Produto Premium e Entrega Segura na Caixa BRK anti-deformação) e Schema.org SEO.";
      } else {
        bannerDesc.innerHTML = "<strong>⭐ Modo B Oficial (Novo Padrão BRK 100/100):</strong> Recomendado para colar na Shopify! Estrutura persuasiva em 3 Atos narrativos com Badges Rápidos no topo, Tabela de Medidas Expansível, Schema.org SEO e SVGs embutidos.";
      }
    }
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
  currentModalProduct.gallery = finalImgs;
  delete currentModalProduct.split_images;
  delete currentModalProduct.narrative_blocks;
  delete currentModalProduct.mode_b_markdown;
  // Recalcular HTML com as novas imagens
  currentModalProduct.mode_b_html = getProductModeBHTML(currentModalProduct);
  if (typeof buildClientModeBMarkdown === "function") {
    currentModalProduct.mode_b_markdown = buildClientModeBMarkdown(currentModalProduct);
  }
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
  const rawTitle = (liveP.title || "Produto BRK").trim()
    .replace(/\bÒculos\b/g, "Óculos")
    .replace(/\bòculos\b/g, "óculos")
    .replace(/\bProtecão\b/g, "Proteção")
    .replace(/\bprotecão\b/g, "proteção")
    .replace(/\bBalaclava\s+Balaclava\b/gi, "Balaclava")
    .replace(/\s{2,}/g, " ")
    .trim();
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
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
      "sub": "Conforto o Dia Todo"
    },
    {
      "icon": "shield",
      "title": "Costura Dupla Ombro",
      "sub": "Estrutura Anti-Deformação"
    },
    {
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
    }
  ],
  "pants_cargo_tactical": [
    {
      "icon": "shield",
      "title": "Tecido Alta Gramatura",
      "sub": "Resistente ao Atrito"
    },
    {
      "icon": "gear",
      "title": "Costuras Reforçadas",
      "sub": "Travetes de Alta Tensão"
    },
    {
      "icon": "box",
      "title": "Bolsos Funcionais",
      "sub": "Profundos e Estruturados"
    },
    {
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
    }
  ],
  "overalls_workwear": [
    {
      "icon": "shield",
      "title": "100% Impermeável",
      "sub": "Termossoldagem Estanque"
    },
    {
      "icon": "shoe",
      "title": "Bota Integrada",
      "sub": "Solado Tratorado Firme"
    },
    {
      "icon": "gear",
      "title": "Alças Reguláveis",
      "sub": "Engate Rápido"
    },
    {
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
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
      "title": "Fixação Anatômica",
      "sub": "Ajuste Firme no Braço"
    },
    {
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
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
      "title": "Toque Frio Anti-Atrito",
      "sub": "Conforto e Respirabilidade"
    },
    {
      "icon": "bolt",
      "title": "Secagem Ultra Rápida",
      "sub": "Tecido Tecnológico Leve"
    },
    {
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
    }
  ],
  "gloves_tactical_fishing": [
    {
      "icon": "shield",
      "title": "Palma Antiderrapante",
      "sub": "Alta Aderência e Grip"
    },
    {
      "icon": "bolt",
      "title": "Dorso Respirável",
      "sub": "Secagem Ultra Rápida"
    },
    {
      "icon": "gear",
      "title": "Encaixe Anatômico",
      "sub": "Firmeza no Pulso"
    },
    {
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
      "sub": "Padrão 100% Garantido"
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
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
      "icon": "sparkle",
      "title": "Qualidade Oficial BRK",
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
      "sub": "Perfume Prolongado"
    },
    {
      "icon": "gear",
      "title": "Suspensão Prática",
      "sub": "Retrovisor Interno"
    },
    {
      "icon": "sparkle",
      "title": "Garantia Oficial BRK",
      "sub": "Procedência 100% Original"
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
      "icon": "sparkle",
      "title": "Garantia Oficial BRK",
      "sub": "Procedência 100% Original"
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
    { icon: "sparkle", title: "Garantia Oficial BRK", sub: "Procedência 100% Original" }
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

  // 1. Identificar se o produto é comprovadamente de vestuário superior / camisa
  // Nota: Camisas ArmorX e Hybrid possuem "com Luva" no título, portanto "luva" não desqualifica quando é camisa/CAX/HYB
  const hasExplicitShirtMarker = /camisa|camiseta|jersey|baby look|babylook|armorx|fusionx|segunda pele/i.test(tLow) || /^(c0|ci|cadv|adv|hyb|cmb|cbt|raglan|cax|fusion|casual|bp|cf|cm|apc)/i.test(skuLow);
  const nonShirtRegex = hasExplicitShirtMarker
    ? /\b(calça|calca|calças|calcas|bermuda|bermudas|shorts|short|macacão|macacao|sandália|sandalia|babuche|chinelo|sapato|tênis|tenis|bota|botina|boaonda|chapéu|chapeu|boné|bone|manguito|manguitos|bandana|tubeneck|buff|balaclava)\b/i
    : /\b(calça|calca|calças|calcas|bermuda|bermudas|shorts|short|macacão|macacao|sandália|sandalia|babuche|chinelo|sapato|tênis|tenis|bota|botina|boaonda|chapéu|chapeu|boné|bone|luva|luvas|manguito|manguitos|bandana|tubeneck|buff|balaclava)\b/i;
  const isShirt = (
    ["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archetypeId) ||
    hasExplicitShirtMarker
  ) && !nonShirtRegex.test(tLow);

  // 0. Exclusão estrita de itens não-têxteis com UV ou termos ambíguos (apenas se NÃO for camisa)
  if (!isShirt) {
    if (/\b(óculos|oculos|faca|facas|canivete|alicate|vara|varas|molinete|carretilha|isca|iscas|linha|linhas|anzol|anzois|anzóis|estojo|garrafa|copo|chaveiro|adesivo|carteira|protetor solar)\b/i.test(tLow)) {
      return "";
    }
  }

  const isFusionSg = isShirt && (tLow.includes("fusion") || skuLow.includes("fusion"));
  const isHybridSg = isShirt && (tLow.includes("hybrid") || skuLow.startsWith("hyb"));
  const isArmorxSg = isShirt && (tLow.includes("armorx") || skuLow.startsWith("cax") || tLow.includes("com luva") || tLow.includes("e luva"));
  const isHoodedSg = isShirt && (tLow.includes("capuz") || isFusionSg || isHybridSg);

  let tipText = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura do ombro à barra | Manga do ombro ao punho). Dica: compare com uma peça sua estendida para escolher o caimento ideal.";
  if (isFusionSg) {
    tipText = "<strong>Como medir com precisão (Linha FusionX — Com Capuz & Bandana Embutida):</strong> A grade do tronco (PP ao G2) segue a mesma modelagem base BRK. <strong>Tórax:</strong> medido de axila a axila | <strong>Altura:</strong> medida da costura do ombro até a barra inferior (<u>sem contar o capuz e a bandana/máscara facial embutida</u>) | <strong>Manga:</strong> medida do ombro ao punho (com extensão elástica e abertura para o polegar/dedeira). O capuz e a bandana acoplada possuem elasticidade anatômica XTech Pro® que se ajusta ao rosto sem apertar.";
  } else if (isHybridSg) {
    tipText = "<strong>Como medir com precisão (Linha Hybrid — Com Capuz Anatômico & Dedeira):</strong> A grade do tronco (PP ao G2) segue a mesma modelagem base BRK. <strong>Tórax:</strong> medido de axila a axila | <strong>Altura:</strong> medida da costura do ombro até a barra inferior (<u>sem contar a altura do capuz integrado</u>) | <strong>Manga:</strong> medida do ombro ao punho (com extensão elástica e abertura para o polegar/dedeira).";
  } else if (isArmorxSg) {
    tipText = "<strong>Como medir com precisão (Linha ArmorX — Com Luva Integrada no Punho):</strong> A grade do tronco (PP ao G2) segue a mesma modelagem base BRK. <strong>Tórax:</strong> medido de axila a axila | <strong>Altura:</strong> medida da costura do ombro até a barra inferior (sem contar a gola alta) | <strong>Manga:</strong> medida do ombro à base do punho (contando com prolongamento anatômico com abertura para o polegar que protege o dorso da mão).";
  } else if (isHoodedSg) {
    tipText = "<strong>Como medir com precisão (Modelo com Capuz Integrado):</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura da costura do ombro à barra inferior, <u>desconsiderando o capuz</u> | Manga do ombro ao punho).";
  }

  let specialShirtPrefix = null;
  if (isFusionSg) specialShirtPrefix = "Camisa UV50+ FusionX (Capuz + Bandana Embutida + Dedeira)";
  else if (isHybridSg) specialShirtPrefix = "Camisa UV50+ Hybrid (Capuz Anatômico + Punho com Dedeira)";
  else if (isArmorxSg) specialShirtPrefix = "Camisa UV50+ ArmorX (Punho Estendido com Luva Integrada)";
  else if (isHoodedSg) specialShirtPrefix = "Camisa Manga Longa UV50 com Capuz Integrado";

  if (isShirt) {
    // 1.1 Camisas de Botão / Utilitárias Work (CMB - Sarja/Algodão corte reto de trabalho)
    const isWorkGuide = (archetypeId === "shirts_button_work" || skuLow.includes("cmb") || skuLow.includes("cbt") || (tLow.includes("work") && tLow.includes("camisa") && !tLow.includes("xtech") && !tLow.includes("dry") && !tLow.includes("uv") && !tLow.includes("pesca"))) && !skuLow.startsWith("c0") && !skuLow.startsWith("ci");
    if (isWorkGuide) {
      const isFemWork = /feminina|feminino|baby look|babylook/i.test(tLow) || skuLow.includes("bl");
      const mHeader = isShortSleeve ? "Manga Curta" : "Manga Longa";
      let rows;
      if (isFemWork) {
        guideTitle = "Tabela de Medidas Feminina - Camisas Country & Classic de Botão (P ao G2)";
        tipText = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Busto/Tórax | Comprimento da gola à barra | Manga). Modelagem feminina acinturada.";
        rows = [
          ["P (36-38)", "92 cm", "61 cm", isShortSleeve ? "19 cm" : "60 cm"],
          ["M (40)", "96 cm", "63 cm", isShortSleeve ? "20 cm" : "61 cm"],
          ["G (42)", "102 cm", "65 cm", isShortSleeve ? "21 cm" : "62 cm"],
          ["GG (44)", "108 cm", "67 cm", isShortSleeve ? "22 cm" : "63 cm"],
          ["G1 (46)", "114 cm", "69 cm", isShortSleeve ? "23 cm" : "64 cm"],
          ["G2 (48)", "120 cm", "71 cm", isShortSleeve ? "24 cm" : "65 cm"],
        ];
      } else {
        guideTitle = "Tabela de Medidas - Camisas Work & Utilitárias de Botão (P ao G2)";
        tipText = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Comprimento da gola à barra | Manga). Modelagem confortável de trabalho.";
        rows = [
          ["P", "102 cm", "68 cm", isShortSleeve ? "22 cm" : "75 cm"],
          ["M", "108 cm", "71 cm", isShortSleeve ? "23 cm" : "77 cm"],
          ["G", "114 cm", "74 cm", isShortSleeve ? "24 cm" : "79 cm"],
          ["GG", "120 cm", "77 cm", isShortSleeve ? "25 cm" : "81 cm"],
          ["XG", "126 cm", "80 cm", isShortSleeve ? "26 cm" : "83 cm"],
          ["EXG (G1)", "132 cm", "83 cm", isShortSleeve ? "27 cm" : "85 cm"],
          ["G2", "138 cm", "85 cm", isShortSleeve ? "28 cm" : "87 cm"],
        ];
      }
      tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Tórax / Circunferência</th><th>Comprimento Total</th><th>${mHeader}</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
    }
    // 1.1b Kit Casal (Exibe AMBAS as tabelas: Masculina + Feminina Baby Look)
    else if (tLow.includes("casal") && (tLow.includes("kit") || tLow.includes("combo"))) {
      guideTitle = "Tabela de Medidas Kit Casal - Masculino & Feminino Baby Look (PP ao G2)";
      const shirtSubPrefix = specialShirtPrefix || (isShortSleeve ? "Camisa Manga Curta UV50" : "Camisa Manga Longa UV50");
      const subtitle = `${shirtSubPrefix} | *As medidas podem variar de 2cm a 3cm`;
      const mRows = [
        ["PP", "49,5 cm", "67 cm", "56 cm"],
        ["P", "51,5 cm", "69 cm", "59,5 cm"],
        ["M", "54 cm", "71 cm", "62 cm"],
        ["G", "56 cm", "72 cm", "64 cm"],
        ["GG", "59 cm", "74 cm", "64 cm"],
        ["G1", "62 cm", "75 cm", "66 cm"],
        ["G2", "65 cm", "76,5 cm", "66 cm"],
      ];
      const fRows = [
        ["Baby Look PP", "33 cm", "51 cm", "53 cm"],
        ["Baby Look P", "37 cm", "54 cm", "55 cm"],
        ["Baby Look M", "43 cm", "57 cm", "59 cm"],
        ["Baby Look G", "47 cm", "60 cm", "60 cm"],
        ["Baby Look GG", "47 cm", "60 cm", "61 cm"],
        ["Baby Look G1", "50 cm", "62 cm", "61 cm"],
        ["Baby Look G2", "55 cm", "64 cm", "63 cm"],
      ];
      tableHtml = `<div class="brk-sg-card-header"><div class="brk-sg-card-title">MASCULINO</div><div class="brk-sg-subtitle">${subtitle}</div></div><table class="brk-sg-table" style="margin-bottom: 18px;"><thead><tr class="brk-sg-th-row"><th>TAMANHO</th><th>TÓRAX</th><th>ALTURA</th><th>MANGA</th></tr></thead><tbody>${mRows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table><div class="brk-sg-card-header"><div class="brk-sg-card-title">FEMININO (BABY LOOK)</div><div class="brk-sg-subtitle">${subtitle}</div></div><table class="brk-sg-table"><thead><tr class="brk-sg-th-row"><th>TAMANHO</th><th>TÓRAX</th><th>ALTURA</th><th>MANGA</th></tr></thead><tbody>${fRows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
    }
    // 1.2 Camisas UV C0 Infantil (1 a 13 Anos | PP ao G2)
    else if (
      isKids
      || /infantil|kids|juvenil|criança|crianca/i.test(tLow)
      || /kids|inf/i.test(skuLow)
      || ((skuLow.startsWith("ci") || /^(?:c0|ci|cf|cm|casual|adv|cadv|ccpbr|bp|hyb|fusion|cax|raglan)\d+i(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$/i.test(skuLow)) && !/feminina|feminino|baby look|babylook|masculina|masculino|adulto/i.test(tLow))
    ) {
      guideTitle = "Guia de Tamanhos Infantil (1 a 13 Anos)";
      const badgeTitle = "INFANTIL";
      tipText = "<strong>Escolha por Idade com Referência de Tamanho (PP ao G2):</strong> Na linha Infantil BRK, a seleção é guiada pela faixa de idade (1 a 13 Anos) mantendo a indicação do tamanho equivalente (PP ao G2). Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura do ombro à barra, sem contar eventual capuz | Manga do ombro ao punho).";
      const shirtSubPrefix = specialShirtPrefix || (archetypeId === "agro_field" ? "Camiseta Algodão Premium" : (isShortSleeve ? "Camisa Manga Curta UV50" : "Camisa Manga Longa UV50"));
      const subtitle = `${shirtSubPrefix} | *As medidas podem variar de 2cm a 3cm`;
      const rows = [
        ["1 a 2 Anos (PP)", "31 cm", "41 cm", "31 cm"],
        ["2 a 3 Anos (P)", "33 cm", "45 cm", "35 cm"],
        ["4 a 5 Anos (M)", "35 cm", "49 cm", "37 cm"],
        ["6 a 7 Anos (G)", "38 cm", "52 cm", "39 cm"],
        ["8 a 9 Anos (GG)", "39 cm", "55 cm", "42 cm"],
        ["10 a 11 Anos (G1)", "41 cm", "58 cm", "44 cm"],
        ["12 a 13 Anos (G2)", "43 cm", "61 cm", "45 cm"],
      ];
      tableHtml = `<div class="brk-sg-card-header"><div class="brk-sg-card-title">${badgeTitle}</div><div class="brk-sg-subtitle">${subtitle}</div></div><table class="brk-sg-table"><thead><tr class="brk-sg-th-row"><th>IDADE / TAMANHO</th><th>TÓRAX</th><th>ALTURA</th><th>MANGA</th></tr></thead><tbody>${rows.map(r => `<tr><td><strong>${r[0]}</strong></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table>`;
    }
    // 1.3 Camisas UV C0 Feminina / Baby Look (PP ao G2)
    else if (/feminina|feminino|baby look|fem|babylook/i.test(tLow) || skuLow.includes("bl")) {
      guideTitle = "Tabela de Medidas Feminina - Baby Look (PP ao G2)";
      const badgeTitle = "FEMININO";
      const shirtSubPrefix = specialShirtPrefix || (archetypeId === "agro_field" ? "Camiseta Algodão Premium" : (isShortSleeve ? "Camisa Manga Curta UV50" : "Camisa Manga Longa UV50"));
      const subtitle = `${shirtSubPrefix} | *As medidas podem variar de 2cm a 3cm`;
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
      const shirtSubPrefix = specialShirtPrefix || (archetypeId === "agro_field" ? "Camiseta Algodão Premium" : (isShortSleeve ? "Camisa Manga Curta UV50" : "Camisa Manga Longa UV50"));
      const subtitle = `${shirtSubPrefix} | *As medidas podem variar de 2cm a 3cm`;
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
  else if ((["pants_cargo_tactical", "overalls_workwear"].includes(archetypeId) || (!isShirt && /\b(calça|calca|calças|calcas|bermuda|bermudas|shorts|short|macacão|macacao)\b/i.test(tLow))) && !tLow.includes("bota")) {
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
  } else if (archetypeId === "neck_gaiters_balaclavas" || /bandana|tubeneck|buff|balaclava|lenço|lenco/i.test(tLow)) {
    if (tLow.includes("lenço") || tLow.includes("lenco")) {
      guideTitle = "Dimensões - Lenço Quadrado de Amarração UV50+";
      tipText = "<strong>Dimensões do produto:</strong> Modelagem quadrada plana em tecido leve com proteção UV50+ para amarração versátil na cabeça, cabelo ou pescoço.";
      tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Formato</th><th>Dimensões Aproximadas</th><th>Ajuste</th></tr></thead><tbody><tr><td><strong>Tamanho Único</strong></td><td>Quadrado Plano</td><td>Aprox. 55 x 55 cm</td><td>Amarração livre ajustável (cabeça, pescoço, cabelo ou acessórios)</td></tr></tbody></table>`;
    } else if (tLow.includes("black mask") || tLow.includes("blackmask")) {
      guideTitle = "Dimensões - Bandana Anatômica Black Mask UV50+";
      tipText = "<strong>Dimensões do produto:</strong> Modelagem anatômica 3D com recorte nasal ergonômico, painel frontal respirável em tela Mesh e cobertura alongada de pescoço.";
      tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Largura Facial</th><th>Altura Frontal / Pescoço</th><th>Estrutura</th></tr></thead><tbody><tr><td><strong>Tamanho Único</strong></td><td>Aprox. 25 cm (Elástica)</td><td>Aprox. 36 cm</td><td>Recorte nasal anatômico + Tela respirável frontal + Tecido UV50+</td></tr></tbody></table>`;
    } else if (tLow.includes("balaclava") && !tLow.includes("tubeneck")) {
      guideTitle = "Dimensões - Capuz Balaclava Integral UV50+";
      tipText = "<strong>Dimensões do produto:</strong> Capuz integral elástico com visor ocular anatômico para cobertura completa de cabeça, rosto, orelhas e pescoço.";
      tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Circunferência Cabeça</th><th>Comprimento Total</th><th>Elasticidade</th></tr></thead><tbody><tr><td><strong>Tamanho Único</strong></td><td>54 cm a 62 cm (Adaptável)</td><td>Aprox. 40 cm</td><td>Malha tecnológica elástica com visor ocular anatômico</td></tr></tbody></table>`;
    } else {
      guideTitle = "Dimensões - Bandana Tubular Multifuncional UV50+";
      tipText = "<strong>Dimensões do produto:</strong> Microfibra tubular de alta elasticidade com proteção UV50+ e memória anatômica.";
      tableHtml = `<table class="brk-sg-table"><thead><tr><th>Tamanho</th><th>Largura (Plana)</th><th>Comprimento</th><th>Elasticidade</th></tr></thead><tbody><tr><td><strong>Tamanho Único</strong></td><td>Aprox. 24 cm</td><td>Aprox. 48 cm</td><td>Microfibra tubular elástica 4-Way Stretch com memória anatômica</td></tr></tbody></table>`;
    }
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
const MODO_B_VERSION = "2";

function buildClientTrackingMarker(sku, archetypeId) {
  const clean = (v) => String(v || "").replace(/[^A-Za-z0-9_.\-]/g, "").slice(0, 60).replace(/--/g, "-");
  return `<!-- BRK-MODO-B v${MODO_B_VERSION} | sku:${clean(sku)} | molde:${clean(archetypeId)} -->`;
}

const KNOWN_SHOPIFY_DUP_IMAGE_TOKENS = new Set([
  "0130fa478fe94fbd808e04a745ee4a96",
  "02539031efdb45bf80aa2ff07750588e",
  "02bce54ffdae4737bb5cb3e65005a9ed",
  "074d5ba735b4483990428b74a35b7ed1",
  "07f53a4c219149f4ae6734d196d54620",
  "0900789cc8c1460abd7df610904c4b2d",
  "09b4d40da2274d05b2fd0c2c5d868a55",
  "09c44b69f2b649ef9d8231a30021d36a",
  "0b12bc26bd6d4a4da12ee35cc0d3c616",
  "0b6247882ff24f63a7d106240fe5bd89",
  "0bd070689a8f4402be998734076dd2c8",
  "0bd1ffe19a9d47158d0e9e1750def8cd",
  "0c5e319cca3b40f6897bf96d9577a79f",
  "0e23c5eea4be458e92e74f121ec48b39",
  "0e3d4728d00a4c92970906d3311d6408",
  "0fb7c8ba7f0840c6911a0aebc7d1cf5a",
  "109a04128bc948b9a56797e0f732b00f",
  "10d106b973e3438286b054bf3e9f5c12",
  "119a7881885f43eeab36697519b2affe",
  "123ecc4f111f41688371d047a376887c",
  "1420181cbd1043e884b6094186b0f526",
  "1475b5209eab42b79cde7956bb0e76ab",
  "1750954608038-01_masc.jpg",
  "1750954608038-01_masc_91379c43-6657-4f6a-9d59-f80edaabe345.jpg",
  "1750954608038-01_masc_a1e40c2a-873f-4d53-9122-870039114d3b.jpg",
  "1750954608038-01_masc_cae84974-db9e-4cf5-bba1-78e49197cbdf.jpg",
  "1750954608038-01_masc_d4332740-c512-4c78-8c0f-5e87e5c859dc.jpg",
  "1750956158411-01_masc.jpg",
  "1750956158411-01_masc_1fa45ffb-b5f4-4d26-879d-4a29deae6abf.jpg",
  "1750956158411-01_masc_2314255d-07d1-466b-bd3d-de4cd2b620a7.jpg",
  "1750956158411-01_masc_8efe0125-a8cc-4ce6-abe7-a3f283414190.jpg",
  "1750956158411-01_masc_dfe0103b-9fa8-4bdb-ba1e-4f9d440ca513.jpg",
  "1752686429164-8_frente.jpg",
  "1752686430113-9_costas.jpg",
  "1a42261505774a85820f21db66796dc9",
  "1b32fa89d94d46ac82a8db5f0a9b081b",
  "1b35d5d1a2e54303bc6065f224a792c3",
  "1f419c603ecc426b828ee12fce2d45b6",
  "200845a16d7441d0855fb6329afce98d",
  "2017048dd2444a01a1dc6c3df73a3957",
  "2139af2a6d544758920a32a55cdfb30c",
  "2202db9f16554b568b1c176552a25748",
  "22b981cd6d8545cebf8381ccb8345083",
  "2429e08baf0a466bb0750fedf65f3838",
  "24838a29cc8244ac8664a032f3df232a",
  "27b94edbeb7c450e98ee8dbc19fb41f9",
  "2819e7f2c7f64ef4947388c495ea5392",
  "2920f776fd8e4428929702b9eb8eec45",
  "2b50f7c907054a5d95898bb0ce0ed105",
  "2be597f4817a4d9abfd0b8d0af8bea0b",
  "2bfaabf2469f4b59b6af1a36419f12eb",
  "2e34835beffb4c6aa34f2899bf5edd91",
  "2e6e3e83159d4fcf85d1094f4179d73b",
  "2f20b7136d2a42ceb42cb48b4a7367a3",
  "2f308d8d89e4447db1eb726596554dc6",
  "2f5e84430f264a3c9d39062d5b940611",
  "2fc34f0b0156487fb0ce14ac31bab947",
  "333ecce931d743d9afc42368942a886a",
  "33b4b44ea9cf4be0899966e3809c95e9",
  "341c9efb19a44453a9993015ffb22db1",
  "360991b7830e440fa55e68926bcdf4b4",
  "366d55c7ea3e46aaad0d60fcd3d0f9b5",
  "36901243a1fe4d5bb5654529e78e183f",
  "3735795d965b439eb86a5b89ed4c590d",
  "37e780617282406c800fd178a5b61a7f",
  "388b8179206d4d98852eb1cdbcda1fd6",
  "39b168f6f7c54e66835cda4f45e6e3db",
  "3d9adeab42e543acace85e28d34079b5",
  "3e1b3c9de58943c685da0ead456752a9",
  "409bce9db3624834af448d3120a63c12",
  "43b261897af24ba3b4a103bdfc64e788",
  "46727814b21e45f6883a218a944d0f9a",
  "4a10d6b747254e1685c0565f2f4867df",
  "4b01c34c8d6e477eb6a7cdff4d7e6666",
  "4c2921805fcd4187b1b2039d8bf521d2",
  "4c510b958cce45718e74cd86389229f1",
  "4cb5be6dbd2b4618b1e7da8d55c64145",
  "4d79af9439ab459dbf5413881e64dd6e",
  "4eda9bfd52894efc9d64796c6ba6b513",
  "4f7c178c274a4de59c7efa679b0296da",
  "4f84e2aad02f46efbf1e68ca2a954aad",
  "4fcdc6f74baf485d8a3b61241e59056b",
  "53248c610b324174a15c5e29c37b8ae7",
  "54374e8640964923916a8c79166b6f1e",
  "5575f62ca4014656ab4fbc7f036a90a9",
  "5607730a884f4af0a4f2db6ab6e3895e",
  "56a03f9923464be4b38febd23f085242",
  "576d2723fe1342c1bfe07d2a303c869d",
  "59674c7c8efe483084a090c9a02183e9",
  "599a7fdfed5d4df0a9964f2bec1e0902",
  "59b85d0331884bbfa63b0103d1a9cb2f",
  "5c2cf6a5f8ee447d902760c873b81368",
  "5d33e1fbdcdd436cb9f9a9d87d292005",
  "5e51f4a3e2ee49ffa871fad9bcaa4fcf",
  "5fb20ebea1914f3090e46410fdf66b86",
  "617fa9e526914c898d26e0abe5878dd6",
  "63a10590d393408dbdc086bd8f1173d6",
  "644d0ef00c5845db9619b7bc5455d5eb",
  "663d68eae93847bfaa8622da60651504",
  "66d05fc41cae4f5ab799cb61b1041102",
  "67a247e2f67848f5af7543adf8a1fff4",
  "69cc449c95d148dcb271f7b5127cc57f",
  "6bd5f20f2f484faea8da46cb2a004485",
  "6c584b43b17e4708ab5a853661b19184",
  "6e540ab30fb14ed69b1b73edc500c9f1",
  "6e691a1ac6e048a7821b8bcf499acd13",
  "6f5c474f9c594489875f083a0bb177fc",
  "70873852b5e045e8be6cc8c3e35317d3",
  "70fdf10f6fd244f4a074997f7aed4cbc",
  "72b0431e143e4981af6a0e09617b261c",
  "738c36cd8db64a099a172242b7cdd099",
  "73f2a135929c42709ab16646a4f8cb8d",
  "756600c792604ae1ac5d756ff5f77199",
  "773234af5942435197abf66f209860e1",
  "78bd16a7c3744d0aac11bda274bd369a",
  "792d1cd7f1c648859e48a0b77253323f",
  "792fc6ff6baa495184bfb90eaf9940e1",
  "7ce3f9c005f34642bdd3f94b7b8b0993",
  "7d612095efce48e59bc0eba6a988da16",
  "7fc2b61c8b5c4fd29c3255b3ed8be5a0",
  "80f2837593b1469fb55b21e73b347566",
  "81481598901048c4bf7cd4cfc8b61548",
  "8262dbf88f0549ec95ef6a60e76ceb3e",
  "82ee07f87b934e0f9a345ba530e57a0b",
  "83df9409d1c54d3791ac88fe037050e5",
  "85d1baf420ae40d99ef62a94403c540b",
  "870ffc7c817d4d879a76ec5e4e0b4525",
  "87c4e0e271eb4d5cab59cb100346a8b0",
  "87e0198755514d75a106b4fcceec1870",
  "880019dbae7c40479a9e7d592d783225",
  "8b14d4f17c564a1d89b391e38e9b7a93",
  "8d6f9e9fe5bd48eb9bc408a08162abdb",
  "8ddd73ca7e054abaab34e962ccd07f2f",
  "8ef0dbfea2ae4182bcd8b1892a15c238",
  "8ef33820b0574209b3aec89a81331f56",
  "8efa6c227fb541c2b48134003438dc6d",
  "8f3324f3600945f3891f80198ab483a4",
  "9124809cfc1746f6afb48bfbfd86ef9a",
  "924d0c66d64041899728ab18771677a0",
  "964df29bfaf84a0abd2356c784a1d82f",
  "97065dd51b0f4957bcddb1886e6c461d",
  "97e753a3c4844448a3dec11c3e1c29c9",
  "98b58fc3cfaa4ff89a31df2d1323bd48",
  "9a943601f8f24f66add5fe52dade723d",
  "9aa15896d03f44f5b4ad94f6fa90af88",
  "9b8fe3c4edc147d2b31e1e1dcfb8f534",
  "9bf8e1e957a34492b41485b6a470cd98",
  "9c0bd95bc2904bd5961ee88314dc5383",
  "9c1284001d9944608acc2dae4a36c888",
  "9d8931bd154b40bebe804a1d06c99e34",
  "9dd8f5d344e54e87bfc2251b6b675d55",
  "9e42b6851079451e9cb456356529cf52",
  "9ea61be537964c43be14efb42f20cd9a",
  "a00f3f91d0024158bcd065ce2025f179",
  "a085713739a24f92975fa42a48c893c3",
  "a0ec6f9ce03c401b948a291b7f3c8119",
  "a1ef49e2e2404cfd96f3462db4ecd911",
  "a3354d559c064477a566d0399934e3b6",
  "a3b3db5355344e44b9e5194a46e1af91",
  "a41e2520f0334d45a52c744412166c0b",
  "a50e3d52ea2e42b08b6a8307c114e8c9",
  "a5969d79260840d4859ab293178c5c75",
  "a5fc231c2ee04fdebede6c7446c8d185",
  "a957d576889045ad97ce8d6228895e57",
  "aabc408c343040e1986dc28b382a1b8f",
  "aba6a317ae514ba7b18e77ac0610deab",
  "ac5d7aac75c54e239a8ac3541d4a20bf",
  "ad6c1d776939419395d0d408f843891c",
  "ad6ebca104e94248b28d2e6f2609cb97",
  "ae98edd304924309b69af0881c126f89",
  "b07902021382425e873c07431563bcbc",
  "b12b03ea038d4cc289191d32487528d9",
  "b1560d73013547f9ad239a557e9daa80",
  "b30c206c171f469792b516ba4e3d442a",
  "b3a155fe185e45c9ab05f66960d09512",
  "b64e144795e64b258dab792411e8fe17",
  "b7d9df5733b14850a1fb74862ab74e18",
  "b847dcad60e4437787f4afebc28a45d1",
  "b8f5b75cab344afbbbdfd59bcc21a6c0",
  "b91380e34dfe48a98ec184d66486cb54",
  "be5534ff14a24ef79cfcd54de1a5b16e",
  "bf5c9610034f4fc7839736654846ebfa",
  "bf7493bde73d477f98e254fb15e42025",
  "bfb14f0ae7dd4addae1d9b091bd50342",
  "bfd6a01a86a34b91acde28c3d7d6947e",
  "bff288ad7be84bb4987c10741114419f",
  "c14f205a2cd646e3aa09b36762639610",
  "c15674b7eb9941f886f47d82df5305bc",
  "c15f012455fc4be395e4a98c0bd4e574",
  "c2376731105c4cfb9b94f2517a4a179e",
  "c2fe47b2142f4fafa377941743881abe",
  "c42f922b43f74651859c4d41eec0f097",
  "c55f50d6bb944f7ba84d6c2c3ca4f2bb",
  "c6a4654607214347b9d0f8f1df28ae02",
  "c7f9037243d0404cb134f0b7c3cc47f0",
  "cab17a0cccca47f2884f25efde8b8e42",
  "cb2bb07ad82347b5856bdcde10200b86",
  "cb5b0db3a9e045328e683d0cc1966104",
  "cf2fc9bf51d94d8b86fd7f035d46d036",
  "d0ea5ec87f0349f68e70e391d09a8363",
  "d3920c717c55416794c070500ed224e4",
  "d492749f64f849b08462595a1eb29f9a",
  "d5222baad8da454f832a5d3fb0bedda1",
  "d595a026cb0f41269f49a5ebd5374c1f",
  "d608c18612e542d8a4eb9ef532ab2bc1",
  "d79ff16ced6340ef90d4e339bcb6572e",
  "d930950665cb4b089277345fc4e7f8b5",
  "da70e9fa00204babb2231735df758f95",
  "dba7086f487943b29eed3a58da0ef1c1",
  "dea06687c3dd4a1ca2003ac0dda2a436",
  "e0ac0b0e251f47538ae061cb0cc01f86",
  "e1e9b05ce7ab482ea29f16337499084b",
  "e306d28dd244493b8b38527d66ac3527",
  "e32e9b28ebda4b09a456e0ba8c0c2524",
  "e65169c353154aaeb557d806ae1cf296",
  "ecfc45c9c4cb4d108d9657bc1c1d83db",
  "ef03305e5d674c4c902f05d58d2682aa",
  "ef99a23a13544c738802a6be70c0ba0a",
  "f06206dd58594f51b9472c9acc58d9bf",
  "f0ca4b7d9883484a8b1bbf70f66d6f51",
  "f12c325d6ccb415f8bdb6f9c23470d5f",
  "f256198473974784b27181ba18ff70cd",
  "f364e233d28f4c0b9fe312316b0f0ec2",
  "f399744e19924d3f8fdeaf6e50ec2f2b",
  "f409ce350e5542b180c80390d388edab",
  "f685a6ebe7e4479ca59d2492b3f59db6",
  "f7542336b44e468e8c3e57c5e263ac42",
  "f78f55cb63f64aa3b59a0980b93165e0",
  "f9ce986a86e543f8b6d288714093825a",
  "fa6530264a684924a8f261eb8fc73011",
  "fb17213952f84ecca5ec7b02ec3304be",
  "fb9def04c9174ae3a29a572694315f4d",
  "fbb9f22bb404418fb41e242a94b8ae21",
  "fedcc88e79524f51ae0e6900a6dc7730",
  "ff03f85c460f4aac930bcfab9e761b7c",
  "ff854bc26d574957bca986fe0049263f",
  "whgf96p_7db6902a-a660-49dd-b94f-647a3bf0246a.png"
]);

function sanitizeAndDedupClientImages(rawSources, archetypeId = "uv_performance", title = "") {
  if (!rawSources || !Array.isArray(rawSources)) return [];
  const tLow = String(title || "").toLowerCase();
  const isMultiColorProduct = ["kit", "combo", "sortid", "cores", "opções", "opcoes"].some(w => tLow.includes(w)) || archetypeId === "fishing_lures";

  // Camada 1: Se vierem objetos da API Shopify com variant_ids, colapsar capas repetidas por tamanho
  const dictItems = rawSources.filter(x => x && typeof x === "object" && x.src);
  let filteredSources = rawSources;
  if (dictItems.length >= 3 && !isMultiColorProduct) {
    const varImgs = dictItems.filter(x => Array.isArray(x.variant_ids) && x.variant_ids.length > 0);
    const nonVarImgs = dictItems.filter(x => !Array.isArray(x.variant_ids) || x.variant_ids.length === 0);
    if (varImgs.length >= 2 && nonVarImgs.length >= 1) {
      const firstDims = `${varImgs[0].width || 0}x${varImgs[0].height || 0}`;
      const allSameDims = varImgs.every(x => `${x.width || 0}x${x.height || 0}` === firstDims);
      if (allSameDims) {
        filteredSources = [varImgs[0], ...nonVarImgs];
      }
    }
  }

  const uuidRe = /_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?=\.[a-z0-9]+$)/i;
  const seenKeys = new Set();
  const seenPureFrontMockup = new Set();
  const rawDeduped = [];

  filteredSources.forEach(item => {
    const u = (item && typeof item === "object") ? item.src : item;
    if (!u || typeof u !== "string") return;
    const cleanU = u.trim();
    if (!cleanU || !cleanU.startsWith("http")) return;

    const uLow = cleanU.toLowerCase();
    // Camada 2: Bloqueio de tokens secundários 100% idênticos em bytes auditados nas 3 lojas
    if (rawDeduped.length >= 1 && Array.from(KNOWN_SHOPIFY_DUP_IMAGE_TOKENS).some(tok => uLow.includes(tok))) {
      return;
    }

    // Camada 3: Normalização de UUID, sufixos de re-exportação e prefixos de timestamp
    const fname = cleanU.split("?")[0].split("/").pop().toLowerCase();
    const fnameNoUuid = fname.replace(uuidRe, "");
    let stem = fnameNoUuid.replace(/\.(jpg|jpeg|png|webp|gif)$/i, "");
    stem = stem.replace(/(_-_jpg|_-_png|-reduzido|_reduzido|_copy|-copy)$/i, "");
    const tsStripped = stem.replace(/^\d{10,14}[-_]/, "");
    if (tsStripped.length > 2) {
      stem = tsStripped;
    }

    if (seenKeys.has(stem)) return;

    const isPureFrontLabel = stem.includes("frente") && !["costa", "verso", "tras", "detalhe", "zoom", "persp", "lateral", "2", "02", "3", "03", "4", "04", "5", "05"].some(k => stem.includes(k));
    if (isPureFrontLabel) {
      const audTag = stem.includes("fem") ? "fem" : (stem.includes("inf") ? "inf" : "masc");
      if (seenPureFrontMockup.has(audTag) && rawDeduped.length >= 1) {
        return;
      }
      seenPureFrontMockup.add(audTag);
    }

    seenKeys.add(stem);
    rawDeduped.push(cleanU);
  });

  // Camada 4: Contingência Estrutural productOnChannel (ERP envia 1ª foto isolada + lote com 1ª foto repetida com UUID)
  if (rawDeduped.length >= 3 && !isMultiColorProduct) {
    const pocGroups = rawDeduped.map(u => {
      const m = u.match(/productOnChannel(?:_2F|\/)images(?:_2F|\/)([^\/_?]+)/i);
      return m ? m[1].toLowerCase() : null;
    });
    if (pocGroups[0] && pocGroups[1] && pocGroups[0] !== pocGroups[1]) {
      const groupCounts = {};
      pocGroups.forEach(g => { if (g) groupCounts[g] = (groupCounts[g] || 0) + 1; });
      if (groupCounts[pocGroups[0]] === 1 && (groupCounts[pocGroups[1]] || 0) >= 2) {
        const fname1 = rawDeduped[1].split("?")[0].split("/").pop();
        const fname2 = rawDeduped[2].split("?")[0].split("/").pop();
        if (uuidRe.test(fname1) && !uuidRe.test(fname2)) {
          rawDeduped.splice(1, 1);
        }
      } else if (groupCounts[pocGroups[0]] === 1 && groupCounts[pocGroups[1]] === 1) {
        const keep = [rawDeduped[0]];
        let idx = 1;
        while (idx < rawDeduped.length && pocGroups[idx] && groupCounts[pocGroups[idx]] === 1) {
          idx++;
        }
        if (idx < rawDeduped.length) {
          keep.push(...rawDeduped.slice(idx));
          rawDeduped.length = 0;
          rawDeduped.push(...keep);
        }
      }
    }
  }

  const nonBanner = rawDeduped.filter(u => !u.toLowerCase().includes("catalogobrkfishing_iscapremiumemdetalhes"));
  let images = nonBanner.length >= 3 ? nonBanner : rawDeduped;
  const bannerTokens = [
    "capacategoria", "prancheta_1_copiar", "versao3", "diferencialuv",
    "diferencialtela", "guia-de-tamanhos", "star-feminino", "dfubcro", "mqlxrlf"
  ];
  const realPhotos = images.filter(u => !bannerTokens.some(tok => u.toLowerCase().includes(tok)));
  const infoBanners = images.filter(u => bannerTokens.some(tok => u.toLowerCase().includes(tok)));
  if (realPhotos.length > 0 && infoBanners.length > 0) {
    images = [...realPhotos, ...infoBanners];
  }
  return images;
}

function buildClientSchemaJsonLd(liveP) {
  const originInfo = resolveClientOriginAndTitle(liveP);
  const formattedTitle = liveP.formatted_title || originInfo.formattedTitle;
  const brandName = liveP.brand_name || originInfo.brandName;
  const sku = liveP.master_sku || liveP.sku || liveP.id || "";
  const rawPrice = String(liveP.price || (liveP.variants && liveP.variants[0] && liveP.variants[0].price) || "0.00");
  let cleanPrice = rawPrice.replace(/[^\d,.]/g, "").trim();
  if (cleanPrice.includes(",") && cleanPrice.includes(".")) {
    cleanPrice = cleanPrice.replace(/\./g, "").replace(",", ".");
  } else if (cleanPrice.includes(",")) {
    cleanPrice = cleanPrice.replace(",", ".");
  }
  const price = cleanPrice || "0.00";

  const rawImgs = (liveP.cdn_images && liveP.cdn_images.length > 0)
    ? liveP.cdn_images
    : (liveP.gallery && liveP.gallery.length > 0)
      ? liveP.gallery
      : (liveP.images || []);
  const images = sanitizeAndDedupClientImages(rawImgs, liveP.archetype_id, liveP.title).slice(0, 3);

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

function buildClientCapOrHatHtml(liveP, archetypeId) {
  const originInfo = resolveClientOriginAndTitle(liveP);
  const formattedTitle = liveP.formatted_title || originInfo.formattedTitle || liveP.title || "Boné BRK";
  const sku = liveP.sku || liveP.master_sku || "";
  const stKey = liveP.store_key || (typeof currentStore !== "undefined" ? currentStore : "brk_fishing");
  const schemaJsonLd = buildClientSchemaJsonLd(liveP);

  let gradHoriz, gradVert, colorAccent, brandLabel;
  if (stKey === "brk_agro") {
    gradHoriz = "linear-gradient(90deg, #15803d, #ca8a04)";
    gradVert = "linear-gradient(180deg, #15803d, #ca8a04)";
    colorAccent = "#15803d";
    brandLabel = "BRK Agro";
  } else if (stKey === "brk_motors") {
    gradHoriz = "linear-gradient(90deg, #ea580c, #dc2626)";
    gradVert = "linear-gradient(180deg, #ea580c, #dc2626)";
    colorAccent = "#ea580c";
    brandLabel = "BRK Motors";
  } else {
    gradHoriz = "linear-gradient(90deg, #00a8ff, #00d084)";
    gradVert = "linear-gradient(180deg, #00a8ff, #00d084)";
    colorAccent = "#00a8ff";
    brandLabel = "BRK Fishing";
  }

  let details = [];
  let caractTitle = "";
  let caractItems = [];
  let cuidadosTitle = "";
  let cuidadosItems = [];
  let split1_p1, split1_p2, split1_p3, split2_p1, split2_p2, split2_p3;

  const titleLow = formattedTitle.toLowerCase();
  const rawImgs = (liveP.cdn_images && liveP.cdn_images.length > 0) ? liveP.cdn_images : (liveP.gallery || liveP.images || []);
  const galleryUrls = sanitizeAndDedupClientImages(rawImgs, archetypeId, formattedTitle);
  const nonPng = galleryUrls.filter(u => !String(u).toLowerCase().split("?")[0].endsWith(".png"));
  const hwPool = nonPng.length >= 4 ? nonPng : (nonPng.length > 0 ? [...nonPng, ...galleryUrls.filter(u => !nonPng.includes(u))] : galleryUrls);
  const img1 = hwPool[0] || "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg";
  const img2 = hwPool[1] || (hwPool.length === 0 ? "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg" : "");
  const img3 = hwPool[2] || (hwPool.length === 0 ? "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg" : "");
  const img4 = hwPool[3] || (hwPool.length === 0 ? "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg" : "");

  if (archetypeId === "caps_trucker_snapback") {
    const is6Gomos = titleLow.includes("6 gomos") || titleLow.includes("seis gomos");
    const copaBullet = is6Gomos
      ? "Copa estruturada de 6 gomos fechada em tecido camuflado, com frente firme e ilhoses bordados que favorecem a ventilação."
      : "Copa estruturada estilo trucker, com frente firme e tela traseira que favorece a ventilação.";

    let capTheme = stKey;
    if (["fishing", "pesca", "robalo", "tucunar", "tambaqui", "traira", "traíra", "dourado", "pirarara", "red tail", "black bass"].some(w => titleLow.includes(w))) {
      capTheme = "brk_fishing";
    } else if (["agro", "peacemaker", "country", "texas", "bull", "nelore", "fazenda", "sertanejo"].some(w => titleLow.includes(w))) {
      capTheme = "brk_agro";
    } else if (["motors", "racing", "off-road", "off road", "motocross", "trilha"].some(w => titleLow.includes(w))) {
      capTheme = "brk_motors";
    }

    let exclusiveDesc = "Arte exclusiva inspirada no lifestyle BRK, combinando atitude e identidade visual marcante.";
    if (capTheme === "brk_fishing") {
      exclusiveDesc = "Arte exclusiva BRK Fishing inspirada na pesca esportiva, para você se destacar dentro e fora da água.";
    } else if (capTheme === "brk_agro") {
      exclusiveDesc = "Arte exclusiva BRK Agro inspirada no campo e no agronegócio, para você se destacar em qualquer ambiente.";
    } else if (capTheme === "brk_motors") {
      exclusiveDesc = "Arte exclusiva BRK Motors inspirada na velocidade e no off-road, para você se destacar dentro e fora das pistas.";
    }

    details = [
      {
        img: img1,
        alt: `Aba do boné ${formattedTitle} com costuras reforçadas e estrutura moldável`,
        title: "Aba Moldável",
        desc: "Aba estruturada com diversas costuras e moldável, garantindo durabilidade e proteção extra contra o sol."
      },
      {
        img: img2,
        alt: `Parte interna do boné ${formattedTitle} com costuras em tear`,
        title: "Interno em Tear",
        desc: capTheme === "brk_fishing"
          ? "Acabamento interno em tear com costuras reforçadas, pensado para aguentar longas jornadas de pesca."
          : "Acabamento interno em tear com costuras reforçadas, pensado para aguentar longas jornadas de uso contínuo."
      },
      {
        img: img3,
        alt: `Etiqueta BRK de qualidade aplicada no boné ${formattedTitle}`,
        title: "Etiqueta BRK de Qualidade",
        desc: "Etiqueta BRK aplicada com acabamento premium, garantindo autenticidade e padrão de qualidade."
      },
      {
        img: img4,
        alt: `Design exclusivo do boné ${formattedTitle}`,
        title: "Design Exclusivo",
        desc: exclusiveDesc
      }
    ];
    caractTitle = "Características do Boné BRK";
    caractItems = [
      copaBullet,
      "Aba moldável com costuras reforçadas, oferecendo conforto e proteção para o rosto e os olhos.",
      "Tamanho único com regulagem traseira, se ajustando à maioria dos formatos de cabeça.",
      capTheme === "brk_agro"
        ? "Ideal para o campo, atividades ao ar livre e uso no dia a dia."
        : (capTheme === "brk_motors"
          ? "Ideal para trilha, velocidade, eventos automotivos e uso no dia a dia."
          : "Ideal para pesca esportiva, atividades ao ar livre e uso no dia a dia."),
      capTheme === "brk_fishing"
        ? "Acabamento interno pensado para máximo conforto mesmo em longas jornadas de pesca."
        : (capTheme === "brk_agro"
          ? "Acabamento interno pensado para máximo conforto mesmo em longas jornadas de trabalho."
          : "Acabamento interno pensado para máximo conforto mesmo em longas jornadas.")
    ];
    cuidadosTitle = "Cuidados com o Seu Boné";
    cuidadosItems = [
      "Não lave o boné na máquina e não utilize água quente.",
      "Para limpeza, use um pano úmido com sabão neutro nas áreas sujas.",
      "Retire o excesso de sabão com outro pano levemente úmido.",
      "Deixe secar à sombra, em superfície plana, longe de fontes de calor.",
      "Não utilize alvejante, não passe a ferro e não leve à secadora."
    ];

    if (capTheme === "brk_fishing") {
      split1_p1 = "Cada boné BRK é desenvolvido pensando no pescador que vive a pesca esportiva intensamente.";
      split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance.";
      split1_p3 = "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo em qualquer pescaria.";
      split2_p1 = "A sua experiência começa antes mesmo de abrir a caixa.";
      split2_p2 = "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições.";
      split2_p3 = "Assim, seu novo boné de pesca chega pronto para encarar a próxima aventura, seja na beira do rio, na represa ou em alto mar.";
    } else if (capTheme === "brk_agro") {
      split1_p1 = "Cada boné BRK é desenvolvido pensando em quem vive a vida no campo intensamente.";
      split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance.";
      split1_p3 = "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo no campo ou na cidade.";
      split2_p1 = "A sua experiência começa antes mesmo de abrir a caixa.";
      split2_p2 = "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições.";
      split2_p3 = "Assim, seu novo boné chega pronto para encarar a lida na fazenda, feiras agropecuárias ou eventos sertanejos.";
    } else if (capTheme === "brk_motors") {
      split1_p1 = "Cada boné BRK é desenvolvido pensando no piloto e entusiasta que vive a velocidade intensamente.";
      split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance.";
      split1_p3 = "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo em qualquer aventura sobre rodas.";
      split2_p1 = "A sua experiência começa antes mesmo de abrir a caixa.";
      split2_p2 = "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições.";
      split2_p3 = "Assim, seu novo boné chega pronto para encarar a próxima trilha, viagem ou pista com atitude e proteção.";
    } else {
      split1_p1 = "Cada boné BRK é desenvolvido pensando em quem vive a vida ao ar livre intensamente.";
      split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item original e de alta performance.";
      split1_p3 = "Da escolha dos tecidos ao acabamento das costuras, tudo é pensado para entregar conforto e estilo na aventura ou no dia a dia.";
      split2_p1 = "A sua experiência começa antes mesmo de abrir a caixa.";
      split2_p2 = "O boné é enviado em embalagem protegida e personalizada BRK, pensada para que ele chegue impecável até você, sem amassar e pronto para o uso.";
      split2_p3 = "Assim, seu novo boné chega pronto para encarar a próxima aventura, seja no campo, na pista ou nas águas.";
    }
  } else if (archetypeId === "hats_safari_outdoor") {
    if (["juta", "bambu", "palha"].some(w => titleLow.includes(w))) {
      details = [
        {
          img: img1,
          alt: `Trama natural em juta e palha de bambu do chapéu ${formattedTitle}`,
          title: "Trama em Juta & Bambu",
          desc: "Trançado nobre em fibras selecionadas de juta e palha de bambu que proporciona ventilação natural constante e leveza superior."
        },
        {
          img: img2,
          alt: `Bandinha personalizada BRK Agro com fivela metálica do chapéu ${formattedTitle}`,
          title: "Bandinha BRK Agro Exclusiva",
          desc: "Acabamento externo em fita caramelo personalizada BRK Agro com fivela metálica lateral, conferindo identidade autêntica do campo."
        },
        {
          img: img3,
          alt: `Copa e aba estruturadas com viés protetor do chapéu ${formattedTitle}`,
          title: "Copa & Aba Estruturadas",
          desc: "Modelagem clássica com copa bem definida e aba ampla finalizada com viés de proteção nas bordas para excelente cobertura solar."
        },
        {
          img: img4,
          alt: `Carneira interna confortável do chapéu ${formattedTitle}`,
          title: "Carneira Interna Confortável",
          desc: "Faixa interna macia e anatômica que garante encaixe firme e estável na cabeça ao longo de todo o dia."
        }
      ];
      caractTitle = "Características do Chapéu BRK Agro Juta & Bambu";
      caractItems = [
        "Confeccionado em trama selecionada de juta e palha de bambu altamente respirável.",
        "Aba estruturada com acabamento em viés nas bordas para proteção solar no campo e lazer.",
        "Bandinha externa personalizada BRK Agro em tom caramelo com fivela metálica.",
        "Carneira interna macia que proporciona ajuste confortável e seguro na cabeça.",
        "Ideal para dias de sol na fazenda, feiras agropecuárias, encontros sertanejos e lazer ao ar livre."
      ];
      cuidadosTitle = "Cuidados com o Seu Chapéu de Fibra Natural";
      cuidadosItems = [
        "Limpar delicadamente com pano seco ou escova de cerdas macias.",
        "Não lavar em água, não submergir e não utilizar máquina de lavar.",
        "Evitar exposição à chuva intensa ou ambientes úmidos fechados.",
        "Caso receba respingos leves, deixe secar naturalmente à sombra em local arejado.",
        "Guardar sempre apoiado pela copa ou em suporte próprio para preservar a aba estruturada."
      ];
      split1_p1 = "Estilo autêntico do campo aliado ao frescor das fibras naturais.";
      split1_p2 = "O Chapéu BRK Agro Juta Palha de Bambu Premium foi desenvolvido para quem valoriza elegância rústica, conforto térmico e acabamento impecável.";
      split1_p3 = "Cada detalhe — da trama ventilada à bandinha exclusiva BRK Agro — entrega presença marcante e bem-estar sob o sol.";
      split2_p1 = "Embalagem protetora pensada para preservar o formato original.";
      split2_p2 = "O chapéu é enviado em caixa reforçada BRK, projetada para proteger a copa e a aba durante todo o transporte.";
      split2_p3 = "Assim, seu novo chapéu chega impecável e pronto para acompanhar você na fazenda, nos eventos ou no lazer.";
    } else {
      details = [
        {
          img: img1,
          alt: `Aba 360° com proteção solar do chapéu ${formattedTitle}`,
          title: "Aba 360° UV50+",
          desc: "Aba circular ampla com costuras reforçadas, bloqueando os raios solares diretos no rosto, orelhas e pescoço com máxima cobertura."
        },
        {
          img: img2,
          alt: `Cordão jugular com trava anti-vento do chapéu ${formattedTitle}`,
          title: "Cordão Jugular Anti-Vento",
          desc: "Ajuste seguro sob o queixo com trava regulável, mantendo o chapéu firme mesmo sob rajadas de vento e navegação rápida."
        },
        {
          img: img3,
          alt: `Protetor de nuca e acabamento do chapéu ${formattedTitle}`,
          title: "Protetor de Nuca Integrado",
          desc: "Cobertura estendida para a nuca que previne queimaduras solares durante longas jornadas sob sol intenso."
        },
        {
          img: img4,
          alt: `Tecido leve e respirável do chapéu ${formattedTitle}`,
          title: "Tecido Respirável & Leve",
          desc: "Construção de secagem rápida com ilhoses de ventilação lateral para dissipação imediata de calor e sensação de frescor contínuo."
        }
      ];
      caractTitle = "Características do Chapéu Safári BRK";
      caractItems = [
        "Copa anatômica com ilhoses laterais que garantem circulação de ar constante.",
        "Aba larga circular de 360° com fator de proteção UV50+ permanente.",
        "Cordão jugular com trava ajustável de segurança contra quedas e vento forte.",
        "Protetor de nuca para proteção solar total na região posterior do pescoço.",
        "Tecido tecnológico leve de secagem ultra rápida e alta resistência ao desgaste."
      ];
      cuidadosTitle = "Cuidados com o Seu Chapéu";
      cuidadosItems = [
        "Lavar à mão com água fria e sabão neutro.",
        "Não lavar em máquina e não torcer para preservar a estrutura da aba.",
        "Secar estendido à sombra em superfície plana.",
        "Não usar alvejantes, amaciantes ou produtos à base de cloro.",
        "Guardar sem dobrar a aba estruturada para manter o caimento original."
      ];
      split1_p1 = "Cada chapéu BRK é desenvolvido pensando na proteção de quem enfrenta longas jornadas ao ar livre.";
      split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem padrão de proteção solar certificado.";
      split1_p3 = "Construído com materiais leves e resistentes, oferece o máximo de conforto térmico para pescarias e trabalho sob sol forte.";
      split2_p1 = "A sua experiência começa antes mesmo de abrir a caixa.";
      split2_p2 = "O chapéu é enviado em embalagem protegida BRK, projetada para evitar deformações na aba durante o transporte.";
      split2_p3 = "Seu novo chapéu chega pronto para encarar o sol com proteção e estilo incomparáveis.";
    }
  } else {
    const isStrawCountry = ["bozeman", " cal", "palha"].some(w => titleLow.includes(w));

    details = [
      {
        img: img1,
        alt: `Aba larga estruturada do chapéu ${formattedTitle}`,
        title: "Aba Larga Estruturada",
        desc: "Formato clássico western com curvatura marcante e acabamento impecável, unindo tradição, imponência e proteção solar no campo."
      },
      {
        img: img2,
        alt: `Carneira interna do chapéu ${formattedTitle}`,
        title: "Carneira Interna Confortável",
        desc: "Faixa interna com toque macio e anatômico, oferecendo fixação firme e confortável na cabeça sem marcar a testa."
      },
      {
        img: img3,
        alt: `Fita decorativa e acabamento do chapéu ${formattedTitle}`,
        title: "Fita & Acabamento Premium",
        desc: "Bandinha externa clássica com fivela, passador e ponteira metálica trabalhada, reforçando a autenticidade western."
      },
      {
        img: img4,
        alt: `Estrutura de alta densidade do chapéu ${formattedTitle}`,
        title: isStrawCountry ? "Copa Ventilada em Palha Nobre" : "Feltro Country de Alta Densidade",
        desc: isStrawCountry
          ? "Trama firme em fibra nobre com microperfurações na copa que favorecem a ventilação térmica mantendo a estrutura impecável."
          : "Feltro encorpado de alta densidade que preserva os vincos da copa Cattleman e a curvatura da aba mesmo com uso contínuo."
      }
    ];
    caractTitle = "Características do Chapéu Country";
    caractItems = [
      isStrawCountry
        ? "Copa alta estruturada em palha/fibra nobre com trama ventilada no legítimo estilo western."
        : "Copa alta estruturada em feltro encorpado moldado no legítimo estilo Cattleman / Western.",
      "Aba larga de presença marcante que proporciona excelente sombra e proteção.",
      "Carneira interna acolchoada para conforto prolongado em cavalgadas e eventos.",
      "Bandinha externa com conjunto de fivela metálica e identidade autêntica do campo.",
      "Ideal para rodeios, feiras agropecuárias, lida na fazenda e dia a dia sertanejo."
    ];
    cuidadosTitle = "Cuidados & Conservação do Chapéu";
    cuidadosItems = [
      "Limpar delicadamente com escova de cerdas macias sempre no sentido da trama ou das fibras.",
      "Evitar contato direto com chuva intensa ou umidade excessiva.",
      "Armazenar sempre apoiado pela copa ou em suporte adequado para não desformar a aba.",
      "Nunca dobrar, amassar ou deixar exposto no interior de veículos sob sol forte.",
      "Em caso de umidade leve, deixe secar naturalmente à sombra em local ventilado."
    ];
    split1_p1 = "A tradição e o orgulho do campo em cada detalhe artesanal.";
    split1_p2 = "Cada chapéu é selecionado para entregar autenticidade, robustez e elegância para os amantes do estilo country.";
    split1_p3 = "Acabamento primoroso que valoriza a cultura sertaneja e a presença marcante onde quer que você esteja.";
    split2_p1 = "Embalagem especial anti-deformação.";
    split2_p2 = "O chapéu é embalado em caixa reforçada para garantir que a copa e a aba cheguem impecáveis e sem amassados.";
    split2_p3 = "Pronto para usar na lida, nas cavalgadas ou nos grandes eventos do agronegócio.";
  }

  let radialColor = "rgba(0, 168, 255, 0.15)";
  if (stKey === "brk_agro") {
    radialColor = "rgba(21, 128, 61, 0.15)";
  } else if (stKey === "brk_motors") {
    radialColor = "rgba(234, 88, 12, 0.15)";
  }

  const detailsMarkup = details.map(d => {
    const safeAlt = String(d.alt || "").replace(/"/g, "&quot;");
    const imgDiv = d.img ? `        <div class="brk-cap-detail-image"><img src="${d.img}" alt="${safeAlt}"></div>\n` : "";
    return `      <!-- ${d.title} -->
      <article class="brk-cap-detail-item">
${imgDiv}        <h3>${d.title}</h3>
        <p>${d.desc}</p>
      </article>`;
  }).join("\n");

  const caractLi = caractItems.map(item => `            <li>${item}</li>`).join("\n");
  const cuidadosLi = cuidadosItems.map(item => `            <li>${item}</li>`).join("\n");

  const svgSparkle = getSvgIcon("sparkle", colorAccent, 36);
  const svgCare = getSvgIcon("care", colorAccent, 36, "brk-cap-info-icon--care");

  const trackingMarker = `<!-- BRK-MODO-B v1 | sku:${(sku || "").replace(/[^A-Za-z0-9_.-]/g, "").slice(0, 60)} | molde:${archetypeId} -->`;

  return `${trackingMarker}
${schemaJsonLd}
<style>
  .brk-cap-description {
    font-family: inherit;
    color: #222222;
    line-height: 1.5;
    font-size: 15px;
  }

  .brk-cap-description * {
    box-sizing: border-box;
  }

  .brk-cap-section {
    margin: 24px 0;
  }

  .brk-cap-section-header {
    text-align: center;
    margin-bottom: 18px;
  }

  .brk-cap-section-title {
    display: inline-block;
    font-size: 20px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    position: relative;
    padding-bottom: 6px;
  }

  .brk-cap-section-title::after {
    content: "";
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 0;
    width: 42px;
    height: 3px;
    border-radius: 999px;
    background: ${gradHoriz};
  }

  /* DETALHES – GRID DE IMAGENS 260x260 + TEXTO */
  .brk-cap-details-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 16px;
  }

  .brk-cap-detail-item {
    text-align: center;
    max-width: 260px;
    flex: 1 1 220px;
  }

  .brk-cap-detail-image {
    width: 100%;
    max-width: 260px;
    margin: 0 auto 8px;
  }

  .brk-cap-detail-image img {
    display: block;
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
    border-radius: 12px;
  }

  .brk-cap-detail-item h3 {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    margin: 6px 0 4px;
    letter-spacing: 0.04em;
  }

  .brk-cap-detail-item p {
    font-size: 13px;
    margin: 0;
    color: #555555;
  }

  /* INFORMAÇÕES – CARDS SUTIS + LISTA COM QUADRADOS + SVG NO TÍTULO */
  .brk-cap-info-wrapper {
    display: grid;
    grid-template-columns: minmax(0, 1.25fr);
    gap: 20px;
  }

  .brk-cap-info-block {
    padding: 16px 18px 18px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.05);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
  }

  .brk-cap-info-title {
    position: relative;
    display: inline-block;
    padding: 4px 0;
    margin-bottom: 10px;
  }

  .brk-cap-info-title h3 {
    font-size: 15px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0;
    position: relative;
    z-index: 1;
  }

  .brk-cap-info-title svg {
    position: absolute;
    left: -10px;
    top: -8px;
    width: 44px;
    height: 44px;
    opacity: 0.18;
    z-index: 0;
  }

  .brk-cap-info-icon--care {
    transform: translateX(-4px);
  }

  .brk-cap-info-list {
    margin: 4px 0 0;
    padding: 0;
  }

  .brk-cap-info-block ul {
    margin: 0;
    padding-left: 0;
    list-style: none;
  }

  .brk-cap-info-block li {
    position: relative;
    padding-left: 20px;
    margin-bottom: 6px;
    font-size: 14px;
  }

  .brk-cap-info-block li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 6px;
    width: 9px;
    height: 9px;
    border-radius: 3px;
    background: ${gradHoriz};
  }

  @media (min-width: 900px) {
    .brk-cap-info-block ul {
      column-count: 2;
      column-gap: 28px;
    }

    .brk-cap-info-block li {
      break-inside: avoid;
    }
  }

  /* SEÇÕES DIVIDIDAS (IMAGEM + TEXTO) */
  .brk-cap-split-sections {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .brk-cap-split {
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .brk-cap-split.reverse {
    flex-direction: row-reverse;
  }

  .brk-cap-split-image {
    flex: 1 1 50%;
    max-width: 450px;
    border-radius: 18px;
    overflow: hidden;
    background: radial-gradient(circle at top left, ${radialColor}, transparent 55%);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
  }

  .brk-cap-split-image img {
    display: block;
    width: 100%;
    height: auto;
  }

  .brk-cap-split-content {
    flex: 1 1 50%;
    position: relative;
    padding-left: 18px;
  }

  .brk-cap-split.reverse .brk-cap-split-content {
    padding-left: 0;
    padding-right: 18px;
  }

  /* Barrinha vertical atrás de todo o texto */
  .brk-cap-split-content::before {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 3px;
    border-radius: 999px;
    background: ${gradVert};
    left: 0;
  }

  .brk-cap-split.reverse .brk-cap-split-content::before {
    left: auto;
    right: 0;
  }

  .brk-cap-split-content h2 {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .brk-cap-split-content p {
    margin: 0 0 4px;
    font-size: 14px;
  }

  /* RESPONSIVIDADE */
  @media (max-width: 768px) {
    .brk-cap-details-grid {
      justify-content: center;
    }

    .brk-cap-detail-item {
      flex: 1 1 45%;
      max-width: 220px;
    }

    .brk-cap-split,
    .brk-cap-split.reverse {
      flex-direction: column;
    }

    .brk-cap-split-image,
    .brk-cap-split-content {
      flex: 1 1 100%;
      max-width: 100%;
      width: 100%;
    }

    .brk-cap-split-content {
      padding-left: 14px;
    }

    .brk-cap-split.reverse .brk-cap-split-content {
      padding-right: 0;
      padding-left: 14px;
    }

    .brk-cap-split.reverse .brk-cap-split-content::before {
      right: auto;
      left: 0;
    }
  }

  @media (max-width: 480px) {
    .brk-cap-detail-item {
      flex: 1 1 100%;
      max-width: 260px;
    }
  }
</style>
<div class="brk-cap-description">
  <!-- SEÇÃO DETALHES -->
  <section class="brk-cap-section brk-cap-details">
    <header class="brk-cap-section-header">
      <h2 class="brk-cap-section-title">Detalhes</h2>
    </header>
    <div class="brk-cap-details-grid">
${detailsMarkup}
    </div>
  </section>

  <!-- SEÇÃO INFORMAÇÕES -->
  <section class="brk-cap-section brk-cap-information">
    <header class="brk-cap-section-header">
      <h2 class="brk-cap-section-title">Informações</h2>
    </header>
    <div class="brk-cap-info-wrapper">
      <!-- BLOCO 1: CARACTERÍSTICAS -->
      <div class="brk-cap-info-block">
        <div class="brk-cap-info-title">
          ${svgSparkle}
          <h3>${caractTitle}</h3>
        </div>
        <div class="brk-cap-info-list">
          <ul>
${caractLi}
          </ul>
        </div>
      </div>

      <!-- BLOCO 2: CUIDADOS -->
      <div class="brk-cap-info-block">
        <div class="brk-cap-info-title">
          ${svgCare}
          <h3>${cuidadosTitle}</h3>
        </div>
        <div class="brk-cap-info-list">
          <ul>
${cuidadosLi}
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- SEÇÕES IMAGEM + TEXTO -->
  <section class="brk-cap-section brk-cap-split-sections">
    <!-- 1ª seção: Etiquetas BRK (FOTO -> TEXTO) -->
    <div class="brk-cap-split">
      <div class="brk-cap-split-image">
        <img src="https://cdn.shopify.com/s/files/1/0628/1445/3826/files/13-Tags.webp?v=1785788893" alt="Etiquetas BRK aplicadas em produtos originais">
      </div>
      <div class="brk-cap-split-content">
        <h2>PRODUTO PREMIUM BRK</h2>
        <p><strong>${split1_p1}</strong></p>
        <p>${split1_p2}</p>
        <p>${split1_p3}</p>
      </div>
    </div>

    <!-- 2ª seção: Caixa / Entrega (TEXTO <- FOTO) -->
    <div class="brk-cap-split reverse">
      <div class="brk-cap-split-image">
        <img src="https://cdn.shopify.com/s/files/1/0628/1445/3826/files/CAIXA-BRK.webp?v=1785788895" alt="Caixa personalizada BRK para envio seguro">
      </div>
      <div class="brk-cap-split-content">
        <h2>ENTREGA SEGURA BRK</h2>
        <p><strong>${split2_p1}</strong></p>
        <p>${split2_p2}</p>
        <p>${split2_p3}</p>
      </div>
    </div>
  </section>
</div>`;
}

const EXPLICIT_BACK_POC_HASHES = [
  "7b19cafab14e", "e2f62ee973da", "387e870f3379", "7bdc66337bfe",
  "b4b1be48b687", "028bb8fdcfd5", "fff9408f57fe", "b01708bd7eea",
  "0855ecb1a641", "61d791ea91ca", "ee825cc65556", "e8f232579489",
  "c4773979284d", "3b4aba35b3d2", "0c83e30f278a", "22311f856466",
  "2320ad7a784d", "8da0d64f829c", "9656ca14524e", "33beb817c568",
  "7b1e90ac1efc", "71b9cbecac2a", "c06bcd092644", "6f84821f7619",
  "236b64bb841b", "0721a4c8ce17", "82bf06e5656d", "086u9hh",
  "4ad9fc8f16bc", "94a3b81f5954", "73591bff33b1", "32165d82a90b",
  "fcb50f9e02ac", "b3e2c7dc24a2", "c8a91438bfdd", "e5092aceccc3",
  "2339b90698f3", "84a9e29f3d47", "0a5de4344adb", "c02837bl.webp"
];

function isClientBackViewUrl(url, include03 = false) {
  if (!url || typeof url !== "string") return false;
  const uLow = url.toLowerCase();
  const fname = uLow.split("/").pop().split("?")[0];
  if (fname.startsWith("02_1918aa2d") || fname.includes("zoom") || fname.includes("2-capa") || fname.includes("capa-2")) {
    return false;
  }
  if (fname.includes("productonchannel")) {
    return EXPLICIT_BACK_POC_HASHES.some(h => fname.includes(h));
  }
  if (EXPLICIT_BACK_POC_HASHES.some(h => fname.includes(h))) return true;
  const fnameNoTs = fname.replace(/(?:^|[_.\-\s])\d{2}_\d{2}_\d{2}(?=[_.\-\s]|$)/g, "");
  if (fnameNoTs.includes("frente") || fnameNoTs.includes("mkpmaopunho")) return false;
  const keywords = [
    "costas", "costa", "back", "traseira", "verso", "tras",
    "02fem", "02masc", "02inf", "02_fem", "02_masc", "02_inf",
    "2fem", "2masc", "2inf", "2-fem", "2-masc", "2-inf", "2_fem", "2_masc", "2_inf"
  ];
  if (keywords.some(w => fnameNoTs.includes(w))) return true;
  if (["-brk-agro-", "-brk-fishing-", "-brk-motors-", "camisa-agro-", "camisa-de-pesca-", "camisa-pesca-"].some(k => fnameNoTs.includes(k))) {
    return false;
  }
  return /(?:^|[-_.\s])(2|02|b)(?:[-_.\s]|masc|fem|inf|kids|bl|$)/i.test(fnameNoTs);
}

function isClientExplicitBackName(url) {
  if (!url || typeof url !== "string") return false;
  const fname = url.toLowerCase().split("/").pop().split("?")[0];
  if (fname.startsWith("02_1918aa2d") || fname.includes("zoom") || fname.includes("2-capa") || fname.includes("capa-2")) {
    return false;
  }
  if (fname.includes("productonchannel")) {
    return EXPLICIT_BACK_POC_HASHES.some(h => fname.includes(h));
  }
  if (EXPLICIT_BACK_POC_HASHES.some(h => fname.includes(h))) return true;
  if (fname.includes("frente") || fname.includes("mkpmaopunho")) return false;
  const keywords = [
    "costas", "costa", "back", "traseira", "verso", "tras",
    "02fem", "02masc", "02inf", "02_fem", "02_masc", "02_inf",
    "02_", "-02."
  ];
  if (keywords.some(w => fname.includes(w))) return true;
  return /(?:^|[-_.\s])0?2[-_]?(?:fem|masc|inf)/i.test(fname);
}

function selectClientApparelActImages(cdnImages, isFemale = false, isKids = false, sku = "", title = "") {
  if (!cdnImages || cdnImages.length === 0) return ["", "", ""];
  if (cdnImages.length === 1) return [cdnImages[0], "", ""];

  if (cdnImages.length >= 3 && cdnImages[0].toLowerCase().includes("01_masc") && cdnImages[1].toLowerCase().includes("10inf")) {
    return [cdnImages[0], cdnImages[1], cdnImages[2]];
  }

  const classifyImgAudience = (u) => {
    const fname = (u || "").toLowerCase().split("?")[0].split("/").pop();
    const hasMasc = ["masc", "man2", "homem"].some(k => fname.includes(k)) || /^(?:casual|c0|cm)\d+(?:pp|p|m|g|gg|xg|xgg|g1|g2|g3)(?:[-_.\d]|$)/i.test(fname);
    const hasFem = ["fem", "mulher"].some(k => fname.includes(k)) || /(?:^|[-_.\d])bl(?:[-_.\d]|$)/i.test(fname) || /^(?:casual|c0|cf|cm)\d+bl/i.test(fname);
    const hasInf = ["inf", "kids", "crianca", "juvenil"].some(k => fname.includes(k)) || /^(?:casual|c0|cm)\d+i(?:pp|p|m|g|gg|g1|g2|\d+)?(?:[-_.\d]|$)/i.test(fname);
    const onlyMasc = hasMasc && !hasFem && !hasInf;
    const onlyFem = hasFem && !hasMasc && !hasInf;
    const onlyInf = hasInf && !hasMasc && !hasFem;
    return { hasMasc, hasFem, hasInf, onlyMasc, onlyFem, onlyInf };
  };

  let workingImages = [...cdnImages];
  if (isKids || isFemale || cdnImages.some(u => { const c = classifyImgAudience(u); return c.onlyMasc || c.onlyFem || c.onlyInf; })) {
    const preferred = [];
    const compatible = [];
    cdnImages.forEach(u => {
      const { hasMasc, hasFem, hasInf, onlyMasc, onlyFem, onlyInf } = classifyImgAudience(u);
      if (isKids) {
        if (hasInf) preferred.push(u);
        if (!onlyMasc && !onlyFem) compatible.push(u);
      } else if (isFemale) {
        if (hasFem) preferred.push(u);
        if (!onlyMasc && !onlyInf) compatible.push(u);
      } else {
        if (hasMasc) preferred.push(u);
        if (!onlyFem && !onlyInf) compatible.push(u);
      }
    });

    if (compatible.length < cdnImages.length) {
      if (preferred.length >= 1 && preferred.length <= 2 && cdnImages.length >= 3) {
        const p0 = preferred[0];
        const neutralCands = compatible.filter(u => !preferred.includes(u));
        if (neutralCands.length === 0) {
          return [p0, preferred.length === 2 ? preferred[1] : "", ""];
        }
        const act1Img = neutralCands[0];
        const act2Img = preferred.length === 2 ? preferred[1] : (neutralCands.length > 1 ? neutralCands[1] : act1Img);
        return [act1Img, act2Img, p0];
      }
      const orderedCompatible = (compatible.length > 0 && compatible[0] === cdnImages[0])
        ? compatible
        : (preferred.length > 0 ? [...preferred, ...compatible.filter(u => !preferred.includes(u))] : compatible);
      if (orderedCompatible.length >= 3) {
        workingImages = orderedCompatible;
      } else if (orderedCompatible.length >= 1) {
        workingImages = orderedCompatible;
      }
    }
  }

  if (workingImages.length === 1) return [workingImages[0], "", ""];
  if (workingImages.length === 2) return [workingImages[0], workingImages[1], ""];

  const fnames = workingImages.map(u => (u || "").toLowerCase().split("?")[0].split("/").pop());
  const skuUp = (sku || "").trim().toUpperCase();
  const skuTLow = `${sku || ""} ${title || ""}`.toLowerCase();

  const matchExplicitStudioNum = (fnameStr) => {
    const mSt = fnameStr.match(/(?:^|\d{10,14}[-_]|[-_])(0?[1-9]|1[0-3])(?:[-_](?:20)?(?:masc|fem|inf|ffem)|masc|fem|inf|ffem)?(?:_\d)?(?:_(?:frente_costas|zoom_fem|zoom_masc|zoom))?(?:_[a-z0-9]{6})?(?:_[0-9a-f]{8}-[0-9a-f-]{27})?\.[a-z0-9]+$/i);
    return mSt ? parseInt(mSt[1], 10) : null;
  };

  const extractTs4 = (fnameStr) => {
    const mTs = fnameStr.match(/^(\d{4})\d{6,10}[-_]/);
    return mTs ? mTs[1] : "";
  };

  const ts0 = extractTs4(fnames[0]);
  const sameSet = (arr, target) => arr.length === target.length && target.every(v => arr.includes(v));

  // PILAR 1: GALERIAS COM 4 OU MAIS FOTOS
  if (workingImages.length >= 4) {
    if (fnames[0].startsWith("1780685222215")) {
      return [workingImages[2], workingImages[1], workingImages[0]];
    }
    if (fnames[1].includes("01_fem_frente_costas") && fnames[0].includes("02_fem")) {
      return [workingImages[0], workingImages[2], workingImages[3]];
    }
    if (fnames[1].includes("2-capa") || fnames[1].includes("capa-2")) {
      return [workingImages[0], workingImages[3], workingImages[2]];
    }
    if (skuUp.startsWith("C01824") || fnames.slice(1, 3).some(f => f.includes("gemini_generated_image"))) {
      return [workingImages[0], workingImages[1], workingImages[3]];
    }
    if (fnames[3].includes("03_zoom") || fnames[3].includes("04_zoom") || fnames[3].includes("11_zoom")) {
      return [workingImages[0], workingImages[1], workingImages[3]];
    }
    if (fnames[2].includes("zoom")) {
      return [workingImages[0], workingImages[1], workingImages[2]];
    }
    if (fnames[3].includes("zoom")) {
      return [workingImages[0], workingImages[2], workingImages[3]];
    }

    let seqMap = {};
    for (let idxU = 0; idxU < 4; idxU++) {
      const f = fnames[idxU];
      const stNum = matchExplicitStudioNum(f);
      if ([1, 2, 3, 4].includes(stNum) && !f.includes("frente_costas") && !f.includes("zoom")) {
        seqMap[stNum] = workingImages[idxU];
      }
    }
    if (![1, 2, 3, 4].every(k => seqMap[k])) {
      const gluedPrefixes = new Set();
      const gluedMap = {};
      for (let idxU = 0; idxU < 4; idxU++) {
        const mGl = fnames[idxU].match(/^((?:c0|casual|adv|cadv|fusion|hyb|cax|raglan)\d+(?:bl|i)?)([1234])\.[a-z0-9]+$/i);
        if (mGl) {
          gluedPrefixes.add(mGl[1]);
          gluedMap[parseInt(mGl[2], 10)] = workingImages[idxU];
        }
      }
      if (gluedPrefixes.size === 1 && [1, 2, 3, 4].every(k => gluedMap[k])) {
        seqMap = gluedMap;
      }
    }
    if ([1, 2, 3, 4].every(k => seqMap[k])) {
      const isCombo1234 = (
        skuUp.startsWith("CCPBR")
        || fnames[0].includes("ccpbr")
        || (ts0 === "1761" && (skuUp.startsWith("HYB") || skuTLow.includes("hyb")))
        || (
          !skuUp.startsWith("ADV")
          && (fnames[0].includes("01fem") || (fnames[0].includes("1fem") && !fnames[0].includes("1_fem")))
          && ["1744", "1746", "1750", "1755", "1757", "1758", "1760", "1762", "1764", "1768", "1770", "1772"].includes(ts0)
        )
        || fnames[0].startsWith("1790364852293")
        || fnames[0].startsWith("1790354628351")
      );
      if (isCombo1234) {
        return [seqMap[1], seqMap[3], seqMap[4]];
      }
      return [seqMap[1], seqMap[2], seqMap[3]];
    }

    const numsFirst4 = fnames.slice(0, 4).map(matchExplicitStudioNum);
    if (sameSet(numsFirst4, [1, 4, 5, 6])) {
      const sMap = {};
      numsFirst4.forEach((n, i) => { sMap[n] = workingImages[i]; });
      if (numsFirst4[0] === 5 || numsFirst4[0] === 6) {
        return [workingImages[0], sMap[4], sMap[1]];
      }
      return [sMap[1], sMap[4], sMap[5]];
    }
    if (sameSet(numsFirst4, [1, 2, 5, 6])) {
      const sMap = {};
      numsFirst4.forEach((n, i) => { sMap[n] = workingImages[i]; });
      if (numsFirst4[0] === 5 || numsFirst4[0] === 6) {
        return [workingImages[0], sMap[2], sMap[1]];
      }
      return [sMap[1], sMap[2], sMap[5]];
    }
    if (sameSet(numsFirst4, [1, 2, 4, 5])) {
      const sMap = {};
      numsFirst4.forEach((n, i) => { sMap[n] = workingImages[i]; });
      if (isFemale) {
        return [sMap[4], sMap[2], sMap[1]];
      }
      return [sMap[1], sMap[2], sMap[4]];
    }

    const n3Str = JSON.stringify(numsFirst4.slice(0, 3));
    if ((n3Str === "[1,2,3]" || n3Str === "[2,1,3]") && numsFirst4[3] === null && !isClientExplicitBackName(workingImages[3])) {
      return [workingImages[0], workingImages[2], workingImages[3]];
    }
    if (JSON.stringify(numsFirst4) === "[1,null,2,3]") {
      if (fnames[3].includes("03fem") || fnames[1].includes("fishing")) {
        return [workingImages[0], workingImages[3], workingImages[1]];
      }
      return [workingImages[0], workingImages[2], workingImages[3]];
    }
    if (fnames[3].includes("frente") && !fnames[3].includes("costas")) {
      if (isClientExplicitBackName(workingImages[0]) && fnames[2].includes("frente")) {
        return [workingImages[2], workingImages[0], workingImages[3]];
      }
      return [workingImages[0], workingImages[2], workingImages[3]];
    }

    const f0Num = numsFirst4[0];
    const restSeq = {};
    for (let idxU = 1; idxU < workingImages.length; idxU++) {
      const stNum = matchExplicitStudioNum(fnames[idxU]);
      if (stNum !== null && !(stNum in restSeq)) {
        restSeq[stNum] = workingImages[idxU];
      }
    }

    if (f0Num !== 1 && restSeq[1]) {
      if (fnames[0].includes("frente") && !fnames[0].includes("costas") && !isKids) {
        if (restSeq[3]) return [workingImages[0], restSeq[2] || workingImages[2], restSeq[3]];
        if (restSeq[5]) return [workingImages[0], restSeq[2] || workingImages[2], restSeq[5]];
      }
      let backCand = restSeq[2] || restSeq[3] || restSeq[4] || restSeq[9] || workingImages[2];
      if (backCand === restSeq[1]) {
        backCand = workingImages[1] !== restSeq[1] ? workingImages[1] : workingImages[2];
      }
      return [workingImages[0], backCand, restSeq[1]];
    }

    if (f0Num === null) {
      if (restSeq[5] && restSeq[6] && restSeq[7]) {
        if (restSeq[5].toLowerCase().includes("frente_costas")) {
          return [workingImages[0], restSeq[7], restSeq[6]];
        }
        return [workingImages[0], restSeq[6], restSeq[7]];
      }
      if (restSeq[6] && restSeq[7] && restSeq[8]) {
        return [workingImages[0], restSeq[7], restSeq[8]];
      }
      if (restSeq[7] && restSeq[8] && restSeq[9]) {
        if (fnames[0].startsWith("c0492bl") || fnames[0].startsWith("c02418bl")) {
          return [workingImages[0], restSeq[9], restSeq[8]];
        }
        return [workingImages[0], restSeq[8], restSeq[9]];
      }
    }

    if (numsFirst4.every(n => n !== null && n >= 4)) {
      if (numsFirst4[0] === 9 && sameSet(numsFirst4, [7, 8, 9, 10])) {
        return [workingImages[1], workingImages[0], workingImages[3]];
      }
      const n4Str = JSON.stringify(numsFirst4);
      if (n4Str === "[6,7,10,11]" || n4Str === "[5,6,7,9]" || (n4Str === "[6,7,8,9]" && !isFemale && !isKids)) {
        return [workingImages[0], workingImages[1], workingImages[2]];
      }
      if (n4Str === "[4,5,6,7]" || n4Str === "[6,5,7,10]" || fnames[0].startsWith("174897")) {
        return [workingImages[0], workingImages[2], workingImages[3]];
      }
      if (isFemale || isKids) {
        return [workingImages[0], workingImages[2], workingImages[1]];
      }
      return [workingImages[0], workingImages[2], workingImages[3]];
    }

    const nonNullSet = [...new Set(numsFirst4.filter(n => n !== null))];
    if (["[7,6,8]", "[6,7,8]", "[5,6,7]", "[6,5,7]"].includes(n3Str) || sameSet(nonNullSet, [7, 8, 9])) {
      return [workingImages[0], workingImages[2], workingImages[3]];
    }

    if (fnames[0].includes("frente") && isClientExplicitBackName(workingImages[1])) {
      const nonBackRest = workingImages.slice(1).filter(u => !isClientExplicitBackName(u));
      if (nonBackRest.length > 0) {
        return [workingImages[0], workingImages[1], nonBackRest[0]];
      }
      return [workingImages[2], workingImages[1], workingImages[0]];
    }

    if (isClientExplicitBackName(workingImages[2]) && isClientExplicitBackName(workingImages[3])) {
      return [workingImages[0], workingImages[2], workingImages[1]];
    }
    if (isClientExplicitBackName(workingImages[3]) && !isClientExplicitBackName(workingImages[2])) {
      return [workingImages[0], workingImages[3], workingImages[2]];
    }
    if (isClientExplicitBackName(workingImages[2]) && !isClientExplicitBackName(workingImages[3])) {
      return [workingImages[0], workingImages[2], workingImages[3]];
    }
    if (isClientExplicitBackName(workingImages[1]) && !isClientExplicitBackName(workingImages[2])) {
      return [workingImages[0], workingImages[1], workingImages[2]];
    }

    const pocFlags = fnames.slice(0, 4).map(f => f.includes("productonchannel"));
    if (!pocFlags[0] && pocFlags[1] && pocFlags[2] && pocFlags[3]) {
      return [workingImages[0], workingImages[2], workingImages[1]];
    }
    if (!pocFlags[0] && !pocFlags[1] && pocFlags[2] && pocFlags[3]) {
      return [workingImages[0], workingImages[2], workingImages[3]];
    }
    if (pocFlags.every(Boolean)) {
      if (["raglan", "segunda pele", "hyb", "cax"].some(k => skuTLow.includes(k)) || isKids) {
        return [workingImages[0], workingImages[1], workingImages[3]];
      }
      return [workingImages[0], workingImages[1], workingImages[2]];
    }

    if (skuUp.startsWith("ADV")) {
      return [workingImages[0], workingImages[2], workingImages[3]];
    }
    if (["-brk-agro-", "-brk-fishing-", "-brk-motors-", "camisa-agro-", "camisa-de-pesca-", "camisa-pesca-", "camisa-uv"].some(k => fnames[0].includes(k))) {
      return [workingImages[0], workingImages[1], workingImages[2]];
    }
    return [workingImages[0], workingImages[2], workingImages[1]];
  }

  // PILAR 2: GALERIAS COM EXATAMENTE 3 FOTOS
  const nonBackAll = workingImages.filter(u => !isClientExplicitBackName(u));
  if (nonBackAll.length === 1) {
    const onlyFront = nonBackAll[0];
    const backs = workingImages.filter(u => u !== onlyFront);
    return [backs[0], backs[1], onlyFront];
  }
  if (fnames[0].startsWith("1755030263590")) {
    return [workingImages[1], workingImages[2], workingImages[0]];
  }

  const nums3 = fnames.slice(0, 3).map(matchExplicitStudioNum);
  const nums3Str = JSON.stringify(nums3);
  if (["[2,3,4]", "[1,2,5]", "[1,5,6]"].includes(nums3Str)) {
    return [workingImages[1], workingImages[2], workingImages[0]];
  }
  if (nums3Str === "[2,1,3]") {
    return [workingImages[0], workingImages[2], workingImages[1]];
  }
  if (nums3Str === "[6,5,7]") {
    return [workingImages[1], workingImages[2], workingImages[0]];
  }
  if (nums3Str === "[8,9,7]") {
    return [workingImages[2], workingImages[1], workingImages[0]];
  }

  let img1 = workingImages[0];
  if (isClientExplicitBackName(img1) && nonBackAll.length > 0) {
    img1 = nonBackAll[0];
  }
  const rem = workingImages.filter(u => u !== img1);
  if (rem.length < 2) {
    return [img1, rem[0] || "", ""];
  }

  if (nums3Str === "[1,2,3]") {
    const isCombo123 = (
      skuUp.startsWith("CCPBR")
      || fnames[0].includes("ccpbr")
      || (fnames[0].includes("01fem") && Boolean(ts0) && parseInt(ts0, 10) < 1775)
    );
    if (isCombo123) {
      return [workingImages[0], workingImages[2], workingImages[1]];
    }
    return [workingImages[0], workingImages[1], workingImages[2]];
  }

  if (
    ["[6,7,8]", "[7,8,9]", "[7,8,11]", "[9,12,13]"].includes(nums3Str)
    || (nums3Str === "[5,6,7]" && (fnames[0].includes("frente_costas") || (["1760", "1761", "1768"].includes(ts0) && !skuUp.startsWith("FUSION"))))
    || (nums3[0] === null && !fnames[0].includes("frente") && nums3[1] === 1 && (nums3[2] === 2 || nums3[2] === 3))
  ) {
    return [workingImages[0], workingImages[2], workingImages[1]];
  }

  if (isClientExplicitBackName(rem[0]) && !isClientExplicitBackName(rem[1])) {
    return [img1, rem[0], rem[1]];
  }
  if (isClientBackViewUrl(rem[1]) && !isClientBackViewUrl(rem[0])) {
    return [img1, rem[1], rem[0]];
  }

  const pocRe = /productonchannel(?:_2f|\/)images(?:_2f|\/)(\d+)/i;
  const g0 = (img1.match(pocRe) || [])[1] || null;
  const g1 = (rem[0].match(pocRe) || [])[1] || null;
  const g2 = (rem[1].match(pocRe) || [])[1] || null;
  if (g0 === null && g1 && g2 && g1 === g2) {
    return [img1, rem[1], rem[0]];
  }

  return [img1, rem[0], rem[1]];
}

function selectClientCutleryActImages(cdnImages, title = "") {
  if (!cdnImages || cdnImages.length === 0) return ["", "", ""];
  if (cdnImages.length === 1) return [cdnImages[0], "", ""];
  if (cdnImages.length === 2) return [cdnImages[0], cdnImages[1], ""];

  const tLow = (title || "").toLowerCase();
  const isPng = (u) => u.toLowerCase().split("?")[0].endsWith(".png");

  if (tLow.includes("cutelaria d'avila") || tLow.includes("cutelaria davila")) {
    const validAfter = cdnImages.slice(1).filter(u => !u.toLowerCase().includes("designsemnome"));
    const img1 = cdnImages[0];
    const img2 = validAfter[0] || cdnImages[1];
    const img3 = validAfter[1] || (cdnImages[2] || "");
    return [img1, img2, img3];
  }

  if ((tLow.includes("rodeio 5") || tLow.includes("curva 3") || tLow.includes("curva nelore 3")) && cdnImages.some(isPng)) {
    const jpgs = cdnImages.filter(u => !isPng(u));
    if (jpgs.length >= 3) {
      const img1 = jpgs[0];
      const img2 = jpgs[jpgs.length - 1];
      const img3 = jpgs.length >= 4 ? jpgs[2] : jpgs[1];
      return [img1, img2, img3];
    }
  }

  if (tLow.includes("faca") && tLow.includes("10") && (tLow.includes("resina") || tLow.includes("madeira")) && cdnImages.length >= 4) {
    return [cdnImages[0], cdnImages[2], cdnImages[1]];
  }

  return [cdnImages[0], cdnImages[1], cdnImages[2]];
}

function getProductModeBHTML(liveP) {
  if (!liveP) return "";
  const originInfo = resolveClientOriginAndTitle(liveP);
  const formattedTitle = liveP.formatted_title || originInfo.formattedTitle;
  const brandName = liveP.brand_name || originInfo.brandName;
  const originType = liveP.origin_type || originInfo.originType;
  const archetypeId = liveP.archetype_id || (typeof detectClientArchetype === "function" ? detectClientArchetype(liveP.title, liveP.category, liveP.tags).id : "uv_performance");

  // Despacho especializado para Bonés e Chapéus (Layout D2C Oficial com Detalhes, Info e Split)
  if (["caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"].includes(archetypeId)) {
    return buildClientCapOrHatHtml(liveP, archetypeId);
  }
  const showCopyright = (liveP.show_copyright !== undefined) ? liveP.show_copyright : originInfo.showCopyright;

  const themeColor = liveP.theme_color || (liveP.store_key === "brk_agro" ? "#16a34a" : liveP.store_key === "brk_motors" ? "#f97316" : "#0284c7");
  const themeBg = liveP.theme_bg || (liveP.store_key === "brk_agro" ? "#f0fdf4" : liveP.store_key === "brk_motors" ? "#fff7ed" : "#f0f9ff");

  // Coleta oficial e desduplicação em 4 camadas (Contingência Anti-Duplicação da 1ª Foto na Shopify)
  const rawSources = (liveP.cdn_images && liveP.cdn_images.length > 0)
    ? liveP.cdn_images
    : (liveP.gallery && liveP.gallery.length > 0)
      ? liveP.gallery
      : (liveP.images || []);
  const images = sanitizeAndDedupClientImages(rawSources, archetypeId, liveP.title || "");

  const isApparel = ["uv_performance", "agro_field", "motors_speed", "shirts_button_work", "pants_cargo_tactical"].includes(archetypeId);
  const isLure = (archetypeId === "fishing_lures");
  const hasMultipleVariations = isLure && (Boolean(liveP.has_multiple_variations) || images.length >= 2 || (liveP.variants && liveP.variants.length > 1));
  let splitImages = isLure ? (liveP.split_images || null) : null;
  if (!splitImages && hasMultipleVariations && (images.length >= 4 || images.length === 2)) {
    splitImages = [images[0], images[1]];
  }
  let variationsSummary = isLure ? (liveP.variations_summary || "") : "";
  if (!variationsSummary && hasMultipleVariations) {
    variationsSummary = "Múltiplas variações e opções de cores disponíveis para escolha no anúncio.";
  }

  const tLowModal = (liveP.title || "").toLowerCase();
  const skuLowModal = (liveP.sku || liveP.master_sku || "").toLowerCase().trim();
  const tagsLowModal = (Array.isArray(liveP.tags) ? liveP.tags.join(" ") : (liveP.tags || "")).toLowerCase();
  const isFusionModal = isApparel && (/\b(fusion|fusionx)\b/i.test(tLowModal) || /fusion/i.test(skuLowModal) || /fusion/i.test(tagsLowModal));
  const isHybridModal = isApparel && (/\bhybrid\b/i.test(tLowModal) || /^hyb/i.test(skuLowModal) || /hybrid/i.test(skuLowModal) || /hybrid/i.test(tagsLowModal));
  const isHoodedModal = (isApparel && /\b(capuz|hood|hoodie)\b/i.test(tLowModal)) || isFusionModal || isHybridModal;
  const isKidsSkuModal = isApparel && (skuLowModal.startsWith("ci") || /^(?:c0|ci|cf|cm|casual|adv|cadv|ccpbr|bp|hyb|fusion|cax|raglan)\d+i(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$/i.test(skuLowModal)) && !/\b(feminina|feminino|baby look|babylook|masculina|masculino|adulto)\b/i.test(tLowModal);
  const isKidsModal = isApparel && (/\b(infantil|kids|juvenil|mini)\b/i.test(tLowModal) || isKidsSkuModal) && !/\b(adulto|unissex adulto)\b/i.test(tLowModal);
  const isSegundaPeleModal = isApparel && (tLowModal.includes("segunda pele") || skuLowModal.startsWith("raglan"));
  const isShortSleeveModal = isApparel && (/\b(manga curta|manga-curta|camiseta)\b/i.test(tLowModal) || (tLowModal.includes("curta") && tLowModal.includes("manga")) || skuLowModal.startsWith("cbtmc") || ((/^(casual|bp|cm|cadv|cf)/i.test(skuLowModal)) && !/^(cmb|cbt)/i.test(skuLowModal))) && !/\b(manga longa|manga-longa)\b/i.test(tLowModal) && !isSegundaPeleModal;
  const isHasGloveModal = isApparel && (/\b(com luva|e luva|luva integrada|armorx)\b/i.test(tLowModal) || skuLowModal.startsWith("cax"));
  const isFemaleModal = (/\b(feminina|feminino|baby look|babylook|mulher)\b/i.test(tLowModal) || /femin/i.test(tagsLowModal) || (isApparel && /bl(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$/i.test(skuLowModal))) && !isKidsModal;
  const isRoundNeckModal = isApparel && archetypeId !== "shirts_button_work" && !/^(cmb|cbt)/i.test(skuLowModal) && !/\b(botão|botao|colarinho|camisa work)\b/i.test(tLowModal) && (isSegundaPeleModal || isShortSleeveModal || /^ci0(?:54|7[2-9]|8[0-4])(?:i|pp|p|m|g|gg|g1|g2)?(?:_full|_out)?$/i.test(skuLowModal) || /\b(gola careca|gola redonda|sem zíper|sem ziper|t-shirt|camisa casual|casual)\b/i.test(tLowModal)) && !/\b(com zíper|com ziper)\b/i.test(tLowModal);

  // Atribuição de imagens exclusivas por ato - ZERO DUPLICAÇÃO e Alinhamento Semântico
  let img1 = images[0] || "";
  let img2 = images[1] || "";
  let img3 = images[2] || "";

  if (hasMultipleVariations && (images.length >= 4 || images.length === 2)) {
    img2 = images[2] || "";
    img3 = images[3] || "";
  } else if (isApparel) {
    [img1, img2, img3] = selectClientApparelActImages(images, isFemaleModal, isKidsModal, skuLowModal, liveP.title || "");
  } else if (archetypeId === "cutlery_unique") {
    [img1, img2, img3] = selectClientCutleryActImages(images, liveP.title || "");
  } else if (archetypeId === "fishing_tackle_gear" && (liveP.title || "").toLowerCase().includes("trava vara") && images.length >= 3) {
    [img1, img2, img3] = [images[0], images[2], images[1]];
  }

  let blocks = liveP.narrative_blocks ? liveP.narrative_blocks.map(b => ({ ...b })) : null;
  if (!blocks || blocks.length === 0) {
    const moldes = window.__STORE_MOLDES || {};
    let archKey = archetypeId;
    const tmpl = moldes[archKey] || moldes["uv_performance"];

    if (tmpl && tmpl.act1 && tmpl.act2 && tmpl.act3) {
      let act1Title = tmpl.act1.title || "QUALIDADE E DESEMPENHO";
      let act1Desc = (tmpl.act1.desc_tmpl || "").replace(/\{title\}/g, formattedTitle);
      let act2Title = tmpl.act2.title || "CONFORTO E TECNOLOGIA";
      let act2Desc = (tmpl.act2.desc_tmpl || "").replace(/\{title\}/g, formattedTitle);
      let act3Title = tmpl.act3.title || "COSTURAS PLANAS REFORÇADAS E ACABAMENTO PREMIUM";
      let act3Desc = (tmpl.act3.desc_tmpl || "").replace(/\{title\}/g, formattedTitle);
      let act3Tag = tmpl.act3.tag || "Durabilidade & Acabamento";

      if (isKidsModal) {
        act1Title = "CONFORTO E PROTEÇÃO SOLAR TOTAL PARA OS PEQUENOS AVENTUREIROS";
        act1Desc = `Desenvolvida especialmente para crianças e jovens exploradores com grade inteligente por faixa de idade (1 a 13 anos, mantendo a referência dos tamanhos PP ao G2), o(a) ${formattedTitle} oferece proteção solar máxima FPU 50+ com toque extra suave na pele, garantindo segurança, leveza e liberdade total para brincar ao ar livre.`;
        act2Title = "TECNOLOGIA DRY FIT QUE MANTÉM AS CRIANÇAS FRESCAS E SECAS";
        act2Desc = "Tecido tecnológico respirável que absorve e dissipa o suor rapidamente, evitando o superaquecimento e mantendo o corpo seco e confortável durante todas as brincadeiras e pescarias em família.";
        if (!isHoodedModal) {
          act3Tag = "Durabilidade & Liberdade";
          act3Title = "COSTURAS PLANAS ANTI-ATRITO E MÁXIMA DURABILIDADE";
          act3Desc = "Construída com acabamento elástico de alta resistência que não pinica nem irrita a pele sensível das crianças, oferecendo caimento confortável que aguenta todas as aventuras infantis.";
        }
      } else if (isFemaleModal && archetypeId === "uv_performance") {
        act1Title = "MODELAGEM FEMININA ANATÔMICA COM CAIMENTO IMPECÁVEL";
        act1Desc = `Projetada sob medida para a anatomia feminina, a ${formattedTitle} combina corte acinturado esportivo (Baby Look), máxima liberdade de movimentos e proteção solar FPU 50+ com toque suave e elegante.`;
      }

      if (isFusionModal) {
        act3Tag = "Capuz com Máscara Integrada & Proteção 360°";
        act3Title = "CAPUZ COM MÁSCARA FACIAL INTEGRADA E PUNHO COM DEDEIRA";
        act3Desc = "Desenvolvida com modelagem anatômica contínua para máximo conforto e zero atrito, a camisa FusionX conta com capuz anatômico acoplado com máscara facial protetora (balaclava integrada) que protege cabeça, nuca e rosto contra o sol forte e o vento, além de punhos anatômicos com abertura para o polegar (dedeira) que mantêm o dorso da mão sempre protegido.";
      } else if (isHybridModal) {
        act3Tag = "Capuz Anatômico & Punho com Dedeira";
        act3Title = "CAPUZ ANATÔMICO INTEGRADO E PUNHO COM ABERTURA PARA POLEGAR";
        act3Desc = "Projetada com caimento leve, contínuo e livre de atrito, a camisa Hybrid integra capuz anatômico de proteção solar 360° para nuca e cabeça, mangas com costuras planas reforçadas e punhos com abertura para o polegar (dedeira) que protegem o dorso das mãos durante toda a pescaria ou atividade ao ar livre.";
      } else if (isHoodedModal) {
        act3Tag = "Capuz Anatômico & Proteção 360°";
        act3Title = "CAPUZ ANATÔMICO INTEGRADO E COSTURA REFORÇADA";
        act3Desc = "Equipada com capuz anatômico integrado que oferece proteção solar 360° para nuca, orelhas e laterais do rosto contra a radiação forte e o vento, dispensando acessórios extras, com costuras planas reforçadas anti-atrito.";
      } else if (isShortSleeveModal) {
        act3Desc = act3Desc
          .replace(/punhos anatômicos que não laceiam com o uso frequente/gi, "mangas curtas com barra em costura dupla reforçada que proporcionam ventilação ideal e liberdade nos braços")
          .replace(/manga longa/gi, "manga curta");
      } else if (isRoundNeckModal) {
        act3Title = "COSTURA REFORÇADA E GOLA REDONDA ANATÔMICA";
        act3Desc = "Acabamento de alto padrão com costuras planas anti-atrito, gola careca canelada reforçada ombro a ombro e caimento confortável para uso prolongado.";
      } else if (isHasGloveModal) {
        act3Tag = "Punho com Luva Integrada & Acabamento";
        act3Title = "PUNHOS ESTENDIDOS COM LUVA INTEGRADA E COSTURAS REFORÇADAS";
        act3Desc = "Acabamento de alto padrão com costuras planas anti-atrito, gola padre anatômica e punhos estendidos com luva integrada (abertura para o polegar) que garantem proteção solar contínua no dorso das mãos com total liberdade nos dedos.";
      }

      if (archetypeId === "uv_performance" && !isKidsModal) {
        const storeKeyEff = liveP.store_key || (typeof currentStore !== "undefined" ? currentStore : "brk_fishing");
        if (storeKeyEff === "brk_agro" || /\b(agro|campo|rural|trator|fazenda|pecuaria|pecuária)\b/i.test(tLowModal)) {
          act1Desc = act1Desc
            .replace(/pescadores e entusiastas do ar livre/g, "o homem e a mulher do campo e entusiastas do ar livre")
            .replace(/arremessos e manobras/g, "a rotina intensa no campo e manobras");
        } else if (storeKeyEff === "brk_motors" || /\b(moto|trail|cross|velocidade|motors|pista)\b/i.test(tLowModal)) {
          act1Desc = act1Desc
            .replace(/pescadores e entusiastas do ar livre/g, "pilotos, motociclistas e aventureiros")
            .replace(/arremessos e manobras/g, "a pilotagem e manobras");
        }
      }

      blocks = [
        {
          tag: isKidsModal ? "Proteção Infantil & Conforto" : (tmpl.act1.tag || "Destaque"),
          title: act1Title,
          description: act1Desc,
          image: img1,
          split_images: splitImages,
          variations_summary: variationsSummary
        },
        {
          tag: isKidsModal ? "Respirabilidade & Frescor" : (tmpl.act2.tag || "Destaque"),
          title: act2Title,
          description: act2Desc,
          image: img2
        },
        {
          tag: act3Tag,
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

  const isReadyDelivery = (p) => {
    if (!p) return false;
    const fullOutPattern = /(_FULL|_OUT|\bFULL\b|\bOUT\b|-FULL|-OUT)/i;
    const skus = [p.sku, p.master_sku, ...(p.variants_skus || [])].filter(Boolean);
    if (skus.some(s => fullOutPattern.test(s))) return true;
    if (p.variants && Array.isArray(p.variants)) {
      if (p.variants.some(v => v && fullOutPattern.test(v.sku || ""))) return true;
    }
    const title = p.title || "";
    const tags = Array.isArray(p.tags) ? p.tags.join(" ") : (p.tags || "");
    if (fullOutPattern.test(title) || fullOutPattern.test(tags)) return true;
    if (/pronta entrega|envio imediato/i.test(title)) return true;
    return false;
  };

  let specs = (liveP.specs || []).map(s => ({ ...s }));
  if (specs.length === 0 && window.__STORE_MOLDES) {
    const archKey = archetypeId;
    const tmpl = window.__STORE_MOLDES[archKey] || window.__STORE_MOLDES["uv_performance"];
    if (tmpl && tmpl.base_specs) {
      specs = tmpl.base_specs.map(s => ({ label: s.label, value: s.default }));
    }
  }

  // Ajuste inteligente do Prazo de Produção para Camisas C0 (Pronta entrega para _FULL e _OUT, 10 dias úteis para padrão)
  const isC0Shirt = (archetypeId === "uv_performance") ||
                    (liveP.sku && /^(c0|ci|cadv|adv)/i.test(liveP.sku)) ||
                    (liveP.master_sku && /^(c0|ci|cadv|adv)/i.test(liveP.master_sku));
  if (isC0Shirt && specs.length > 0) {
    const prazoVal = isReadyDelivery(liveP) ? "Pronta entrega" : "10 dias úteis";
    specs = specs.map(s => {
      if (s.label === "Prazo de Produção") {
        return { ...s, value: prazoVal };
      }
      return s;
    });
  }

  if (isHasGloveModal && !isShortSleeveModal) {
    specs = specs.map(s => {
      if (/punho/i.test(s.label)) {
        return { label: "Punhos / Luva", value: "Punhos estendidos anatômicos com luva integrada para o dorso da mão" };
      }
      return s;
    });
    if (!specs.some(s => /luva/i.test(s.label))) {
      specs.push({ label: "Punhos / Luva", value: "Punhos estendidos anatômicos com luva integrada para o dorso da mão" });
    }
  }

  if (isFusionModal) {
    if (!specs.some(s => /capuz|máscara/i.test(s.label))) {
      specs.push({ label: "Capuz & Máscara", value: "Capuz anatômico integrado com máscara facial de proteção UV50+" });
    }
    if (!specs.some(s => /punho/i.test(s.label))) {
      specs.push({ label: "Punhos", value: "Punhos anatômicos com abertura para o polegar (dedeira)" });
    }
  } else if (isHybridModal) {
    if (!specs.some(s => /capuz/i.test(s.label))) {
      specs.push({ label: "Capuz", value: "Capuz anatômico integrado de alta cobertura solar" });
    }
    if (!specs.some(s => /punho/i.test(s.label))) {
      specs.push({ label: "Punhos", value: "Punhos anatômicos com abertura para o polegar (dedeira)" });
    }
  } else if (isHoodedModal && !specs.some(s => /capuz/i.test(s.label))) {
    specs.push({ label: "Capuz", value: "Capuz anatômico integrado para proteção solar estendida" });
  }

  if (!isFusionModal && !isHybridModal && !isRoundNeckModal && !isHoodedModal && archetypeId === "uv_performance") {
    if (!specs.some(s => /gola|fechamento/i.test(s.label))) {
      specs.push({ label: "Gola / Fechamento", value: "Gola padre anatômica com zíper e trava de segurança" });
    }
  }

  // Trava Estrita Anti-Zíper no Modal para Fusion, Hybrid, Capuz, Gola Careca e Botão
  if (isFusionModal || isHybridModal || isHoodedModal || isRoundNeckModal || archetypeId === "shirts_button_work") {
    const replacementCollar = (isFusionModal || isHybridModal || isHoodedModal) ? "capuz anatômico contínuo" : "gola redonda anatômica";
    const replacementHood = isFusionModal ? "capuz com máscara facial integrada" : ((isHybridModal || isHoodedModal) ? "capuz anatômico integrado" : "gola redonda anatômica");
    blocks.forEach(b => {
      if (b.title) b.title = b.title.replace(/\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b/gi, "").trim();
      if (b.description) {
        b.description = b.description
          .replace(/gola padre com cobertura no cursor do z[íi]per/gi, replacementCollar)
          .replace(/\bcursor do z[íi]per\b/gi, "acabamento anatômico")
          .replace(/\bz[íi]per com trava de seguran[çc]a\b/gi, "conforto anatômico contínuo")
          .replace(/\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b/gi, "")
          .replace(/\(\s*\)/g, "")
          .trim();
      }
    });
    specs = specs.map(s => {
      const lbl = s.label.replace(/\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b/gi, "").trim() || "Acabamento";
      let val = s.value
        .replace(/gola padre[^,;.]*/gi, replacementHood)
        .replace(/\bcursor do z[íi]per\b/gi, "acabamento contínuo")
        .replace(/\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b/gi, "")
        .replace(/\(\s*\)/g, "")
        .trim();
      return { label: lbl, value: val };
    });
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

  const tLowTitle = (formattedTitle || liveP.title || "").toLowerCase();
  const isKids = ["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archetypeId) && (liveP.is_kids !== undefined ? liveP.is_kids : isKidsModal);
  const isShortSleeve = liveP.is_short_sleeve !== undefined ? liveP.is_short_sleeve : isShortSleeveModal;

  const quickBadgesHtml = buildClientQuickBadges(themeColor, themeBg, archetypeId, liveP);
  const sizeGuideHtml = buildClientSizeGuide(themeColor, themeBg, archetypeId, isKids, isShortSleeve, liveP);
  const schemaJsonLd = buildClientSchemaJsonLd(liveP);

  // 2. Blocos Narrativos
  function getClientMediaInfographicMeta(idx, archetypeId, prodObj, fTitle, isShortSlv, isSplit) {
    const tLow = String(fTitle || prodObj.title || "").toLowerCase();
    const skuLow = String(prodObj.master_sku || prodObj.sku || "").toLowerCase();
    const tagsLow = String(Array.isArray(prodObj.tags) ? prodObj.tags.join(" ") : (prodObj.tags || "")).toLowerCase();
    const shortSlv = Boolean(isShortSlv) || ["manga curta", "camiseta", "t-shirt", "tshirt", "baby look"].some(w => tLow.includes(w));
    const isShirtArch = ["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archetypeId);
    const hasUv = ["uv", "fpu", "proteção solar", "protecao solar", "xtech", "dry"].some(w => tLow.includes(w) || tagsLow.includes(w));
    const isCotton = ["algodão", "algodao", "cotton", "100% algod"].some(w => tLow.includes(w) || tagsLow.includes(w)) || (archetypeId === "agro_field" && !hasUv && tLow.includes("camiseta"));

    if (idx === 0) {
      if (isSplit) {
        return { view_tag: "GALERIA OFICIAL • ATO 01", icon: "palette", label: "Padrões de Cores & Acabamento Visual", pill: "Alta Atratividade", zoom_act3: false };
      }
      if (isShirtArch) {
        return { view_tag: "VISTA FRONTAL • ATO 01", icon: "sparkle", label: "Modelagem Anatômica & Identidade Visual", pill: "Caimento Oficial BRK", zoom_act3: false };
      }
      return { view_tag: "APRESENTAÇÃO • ATO 01", icon: "sparkle", label: "Design Funcional & Construção Original", pill: "Padrão Oficial", zoom_act3: false };
    }

    if (idx === 1) {
      if (isShirtArch) {
        if (isCotton) {
          return { view_tag: "ENGENHARIA TÊXTIL • ATO 02", icon: "care", label: "Malha 100% Algodão Premium & Respirabilidade", pill: "Toque Nobre", zoom_act3: false };
        }
        if (archetypeId === "shirts_button_work" || ["botão", "botao", "work", "sarja"].some(w => tLow.includes(w)) || skuLow.startsWith("cmb") || skuLow.startsWith("cbt")) {
          return { view_tag: "ESTRUTURA TÊXTIL • ATO 02", icon: "shield", label: "Tecido de Alta Gramatura & Resistência", pill: "Uso Operacional", zoom_act3: false };
        }
        return { view_tag: "TECNOLOGIA TÊXTIL • ATO 02", icon: "sun", label: "Painel Dorsal & Tecido Tecnológico UV50+", pill: "Secagem Rápida", zoom_act3: false };
      }
      return { view_tag: "PERFORMANCE • ATO 02", icon: "bolt", label: "Engenharia de Materiais & Desempenho", pill: "Alta Durabilidade", zoom_act3: false };
    }

    if (isShirtArch) {
      const isFusion = tLow.includes("fusion") || skuLow.includes("fusion");
      const isHybrid = tLow.includes("hybrid") || skuLow.startsWith("hyb") || skuLow.includes("hybrid");
      const hasCapuz = isFusion || isHybrid || ["capuz", "hood", "balaclava"].some(w => tLow.includes(w)) || skuLow.startsWith("ccp");
      const isArmor = tLow.includes("armor") || skuLow.startsWith("cax");
      const isRaglan = ["segunda pele", "raglan", "thermal", "termica", "térmica"].some(w => tLow.includes(w)) || skuLow.includes("raglan");
      const isButton = archetypeId === "shirts_button_work" || ["botão", "botao", "work", "operacional"].some(w => tLow.includes(w)) || skuLow.startsWith("cmb") || skuLow.startsWith("cbt");
      const isCrew = ["careca", "redonda", "sem zíper", "sem ziper"].some(w => tLow.includes(w));

      let lbl = "Foco Frontal: Gola Padre Anatômica, Zíper & Punhos";
      let pill = "Pesponto Duplo";
      if (isFusion) { lbl = "Foco Frontal: Capuz, Máscara Facial & Dedeira"; pill = "Proteção 360°"; }
      else if (isHybrid) { lbl = "Foco Frontal: Capuz Anatômico & Punho c/ Dedeira"; pill = "Nuca & Mãos"; }
      else if (hasCapuz) { lbl = "Foco Frontal: Capuz Integrado & Proteção de Nuca"; pill = "Barreira Solar"; }
      else if (isArmor) { lbl = "Foco Frontal: Punho c/ Luva Integrada & Gola"; pill = "Proteção de Punho"; }
      else if (isRaglan) { lbl = "Foco Frontal: Corte Raglan & Costura Plana"; pill = "Zero Atrito"; }
      else if (isButton) { lbl = "Foco Frontal: Colarinho Estruturado & Botões"; pill = "Costura em X"; }
      else if (isCotton) { lbl = "Foco Frontal: Gola em Ribana & Costura Dupla"; pill = "Anti-Deformação"; }
      else if (isCrew || shortSlv) { lbl = "Foco Frontal: Gola Anatômica & Costura Dupla"; pill = "Toque Suave"; }

      return { view_tag: "ZOOM DE ACABAMENTO • ATO 03", icon: "shield", label: lbl, pill: pill, zoom_act3: true };
    }

    return { view_tag: "DETALHE TÉCNICO • ATO 03", icon: "shield", label: "Acabamento de Precisão & Componentes", pill: "Rigor Oficial BRK", zoom_act3: false };
  }

  const rawUid = String(liveP.id || liveP.master_sku || liveP.sku || "brk");
  const uidBase = rawUid.replace(/[^A-Za-z0-9]/g, "").slice(0, 16) || "brk";
  const isShirtArchMain = ["uv_performance", "agro_field", "motors_speed", "shirts_button_work"].includes(archetypeId);
  const act2ImgCandidate = img2 || "";
  const mlTrackAttrs = `onmousemove="var r=this.getBoundingClientRect(),x=Math.max(0,Math.min(100,((event.clientX-r.left)/r.width)*100)).toFixed(2)+'%',y=Math.max(0,Math.min(100,((event.clientY-r.top)/r.height)*100)).toFixed(2)+'%';var lz=this.querySelectorAll('.brk-ml-zoom-layer');for(var i=0;i<lz.length;i++){lz[i].style.backgroundPosition=x+' '+y;}var cr=this.querySelector('.brk-ml-cursor');if(cr){cr.style.left=x;cr.style.top=y;}" ontouchmove="if(event.touches&&event.touches[0]){var r=this.getBoundingClientRect(),x=Math.max(0,Math.min(100,((event.touches[0].clientX-r.left)/r.width)*100)).toFixed(2)+'%',y=Math.max(0,Math.min(100,((event.touches[0].clientY-r.top)/r.height)*100)).toFixed(2)+'%';var lz=this.querySelectorAll('.brk-ml-zoom-layer');for(var i=0;i<lz.length;i++){lz[i].style.backgroundPosition=x+' '+y;}}"`;

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

    const safeTitleAlt = String(formattedTitle || "").replace(/"/g, "&quot;");
    const safeBlockAlt = String(block.alt || formattedTitle || "").replace(/"/g, "&quot;");
    let mediaHtml = "";
    if (blockSplitImgs && blockSplitImgs.length >= 2) {
      const infoMeta = getClientMediaInfographicMeta(idx, archetypeId, liveP, formattedTitle, isShortSleeve, true);
      mediaHtml = `<div class="brk-desc-media brk-media-card">
        <div class="brk-media-stage brk-desc-media-split">
          <div class="brk-split-item brk-stage-loupe" ${mlTrackAttrs}>
            <img src="${blockSplitImgs[0]}" alt="${safeTitleAlt} - Opção 1" loading="lazy" referrerpolicy="no-referrer" />
            <div class="brk-ml-zoom-layer" style="background-image: url('${blockSplitImgs[0]}');"></div>
          </div>
          <div class="brk-split-item brk-stage-loupe" ${mlTrackAttrs}>
            <img src="${blockSplitImgs[1]}" alt="${safeTitleAlt} - Opção 2" loading="lazy" referrerpolicy="no-referrer" />
            <div class="brk-ml-zoom-layer" style="background-image: url('${blockSplitImgs[1]}');"></div>
          </div>
          <span class="brk-loupe-cta">Passe o mouse p/ Lupa 2.4x</span>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">${getSvgIcon(infoMeta.icon, themeColor, 14)} <span>${infoMeta.label}</span></span>
          <span class="brk-media-info-pill">${infoMeta.pill}</span>
        </div>
      </div>`;
    } else if (blockImg && idx === 0) {
      const infoMeta = getClientMediaInfographicMeta(idx, archetypeId, liveP, formattedTitle, isShortSleeve, false);
      const back360Url = act2ImgCandidate || blockImg;
      const focusCls = isShirtArchMain ? " brk-focus-top" : " brk-focus-center";
      const btn1Lbl = isShirtArchMain ? "0° Frente" : "0° Vista 1";
      const btn2Lbl = (isShirtArchMain && act2ImgCandidate) ? "180° Costas" : "180° Giro 3D";
      mediaHtml = `<div class="brk-desc-media brk-media-card brk-card-360">
        <input type="radio" name="brk360_${uidBase}" id="brk360_${uidBase}_1" class="brk-360-inp brk-360-i1" checked />
        <input type="radio" name="brk360_${uidBase}" id="brk360_${uidBase}_2" class="brk-360-inp brk-360-i2" />
        <div class="brk-media-stage brk-stage-360${focusCls}" ${mlTrackAttrs}>
          <div class="brk-360-rotator">
            <div class="brk-360-face brk-360-front">
              <img src="${blockImg}" alt="${safeBlockAlt}" loading="lazy" referrerpolicy="no-referrer" />
              <div class="brk-ml-zoom-layer" style="background-image: url('${blockImg}');"></div>
            </div>
            <div class="brk-360-face brk-360-back" style="background-image: url('${back360Url}');">
              <div class="brk-ml-zoom-layer" style="background-image: url('${back360Url}');"></div>
            </div>
          </div>
          <span class="brk-ml-cursor"></span>
        </div>
        <div class="brk-360-controls">
          <label for="brk360_${uidBase}_1" class="brk-360-btn brk-360-b1">${btn1Lbl}</label>
          <label for="brk360_${uidBase}_2" class="brk-360-btn brk-360-b2">${btn2Lbl}</label>
          <span class="brk-360-hint">Passe o mouse p/ Lupa 2.4x</span>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">${getSvgIcon(infoMeta.icon, themeColor, 14)} <span>${infoMeta.label}</span></span>
          <span class="brk-media-info-pill">${infoMeta.pill}</span>
        </div>
      </div>`;
    } else if (blockImg) {
      const infoMeta = getClientMediaInfographicMeta(idx, archetypeId, liveP, formattedTitle, isShortSleeve, false);
      let focusCls = " brk-focus-center";
      if (idx === 2 && isShirtArchMain) focusCls = " brk-focus-top";
      else if (idx === 1 && isShirtArchMain) focusCls = " brk-focus-mid";
      mediaHtml = `<div class="brk-desc-media brk-media-card brk-card-loupe">
        <div class="brk-media-stage brk-stage-loupe${focusCls}" ${mlTrackAttrs}>
          <img src="${blockImg}" alt="${safeBlockAlt}" loading="lazy" referrerpolicy="no-referrer" />
          <div class="brk-ml-zoom-layer" style="background-image: url('${blockImg}');"></div>
          <span class="brk-ml-cursor"></span>
          <span class="brk-loupe-lens" style="background-image: url('${blockImg}');"><span class="brk-loupe-badge">Lupa 2.4x</span></span>
          <span class="brk-loupe-cta">Passe o mouse p/ Lupa 2.4x</span>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">${getSvgIcon(infoMeta.icon, themeColor, 14)} <span>${infoMeta.label}</span></span>
          <span class="brk-media-info-pill">${infoMeta.pill}</span>
        </div>
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
      flex-direction: column;
      align-items: stretch;
      justify-content: center;
    }
    .brk-media-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
      transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .brk-media-card:hover {
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.11);
    }
    .brk-media-stage {
      position: relative;
      width: 100%;
      overflow: hidden;
      background: #ffffff;
      padding: 6px;
      display: block;
    }
    .brk-desc-media img {
      width: 100%;
      height: auto;
      max-height: 500px;
      object-fit: contain;
      border-radius: 10px;
      display: block;
      margin: 0 auto;
      background: #ffffff;
    }
    .brk-ml-zoom-layer {
      position: absolute;
      inset: 6px;
      border-radius: 10px;
      background-repeat: no-repeat;
      background-color: #ffffff;
      background-size: 250%;
      background-position: 50% 30%;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.16s ease;
      z-index: 2;
    }
    .brk-stage-loupe:hover .brk-ml-zoom-layer,
    .brk-stage-360:hover .brk-360-front .brk-ml-zoom-layer {
      opacity: 1;
    }
    .brk-360-i2:checked ~ .brk-stage-360:hover .brk-360-front .brk-ml-zoom-layer {
      opacity: 0;
    }
    .brk-360-i2:checked ~ .brk-stage-360:hover .brk-360-back .brk-ml-zoom-layer {
      opacity: 1;
    }
    .brk-360-inp, .brk-loupe-inp {
      display: none !important;
    }
    .brk-stage-360 {
      perspective: 1100px;
      cursor: crosshair;
    }
    .brk-360-rotator {
      position: relative;
      width: 100%;
      transform-style: preserve-3d;
      transition: transform 0.65s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .brk-360-face {
      position: relative;
      width: 100%;
      overflow: hidden;
      border-radius: 10px;
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .brk-360-back {
      position: absolute;
      inset: 0;
      transform: rotateY(180deg);
      background-size: contain;
      background-position: center;
      background-repeat: no-repeat;
      background-color: #ffffff;
      border-radius: 10px;
    }
    .brk-360-i2:checked ~ .brk-stage-360 .brk-360-rotator {
      transform: rotateY(180deg);
    }
    .brk-360-controls {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 8px 10px;
      background: #f1f5f9;
      border-top: 1px solid #e2e8f0;
    }
    .brk-360-btn {
      flex: 1;
      text-align: center;
      font-size: 11px;
      font-weight: 800;
      color: #475569;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 6px 8px;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s ease;
    }
    .brk-360-btn:hover {
      border-color: ${themeColor};
      color: ${themeColor};
    }
    .brk-360-i1:checked ~ .brk-360-controls .brk-360-b1,
    .brk-360-i2:checked ~ .brk-360-controls .brk-360-b2 {
      background: ${themeColor};
      color: #ffffff;
      border-color: ${themeColor};
      box-shadow: 0 2px 8px ${themeColor}40;
    }
    .brk-360-hint {
      font-size: 10px;
      font-weight: 700;
      color: #64748b;
      padding: 0 6px;
      white-space: nowrap;
    }
    .brk-stage-loupe {
      position: relative;
      cursor: crosshair;
    }
    .brk-ml-cursor {
      position: absolute;
      left: 50%;
      top: 50%;
      width: 96px;
      height: 96px;
      transform: translate(-50%, -50%) scale(0.7);
      border-radius: 50%;
      border: 2px solid ${themeColor};
      background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, rgba(15,23,42,0.06) 100%);
      box-shadow: 0 0 0 1px rgba(255,255,255,0.85), 0 6px 18px rgba(15,23,42,0.22);
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.18s ease, transform 0.18s ease;
      z-index: 4;
    }
    .brk-media-stage:hover .brk-ml-cursor {
      opacity: 1;
      transform: translate(-50%, -50%) scale(1);
    }
    .brk-loupe-lens {
      display: none !important;
    }
    .brk-loupe-badge {
      display: none !important;
    }
    .brk-loupe-cta {
      position: absolute;
      bottom: 10px;
      right: 12px;
      z-index: 3;
      background: rgba(15, 23, 42, 0.78);
      color: #ffffff;
      font-size: 10px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 9999px;
      backdrop-filter: blur(4px);
      pointer-events: none;
      transition: opacity 0.2s ease;
    }
    .brk-stage-loupe:hover .brk-loupe-cta,
    .brk-media-stage:hover .brk-loupe-cta {
      opacity: 0;
    }
    .brk-media-infobar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 14px;
      background: #f8fafc;
      border-top: 1px solid #e2e8f0;
      font-size: 11.5px;
    }
    .brk-media-info-left {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      font-weight: 700;
      color: #1e293b;
      min-width: 0;
      line-height: 1.25;
    }
    .brk-media-info-left span {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .brk-media-info-pill {
      flex-shrink: 0;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: ${themeColor};
      background: ${themeBg};
      border: 1px solid ${themeColor}30;
      padding: 3px 9px;
      border-radius: 9999px;
    }
    .brk-desc-media-split {
      display: flex;
      gap: 10px;
      padding: 10px;
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
      background: ${themeColor};
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
      grid-template-columns: repeat(2, 1fr);
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
      .brk-media-infobar {
        padding: 8px 10px;
        font-size: 10.5px;
      }
      .brk-media-info-pill {
        font-size: 9px;
        padding: 2px 7px;
      }
      .brk-loupe-lens {
        width: 90px;
        height: 90px;
        right: 10px;
        bottom: 38px;
      }
      .brk-360-btn {
        font-size: 10px;
        padding: 5px 6px;
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
  </div>

${copyrightHtml}

</div>

${schemaJsonLd}`;
}

// Delegação global para Lupa Dinâmica Estilo Mercado Livre (acompanha o mouse em tempo real nos 3 Atos sem travar)
if (typeof document !== "undefined" && !window.__BRK_ML_LOUPE_BOUND) {
  window.__BRK_ML_LOUPE_BOUND = true;
  const updateBrkStageCoords = (e, clientX, clientY) => {
    const stage = e.target && e.target.closest ? e.target.closest(".brk-stage-loupe, .brk-stage-360, .brk-media-stage") : null;
    if (!stage) return;
    const r = stage.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const x = Math.max(0, Math.min(100, ((clientX - r.left) / r.width) * 100)).toFixed(2) + "%";
    const y = Math.max(0, Math.min(100, ((clientY - r.top) / r.height) * 100)).toFixed(2) + "%";
    const layers = stage.querySelectorAll(".brk-ml-zoom-layer");
    for (let i = 0; i < layers.length; i++) {
      layers[i].style.backgroundPosition = x + " " + y;
    }
    const cursor = stage.querySelector(".brk-ml-cursor");
    if (cursor) {
      cursor.style.left = x;
      cursor.style.top = y;
    }
  };
  document.addEventListener("mousemove", (e) => updateBrkStageCoords(e, e.clientX, e.clientY), { passive: true });
  document.addEventListener("touchmove", (e) => {
    if (e.touches && e.touches[0]) updateBrkStageCoords(e, e.touches[0].clientX, e.touches[0].clientY);
  }, { passive: true });
}
