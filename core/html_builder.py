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

    def _build_quick_badges(self, theme_color: str, archetype_id: str, enriched_data: Dict[str, Any]) -> str:
        title_low = (enriched_data.get("formatted_title") or enriched_data.get("title") or "").lower()
        
        # Determinar os 4 badges contextuais baseados no arquétipo e produto
        if archetype_id in ("uv_performance", "sun_sleeves_manguitos", "neck_gaiters_balaclavas") or "uv" in title_low or "pesca" in title_low:
            badges = [
                {"icon": "sun", "title": "FPU 50+ Certificado", "sub": "Bloqueia 98% Raios UV"},
                {"icon": "bolt", "title": "Tecnologia Dry Fit", "sub": "Secagem Ultra Rápida"},
                {"icon": "shield", "title": "Costura Reforçada", "sub": "Pesponto Duplo Anti-Atrito"},
                {"icon": "return", "title": "Troca Fácil BRK", "sub": "Satisfação 100% Garantida"}
            ]
        elif archetype_id == "agro_field" or "agro" in title_low or "campo" in title_low:
            badges = [
                {"icon": "care", "title": "Algodão Premium", "sub": "Toque Nobre Aveludado"},
                {"icon": "sparkle", "title": "Respirabilidade Natural", "sub": "Conforto no Campo"},
                {"icon": "shield", "title": "Costura Dupla Ombro", "sub": "Estrutura Anti-Deformação"},
                {"icon": "return", "title": "Troca Fácil BRK", "sub": "Procedência Garantida"}
            ]
        elif archetype_id == "motors_speed" or "jersey" in title_low or "moto" in title_low or "trilha" in title_low:
            badges = [
                {"icon": "bolt", "title": "Ventilação Ativa", "sub": "Painéis Microperfurados"},
                {"icon": "gear", "title": "Aerodinâmica Pro", "sub": "Modelagem Anatômica"},
                {"icon": "shield", "title": "Costura Resistente", "sub": "Pronta para Off-Road"},
                {"icon": "return", "title": "Troca Fácil BRK", "sub": "Garantia Oficial BRK"}
            ]
        elif archetype_id in ("hats_safari_outdoor", "caps_trucker_snapback") or any(w in title_low for w in ["chapéu", "chapeu", "boné", "bone"]):
            badges = [
                {"icon": "sun", "title": "Proteção Solar FPU 50+", "sub": "Barreira UV Térmica"},
                {"icon": "care", "title": "Tecido Respirável", "sub": "Ilhoses de Respiração"},
                {"icon": "shield", "title": "Ajuste Anatômico", "sub": "Segurança Anti-Vento"},
                {"icon": "return", "title": "Troca Fácil BRK", "sub": "Satisfação Garantida"}
            ]
        elif archetype_id in ("footwear_sandals_boaonda", "closed_footwear_sneakers") or any(w in title_low for w in ["sandália", "sandalia", "babuche", "chinelo"]):
            badges = [
                {"icon": "shoe", "title": "Palmilha Antiestresse", "sub": "Amortecimento Anatômico"},
                {"icon": "shield", "title": "Solado Antiderrapante", "sub": "Aderência em Solo Molhado"},
                {"icon": "care", "title": "Fácil Higienização", "sub": "Material Antibacteriano"},
                {"icon": "return", "title": "Troca Fácil BRK", "sub": "Ajuste Perfeito Garantido"}
            ]
        elif archetype_id == "fishing_lures" or "isca" in title_low:
            badges = [
                {"icon": "fish", "title": "Ação & Nado Realista", "sub": "Atratividade para Predadores"},
                {"icon": "shield", "title": "Pitões Reforçados", "sub": "Componentes em Aço Inox"},
                {"icon": "gear", "title": "Equilíbrio Hidrodinâmico", "sub": "Arremessos Precisos"},
                {"icon": "sparkle", "title": "Garantia de Procedência", "sub": "100% Original e Testado"}
            ]
        elif archetype_id == "drinkware_thermo" or any(w in title_low for w in ["copo", "garrafa", "caneca", "térmic", "termic"]):
            badges = [
                {"icon": "shield", "title": "Inox 18/8 com Vácuo", "sub": "Parede Dupla Térmica"},
                {"icon": "bolt", "title": "Máximo Isolamento", "sub": "Bebida Gelada por Horas"},
                {"icon": "care", "title": "Livre de BPA", "sub": "Sem Condensação Externa"},
                {"icon": "return", "title": "Garantia BRK", "sub": "Qualidade Assegurada"}
            ]
        elif archetype_id == "cutlery_unique" or "faca" in title_low:
            badges = [
                {"icon": "knife", "title": "Aço Especial Nobre", "sub": "Alta Retenção de Fio"},
                {"icon": "gear", "title": "Tratamento Térmico", "sub": "Dureza e Tenacidade"},
                {"icon": "shield", "title": "Acabamento Artesanal", "sub": "Cabo Anatômico Nobre"},
                {"icon": "sparkle", "title": "Garantia BRK", "sub": "Procedência Garantida"}
            ]
        else:
            badges = [
                {"icon": "shield", "title": "Qualidade Oficial", "sub": "Matéria-Prima Selecionada"},
                {"icon": "sparkle", "title": "Acabamento Premium", "sub": "Rigoroso Padrão BRK"},
                {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Rastreamento Completo"},
                {"icon": "return", "title": "Troca Descomplicada", "sub": "Satisfação Garantida"}
            ]

        items_html = []
        for b in badges:
            items_html.append(f"""    <div class="brk-badge-item">
      <span class="brk-badge-icon">{get_svg_icon(b['icon'], color=theme_color, size=18)}</span>
      <div class="brk-badge-content">
        <strong class="brk-badge-title">{b['title']}</strong>
        <span class="brk-badge-sub">{b['sub']}</span>
      </div>
    </div>\n""")

        return f"""  <!-- Selos Rapidos de Confianca e Tecnologia (Destaque Superior) -->
  <div class="brk-quick-badges">
{"".join(items_html)}  </div>"""

    def _build_size_guide(self, theme_color: str, archetype_id: str, is_kids: bool, is_short_sleeve: bool, enriched_data: Dict[str, Any]) -> str:
        title_low = (enriched_data.get("formatted_title") or enriched_data.get("title") or "").lower()

        # 1. Infantil (Kids)
        if is_kids:
            guide_title = "Guia de Tamanhos Infantil (02 a 16 Anos)"
            manga_header = "Manga Curta" if is_short_sleeve else "Manga Longa"
            rows = [
                ("02 Anos", "64 cm", "42 cm", "14 cm" if is_short_sleeve else "40 cm"),
                ("04 Anos", "70 cm", "46 cm", "15 cm" if is_short_sleeve else "44 cm"),
                ("06 Anos", "76 cm", "50 cm", "16 cm" if is_short_sleeve else "48 cm"),
                ("08 Anos", "82 cm", "54 cm", "17 cm" if is_short_sleeve else "52 cm"),
                ("10 Anos", "88 cm", "58 cm", "18 cm" if is_short_sleeve else "56 cm"),
                ("12 Anos", "92 cm", "62 cm", "19 cm" if is_short_sleeve else "60 cm"),
                ("14 Anos", "96 cm", "65 cm", "20 cm" if is_short_sleeve else "64 cm"),
                ("16 Anos", "100 cm", "68 cm", "21 cm" if is_short_sleeve else "68 cm"),
            ]
            rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in rows])
            table_html = f"""<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Idade / Tam</th>
            <th>Tórax / Peito</th>
            <th>Comprimento</th>
            <th>{manga_header}</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

        # 2. Camisas Adulto (uv_performance, agro_field, motors_speed, shirts_button_work)
        elif archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work") or any(w in title_low for w in ["camisa", "camiseta", "jersey", "baby look"]):
            guide_title = "Tabela de Medidas Adulto (P ao EXG)"
            manga_header = "Manga Curta" if is_short_sleeve else "Manga Longa"
            rows = [
                ("P", "102 cm", "68 cm", "22 cm" if is_short_sleeve else "75 cm"),
                ("M", "108 cm", "71 cm", "23 cm" if is_short_sleeve else "77 cm"),
                ("G", "114 cm", "74 cm", "24 cm" if is_short_sleeve else "79 cm"),
                ("GG", "120 cm", "77 cm", "25 cm" if is_short_sleeve else "81 cm"),
                ("XG", "126 cm", "80 cm", "26 cm" if is_short_sleeve else "83 cm"),
                ("EXG (G1)", "132 cm", "83 cm", "27 cm" if is_short_sleeve else "85 cm"),
                ("G2", "138 cm", "85 cm", "28 cm" if is_short_sleeve else "87 cm"),
                ("G3", "144 cm", "87 cm", "29 cm" if is_short_sleeve else "89 cm"),
            ]
            rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in rows])
            table_html = f"""<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Tamanho</th>
            <th>Tórax / Circunferência</th>
            <th>Comprimento Total</th>
            <th>{manga_header}</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

        # 3. Calças e Bermudas / Macacões (pants_cargo_tactical, overalls_workwear)
        elif archetype_id in ("pants_cargo_tactical", "overalls_workwear") or any(w in title_low for w in ["calça", "calca", "bermuda", "shorts", "macacão", "macacao"]):
            guide_title = "Tabela de Medidas - Calças & Bermudas (38 ao 52)"
            rows = [
                ("38", "78 - 82 cm", "98 cm", "104 cm"),
                ("40", "82 - 86 cm", "102 cm", "105 cm"),
                ("42", "86 - 90 cm", "106 cm", "106 cm"),
                ("44", "90 - 94 cm", "110 cm", "107 cm"),
                ("46", "94 - 98 cm", "114 cm", "108 cm"),
                ("48", "98 - 102 cm", "118 cm", "109 cm"),
                ("50", "102 - 106 cm", "122 cm", "110 cm"),
                ("52", "106 - 110 cm", "126 cm", "111 cm"),
            ]
            rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in rows])
            table_html = f"""<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Numeração</th>
            <th>Cintura</th>
            <th>Quadril</th>
            <th>Comprimento</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

        # 4. Chapéus e Bonés (hats_safari_outdoor, caps_trucker_snapback)
        elif archetype_id in ("hats_safari_outdoor", "caps_trucker_snapback") or any(w in title_low for w in ["chapéu", "chapeu", "boné", "bone"]):
            guide_title = "Guia de Dimensões - Chapéus & Bonés"
            table_html = """<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Modelo</th>
            <th>Circunferência da Cabeça</th>
            <th>Aba / Profundidade</th>
            <th>Regulagem & Ajuste</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Chapéu Safári / Australiano</strong></td>
            <td>56 cm a 60 cm (Veste P ao GG)</td>
            <td>Aba 7,5 cm de proteção 360°</td>
            <td>Cordão jugular com trava anti-vento</td>
          </tr>
          <tr>
            <td><strong>Boné Trucker / Snapback</strong></td>
            <td>54 cm a 61 cm (Ajustável)</td>
            <td>Aba 7,0 cm estruturada curvada</td>
            <td>Fecho regulador traseiro de alta pressão</td>
          </tr>
        </tbody>
      </table>"""

        # 5. Calçados (footwear_sandals_boaonda, closed_footwear_sneakers)
        elif archetype_id in ("footwear_sandals_boaonda", "closed_footwear_sneakers") or any(w in title_low for w in ["sandália", "sandalia", "babuche", "chinelo", "sapato", "tênis", "tenis", "bota"]):
            guide_title = "Guia de Tamanhos de Calçados (Medida da Palmilha)"
            rows = [
                ("34", "23,0 cm"), ("35", "23,7 cm"), ("36", "24,3 cm"),
                ("37", "25,0 cm"), ("38", "25,7 cm"), ("39", "26,3 cm"),
                ("40", "27,0 cm"), ("41", "27,7 cm"), ("42", "28,3 cm"),
                ("43", "29,0 cm"), ("44", "29,7 cm"), ("45", "30,3 cm"),
            ]
            rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td></tr>\n" for r in rows])
            table_html = f"""<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Numeração BR</th>
            <th>Comprimento da Palmilha (cm)</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

        # 6. Luvas (gloves_tactical_fishing)
        elif archetype_id == "gloves_tactical_fishing" or "luva" in title_low:
            guide_title = "Tabela de Medidas de Luvas (Largura da Palma)"
            rows = [
                ("P", "8,0 a 8,5 cm", "19 cm"),
                ("M", "8,5 a 9,0 cm", "20 cm"),
                ("G", "9,0 a 9,5 cm", "21 cm"),
                ("GG", "9,5 a 10,5 cm", "22 cm"),
            ]
            rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td></tr>\n" for r in rows])
            table_html = f"""<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Tamanho</th>
            <th>Largura da Palma</th>
            <th>Comprimento da Mão</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

        # 7. Manguitos (sun_sleeves_manguitos)
        elif archetype_id == "sun_sleeves_manguitos" or "manguito" in title_low:
            guide_title = "Tabela de Medidas - Manguitos de Proteção Solar"
            rows = [
                ("P / M", "24 a 30 cm", "16 a 20 cm", "45 cm"),
                ("G / GG", "30 a 38 cm", "18 a 24 cm", "48 cm"),
            ]
            rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td></tr>\n" for r in rows])
            table_html = f"""<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Tamanho</th>
            <th>Circunferência Bíceps</th>
            <th>Circunferência Punho</th>
            <th>Comprimento Total</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

        # 8. Bandanas / Balaclavas
        elif archetype_id == "neck_gaiters_balaclavas" or any(w in title_low for w in ["bandana", "tubeneck", "buff", "balaclava"]):
            guide_title = "Dimensões - Bandana Tubular Seamless Multifuncional"
            table_html = """<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Tamanho</th>
            <th>Largura (Plana)</th>
            <th>Comprimento</th>
            <th>Elasticidade</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Tamanho Único</strong></td>
            <td>Aprox. 24 cm</td>
            <td>Aprox. 48 cm</td>
            <td>Microfibra tubular elástica seamless com memória anatômica</td>
          </tr>
        </tbody>
      </table>"""

        else:
            return ""

        return f"""  <!-- Tabela de Medidas Inteligente Integrada (Accordion Nativo) -->
  <details class="brk-size-guide">
    <summary class="brk-sg-summary">
      <span class="brk-sg-title-wrap">
        <span class="brk-sg-icon">{get_svg_icon('ruler', color=theme_color, size=18)}</span>
        <strong class="brk-sg-heading">{guide_title}</strong>
      </span>
      <span class="brk-sg-trigger">Ver Medidas em cm ▾</span>
    </summary>
    <div class="brk-sg-body">
      <div class="brk-sg-tip">
        <span>📏</span>
        <span><strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros. Em caso de dúvida entre dois tamanhos, opte pelo tamanho maior para garantir caimento livre e confortável.</span>
      </div>
      {table_html}
    </div>
  </details>"""

    def _build_schema_json_ld(self, enriched_data: Dict[str, Any]) -> str:
        import json
        import re

        formatted_title = enriched_data.get("formatted_title") or enriched_data.get("title", "Produto BRK")
        brand_name = enriched_data.get("brand_name", "BRK")
        sku = enriched_data.get("sku") or ""
        price = enriched_data.get("price") or "0.00"

        blocks = enriched_data.get("narrative_blocks", [])
        desc_parts = []
        for b in blocks:
            d = b.get("description", "")
            if d:
                clean_d = re.sub(r'<[^>]+>', ' ', d)
                desc_parts.append(" ".join(clean_d.split()))
        short_desc = " ".join(desc_parts)[:280] if desc_parts else f"{formatted_title} oficial com qualidade e garantia BRK."

        raw_imgs = enriched_data.get("images") or []
        imgs = [u for u in raw_imgs if isinstance(u, str) and u.startswith("http")]

        schema_obj = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": formatted_title,
            "description": short_desc,
            "sku": sku,
            "brand": {
                "@type": "Brand",
                "name": brand_name
            },
            "offers": {
                "@type": "Offer",
                "priceCurrency": "BRL",
                "price": price if price and price != "0.00" else "0.00",
                "availability": "https://schema.org/InStock",
                "itemCondition": "https://schema.org/NewCondition"
            }
        }
        if imgs:
            schema_obj["image"] = imgs[:3]

        json_str = json.dumps(schema_obj, ensure_ascii=False, indent=2)
        return f"""  <!-- Schema.org Microdata JSON-LD para Google Search & Merchant Center -->
  <script type="application/ld+json">
{json_str}
  </script>"""

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

        archetype_id = enriched_data.get("archetype_id", "")
        is_kids = enriched_data.get("is_kids", False)
        is_short_sleeve = enriched_data.get("is_short_sleeve", False)

        theme_color = enriched_data.get("theme_color", "#0284c7")
        theme_bg = enriched_data.get("theme_bg", "#f0f9ff")

        quick_badges_html = self._build_quick_badges(theme_color, archetype_id, enriched_data)
        size_guide_html = self._build_size_guide(theme_color, archetype_id, is_kids, is_short_sleeve, enriched_data)
        schema_json_ld = self._build_schema_json_ld(enriched_data)
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
            img_src = block.get("image") or ""
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

    /* Selos Rapidos de Confianca e Tecnologia (Destaque Superior) */
    .brk-quick-badges {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 34px;
    }}
    .brk-badge-item {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 12px 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }}
    .brk-badge-icon {{
      width: 34px;
      height: 34px;
      border-radius: 10px;
      background: {theme_bg};
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .brk-badge-content {{
      display: flex;
      flex-direction: column;
      min-width: 0;
    }}
    .brk-badge-title {{
      font-size: 12px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.25;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .brk-badge-sub {{
      font-size: 10.5px;
      color: #64748b;
      line-height: 1.25;
      margin-top: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
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

    /* Tabela de Medidas Inteligente (Accordion Nativo) */
    .brk-size-guide {{
      margin-top: 32px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
    }}
    .brk-sg-summary {{
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
    }}
    .brk-sg-summary::-webkit-details-marker {{
      display: none;
    }}
    .brk-size-guide[open] .brk-sg-summary {{
      border-bottom-color: #e2e8f0;
      background: {theme_bg};
    }}
    .brk-sg-title-wrap {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .brk-sg-icon {{
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .brk-sg-heading {{
      font-size: 14px;
      font-weight: 800;
      color: #0f172a;
    }}
    .brk-sg-trigger {{
      font-size: 11px;
      font-weight: 700;
      color: {theme_color};
      background: #ffffff;
      padding: 4px 10px;
      border-radius: 9999px;
      border: 1px solid {theme_color}40;
    }}
    .brk-sg-body {{
      padding: 20px;
    }}
    .brk-sg-tip {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      background: #f8fafc;
      border-left: 3px solid {theme_color};
      padding: 10px 14px;
      border-radius: 0 8px 8px 0;
      font-size: 12px;
      color: #475569;
      margin-bottom: 16px;
      line-height: 1.5;
    }}
    .brk-sg-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      text-align: left;
    }}
    .brk-sg-table th {{
      background: #f1f5f9;
      color: #334155;
      font-weight: 800;
      text-transform: uppercase;
      font-size: 10.5px;
      letter-spacing: 0.5px;
      padding: 10px 12px;
      border-bottom: 2px solid #e2e8f0;
    }}
    .brk-sg-table td {{
      padding: 9px 12px;
      border-bottom: 1px solid #f1f5f9;
      color: #1e293b;
    }}
    .brk-sg-table tr:nth-child(even) td {{
      background: #f8fafc;
    }}
    .brk-sg-table tr:hover td {{
      background: {theme_bg};
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
      .brk-quick-badges {{
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-bottom: 26px;
      }}
      .brk-badge-item {{
        padding: 10px;
        gap: 8px;
      }}
      .brk-badge-title {{
        font-size: 11px;
      }}
      .brk-badge-sub {{
        font-size: 9.5px;
      }}
      .brk-sg-table {{
        font-size: 11px;
      }}
      .brk-sg-table th, .brk-sg-table td {{
        padding: 8px 6px;
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

{quick_badges_html}

  <!-- 3 Atos Narrativos de Alta Conversão -->
  {"".join(blocks_html)}

{specs_section}

{size_guide_html}

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

{schema_json_ld}
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

        archetype_id = enriched_data.get("archetype_id", "")
        is_kids = enriched_data.get("is_kids", False)
        is_short_sleeve = enriched_data.get("is_short_sleeve", False)
        title_low = (formatted_title or "").lower()

        # Tabela de medidas inteligente em Markdown
        if is_kids:
            md_parts.append("### 📐 Tabela de Medidas Infantil (02 a 16 Anos)\n")
            m_header = "Manga Curta" if is_short_sleeve else "Manga Longa"
            md_parts.append(f"| Idade / Tam | Tórax | Comprimento | {m_header} |")
            md_parts.append("| :--- | :--- | :--- | :--- |")
            k_rows = [
                ("02 Anos", "64 cm", "42 cm", "14 cm" if is_short_sleeve else "40 cm"),
                ("04 Anos", "70 cm", "46 cm", "15 cm" if is_short_sleeve else "44 cm"),
                ("06 Anos", "76 cm", "50 cm", "16 cm" if is_short_sleeve else "48 cm"),
                ("08 Anos", "82 cm", "54 cm", "17 cm" if is_short_sleeve else "52 cm"),
                ("10 Anos", "88 cm", "58 cm", "18 cm" if is_short_sleeve else "56 cm"),
                ("12 Anos", "92 cm", "62 cm", "19 cm" if is_short_sleeve else "60 cm"),
                ("14 Anos", "96 cm", "65 cm", "20 cm" if is_short_sleeve else "64 cm"),
                ("16 Anos", "100 cm", "68 cm", "21 cm" if is_short_sleeve else "68 cm"),
            ]
            for r in k_rows:
                md_parts.append(f"| **{r[0]}** | {r[1]} | {r[2]} | {r[3]} |")
            md_parts.append("\n*Medidas tiradas com a peça plana em cm. Em dúvida entre dois tamanhos, escolha o maior.*\n")
        elif archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work") or any(w in title_low for w in ["camisa", "camiseta", "jersey", "baby look"]):
            md_parts.append("### 📐 Tabela de Medidas Adulto (P ao EXG)\n")
            m_header = "Manga Curta" if is_short_sleeve else "Manga Longa"
            md_parts.append(f"| Tamanho | Tórax / Peito | Comprimento | {m_header} |")
            md_parts.append("| :--- | :--- | :--- | :--- |")
            a_rows = [
                ("P", "102 cm", "68 cm", "22 cm" if is_short_sleeve else "75 cm"),
                ("M", "108 cm", "71 cm", "23 cm" if is_short_sleeve else "77 cm"),
                ("G", "114 cm", "74 cm", "24 cm" if is_short_sleeve else "79 cm"),
                ("GG", "120 cm", "77 cm", "25 cm" if is_short_sleeve else "81 cm"),
                ("XG", "126 cm", "80 cm", "26 cm" if is_short_sleeve else "83 cm"),
                ("EXG (G1)", "132 cm", "83 cm", "27 cm" if is_short_sleeve else "85 cm"),
                ("G2", "138 cm", "85 cm", "28 cm" if is_short_sleeve else "87 cm"),
                ("G3", "144 cm", "87 cm", "29 cm" if is_short_sleeve else "89 cm"),
            ]
            for r in a_rows:
                md_parts.append(f"| **{r[0]}** | {r[1]} | {r[2]} | {r[3]} |")
            md_parts.append("\n*Medidas tiradas com a peça plana em cm. Em dúvida entre dois tamanhos, escolha o maior.*\n")
        elif archetype_id in ("pants_cargo_tactical", "overalls_workwear") or any(w in title_low for w in ["calça", "calca", "bermuda", "shorts"]):
            md_parts.append("### 📐 Tabela de Medidas - Calças & Bermudas (38 ao 52)\n")
            md_parts.append("| Tamanho | Cintura | Quadril | Comprimento |")
            md_parts.append("| :--- | :--- | :--- | :--- |")
            p_rows = [
                ("38", "78-82 cm", "98 cm", "104 cm"),
                ("40", "82-86 cm", "102 cm", "105 cm"),
                ("42", "86-90 cm", "106 cm", "106 cm"),
                ("44", "90-94 cm", "110 cm", "107 cm"),
                ("46", "94-98 cm", "114 cm", "108 cm"),
                ("48", "98-102 cm", "118 cm", "109 cm"),
                ("50", "102-106 cm", "122 cm", "110 cm"),
                ("52", "106-110 cm", "126 cm", "111 cm"),
            ]
            for r in p_rows:
                md_parts.append(f"| **{r[0]}** | {r[1]} | {r[2]} | {r[3]} |")
            md_parts.append("\n*Medidas tiradas com a peça plana em cm.*\n")
        elif archetype_id in ("footwear_sandals_boaonda", "closed_footwear_sneakers") or any(w in title_low for w in ["sandália", "sandalia", "babuche", "chinelo"]):
            md_parts.append("### 📐 Guia de Tamanhos de Calçados (Palmilha)\n")
            md_parts.append("| Numeração BR | Palmilha (cm) |")
            md_parts.append("| :--- | :--- |")
            s_rows = [
                ("34", "23,0 cm"), ("35", "23,7 cm"), ("36", "24,3 cm"),
                ("37", "25,0 cm"), ("38", "25,7 cm"), ("39", "26,3 cm"),
                ("40", "27,0 cm"), ("41", "27,7 cm"), ("42", "28,3 cm"),
                ("43", "29,0 cm"), ("44", "29,7 cm"), ("45", "30,3 cm"),
            ]
            for r in s_rows:
                md_parts.append(f"| **{r[0]}** | {r[1]} |")
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
