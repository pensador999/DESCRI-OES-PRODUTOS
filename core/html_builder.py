"""
Compilador de HTML & Markdown Verticalizado e Blindado para Shopify (Padrão Autêntico BRK).
100% autônomo e nativo (ZERO dependência de Font Awesome ou CDNs externos).
100% responsivo (Mobile e Desktop), sem risco de quebra de layout no tema Shopify.

Implementa os 8 Pilares Estratégicos:
1. Veracidade das Informações: Preservação rigorosa dos dados técnicos confirmados.
2. Formatação em Markdown e HTML estruturados.
3. Ícones Nativos & Emojis UTF-8 (Eliminação de CDNs Font Awesome que quebram na Shopify).
4. Título Obrigatório na Descrição:
   - Produção Própria: Prefixo 'BRK' garantido.
   - Revenda: Marca correspondente garantida no título.
5. Shopify Específica: Integração com store_key e links diretos ao Admin Shopify.
6. Iscas e Produtos com Várias Variações: Layout split com 2 imagens lado a lado e aviso de variações.
7. Camisas C0 de Produção Própria: Aviso exclusivo de direitos autorais e proteção de estampas.
"""

from typing import Dict, Any, List

try:
    from core.svg_icons import get_svg_icon
except ImportError:
    try:
        from svg_icons import get_svg_icon
    except ImportError:
        def get_svg_icon(name: str, color: str = "currentColor", size: int = 16, extra_class: str = "") -> str:
            return ""

class HTMLBuilder:
    def __init__(self):
        pass

    def _get_tag_icon_name(self, tag_text: str) -> str:
        t = tag_text.lower()
        if any(w in t for w in ["performance", "conforto", "respirabilidade"]):
            return "bolt"
        if any(w in t for w in ["design", "identidade", "visual", "estilo", "estampa"]):
            return "palette"
        if any(w in t for w in ["durabilidade", "acabamento", "proteção", "resiste"]):
            return "shield"
        if any(w in t for w in ["nado", "ação", "pesca", "isca", "predador"]):
            return "fish"
        if any(w in t for w in ["solar", "sol", "uv"]):
            return "sun"
        if any(w in t for w in ["lâmina", "afiação", "corte", "faca"]):
            return "knife"
        if any(w in t for w in ["ergonomia", "calçado", "solado", "pisada"]):
            return "shoe"
        if any(w in t for w in ["organização", "espaço", "caixa", "maleta"]):
            return "box"
        if any(w in t for w in ["engenharia", "mecânica", "precisão", "engrenagem"]):
            return "gear"
        return "sparkle"

    def _get_tag_emoji(self, tag_text: str) -> str:
        t = tag_text.lower()
        if any(w in t for w in ["performance", "conforto", "respirabilidade"]):
            return "⚡"
        if any(w in t for w in ["design", "identidade", "visual", "estilo", "estampa"]):
            return "🎨"
        if any(w in t for w in ["durabilidade", "acabamento", "proteção", "resiste"]):
            return "🛡️"
        if any(w in t for w in ["nado", "ação", "pesca", "isca", "predador"]):
            return "🎣"
        if any(w in t for w in ["solar", "sol", "uv"]):
            return "☀️"
        if any(w in t for w in ["lâmina", "afiação", "corte", "faca"]):
            return "🔪"
        if any(w in t for w in ["ergonomia", "calçado", "solado", "pisada"]):
            return "👟"
        if any(w in t for w in ["organização", "espaço", "caixa", "maleta"]):
            return "📦"
        if any(w in t for w in ["engenharia", "mecânica", "precisão", "engrenagem"]):
            return "⚙️"
        if any(w in t for w in ["térmico", "temperatura", "frio"]):
            return "❄️"
        if any(w in t for w in ["campo", "rural", "agro"]):
            return "🌱"
        if any(w in t for w in ["velocidade", "adrenalina", "off-road"]):
            return "🏍️"
        return "✨"

    def build_shopify_html(self, enriched_data: Dict[str, Any]) -> str:
        """
        Compila a descrição em HTML no padrão verticalizado BRK, 100% autônomo com SVGs inline estilo Font Awesome.
        """
        formatted_title = enriched_data.get("formatted_title") or enriched_data.get("title", "Produto BRK")
        brand_name = enriched_data.get("brand_name", "BRK")
        origin_type = enriched_data.get("origin_type", "producao_propria")
        show_copyright = enriched_data.get("show_copyright", False)
        has_multiple_variations = enriched_data.get("has_multiple_variations", False)
        split_images = enriched_data.get("split_images")
        variations_summary = enriched_data.get("variations_summary", "")

        theme_color = enriched_data.get("theme_color", "#0284c7")
        theme_bg = enriched_data.get("theme_bg", "#f0f9ff")
        blocks = enriched_data.get("narrative_blocks", [])
        if not blocks:
            acts = []
            for act_key in ["act1", "act2", "act3"]:
                if act_key in enriched_data and isinstance(enriched_data[act_key], dict):
                    acts.append(enriched_data[act_key])
            if acts:
                blocks = acts

        specs = enriched_data.get("specs", [])
        care_tips = enriched_data.get("care_tips", "Lavar à mão ou em ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar).")

        # 1. Cabeçalho com Título Oficial e Origem
        if origin_type == "revenda":
            origin_badge = f'<span class="brk-desc-origin-badge revenda">{get_svg_icon("sparkle", color="#b45309", size=12)} PRODUTO ORIGINAL • MARCA {brand_name.upper()}</span>'
        else:
            origin_badge = f'<span class="brk-desc-origin-badge propria">{get_svg_icon("shield", color=theme_color, size=12)} PRODUTO ORIGINAL</span>'

        header_html = f"""  <!-- Cabecalho Oficial com Origem e Marca -->
  <div class="brk-desc-header">
    {origin_badge}
    <h2 class="brk-desc-main-title">{formatted_title}</h2>
  </div>"""

        # 2. Aviso de Proteção de Estampas e Direitos Autorais (Camisas C0 - Posicionado no Final da Descrição)
        copyright_html = ""
        if show_copyright:
            copyright_html = """
  <!-- Aviso de Protecao de Estampas e Direitos Autorais (Camisas C0 - Final da Descricao) -->
  <div class="brk-desc-copyright-box">
    <div class="brk-copyright-text">
      <strong>Aviso de Propriedade Intelectual:</strong> Nossas estampas são protegidas pela Lei de Direitos Autorais (Lei 9.610/98) a Reprodução não autorizada está sujeita às penalidades legais. Copiar é crime !
    </div>
  </div>"""

        # 3. Os 3 Atos Narrativos
        blocks_html = []
        for idx, block in enumerate(blocks):
            is_reverse = (idx % 2 == 1)
            reverse_class = " reverse" if is_reverse else ""
            img_src = block.get("image") or "https://placehold.co/800x600?text=BRK+Foto+Oficial"
            tag_text = block.get("tag", "Destaque")
            tag_icon = self._get_tag_icon_name(tag_text)
            act_title = block.get("title", "").upper()
            act_desc = block.get("description", "")
            block_split_imgs = block.get("split_images") or (split_images if idx == 0 else None)
            
            # Layout de Mídia: Split para iscas/variações ou Imagem Única
            if block_split_imgs and len(block_split_imgs) >= 2:
                media_html = f"""<div class="brk-desc-media brk-desc-media-split">
        <div class="brk-split-item">
          <img src="{block_split_imgs[0]}" alt="{formatted_title} - Opção 1" loading="lazy" referrerpolicy="no-referrer" />
        </div>
        <div class="brk-split-item">
          <img src="{block_split_imgs[1]}" alt="{formatted_title} - Opção 2" loading="lazy" referrerpolicy="no-referrer" />
        </div>
      </div>"""
            elif img_src:
                media_html = f"""<div class="brk-desc-media">
        <img src="{img_src}" alt="{block.get('alt', formatted_title)}" loading="lazy" referrerpolicy="no-referrer" />
      </div>"""
            else:
                media_html = ""

            # Aviso de variações adicionais no primeiro bloco se houver
            var_notice_html = ""
            if idx == 0 and has_multiple_variations and variations_summary:
                var_notice_html = f"""
      <div class="brk-variations-notice">
        <span class="brk-var-icon">{get_svg_icon('palette', color=theme_color, size=15)}</span>
        <span class="brk-var-text">{variations_summary}</span>
      </div>"""

            if media_html:
                block_markup = f"""
  <!-- Ato {idx + 1}: {tag_text} -->
  <div class="brk-desc-block{reverse_class}">
    {media_html}
    <div class="brk-desc-text">
      <span class="brk-desc-tag">{get_svg_icon(tag_icon, color=theme_color, size=12)} {tag_text}</span>
      <h3 class="brk-desc-title">{act_title}</h3>
      <p class="brk-desc-paragraph">{act_desc}</p>{var_notice_html}
    </div>
  </div>"""
            else:
                block_markup = f"""
  <!-- Ato {idx + 1}: {tag_text} (Destaque Conceitual) -->
  <div class="brk-desc-block brk-desc-block-text-only">
    <div class="brk-desc-text" style="width: 100%; max-width: 100%;">
      <span class="brk-desc-tag">{get_svg_icon(tag_icon, color=theme_color, size=12)} {tag_text}</span>
      <h3 class="brk-desc-title">{act_title}</h3>
      <p class="brk-desc-paragraph">{act_desc}</p>{var_notice_html}
    </div>
  </div>"""
            blocks_html.append(block_markup)

        # 4. Especificações Técnicas no Grid Clássico BRK (Omitido para Camisas Agro e Motors)
        if specs and len(specs) > 0:
            specs_rows = []
            for spec in specs:
                specs_rows.append(f"""
      <div class="brk-spec-item">
        <span class="brk-spec-label"><span class="brk-bullet">{get_svg_icon('chevron', color=theme_color, size=9)}</span> {spec['label']}</span>
        <span class="brk-spec-value">{spec['value']}</span>
      </div>""")
            specs_markup = "".join(specs_rows)
            specs_section = f"""  <!-- Box de Especificacoes e Cuidados -->
  <div class="brk-desc-specs-box">
    <h4 class="brk-desc-specs-title">
      <span class="brk-title-icon">{get_svg_icon('clipboard', color=theme_color, size=16)}</span>
      <span>Ficha Técnica & Cuidados de Conservação</span>
    </h4>
    <div class="brk-specs-grid">{specs_markup}
    </div>

    <!-- Guia de Cuidados -->
    <div class="brk-desc-care-box">
      <span class="brk-care-icon">{get_svg_icon('care', color=theme_color, size=18)}</span>
      <div class="brk-care-text">
        <strong>Guia de Cuidados & Conservação da Peça:</strong> {care_tips}
      </div>
    </div>
  </div>"""
        else:
            specs_section = f"""  <!-- Guia de Cuidados (Ficha Técnica Descartada para Camisas Agro e Motors) -->
  <div class="brk-desc-care-box" style="margin-top: 36px;">
    <span class="brk-care-icon">{get_svg_icon('care', color=theme_color, size=18)}</span>
    <div class="brk-care-text">
      <strong>Guia de Cuidados & Conservação da Peça:</strong> {care_tips}
    </div>
  </div>"""

        # 5. Template Completo Encapsulado (100% Autônomo e sem Font Awesome)
        full_html = f"""<!-- BRK GROUP - DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL SHOPIFY) -->
<div class="brk-desc-wrapper">
  <style>
    .brk-desc-wrapper {{
      width: 100%;
      max-width: 980px;
      margin: 30px auto;
      padding: 0 10px;
      font-family: inherit;
      color: #1e293b;
      box-sizing: border-box;
      line-height: 1.5;
    }}
    .brk-desc-wrapper * {{
      box-sizing: border-box;
    }}

    /* Cabecalho de Origem e Titulo */
    .brk-desc-header {{
      margin-bottom: 32px;
      text-align: center;
      padding-bottom: 20px;
      border-bottom: 2px solid #e2e8f0;
    }}
    .brk-desc-origin-badge {{
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
    }}
    .brk-desc-origin-badge.propria {{
      color: {theme_color};
      background: {theme_bg};
      border: 1px solid {theme_color}35;
    }}
    .brk-desc-origin-badge.revenda {{
      color: #b45309;
      background: #fef3c7;
      border: 1px solid #fde68a;
    }}
    .brk-desc-main-title {{
      font-size: 26px;
      font-weight: 800;
      line-height: 1.25;
      color: #0f172a;
      margin: 0;
      letter-spacing: -0.4px;
    }}

    /* Aviso de Direitos Autorais em Camisas C0 (Amarelo sem icone no final) */
    .brk-desc-copyright-box {{
      background: #fffbeb;
      border-left: 4px solid #f59e0b;
      border-radius: 0 10px 10px 0;
      padding: 14px 18px;
      margin-top: 28px;
      border-top: 1px solid #fef3c7;
      border-right: 1px solid #fef3c7;
      border-bottom: 1px solid #fef3c7;
    }}
    .brk-copyright-text {{
      font-size: 12.5px;
      line-height: 1.55;
      color: #92400e;
    }}
    .brk-copyright-text strong {{
      color: #78350f;
    }}

    /* Atos Narrativos */
    .brk-desc-block {{
      display: flex;
      align-items: center;
      gap: 36px;
      margin-bottom: 42px;
    }}
    .brk-desc-block.reverse {{
      flex-direction: row-reverse;
    }}
    .brk-desc-block.brk-desc-block-text-only {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 24px 28px;
      margin-bottom: 34px;
    }}
    .brk-desc-media {{
      flex: 1;
      min-width: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .brk-desc-media img {{
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
    }}

    /* Midia Dividida para Iscas / Variacoes (Split Media) */
    .brk-desc-media-split {{
      display: flex;
      gap: 12px;
    }}
    .brk-desc-media-split .brk-split-item {{
      flex: 1;
      min-width: 0;
    }}
    .brk-desc-media-split .brk-split-item img {{
      max-height: 380px;
    }}

    .brk-desc-text {{
      flex: 1.15;
      min-width: 0;
    }}
    .brk-desc-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: {theme_color};
      background: {theme_bg};
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 10px;
      border: 1px solid {theme_color}25;
    }}
    .brk-desc-title {{
      font-size: 22px;
      font-weight: 800;
      line-height: 1.25;
      color: #0f172a;
      margin: 0 0 12px 0;
      text-transform: uppercase;
      letter-spacing: -0.3px;
    }}
    .brk-desc-paragraph {{
      font-size: 15px;
      line-height: 1.7;
      color: #475569;
      margin: 0;
    }}

    /* Aviso de Variacoes no Primeiro Bloco */
    .brk-variations-notice {{
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
    }}
    .brk-var-icon {{
      font-size: 16px;
    }}

    /* Box de Ficha Técnica & Cuidados */
    .brk-desc-specs-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 26px 24px;
      margin-top: 36px;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
    }}
    .brk-desc-specs-title {{
      font-size: 16px;
      font-weight: 800;
      color: #0f172a;
      margin: 0 0 18px 0;
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 12px;
      border-bottom: 2px solid #edf2f7;
    }}
    .brk-title-icon {{
      font-size: 18px;
    }}
    .brk-specs-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px 22px;
    }}
    .brk-spec-item {{
      display: flex;
      flex-direction: column;
      border-bottom: 1px dashed #e2e8f0;
      padding-bottom: 8px;
    }}
    .brk-spec-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .brk-bullet {{
      font-weight: 900;
      font-size: 13px;
    }}
    .brk-spec-value {{
      font-size: 13.5px;
      font-weight: 600;
      color: #0f172a;
      margin-top: 3px;
    }}

    /* Guia de Conservação */
    .brk-desc-care-box {{
      margin-top: 20px;
      background: #ffffff;
      border-left: 4px solid {theme_color};
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
    }}
    .brk-care-icon {{
      font-size: 20px;
      line-height: 1.2;
    }}
    .brk-care-text strong {{
      color: #0f172a;
    }}

    /* Rodapé de Confiança e Garantia BRK */
    .brk-desc-trust-bar {{
      margin-top: 32px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      text-align: center;
    }}
    .brk-svg-icon {{
      display: inline-block;
      vertical-align: -0.15em;
      flex-shrink: 0;
    }}
    .brk-trust-svg {{
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 2px;
      height: 28px;
    }}
    .brk-trust-item {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }}
    .brk-trust-title {{
      font-size: 12.5px;
      font-weight: 800;
      color: #0f172a;
    }}
    .brk-trust-desc {{
      font-size: 11px;
      color: #64748b;
      line-height: 1.3;
    }}

    /* Responsividade Mobile-First Blindada */
    @media (max-width: 768px) {{
      .brk-desc-main-title {{
        font-size: 20px;
      }}
      .brk-desc-block, .brk-desc-block.reverse {{
        flex-direction: column !important;
        gap: 16px;
        margin-bottom: 34px;
        text-align: left;
      }}
      .brk-desc-media-split {{
        flex-direction: row;
        gap: 8px;
      }}
      .brk-desc-title {{
        font-size: 18px;
      }}
      .brk-desc-paragraph {{
        font-size: 14px;
      }}
      .brk-specs-grid {{
        grid-template-columns: 1fr;
      }}
      .brk-desc-trust-bar {{
        grid-template-columns: 1fr;
        gap: 8px;
      }}
      .brk-trust-item {{
        flex-direction: row;
        text-align: left;
        padding: 12px 14px;
        gap: 12px;
      }}
    }}
  </style>

{header_html}

  <!-- 3 Atos Narrativos de Alta Conversão -->
  {"".join(blocks_html)}

{specs_section}

  <!-- Selos de Confiança e Garantia BRK -->
  <div class="brk-desc-trust-bar">
    <div class="brk-trust-item">
      <span class="brk-trust-svg">{get_svg_icon('shield', color=theme_color, size=24)}</span>
      <div>
        <div class="brk-trust-title">Qualidade Oficial BRK</div>
        <div class="brk-trust-desc">Matérias-primas nobres testadas</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <span class="brk-trust-svg">{get_svg_icon('truck', color=theme_color, size=24)}</span>
      <div>
        <div class="brk-trust-title">Envio Rápido & Seguro</div>
        <div class="brk-trust-desc">Rastreamento de ponta a ponta</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <span class="brk-trust-svg">{get_svg_icon('return', color=theme_color, size=24)}</span>
      <div>
        <div class="brk-trust-title">Troca Descomplicada</div>
        <div class="brk-trust-desc">Satisfação garantida ou seu dinheiro de volta</div>
      </div>
    </div>
  </div>

{copyright_html}

</div>
"""
        return full_html.strip()

    def build_shopify_markdown(self, enriched_data: Dict[str, Any]) -> str:
        """
        Compila a descrição em Markdown limpo, sem tags HTML externas e sem Font Awesome.
        """
        formatted_title = enriched_data.get("formatted_title") or enriched_data.get("title", "Produto BRK")
        show_copyright = enriched_data.get("show_copyright", False)
        has_multiple_variations = enriched_data.get("has_multiple_variations", False)
        split_images = enriched_data.get("split_images")
        variations_summary = enriched_data.get("variations_summary", "")
        blocks = enriched_data.get("narrative_blocks", [])
        if not blocks:
            acts = []
            for act_key in ["act1", "act2", "act3"]:
                if act_key in enriched_data and isinstance(enriched_data[act_key], dict):
                    acts.append(enriched_data[act_key])
            if acts:
                blocks = acts

        specs = enriched_data.get("specs", [])
        care_tips = enriched_data.get("care_tips", "Lavar à mão ou em ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar).")

        md_parts = []
        md_parts.append(f"# {formatted_title}\n")

        for idx, block in enumerate(blocks):
            tag_text = block.get("tag", f"Ato {idx+1}")
            tag_emoji = self._get_tag_emoji(tag_text)
            act_title = block.get("title", "").strip()
            act_desc = block.get("description", "").strip()
            img_src = block.get("image", "")

            md_parts.append(f"### {tag_emoji} {tag_text}: {act_title}\n")
            if img_src:
                md_parts.append(f"![{act_title}]({img_src})\n")
            
            block_split_imgs = block.get("split_images") or (split_images if idx == 0 else None)
            if block_split_imgs and len(block_split_imgs) >= 2:
                md_parts.append(f"![{act_title} - Detalhe 2]({block_split_imgs[1]})\n")

            md_parts.append(f"{act_desc}\n")

            if idx == 0 and has_multiple_variations and variations_summary:
                md_parts.append(f"*🎨 **Variações:** {variations_summary}*\n")

        if specs and len(specs) > 0:
            md_parts.append("### 📋 Ficha Técnica & Especificações\n")
            md_parts.append("| Característica | Especificação |")
            md_parts.append("| :--- | :--- |")
            for spec in specs:
                md_parts.append(f"| **{spec['label']}** | {spec['value']} |")
            md_parts.append("")

        md_parts.append("### 🧼 Guia de Cuidados & Conservação")
        md_parts.append(f"{care_tips}\n")

        md_parts.append("---")
        md_parts.append("- 🛡️ **Qualidade Oficial BRK:** Matérias-primas nobres testadas")
        md_parts.append("- 🚚 **Envio Rápido & Seguro:** Rastreamento de ponta a ponta")
        md_parts.append("- 🔄 **Troca Descomplicada:** Satisfação garantida ou seu dinheiro de volta")

        if show_copyright:
            md_parts.append("\n> **Aviso de Propriedade Intelectual:** Nossas estampas são protegidas pela Lei de Direitos Autorais (Lei 9.610/98) a Reprodução não autorizada está sujeita às penalidades legais. Copiar é crime !\n")

        return "\n".join(md_parts).strip()
