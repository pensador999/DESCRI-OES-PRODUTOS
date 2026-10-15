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

import re
from typing import Dict, Any, List

try:
    from core.svg_icons import get_svg_icon
except ImportError:
    try:
        from svg_icons import get_svg_icon
    except ImportError:
        def get_svg_icon(name: str, color: str = "currentColor", size: int = 16, extra_class: str = "") -> str:
            return ""

# Versao do padrao Modo B. Ao evoluir moldes/layout, incremente: o catalogo ao vivo
# passa a listar como "Desatualizado" tudo que estiver colado com versao anterior.
MODO_B_VERSION = "1"


def brk_tracking_marker(sku: str, archetype_id: str) -> str:
    """Comentario HTML invisivel de rastreio: <!-- BRK-MODO-B v1 | sku:X | molde:Y -->"""
    def clean(v):
        return re.sub(r"[^A-Za-z0-9_.\-]", "", str(v or ""))[:60].replace("--", "-")
    return f"<!-- BRK-MODO-B v{MODO_B_VERSION} | sku:{clean(sku)} | molde:{clean(archetype_id)} -->"


_TROCA = {"icon": "return", "title": "Troca Fácil BRK", "sub": "Satisfação 100% Garantida"}

# Quick Badges por ARQUÉTIPO (fonte única de verdade).
# REGRA DE OURO: o arquétipo detectado decide os selos; palavras soltas do título
# (ex.: "pesca" em "Vara de Pesca") NUNCA podem ativar selos de outra categoria.
# Cada selo só afirma o que o molde (core/template_engine.py) já afirma na ficha técnica.
QUICK_BADGES_BY_ARCHETYPE: Dict[str, List[Dict[str, str]]] = {
    # --- Vestuário superior ---
    "uv_performance": [
        {"icon": "sun", "title": "FPU 50+ Certificado", "sub": "Bloqueia 98% Raios UV"},
        {"icon": "bolt", "title": "Tecnologia Dry Fit", "sub": "Secagem Ultra Rápida"},
        {"icon": "shield", "title": "Costura Reforçada", "sub": "Pesponto Duplo Anti-Atrito"},
        _TROCA,
    ],
    "agro_field": [
        {"icon": "care", "title": "Algodão Premium", "sub": "Toque Nobre Aveludado"},
        {"icon": "sparkle", "title": "Respirabilidade Natural", "sub": "Conforto o Dia Todo"},
        {"icon": "shield", "title": "Costura Dupla Ombro", "sub": "Estrutura Anti-Deformação"},
        {"icon": "return", "title": "Troca Fácil BRK", "sub": "Procedência Garantida"},
    ],
    "motors_speed": [
        {"icon": "bolt", "title": "Ventilação Ativa", "sub": "Painéis Microperfurados"},
        {"icon": "gear", "title": "Aerodinâmica Pro", "sub": "Modelagem Anatômica"},
        {"icon": "shield", "title": "Costura Resistente", "sub": "Pronta para Off-Road"},
        {"icon": "return", "title": "Troca Fácil BRK", "sub": "Garantia Oficial BRK"},
    ],
    "shirts_button_work": [
        {"icon": "shield", "title": "Abotoamento Reforçado", "sub": "Botões com Costura em X"},
        {"icon": "box", "title": "Bolsos Utilitários", "sub": "Funcionais no Peito"},
        {"icon": "care", "title": "Colarinho Estruturado", "sub": "Postura o Dia Todo"},
        _TROCA,
    ],
    # --- Vestuário inferior / macacões ---
    "pants_cargo_tactical": [
        {"icon": "shield", "title": "Tecido Alta Gramatura", "sub": "Resistente ao Atrito"},
        {"icon": "gear", "title": "Costuras Reforçadas", "sub": "Travetes de Alta Tensão"},
        {"icon": "box", "title": "Bolsos Funcionais", "sub": "Profundos e Estruturados"},
        _TROCA,
    ],
    "overalls_workwear": [
        {"icon": "shield", "title": "100% Impermeável", "sub": "Termossoldagem Estanque"},
        {"icon": "shoe", "title": "Bota Integrada", "sub": "Solado Tratorado Firme"},
        {"icon": "gear", "title": "Alças Reguláveis", "sub": "Engate Rápido"},
        _TROCA,
    ],
    # --- Acessórios de proteção solar ---
    "sun_sleeves_manguitos": [
        {"icon": "sun", "title": "FPU 50+ Permanente", "sub": "Proteção Solar Certificada"},
        {"icon": "bolt", "title": "Tecnologia Dry Fit", "sub": "Evaporação do Suor"},
        {"icon": "shield", "title": "Fixação Anatômica", "sub": "Ajuste Firme no Braço"},
        _TROCA,
    ],
    "neck_gaiters_balaclavas": [
        {"icon": "sun", "title": "FPU 50+ Permanente", "sub": "Bloqueador de Radiação"},
        {"icon": "shield", "title": "Toque Frio Anti-Atrito", "sub": "Conforto e Respirabilidade"},
        {"icon": "bolt", "title": "Secagem Ultra Rápida", "sub": "Tecido Tecnológico Leve"},
        _TROCA,
    ],
    "gloves_tactical_fishing": [
        {"icon": "shield", "title": "Palma Antiderrapante", "sub": "Alta Aderência e Grip"},
        {"icon": "bolt", "title": "Dorso Respirável", "sub": "Secagem Ultra Rápida"},
        {"icon": "gear", "title": "Encaixe Anatômico", "sub": "Firmeza no Pulso"},
        _TROCA,
    ],
    # --- Chapéus e bonés ---
    "hats_safari_outdoor": [
        {"icon": "sun", "title": "Proteção Solar FPU 50+", "sub": "Barreira UV Térmica"},
        {"icon": "care", "title": "Tecido Respirável", "sub": "Ilhoses de Respiração"},
        {"icon": "shield", "title": "Ajuste Anatômico", "sub": "Segurança Anti-Vento"},
        {"icon": "return", "title": "Troca Fácil BRK", "sub": "Satisfação Garantida"},
    ],
    "hats_country_cowboy": [
        {"icon": "shield", "title": "Copa Estruturada", "sub": "Aba com Retenção de Formato"},
        {"icon": "sparkle", "title": "Bandinha em Couro", "sub": "Fivela Metálica"},
        {"icon": "care", "title": "Carneira Acolchoada", "sub": "Encaixe Macio e Estável"},
        _TROCA,
    ],
    "caps_trucker_snapback": [
        {"icon": "care", "title": "Tela Respirável", "sub": "Lateral e Traseira"},
        {"icon": "shield", "title": "Aba Curva Reforçada", "sub": "6 Costuras de Reforço"},
        {"icon": "gear", "title": "Fecho Snapback", "sub": "Tamanho Único Ajustável"},
        _TROCA,
    ],
    "eyewear_sunglasses": [
        {"icon": "sun", "title": "Lentes Polarizadas", "sub": "Filtro Anti-Reflexo"},
        {"icon": "shield", "title": "Proteção UV400", "sub": "Bloqueio UVA e UVB"},
        {"icon": "care", "title": "Armação Ultraleve", "sub": "Apoio Nasal Anatômico"},
        {"icon": "sparkle", "title": "Estojo Incluso", "sub": "Com Flanela de Microfibra"},
    ],
    # --- Calçados ---
    "footwear_sandals_boaonda": [
        {"icon": "shoe", "title": "Palmilha Antiestresse", "sub": "Amortecimento Anatômico"},
        {"icon": "shield", "title": "Solado Antiderrapante", "sub": "Aderência em Solo Molhado"},
        {"icon": "care", "title": "Fácil Higienização", "sub": "Material Antibacteriano"},
        {"icon": "return", "title": "Troca Fácil BRK", "sub": "Ajuste Perfeito Garantido"},
    ],
    "closed_footwear_sneakers": [
        {"icon": "shoe", "title": "Palmilha Anatômica", "sub": "Espuma de Alta Densidade"},
        {"icon": "shield", "title": "Solado Antiderrapante", "sub": "Borracha de Alta Tração"},
        {"icon": "care", "title": "Cabedal Respirável", "sub": "Reforços Laterais"},
        {"icon": "return", "title": "Troca Fácil BRK", "sub": "Ajuste Perfeito Garantido"},
    ],
    # --- Equipamentos de pesca (NUNCA vestuário) ---
    "fishing_tackle_gear": [
        {"icon": "fish", "title": "Sensibilidade & Precisão", "sub": "Resposta Rápida ao Toque"},
        {"icon": "shield", "title": "Estrutura Reforçada", "sub": "Feita para Brigas Pesadas"},
        {"icon": "gear", "title": "Tratamento Anti-Corrosão", "sub": "Água Doce e Salgada"},
        {"icon": "sparkle", "title": "100% Original", "sub": "Procedência e Garantia"},
    ],
    "fishing_lures": [
        {"icon": "fish", "title": "Ação & Nado Realista", "sub": "Atratividade para Predadores"},
        {"icon": "shield", "title": "Pitões Reforçados", "sub": "Componentes em Aço Inox"},
        {"icon": "gear", "title": "Equilíbrio Hidrodinâmico", "sub": "Arremessos Precisos"},
        {"icon": "sparkle", "title": "Garantia de Procedência", "sub": "100% Original e Testado"},
    ],
    "tackle_boxes_storage": [
        {"icon": "box", "title": "Polipropileno Anti-Impacto", "sub": "Proteção UV"},
        {"icon": "shield", "title": "Travas de Alta Pressão", "sub": "Sistema Duplo Reforçado"},
        {"icon": "gear", "title": "Divisórias Removíveis", "sub": "Reposicionáveis sob Medida"},
        {"icon": "care", "title": "Vedação Anti-Respingos", "sub": "Contra Água e Poeira"},
    ],
    # --- Outros ---
    "drinkware_thermo": [
        {"icon": "shield", "title": "Inox 18/8 com Vácuo", "sub": "Parede Dupla Térmica"},
        {"icon": "bolt", "title": "Máximo Isolamento", "sub": "Bebida Gelada por Horas"},
        {"icon": "care", "title": "Livre de BPA", "sub": "Sem Condensação Externa"},
        {"icon": "return", "title": "Garantia BRK", "sub": "Qualidade Assegurada"},
    ],
    "cutlery_unique": [
        {"icon": "knife", "title": "Aço Especial Nobre", "sub": "Alta Retenção de Fio"},
        {"icon": "gear", "title": "Tratamento Térmico", "sub": "Dureza e Tenacidade"},
        {"icon": "shield", "title": "Acabamento Artesanal", "sub": "Cabo Anatômico Nobre"},
        {"icon": "sparkle", "title": "Garantia BRK", "sub": "Procedência Garantida"},
    ],
    "accessories_car_care": [
        {"icon": "sparkle", "title": "Fragrância Contínua", "sub": "Liberação Gradual"},
        {"icon": "care", "title": "Longa Duração", "sub": "Perfume Prolongado"},
        {"icon": "gear", "title": "Suspensão Prática", "sub": "Retrovisor Interno"},
        {"icon": "return", "title": "Troca Descomplicada", "sub": "Satisfação Garantida"},
    ],
    "accessories_general": [
        {"icon": "shield", "title": "Resistente à Água", "sub": "E à Exposição Solar"},
        {"icon": "care", "title": "Material Reforçado", "sub": "Alta Resistência"},
        {"icon": "sparkle", "title": "Item Original BRK", "sub": "Colecionável Oficial"},
        {"icon": "return", "title": "Troca Descomplicada", "sub": "Satisfação Garantida"},
    ],
    "books_publications": [
        {"icon": "sparkle", "title": "Impressão em Alta Definição", "sub": "Ilustrações Detalhadas"},
        {"icon": "care", "title": "Capa Colorida Laminada", "sub": "Papel Resistente"},
        {"icon": "box", "title": "Ideal para Presentear", "sub": "Para Todas as Idades"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Rastreamento Completo"},
    ],
}


class HTMLBuilder:
    def __init__(self):
        pass

    def _render_quick_badges(self, theme_color: str, badges: List[Dict[str, str]]) -> str:
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
        """
        Seleciona os 4 selos EXCLUSIVAMENTE pelo arquétipo detectado.
        Nunca usa palavras soltas do título (ex.: "pesca" em "Vara de Pesca"),
        pois isso contaminava equipamentos com selos de camisa UV (FPU 50+, Dry Fit).
        Arquétipo desconhecido -> selos genéricos e seguros.
        """
        badges = QUICK_BADGES_BY_ARCHETYPE.get(archetype_id) or [
            {"icon": "shield", "title": "Qualidade Oficial", "sub": "Matéria-Prima Selecionada"},
            {"icon": "sparkle", "title": "Acabamento Premium", "sub": "Rigoroso Padrão BRK"},
            {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Rastreamento Completo"},
            {"icon": "return", "title": "Troca Descomplicada", "sub": "Satisfação Garantida"},
        ]
        return self._render_quick_badges(theme_color, badges)

    def _build_size_guide(self, theme_color: str, archetype_id: str, is_kids: bool, is_short_sleeve: bool, enriched_data: Dict[str, Any]) -> str:
        title_low = (enriched_data.get("formatted_title") or enriched_data.get("title") or "").lower()
        sku_low = (enriched_data.get("sku") or enriched_data.get("master_sku") or "").lower()

        # 1. Identificar se o produto é comprovadamente de vestuário superior / camisa
        is_shirt = (
            archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work")
            or any(w in title_low for w in ["camisa", "camiseta", "jersey", "baby look", "babylook"])
            or any(sku_low.startswith(pfx) for pfx in ["c0", "ci", "cadv", "adv", "hyb", "cmb", "raglan"])
        ) and not bool(re.search(r'\b(calça|calca|calças|calcas|bermuda|bermudas|shorts|short|macacão|macacao|sandália|sandalia|babuche|chinelo|sapato|tênis|tenis|bota|botina|boaonda|chapéu|chapeu|boné|bone|luva|luvas|manguito|manguitos|bandana|tubeneck|buff|balaclava)\b', title_low))

        # 0. Exclusão estrita de itens não-têxteis com UV ou termos ambíguos (apenas se NÃO for camisa)
        if not is_shirt:
            non_textile_pattern = r'\b(óculos|oculos|faca|facas|canivete|alicate|vara|varas|molinete|carretilha|isca|iscas|linha|linhas|anzol|anzois|anzóis|estojo|garrafa|copo|chaveiro|adesivo|carteira|protetor solar)\b'
            if re.search(non_textile_pattern, title_low):
                return ""

        tip_text = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura do ombro à barra | Manga do ombro ao punho). Dica: compare com uma peça sua estendida para escolher o caimento ideal."

        if is_shirt:
            # 1.1 Camisas de Botão / Utilitárias Work (CMB - Sarja/Algodão corte reto de trabalho)
            is_work_guide = (
                (archetype_id == "shirts_button_work" or "cmb" in sku_low or "cbt" in sku_low or ("work" in title_low and "camisa" in title_low and not any(w in title_low for w in ["xtech", "dry", "uv", "uv50", "pesca"])))
                and not sku_low.startswith("c0") and not sku_low.startswith("ci")
            )
            if is_work_guide:
                guide_title = "Tabela de Medidas - Camisas Work & Utilitárias de Botão (P ao G2)"
                tip_text = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Comprimento da gola à barra | Manga). Modelagem confortável de trabalho."
                manga_header = "Manga Curta" if is_short_sleeve else "Manga Longa"
                rows = [
                    ("P", "102 cm", "68 cm", "22 cm" if is_short_sleeve else "75 cm"),
                    ("M", "108 cm", "71 cm", "23 cm" if is_short_sleeve else "77 cm"),
                    ("G", "114 cm", "74 cm", "24 cm" if is_short_sleeve else "79 cm"),
                    ("GG", "120 cm", "77 cm", "25 cm" if is_short_sleeve else "81 cm"),
                    ("XG", "126 cm", "80 cm", "26 cm" if is_short_sleeve else "83 cm"),
                    ("EXG (G1)", "132 cm", "83 cm", "27 cm" if is_short_sleeve else "85 cm"),
                    ("G2", "138 cm", "85 cm", "28 cm" if is_short_sleeve else "87 cm"),
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

            # 1.2 Camisas UV C0 Infantil (1 a 13 Anos | PP ao G2)
            elif (
                is_kids
                or any(w in title_low for w in ["infantil", "kids", "juvenil", "criança", "crianca"])
                or "kids" in sku_low
                or "inf" in sku_low
                or (
                    (sku_low.startswith("ci") or bool(re.search(r'^(?:c0|ci|cf|cm|casual|adv|cadv|ccpbr|bp|hyb|fusion|cax|raglan)\d+i(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$', sku_low)))
                    and not any(w in title_low for w in ["feminina", "feminino", "baby look", "babylook", "masculina", "masculino", "adulto"])
                )
            ):
                guide_title = "Guia de Tamanhos Infantil (1 a 13 Anos)"
                badge_title = "INFANTIL"
                tip_text = "<strong>Escolha por Idade com Referência de Tamanho (PP ao G2):</strong> Na linha Infantil BRK, a seleção é guiada pela faixa de idade (1 a 13 Anos) mantendo a indicação do tamanho equivalente (PP ao G2). Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura do ombro à barra | Manga do ombro ao punho)."
                shirt_sub_prefix = "Camiseta Algodão Premium" if archetype_id == "agro_field" else ("Camisa Manga Curta UV50" if is_short_sleeve else "Camisa Manga Longa UV50")
                subtitle = f"{shirt_sub_prefix} | *As medidas podem variar de 2cm a 3cm"
                rows = [
                    ("1 a 2 Anos (PP)", "31 cm", "41 cm", "31 cm"),
                    ("2 a 3 Anos (P)", "33 cm", "45 cm", "35 cm"),
                    ("4 a 5 Anos (M)", "35 cm", "49 cm", "37 cm"),
                    ("6 a 7 Anos (G)", "38 cm", "52 cm", "39 cm"),
                    ("8 a 9 Anos (GG)", "39 cm", "55 cm", "42 cm"),
                    ("10 a 11 Anos (G1)", "41 cm", "58 cm", "44 cm"),
                    ("12 a 13 Anos (G2)", "43 cm", "61 cm", "45 cm"),
                ]
                rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in rows])
                table_html = f"""<div class="brk-sg-card-header">
        <div class="brk-sg-card-title">{badge_title}</div>
        <div class="brk-sg-subtitle">{subtitle}</div>
      </div>
      <table class="brk-sg-table">
        <thead>
          <tr class="brk-sg-th-row">
            <th>IDADE / TAMANHO</th>
            <th>TÓRAX</th>
            <th>ALTURA</th>
            <th>MANGA</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

            # 1.3 Camisas UV C0 Feminina / Baby Look (PP ao G2)
            elif any(w in title_low for w in ["feminina", "feminino", "baby look", "fem", "babylook"]) or "bl" in sku_low:
                guide_title = "Tabela de Medidas Feminina - Baby Look (PP ao G2)"
                badge_title = "FEMININO"
                shirt_sub_prefix = "Camiseta Algodão Premium" if archetype_id == "agro_field" else ("Camisa Manga Curta UV50" if is_short_sleeve else "Camisa Manga Longa UV50")
                subtitle = f"{shirt_sub_prefix} | *As medidas podem variar de 2cm a 3cm"
                rows = [
                    ("Baby Look PP", "33 cm", "51 cm", "53 cm"),
                    ("Baby Look P", "37 cm", "54 cm", "55 cm"),
                    ("Baby Look M", "43 cm", "57 cm", "59 cm"),
                    ("Baby Look G", "47 cm", "60 cm", "60 cm"),
                    ("Baby Look GG", "47 cm", "60 cm", "61 cm"),
                    ("Baby Look G1", "50 cm", "62 cm", "61 cm"),
                    ("Baby Look G2", "55 cm", "64 cm", "63 cm"),
                ]
                rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in rows])
                table_html = f"""<div class="brk-sg-card-header">
        <div class="brk-sg-card-title">{badge_title}</div>
        <div class="brk-sg-subtitle">{subtitle}</div>
      </div>
      <table class="brk-sg-table">
        <thead>
          <tr class="brk-sg-th-row">
            <th>TAMANHO</th>
            <th>TÓRAX</th>
            <th>ALTURA</th>
            <th>MANGA</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

            # 1.4 Camisas UV C0 Masculino / Unissex Padrão (PP ao G2)
            else:
                guide_title = "Tabela de Medidas Masculino / Unissex (PP ao G2)"
                badge_title = "MASCULINO"
                shirt_sub_prefix = "Camiseta Algodão Premium" if archetype_id == "agro_field" else ("Camisa Manga Curta UV50" if is_short_sleeve else "Camisa Manga Longa UV50")
                subtitle = f"{shirt_sub_prefix} | *As medidas podem variar de 2cm a 3cm"
                rows = [
                    ("PP", "49,5 cm", "67 cm", "56 cm"),
                    ("P", "51,5 cm", "69 cm", "59,5 cm"),
                    ("M", "54 cm", "71 cm", "62 cm"),
                    ("G", "56 cm", "72 cm", "64 cm"),
                    ("GG", "59 cm", "74 cm", "64 cm"),
                    ("G1", "62 cm", "75 cm", "66 cm"),
                    ("G2", "65 cm", "76,5 cm", "66 cm"),
                ]
                rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in rows])
                table_html = f"""<div class="brk-sg-card-header">
        <div class="brk-sg-card-title">{badge_title}</div>
        <div class="brk-sg-subtitle">{subtitle}</div>
      </div>
      <table class="brk-sg-table">
        <thead>
          <tr class="brk-sg-th-row">
            <th>TAMANHO</th>
            <th>TÓRAX</th>
            <th>ALTURA</th>
            <th>MANGA</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""

        # 2. Calças e Bermudas / Macacões sem bota acoplada (pants_cargo_tactical, overalls_workwear)
        elif (archetype_id in ("pants_cargo_tactical", "overalls_workwear") or (not is_shirt and bool(re.search(r'\b(calça|calca|calças|calcas|bermuda|bermudas|shorts|short|macacão|macacao)\b', title_low)))) and "bota" not in title_low:
            guide_title = "Tabela de Medidas - Calças & Bermudas (38 ao 52)"
            tip_text = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Cintura na altura do cós | Quadril na parte mais larga | Comprimento da cintura até a barra). Dica: compare com uma peça sua estendida."
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

        # 3. Chapéus e Bonés (hats_safari_outdoor, caps_trucker_snapback)
        elif archetype_id in ("hats_safari_outdoor", "caps_trucker_snapback") or (
            (any(w in title_low for w in ["trucker", "snapback", "chapéu", "chapeu"]) or bool(re.search(r'\b(boné|bone|bonés)\b', title_low)))
            and not any(w in title_low for w in ["copo", "garrafa", "camisa", "till the bones"])
        ):
            guide_title = "Guia de Dimensões - Chapéus & Bonés"
            tip_text = "<strong>Como medir com precisão:</strong> Passe uma fita métrica ao redor da cabeça, cerca de 1 dedo acima das orelhas e sobrancelhas."
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

        # 4. Calçados (footwear_sandals_boaonda, closed_footwear_sneakers, calcados_botinas)
        elif archetype_id in ("footwear_sandals_boaonda", "closed_footwear_sneakers", "calcados_botinas") or any(w in title_low for w in ["sandália", "sandalia", "babuche", "chinelo", "sapato", "tênis", "tenis", "bota", "botina", "boaonda"]):
            guide_title = "Guia de Tamanhos de Calçados (Medida da Palmilha)"
            tip_text = "<strong>Como medir com precisão:</strong> Meça a palmilha interna de um calçado confortável do calcanhar até a ponta do dedão para escolher a numeração perfeita."
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

        # 5. Luvas (gloves_tactical_fishing)
        elif archetype_id == "gloves_tactical_fishing" or "luva" in title_low:
            guide_title = "Tabela de Medidas de Luvas (Largura da Palma)"
            tip_text = "<strong>Como medir com precisão:</strong> Meça a largura da palma da mão na parte mais larga (logo abaixo das articulações dos dedos)."
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

        # 6. Manguitos (sun_sleeves_manguitos)
        elif archetype_id == "sun_sleeves_manguitos" or "manguito" in title_low:
            guide_title = "Tabela de Medidas - Manguitos de Proteção Solar"
            tip_text = "<strong>Como medir com precisão:</strong> Meça a circunferência do bíceps e punho com o braço em repouso."
            rows = [
                ("P / M", "24 a 30 cm", "16 a 20 cm", "45 cm"),
                ("G / GG", "30 a 38 cm", "18 a 24 cm", "48 cm"),
            ]
            rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in rows])
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

        # 7. Bandanas / Balaclavas / Lenços / Black Mask
        elif archetype_id == "neck_gaiters_balaclavas" or any(w in title_low for w in ["bandana", "tubeneck", "buff", "balaclava", "lenço", "lenco"]):
            if "lenço" in title_low or "lenco" in title_low:
                guide_title = "Dimensões - Lenço Quadrado de Amarração UV50+"
                tip_text = "<strong>Dimensões do produto:</strong> Modelagem quadrada plana em tecido leve com proteção UV50+ para amarração versátil na cabeça, cabelo ou pescoço."
                table_html = """<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Tamanho</th>
            <th>Formato</th>
            <th>Dimensões Aproximadas</th>
            <th>Ajuste</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Tamanho Único</strong></td>
            <td>Quadrado Plano</td>
            <td>Aprox. 55 x 55 cm</td>
            <td>Amarração livre ajustável (cabeça, pescoço, cabelo ou acessórios)</td>
          </tr>
        </tbody>
      </table>"""
            elif "black mask" in title_low or "blackmask" in title_low:
                guide_title = "Dimensões - Bandana Anatômica Black Mask UV50+"
                tip_text = "<strong>Dimensões do produto:</strong> Modelagem anatômica 3D com recorte nasal ergonômico, painel frontal respirável em tela Mesh e cobertura alongada de pescoço."
                table_html = """<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Tamanho</th>
            <th>Largura Facial</th>
            <th>Altura Frontal / Pescoço</th>
            <th>Estrutura</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Tamanho Único</strong></td>
            <td>Aprox. 25 cm (Elástica)</td>
            <td>Aprox. 36 cm</td>
            <td>Recorte nasal anatômico + Tela respirável frontal + Tecido UV50+</td>
          </tr>
        </tbody>
      </table>"""
            elif "balaclava" in title_low and "tubeneck" not in title_low:
                guide_title = "Dimensões - Capuz Balaclava Integral UV50+"
                tip_text = "<strong>Dimensões do produto:</strong> Capuz integral elástico com visor ocular anatômico para cobertura completa de cabeça, rosto, orelhas e pescoço."
                table_html = """<table class="brk-sg-table">
        <thead>
          <tr>
            <th>Tamanho</th>
            <th>Circunferência Cabeça</th>
            <th>Comprimento Total</th>
            <th>Elasticidade</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Tamanho Único</strong></td>
            <td>54 cm a 62 cm (Adaptável)</td>
            <td>Aprox. 40 cm</td>
            <td>Malha tecnológica elástica com visor ocular anatômico</td>
          </tr>
        </tbody>
      </table>"""
            else:
                guide_title = "Dimensões - Bandana Tubular Multifuncional UV50+"
                tip_text = "<strong>Dimensões do produto:</strong> Microfibra tubular de alta elasticidade com proteção UV50+ e memória anatômica."
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
            <td>Microfibra tubular elástica 4-Way Stretch com memória anatômica</td>
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
        <span>{tip_text}</span>
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
        raw_price = str(enriched_data.get("price") or "0.00")
        clean_price = re.sub(r'[^\d,.]', '', raw_price).strip()
        if ',' in clean_price and '.' in clean_price:
            clean_price = clean_price.replace('.', '').replace(',', '.')
        elif ',' in clean_price:
            clean_price = clean_price.replace(',', '.')
        price = clean_price if clean_price else "0.00"

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

    def _build_cap_or_hat_html(self, enriched_data: Dict[str, Any], archetype_id: str) -> str:
        """
        Compila a descrição especializada de alta conversão para Bonés e Chapéus BRK,
        utilizando o design com Grid de Detalhes 260x260, Cards de Características & Cuidados,
        e Seções Split Intercaladas (Produto Premium + Entrega Segura na Caixa BRK).
        """
        formatted_title = enriched_data.get("formatted_title") or enriched_data.get("title", "Boné BRK")
        sku = str(enriched_data.get("sku") or enriched_data.get("master_sku") or "")
        store_key = enriched_data.get("store_key", "brk_fishing")
        schema_json_ld = self._build_schema_json_ld(enriched_data)

        # Gradientes e Identidade por Loja
        if store_key == "brk_agro":
            grad_horiz = "linear-gradient(90deg, #15803d, #ca8a04)"
            grad_vert = "linear-gradient(180deg, #15803d, #ca8a04)"
            color_accent = "#15803d"
            brand_label = "BRK Agro"
        elif store_key == "brk_motors":
            grad_horiz = "linear-gradient(90deg, #ea580c, #dc2626)"
            grad_vert = "linear-gradient(180deg, #ea580c, #dc2626)"
            color_accent = "#ea580c"
            brand_label = "BRK Motors"
        else:
            grad_horiz = "linear-gradient(90deg, #00a8ff, #00d084)"
            grad_vert = "linear-gradient(180deg, #00a8ff, #00d084)"
            color_accent = "#00a8ff"
            brand_label = "BRK Fishing"

        # 1. Configuração Específica por Categoria e Seleção das 4 Fotos Reais do Produto
        title_low = formatted_title.lower()
        raw_gallery = enriched_data.get("images") or enriched_data.get("gallery") or []
        gallery_urls = [img.get("src") if isinstance(img, dict) else str(img) for img in raw_gallery if img]
        non_png = [u for u in gallery_urls if not u.lower().split("?")[0].endswith(".png")]
        hw_pool = non_png if len(non_png) >= 4 else (non_png + [u for u in gallery_urls if u not in non_png] if non_png else gallery_urls)
        img1 = hw_pool[0] if len(hw_pool) > 0 else "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg"
        img2 = hw_pool[1] if len(hw_pool) > 1 else ("https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg" if len(hw_pool) == 0 else img1)
        img3 = hw_pool[2] if len(hw_pool) > 2 else ("https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg" if len(hw_pool) == 0 else img1)
        img4 = hw_pool[3] if len(hw_pool) > 3 else ("https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg" if len(hw_pool) == 0 else img2)

        if archetype_id == "caps_trucker_snapback":
            item_type_label = "Boné"
            is_6_gomos = ("6 gomos" in title_low or "seis gomos" in title_low)
            copa_bullet = (
                "Copa estruturada de 6 gomos fechada em tecido camuflado, com frente firme e ilhoses bordados que favorecem a ventilação."
                if is_6_gomos else
                "Copa estruturada estilo trucker, com frente firme e tela traseira que favorece a ventilação."
            )
            # Detecta tema visual real do boné pelo título antes de cair no store_key
            if any(w in title_low for w in ["fishing", "pesca", "robalo", "tucunar", "tambaqui", "traira", "traíra", "dourado", "pirarara", "red tail", "black bass"]):
                cap_theme = "brk_fishing"
            elif any(w in title_low for w in ["agro", "peacemaker", "country", "texas", "bull", "nelore", "fazenda", "sertanejo"]):
                cap_theme = "brk_agro"
            elif any(w in title_low for w in ["motors", "racing", "off-road", "off road", "motocross", "trilha"]):
                cap_theme = "brk_motors"
            else:
                cap_theme = store_key

            if cap_theme == "brk_agro":
                exclusive_desc = "Arte exclusiva BRK Agro inspirada no campo e no agronegócio, para você se destacar em qualquer ambiente."
                caract_items = [
                    copa_bullet,
                    "Aba moldável com costuras reforçadas, oferecendo conforto e proteção para o rosto e os olhos.",
                    "Tamanho único com regulagem traseira, se ajustando à maioria dos formatos de cabeça.",
                    "Ideal para o campo, atividades ao ar livre e uso no dia a dia.",
                    "Acabamento interno pensado para máximo conforto mesmo em longas jornadas de trabalho."
                ]
                split1_strong = "Cada boné BRK é desenvolvido pensando em quem vive a vida no campo intensamente."
                split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance."
                split1_p3 = "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo no campo ou na cidade."
                split2_strong = "A sua experiência começa antes mesmo de abrir a caixa."
                split2_p2 = "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições."
                split2_p3 = "Assim, seu novo boné chega pronto para encarar a lida na fazenda, feiras agropecuárias ou eventos sertanejos."
                split1_alt = "Etiquetas BRK aplicadas em produtos agropecuários"
                split2_alt = "Caixa personalizada BRK para envio seguro"
            elif cap_theme == "brk_motors":
                exclusive_desc = "Arte exclusiva BRK Motors inspirada na velocidade e no off-road, para você se destacar dentro e fora das pistas."
                caract_items = [
                    copa_bullet,
                    "Aba moldável com costuras reforçadas, oferecendo conforto e proteção para o rosto e os olhos.",
                    "Tamanho único com regulagem traseira, se ajustando à maioria dos formatos de cabeça.",
                    "Ideal para trilha, velocidade, eventos automotivos e uso no dia a dia.",
                    "Acabamento interno pensado para máximo conforto mesmo em longas jornadas."
                ]
                split1_strong = "Cada boné BRK é desenvolvido pensando no piloto e entusiasta que vive a velocidade intensamente."
                split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance."
                split1_p3 = "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo em qualquer aventura sobre rodas."
                split2_strong = "A sua experiência começa antes mesmo de abrir a caixa."
                split2_p2 = "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições."
                split2_p3 = "Assim, seu novo boné chega pronto para encarar a próxima trilha, viagem ou pista com atitude e proteção."
                split1_alt = "Etiquetas BRK aplicadas em produtos esportivos"
                split2_alt = "Caixa personalizada BRK para envio seguro"
            else:
                exclusive_desc = "Arte exclusiva BRK Fishing inspirada na pesca esportiva, para você se destacar dentro e fora da água."
                caract_items = [
                    copa_bullet,
                    "Aba moldável com costuras reforçadas, oferecendo conforto e proteção para o rosto e os olhos.",
                    "Tamanho único com regulagem traseira, se ajustando à maioria dos formatos de cabeça.",
                    "Ideal para pesca esportiva, atividades ao ar livre e uso no dia a dia.",
                    "Acabamento interno pensado para máximo conforto mesmo em longas jornadas de pesca."
                ]
                split1_strong = "Cada boné BRK é desenvolvido pensando no pescador que vive a pesca esportiva intensamente."
                split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance."
                split1_p3 = "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo em qualquer pescaria."
                split2_strong = "A sua experiência começa antes mesmo de abrir a caixa."
                split2_p2 = "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições."
                split2_p3 = "Assim, seu novo boné de pesca chega pronto para encarar a próxima aventura, seja na beira do rio, na represa ou em alto mar."
                split1_alt = "Etiquetas BRK aplicadas em produtos de pesca"
                split2_alt = "Caixa personalizada BRK para envio dos bonés"

            details = [
                {
                    "img": img1,
                    "alt": f"Aba do boné {formatted_title} com costuras reforçadas e estrutura moldável",
                    "title": "Aba Moldável",
                    "desc": "Aba estruturada com diversas costuras e moldável, garantindo durabilidade e proteção extra contra o sol."
                },
                {
                    "img": img2,
                    "alt": f"Parte interna do boné {formatted_title} com costuras em tear",
                    "title": "Interno em Tear",
                    "desc": "Acabamento interno em tear com costuras reforçadas, pensado para aguentar longas jornadas de pesca." if cap_theme == "brk_fishing" else "Acabamento interno em tear com costuras reforçadas, pensado para aguentar longas jornadas de uso contínuo."
                },
                {
                    "img": img3,
                    "alt": f"Etiqueta BRK de qualidade aplicada no boné {formatted_title}",
                    "title": "Etiqueta BRK de Qualidade",
                    "desc": "Etiqueta BRK aplicada com acabamento premium, garantindo autenticidade e padrão de qualidade."
                },
                {
                    "img": img4,
                    "alt": f"Design exclusivo do boné {formatted_title}",
                    "title": "Design Exclusivo",
                    "desc": exclusive_desc
                }
            ]
            caract_title = "Características do Boné BRK"
            cuidados_title = "Cuidados com o Seu Boné"
            cuidados_items = [
                "Não lave o boné na máquina e não utilize água quente.",
                "Para limpeza, use um pano úmido com sabão neutro nas áreas sujas.",
                "Retire o excesso de sabão com outro pano levemente úmido.",
                "Deixe secar à sombra, em superfície plana, longe de fontes de calor.",
                "Não utilize alvejante, não passe a ferro e não leve à secadora."
            ]
            split1_p1 = f"<strong>{split1_strong}</strong>"
            split2_p1 = f"<strong>{split2_strong}</strong>"

        elif archetype_id == "hats_safari_outdoor":
            item_type_label = "Chapéu"

            if any(w in title_low for w in ["juta", "bambu", "palha"]):
                details = [
                    {
                        "img": img1,
                        "alt": f"Trama natural em juta e palha de bambu do chapéu {formatted_title}",
                        "title": "Trama em Juta & Bambu",
                        "desc": "Trançado nobre em fibras selecionadas de juta e palha de bambu que proporciona ventilação natural constante e leveza superior."
                    },
                    {
                        "img": img2,
                        "alt": f"Bandinha personalizada BRK Agro com fivela metálica do chapéu {formatted_title}",
                        "title": "Bandinha BRK Agro Exclusiva",
                        "desc": "Acabamento externo em fita caramelo personalizada BRK Agro com fivela metálica lateral, conferindo identidade autêntica do campo."
                    },
                    {
                        "img": img3,
                        "alt": f"Copa e aba estruturadas com viés protetor do chapéu {formatted_title}",
                        "title": "Copa & Aba Estruturadas",
                        "desc": "Modelagem clássica com copa bem definida e aba ampla finalizada com viés de proteção nas bordas para excelente cobertura solar."
                    },
                    {
                        "img": img4,
                        "alt": f"Carneira interna confortável do chapéu {formatted_title}",
                        "title": "Carneira Interna Confortável",
                        "desc": "Faixa interna macia e anatômica que garante encaixe firme e estável na cabeça ao longo de todo o dia."
                    }
                ]
                caract_title = "Características do Chapéu BRK Agro Juta & Bambu"
                caract_items = [
                    "Confeccionado em trama selecionada de juta e palha de bambu altamente respirável.",
                    "Aba estruturada com acabamento em viés nas bordas para proteção solar no campo e lazer.",
                    "Bandinha externa personalizada BRK Agro em tom caramelo com fivela metálica.",
                    "Carneira interna macia que proporciona ajuste confortável e seguro na cabeça.",
                    "Ideal para dias de sol na fazenda, feiras agropecuárias, encontros sertanejos e lazer ao ar livre."
                ]
                cuidados_title = "Cuidados com o Seu Chapéu de Fibra Natural"
                cuidados_items = [
                    "Limpar delicadamente com pano seco ou escova de cerdas macias.",
                    "Não lavar em água, não submergir e não utilizar máquina de lavar.",
                    "Evitar exposição à chuva intensa ou ambientes úmidos fechados.",
                    "Caso receba respingos leves, deixe secar naturalmente à sombra em local arejado.",
                    "Guardar sempre apoiado pela copa ou em suporte próprio para preservar a aba estruturada."
                ]
                split1_p1 = "<strong>Estilo autêntico do campo aliado ao frescor das fibras naturais.</strong>"
                split1_p2 = "O Chapéu BRK Agro Juta Palha de Bambu Premium foi desenvolvido para quem valoriza elegância rústica, conforto térmico e acabamento impecável."
                split1_p3 = "Cada detalhe — da trama ventilada à bandinha exclusiva BRK Agro — entrega presença marcante e bem-estar sob o sol."
                split2_p1 = "<strong>Embalagem protetora pensada para preservar o formato original.</strong>"
                split2_p2 = "O chapéu é enviado em caixa reforçada BRK, projetada para proteger a copa e a aba durante todo o transporte."
                split2_p3 = "Assim, seu novo chapéu chega impecável e pronto para acompanhar você na fazenda, nos eventos ou no lazer."
                split1_alt = f"Acabamento exclusivo BRK Agro no chapéu {formatted_title}"
                split2_alt = f"Embalagem reforçada BRK para envio do chapéu {formatted_title}"
            else:
                details = [
                    {
                        "img": img1,
                        "alt": f"Aba 360° com proteção solar do chapéu {formatted_title}",
                        "title": "Aba 360° UV50+",
                        "desc": "Aba circular ampla com costuras reforçadas, bloqueando os raios solares diretos no rosto, orelhas e pescoço com máxima cobertura."
                    },
                    {
                        "img": img2,
                        "alt": f"Cordão jugular com trava anti-vento do chapéu {formatted_title}",
                        "title": "Cordão Jugular Anti-Vento",
                        "desc": "Ajuste seguro sob o queixo com trava regulável, mantendo o chapéu firme mesmo sob rajadas de vento e navegação rápida."
                    },
                    {
                        "img": img3,
                        "alt": f"Protetor de nuca e acabamento do chapéu {formatted_title}",
                        "title": "Protetor de Nuca Integrado",
                        "desc": "Cobertura estendida para a nuca que previne queimaduras solares durante longas jornadas sob sol intenso."
                    },
                    {
                        "img": img4,
                        "alt": f"Tecido leve e respirável do chapéu {formatted_title}",
                        "title": "Tecido Respirável & Leve",
                        "desc": "Construção de secagem rápida com ilhoses de ventilação lateral para dissipação imediata de calor e sensação de frescor contínuo."
                    }
                ]
                caract_title = "Características do Chapéu Safári BRK"
                caract_items = [
                    "Copa anatômica com ilhoses laterais que garantem circulação de ar constante.",
                    "Aba larga circular de 360° com fator de proteção UV50+ permanente.",
                    "Cordão jugular com trava ajustável de segurança contra quedas e vento forte.",
                    "Protetor de nuca para proteção solar total na região posterior do pescoço.",
                    "Tecido tecnológico leve de secagem ultra rápida e alta resistência ao desgaste."
                ]
                cuidados_title = "Cuidados com o Seu Chapéu"
                cuidados_items = [
                    "Lavar à mão com água fria e sabão neutro.",
                    "Não lavar em máquina e não torcer para preservar a estrutura da aba.",
                    "Secar estendido à sombra em superfície plana.",
                    "Não usar alvejantes, amaciantes ou produtos à base de cloro.",
                    "Guardar sem dobrar a aba estruturada para manter o caimento original."
                ]
                split1_p1 = "<strong>Cada chapéu BRK é desenvolvido pensando na proteção de quem enfrenta longas jornadas ao ar livre.</strong>"
                split1_p2 = "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem padrão de proteção solar certificado."
                split1_p3 = "Construído com materiais leves e resistentes, oferece o máximo de conforto térmico para pescarias e trabalho sob sol forte."
                split2_p1 = "<strong>A sua experiência começa antes mesmo de abrir a caixa.</strong>"
                split2_p2 = "O chapéu é enviado em embalagem protegida BRK, projetada para evitar deformações na aba durante o transporte."
                split2_p3 = "Seu novo chapéu chega pronto para encarar o sol com proteção e estilo incomparáveis."
                split1_alt = f"Etiquetas BRK aplicadas no chapéu {formatted_title}"
                split2_alt = f"Embalagem protegida BRK para envio do chapéu {formatted_title}"

        else:  # hats_country_cowboy
            item_type_label = "Chapéu Country"
            is_straw_country = any(w in title_low for w in ["bozeman", " cal", "palha"])

            details = [
                {
                    "img": img1,
                    "alt": f"Aba larga estruturada do chapéu {formatted_title}",
                    "title": "Aba Larga Estruturada",
                    "desc": "Formato clássico western com curvatura marcante e acabamento impecável, unindo tradição, imponência e proteção solar no campo."
                },
                {
                    "img": img2,
                    "alt": f"Carneira interna do chapéu {formatted_title}",
                    "title": "Carneira Interna Confortável",
                    "desc": "Faixa interna com toque macio e anatômico, oferecendo fixação firme e confortável na cabeça sem marcar a testa."
                },
                {
                    "img": img3,
                    "alt": f"Fita decorativa e acabamento do chapéu {formatted_title}",
                    "title": "Fita & Acabamento Premium",
                    "desc": "Bandinha externa clássica com fivela, passador e ponteira metálica trabalhada, reforçando a autenticidade western."
                },
                {
                    "img": img4,
                    "alt": f"Estrutura de alta densidade do chapéu {formatted_title}",
                    "title": "Copa Ventilada em Palha Nobre" if is_straw_country else "Feltro Country de Alta Densidade",
                    "desc": (
                        "Trama firme em fibra nobre com microperfurações na copa que favorecem a ventilação térmica mantendo a estrutura impecável."
                        if is_straw_country else
                        "Feltro encorpado de alta densidade que preserva os vincos da copa Cattleman e a curvatura da aba mesmo com uso contínuo."
                    )
                }
            ]
            caract_title = "Características do Chapéu Country"
            caract_items = [
                (
                    "Copa alta estruturada em palha/fibra nobre com trama ventilada no legítimo estilo western."
                    if is_straw_country else
                    "Copa alta estruturada em feltro encorpado moldado no legítimo estilo Cattleman / Western."
                ),
                "Aba larga de presença marcante que proporciona excelente sombra e proteção.",
                "Carneira interna acolchoada para conforto prolongado em cavalgadas e eventos.",
                "Bandinha externa com conjunto de fivela metálica e identidade autêntica do campo.",
                "Ideal para rodeios, feiras agropecuárias, lida na fazenda e dia a dia sertanejo."
            ]
            cuidados_title = "Cuidados & Conservação do Chapéu"
            cuidados_items = [
                "Limpar delicadamente com escova de cerdas macias sempre no sentido da trama ou das fibras.",
                "Evitar contato direto com chuva intensa ou umidade excessiva.",
                "Armazenar sempre apoiado pela copa ou em suporte adequado para não desformar a aba.",
                "Nunca dobrar, amassar ou deixar exposto no interior de veículos sob sol forte.",
                "Em caso de umidade leve, deixe secar naturalmente à sombra em local ventilado."
            ]
            split1_p1 = "<strong>A tradição e o orgulho do campo em cada detalhe artesanal.</strong>"
            split1_p2 = "Cada chapéu é selecionado para entregar autenticidade, robustez e elegância para os amantes do estilo country."
            split1_p3 = "Acabamento primoroso que valoriza a cultura sertaneja e a presença marcante onde quer que você esteja."
            split2_p1 = "<strong>Embalagem especial anti-deformação.</strong>"
            split2_p2 = "O chapéu é embalado em caixa reforçada para garantir que a copa e a aba cheguem impecáveis e sem amassados."
            split2_p3 = "Pronto para usar na lida, nas cavalgadas ou nos grandes eventos do agronegócio."
            split1_alt = f"Etiquetas de autenticidade do chapéu country {formatted_title}"
            split2_alt = f"Caixa reforçada anti-deformação para envio do chapéu {formatted_title}"

        # Cor radial sutil por loja para a foto do split
        if store_key == "brk_agro":
            radial_color = "rgba(21, 128, 61, 0.15)"
        elif store_key == "brk_motors":
            radial_color = "rgba(234, 88, 12, 0.15)"
        else:
            radial_color = "rgba(0, 168, 255, 0.15)"

        # Montagem dos Detalhes em HTML
        details_html = []
        for d in details:
            safe_d_alt = str(d['alt']).replace('"', '&quot;')
            details_html.append(f"""<!-- {d['title']} -->
<article class="brk-cap-detail-item">
<div class="brk-cap-detail-image"><img src="{d['img']}" alt="{safe_d_alt}"></div>
<h3>{d['title']}</h3>
<p>{d['desc']}</p>
</article>""")
        details_markup = "\n".join(details_html)

        # Montagem das Características e Cuidados
        caract_li = "\n".join([f"<li>{item}</li>" for item in caract_items])
        cuidados_li = "\n".join([f"<li>{item}</li>" for item in cuidados_items])

        svg_care_extra = ' class="brk-cap-info-icon--care"' if color_accent != "#00a8ff" else ''

        return f"""{brk_tracking_marker(sku, archetype_id)}
{schema_json_ld}
<style>
  .brk-cap-description {{
    font-family: inherit;
    color: #222222;
    line-height: 1.5;
    font-size: 15px;
  }}

  .brk-cap-description * {{
    box-sizing: border-box;
  }}

  .brk-cap-section {{
    margin: 24px 0;
  }}

  .brk-cap-section-header {{
    text-align: center;
    margin-bottom: 18px;
  }}

  .brk-cap-section-title {{
    display: inline-block;
    font-size: 20px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    position: relative;
    padding-bottom: 6px;
  }}

  .brk-cap-section-title::after {{
    content: "";
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 0;
    width: 42px;
    height: 3px;
    border-radius: 999px;
    background: {grad_horiz};
  }}

  /* DETALHES – GRID DE IMAGENS 260x260 + TEXTO */
  .brk-cap-details-grid {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 16px;
  }}

  .brk-cap-detail-item {{
    text-align: center;
    max-width: 260px;
    flex: 1 1 220px;
  }}

  .brk-cap-detail-image {{
    width: 100%;
    max-width: 260px;
    margin: 0 auto 8px;
  }}

  .brk-cap-detail-image img {{
    display: block;
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
    border-radius: 12px;
  }}

  .brk-cap-detail-item h3 {{
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    margin: 6px 0 4px;
    letter-spacing: 0.04em;
  }}

  .brk-cap-detail-item p {{
    font-size: 13px;
    margin: 0;
    color: #555555;
  }}

  /* INFORMAÇÕES – CARDS SUTIS + LISTA COM QUADRADOS + SVG NO TÍTULO */
  .brk-cap-info-wrapper {{
    display: grid;
    grid-template-columns: minmax(0, 1.25fr);
    gap: 20px;
  }}

  .brk-cap-info-block {{
    padding: 16px 18px 18px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.05);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
  }}

  .brk-cap-info-title {{
    position: relative;
    display: inline-block;
    padding: 4px 0;
    margin-bottom: 10px;
  }}

  .brk-cap-info-title h3 {{
    font-size: 15px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0;
    position: relative;
    z-index: 1;
  }}

  .brk-cap-info-title svg {{
    position: absolute;
    left: -10px;
    top: -8px;
    width: 44px;
    height: 44px;
    opacity: 0.18;
    z-index: 0;
  }}

  .brk-cap-info-icon--care {{
    transform: translateX(-4px);
  }}

  .brk-cap-info-list {{
    margin: 4px 0 0;
    padding: 0;
  }}

  .brk-cap-info-block ul {{
    margin: 0;
    padding-left: 0;
    list-style: none;
  }}

  .brk-cap-info-block li {{
    position: relative;
    padding-left: 20px;
    margin-bottom: 6px;
    font-size: 14px;
  }}

  .brk-cap-info-block li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 6px;
    width: 9px;
    height: 9px;
    border-radius: 3px;
    background: {grad_horiz};
  }}

  @media (min-width: 900px) {{
    .brk-cap-info-block ul {{
      column-count: 2;
      column-gap: 28px;
    }}

    .brk-cap-info-block li {{
      break-inside: avoid;
    }}
  }}

  /* SEÇÕES DIVIDIDAS (IMAGEM + TEXTO) */
  .brk-cap-split-sections {{
    display: flex;
    flex-direction: column;
    gap: 24px;
  }}

  .brk-cap-split {{
    display: flex;
    align-items: center;
    gap: 24px;
  }}

  .brk-cap-split.reverse {{
    flex-direction: row-reverse;
  }}

  .brk-cap-split-image {{
    flex: 1 1 50%;
    max-width: 450px;
    border-radius: 18px;
    overflow: hidden;
    background: radial-gradient(circle at top left, {radial_color}, transparent 55%);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
  }}

  .brk-cap-split-image img {{
    display: block;
    width: 100%;
    height: auto;
  }}

  .brk-cap-split-content {{
    flex: 1 1 50%;
    position: relative;
    padding-left: 18px;
  }}

  .brk-cap-split.reverse .brk-cap-split-content {{
    padding-left: 0;
    padding-right: 18px;
  }}

  /* Barrinha vertical atrás de todo o texto */
  .brk-cap-split-content::before {{
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 3px;
    border-radius: 999px;
    background: {grad_vert};
    left: 0;
  }}

  .brk-cap-split.reverse .brk-cap-split-content::before {{
    left: auto;
    right: 0;
  }}

  .brk-cap-split-content h2 {{
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}

  .brk-cap-split-content p {{
    margin: 0 0 4px;
    font-size: 14px;
  }}

  .brk-cap-split-content p strong {{
    font-weight: 700;
  }}

  /* RESPONSIVO */
  @media (max-width: 900px) {{
    .brk-cap-detail-item {{
      flex: 1 1 85%;
      max-width: 220px;
    }}
  }}

  @media (max-width: 640px) {{
    .brk-cap-section {{
      margin: 20px 0;
    }}

    .brk-cap-section-title {{
      font-size: 18px;
    }}

    .brk-cap-detail-item {{
      flex: 1 1 100%;
      max-width: 260px;
    }}

    .brk-cap-split {{
      flex-direction: column;
    }}

    .brk-cap-split.reverse {{
      flex-direction: column;
    }}

    .brk-cap-split-image {{
      max-width: 100%;
      width: 100%;
      flex: none;
    }}

    .brk-cap-split-content {{
      padding-left: 14px;
      padding-right: 0;
    }}

    .brk-cap-split.reverse .brk-cap-split-content {{
      padding-right: 14px;
      padding-left: 0;
    }}

    .brk-cap-split-content h2 {{
      font-size: 16px;
    }}
  }}
</style>
<div class="brk-cap-description">
<!-- SEÇÃO DETALHES -->
<section class="brk-cap-section brk-cap-details"><header class="brk-cap-section-header">
<h2 class="brk-cap-section-title">Detalhes</h2>
</header>
<div class="brk-cap-details-grid">
{details_markup}
</div>
</section>
<!-- SEÇÃO INFORMAÇÕES -->
<section class="brk-cap-section brk-cap-information"><header class="brk-cap-section-header">
<h2 class="brk-cap-section-title">Informações</h2>
</header>
<div class="brk-cap-info-wrapper">
<!-- BLOCO 1: CARACTERÍSTICAS -->
<div class="brk-cap-info-block">
<div class="brk-cap-info-title">
<svg class="brk-svg-icon" width="36" height="36" viewBox="0 0 512 512" fill="{color_accent}" style="display:inline-block;vertical-align:-0.15em;flex-shrink:0;" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><path d="M256 0l40 160 160 40-160 40-40 160-40-160-160-40 160-40 40-160z"/></svg>
<h3>{caract_title}</h3>
</div>
<div class="brk-cap-info-list">
<ul>
{caract_li}
</ul>
</div>
</div>
<!-- BLOCO 2: CUIDADOS -->
<div class="brk-cap-info-block">
<div class="brk-cap-info-title">
<svg class="brk-svg-icon brk-cap-info-icon--care" width="36" height="36" viewBox="0 0 512 512" fill="{color_accent}" style="display:inline-block;vertical-align:-0.15em;flex-shrink:0;" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><path d="M256 32c12.5 0 24.1 6.4 30.8 17l40 64c6.7 10.7 6.7 24.3 0 35l-40 64c-6.7 10.7-18.3 17-30.8 17s-24.1-6.4-30.8-17l-40-64c-6.7-10.7-6.7-24.3 0-35l40-64c6.7-10.7 18.3-17 30.8-17zm160 192c12.5 0 24.1 6.4 30.8 17l40 64c6.7 10.7 6.7 24.3 0 35l-40 64c-6.7 10.7-18.3 17-30.8 17s-24.1-6.4-30.8-17l-40-64c-6.7-10.7-6.7-24.3 0-35l40-64c6.7-10.7 18.3-17 30.8-17zM96 224c12.5 0 24.1 6.4 30.8 17l40 64c6.7 10.7 6.7 24.3 0 35l-40 64c-6.7 10.7-18.3 17-30.8 17s-24.1-6.4-30.8-17l-40-64c-6.7-10.7-6.7-24.3 0-35l40-64c6.7-10.7 18.3-17 30.8-17z"/></svg>
<h3>{cuidados_title}</h3>
</div>
<div class="brk-cap-info-list">
<ul>
{cuidados_li}
</ul>
</div>
</div>
</div>
</section>
<!-- SEÇÕES IMAGEM + TEXTO -->
<section class="brk-cap-section brk-cap-split-sections"><!-- 1ª seção: Etiquetas BRK (FOTO -> TEXTO) -->
<div class="brk-cap-split">
<div class="brk-cap-split-image"><img src="https://cdn.shopify.com/s/files/1/0628/1445/3826/files/13-Tags.webp?v=1785788893" alt="{str(split1_alt).replace('"', '&quot;')}"></div>
<div class="brk-cap-split-content">
<h2>PRODUTO PREMIUM BRK</h2>
<p>{split1_p1}</p>
<p>{split1_p2}</p>
<p>{split1_p3}</p>
</div>
</div>
<!-- 2ª seção: Caixa / Entrega (TEXTO <- FOTO) -->
<div class="brk-cap-split reverse">
<div class="brk-cap-split-image"><img src="https://cdn.shopify.com/s/files/1/0628/1445/3826/files/CAIXA-BRK.webp?v=1785788895" alt="{str(split2_alt).replace('"', '&quot;')}"></div>
<div class="brk-cap-split-content">
<h2>ENTREGA SEGURA BRK</h2>
<p>{split2_p1}</p>
<p>{split2_p2}</p>
<p>{split2_p3}</p>
</div>
</div>
</section>
</div>"""

    def build_shopify_html(self, enriched_data: Dict[str, Any]) -> str:
        """
        Compila a descrição em HTML no padrão verticalizado BRK, 100% autônomo com SVGs inline estilo Font Awesome.
        """
        formatted_title = enriched_data.get("formatted_title") or enriched_data.get("title", "Produto BRK")
        brand_name = enriched_data.get("brand_name", "BRK")
        archetype_id = enriched_data.get("archetype_id", "")
        if not archetype_id:
            title_low = (formatted_title or enriched_data.get("title") or "").lower()
            if (any(w in title_low for w in ["trucker", "snapback"]) or bool(re.search(r'\b(boné|bone|bonés)\b', title_low))) and not any(w in title_low for w in ["copo", "garrafa", "camisa", "till the bones"]):
                archetype_id = "caps_trucker_snapback"
            elif any(w in title_low for w in ["chapéu", "chapeu"]) and any(w in title_low for w in ["country", "feltro", "cowboy"]):
                archetype_id = "hats_country_cowboy"
            elif any(w in title_low for w in ["chapéu", "chapeu"]):
                archetype_id = "hats_safari_outdoor"

        # Despacho especializado para Bonés e Chapéus (Layout D2C Oficial com Detalhes, Info e Split)
        if archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
            return self._build_cap_or_hat_html(enriched_data, archetype_id)
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

        # Trava Estrita Anti-Zíper para Linhas Fusion, Hybrid, Gola Careca e Camisas de Botão
        t_low = (formatted_title or "").lower()
        sku_low = str(enriched_data.get("sku") or enriched_data.get("master_sku") or "").lower()
        is_fusion_b = "fusion" in t_low or "fusion" in sku_low
        is_hybrid_b = "hybrid" in t_low or sku_low.startswith("hyb") or "hybrid" in sku_low
        is_anti_zipper = (
            is_fusion_b or is_hybrid_b or
            any(w in t_low for w in ["careca", "redonda", "sem zíper", "sem ziper"]) or
            archetype_id == "shirts_button_work"
        )
        if is_anti_zipper:
            for b in blocks:
                if isinstance(b, dict):
                    if "title" in b:
                        b["title"] = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', b["title"], flags=re.IGNORECASE).strip()
                    if "description" in b:
                        b["description"] = re.sub(r'gola padre com cobertura no cursor do z[íi]per', 'capuz anatômico contínuo', b["description"], flags=re.IGNORECASE)
                        b["description"] = re.sub(r'\bcursor do z[íi]per\b', 'acabamento anatômico', b["description"], flags=re.IGNORECASE)
                        b["description"] = re.sub(r'\bz[íi]per com trava de seguran[çc]a\b', 'conforto anatômico contínuo', b["description"], flags=re.IGNORECASE)
                        b["description"] = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', b["description"], flags=re.IGNORECASE)
                        b["description"] = re.sub(r'\(\s*\)', '', b["description"]).strip()
            new_clean_specs = []
            for sp in specs:
                lbl_c = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', sp["label"], flags=re.IGNORECASE).strip()
                replacement_hood = "capuz com máscara facial integrada" if is_fusion_b else "capuz anatômico integrado"
                val_c = re.sub(r'gola padre[^,;.]*', replacement_hood, sp["value"], flags=re.IGNORECASE)
                val_c = re.sub(r'\bcursor do z[íi]per\b', 'acabamento contínuo', val_c, flags=re.IGNORECASE)
                val_c = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', val_c, flags=re.IGNORECASE)
                val_c = re.sub(r'\(\s*\)', '', val_c).strip()
                new_clean_specs.append({"label": lbl_c or "Acabamento", "value": val_c})
            specs = new_clean_specs

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
            
            safe_title_alt = str(formatted_title).replace('"', '&quot;')
            safe_block_alt = str(block.get('alt', formatted_title)).replace('"', '&quot;')
            # Layout de Mídia: Split para iscas/variações ou Imagem Única
            if block_split_imgs and len(block_split_imgs) >= 2:
                media_html = f"""<div class="brk-desc-media brk-desc-media-split">
        <div class="brk-split-item">
          <img src="{block_split_imgs[0]}" alt="{safe_title_alt} - Opção 1" loading="lazy" referrerpolicy="no-referrer" />
        </div>
        <div class="brk-split-item">
          <img src="{block_split_imgs[1]}" alt="{safe_title_alt} - Opção 2" loading="lazy" referrerpolicy="no-referrer" />
        </div>
      </div>"""
            elif img_src:
                media_html = f"""<div class="brk-desc-media">
        <img src="{img_src}" alt="{safe_block_alt}" loading="lazy" referrerpolicy="no-referrer" />
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
      <span>Detalhes Técnicos & Cuidados de Conservação</span>
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
        full_html = f"""{brk_tracking_marker(enriched_data.get("sku"), archetype_id)}
<!-- BRK GROUP - DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL SHOPIFY) -->
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
    .brk-sg-card-header {{
      background: {theme_color};
      color: #ffffff;
      padding: 12px 16px;
      border-radius: 10px 10px 0 0;
      text-align: center;
      margin-bottom: 0;
    }}
    .brk-sg-card-title {{
      font-size: 15px;
      font-weight: 900;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: #ffffff;
      margin: 0;
    }}
    .brk-sg-subtitle {{
      font-size: 11.5px;
      color: #ffffff;
      opacity: 0.95;
      margin-top: 3px;
      font-style: italic;
    }}
    .brk-sg-th-row th {{
      background: #1e293b !important;
      color: #ffffff !important;
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
            md_parts.append("### 📋 Detalhes Técnicos & Especificações\n")
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
            md_parts.append("### 📐 Guia de Tamanhos Infantil (1 a 13 Anos | PP ao G2)\n")
            md_parts.append("| Idade / Tamanho | Tórax | Altura | Manga |")
            md_parts.append("| :--- | :--- | :--- | :--- |")
            k_rows = [
                ("1 a 2 Anos (PP)", "31 cm", "41 cm", "31 cm"),
                ("2 a 3 Anos (P)", "33 cm", "45 cm", "35 cm"),
                ("4 a 5 Anos (M)", "35 cm", "49 cm", "37 cm"),
                ("6 a 7 Anos (G)", "38 cm", "52 cm", "39 cm"),
                ("8 a 9 Anos (GG)", "39 cm", "55 cm", "42 cm"),
                ("10 a 11 Anos (G1)", "41 cm", "58 cm", "44 cm"),
                ("12 a 13 Anos (G2)", "43 cm", "61 cm", "45 cm"),
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
