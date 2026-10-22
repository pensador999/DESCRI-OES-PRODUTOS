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
MODO_B_VERSION = "2"


def brk_tracking_marker(sku: str, archetype_id: str) -> str:
    """Comentario HTML invisivel de rastreio: <!-- BRK-MODO-B v1 | sku:X | molde:Y -->"""
    def clean(v):
        return re.sub(r"[^A-Za-z0-9_.\-]", "", str(v or ""))[:60].replace("--", "-")
    prefix = "VTEX-MODO-B" if str(archetype_id or "").startswith("ld_") else "BRK-MODO-B"
    return f"<!-- {prefix} v{MODO_B_VERSION} | sku:{clean(sku)} | molde:{clean(archetype_id)} -->"


_TROCA = {"icon": "sparkle", "title": "Qualidade Oficial BRK", "sub": "Padrão 100% Garantido"}

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
        {"icon": "sparkle", "title": "Qualidade Oficial BRK", "sub": "Procedência Garantida"},
    ],
    "motors_speed": [
        {"icon": "bolt", "title": "Ventilação Ativa", "sub": "Painéis Microperfurados"},
        {"icon": "gear", "title": "Aerodinâmica Pro", "sub": "Modelagem Anatômica"},
        {"icon": "shield", "title": "Costura Resistente", "sub": "Pronta para Off-Road"},
        {"icon": "sparkle", "title": "Qualidade Oficial BRK", "sub": "Garantia Oficial BRK"},
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
        {"icon": "sparkle", "title": "Qualidade Oficial BRK", "sub": "Satisfação Garantida"},
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
        {"icon": "sparkle", "title": "Qualidade Oficial BRK", "sub": "Ajuste Perfeito Garantido"},
    ],
    "closed_footwear_sneakers": [
        {"icon": "shoe", "title": "Palmilha Anatômica", "sub": "Espuma de Alta Densidade"},
        {"icon": "shield", "title": "Solado Antiderrapante", "sub": "Borracha de Alta Tração"},
        {"icon": "care", "title": "Cabedal Respirável", "sub": "Reforços Laterais"},
        {"icon": "sparkle", "title": "Qualidade Oficial BRK", "sub": "Ajuste Perfeito Garantido"},
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
        {"icon": "sparkle", "title": "Garantia Oficial BRK", "sub": "Procedência 100% Original"},
    ],
    "accessories_general": [
        {"icon": "shield", "title": "Resistente à Água", "sub": "E à Exposição Solar"},
        {"icon": "care", "title": "Material Reforçado", "sub": "Alta Resistência"},
        {"icon": "sparkle", "title": "Item Original BRK", "sub": "Colecionável Oficial"},
        {"icon": "sparkle", "title": "Garantia Oficial BRK", "sub": "Procedência 100% Original"},
    ],
    "books_publications": [
        {"icon": "sparkle", "title": "Impressão em Alta Definição", "sub": "Ilustrações Detalhadas"},
        {"icon": "care", "title": "Capa Colorida Laminada", "sub": "Papel Resistente"},
        {"icon": "box", "title": "Ideal para Presentear", "sub": "Para Todas as Idades"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Rastreamento Completo"},
    ],
    # --- Catálogo VTEX (Confeitaria, Bomboniere, Embalagens, Festas, Presentes e Papelaria) ---
    "ld_confeitaria_ingredientes": [
        {"icon": "sparkle", "title": "Padrão Confeitaria Pro", "sub": "Estabilidade & Rendimento"},
        {"icon": "shield", "title": "Textura Homogênea", "sub": "Fácil Incorporação"},
        {"icon": "box", "title": "Embalagem Lacrada", "sub": "Lote Fresco de Fábrica"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
    ],
    "ld_confeitaria_formas_utensilios": [
        {"icon": "shield", "title": "Padrão Profissional", "sub": "Acabamento de Precisão"},
        {"icon": "bolt", "title": "Alta Estabilidade", "sub": "Padronização de Produção"},
        {"icon": "sparkle", "title": "Apresentação Impecável", "sub": "Valoriza suas Receitas"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
    ],
    "ld_bomboniere_chocolates": [
        {"icon": "sparkle", "title": "Sabor & Cremosidade", "sub": "Marca Original Consagrada"},
        {"icon": "box", "title": "Lote Fresco & Lacrado", "sub": "Conservação Garantida"},
        {"icon": "bolt", "title": "Alto Giro Comercial", "sub": "Ideal p/ Festas e Revenda"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
    ],
    "ld_bomboniere_balas_gomas": [
        {"icon": "sparkle", "title": "Cores & Sabores Vivos", "sub": "Sucesso em Lembrancinhas"},
        {"icon": "box", "title": "Pacote Econômico", "sub": "Alto Rendimento por Embalagem"},
        {"icon": "shield", "title": "100% Original", "sub": "Procedência Direta da Marca"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
    ],
    "ld_embalagens_descartaveis": [
        {"icon": "shield", "title": "Estrutura Firme", "sub": "Transporte e Exposição Seguros"},
        {"icon": "box", "title": "Praticidade & Higiene", "sub": "Ideal para Delivery e Eventos"},
        {"icon": "sparkle", "title": "Acabamento Limpo", "sub": "Valoriza seu Produto"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
    ],
    "ld_artigos_festa_decoracao": [
        {"icon": "palette", "title": "Visual Vibrante", "sub": "Destaque na Decoração"},
        {"icon": "sparkle", "title": "Acabamento Festivo", "sub": "Fácil Composição de Cenário"},
        {"icon": "shield", "title": "Material Selecionado", "sub": "Durabilidade Durante o Evento"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
    ],
    "ld_presentes_caixas_sacolas": [
        {"icon": "box", "title": "Estrutura Reforçada", "sub": "Proteção e Elegância"},
        {"icon": "sparkle", "title": "Pronta para Presentear", "sub": "Valoriza Cestas e Kits"},
        {"icon": "palette", "title": "Acabamento Premium", "sub": "Apresentação Sofisticada"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
    ],
    "ld_papelaria_artesanato": [
        {"icon": "gear", "title": "Praticidade no Uso", "sub": "Rotina Escolar, Loja e Ateliê"},
        {"icon": "shield", "title": "Qualidade Comprovada", "sub": "Desempenho Consistente"},
        {"icon": "sparkle", "title": "Acabamento Preciso", "sub": "Ideal para Personalizados"},
        {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Pronta Entrega Imediata"},
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
        Seleciona os 4 selos EXCLUSIVAMENTE pelo arquétipo detectado (ou Kit Híbrido Camisa + Botina).
        Nunca usa palavras soltas do título (ex.: "pesca" em "Vara de Pesca"),
        pois isso contaminava equipamentos com selos de camisa UV (FPU 50+, Dry Fit).
        Arquétipo desconhecido -> selos genéricos e seguros.
        """
        t_low = str(enriched_data.get("formatted_title") or enriched_data.get("title") or "").lower()
        is_kit_shirt_boot = any(w in t_low for w in ["camisa", "camiseta", "blusa", "segunda pele"]) and bool(
            re.search(r'\b(botina|bota|coturno)\b', t_low)
        )
        if is_kit_shirt_boot:
            badges = [
                {"icon": "box", "title": "Kit Completo 2 em 1", "sub": "Camisa BRK + Botina Couro"},
                {"icon": "sun", "title": "Camisa FPU 50+ Dry", "sub": "Proteção Solar & Frescor"},
                {"icon": "shield", "title": "Couro Bovino Legítimo", "sub": "Botina de Alta Resistência"},
                {"icon": "bolt", "title": "Solado Antiderrapante", "sub": "Tração Firme no Campo"},
            ]
            return self._render_quick_badges(theme_color, badges)

        if archetype_id == "drinkware_thermo":
            if "geladeira" in t_low:
                badges = [
                    {"icon": "snowflake", "title": "Compressor 12V/24V", "sub": "Refrigeração Portátil"},
                    {"icon": "bolt", "title": "Proteção de Bateria", "sub": "Painel Digital Inteligente"},
                    {"icon": "shield", "title": "Gabinete Reforçado", "sub": "Isolamento Alta Densidade"},
                    {"icon": "sparkle", "title": "100% Original Elber", "sub": "Garantia Oficial de Fábrica"},
                ]
                return self._render_quick_badges(theme_color, badges)
            if any(w in t_low for w in ["bolsa termica", "bolsa térmica", "caixa termica", "caixa térmica", "cooler"]):
                badges = [
                    {"icon": "snowflake", "title": "Isolamento Térmico", "sub": "Conservação Prolongada"},
                    {"icon": "shield", "title": "Interior Impermeável", "sub": "Fácil Higienização"},
                    {"icon": "bolt", "title": "Alças Reforçadas", "sub": "Transporte Confortável"},
                    {"icon": "sparkle", "title": "Qualidade Oficial", "sub": "Procedência Garantida"},
                ]
                return self._render_quick_badges(theme_color, badges)
        elif archetype_id == "tackle_boxes_storage":
            if any(w in t_low for w in ["primeiros socorros", "bolsa tática", "bolsa tatica"]):
                badges = [
                    {"icon": "shield", "title": "Nylon Oxford 600D", "sub": "Alta Resistência a Rasgos"},
                    {"icon": "box", "title": "Sistema Modular MOLLE", "sub": "Fixação Rápida em Mochilas"},
                    {"icon": "gear", "title": "Divisórias Elásticas", "sub": "Organização Interna"},
                    {"icon": "bolt", "title": "Fecho Engate Rápido", "sub": "Acesso Imediato"},
                ]
                return self._render_quick_badges(theme_color, badges)
            if "suporte porta iscas" in t_low or ("porta iscas" in t_low and "inox" in t_low):
                badges = [
                    {"icon": "shield", "title": "Aço Inox Naval", "sub": "Imune à Ferrugem"},
                    {"icon": "fish", "title": "5 Fendas p/ Iscas", "sub": "Acesso Rápido no Barco"},
                    {"icon": "gear", "title": "Trava Elástica", "sub": "Para Alicates e Tesoura"},
                    {"icon": "sparkle", "title": "Alta Durabilidade", "sub": "Água Doce e Salgada"},
                ]
                return self._render_quick_badges(theme_color, badges)
        elif archetype_id == "closed_footwear_sneakers":
            if bool(re.search(r'\b(botina|bota|coturno)\b', t_low)):
                badges = [
                    {"icon": "shield", "title": "Couro Bovino Legítimo", "sub": "Alta Durabilidade"},
                    {"icon": "bolt", "title": "Solado Antiderrapante", "sub": "Blaqueado de Alta Tração"},
                    {"icon": "sparkle", "title": "Palmilha Anatômica", "sub": "Absorção de Impacto"},
                    {"icon": "care", "title": "Calce Fácil", "sub": "Elásticos Laterais Reforçados"},
                ]
                return self._render_quick_badges(theme_color, badges)
        elif archetype_id == "accessories_general":
            if "barraca" in t_low:
                badges = [
                    {"icon": "shield", "title": "Sobreteto Impermeável", "sub": "Proteção Chuva & Sol"},
                    {"icon": "wind", "title": "Tela Mosquiteiro", "sub": "Ventilação Segura"},
                    {"icon": "bolt", "title": "Varetas Flexíveis", "sub": "Fibra de Alta Resistência"},
                    {"icon": "box", "title": "Bolsa Inclusa", "sub": "Transporte Compacto"},
                ]
                return self._render_quick_badges(theme_color, badges)
            if any(w in t_low for w in ["mesa dobravel", "mesa dobrável", "mesa de camping", "cadeira", "banqueta"]):
                badges = [
                    {"icon": "shield", "title": "Estrutura Tubular", "sub": "Aço Anticorrosivo"},
                    {"icon": "bolt", "title": "Dobrável & Compacta", "sub": "Montagem em Segundos"},
                    {"icon": "sparkle", "title": "Alta Resistência", "sub": "Estabilidade no Terreno"},
                    {"icon": "box", "title": "Bolsa de Transporte", "sub": "Portabilidade Fácil"},
                ]
                return self._render_quick_badges(theme_color, badges)
            if "fogareiro" in t_low:
                badges = [
                    {"icon": "shield", "title": "Aço Inoxidável", "sub": "Alta Durabilidade"},
                    {"icon": "bolt", "title": "Ignição Automática", "sub": "Dispensa Fósforos"},
                    {"icon": "gear", "title": "Trava de Segurança", "sub": "Controle de Chama"},
                    {"icon": "box", "title": "Compacto & Portátil", "sub": "Ideal p/ Camping e Pesca"},
                ]
                return self._render_quick_badges(theme_color, badges)
            if any(w in t_low for w in ["cabo plug", "cabo de força", "cabo de alimentacao", "cabo de alimentação", "fonte conversora"]):
                badges = [
                    {"icon": "bolt", "title": "Acessório Original Elber", "sub": "Encaixe Padrão Direto"},
                    {"icon": "shield", "title": "Proteção Elétrica", "sub": "Contra Surtos e Curto"},
                    {"icon": "gear", "title": "Alimentação Estável", "sub": "12V / 24V Contínuos"},
                    {"icon": "sparkle", "title": "Alta Durabilidade", "sub": "Isolamento Reforçado"},
                ]
                return self._render_quick_badges(theme_color, badges)
            if any(w in t_low for w in ["coleira", "peitoral"]):
                badges = [
                    {"icon": "wind", "title": "Malha Air Mesh", "sub": "Ventilada & Macia"},
                    {"icon": "sun", "title": "Faixas Refletivas 360°", "sub": "Visibilidade Noturna"},
                    {"icon": "shield", "title": "Trava Engate Rápido", "sub": "Ajuste Anatômico"},
                    {"icon": "sparkle", "title": "Guia Inclusa", "sub": "Passeio Seguro"},
                ]
                return self._render_quick_badges(theme_color, badges)
            if any(w in t_low for w in ["personalização", "personalizacao"]):
                badges = [
                    {"icon": "sparkle", "title": "Personalização Oficial", "sub": "Padrão de Fábrica BRK"},
                    {"icon": "shield", "title": "Alta Fixação", "sub": "Termotransferência Pro"},
                    {"icon": "sun", "title": "Não Desbota", "sub": "Alta Durabilidade"},
                    {"icon": "palette", "title": "Tipografia Esportiva", "sub": "Alinhada ao Design"},
                ]
                return self._render_quick_badges(theme_color, badges)

        badges = QUICK_BADGES_BY_ARCHETYPE.get(archetype_id) or [
            {"icon": "shield", "title": "Qualidade Oficial", "sub": "Matéria-Prima Selecionada"},
            {"icon": "sparkle", "title": "Acabamento Premium", "sub": "Rigoroso Padrão BRK"},
            {"icon": "truck", "title": "Envio Rápido & Seguro", "sub": "Rastreamento Completo"},
            {"icon": "sparkle", "title": "Garantia Oficial BRK", "sub": "Procedência 100% Original"},
        ]
        return self._render_quick_badges(theme_color, badges)

    def _build_size_guide(self, theme_color: str, archetype_id: str, is_kids: bool, is_short_sleeve: bool, enriched_data: Dict[str, Any]) -> str:
        if str(archetype_id or "").startswith("ld_"):
            return ""
        title_low = (enriched_data.get("formatted_title") or enriched_data.get("title") or "").lower()
        sku_low = (enriched_data.get("sku") or enriched_data.get("master_sku") or "").lower()

        # 1. Identificar se o produto é comprovadamente de vestuário superior / camisa
        # Nota: Camisas ArmorX e Hybrid possuem "com Luva" no título, portanto "luva" não desqualifica quando é explícita camisa/CAX/HYB
        has_explicit_shirt_marker = (
            any(w in title_low for w in ["camisa", "camiseta", "jersey", "baby look", "babylook", "armorx", "fusionx", "segunda pele"])
            or any(sku_low.startswith(pfx) for pfx in ["c0", "ci", "cadv", "adv", "hyb", "cmb", "cbt", "raglan", "cax", "fusion", "casual", "bp", "cf", "cm", "apc"])
        )
        is_kit_shirt_boot_sg = has_explicit_shirt_marker and bool(
            re.search(r'\b(bota|botina|coturno|tênis|tenis|sapato)\b', title_low)
        )
        non_shirt_exclusions = (
            r'\b(calça|calca|calças|calcas|bermuda|bermudas|shorts|short|macacão|macacao|sandália|sandalia|babuche|chinelo|sapato|tênis|tenis|bota|botina|boaonda|chapéu|chapeu|boné|bone|manguito|manguitos|bandana|tubeneck|buff|balaclava)\b'
            if has_explicit_shirt_marker else
            r'\b(calça|calca|calças|calcas|bermuda|bermudas|shorts|short|macacão|macacao|sandália|sandalia|babuche|chinelo|sapato|tênis|tenis|bota|botina|boaonda|chapéu|chapeu|boné|bone|luva|luvas|manguito|manguitos|bandana|tubeneck|buff|balaclava)\b'
        )
        is_shirt = (
            archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work")
            or has_explicit_shirt_marker
        ) and not bool(re.search(non_shirt_exclusions, title_low))

        # 0. Exclusão estrita de itens não-têxteis com UV ou termos ambíguos (apenas se NÃO for camisa nem Kit Camisa+Calçado)
        if not is_shirt and not is_kit_shirt_boot_sg:
            non_textile_pattern = r'\b(óculos|oculos|faca|facas|canivete|alicate|vara|varas|molinete|carretilha|isca|iscas|linha|linhas|anzol|anzois|anzóis|estojo|garrafa|copo|chaveiro|adesivo|carteira|protetor solar)\b'
            if re.search(non_textile_pattern, title_low):
                return ""

        is_fusion_sg = is_shirt and ("fusion" in title_low or "fusion" in sku_low)
        is_hybrid_sg = is_shirt and ("hybrid" in title_low or sku_low.startswith("hyb"))
        is_armorx_sg = is_shirt and ("armorx" in title_low or sku_low.startswith("cax") or "com luva" in title_low or "e luva" in title_low)
        is_hooded_sg = is_shirt and ("capuz" in title_low or is_fusion_sg or is_hybrid_sg)

        if is_fusion_sg:
            tip_text = "<strong>Como medir com precisão (Linha FusionX — Com Capuz & Bandana Embutida):</strong> A grade do tronco (PP ao G2) segue a mesma modelagem base BRK. <strong>Tórax:</strong> medido de axila a axila | <strong>Altura:</strong> medida da costura do ombro até a barra inferior (<u>sem contar o capuz e a bandana/máscara facial embutida</u>) | <strong>Manga:</strong> medida do ombro ao punho (com extensão elástica e abertura para o polegar/dedeira). O capuz e a bandana acoplada possuem elasticidade anatômica XTech Pro® que se ajusta ao rosto sem apertar."
        elif is_hybrid_sg:
            tip_text = "<strong>Como medir com precisão (Linha Hybrid — Com Capuz Anatômico & Dedeira):</strong> A grade do tronco (PP ao G2) segue a mesma modelagem base BRK. <strong>Tórax:</strong> medido de axila a axila | <strong>Altura:</strong> medida da costura do ombro até a barra inferior (<u>sem contar a altura do capuz integrado</u>) | <strong>Manga:</strong> medida do ombro ao punho (com extensão elástica e abertura para o polegar/dedeira)."
        elif is_armorx_sg:
            tip_text = "<strong>Como medir com precisão (Linha ArmorX — Com Luva Integrada no Punho):</strong> A grade do tronco (PP ao G2) segue a mesma modelagem base BRK. <strong>Tórax:</strong> medido de axila a axila | <strong>Altura:</strong> medida da costura do ombro até a barra inferior (sem contar a gola alta) | <strong>Manga:</strong> medida do ombro à base do punho (contando com prolongamento anatômico com abertura para o polegar que protege o dorso da mão)."
        elif is_hooded_sg:
            tip_text = "<strong>Como medir com precisão (Modelo com Capuz Integrado):</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura da costura do ombro à barra inferior, <u>desconsiderando o capuz</u> | Manga do ombro ao punho)."
        else:
            sleeve_measure_lbl = "Manga do ombro à barra da manga curta" if is_short_sleeve else "Manga do ombro ao punho"
            tip_text = f"<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Altura do ombro à barra | {sleeve_measure_lbl}). Dica: compare com uma peça sua estendida para escolher o caimento ideal."

        if is_fusion_sg:
            special_shirt_prefix = "Camisa UV50+ FusionX (Capuz + Bandana Embutida + Dedeira)"
        elif is_hybrid_sg:
            special_shirt_prefix = "Camisa UV50+ Hybrid (Capuz Anatômico + Punho com Dedeira)"
        elif is_armorx_sg:
            special_shirt_prefix = "Camisa UV50+ ArmorX (Punho Estendido com Luva Integrada)"
        elif is_hooded_sg:
            special_shirt_prefix = "Camisa Manga Longa UV50 com Capuz Integrado"
        else:
            special_shirt_prefix = None

        if is_kit_shirt_boot_sg:
            guide_title = "Guia de Medidas do Kit — Camisa (PP ao G2) & Botina (34 ao 45)"
            tip_text = "<strong>Como conferir as medidas dos 2 itens do Kit:</strong> Para a <strong>Camisa</strong>, compare Tórax (axila a axila), Altura (ombro à barra) e Manga com uma peça sua estendida. Para a <strong>Botina em Couro Legítimo</strong>, meça o comprimento da palmilha interna de um calçado confortável do calcanhar até a ponta do dedão."
            shirt_sub_prefix = "Segunda Pele Térmica UV50+" if any(w in title_low for w in ["térmica", "termica", "segunda pele"]) else ("Camisa Manga Curta UV50+" if is_short_sleeve else "Camisa Manga Longa UV50+")
            subtitle_shirt = f"{shirt_sub_prefix} | *As medidas podem variar de 2cm a 3cm"
            s_rows = [
                ("PP", "49,5 cm", "67 cm", "56 cm"),
                ("P", "51,5 cm", "69 cm", "59,5 cm"),
                ("M", "54 cm", "71 cm", "62 cm"),
                ("G", "56 cm", "72 cm", "64 cm"),
                ("GG", "59 cm", "74 cm", "64 cm"),
                ("G1", "62 cm", "75 cm", "66 cm"),
                ("G2", "65 cm", "76,5 cm", "66 cm"),
            ]
            b_rows = [
                ("34", "23,0 cm"), ("35", "23,7 cm"), ("36", "24,3 cm"),
                ("37", "25,0 cm"), ("38", "25,7 cm"), ("39", "26,3 cm"),
                ("40", "27,0 cm"), ("41", "27,7 cm"), ("42", "28,3 cm"),
                ("43", "29,0 cm"), ("44", "29,7 cm"), ("45", "30,3 cm"),
            ]
            s_rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in s_rows])
            b_rows_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td></tr>\n" for r in b_rows])
            table_html = f"""<div class="brk-sg-card-header">
        <div class="brk-sg-card-title">ITEM 01 — TABELA DE MEDIDAS DA CAMISA (PP AO G2)</div>
        <div class="brk-sg-subtitle">{subtitle_shirt}</div>
      </div>
      <table class="brk-sg-table" style="margin-bottom: 18px;">
        <thead>
          <tr class="brk-sg-th-row">
            <th>TAMANHO</th>
            <th>TÓRAX</th>
            <th>ALTURA</th>
            <th>MANGA</th>
          </tr>
        </thead>
        <tbody>
{s_rows_html}        </tbody>
      </table>
      <div class="brk-sg-card-header">
        <div class="brk-sg-card-title">ITEM 02 — GUIA DE TAMANHOS DA BOTINA / CALÇADO (34 AO 45)</div>
        <div class="brk-sg-subtitle">Botina Country em Couro Bovino Legítimo | Medida da Palmilha Interna</div>
      </div>
      <table class="brk-sg-table">
        <thead>
          <tr class="brk-sg-th-row">
            <th>NUMERAÇÃO BR</th>
            <th>COMPRIMENTO DA PALMILHA (CM)</th>
          </tr>
        </thead>
        <tbody>
{b_rows_html}        </tbody>
      </table>"""

        elif is_shirt:
            # 1.1 Camisas de Botão / Utilitárias Work (CMB - Sarja/Algodão corte reto de trabalho)
            is_work_guide = (
                (archetype_id == "shirts_button_work" or "cmb" in sku_low or "cbt" in sku_low or ("work" in title_low and "camisa" in title_low and not any(w in title_low for w in ["xtech", "dry", "uv", "uv50", "pesca"])))
                and not sku_low.startswith("c0") and not sku_low.startswith("ci")
            )
            if is_work_guide:
                is_fem_work = any(w in title_low for w in ["feminina", "feminino", "baby look", "babylook"]) or "bl" in sku_low
                manga_header = "Manga Curta" if is_short_sleeve else "Manga Longa"
                if is_fem_work:
                    guide_title = "Tabela de Medidas Feminina - Camisas Country & Classic de Botão (P ao G2)"
                    tip_text = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Busto/Tórax | Comprimento da gola à barra | Manga). Modelagem feminina acinturada."
                    rows = [
                        ("P (36-38)", "92 cm", "61 cm", "19 cm" if is_short_sleeve else "60 cm"),
                        ("M (40)", "96 cm", "63 cm", "20 cm" if is_short_sleeve else "61 cm"),
                        ("G (42)", "102 cm", "65 cm", "21 cm" if is_short_sleeve else "62 cm"),
                        ("GG (44)", "108 cm", "67 cm", "22 cm" if is_short_sleeve else "63 cm"),
                        ("G1 (46)", "114 cm", "69 cm", "23 cm" if is_short_sleeve else "64 cm"),
                        ("G2 (48)", "120 cm", "71 cm", "24 cm" if is_short_sleeve else "65 cm"),
                    ]
                else:
                    guide_title = "Tabela de Medidas - Camisas Work & Utilitárias de Botão (P ao G2)"
                    tip_text = "<strong>Como medir com precisão:</strong> Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | Comprimento da gola à barra | Manga). Modelagem confortável de trabalho."
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

            # 1.1b Kit Casal (Exibe AMBAS as tabelas: Masculina + Feminina Baby Look)
            elif "casal" in title_low and ("kit" in title_low or "combo" in title_low):
                guide_title = "Tabela de Medidas Kit Casal - Masculino & Feminino Baby Look (PP ao G2)"
                shirt_sub_prefix = special_shirt_prefix or ("Camisa Manga Curta UV50" if is_short_sleeve else "Camisa Manga Longa UV50")
                subtitle = f"{shirt_sub_prefix} | *As medidas podem variar de 2cm a 3cm"
                m_rows = [
                    ("PP", "49,5 cm", "67 cm", "56 cm"),
                    ("P", "51,5 cm", "69 cm", "59,5 cm"),
                    ("M", "54 cm", "71 cm", "62 cm"),
                    ("G", "56 cm", "72 cm", "64 cm"),
                    ("GG", "59 cm", "74 cm", "64 cm"),
                    ("G1", "62 cm", "75 cm", "66 cm"),
                    ("G2", "65 cm", "76,5 cm", "66 cm"),
                ]
                f_rows = [
                    ("Baby Look PP", "33 cm", "51 cm", "53 cm"),
                    ("Baby Look P", "37 cm", "54 cm", "55 cm"),
                    ("Baby Look M", "43 cm", "57 cm", "59 cm"),
                    ("Baby Look G", "47 cm", "60 cm", "60 cm"),
                    ("Baby Look GG", "47 cm", "60 cm", "61 cm"),
                    ("Baby Look G1", "50 cm", "62 cm", "61 cm"),
                    ("Baby Look G2", "55 cm", "64 cm", "63 cm"),
                ]
                m_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in m_rows])
                f_html = "".join([f"          <tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n" for r in f_rows])
                table_html = f"""<div class="brk-sg-card-header">
        <div class="brk-sg-card-title">MASCULINO</div>
        <div class="brk-sg-subtitle">{subtitle}</div>
      </div>
      <table class="brk-sg-table" style="margin-bottom: 18px;">
        <thead>
          <tr class="brk-sg-th-row">
            <th>TAMANHO</th>
            <th>TÓRAX</th>
            <th>ALTURA</th>
            <th>MANGA</th>
          </tr>
        </thead>
        <tbody>
{m_html}        </tbody>
      </table>
      <div class="brk-sg-card-header">
        <div class="brk-sg-card-title">FEMININO (BABY LOOK)</div>
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
{f_html}        </tbody>
      </table>"""

            # 1.2 Camisas UV C0 Infantil (1 a 13 Anos | PP ao G2)
            elif (
                is_kids
                or any(w in title_low for w in ["infantil", "kids", "juvenil"])
                or "kids" in sku_low
                or "inf" in sku_low
                or (
                    (sku_low.startswith("ci") or bool(re.search(r'^(?:c0|ci|cf|cm|casual|adv|cadv|ccpbr|bp|hyb|fusion|cax|raglan)\d+i(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$', sku_low)))
                    and not any(w in title_low for w in ["feminina", "feminino", "baby look", "babylook", "masculina", "masculino", "adulto"])
                )
            ):
                guide_title = "Guia de Tamanhos Infantil (1 a 13 Anos)"
                badge_title = "INFANTIL"
                kids_sleeve_lbl = "Manga do ombro à barra da manga curta" if is_short_sleeve else "Manga do ombro ao punho"
                kids_height_lbl = "Altura do ombro à barra, sem contar o capuz" if is_hooded_sg else "Altura do ombro à barra"
                tip_text = f"<strong>Escolha por Idade com Referência de Tamanho (PP ao G2):</strong> Na linha Infantil BRK, a seleção é guiada pela faixa de idade (1 a 13 Anos) mantendo a indicação do tamanho equivalente (PP ao G2). Medidas tiradas com a peça plana em centímetros (Tórax de axila a axila | {kids_height_lbl} | {kids_sleeve_lbl})."
                shirt_sub_prefix = special_shirt_prefix or ("Camiseta Algodão Premium" if archetype_id == "agro_field" else ("Camisa Manga Curta UV50" if is_short_sleeve else "Camisa Manga Longa UV50"))
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
                shirt_sub_prefix = special_shirt_prefix or ("Camiseta Algodão Premium" if archetype_id == "agro_field" else ("Camisa Manga Curta UV50" if is_short_sleeve else "Camisa Manga Longa UV50"))
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
                shirt_sub_prefix = special_shirt_prefix or ("Camiseta Algodão Premium" if archetype_id == "agro_field" else ("Camisa Manga Curta UV50" if is_short_sleeve else "Camisa Manga Longa UV50"))
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

        is_ld_schema = str(enriched_data.get("archetype_id") or "").startswith("ld_") or enriched_data.get("store_key") == "loja_doce"
        default_title = "Produto Oficial" if is_ld_schema else "Produto BRK"
        default_brand = "Linha Oficial" if is_ld_schema else "BRK"
        formatted_title = enriched_data.get("formatted_title") or enriched_data.get("title", default_title)
        brand_name = enriched_data.get("brand_name") or default_brand
        if is_ld_schema and str(brand_name).upper() in ("BRK", "LOJA DOCE", "LOJA DOCE IMPORT"):
            brand_name = "Linha Oficial"
        sku = str(enriched_data.get("sku") or enriched_data.get("master_sku") or enriched_data.get("id") or "")
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
        fallback_desc = f"{formatted_title} original com procedência garantida." if is_ld_schema else f"{formatted_title} oficial com qualidade e garantia BRK."
        short_desc = " ".join(desc_parts)[:280] if desc_parts else fallback_desc

        block_imgs = [b.get("image") for b in blocks if isinstance(b, dict) and b.get("image")]
        raw_imgs = block_imgs or enriched_data.get("images") or enriched_data.get("cdn_images") or enriched_data.get("gallery") or []
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
        img2 = hw_pool[1] if len(hw_pool) > 1 else ("https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg" if len(hw_pool) == 0 else "")
        img3 = hw_pool[2] if len(hw_pool) > 2 else ("https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg" if len(hw_pool) == 0 else "")
        img4 = hw_pool[3] if len(hw_pool) > 3 else ("https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg" if len(hw_pool) == 0 else "")

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

        # Montagem dos Detalhes em HTML (omite <img> se o produto tiver menos de 4 fotos na galeria para jamais duplicar URL)
        details_html = []
        for d in details:
            safe_d_alt = str(d['alt']).replace('"', '&quot;')
            img_div = f'<div class="brk-cap-detail-image"><img src="{d['img']}" alt="{safe_d_alt}"></div>\n' if d.get("img") else ""
            details_html.append(f"""<!-- {d['title']} -->
<article class="brk-cap-detail-item">
{img_div}<h3>{d['title']}</h3>
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

    def _get_media_infographic_meta(
        self,
        idx: int,
        archetype_id: str,
        enriched_data: Dict[str, Any],
        is_split: bool = False
    ) -> Dict[str, Any]:
        """
        Retorna metadados de infográfico técnico (badge de ângulo, ícone, legenda técnica, pílula e flag de zoom)
        para transformar fotos de estúdio nos 3 Atos em cards informativos visuais sem poluição semântica.
        """
        t_low = str(enriched_data.get("formatted_title") or enriched_data.get("title") or "").lower()
        sku_low = str(enriched_data.get("sku") or enriched_data.get("master_sku") or "").lower()
        tags_low = str(enriched_data.get("tags") or "").lower()
        is_short_sleeve = bool(enriched_data.get("is_short_sleeve", False)) or any(
            w in t_low for w in ["manga curta", "camiseta", "t-shirt", "tshirt", "baby look"]
        )
        is_shirt_arch = archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work")

        has_uv = any(w in t_low or w in tags_low for w in ["uv", "fpu", "proteção solar", "protecao solar", "xtech", "dry"])
        is_cotton = (
            (any(w in t_low or w in tags_low for w in ["algodão", "algodao", "cotton", "100% algod"]) and "algodão sombreado" not in t_low and "algodao sombreado" not in t_low and not has_uv)
            or (archetype_id == "agro_field" and not has_uv and "camiseta" in t_low)
        )
        is_kit_shirt_boot = any(w in t_low for w in ["camisa", "camiseta", "blusa", "segunda pele"]) and bool(
            re.search(r'\b(botina|bota|coturno)\b', t_low)
        )

        if is_kit_shirt_boot:
            if idx == 0:
                return {
                    "view_tag": "ITEM 01 DO KIT • ATO 01",
                    "icon": "sun",
                    "label": "Item 01 do Kit: Camisa Técnica BRK UV50+",
                    "pill": "Conforto & Proteção",
                    "zoom_act3": False,
                }
            if idx == 1:
                return {
                    "view_tag": "ITEM 02 DO KIT • ATO 02",
                    "icon": "shield",
                    "label": "Item 02 do Kit: Botina em Couro Bovino Legítimo",
                    "pill": "Solado Antiderrapante",
                    "zoom_act3": False,
                }
            return {
                "view_tag": "CONJUNTO COMPLETO • ATO 03",
                "icon": "sparkle",
                "label": "Conjunto Completo: Proteção do Tronco aos Pés",
                "pill": "Kit 2 em 1",
                "zoom_act3": False,
            }

        if str(archetype_id or "").startswith("ld_"):
            if idx == 0:
                return {
                    "view_tag": "APRESENTAÇÃO • ATO 01",
                    "icon": "sparkle",
                    "label": "Apresentação Comercial & Embalagem Original",
                    "pill": "Curadoria Oficial",
                    "zoom_act3": False,
                }
            if idx == 1:
                return {
                    "view_tag": "ESPECIFICAÇÃO • ATO 02",
                    "icon": "bolt",
                    "label": "Rendimento, Composição & Padrão Profissional",
                    "pill": "Alto Desempenho",
                    "zoom_act3": False,
                }
            return {
                "view_tag": "APLICAÇÃO • ATO 03",
                "icon": "shield",
                "label": "Acabamento & Praticidade na Rotina",
                "pill": "Procedência Original",
                "zoom_act3": False,
            }

        if idx == 0:
            if is_split:
                return {
                    "view_tag": "GALERIA OFICIAL • ATO 01",
                    "icon": "palette",
                    "label": "Padrões de Cores & Acabamento Visual",
                    "pill": "Alta Atratividade",
                    "zoom_act3": False,
                }
            if is_shirt_arch:
                return {
                    "view_tag": "VISTA FRONTAL • ATO 01",
                    "icon": "sparkle",
                    "label": "Modelagem Anatômica & Identidade Visual",
                    "pill": "Caimento Oficial BRK",
                    "zoom_act3": False,
                }
            return {
                "view_tag": "APRESENTAÇÃO • ATO 01",
                "icon": "sparkle",
                "label": "Design Funcional & Construção Original",
                "pill": "Padrão Oficial",
                "zoom_act3": False,
            }

        if idx == 1:
            if is_shirt_arch:
                if is_cotton:
                    return {
                        "view_tag": "ENGENHARIA TÊXTIL • ATO 02",
                        "icon": "care",
                        "label": "Malha 100% Algodão Premium & Respirabilidade",
                        "pill": "Toque Nobre",
                        "zoom_act3": False,
                    }
                if archetype_id == "shirts_button_work" or any(w in t_low for w in ["botão", "botao", "work", "sarja"]) or sku_low.startswith(("cmb", "cbt")):
                    return {
                        "view_tag": "ESTRUTURA TÊXTIL • ATO 02",
                        "icon": "shield",
                        "label": "Tecido de Alta Gramatura & Resistência",
                        "pill": "Uso Operacional",
                        "zoom_act3": False,
                    }
                return {
                    "view_tag": "TECNOLOGIA TÊXTIL • ATO 02",
                    "icon": "sun",
                    "label": "Painel Dorsal & Tecido Tecnológico UV50+",
                    "pill": "Secagem Rápida",
                    "zoom_act3": False,
                }
            return {
                "view_tag": "PERFORMANCE • ATO 02",
                "icon": "bolt",
                "label": "Engenharia de Materiais & Desempenho",
                "pill": "Alta Durabilidade",
                "zoom_act3": False,
            }

        # Ato 3 (idx == 2)
        blocks_meta = enriched_data.get("narrative_blocks") or []
        act3_block = (blocks_meta[2] if len(blocks_meta) > 2 and isinstance(blocks_meta[2], dict) else enriched_data.get("act3")) or {}
        act3_img = str(act3_block.get("image") or "")
        act3_fname = act3_img.lower().split("?")[0].split("/")[-1] if act3_img else ""
        is_hand_glove_img = bool(
            act3_block.get("is_hand_glove_act3")
            or "mkpmaopunho" in act3_fname
            or any(tok in act3_fname for tok in ("44c44e9612c4", "f2e090fe8ba1", "62aa6b25986", "d77f4f49cf301", "8059f931198b", "dc7c509bffe8", "aa4b90bdb553", "48aec41d5e02"))
            or (
                re.match(r'^cax\d+(?:[._-]|$)', act3_fname)
                and not any(k in act3_fname for k in ("01fem", "02fem", "03fem", "01masc", "02masc", "03masc", "frente", "costas"))
                and not re.match(r'^cax\d+(?:bl|i)?[1234]\.', act3_fname)
            )
        )
        is_humanized_model_img = bool(
            act3_block.get("is_humanized_model_act3")
            or any(tok in act3_fname for tok in ("aayvxta", "tb1io0b", "5m5m0yc", "iyewcrl", "dw7n5ow", "yx5ql6y", "nc5vehx", "vbu8izl", "gemini_generat"))
            or re.match(r'^c028\d+(?:bl|i)?(?:_[0-9a-f-]+)?\.webp$', act3_fname)
        )

        if is_shirt_arch:
            is_fusion = "fusion" in t_low or "fusion" in sku_low
            is_hybrid = "hybrid" in t_low or sku_low.startswith("hyb") or "hybrid" in sku_low
            has_capuz = is_fusion or is_hybrid or any(w in t_low for w in ["capuz", "hood", "balaclava"]) or sku_low.startswith("ccp")
            is_armor = "armor" in t_low or sku_low.startswith("cax")
            is_raglan = any(w in t_low for w in ["segunda pele", "raglan", "thermal", "termica", "térmica"]) or "raglan" in sku_low
            is_button = archetype_id == "shirts_button_work" or any(w in t_low for w in ["botão", "botao", "work", "operacional"]) or sku_low.startswith(("cmb", "cbt"))
            is_crew = (
                any(w in t_low for w in ["careca", "redonda", "sem zíper", "sem ziper", "casual", "t-shirt", "camiseta"])
                or sku_low.startswith(("casual", "bp", "cm", "cadv", "cf"))
                or bool(re.match(r'^ci0(?:54|7[2-9]|8[0-4])', sku_low))
            )
            is_kids_meta = bool(enriched_data.get("is_kids", False)) or any(w in t_low for w in ["infantil", "kids", "juvenil"]) or sku_low.startswith("ci")
            is_casal_meta = "casal" in t_low and ("kit" in t_low or "combo" in t_low)

            if is_hand_glove_img:
                lbl, pill = "Detalhe Humanizado: Furo Anatômico p/ Polegar", "Proteção no Dorso da Mão"
            elif is_humanized_model_img:
                if is_fusion:
                    lbl, pill = "Caimento Real: Capuz, Máscara & Punho em Ação", "Proteção 360°"
                else:
                    lbl, pill = "Caimento Real no Corpo: Mobilidade & Proteção Solar", "Uso na Prática"
            elif is_fusion:
                lbl, pill = "Foco Frontal: Capuz, Máscara Facial & Dedeira", "Proteção 360°"
            elif is_hybrid:
                lbl, pill = "Foco Frontal: Capuz Anatômico & Punho c/ Dedeira", "Nuca & Mãos"
            elif has_capuz:
                lbl, pill = "Foco Frontal: Capuz Integrado & Proteção de Nuca", "Barreira Solar"
            elif is_armor:
                lbl, pill = "Vista 3/4: Gola Padre c/ Zíper & Punho c/ Dedeira", "Proteção de Punho"
            elif is_raglan:
                lbl, pill = "Foco Frontal: Corte Raglan & Costura Plana", "Zero Atrito"
            elif is_button:
                lbl, pill = "Foco Frontal: Colarinho Estruturado & Botões", "Costura em X"
            elif is_cotton:
                lbl, pill = "Foco Frontal: Gola em Ribana & Costura Dupla", "Anti-Deformação"
            elif is_crew or is_short_sleeve:
                lbl, pill = "Foco Frontal: Gola Anatômica & Costura Dupla", "Toque Suave"
            elif is_kids_meta:
                lbl, pill = "Foco Frontal: Costuras Planas & Acabamento Macio", "Toque Suave"
            elif is_casal_meta:
                lbl, pill = "Foco Frontal: Acabamento Duplo & Costura Plana", "Kit Casal"
            else:
                lbl, pill = "Foco Frontal: Gola Padre Anatômica, Zíper & Punhos", "Pesponto Duplo"

            return {
                "view_tag": "ZOOM DE ACABAMENTO • ATO 03",
                "icon": "shield",
                "label": lbl,
                "pill": pill,
                "zoom_act3": True,
                "is_hand_glove_img": is_hand_glove_img,
            }

        if archetype_id == "neck_gaiters_balaclavas":
            return {
                "view_tag": "USO NA PRÁTICA • ATO 03",
                "icon": "shield",
                "label": "Ajuste Anatômico no Rosto & Pescoço em Uso Real",
                "pill": "Estabilidade em Movimento",
                "zoom_act3": False,
            }

        return {
            "view_tag": "DETALHE TÉCNICO • ATO 03",
            "icon": "shield",
            "label": "Acabamento de Precisão & Componentes",
            "pill": "Rigor Oficial BRK",
            "zoom_act3": False,
        }

    def _build_lojadoce_infographic_card(
        self,
        idx: int,
        archetype_id: str,
        theme_color: str,
        theme_bg: str,
        enriched_data: Dict[str, Any],
        primary_img: str,
        safe_title_alt: str,
        ml_track_attrs: str,
    ) -> str:
        """
        Gera o Card Visual Infográfico 100% HTML/CSS + SVG inline para Atos sem foto dedicada
        no catálogo VTEX (eliminando blocos sem imagem e mantendo os 3 Atos com coluna visual).
        - Ato 2 (idx == 1): Infográfico Técnico de Rendimento, Medidas & Parâmetros de Trabalho
        - Ato 3 (idx == 2): Infográfico de Segurança Alimentar / ANVISA, Conservação & Procedência
        """
        yield_info = enriched_data.get("yield_info") if isinstance(enriched_data.get("yield_info"), dict) else {}
        b2b_economics = enriched_data.get("b2b_economics") if isinstance(enriched_data.get("b2b_economics"), dict) else {}
        allergen_info = enriched_data.get("allergen_info") if isinstance(enriched_data.get("allergen_info"), dict) else {}
        vtex_specs = enriched_data.get("vtex_specifications") if isinstance(enriched_data.get("vtex_specifications"), dict) else {}
        specs_list = enriched_data.get("specs") if isinstance(enriched_data.get("specs"), list) else []
        specs_map = {str(s.get("label", "")).strip(): str(s.get("value", "")).strip() for s in specs_list if isinstance(s, dict)}

        brand_name = str(
            enriched_data.get("brand_name")
            or vtex_specs.get("Marca")
            or specs_map.get("Marca / Fabricante")
            or "Original"
        ).strip()
        sku_code = str(
            enriched_data.get("sku")
            or enriched_data.get("master_sku")
            or vtex_specs.get("Código de Referência (SKU)")
            or vtex_specs.get("Código SKU")
            or specs_map.get("Código de Referência (SKU)")
            or specs_map.get("Código SKU")
            or ""
        ).strip()
        care_tips = str(
            enriched_data.get("care_tips")
            or "Conservar na embalagem original fechada, em local seco, fresco e arejado, ao abrigo da luz solar direta."
        ).strip()

        peso_medida = (
            vtex_specs.get("Peso Líquido / Volume")
            or vtex_specs.get("Peso / Volume")
            or vtex_specs.get("Dimensões / Medidas")
            or specs_map.get("Peso Líquido / Volume")
            or specs_map.get("Peso / Volume Líquido")
            or specs_map.get("Dimensões / Medidas")
            or "Padrão Oficial de Fábrica"
        )
        qtd_emb = (
            vtex_specs.get("Apresentação / Quantidade")
            or vtex_specs.get("Quantidade por Embalagem")
            or specs_map.get("Apresentação / Quantidade")
            or specs_map.get("Conteúdo da Embalagem")
            or "Embalagem Comercial"
        )
        dim_summary = f"{peso_medida} • {qtd_emb}" if peso_medida != qtd_emb else peso_medida
        pill_code = f"SKU {sku_code}" if sku_code else f"Marca {brand_name}"

        if idx == 0:
            cat_val = (
                vtex_specs.get("Categoria VTEX")
                or specs_map.get("Departamento / Linha")
                or specs_map.get("Categoria Técnica")
                or "Confeitaria, Festas & Embalagens"
            )
            uso_val = (
                specs_map.get("Uso Recomendado")
                or specs_map.get("Modo de Aplicação Técnica")
                or vtex_specs.get("Uso Recomendado")
                or "Pronto para uso profissional e doméstico com padrão de fábrica."
            )
            return f"""<div class="brk-desc-media brk-media-card brk-infographic-card">
        <div class="brk-infog-header">
          <span class="brk-infog-head-left">{get_svg_icon('sparkle', color=theme_color, size=14)} <span>APRESENTAÇÃO • FICHA COMERCIAL & ORIGEM</span></span>
          <span class="brk-infog-head-pill">{pill_code}</span>
        </div>
        <div class="brk-infog-stage">
          <div class="brk-infog-hero">
            <div class="brk-infog-diagram">
              <div class="brk-infog-svg-badge">
                <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <rect x="6" y="8" width="36" height="32" rx="6" fill="{theme_bg}" stroke="{theme_color}" stroke-width="2.5"/>
                  <path d="M14 18H34M14 25H28M14 32H22" stroke="{theme_color}" stroke-width="2.5" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="brk-infog-hero-copy">
                <span class="brk-infog-kicker">IDENTIFICAÇÃO OFICIAL DO ITEM</span>
                <strong class="brk-infog-headline">Marca {brand_name} • {peso_medida}</strong>
                <span class="brk-infog-subline">{qtd_emb} • {pill_code}</span>
              </div>
            </div>
          </div>
          <div class="brk-infog-metrics">
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('box', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Apresentação Comercial & Embalagem</span>
              </div>
              <div class="brk-infog-metric-val">{dim_summary}</div>
            </div>
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('sparkle', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Departamento & Linha Oficial</span>
              </div>
              <div class="brk-infog-metric-val">{cat_val}</div>
            </div>
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('check', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Aplicação & Indicação Principal</span>
              </div>
              <div class="brk-infog-metric-val">{uso_val}</div>
            </div>
          </div>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">{get_svg_icon('sparkle', color=theme_color, size=14)} <span>Apresentação Comercial & Embalagem Original</span></span>
          <span class="brk-media-info-pill">Curadoria Oficial</span>
        </div>
      </div>"""

        if idx == 1:
            yield_val = (
                yield_info.get("yield_estimate")
                or yield_info.get("dimensional_equiv")
                or vtex_specs.get("Rendimento Prático Estimado")
                or vtex_specs.get("Rendimento Estimado")
                or vtex_specs.get("Equivalência Dimensional / Capacidade")
                or vtex_specs.get("Equivalência Dimensional")
                or specs_map.get("Rendimento Prático Estimado")
                or specs_map.get("Rendimento Estimado")
                or specs_map.get("Equivalência Dimensional / Capacidade")
                or specs_map.get("Equivalência Dimensional")
                or yield_info.get("resumo_rendimento")
                or "Dimensionamento otimizado para padronização de receitas, montagem e controle exato de custo por unidade produzida."
            )
            dim_equiv_extra = (
                yield_info.get("dimensional_equiv")
                or vtex_specs.get("Equivalência Dimensional / Capacidade")
                or specs_map.get("Equivalência Dimensional / Capacidade")
                or ""
            )
            if dim_equiv_extra and dim_equiv_extra != yield_val and dim_equiv_extra not in dim_summary:
                supply_format_val = f"{dim_summary} ({dim_equiv_extra})"
            else:
                supply_format_val = dim_summary

            hero_headline = peso_medida if peso_medida != "Padrão Oficial de Fábrica" else dim_summary
            hero_subline = f"{qtd_emb} • Marca {brand_name}" if peso_medida != qtd_emb else f"Marca {brand_name} • Medição Padronizada"

            tech_param_label = "Parâmetro Técnico de Aplicação"
            tech_param_val = ""
            for cand_lbl in (
                "Classificação Técnica",
                "Necessita Temperagem?",
                "Modo de Aplicação Técnica",
                "Tipo de Inflagem Recomendada",
                "Inflagem / Aplicação",
                "Estabilidade Térmica",
                "Solubilidade / Base Técnica",
                "Material Principal",
                "Uso Recomendado",
                "Sabor / Tonalidade",
                "Sabor / Cor / Tonalidade",
                "Categoria Técnica",
                "Departamento / Linha",
                "Categoria VTEX",
            ):
                if specs_map.get(cand_lbl):
                    tech_param_label = cand_lbl
                    tech_param_val = specs_map[cand_lbl]
                    break
            if not tech_param_val:
                if yield_info.get("gas_and_arch"):
                    tech_param_label = "Tipo de Inflagem Recomendada"
                    tech_param_val = str(yield_info["gas_and_arch"])
                else:
                    for v_lbl in (
                        "Modo de Aplicação Técnica",
                        "Tipo de Inflagem Recomendada",
                        "Inflagem / Aplicação",
                        "Uso Recomendado",
                        "Sabor / Cor / Tonalidade",
                        "Sabor / Tonalidade",
                        "Material",
                        "Categoria VTEX",
                    ):
                        if vtex_specs.get(v_lbl):
                            tech_param_label = v_lbl
                            tech_param_val = str(vtex_specs[v_lbl])
                            break
            if not tech_param_val:
                tech_param_val = "Desempenho calibrado para uso profissional e doméstico com alta estabilidade."

            b2b_econ_val = (
                b2b_economics.get("resumo_economia_b2b")
                or b2b_economics.get("value")
                or vtex_specs.get("Economia & Custo Unitário (B2B)")
                or specs_map.get("Economia & Custo Unitário (B2B)")
                or ""
            )
            b2b_metric_html = ""
            if b2b_econ_val:
                b2b_metric_html = f"""
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('bolt', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Economia & Custo Unitário (B2B)</span>
              </div>
              <div class="brk-infog-metric-val">{b2b_econ_val}</div>
            </div>"""

            thumb_html = ""
            if primary_img:
                thumb_html = f"""
            <div class="brk-infog-thumb brk-stage-loupe" {ml_track_attrs}>
              <img src="{primary_img}" alt="{safe_title_alt} - Zoom de Especificação" class="brk-infog-crop-zoom" loading="lazy" referrerpolicy="no-referrer" />
              <div class="brk-ml-zoom-layer" style="background-image: url('{primary_img}');"></div>
              <span class="brk-infog-thumb-badge">Zoom 2.4x</span>
            </div>"""

            return f"""<div class="brk-desc-media brk-media-card brk-infographic-card">
        <div class="brk-infog-header">
          <span class="brk-infog-head-left">{get_svg_icon('ruler', color=theme_color, size=14)} <span>INFOGRÁFICO • RENDIMENTO & MEDIDAS</span></span>
          <span class="brk-infog-head-pill">{pill_code}</span>
        </div>
        <div class="brk-infog-stage">
          <div class="brk-infog-hero">{thumb_html}
            <div class="brk-infog-diagram">
              <div class="brk-infog-svg-badge">
                <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <rect x="4" y="10" width="40" height="28" rx="6" fill="{theme_bg}" stroke="{theme_color}" stroke-width="2.5"/>
                  <path d="M12 18V26M18 18V23M24 18V28M30 18V23M36 18V26" stroke="{theme_color}" stroke-width="2.5" stroke-linecap="round"/>
                  <circle cx="24" cy="31" r="2.5" fill="{theme_color}"/>
                </svg>
              </div>
              <div class="brk-infog-hero-copy">
                <span class="brk-infog-kicker">ESPECIFICAÇÃO COMERCIAL</span>
                <strong class="brk-infog-headline">{hero_headline}</strong>
                <span class="brk-infog-subline">{hero_subline}</span>
              </div>
            </div>
          </div>
          <div class="brk-infog-metrics">
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('ruler', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Rendimento & Equivalência Prática</span>
              </div>
              <div class="brk-infog-metric-val">{yield_val}</div>
            </div>{b2b_metric_html}
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('box', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Formato de Fornecimento & Medidas</span>
              </div>
              <div class="brk-infog-metric-val">{supply_format_val}</div>
            </div>
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('gear', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">{tech_param_label}</span>
              </div>
              <div class="brk-infog-metric-val">{tech_param_val}</div>
            </div>
          </div>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">{get_svg_icon('ruler', color=theme_color, size=14)} <span>Infográfico de Rendimento & Dimensionamento</span></span>
          <span class="brk-media-info-pill">Ficha Dimensional</span>
        </div>
      </div>"""

        allergen_spec_keys = (
            "Informação de Alergênicos (ANVISA)",
            "Alerta de Alergênicos & Lactose (ANVISA)",
            "Alerta de Alergênicos & Glúten (ANVISA)",
            "Segurança Alimentar & Alergênicos (ANVISA)",
            "Orientação de Alergênicos (ANVISA)",
            "Segurança & Grau Alimentício",
            "Segurança & Certificação",
            "Segurança & Conformidade",
            "Segurança & Material",
        )
        matched_allergen_key = ""
        matched_allergen_val = ""
        for a_key in allergen_spec_keys:
            if specs_map.get(a_key):
                matched_allergen_key = a_key
                matched_allergen_val = specs_map[a_key]
                break
            if vtex_specs.get(a_key):
                matched_allergen_key = a_key
                matched_allergen_val = str(vtex_specs[a_key])
                break

        allergen_label = str(
            allergen_info.get("label")
            or matched_allergen_key
            or "Orientação de Alergênicos & Segurança (ANVISA)"
        ).strip()
        allergen_val = str(
            allergen_info.get("value")
            or allergen_info.get("alerta_alergenicos")
            or matched_allergen_val
            or "Consulte sempre a listagem oficial de ingredientes, tabela nutricional e alérgenos impressa pelo fabricante no rótulo da embalagem original."
        ).strip()
        is_anvisa_food = (
            "anvisa" in allergen_label.lower()
            or "alerg" in allergen_label.lower()
            or archetype_id in ("ld_chocolates_coberturas", "ld_confeitaria_ingredientes")
        )
        seal_kicker = "CONFORMIDADE REGULATÓRIA • RDC 26/2015" if is_anvisa_food else "CONFORMIDADE TÉCNICA • USO SEGURO"
        seal_headline = "Padrão ANVISA & Rotulagem Oficial" if is_anvisa_food else "Grau Alimentício & Atóxico Certificado"
        seal_pill = "Padrão ANVISA" if is_anvisa_food else "Grau Alimentício"

        thumb_html_act3 = ""
        if primary_img:
            thumb_html_act3 = f"""
            <div class="brk-infog-thumb brk-stage-loupe" {ml_track_attrs}>
              <img src="{primary_img}" alt="{safe_title_alt} - Inspeção de Embalagem e Lote" class="brk-infog-crop-macro" loading="lazy" referrerpolicy="no-referrer" />
              <div class="brk-ml-zoom-layer" style="background-image: url('{primary_img}');"></div>
              <span class="brk-infog-thumb-badge">Inspeção 2.4x</span>
            </div>"""

        return f"""<div class="brk-desc-media brk-media-card brk-infographic-card">
        <div class="brk-infog-header">
          <span class="brk-infog-head-left">{get_svg_icon('shield', color=theme_color, size=14)} <span>SEGURANÇA, CONSERVAÇÃO & PROCEDÊNCIA</span></span>
          <span class="brk-infog-head-pill">{seal_pill}</span>
        </div>
        <div class="brk-infog-stage">
          <div class="brk-infog-hero">{thumb_html_act3}
            <div class="brk-infog-diagram">
              <div class="brk-infog-svg-badge">
                <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M24 4L40 11V23C40 33.4 33.1 41.9 24 45C14.9 41.9 8 33.4 8 23V11L24 4Z" fill="{theme_bg}" stroke="{theme_color}" stroke-width="2.5" stroke-linejoin="round"/>
                  <path d="M17.5 24.5L22 29L31 19.5" stroke="{theme_color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="brk-infog-hero-copy">
                <span class="brk-infog-kicker">{seal_kicker}</span>
                <strong class="brk-infog-headline">{seal_headline}</strong>
                <span class="brk-infog-subline">Marca {brand_name} • Lote Original Lacrado</span>
              </div>
            </div>
          </div>
          <div class="brk-infog-metrics">
            <div class="brk-infog-metric-card brk-infog-metric-alert">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('shield', color='#b45309', size=13)}</span>
                <span class="brk-infog-metric-label">{allergen_label}</span>
              </div>
              <div class="brk-infog-metric-val">{allergen_val}</div>
            </div>
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('care', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Protocolo de Conservação & Armazenamento</span>
              </div>
              <div class="brk-infog-metric-val">{care_tips}</div>
            </div>
            <div class="brk-infog-metric-card">
              <div class="brk-infog-metric-top">
                <span class="brk-infog-metric-icon">{get_svg_icon('check', color=theme_color, size=13)}</span>
                <span class="brk-infog-metric-label">Garantia de Procedência & Integridade</span>
              </div>
              <div class="brk-infog-metric-val">Fornecido em embalagem primária original {brand_name}, lacrada de fábrica com identificação visível de lote e validade.</div>
            </div>
          </div>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">{get_svg_icon('shield', color=theme_color, size=14)} <span>Conformidade ANVISA & Protocolo de Conservação</span></span>
          <span class="brk-media-info-pill">Procedência Original</span>
        </div>
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
        is_ld_arch_care = str(archetype_id or "").startswith("ld_") or enriched_data.get("store_key") == "loja_doce"
        default_care_tips = (
            "Conservar na embalagem original fechada, em local seco, fresco e arejado, ao abrigo da luz solar direta."
            if is_ld_arch_care
            else "Lavar à mão ou em ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar)."
        )
        care_tips = enriched_data.get("care_tips") or default_care_tips

        # Trava Estrita Anti-Zíper para Linhas Fusion, Hybrid, Gola Careca e Camisas de Botão
        t_low = (formatted_title or "").lower()
        sku_low = str(enriched_data.get("sku") or enriched_data.get("master_sku") or "").lower()
        is_fusion_b = "fusion" in t_low or "fusion" in sku_low
        is_hybrid_b = "hybrid" in t_low or sku_low.startswith("hyb") or "hybrid" in sku_low
        is_anti_zipper = (
            is_fusion_b or is_hybrid_b or
            any(w in t_low for w in ["careca", "redonda", "sem zíper", "sem ziper", "casual", "t-shirt", "camiseta"]) or
            sku_low.startswith(("casual", "bp", "cm", "cadv", "cf")) or
            bool(re.match(r'^ci0(?:54|7[2-9]|8[0-4])', sku_low)) or
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
        raw_uid = str(enriched_data.get("id") or enriched_data.get("sku") or enriched_data.get("master_sku") or "brk")
        uid_base = re.sub(r"[^A-Za-z0-9]", "", raw_uid)[:16] or "brk"
        is_shirt_arch_main = archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work")
        is_ld_arch_main = str(archetype_id or "").startswith("ld_") or enriched_data.get("store_key") == "loja_doce"
        primary_ld_img = (
            (blocks[0].get("image") if len(blocks) > 0 and isinstance(blocks[0], dict) else "")
            or ((enriched_data.get("images") or [""])[0] if isinstance(enriched_data.get("images"), list) and enriched_data.get("images") else "")
            or str(enriched_data.get("image") or "")
        )
        act2_img_candidate = (blocks[1].get("image") if len(blocks) > 1 and isinstance(blocks[1], dict) else "") or ""
        ml_track_attrs = (
            'onmousemove="var r=this.getBoundingClientRect(),'
            'x=Math.max(0,Math.min(100,((event.clientX-r.left)/r.width)*100)).toFixed(2)+\'%\','
            'y=Math.max(0,Math.min(100,((event.clientY-r.top)/r.height)*100)).toFixed(2)+\'%\';'
            'var lz=this.querySelectorAll(\'.brk-ml-zoom-layer\');for(var i=0;i<lz.length;i++){lz[i].style.backgroundPosition=x+\' \'+y;}'
            'var cr=this.querySelector(\'.brk-ml-cursor\');if(cr){cr.style.left=x;cr.style.top=y;}" '
            'ontouchmove="if(event.touches&&event.touches[0]){var r=this.getBoundingClientRect(),'
            'x=Math.max(0,Math.min(100,((event.touches[0].clientX-r.left)/r.width)*100)).toFixed(2)+\'%\','
            'y=Math.max(0,Math.min(100,((event.touches[0].clientY-r.top)/r.height)*100)).toFixed(2)+\'%\';'
            'var lz=this.querySelectorAll(\'.brk-ml-zoom-layer\');for(var i=0;i<lz.length;i++){lz[i].style.backgroundPosition=x+\' \'+y;}}"'
        )

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
            # Layout de Mídia: Card Infográfico Técnico c/ Visão 360° Interativa (Ato 1) e Lupa Fluida Estilo Mercado Livre (Atos 1, 2 e 3)
            if block_split_imgs and len(block_split_imgs) >= 2:
                info_meta = self._get_media_infographic_meta(idx, archetype_id, enriched_data, is_split=True)
                media_html = f"""<div class="brk-desc-media brk-media-card">
        <div class="brk-media-stage brk-desc-media-split">
          <div class="brk-split-item brk-stage-loupe" {ml_track_attrs}>
            <img src="{block_split_imgs[0]}" alt="{safe_title_alt} - Opção 1" loading="lazy" referrerpolicy="no-referrer" />
            <div class="brk-ml-zoom-layer" style="background-image: url('{block_split_imgs[0]}');"></div>
          </div>
          <div class="brk-split-item brk-stage-loupe" {ml_track_attrs}>
            <img src="{block_split_imgs[1]}" alt="{safe_title_alt} - Opção 2" loading="lazy" referrerpolicy="no-referrer" />
            <div class="brk-ml-zoom-layer" style="background-image: url('{block_split_imgs[1]}');"></div>
          </div>
          <span class="brk-loupe-cta">Passe o mouse p/ Lupa 2.4x</span>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">{get_svg_icon(info_meta['icon'], color=theme_color, size=14)} <span>{info_meta['label']}</span></span>
          <span class="brk-media-info-pill">{info_meta['pill']}</span>
        </div>
      </div>"""
            elif img_src and idx == 0 and (is_shirt_arch_main or archetype_id == "pants_cargo_tactical") and block.get("back_360_image") and block.get("back_360_image") != img_src:
                info_meta = self._get_media_infographic_meta(idx, archetype_id, enriched_data, is_split=False)
                back_360_url = block.get("back_360_image")
                is_back_cover_360 = bool(block.get("is_back_cover_360"))
                focus_cls = " brk-focus-top" if is_shirt_arch_main else " brk-focus-center"
                if is_back_cover_360:
                    btn1_lbl = "180° Costas"
                    btn2_lbl = "0° Frente"
                else:
                    btn1_lbl = "0° Frente" if is_shirt_arch_main else "0° Vista 1"
                    btn2_lbl = "180° Costas" if is_shirt_arch_main else "180° Giro 3D"
                media_html = f"""<div class="brk-desc-media brk-media-card brk-card-360">
        <input type="radio" name="brk360_{uid_base}" id="brk360_{uid_base}_1" class="brk-360-inp brk-360-i1" checked />
        <input type="radio" name="brk360_{uid_base}" id="brk360_{uid_base}_2" class="brk-360-inp brk-360-i2" />
        <div class="brk-media-stage brk-stage-360{focus_cls}" {ml_track_attrs}>
          <div class="brk-360-rotator">
            <div class="brk-360-face brk-360-front">
              <img src="{img_src}" alt="{safe_block_alt}" loading="lazy" referrerpolicy="no-referrer" />
              <div class="brk-ml-zoom-layer" style="background-image: url('{img_src}');"></div>
            </div>
            <div class="brk-360-face brk-360-back" style="background-image: url('{back_360_url}');">
              <div class="brk-ml-zoom-layer" style="background-image: url('{back_360_url}');"></div>
            </div>
          </div>
          <span class="brk-ml-cursor"></span>
        </div>
        <div class="brk-360-controls">
          <label for="brk360_{uid_base}_1" class="brk-360-btn brk-360-b1">{btn1_lbl}</label>
          <label for="brk360_{uid_base}_2" class="brk-360-btn brk-360-b2">{btn2_lbl}</label>
          <span class="brk-360-hint">Passe o mouse p/ Lupa 2.4x</span>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">{get_svg_icon(info_meta['icon'], color=theme_color, size=14)} <span>{info_meta['label']}</span></span>
          <span class="brk-media-info-pill">{info_meta['pill']}</span>
        </div>
      </div>"""
            elif img_src:
                info_meta = self._get_media_infographic_meta(idx, archetype_id, enriched_data, is_split=False)
                is_crop_sleeve = bool(block.get("crop_sleeve_detail"))
                if is_crop_sleeve:
                    info_meta["label"] = "Detalhe Lateral: Mangas Curtas & Costura" if is_short_sleeve else "Detalhe Lateral: Mangas, Punhos & Costura"
                    info_meta["pill"] = "Pesponto Duplo"
                if idx == 2 and is_shirt_arch_main:
                    if info_meta.get("is_hand_glove_img"):
                        focus_cls = " brk-focus-center"
                    else:
                        focus_cls = " brk-focus-top brk-crop-sleeve-detail" if is_crop_sleeve else " brk-focus-top"
                elif idx == 1 and is_shirt_arch_main:
                    focus_cls = " brk-focus-mid"
                else:
                    focus_cls = " brk-focus-center"
                media_html = f"""<div class="brk-desc-media brk-media-card brk-card-loupe">
        <div class="brk-media-stage brk-stage-loupe{focus_cls}" {ml_track_attrs}>
          <img src="{img_src}" alt="{safe_block_alt}" loading="lazy" referrerpolicy="no-referrer" />
          <div class="brk-ml-zoom-layer" style="background-image: url('{img_src}');"></div>
          <span class="brk-ml-cursor"></span>
          <span class="brk-loupe-lens" style="background-image: url('{img_src}');"><span class="brk-loupe-badge">Lupa 2.4x</span></span>
          <span class="brk-loupe-cta">Passe o mouse p/ Lupa 2.4x</span>
        </div>
        <div class="brk-media-infobar">
          <span class="brk-media-info-left">{get_svg_icon(info_meta['icon'], color=theme_color, size=14)} <span>{info_meta['label']}</span></span>
          <span class="brk-media-info-pill">{info_meta['pill']}</span>
        </div>
      </div>"""
            elif is_ld_arch_main:
                media_html = self._build_lojadoce_infographic_card(
                    idx=idx,
                    archetype_id=archetype_id,
                    theme_color=theme_color,
                    theme_bg=theme_bg,
                    enriched_data=enriched_data,
                    primary_img=primary_ld_img,
                    safe_title_alt=safe_title_alt,
                    ml_track_attrs=ml_track_attrs,
                )
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
        is_ld_arch = str(archetype_id or "").startswith("ld_")
        trust_left_title = "Procedência 100% Original" if is_ld_arch else "Qualidade Oficial BRK"
        trust_left_desc = f"Curadoria Oficial • Marca {brand_name}" if is_ld_arch else "Matérias-primas nobres testadas"
        full_html = f"""{brk_tracking_marker(enriched_data.get("sku") or enriched_data.get("master_sku") or enriched_data.get("id"), archetype_id)}
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
      flex-direction: column;
      align-items: stretch;
      justify-content: center;
    }}
    .brk-media-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
      transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .brk-media-card:hover {{
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.11);
    }}
    .brk-media-stage {{
      position: relative;
      width: 100%;
      overflow: hidden;
      background: #ffffff;
      padding: 6px;
      display: block;
    }}
    .brk-desc-media img {{
      width: 100%;
      height: auto;
      max-height: 500px;
      object-fit: contain;
      border-radius: 10px;
      display: block;
      margin: 0 auto;
      background: #ffffff;
    }}
    .brk-stage-loupe.brk-crop-sleeve-detail img {{
      transform: scale(1.78);
      transform-origin: 78% 58%;
    }}
    /* Camada de Zoom Fluido Estilo Mercado Livre (Segue o Mouse sem Travar) */
    .brk-ml-zoom-layer {{
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
    }}
    .brk-stage-loupe:hover .brk-ml-zoom-layer,
    .brk-stage-360:hover .brk-360-front .brk-ml-zoom-layer {{
      opacity: 1;
    }}
    .brk-360-i2:checked ~ .brk-stage-360:hover .brk-360-front .brk-ml-zoom-layer {{
      opacity: 0;
    }}
    .brk-360-i2:checked ~ .brk-stage-360:hover .brk-360-back .brk-ml-zoom-layer {{
      opacity: 1;
    }}
    /* Visor Interativo 360 / Giro 3D no Ato 1 */
    .brk-360-inp, .brk-loupe-inp {{
      display: none !important;
    }}
    .brk-stage-360 {{
      perspective: 1100px;
      cursor: crosshair;
    }}
    .brk-360-rotator {{
      position: relative;
      width: 100%;
      transform-style: preserve-3d;
      transition: transform 0.65s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .brk-360-face {{
      position: relative;
      width: 100%;
      overflow: hidden;
      border-radius: 10px;
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }}
    .brk-360-back {{
      position: absolute;
      inset: 0;
      transform: rotateY(180deg);
      background-size: contain;
      background-position: center;
      background-repeat: no-repeat;
      background-color: #ffffff;
      border-radius: 10px;
    }}
    .brk-360-i2:checked ~ .brk-stage-360 .brk-360-rotator {{
      transform: rotateY(180deg);
    }}
    .brk-360-controls {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 8px 10px;
      background: #f1f5f9;
      border-top: 1px solid #e2e8f0;
    }}
    .brk-360-btn {{
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
    }}
    .brk-360-btn:hover {{
      border-color: {theme_color};
      color: {theme_color};
    }}
    .brk-360-i1:checked ~ .brk-360-controls .brk-360-b1,
    .brk-360-i2:checked ~ .brk-360-controls .brk-360-b2 {{
      background: {theme_color};
      color: #ffffff;
      border-color: {theme_color};
      box-shadow: 0 2px 8px {theme_color}40;
    }}
    .brk-360-hint {{
      font-size: 10px;
      font-weight: 700;
      color: #64748b;
      padding: 0 6px;
      white-space: nowrap;
    }}
    /* Cursor Guia da Lupa Dinâmica Estilo Mercado Livre */
    .brk-stage-loupe {{
      position: relative;
      cursor: crosshair;
    }}
    .brk-ml-cursor {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: 96px;
      height: 96px;
      transform: translate(-50%, -50%) scale(0.7);
      border-radius: 50%;
      border: 2px solid {theme_color};
      background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, rgba(15,23,42,0.06) 100%);
      box-shadow: 0 0 0 1px rgba(255,255,255,0.85), 0 6px 18px rgba(15,23,42,0.22);
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.18s ease, transform 0.18s ease;
      z-index: 4;
    }}
    .brk-media-stage:hover .brk-ml-cursor {{
      opacity: 1;
      transform: translate(-50%, -50%) scale(1);
    }}
    .brk-loupe-lens {{
      display: none !important;
    }}
    .brk-loupe-badge {{
      display: none !important;
    }}
    .brk-loupe-cta {{
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
    }}
    .brk-stage-loupe:hover .brk-loupe-cta,
    .brk-media-stage:hover .brk-loupe-cta {{
      opacity: 0;
    }}
    .brk-media-infobar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 14px;
      background: #f8fafc;
      border-top: 1px solid #e2e8f0;
      font-size: 11.5px;
    }}
    .brk-media-info-left {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      font-weight: 700;
      color: #1e293b;
      min-width: 0;
      line-height: 1.25;
    }}
    .brk-media-info-left span {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .brk-media-info-pill {{
      flex-shrink: 0;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: {theme_color};
      background: {theme_bg};
      border: 1px solid {theme_color}30;
      padding: 3px 9px;
      border-radius: 9999px;
    }}

    /* Midia Dividida para Iscas / Variacoes (Split Media) */
    .brk-desc-media-split {{
      display: flex;
      gap: 10px;
      padding: 10px;
    }}
    .brk-desc-media-split .brk-split-item {{
      flex: 1;
      min-width: 0;
    }}
    .brk-desc-media-split .brk-split-item img {{
      max-height: 380px;
    }}

    /* Card Visual Infográfico Autônomo (Rendimento, Medidas & Segurança ANVISA) */
    .brk-infographic-card {{
      display: flex;
      flex-direction: column;
      background: #ffffff;
    }}
    .brk-infog-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 10px 14px;
      background: {theme_bg};
      border-bottom: 1px solid {theme_color}28;
    }}
    .brk-infog-head-left {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      font-size: 10.5px;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: #0f172a;
      min-width: 0;
    }}
    .brk-infog-head-left span {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .brk-infog-head-pill {{
      flex-shrink: 0;
      font-size: 10px;
      font-weight: 800;
      color: {theme_color};
      background: #ffffff;
      border: 1px solid {theme_color}38;
      padding: 2px 8px;
      border-radius: 9999px;
      text-transform: uppercase;
    }}
    .brk-infog-stage {{
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }}
    .brk-infog-hero {{
      display: flex;
      align-items: stretch;
      gap: 12px;
    }}
    .brk-infog-thumb {{
      position: relative;
      width: 112px;
      min-height: 104px;
      flex-shrink: 0;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      overflow: hidden;
      background: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 4px;
    }}
    .brk-infog-thumb img {{
      width: 100%;
      height: 96px;
      object-fit: contain;
      border-radius: 8px;
      transition: transform 0.3s ease;
    }}
    .brk-infog-thumb img.brk-infog-crop-zoom {{
      transform: scale(1.22);
      transform-origin: 50% 45%;
    }}
    .brk-infog-thumb img.brk-infog-crop-macro {{
      transform: scale(1.28);
      transform-origin: 50% 60%;
    }}
    .brk-infog-thumb-badge {{
      position: absolute;
      bottom: 5px;
      right: 5px;
      z-index: 3;
      background: rgba(15, 23, 42, 0.82);
      color: #ffffff;
      font-size: 9px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 9999px;
      pointer-events: none;
    }}
    .brk-infog-diagram {{
      flex: 1;
      min-width: 0;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 10px 12px;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    }}
    .brk-infog-svg-badge {{
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: {theme_bg};
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .brk-infog-hero-copy {{
      display: flex;
      flex-direction: column;
      min-width: 0;
      gap: 2px;
    }}
    .brk-infog-kicker {{
      font-size: 9.5px;
      font-weight: 800;
      letter-spacing: 0.6px;
      text-transform: uppercase;
      color: {theme_color};
    }}
    .brk-infog-headline {{
      font-size: 13px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.25;
    }}
    .brk-infog-subline {{
      font-size: 11px;
      color: #64748b;
      line-height: 1.25;
    }}
    .brk-infog-metrics {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .brk-infog-metric-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-left: 3px solid {theme_color};
      border-radius: 10px;
      padding: 9px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .brk-infog-metric-card.brk-infog-metric-alert {{
      background: #fffbeb;
      border-color: #fde68a;
      border-left: 3px solid #d97706;
    }}
    .brk-infog-metric-top {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .brk-infog-metric-icon {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .brk-infog-metric-label {{
      font-size: 10.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      color: #334155;
    }}
    .brk-infog-metric-card.brk-infog-metric-alert .brk-infog-metric-label {{
      color: #92400e;
    }}
    .brk-infog-metric-val {{
      font-size: 12px;
      line-height: 1.45;
      color: #1e293b;
      font-weight: 600;
    }}
    .brk-infog-metric-card.brk-infog-metric-alert .brk-infog-metric-val {{
      color: #78350f;
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
      grid-template-columns: repeat(2, 1fr);
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
      .brk-infog-hero {{
        flex-direction: column;
        gap: 8px;
      }}
      .brk-infog-thumb {{
        width: 100%;
        min-height: 120px;
      }}
      .brk-infog-thumb img {{
        height: 110px;
      }}
      .brk-media-infobar {{
        padding: 8px 10px;
        font-size: 10.5px;
      }}
      .brk-media-info-pill {{
        font-size: 9px;
        padding: 2px 7px;
      }}
      .brk-loupe-lens {{
        width: 90px;
        height: 90px;
        right: 10px;
        bottom: 38px;
      }}
      .brk-360-btn {{
        font-size: 10px;
        padding: 5px 6px;
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
        <div class="brk-trust-title">{trust_left_title}</div>
        <div class="brk-trust-desc">{trust_left_desc}</div>
      </div>
    </div>
    <div class="brk-trust-item">
      <span class="brk-trust-svg">{get_svg_icon('truck', color=theme_color, size=24)}</span>
      <div>
        <div class="brk-trust-title">Envio Rápido & Seguro</div>
        <div class="brk-trust-desc">Rastreamento de ponta a ponta</div>
      </div>
    </div>
  </div>

{copyright_html}

</div>

{schema_json_ld}
"""
        if is_ld_arch or enriched_data.get("store_key") == "loja_doce":
            full_html = full_html.replace(
                "<!-- BRK GROUP - DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL SHOPIFY) -->",
                "<!-- DESCRICAO VERTICALIZADA EM 3 ATOS (PADRAO OFICIAL VTEX) -->",
            )
            full_html = full_html.replace(
                "/* Rodapé de Confiança e Garantia BRK */",
                "/* Rodapé de Confiança e Procedência Oficial */",
            )
            full_html = full_html.replace(
                "<!-- Selos de Confiança e Garantia BRK -->",
                "<!-- Selos de Confiança e Procedência Oficial -->",
            )
            full_html = re.sub(
                r"\s*\.brk-desc-block\.brk-desc-block-text-only\s*\{[^}]*\}",
                "",
                full_html,
            )
            full_html = full_html.replace("brk-", "vtex-").replace("brk360_", "vtex360_")
        return full_html.strip()

    def build_shopify_markdown(self, enriched_data: Dict[str, Any]) -> str:
        """
        Compila a descrição em Markdown limpo, sem tags HTML externas e sem Font Awesome.
        """
        is_ld_md = str(enriched_data.get("archetype_id") or "").startswith("ld_") or enriched_data.get("store_key") == "loja_doce"
        formatted_title = enriched_data.get("formatted_title") or enriched_data.get("title", "Produto Oficial" if is_ld_md else "Produto BRK")
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
        default_md_care = (
            "Conservar na embalagem original fechada, em local seco, fresco e arejado, ao abrigo da luz solar direta."
            if is_ld_md
            else "Lavar à mão ou em ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar)."
        )
        care_tips = enriched_data.get("care_tips") or default_md_care

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
        if is_kids and not is_ld_md:
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
        elif not is_ld_md and (archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work") or any(w in title_low for w in ["camisa", "camiseta", "jersey", "baby look"])):
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
        elif not is_ld_md and (archetype_id in ("pants_cargo_tactical", "overalls_workwear") or any(w in title_low for w in ["calça", "calca", "bermuda", "shorts"])):
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
        elif not is_ld_md and (archetype_id in ("footwear_sandals_boaonda", "closed_footwear_sneakers") or any(w in title_low for w in ["sandália", "sandalia", "babuche", "chinelo"])):
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
        if is_ld_md:
            b_md = enriched_data.get("brand_name") or "Linha Oficial"
            if str(b_md).upper() in ("BRK", "LOJA DOCE", "LOJA DOCE IMPORT"):
                b_md = "Linha Oficial"
            md_parts.append(f"- 🛡️ **Procedência 100% Original:** Curadoria Oficial • Marca {b_md}")
        else:
            md_parts.append("- 🛡️ **Qualidade Oficial BRK:** Matérias-primas nobres testadas")
        md_parts.append("- 🚚 **Envio Rápido & Seguro:** Rastreamento de ponta a ponta")

        if show_copyright and not is_ld_md:
            md_parts.append("\n> **Aviso de Propriedade Intelectual:** Nossas estampas são protegidas pela Lei de Direitos Autorais (Lei 9.610/98) a Reprodução não autorizada está sujeita às penalidades legais. Copiar é crime !\n")

        return "\n".join(md_parts).strip()
