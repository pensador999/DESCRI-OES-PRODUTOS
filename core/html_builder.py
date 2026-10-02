"""
Compilador de HTML Verticalizado e Blindado para Shopify (Padrão Autêntico BRK com Font Awesome).
100% responsivo (Mobile e Desktop), sem risco de quebra de layout no tema Shopify.
Segue rigorosamente o padrão consagrado da marca:
- Abertura direta nos 3 Atos Narrativos (sem banners ou microcards no topo)
- Imagens 4:3 oficiais com bordas arredondadas e sombra sutil
- Títulos em CAIXA ALTA (UPPERCASE) de alto impacto
- Ícones 100% vetorizados da Font Awesome (zero emojis nativos de sistema)
- Ficha Técnica clássica em grid pontilhada elegante
- Selos de Confiança e Garantia BRK com Font Awesome
"""

from typing import Dict, Any, List

class HTMLBuilder:
    def __init__(self):
        pass

    def build_shopify_html(self, enriched_data: Dict[str, Any]) -> str:
        """
        Compila a descrição em 3 Atos e especificações no padrão autêntico BRK com Font Awesome.
        """
        title = enriched_data.get("title", "Produto BRK")
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
        care_icon = enriched_data.get("care_icon", "fa-solid fa-hand-sparkles")

        # 1. Os 3 Atos Narrativos (Abertura Direta)
        blocks_html = []
        for idx, block in enumerate(blocks):
            is_reverse = (idx % 2 == 1)
            reverse_class = " reverse" if is_reverse else ""
            img_src = block.get("image") or "https://placehold.co/800x600?text=BRK+Foto+Oficial"
            fa_icon = block.get("fa_icon", "fa-solid fa-circle-check")
            tag_text = block.get("tag", "Destaque")
            act_title = block.get("title", "").upper()
            act_desc = block.get("description", "")
            
            block_markup = f"""
  <!-- Ato {idx + 1}: {tag_text} -->
  <div class="brk-desc-block{reverse_class}">
    <div class="brk-desc-media">
      <img src="{img_src}" alt="{block.get('alt', title)}" loading="lazy" />
    </div>
    <div class="brk-desc-text">
      <span class="brk-desc-tag"><i class="{fa_icon}"></i> {tag_text}</span>
      <h3 class="brk-desc-title">{act_title}</h3>
      <p class="brk-desc-paragraph">{act_desc}</p>
    </div>
  </div>"""
            blocks_html.append(block_markup)

        # 2. Especificações Técnicas no Grid Clássico BRK (Omitido para Camisas Agro e Motors)
        if specs and len(specs) > 0:
            specs_rows = []
            for spec in specs:
                specs_rows.append(f"""
      <div class="brk-spec-item">
        <span class="brk-spec-label"><i class="fa-solid fa-angle-right" style="color: {theme_color}; font-size: 10px;"></i> {spec['label']}</span>
        <span class="brk-spec-value">{spec['value']}</span>
      </div>""")
            specs_markup = "".join(specs_rows)
            specs_section = f"""  <!-- Box de Especificacoes e Cuidados -->
  <div class="brk-desc-specs-box">
    <h4 class="brk-desc-specs-title">
      <i class="fa-solid fa-list-check" style="color: {theme_color};"></i>
      <span>Ficha Técnica & Cuidados de Conservação</span>
    </h4>
    <div class="brk-specs-grid">{specs_markup}
    </div>

    <!-- Guia de Cuidados -->
    <div class="brk-desc-care-box">
      <i class="{care_icon}" style="color: {theme_color}; margin-right: 8px;"></i>
      <strong>Guia de Cuidados & Conservação da Peça:</strong> {care_tips}
    </div>
  </div>"""
        else:
            # Ficha técnica descartada para camisas Agro e Motors conforme diretriz
            specs_section = f"""  <!-- Guia de Cuidados (Ficha Técnica Descartada para Camisas Agro e Motors) -->
  <div class="brk-desc-care-box" style="margin-top: 36px;">
    <i class="{care_icon}" style="color: {theme_color}; margin-right: 8px;"></i>
    <strong>Guia de Cuidados & Conservação da Peça:</strong> {care_tips}
  </div>"""

        # 3. Template Completo Encapsulado (Padrão Autêntico BRK)
        full_html = f"""<!-- BRK GROUP - DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL SHOPIFY) -->
<div class="brk-desc-wrapper">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
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
      font-size: 23px;
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
    }}
    .brk-desc-care-box strong {{
      color: #0f172a;
    }}

    /* Rodapé de Confiança e Garantia BRK com Font Awesome */
    .brk-desc-trust-bar {{
      margin-top: 32px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      text-align: center;
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
    .brk-trust-icon {{
      font-size: 22px;
      color: {theme_color};
      margin-bottom: 2px;
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
      .brk-desc-block, .brk-desc-block.reverse {{
        flex-direction: column !important;
        gap: 16px;
        margin-bottom: 34px;
        text-align: left;
      }}
      .brk-desc-title {{
        font-size: 19px;
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
      .brk-trust-icon {{
        font-size: 20px;
        margin-bottom: 0;
      }}
    }}
  </style>

  <!-- 3 Atos Narrativos de Alta Conversão -->
  {"".join(blocks_html)}

{specs_section}

  <!-- Selos de Confiança e Garantia BRK (Font Awesome) -->
  <div class="brk-desc-trust-bar">
    <div class="brk-trust-item">
      <i class="fa-solid fa-circle-check brk-trust-icon"></i>
      <div>
        <div class="brk-trust-title">Qualidade Oficial BRK</div>
        <div class="brk-trust-desc">Matérias-primas nobres testadas</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <i class="fa-solid fa-truck-fast brk-trust-icon"></i>
      <div>
        <div class="brk-trust-title">Envio Rápido & Seguro</div>
        <div class="brk-trust-desc">Rastreamento de ponta a ponta</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <i class="fa-solid fa-arrow-rotate-left brk-trust-icon"></i>
      <div>
        <div class="brk-trust-title">Troca Descomplicada</div>
        <div class="brk-trust-desc">Satisfação garantida ou seu dinheiro de volta</div>
      </div>
    </div>
  </div>

</div>
"""
        return full_html.strip()
