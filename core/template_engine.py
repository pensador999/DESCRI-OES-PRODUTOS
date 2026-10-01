"""
Motor de Moldes Mestres e Extração de Especificações Técnicas (Pilar 2).
Mapeia os melhores padrões de descrições para 5 arquétipos:
1. UV50+ Performance (Pesca / Proteção Solar)
2. Agro & Campo (Resistência na lida / Algodão & Conforto)
3. Motors & Trilha (Jerseys Off-road / Velocidade / Respirabilidade)
4. Bonés & Acessórios (Trucker / Snapback / Ajuste / Alta definição)
5. Cutelaria & Peças Únicas (Facas artesanais / Retenção de fio / Exclusividade)

Preserva rigorosamente 100% dos dados técnicos reais da peça sem alucinar especificações.
"""

import re
from typing import Dict, Any, List

class TemplateEngine:
    def __init__(self):
        self.templates = {
            "uv_performance": {
                "id": "uv_performance",
                "name": "UV50+ Performance & Pesca",
                "fa_icon": "fa-solid fa-fish",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["camisa", "pesca", "uv", "manga longa", "dry", "solar", "fishing"],
                "default_tagline": "Máxima Proteção Solar e Respirabilidade Ativa no Ar Livre",
                "act1": {
                    "tag": "Design & Identidade",
                    "fa_icon": "fa-solid fa-palette",
                    "title": "ESTAMPA EM ALTA DEFINIÇÃO E MODELAGEM ANATÔMICA",
                    "desc_tmpl": "Desenvolvida para pescadores e entusiastas do ar livre, a {title} combina visual marcante com corte que proporciona liberdade total de movimentos durante os arremessos e manobras."
                },
                "act2": {
                    "tag": "Performance & Conforto",
                    "fa_icon": "fa-solid fa-sun",
                    "title": "PROTEÇÃO SOLAR UV50+ COM SECAGEM ULTRA RÁPIDA",
                    "desc_tmpl": "Confeccionada em tecido tecnológico de absorção instantânea de suor, bloqueia até 98% dos raios UVA e UVB, mantendo a sensação de frescor e conforto térmico mesmo sob sol intenso o dia todo."
                },
                "act3": {
                    "tag": "Durabilidade & Detalhes",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "COSTURA REFORÇADA E ZÍPER COM TRAVA DE SEGURANÇA",
                    "desc_tmpl": "Acabamento de alto padrão com costuras planas anti-atrito, gola padre com cobertura no cursor do zíper e punhos anatômicos que não laceiam com o uso frequente."
                },
                "base_specs": [
                    {"label": "Proteção Solar", "default": "Fator FPU 50+ permanente certificado"},
                    {"label": "Composição", "default": "100% Poliéster Tecnológico Dry Fit"},
                    {"label": "Modelagem", "default": "Conforto com mangas raglan esportivas"},
                    {"label": "Gola e Zíper", "default": "Gola alta anatômica com zíper frontal e trava"},
                    {"label": "Secagem", "default": "Secagem ultra rápida (Quick Dry)"},
                    {"label": "Cuidados", "default": "Lavar à mão ou máquina no ciclo delicado, dispensando ferro"}
                ],
                "care_tips": "Lavar à mão ou em máquina no ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar)."
            },
            "agro_field": {
                "id": "agro_field",
                "name": "Força, Campo & Tradição",
                "fa_icon": "fa-solid fa-tractor",
                "theme_color": "#15803d",
                "theme_bg": "#f0fdf4",
                "category_keywords": ["agro", "campo", "rural", "camiseta", "fazenda", "trator", "algodao"],
                "default_tagline": "Resistência para o Campo e Estilo Autêntico para Qualquer Momento",
                "act1": {
                    "tag": "Origem & Estilo",
                    "fa_icon": "fa-solid fa-wheat-awn",
                    "title": "ORGULHO RURAL COM VISUAL CONTEMPORÂNEO",
                    "desc_tmpl": "A {title} celebra a identidade do homem e da mulher do campo com estampas exclusivas de alta durabilidade e caimento equilibrado para todas as ocasiões."
                },
                "act2": {
                    "tag": "Conforto Térmico",
                    "fa_icon": "fa-solid fa-seedling",
                    "title": "TOQUE MACIO E RESPIRAÇÃO NATURAL DO TECIDO",
                    "desc_tmpl": "Produzida com matéria-prima selecionada que garante sensação agradável sobre a pele, excelente respirabilidade e resistência ideal para enfrentar longas jornadas com conforto."
                },
                "act3": {
                    "tag": "Resistência & Acabamento",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "GOLA COM REFORÇO OMBRO A OMBRO E COSTURA DUPLA",
                    "desc_tmpl": "Estrutura robusta desenvolvida para manter a forma e a cor vivas mesmo após sucessivas lavagens, sem deformar ou desbotar."
                },
                "base_specs": [
                    {"label": "Composição", "default": "Algodão Premium com toque aveludado"},
                    {"label": "Gola", "default": "Gola redonda com reforço canelado e fita ombro a ombro"},
                    {"label": "Costura", "default": "Pesponto duplo reforçado nas barras e mangas"},
                    {"label": "Toque", "default": "Macio, anti-pilling (não cria bolinhas)"},
                    {"label": "Uso Recomendado", "default": "Trabalho rural, eventos do agronegócio e dia a dia"}
                ],
                "care_tips": "Lavar com cores semelhantes. Não alvejar. Secar ao ar livre e passar em temperatura média pelo avesso para preservar a estampa intacta."
            },
            "motors_speed": {
                "id": "motors_speed",
                "name": "Trilha, Velocidade & Off-Road",
                "fa_icon": "fa-solid fa-motorcycle",
                "theme_color": "#e11d48",
                "theme_bg": "#fff1f2",
                "category_keywords": ["jersey", "moto", "cross", "off-road", "trilha", "speed", "velocidade"],
                "default_tagline": "Aerodinâmica e Ventilação Máxima para Trilhas e Pistas",
                "act1": {
                    "tag": "Visual & Identidade",
                    "fa_icon": "fa-solid fa-gauge-high",
                    "title": "GRAFISMOS VIBRANTES SUBLIMADOS DE ALTA RESOLUÇÃO",
                    "desc_tmpl": "Projetada para os apaixonados por adrenalina e velocidade, a {title} se destaca pelas cores vivas e identidade forte nas pistas e trilhas."
                },
                "act2": {
                    "tag": "Ventilação & Aerodinâmica",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "TECIDO MICROPERFURADO COM TROCA TÉRMICA CONTÍNUA",
                    "desc_tmpl": "Painéis estratégicos que aceleram o fluxo de ar, permitindo usar protetores e coletes sem acúmulo excessivo de calor ou peso de umidade."
                },
                "act3": {
                    "tag": "Resistência a Impactos",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "CORTE TRASEIRO ALONGADO E PUNHOS ELÁSTICOS",
                    "desc_tmpl": "A modelagem mais longa na parte traseira impede que a peça saia de dentro da calça durante a pilotagem severa, proporcionando ajuste firme e seguro."
                },
                "base_specs": [
                    {"label": "Tecido", "default": "Poliéster esportivo ventilado de alta tenacidade"},
                    {"label": "Corte Traseiro", "default": "Cauda alongada tipo Drop-tail para melhor encaixe na calça"},
                    {"label": "Punhos", "default": "Elásticos de compressão suave que não prendem a circulação"},
                    {"label": "Sublimação", "default": "Cores ultra pigmentadas que não desbotam com lama e sol"}
                ],
                "care_tips": "Após a trilha ou pista, remover o excesso de barro com água antes da lavagem. Não lavar a seco nem utilizar ferro sobre as áreas sublimadas."
            },
            "caps_accessories": {
                "id": "caps_accessories",
                "name": "Bonés, Chapéus & Acessórios",
                "fa_icon": "fa-solid fa-hat-cowboy-side",
                "theme_color": "#d97706",
                "theme_bg": "#fffbeb",
                "category_keywords": ["bone", "chapeu", "trucker", "snapback", "bandana", "faixa", "copa"],
                "default_tagline": "Design Anatômico, Estrutura Firme e Ventilação",
                "act1": {
                    "tag": "Estrutura & Copa",
                    "fa_icon": "fa-solid fa-hat-cowboy-side",
                    "title": "COPA ESTRUTURADA COM BORDADO DE ALTA PRECISÃO",
                    "desc_tmpl": "O {title} destaca-se pela frente firme e acabamento impecável, mantendo o formato clássico intacto em qualquer situação."
                },
                "act2": {
                    "tag": "Ventilação & Conforto",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "TELA RESPIRÁVEL E CARNEIRA INTERNA ACOLCHOADA",
                    "desc_tmpl": "Garante circulação constante de ar para evitar suor excessivo na cabeça, aliado à carneira interna macia para uso contínuo o dia todo."
                },
                "act3": {
                    "tag": "Ajuste Personalizado",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "FECHO REGULÁVEL DE ALTA DURABILIDADE",
                    "desc_tmpl": "Ajuste sob medida para diferentes circunferências cranianas, com pinos ou fecho de engate seguro e aba com curvatura milimétrica."
                },
                "base_specs": [
                    {"label": "Modelo", "default": "Trucker com lateral e traseira telada respirável"},
                    {"label": "Aba", "default": "Curva com 6 costuras de sustentação"},
                    {"label": "Fechamento", "default": "Snapback regulável em polímero virgem"},
                    {"label": "Bordado / Aplique", "default": "Bordado em alto relevo com linha especial"},
                    {"label": "Tamanho", "default": "Único ajustável (54 a 60 cm de circunferência)"}
                ],
                "care_tips": "Limpar com pano úmido e sabão neutro. Não mergulhar a copa em água nem lavar em máquina para manter a estrutura e a curvatura da aba perfeitas."
            },
            "cutlery_unique": {
                "id": "cutlery_unique",
                "name": "Cutelaria & Peças Artesanais",
                "fa_icon": "fa-solid fa-utensils",
                "theme_color": "#475569",
                "theme_bg": "#f8fafc",
                "category_keywords": ["faca", "cutelaria", "lamina", "bainha", "churrasco", "artesanal", "aco"],
                "default_tagline": "Forja Artesanal, Retenção Excepcional de Fio e Nobreza",
                "act1": {
                    "tag": "Lâmina & Geometria",
                    "fa_icon": "fa-solid fa-utensils",
                    "title": "AÇO TRATADO TERMICAMENTE PARA FIO NAVALHA",
                    "desc_tmpl": "Construída com precisão cirúrgica, a {title} oferece equilíbrio de peso ideal, proporcionando cortes limpos e suaves sem esforço."
                },
                "act2": {
                    "tag": "Empunhadura Nobre",
                    "fa_icon": "fa-solid fa-gem",
                    "title": "CABO ANATÔMICO EM MADEIRA NOBRE OU MATERIAL PREMIUM",
                    "desc_tmpl": "Proporciona pegada firme e confortável até mesmo com mãos molhadas ou engorduradas, valorizando a exclusividade dos veios da matéria-prima."
                },
                "act3": {
                    "tag": "Bainha & Proteção",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "ACOMPANHA BAINHA FEITA SOB MEDIDA",
                    "desc_tmpl": "Proteção segura para transporte e conservação da lâmina, costurada com linha grossa e travamento firme."
                },
                "base_specs": [
                    {"label": "Material da Lâmina", "default": "Aço Especial com têmpera integral de alta dureza"},
                    {"label": "Empunhadura", "default": "Anatômica com pinos de fixação em latão/inox"},
                    {"label": "Fio de Corte", "default": "Geometria Razor com polimento espelhado"},
                    {"label": "Acompanhamento", "default": "Bainha reforçada com passador para cinto"}
                ],
                "care_tips": "Lavar com água e esponja macia logo após o uso. Secar imediatamente para evitar oxidação. Aplicar leve camada de óleo mineral na lâmina periodicamente."
            },
            "footwear_sandals": {
                "id": "footwear_sandals",
                "name": "Calçados & Sandálias",
                "fa_icon": "fa-solid fa-shoe-prints",
                "theme_color": "#0d9488",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["sandalia", "sandália", "chinelo", "pantufa", "bota", "boaonda", "tenis", "tênis", "sapato", "crocs"],
                "default_tagline": "Conforto Anatômico e Solado Antiderrapante para Uso em Embarcações e Lazer",
                "act1": {
                    "tag": "Conforto & Ergonomia",
                    "fa_icon": "fa-solid fa-shoe-prints",
                    "title": "DESIGN ANATÔMICO COM PALMILHA ANTI-IMPACTO",
                    "desc_tmpl": "Desenvolvida para proporcionar amortecimento suave e alívio de pressão na pisada, a {title} garante descanso aos pés durante longos períodos em pé na pescaria ou no dia a dia."
                },
                "act2": {
                    "tag": "Aderência & Drenagem",
                    "fa_icon": "fa-solid fa-water",
                    "title": "SOLADO ANTIDERRAPANTE COM DRENAGEM RÁPIDA",
                    "desc_tmpl": "Possui frisos e canais de escoamento especialmente projetados para pisos molhados, decks de barcos e bordas de piscina, oferecendo tração segura e passos firmes."
                },
                "act3": {
                    "tag": "Durabilidade & Higiene",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "MATERIAL ANTIMICROBIANO E SECAGEM INSTANTÂNEA",
                    "desc_tmpl": "Confeccionada em polímero nobre impermeável que não absorve umidade nem odores, sendo extremamente fácil de lavar e secar rapidamente para o próximo uso."
                },
                "base_specs": [
                    {"label": "Material do Cabedal", "default": "EVA Termomoldado macio e flexível"},
                    {"label": "Solado", "default": "Borracha antiderrapante com ranhuras de tração e escoamento"},
                    {"label": "Palmilha", "default": "Anatômica com amortecimento anti-impacto"},
                    {"label": "Resistência", "default": "100% à prova d'água, secagem instantânea"},
                    {"label": "Uso Recomendado", "default": "Embarcações, pesqueiros, praia, piscina e uso casual"}
                ],
                "care_tips": "Lavar com água corrente e sabão neutro. Não expor ao sol excessivo direto para evitar deformação do EVA."
            },
            "tackle_boxes_storage": {
                "id": "tackle_boxes_storage",
                "name": "Caixas, Estojos & Organização",
                "fa_icon": "fa-solid fa-box-archive",
                "theme_color": "#1d4ed8",
                "theme_bg": "#eff6ff",
                "category_keywords": ["caixa", "estojo", "maleta", "organizador", "bolsa", "mochila", "tubo", "porta-vara", "case", "tralha"],
                "default_tagline": "Estrutura Reforçada e Compartimentação Inteligente para sua Tralha",
                "act1": {
                    "tag": "Organização & Espaço",
                    "fa_icon": "fa-solid fa-box-archive",
                    "title": "DIVISÓRIAS MODULARES E COMPARTIMENTAÇÃO INTELIGENTE",
                    "desc_tmpl": "Projetada para acomodar iscas, anzóis, chumbadas e equipamentos com total organização, a {title} permite ajustar o espaço interno de acordo com a sua necessidade."
                },
                "act2": {
                    "tag": "Segurança & Travamento",
                    "fa_icon": "fa-solid fa-lock",
                    "title": "TRAVAS DUPLAS REFORÇADAS ANTI-ABERTURA",
                    "desc_tmpl": "Equipada com fechos de alta pressão que garantem travamento firme e seguro, impedindo aberturas acidentais mesmo durante impactos e movimentação intensa na embarcação."
                },
                "act3": {
                    "tag": "Proteção & Durabilidade",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "POLÍMERO VIRGEM DE ALTA RESISTÊNCIA COM PROTEÇÃO UV",
                    "desc_tmpl": "Construção robusta resistente a quedas, choques mecânicos e à degradação solar, preservando suas tralhas protegidas da água e do sol por muito mais tempo."
                },
                "base_specs": [
                    {"label": "Material", "default": "Polipropileno virgem de alto impacto com proteção UV"},
                    {"label": "Divisórias", "default": "Removíveis e reposicionáveis sob medida"},
                    {"label": "Travas", "default": "Sistema duplo reforçado de alta pressão"},
                    {"label": "Vedação", "default": "Resistente a respingos d'água e poeira"},
                    {"label": "Aplicação", "default": "Organização de tralhas em barcos, caiaques, pesqueiros e camping"}
                ],
                "care_tips": "Lavar periodicamente com água doce após uso em ambiente salino e secar antes de fechar."
            },
            "fishing_tackle_gear": {
                "id": "fishing_tackle_gear",
                "name": "Equipamentos de Pesca & Revenda",
                "fa_icon": "fa-solid fa-gear",
                "theme_color": "#4338ca",
                "theme_bg": "#eef2ff",
                "category_keywords": ["vara", "carretilha", "molinete", "isca", "linha", "anzol", "alicate", "passagua", "passaguá", "girador", "snap", "chumbada", "boia", "marine sports", "shimano", "daiwa", "albatroz", "rapala", "nakamura", "yara", "maruri"],
                "default_tagline": "Engenharia de Precisão e Alta Performance para Pesca Esportiva",
                "act1": {
                    "tag": "Engenharia & Precisão",
                    "fa_icon": "fa-solid fa-gear",
                    "title": "MECÂNICA BALANCEADA PARA ALTO DESEMPENHO",
                    "desc_tmpl": "Construído com componentes de engenharia refinada, o(a) {title} oferece arremessos precisos, sensibilidade máxima no trabalho da isca e funcionamento suave."
                },
                "act2": {
                    "tag": "Força & Controle",
                    "fa_icon": "fa-solid fa-hand-fist",
                    "title": "RESISTÊNCIA SOB TRAÇÃO E CONTROLE PROGRESSIVO",
                    "desc_tmpl": "Projetado para suportar esforço extremo nas brigas com grandes exemplares, mantendo tração firme e confiabilidade absoluta na linha."
                },
                "act3": {
                    "tag": "Durabilidade & Acabamento",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "COMPONENTES TRATADOS CONTRA CORROSÃO",
                    "desc_tmpl": "Materiais selecionados de alta dureza com revestimento resistente à água doce e salinidade, garantindo longa vida útil e preservação dos mecanismos."
                },
                "base_specs": [
                    {"label": "Categoria", "default": "Equipamento de Precisão para Pesca Esportiva"},
                    {"label": "Estrutura", "default": "Liga reforçada de baixo peso e alta rigidez estrutural"},
                    {"label": "Mecânica", "default": "Componentes de precisão com rolamentos selados"},
                    {"label": "Aplicação", "default": "Pesca esportiva em rios, lagos, pesqueiros e mar aberto"},
                    {"label": "Origem / Distribuição", "default": "Produto original com procedência e garantia"}
                ],
                "care_tips": "Após uso em água salgada, lavar levemente com água doce corrente, secar e aplicar óleo lubrificante nos pontos móveis recomendados."
            },
            "thermal_gear": {
                "id": "thermal_gear",
                "name": "Térmicos, Camping & Hidratação",
                "fa_icon": "fa-solid fa-snowflake",
                "theme_color": "#0891b2",
                "theme_bg": "#ecfeff",
                "category_keywords": ["copo", "garrafa", "cooler", "termico", "térmico", "elber", "geladeira", "cantil", "caneca"],
                "default_tagline": "Retenção Térmica Eficiente e Construção Robusta para o Ar Livre",
                "act1": {
                    "tag": "Isolamento Térmico",
                    "fa_icon": "fa-solid fa-snowflake",
                    "title": "RETENÇÃO TÉRMICA PROLONGADA SOB CALOR EXTREMO",
                    "desc_tmpl": "Desenvolvido para manter suas bebidas ou alimentos na temperatura ideal por muito mais tempo, o(a) {title} é essencial para suas pescarias e acampamentos."
                },
                "act2": {
                    "tag": "Construção & Vedação",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "PAREDES REFORÇADAS E VEDAÇÃO HERMÉTICA",
                    "desc_tmpl": "Estrutura robusta à prova de vazamentos com isolamento de alta densidade que não transpira externamente e resiste ao transporte em estradas e barcos."
                },
                "act3": {
                    "tag": "Praticidade & Higiene",
                    "fa_icon": "fa-solid fa-droplet",
                    "title": "FÁCIL HIGIENIZAÇÃO E MATERIAIS LIVRES DE BPA",
                    "desc_tmpl": "Superfície interna lisa que não retém odores nem sabores, fácil de limpar e pronta para acompanhar qualquer jornada."
                },
                "base_specs": [
                    {"label": "Material", "default": "Aço Inox 18/8 / Polímero de alta densidade livre de BPA"},
                    {"label": "Isolamento", "default": "Parede dupla com isolamento a vácuo / PU injetado"},
                    {"label": "Vedação", "default": "Hermética à prova de vazamentos acidentais"},
                    {"label": "Uso Recomendado", "default": "Pesca embarcada, camping, viagens, trabalho rural e dia a dia"}
                ],
                "care_tips": "Lavar com água e sabão neutro. Não utilizar esponjas de aço ou abrasivos na parte externa."
            }
        }

    def detect_archetype(self, title: str, category: str = "", tags: List[str] = None, vendor: str = "") -> str:
        """
        Detecta com rigor o arquétipo correto do produto, evitando que calçados,
        caixas, equipamentos de revenda ou térmicos caiam em vestuário/camisas.
        """
        text = f"{title} {category} {vendor} {' '.join(tags or [])}".lower()
        
        # 1. Calçados & Sandálias (Prioridade Máxima)
        if any(w in text for w in ["sandalia", "sandália", "chinelo", "pantufa", "boaonda", "calcado", "calçado", "bota", "tenis", "tênis", "crocs", "papete"]):
            return "footwear_sandals"
            
        # 2. Caixas, Estojos & Organização de Tralha
        if any(w in text for w in ["caixa de pesca", "caixa pesca", "estojo", "maleta", "organizador", "porta-vara", "porta vara", "tubo de vara", "case pesca", "bolsa de pesca"]) or (any(w in text for w in ["caixa", "estojo", "maleta"]) and not any(w in text for w in ["camisa", "camiseta", "termica", "térmica"])):
            return "tackle_boxes_storage"
            
        # 3. Térmicos & Geladeiras Portáteis
        if any(w in text for w in ["copo termico", "copo térmico", "garrafa termica", "garrafa térmica", "cooler", "geladeira", "caixa termica", "caixa térmica", "elber", "cantil"]):
            return "thermal_gear"

        # 4. Equipamentos de Pesca & Revenda de Marcas Parceiras
        gear_keywords = ["vara de pesca", "vara para", "carretilha", "molinete", "isca artificial", "isca de pesca", "anzol", "alicate de bico", "alicate de contenção", "passagua", "passaguá", "linha multifilamento", "linha monofilamento", "girador", "snap", "chumbada", "boia cevadeira", "boia de pesca"]
        resale_vendors = ["marine sports", "shimano", "daiwa", "deyu", "albatroz", "rapala", "lucky nelson nakamura", "maruri", "yara", "sumax"]
        if any(w in text for w in gear_keywords) or any(v in text for v in resale_vendors) or any(w in text for w in ["vara", "carretilha", "molinete", "isca"]) and not any(w in text for w in ["camisa", "camiseta", "bone", "boné"]):
            return "fishing_tackle_gear"

        # 5. Cutelaria & Facas
        if any(w in text for w in ["faca", "cutelaria", "lamina", "lâmina", "bainha", "churrasco", "canivete"]):
            return "cutlery_unique"

        # 6. Bonés, Chapéus & Acessórios de Cabeça
        if any(w in text for w in ["bone", "boné", "chapeu", "chapéu", "trucker", "snapback", "bandana", "balaclava", "viseira"]):
            return "caps_accessories"

        # 7. Motors & Velocidade
        if any(w in text for w in ["jersey", "moto", "motociclismo", "cross", "motocross", "off-road", "velocidade", "trail", "expedição", "expedicao", "atacama", "ushuaia", "motors"]):
            return "motors_speed"

        # 8. Agro & Campo
        if any(w in text for w in ["agro", "campo", "rural", "soja", "milho", "trator", "gado", "fazenda"]):
            return "agro_field"

        # 9. Padrão: UV Performance / Camisas de Pesca
        return "uv_performance"

    def extract_product_specs(self, product: Dict[str, Any], archetype_id: str) -> List[Dict[str, str]]:
        """
        Extrai dados reais do produto (título, tags, vendor e body_html anterior) para preencher a tabela técnica sem alucinações.
        """
        template = self.templates.get(archetype_id, self.templates["uv_performance"])
        base_specs = template["base_specs"]
        
        title = product.get("title", "")
        vendor = product.get("vendor", "")
        body = product.get("body_html", "") or ""
        tags = product.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        
        full_text = f"{title} {vendor} {body} {' '.join(tags)}".lower()

        extracted = []
        for spec in base_specs:
            label = spec["label"]
            val = spec["default"]
            
            # Se for equipamento de revenda, injetar Vendor real
            if label == "Origem / Distribuição" and vendor:
                val = f"Produto Original {vendor} com garantia oficial"
            elif label == "Categoria" and vendor:
                val = f"Equipamento de Precisão {vendor}"
            elif label == "Material do Cabedal" and "boaonda" in full_text:
                val = "Termoplástico nobre Boaonda flexível e lavável"

            # 1. Proteção Solar (apenas para roupas e bonés)
            if "proteção" in label.lower() or "solar" in label.lower():
                if "50+" in full_text or "uv 50" in full_text or "fps 50" in full_text or "fpu 50" in full_text:
                    val = "Fator FPU 50+ permanente certificado"
                elif "uv" in full_text:
                    val = "Proteção UV integrada ao tecido"
            
            # 2. Composição / Tecido (apenas roupas)
            elif "composição" in label.lower() or "tecido" in label.lower():
                if "dry fit" in full_text or "dryfit" in full_text or "dry" in full_text:
                    val = "100% Poliéster Tecnológico Dry Fit respirável"
                elif "algodão" in full_text or "algodao" in full_text:
                    val = "100% Algodão Premium Penteado 30.1 com toque macio"

            # 3. Zíper
            elif "zíper" in label.lower() or "ziper" in label.lower():
                if "ykk" in full_text:
                    val = "Zíper reforçado YKK com trava emborrachada"
                elif "sem zíper" in full_text or "careca" in full_text:
                    val = "Gola careca com acabamento reforçado"

            extracted.append({"label": label, "value": val})

        return extracted
    def generate_narrative_from_template(self, product: Dict[str, Any], archetype_id: str, cdn_images: List[str], store_key: str = None) -> Dict[str, Any]:
        """
        Gera os 3 blocos narrativos e especificações prontos para o HTMLBuilder.
        Garante que a paleta suave de cores siga rigorosamente a identidade da loja:
        - BRK Fishing: Azul Leve (#0284c7 / #f0f9ff)
        - BRK Agro: Verde Leve (#16a34a / #f0fdf4)
        - BRK Motors: Laranja Leve (#f97316 / #fff7ed)
        """
        template = self.templates.get(archetype_id, self.templates["uv_performance"])
        title = product.get("title", "Produto BRK")
        
        # Paleta Cromática Suave por Loja
        store_palettes = {
            "brk_fishing": {"color": "#0284c7", "bg": "#f0f9ff"}, # Azul Leve
            "brk_agro":    {"color": "#16a34a", "bg": "#f0fdf4"}, # Verde Leve
            "brk_motors":  {"color": "#f97316", "bg": "#fff7ed"}, # Laranja Leve
        }
        
        if not store_key:
            url = (product.get("url") or "").lower()
            vendor = (product.get("vendor") or "").lower()
            category = (product.get("category") or "").lower()
            if "agro" in url or "agro" in vendor or "agro" in category or archetype_id == "agro_field":
                store_key = "brk_agro"
            elif "motors" in url or "motors" in vendor or "motors" in category or archetype_id == "motors_speed":
                store_key = "brk_motors"
            else:
                store_key = "brk_fishing"

        theme_color = store_palettes.get(store_key, {}).get("color", template.get("theme_color", "#0284c7"))
        theme_bg = store_palettes.get(store_key, {}).get("bg", template.get("theme_bg", "#f0f9ff"))

        # Determinar ícone de cuidados apropriado ao arquétipo
        care_icons = {
            "footwear_sandals": "fa-solid fa-shoe-prints",
            "tackle_boxes_storage": "fa-solid fa-box-archive",
            "fishing_tackle_gear": "fa-solid fa-screwdriver-wrench",
            "thermal_gear": "fa-solid fa-snowflake",
            "cutlery_unique": "fa-solid fa-utensils",
            "caps_accessories": "fa-solid fa-hat-cowboy",
            "motors_speed": "fa-solid fa-shield-halved",
            "agro_field": "fa-solid fa-seedling",
            "uv_performance": "fa-solid fa-shirt"
        }
        care_icon = care_icons.get(archetype_id, "fa-solid fa-hand-sparkles")

        # Até 3 imagens CDN oficiais
        img1 = cdn_images[0] if len(cdn_images) > 0 else ""
        img2 = cdn_images[1] if len(cdn_images) > 1 else img1
        img3 = cdn_images[2] if len(cdn_images) > 2 else img1

        block1 = {
            "tag": template["act1"]["tag"],
            "fa_icon": template["act1"].get("fa_icon", "fa-solid fa-palette"),
            "title": template["act1"]["title"],
            "description": template["act1"]["desc_tmpl"].format(title=title),
            "image": img1,
            "alt": f"{title} - Visual e Design"
        }
        
        block2 = {
            "tag": template["act2"]["tag"],
            "fa_icon": template["act2"].get("fa_icon", "fa-solid fa-sun"),
            "title": template["act2"]["title"],
            "description": template["act2"]["desc_tmpl"].format(title=title),
            "image": img2,
            "alt": f"{title} - Performance e Detalhes"
        }

        block3 = {
            "tag": template["act3"]["tag"],
            "fa_icon": template["act3"].get("fa_icon", "fa-solid fa-shield-halved"),
            "title": template["act3"]["title"],
            "description": template["act3"]["desc_tmpl"].format(title=title),
            "image": img3,
            "alt": f"{title} - Durabilidade e Acabamento"
        }

        specs = self.extract_product_specs(product, archetype_id)

        return {
            "title": title,
            "tagline": template.get("default_tagline", ""),
            "archetype_id": archetype_id,
            "archetype_name": template.get("name", "BRK"),
            "fa_icon": template.get("fa_icon", "fa-solid fa-fish"),
            "store_key": store_key,
            "theme_color": theme_color,
            "theme_bg": theme_bg,
            "care_icon": care_icon,
            "care_tips": template.get("care_tips", "Lavar à mão ou em ciclo suave. Secar à sombra."),
            "narrative_blocks": [block1, block2, block3],
            "specs": specs
        }
