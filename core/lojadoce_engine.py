"""
Motor de Verticalização e Higienização para Loja Doce (VTEX - https://www.lojadoce.com.br/).

Expande títulos abreviados de ERP, extrai atributos técnicos reais de cada SKU
(peso/volume, dimensões, quantidade no pacote/caixa, material, sabor/cor, marca,
departamento VTEX e EAN) e gera narrativas de 3 Atos + Ficha Técnica + Conservação
100% específicas para cada subtipo de Confeitaria, Bomboniere, Embalagens,
Artigos de Festa, Presentes/MDF e Papelaria.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


ACCENT_MAP: Dict[str, str] = {
    "CORACAO": "Coração",
    "ACUCAR": "Açúcar",
    "UNIAO": "União",
    "GLACUCAR": "Glaçúcar",
    "AVELA": "Avelã",
    "AMELIA": "Amélia",
    "MOCA": "Moça",
    "NESTLE": "Nestlé",
    "MAVALERIO": "Mavalério",
    "UNTAFACIL": "Untafácil",
    "FACIL": "Fácil",
    "SACHE": "Sachê",
    "IMPALPAVEL": "Impalpável",
    "TRIANGULO": "Triângulo",
    "INSTANTANEO": "Instantâneo",
    "INSTANTANE": "Instantâneo",
    "FORNEAVEL": "Forneável",
    "MASTIGAVEL": "Mastigável",
    "CLASSICOS": "Clássicos",
    "HORTELA": "Hortelã",
    "AMENDOAS": "Amêndoas",
    "TORCAO": "Torção",
    "CITRICO": "Cítrico",
    "REFEICAO": "Refeição",
    "ACRILICA": "Acrílica",
    "ACRILICO": "Acrílico",
    "PLASTICA": "Plástica",
    "PLASTICO": "Plástico",
    "REFORCADO": "Reforçado",
    "REFORCADA": "Reforçada",
    "DESCARTAVEL": "Descartável",
    "DESCARTAVEIS": "Descartáveis",
    "LILAS": "Lilás",
    "TACA": "Taça",
    "TACAS": "Taças",
    "PETALAS": "Pétalas",
    "BEBE": "Bebê",
    "PEROLA": "Pérola",
    "MEDIA": "Média",
    "LANCA": "Lança",
    "OCULOS": "Óculos",
    "MAO": "Mão",
    "SAO": "São",
    "MAGICO": "Mágico",
    "LACO": "Laço",
    "LACOS": "Laços",
    "TOQUIO": "Tóquio",
    "SINTETICO": "Sintético",
    "SINTETICA": "Sintética",
    "FE": "Fé",
    "NIQUEL": "Níquel",
    "POLIESTER": "Poliéster",
    "CRIANCA": "Criança",
    "CRIANCAS": "Crianças",
    "DOBRADICA": "Dobradiça",
    "BASTAO": "Bastão",
    "ANOTACAO": "Anotação",
    "ABRACADEIRA": "Abraçadeira",
    "METALICO": "Metálico",
    "METALICA": "Metálica",
    "PICOLE": "Picolé",
    "ESPACIAL": "Espacial",
    "DIGITOS": "Dígitos",
    "ESFEROGRAFICA": "Esferográfica",
    "APAGAVEL": "Apagável",
    "LINGUA": "Língua",
    "PANICO": "Pânico",
    "CHAPEU": "Chapéu",
    "MASCARA": "Máscara",
    "GAS": "Gás",
    "ABOBORA": "Abóbora",
    "LAMPADA": "Lâmpada",
    "ESSENCIA": "Essência",
    "ESSENCIAS": "Essências",
    "ARVORE": "Árvore",
    "FAMILIA": "Família",
    "PRESEPIO": "Presépio",
    "PECAS": "Peças",
    "BALAO": "Balão",
    "BALOES": "Balões",
    "LATEX": "Látex",
    "EGIPCIO": "Egípcio",
    "DECORACAO": "Decoração",
    "UNICORNIO": "Unicórnio",
    "ECONOMICA": "Econômica",
    "ECONOMICO": "Econômico",
    "PO": "Pó",
    "CAFE": "Café",
    "MACA": "Maçã",
    "LIMAO": "Limão",
    "MARACUJA": "Maracujá",
    "CABECA": "Cabeça",
}

LOWER_PARTICLES = {
    "de", "da", "do", "das", "dos", "e", "em", "com", "para", "por", "ao", "na", "no", "nas", "nos", "a", "o"
}
UPPER_ACRONYMS = {
    "MDF", "PP", "PET", "PVC", "TNT", "LED", "UHT", "3D", "4D", "3M", "BRW", "YDH", "VMP", "MB", "KAZ", "WEI", "LSC", "NC"
}

GENERIC_BRAND_STOPWORDS = {
    "",
    "LOJA DOCE",
    "LOJA DOCE IMPORT",
    "BRK",
    "CATÁLOGO OFICIAL",
    "CATALOGO OFICIAL",
    "CATÁLOGO OFICIAL IMPORT",
    "CATALOGO OFICIAL IMPORT",
    "LINHA OFICIAL",
    "IMPORT",
    "TNT",
    "LEMBRANCINHA",
    "LEMBRANCINHAS",
    "BALAO IMPORTADO",
    "BALÃO IMPORTADO",
    "BAZAR IMPORTADORA",
    "GER",
}


def normalize_lojadoce_brand(brand: str, raw_title: str = "") -> str:
    """
    Higieniza marcas genéricas/departamentos de ERP (IMPORT, TNT, LEMBRANCINHA, GER, etc.)
    para 'Linha Oficial' e preserva marcas reais como '3M' quando presentes no título.
    """
    t_up = (raw_title or "").upper()
    if re.search(r"(?<![X/\d])\b3M\b", t_up):
        return "3M"
    raw_b = (brand or "").strip()
    if not raw_b or raw_b.upper() in GENERIC_BRAND_STOPWORDS:
        return "Linha Oficial"
    return raw_b.title() if (raw_b.isupper() and len(raw_b) > 3) else raw_b



LOJA_DOCE_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "ld_confeitaria_ingredientes": {
        "id": "ld_confeitaria_ingredientes",
        "name": "Confeitaria, Chocolates & Ingredientes",
        "fa_icon": "fa-solid fa-cake-candles",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["confeitaria", "cobertura", "recheio", "chantilly", "granulado", "corante", "essencia", "leite condensado", "creme de leite", "cacau", "pasta americana", "desmoldante", "fermento"],
        "default_tagline": "Rendimento Profissional, Estabilidade de Receita e Padronização na Confeitaria",
        "act1": {
            "tag": "Qualidade Profissional & Sabor",
            "fa_icon": "fa-solid fa-cake-candles",
            "title": "PADRONIZAÇÃO TÉCNICA E SABOR SUPERIOR NA CONFEITARIA",
            "desc_tmpl": "Desenvolvido para atender confeiteiros profissionais, padarias e produções artesanais exigentes, o {title} entrega textura uniforme, excelente estabilidade de trabalho e sabor marcante em cada receita."
        },
        "act2": {
            "tag": "Rendimento & Performance",
            "fa_icon": "fa-solid fa-wand-magic-sparkles",
            "title": "ALTO RENDIMENTO E EXCELENTE FLUIDEZ NO PREPARO",
            "desc_tmpl": "Formulado com matérias-primas selecionadas que garantem consistência previsível no derretimento, batimento ou aplicação, evitando perdas de insumos e assegurando acabamento profissional."
        },
        "act3": {
            "tag": "Procedência & Conservação",
            "fa_icon": "fa-solid fa-shield-halved",
            "title": "EMBALAGEM ORIGINAL LACRADA COM CONSERVAÇÃO IDEAL",
            "desc_tmpl": "Fornecido em embalagem original de fábrica que preserva o aroma, o frescor e as propriedades técnicas do ingrediente do início ao fim do uso na cozinha ou ateliê."
        },
        "base_specs": [
            {"label": "Categoria", "default": "Insumos e Ingredientes para Confeitaria Profissional"},
            {"label": "Padrão de Qualidade", "default": "Alto rendimento e estabilidade técnica comprovada"},
            {"label": "Embalagem", "default": "Original de fábrica com vedação segura"},
            {"label": "Aplicação", "default": "Bolos, tortas, doces finos, trufas e sobremesas"}
        ],
        "care_tips": "Armazenar em local seco, fresco e arejado (entre 18°C e 25°C), longe de luz solar direta e de produtos com odores fortes. Após aberto, manter a embalagem bem vedada."
    },
    "ld_confeitaria_formas_utensilios": {
        "id": "ld_confeitaria_formas_utensilios",
        "name": "Formas Forneáveis, Cake Boards & Utensílios",
        "fa_icon": "fa-solid fa-utensils",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["forma", "forminha", "cake board", "tabuleiro", "bico", "papel manteiga", "fundo p/doces", "forneavel"],
        "default_tagline": "Precisão no Acabamento, Sustentação Firme e Apresentação Impecável de Bolos e Doces",
        "act1": {
            "tag": "Apresentação & Padronização",
            "fa_icon": "fa-solid fa-utensils",
            "title": "ACABAMENTO PROFISSIONAL PARA BOLOS, PANETONES E DOCES FINOS",
            "desc_tmpl": "O(A) {title} foi projetado(a) para valorizar a apresentação visual das suas produções de confeitaria, oferecendo medidas precisas e estrutura confiável do preparo à entrega ao cliente."
        },
        "act2": {
            "tag": "Material Higiênico & Firmeza",
            "fa_icon": "fa-solid fa-shield-halved",
            "title": "ESTRUTURA RESISTENTE PRÓPRIA PARA CONTATO COM ALIMENTOS",
            "desc_tmpl": "Confeccionado(a) com material selecionado de grau alimentício que não transfere odor nem sabor, garantindo segurança higiênica, rigidez adequada e praticidade na rotina da confeitaria."
        },
        "act3": {
            "tag": "Praticidade & Produtividade",
            "fa_icon": "fa-solid fa-bolt",
            "title": "AGILIDADE NA PRODUÇÃO E VALORIZAÇÃO NA MESA OU VITRINE",
            "desc_tmpl": "Otimiza o tempo de montagem e finalização em encomendas, festas e datas comemorativas, entregando padrão de vitrine para docerias, confeiteiras e eventos."
        },
        "base_specs": [
            {"label": "Linha", "default": "Utensílios, Formas e Suportes para Confeitaria"},
            {"label": "Segurança Alimentar", "default": "Material atóxico próprio para uso em confeitaria"},
            {"label": "Acabamento", "default": "Corte e conformação de alta precisão"},
            {"label": "Indicação de Uso", "default": "Confeitarias, docerias, padarias e festas"}
        ],
        "care_tips": "Conservar em local seco e protegido de umidade e poeira até o momento do uso. Para utensílios reutilizáveis, higienizar com água e detergente neutro utilizando o lado macio da esponja."
    },
    "ld_bomboniere_chocolates": {
        "id": "ld_bomboniere_chocolates",
        "name": "Chocolates, Bombons, Wafers & Biscoitos",
        "fa_icon": "fa-solid fa-cookie-bite",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["chocolate", "bombom", "biscoito", "wafer", "waffer", "kit kat", "bis", "oreo", "baton", "ouro branco", "stikadinho"],
        "default_tagline": "Sabor Clássico Irresistível, Crocância e Alto Giro para Consumo, Festas ou Revenda",
        "act1": {
            "tag": "Sabor & Indulgência",
            "fa_icon": "fa-solid fa-cookie-bite",
            "title": "SABOR MARCANTE E TEXTURA IRRESISTÍVEL A CADA MORDIDA",
            "desc_tmpl": "Reconhecido pela qualidade e sabor inconfundível, o {title} combina ingredientes selecionados que entregam a experiência perfeita para o lanche, sobremesa, cestas de presente ou revenda."
        },
        "act2": {
            "tag": "Versatilidade & Alto Giro",
            "fa_icon": "fa-solid fa-star",
            "title": "PERFEITO PARA CONSUMO PRÓPRIO, LEMBRANCINHAS, CESTAS E PDV",
            "desc_tmpl": "Item de altíssima aceitação entre crianças e adultos, sendo excelente escolha para compor kits de festa, cestas comemorativas, decoração de bolos e exposição estratégica no ponto de venda."
        },
        "act3": {
            "tag": "Frescor & Procedência",
            "fa_icon": "fa-solid fa-shield-halved",
            "title": "PRODUTO 100% ORIGINAL COM EMBALAGEM PROTETORA DE FÁBRICA",
            "desc_tmpl": "Embalagem desenvolvida para proteger o produto contra umidade e variações externas, preservando a crocância, o brilho e o sabor original até o momento do consumo."
        },
        "base_specs": [
            {"label": "Departamento", "default": "Bomboniere — Chocolates, Bombons e Biscoitos"},
            {"label": "Procedência", "default": "Produto 100% original de fábrica com lote vigente"},
            {"label": "Conservação", "default": "Embalagem selada protetora de aroma e textura"},
            {"label": "Indicação", "default": "Consumo direto, festas, cestas, receitas e revenda"}
        ],
        "care_tips": "Manter em local fresco, seco e inodoro, preferencialmente entre 18°C e 22°C, longe de fontes de calor e da incidência solar direta para evitar derretimento ou alteração de textura."
    },
    "ld_bomboniere_balas_gomas": {
        "id": "ld_bomboniere_balas_gomas",
        "name": "Balas, Gomas, Marshmallows, Chicletes & Pirulitos",
        "fa_icon": "fa-solid fa-candy-cane",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["bala", "chicle", "goma", "marshmallow", "maxmallow", "pirulito", "drops", "tubes", "gelatina", "salgadinho"],
        "default_tagline": "Cores Vibrantes, Sabores Intensos e Excelente Custo-Benefício para Festas e Bomboniere",
        "act1": {
            "tag": "Sabor & Diversão",
            "fa_icon": "fa-solid fa-candy-cane",
            "title": "SABORES FRUTADOS MARCANTE E TEXTURA QUE ENCANTA",
            "desc_tmpl": "O(A) {title} traz toda a alegria, cor e sabor das melhores marcas de bomboniere, garantindo sucesso imediato em festas infantis, eventos temáticos, recepções e no dia a dia."
        },
        "act2": {
            "tag": "Rendimento em Festas & Revenda",
            "fa_icon": "fa-solid fa-gift",
            "title": "IDEAL PARA SACOLINHAS SURPRESA, MESA DE DOCES E COMÉRCIO",
            "desc_tmpl": "Com ótimo rendimento por embalagem, facilita a montagem de lembrancinhas, potes decorativos, espetinhos de doces, baleiros de recepção e exposição de impulso no balcão."
        },
        "act3": {
            "tag": "Qualidade & Higiene",
            "fa_icon": "fa-solid fa-shield-halved",
            "title": "PADRONIZAÇÃO INDUSTRIAL E PROTEÇÃO CONTRA UMIDADE",
            "desc_tmpl": "Produzido sob rigoroso controle de qualidade alimentar e acondicionado em embalagem resistente que preserva a maciez, o aroma e o frescor de cada unidade."
        },
        "base_specs": [
            {"label": "Departamento", "default": "Bomboniere — Balas, Gomas, Marshmallows e Pirulitos"},
            {"label": "Padrão Visual", "default": "Cores vibrantes e acabamento atrativo para festas e PDV"},
            {"label": "Embalagem", "default": "Original lacrada de fábrica"},
            {"label": "Uso Recomendado", "default": "Festas de aniversário, sacolinhas surpresa, eventos e revenda"}
        ],
        "care_tips": "Conservar em local seco, fresco e ao abrigo da luz solar. Após abrir o pacote principal, manter vedado em pote hermético ou com fecho para evitar que absorva umidade do ar."
    },
    "ld_embalagens_descartaveis": {
        "id": "ld_embalagens_descartaveis",
        "name": "Embalagens para Bolos, Copos, Pratos & Descartáveis",
        "fa_icon": "fa-solid fa-box-open",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["embalagem", "copo", "prato", "guardanapo", "garfo", "colher", "bandeja", "pote", "cake box", "disco isopor", "saco p/pipoca", "taca"],
        "default_tagline": "Apresentação Cristalina na Vitrine, Segurança no Transporte e Praticidade para Festas e Delivery",
        "act1": {
            "tag": "Praticidade & Apresentação",
            "fa_icon": "fa-solid fa-box-open",
            "title": "HIGIENE, SEGURANÇA E VALORIZAÇÃO VISUAL PARA FESTAS E DELIVERY",
            "desc_tmpl": "Desenvolvido(a) para oferecer praticidade e apresentação impecável, o(a) {title} garante resistência e excelente acabamento no serviço de festas, eventos, confeitarias e entregas."
        },
        "act2": {
            "tag": "Resistência & Funcionalidade",
            "fa_icon": "fa-solid fa-shield-halved",
            "title": "ESTRUTURA FIRME E MATERIAL ATÓXICO DE GRAU ALIMENTÍCIO",
            "desc_tmpl": "Fabricado(a) com matéria-prima virgem de qualidade controlada que assegura firmeza no manuseio, empilhamento organizado e proteção confiável para alimentos, doces ou bebidas."
        },
        "act3": {
            "tag": "Economia & Agilidade",
            "fa_icon": "fa-solid fa-bolt",
            "title": "OTIMIZAÇÃO DE TEMPO EM EVENTOS, COMÉRCIOS E ENCOMENDAS",
            "desc_tmpl": "Proporciona rapidez na organização e limpeza pós-evento ou agilidade na linha de produção de docerias e lanchonetes, com excelente relação custo-benefício."
        },
        "base_specs": [
            {"label": "Departamento", "default": "Embalagens Confeitaria e Descartáveis para Festas"},
            {"label": "Material", "default": "Grau alimentício atóxico, higiênico e reciclável"},
            {"label": "Acabamento", "default": "Uniforme, resistente e de excelente apresentação"},
            {"label": "Indicação de Uso", "default": "Confeitarias, delivery, festas, buffets e uso doméstico"}
        ],
        "care_tips": "Armazenar em local coberto, seco e livre de poeira, longe de fontes intensas de calor que possam deformar materiais plásticos ou térmicos."
    },
    "ld_artigos_festa_decoracao": {
        "id": "ld_artigos_festa_decoracao",
        "name": "Artigos para Festas, Balões, Fitas & Decoração Sazonal",
        "fa_icon": "fa-solid fa-wand-magic-sparkles",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["balao", "fita", "fitilho", "halloween", "natal", "enfeite", "mascara", "vassoura", "cofrinho", "tubo lata", "bomba manual", "lanca confete", "adereco", "fantasma", "noel"],
        "default_tagline": "Cores Intensas, Acabamento Festivo e Destaque Visual para Comemorações Inesquecíveis",
        "act1": {
            "tag": "Decoração & Impacto Visual",
            "fa_icon": "fa-solid fa-wand-magic-sparkles",
            "title": "DESTAQUE VISUAL E AMBIENTAÇÃO PERFEITA PARA SUA COMEMORAÇÃO",
            "desc_tmpl": "Projetado(a) para transformar qualquer ambiente festivo, o(a) {title} entrega cores vibrantes, excelente acabamento e presença marcante na decoração de festas, vitrines e eventos temáticos."
        },
        "act2": {
            "tag": "Durabilidade & Acabamento",
            "fa_icon": "fa-solid fa-star",
            "title": "MATERIAIS SELECIONADOS QUE MANTÊM O FORMATO E O BRILHO",
            "desc_tmpl": "Produzido(a) com insumos de alta qualidade que garantem resistência durante toda a montagem e realização do evento, facilitando o trabalho de decoradores profissionais e famílias."
        },
        "act3": {
            "tag": "Versatilidade Criativa",
            "fa_icon": "fa-solid fa-gift",
            "title": "FÁCIL COMBINAÇÃO EM PAINÉIS, MESAS TEMÁTICAS E LEMBRANCINHAS",
            "desc_tmpl": "Adapta-se com facilidade a diferentes composições decorativas, arcos, arranjos, fantasias ou lembrancinhas personalizadas, elevando o nível estético da celebração."
        },
        "base_specs": [
            {"label": "Departamento", "default": "Artigos para Festas, Balões e Decoração Sazonal"},
            {"label": "Padrão Estético", "default": "Cores vivas e acabamento de alta definição"},
            {"label": "Praticidade", "default": "Fácil manuseio, montagem e aplicação decorativa"},
            {"label": "Indicação", "default": "Aniversários, eventos temáticos, vitrines e comemorações"}
        ],
        "care_tips": "Manter na embalagem original em local seco e fresco até o momento da montagem. Para itens infláveis ou pequenos, recomenda-se a supervisão de um adulto durante o manuseio por crianças."
    },
    "ld_presentes_caixas_sacolas": {
        "id": "ld_presentes_caixas_sacolas",
        "name": "Caixas em MDF, Sacolas de Presente, Cestas & Mimos",
        "fa_icon": "fa-solid fa-gift",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["caixa mdf", "sacola", "cesta", "laco pronto", "maleta", "caneca", "porta niquel", "espelho bolso", "envelope", "saboneteira", "presente"],
        "default_tagline": "Apresentação Sofisticada, Estrutura Reforçada e Valorização Imediata de Presentes e Kits",
        "act1": {
            "tag": "Apresentação & Encantamento",
            "fa_icon": "fa-solid fa-gift",
            "title": "VALORIZE SEUS PRESENTES, CESTAS E KITS COM ACABAMENTO SUPERIOR",
            "desc_tmpl": "A experiência de presentear começa pelo visual: o(a) {title} une estrutura firme e estética refinada para acomodar lembranças, doces artesanais, bebidas ou mimos especiais com segurança e charme."
        },
        "act2": {
            "tag": "Estrutura & Resistência",
            "fa_icon": "fa-solid fa-shield-halved",
            "title": "CONSTRUÇÃO REFORÇADA E ENCAIXE PRECISO PARA TRANSPORTE SEGURO",
            "desc_tmpl": "Fabricado(a) com materiais de gramatura e rigidez dimensionadas para suportar o peso do conteúdo sem deformar, mantendo a integridade e a elegância do presente até a entrega."
        },
        "act3": {
            "tag": "Personalização & Versatilidade",
            "fa_icon": "fa-solid fa-wand-magic-sparkles",
            "title": "EXCELENTE PARA ARTESANATO, DATAS COMEMORATIVAS E BRINDES CORPORATIVOS",
            "desc_tmpl": "Versátil e pronto(a) para uso ou customização com fitas, laços, papéis de seda, pintura ou tags personalizadas em datas especiais como Dia das Mães, Professores, Natal e aniversários."
        },
        "base_specs": [
            {"label": "Departamento", "default": "Presentes, Caixas em MDF, Cestas e Sacolas"},
            {"label": "Estrutura", "default": "Acabamento reforçado de alta apresentação visual"},
            {"label": "Finalidade", "default": "Montagem de presentes, kits gourmet, cestas e organização"},
            {"label": "Diferencial", "default": "Pronto para uso ou personalização criativa"}
        ],
        "care_tips": "Armazenar em ambiente seco e plano, longe de umidade excessiva. Limpar apenas com pano seco e macio quando necessário."
    },
    "ld_papelaria_artesanato": {
        "id": "ld_papelaria_artesanato",
        "name": "Papelaria, Escritório, Fitas Adesivas & Artesanato",
        "fa_icon": "fa-solid fa-pen-ruler",
        "theme_color": "#db2777",
        "theme_bg": "#fdf2f8",
        "category_keywords": ["papelaria", "fita adesiva", "fita crepe", "fita dupla face", "cola quente", "agenda", "bloco", "caneta", "estojo", "tesoura", "grampeador", "perfurador", "clips", "borracha", "apontador", "massa modelar", "calculadora", "papel colorset", "abracadeira"],
        "default_tagline": "Praticidade no Dia a Dia, Acabamento Limpo em Projetos Criativos e Organização Escolar e Comercial",
        "act1": {
            "tag": "Funcionalidade & Precisão",
            "fa_icon": "fa-solid fa-pen-ruler",
            "title": "DESEMPENHO CONFIÁVEL PARA ROTINA ESCOLAR, ESCRITÓRIO E ARTESANATO",
            "desc_tmpl": "O(A) {title} foi selecionado(a) para entregar praticidade, durabilidade e acabamento limpo nas tarefas diárias de organização, estudos, fechamento de embalagens ou projetos criativos."
        },
        "act2": {
            "tag": "Qualidade Construtiva",
            "fa_icon": "fa-solid fa-shield-halved",
            "title": "MATERIAIS DE ALTA DURABILIDADE E MANUSEIO CONFORTÁVEL",
            "desc_tmpl": "Desenvolvido(a) com componentes resistentes e padrão dimensional preciso que garantem uso suave, seguro e eficiente tanto em casa quanto no ambiente profissional ou ateliê."
        },
        "act3": {
            "tag": "Organização & Produtividade",
            "fa_icon": "fa-solid fa-check",
            "title": "ITEM ESSENCIAL PARA ATELIÊS, COMÉRCIOS, ESTUDANTES E PRESENTES",
            "desc_tmpl": "Combina excelente custo-benefício com apresentação cuidada, sendo ideal para compor kits escolares, suprimentos de expedição/confeitaria ou bancadas de trabalho."
        },
        "base_specs": [
            {"label": "Departamento", "default": "Papelaria, Escritório e Suprimentos de Artesanato"},
            {"label": "Qualidade", "default": "Acabamento preciso e alta durabilidade no uso diário"},
            {"label": "Aplicação", "default": "Escolar, escritório, ateliês criativos e uso comercial"},
            {"label": "Procedência", "default": "Produto original com garantia de qualidade"}
        ],
        "care_tips": "Manter em local seco e arejado, protegido de calor excessivo e umidade para preservar as propriedades originais do produto."
    },
}


def format_lojadoce_title(raw_title: str, brand: str = "") -> str:
    """
    Expande abreviações de ERP da Loja Doce (BISC, CHOC, FORN, C/10UN, PC 24.0, etc.),
    remove códigos internos REF: no final, deduplica marca repetida e aplica Title Case
    com acentuação correta em português.
    """
    if not raw_title:
        return ""
    s = raw_title.strip()
    s = s.replace(")", "")
    s = re.sub(r"\bREF\s*:?\s*[A-Z0-9-]+\s*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"\bLOJA\s+DOCE(?:\s+IMPORT)?\b", "", s, flags=re.IGNORECASE).strip()

    replacements = [
        (r"\bBISC\b", "BISCOITO"),
        (r"\bWAFFER\b", "WAFER"),
        (r"\bCHOC\s+PO\b", "CHOCOLATE EM PO"),
        (r"\bCHOC\s+EM\s+PO\b", "CHOCOLATE EM PO"),
        (r"\bLEITE\s+PO\b", "LEITE EM PO"),
        (r"\bLEITE\s+COND\b", "LEITE CONDENSADO"),
        (r"\bDOCE\s+LEITE\b", "DOCE DE LEITE"),
        (r"\bCREME\s+AVELA\b", "CREME DE AVELA"),
        (r"\bLEITE\s+COCO\b", "LEITE DE COCO"),
        (r"\bFARINHA\s+TRIGO\b", "FARINHA DE TRIGO"),
        (r"\bCHOC\s+COB\s+CONF\b", "CHOCOLATE COBERTURA CONFEITEIRO"),
        (r"\bCHOC\b", "CHOCOLATE"),
        (r"\bCOB\b", "COBERTURA"),
        (r"\bGRANULAD\b", "GRANULADO"),
        (r"\bAO\s+LEIT\b", "AO LEITE"),
        (r"\bMICR\s+LEIT/BR\b", "MICRO AO LEITE E BRANCO"),
        (r"\bGRANULADO\s+CONF\b", "GRANULADO CONFEITEIRO"),
        (r"\bCONF\s+COLORETI\b", "CONFEITO COLORETI"),
        (r"\bRECHEIO\s+FORN\b", "RECHEIO FORNEAVEL"),
        (r"\bFORN\b", "FORNEAVEL"),
        (r"\bDR\s+OET\b", ""),
        (r"\bP/\s*DECORACAO\b", "PARA DECORACAO"),
        (r"\bP/\s*DECOR\b", "PARA DECORACAO"),
        (r"\bP/\s*PRESENTE\b", "PARA PRESENTE"),
        (r"\bP/\s*GARRAFA\b", "PARA GARRAFA"),
        (r"\bP/\s*PIPOCA\b", "PARA PIPOCA"),
        (r"\bP/\s*FESTA\b", "PARA FESTA"),
        (r"\bP/\s*PETISCOS\b", "PARA PETISCOS"),
        (r"\bP/\s*BALA\b", "PARA BALA"),
        (r"\bP/\s*DOCES\b", "PARA DOCES"),
        (r"\bP/\s*ENCHER\b", "PARA ENCHER"),
        (r"\bP/\s*MOLHOS\b", "PARA MOLHOS"),
        (r"\bP/\s*ANOTACAO\b", "PARA ANOTACAO"),
        (r"\bC/LUZ/SOM\b", "COM LUZ E SOM"),
        (r"\bC/LED/SOM\b", "COM LED E SOM"),
        (r"\bC/SOM/LED/MOV\b", "COM SOM LED E MOVIMENTO"),
        (r"\bC/TAMPA\b", "COM TAMPA"),
        (r"\bC/FECHO\b", "COM FECHO"),
        (r"\bC/PEGADOR\b", "COM PEGADOR"),
        (r"\bC/ESPATULA\b", "COM ESPATULA"),
        (r"\bC/ALTO\s+RELEVO\b", "COM ALTO RELEVO"),
        (r"\bC/AMENDOAS\b", "COM AMENDOAS"),
        (r"\bC/PINGENTE\b", "COM PINGENTE"),
        (r"\bC/CAPA\b", "COM CAPA"),
        (r"\bC/LATA\b", "COM LATA"),
        (r"\bC/LINHA\b", "COM LINHA"),
        (r"\bC/ARANHA\b", "COM ARANHA"),
        (r"\bC/GOLA\b", "COM GOLA"),
        (r"\bC/CAPUZ\b", "COM CAPUZ"),
        (r"\bC/RENDA\b", "COM RENDA"),
        (r"\bC/SANGUE\b", "COM SANGUE"),
        (r"\bC/SERINGA\b", "COM SERINGA"),
        (r"\bC/LED\b", "COM LED"),
        (r"\bC/1\s+FURO\b", "COM 1 FURO"),
        (r"\bC/FRUTAS\b", "COM FRUTAS"),
        (r"\bC/BOTAS\b", "COM BOTAS"),
        (r"\bC/\s*(\d+)\s*(?:UN|UNIDADES|UND|UNID)\b", r"COM \1 UNIDADES"),
        (r"\bC/\s*(\d+)\s*(?:PECAS|PCS|PC)\b", r"COM \1 PECAS"),
        (r"\bC/\s*(\d+)\s*(?:FLS?|FOLHAS?|FO|F)\b", r"COM \1 FOLHAS"),
        (r"\bC/\s*(\d+)\s*BLOCOS\b", r"COM \1 BLOCOS"),
        (r"\bC/\s*(\d+(?:,\d+)?M)\b", r"COM \1"),
        (r"\bC/\s*(\d+)\b", r"COM \1 UNIDADES"),
        (r"\b(\d+)\s*PCS\b", r"COM \1 PECAS"),
        (r"\b(\d+)\s*FLS?\b", r"\1 FOLHAS"),
        (r"\b(\d+)\s*F\b", r"\1 FOLHAS"),
        (r"\b(\d+)\s*(?:UN|UNID|UND)\b", r"\1 UNIDADES"),
        (r"\bPC\s*(\d+)(?:\.0)?\b", r"PACOTE COM \1 UNIDADES"),
        (r"\bCX\s*(\d+)(?:\.0)?\b", r"CAIXA COM \1 UNIDADES"),
        (r"\bPCT\s*(\d+)", r"PACOTE \1"),
        (r"\bEMB\s+PLAST\b", "EMBALAGEM PLASTICA"),
        (r"\bEMB\b", "EMBALAGEM"),
        (r"\bTAMPA\s+PLAST\b", "TAMPA PLASTICA"),
        (r"\bSACOLA\s+PLAST\b", "SACOLA PLASTICA"),
        (r"\bPLAST\b", "PLASTICO"),
        (r"\bTRANSPAREN\b", "TRANSPARENTE"),
        (r"\bTRANSP\b", "TRANSPARENTE"),
        (r"\bCOLHER\s+DESC\b", "COLHER DESCARTAVEL"),
        (r"\bPRATO\s+DESC\b", "PRATO DESCARTAVEL"),
        (r"\bFORTE\s+REFOR\b", "FORTE REFORCADO"),
        (r"\bSIMPLIFIC\b", "SIMPLIFICADA"),
        (r"\bSIMP\b", "SIMPLIFICADA"),
        (r"\bGUARD\b", "GUARDANAPO"),
        (r"\bSALG\b", "SALGADINHO"),
        (r"\bMAST\b", "MASTIGAVEL"),
        (r"\bBRINQ\b", "BRINQUEDO"),
        (r"\bTUTTI\s+FRU\b", "TUTTI-FRUTTI"),
        (r"\bFRAMBO\b", "FRAMBOESA"),
        (r"\bBALAO\s+MET\b", "BALAO METALIZADO"),
        (r"\bLISO\s+RED\s+GRANF\b", "LISO REDONDO GRANFESTA"),
        (r"\bLISO\s+RED\b", "LISO REDONDO"),
        (r"\bRED\s+PLATINO\b", "REDONDO PLATINO"),
        (r"\bBAMBU\s+SINTET\s+RED\b", "BAMBU SINTETICO REDONDA"),
        (r"\bAZ/PINK/MARR/VERD/PINK/BEGE\b", "SORTIDA"),
        (r"\bVERM/DOUR\b", "VERMELHO E DOURADO"),
        (r"\bVERM/VERDE\b", "VERMELHO E VERDE"),
        (r"\bDOUR\s+PEROLA\b", "DOURADO PEROLA"),
        (r"\bDOUR\b", "DOURADO"),
        (r"\bVERM\b", "VERMELHO"),
        (r"\bBRANC\b", "BRANCO"),
        (r"\bAZUL\s+CL\b", "AZUL CLARO"),
        (r"\bMELHOR\s+PROF\b", "MELHOR PROFESSOR"),
        (r"\bENF\s+DECOR\b", "ENFEITE DECORATIVO"),
        (r"\bENF\s+FESTA\b", "ENFEITE DE FESTA"),
        (r"\bENF\b", "ENFEITE"),
        (r"\bVELA\s+DECOR\b", "VELA DECORATIVA"),
        (r"\bDECOR\s+PLACA\b", "PLACA DECORATIVA"),
        (r"\bTEC\b", "TECIDO"),
        (r"\bDP\s+FACE\b", "DUPLA FACE"),
        (r"\bTNT\s+EST\b", "TNT ESTAMPADO"),
        (r"\bPOLIRES\b", "POLIRESINA"),
        (r"\bNOEL\s+POLI\b", "NOEL POLIRESINA"),
        (r"\bBICO\s+PAPAG\b", "BICO DE PAPAGAIO"),
        (r"\bSORT\b", "SORTIDO"),
        (r"\bN\.?\s*(\d+)\b", r"Nº \1"),
    ]
    for pat, rep in replacements:
        s = re.sub(pat, rep, s, flags=re.IGNORECASE)

    s = re.sub(r"(\d+),(\d*?[1-9])0+\s*(KG)\b", r"\1,\2\3", s, flags=re.IGNORECASE)
    s = re.sub(r"(\d+)\s*GR\b", r"\1g", s, flags=re.IGNORECASE)
    s = re.sub(r"(\d+)\s*MT\b", r"\1m", s, flags=re.IGNORECASE)
    s = re.sub(r"(\d+)\s*POL\b", r"\1 Polegadas", s, flags=re.IGNORECASE)

    tokens = s.split()
    dedup_tokens: List[str] = []
    for t in tokens:
        if dedup_tokens and dedup_tokens[-1].upper() == t.upper() and t.upper() not in ("PIC", "FINI"):
            continue
        dedup_tokens.append(t)
    tokens = dedup_tokens

    b_clean = (brand or "").strip().upper()
    if len(tokens) > 3 and tokens[0].upper() == tokens[-1].upper() and tokens[0].upper() in ("TNT", "MDF", "EVA"):
        tokens.pop(-1)
    elif b_clean and len(b_clean.split()) == 1 and len(tokens) > 3:
        occurrences = [i for i, t in enumerate(tokens) if t.upper() == b_clean]
        if len(occurrences) >= 2 and occurrences[-1] == len(tokens) - 1:
            if occurrences[0] == 0 and b_clean in ("TNT", "MDF", "EVA", "LED", "PET", "PP", "PVC"):
                tokens.pop(occurrences[-1])
            else:
                tokens.pop(occurrences[0])

    out_words: List[str] = []
    for idx, tok in enumerate(tokens):
        up = tok.upper()
        if "/" in up and not re.match(r"^\d", up):
            slash_parts = [ACCENT_MAP.get(p, p.capitalize()) for p in up.split("/")]
            out_words.append("/".join(slash_parts))
            continue
        if up in UPPER_ACRONYMS or re.match(r"^[A-Z]{1,3}\d+[A-Z0-9]*$", up):
            out_words.append(up)
            continue
        if re.match(r"^\d+(?:[.,]\d+)?L$", up):
            out_words.append(up)
            continue
        if re.match(r"^\d+(?:[.,]\d+)?(?:X\d+(?:[.,]\d+)?)*(?:MM|CM|M|G|KG|ML)$", up):
            out_words.append(up.lower())
            continue
        if re.match(r"^\d+(?:[.,]\d+)?(?:W|V)$", up):
            out_words.append(up)
            continue
        if up in ACCENT_MAP:
            out_words.append(ACCENT_MAP[up])
            continue
        low = up.lower()
        if idx > 0 and low in LOWER_PARTICLES:
            out_words.append(low)
        else:
            out_words.append(low.capitalize())

    return " ".join(out_words)


clean_lojadoce_title = format_lojadoce_title


def detect_lojadoce_archetype(title: str, category: str = "", tags: Optional[List[str]] = None, vendor: str = "", sku: str = "") -> str:
    """
    Classifica qualquer produto da Loja Doce em um dos 8 arquétipos especializados,
    combinando o título soberano do produto com a árvore de categorias VTEX.
    """
    def _norm(txt: str) -> str:
        if not txt:
            return ""
        return "".join(c for c in unicodedata.normalize("NFKD", str(txt)) if not unicodedata.combining(c)).lower()

    t = _norm(title)
    tags_str = " ".join(str(x) for x in (tags or [])) if isinstance(tags, (list, tuple)) else str(tags or "")
    c = _norm(f"{category} {tags_str}")

    # 1. Papelaria & Escritório
    if "/papelaria/" in c or any(w in t for w in (
        "fita adesiva", "fita crepe", "fita dupla face", "cola quente", "agenda ", "bloco p/anotacao",
        "bloco post it", "bloco cole", "bloco adesivo", "caneta esferografica", "estojo juvenil",
        "tesoura escolar", "grampeador", "perfurador de papel", "clips redondo", "apontador",
        "massa modelar", "calculadora de mesa", "corretivo fita", "papel colorset", "abracadeira nylon",
        "pasta porta documentos", "prendedor papel", "tela pintura"
    )):
        return "ld_papelaria_artesanato"

    # 2. Formas, Forminhas, Cake Boards & Utensílios de Confeitaria
    if any(w in t for w in (
        "forma papel", "forma forneavel", "forminha ", "cake board", "tabuleiro", "bico wilton",
        "papel manteiga", "fundo p/doces", "papel p/bala"
    )) or "/formas/" in c or "/utensilios/" in c or "forminhas" in c:
        return "ld_confeitaria_formas_utensilios"

    # 3. Confeitaria — Ingredientes, Coberturas, Recheios, Chantilly, Corantes, Essências
    if any(w in t for w in (
        "cobertura ", "choc cob", "recheio ", "chantilly", "chanty mix", "leite condensado",
        "leite cond ", "creme de leite", "creme avela", "nutella", "choc po ", "choc em po",
        "acucar ", "glacucar", "desmoldante", "granulado", "granulad ", "choco power ball",
        "corante ", "essencia ", "fermento em po", "pasta americana", "liga neutra",
        "brigadeiro de colher", "doce leite colher", "farinha trigo", "leite coco", "po p/decor", "po para decor",
        "leite po ", "leite em po", "leite integral", "leite triangulo"
    )) or ("/confeitaria/" in c and "/formas/" not in c and "/utensilios/" not in c):
        return "ld_confeitaria_ingredientes"

    # 4. Bomboniere — Chocolates de Consumo, Bombons, Wafers, Biscoitos & Panetones (antes de /salgadinhos)
    if not any(x in t for x in ("maleta cx bombom", "emb para trufa", "caixa mdf", "cesta box")) and (
        any(w in t for w in (
            "bisc ", "biscoito", "wafer", "waffer", "kit kat", "bis lacta", "bis xtra", "bombom ", "choc baton",
            "chocolate barra", "moedas ao leite", "doce de leite tablete", "doce de leite em pasta",
            "panetone", "panettone", "chocottone"
        )) or "/bomboniere/chocolate/" in c or "/bomboniere/doces/" in c
    ):
        return "ld_bomboniere_chocolates"

    # 5. Bomboniere — Balas, Gomas, Marshmallows, Chicletes, Pirulitos & Salgadinhos
    if any(w in t for w in (
        "bala ", "chicle ", "goma de mascar", "marshmallow", "maxmallow", "pirulito",
        "drops halls", "tubes twister", "gelatina fini", "gelatines", "salg skid",
        "coloreti", "ovo toys"
    )) or any(sub in c for sub in ("/balas/", "/chicletes", "/gomas e marshmallow/", "/salgadinhos")):
        return "ld_bomboniere_balas_gomas"

    # 6. Embalagens Confeitaria, Copos, Pratos, Talheres & Guardanapos Descartáveis
    if any(w in t for w in (
        "guardanapo", "guard ", "saco p/pipoca", "copo ", "prato ", "cake box", "bandeja isopor",
        "embalagem torta", "embalagem bolo", "embalagem g", "embalagem mini doce", "embalagem cupcake",
        "emb plast", "emb para trufa", "garfo refeicao", "garfo sobremesa", "colher sobremesa",
        "colher desc", "faca refeicao", "caixa doces/salgado", "disco bolo isopor", "pote redondo",
        "mini cake luxo", "mini taca", "lugar americano papel"
    )) or "/embalagens e descartaveis/" in c:
        return "ld_embalagens_descartaveis"

    # 7. Presentes, Caixas em MDF, Sacolas de Presente, Cestas & Utilidades
    if any(w in t for w in (
        "caixa mdf", "bandeja mdf", "sacola ", "cesta ", "laco pronto", "maleta cx bombom",
        "caixa petit", "envelope carta", "caneca frases", "saboneteira", "porta niquel",
        "espelho bolso", "garfos p/ petiscos", "kit de bisnagas"
    )) or "/presentes/" in c:
        return "ld_presentes_caixas_sacolas"

    # 8. Artigos para Festas, Balões, Fitas Decorativas & Sazonais (Halloween / Natal)
    return "ld_artigos_festa_decoracao"


LOJA_DOCE_VTEX_CATEGORIES = (
    "Confeitaria & Panificação",
    "Bomboniere, Chocolates & Doces",
    "Embalagens & Descartáveis",
    "Artigos para Festas & Balões",
    "Presentes, Caixas MDF & Sacolas",
    "Papelaria & Artesanato",
    "Sazonais, Halloween & Natal",
)


def classify_lojadoce_vtex_category(
    title: str,
    category_path: str = "",
    archetype_id: str = "",
    tags: Optional[List[str]] = None,
) -> str:
    """
    Classifica qualquer produto da Loja Doce em uma das 7 categorias oficiais da vitrine VTEX:
    - Confeitaria & Panificação
    - Bomboniere, Chocolates & Doces
    - Embalagens & Descartáveis
    - Artigos para Festas & Balões
    - Presentes, Caixas MDF & Sacolas
    - Papelaria & Artesanato
    - Sazonais, Halloween & Natal
    """
    if category_path in LOJA_DOCE_VTEX_CATEGORIES:
        return category_path

    def _norm(txt: str) -> str:
        if not txt:
            return ""
        return "".join(c for c in unicodedata.normalize("NFKD", str(txt)) if not unicodedata.combining(c)).lower()

    tags_str = " ".join(str(x) for x in (tags or [])) if isinstance(tags, (list, tuple)) else str(tags or "")
    c_norm = _norm(f"{category_path} {tags_str}")
    t_norm = _norm(title)

    # 1. Árvore de departamento VTEX (soberana quando presente)
    if any(k in c_norm for k in ("/halloween", "/fim de ano", "/sazonais", "/natal", "/pascoa")):
        return "Sazonais, Halloween & Natal"
    if "/confeitaria" in c_norm:
        return "Confeitaria & Panificação"
    if "/bomboniere" in c_norm:
        return "Bomboniere, Chocolates & Doces"
    if "/embalagens" in c_norm:
        return "Embalagens & Descartáveis"
    if "/artigos para festas" in c_norm:
        return "Artigos para Festas & Balões"
    if "/presentes" in c_norm:
        return "Presentes, Caixas MDF & Sacolas"
    if "/papelaria" in c_norm:
        return "Papelaria & Artesanato"

    # 2. Fallback por palavras-chave sazonais no título (exceto corante/essência de confeitaria)
    if not any(w in t_norm for w in ("corante", "essencia")) and any(
        w in t_norm for w in (
            "halloween", "natal", "noel", "presepio", "panetone", "panettone", "colomba",
            "vampiro", "bruxa", "fantasma", "esqueleto", "caveira", "zombie", "frankenstein",
            "rena", "azevinho"
        )
    ):
        return "Sazonais, Halloween & Natal"

    # 3. Fallback por arquétipo
    arch = archetype_id or detect_lojadoce_archetype(title=title, category=category_path, tags=tags)
    arch_map = {
        "ld_confeitaria_ingredientes": "Confeitaria & Panificação",
        "ld_confeitaria_formas_utensilios": "Confeitaria & Panificação",
        "ld_bomboniere_chocolates": "Bomboniere, Chocolates & Doces",
        "ld_bomboniere_balas_gomas": "Bomboniere, Chocolates & Doces",
        "ld_embalagens_descartaveis": "Embalagens & Descartáveis",
        "ld_artigos_festa_decoracao": "Artigos para Festas & Balões",
        "ld_presentes_caixas_sacolas": "Presentes, Caixas MDF & Sacolas",
        "ld_papelaria_artesanato": "Papelaria & Artesanato",
    }
    return arch_map.get(arch, "Confeitaria & Panificação")



def extract_lojadoce_attributes(
    raw_title: str,
    formatted_title: str,
    brand: str,
    category: str,
    sku: str,
    archetype_id: str = "",
) -> Dict[str, str]:
    """
    Extrai dimensões, peso/volume, quantidade por embalagem, material, sabor/cor e subcategoria
    diretamente do título e árvore VTEX do produto para popular os 3 Atos e a Ficha Técnica.
    """
    t_up = (raw_title or "").upper()
    f_low = (formatted_title or "").lower()
    arch = archetype_id or detect_lojadoce_archetype(raw_title, category=category, vendor=brand, sku=sku)

    # 1. Peso ou Volume (ex: 700g, 1,01kg, 1L, 600ml, 18g)
    m_wv = re.search(r"\b(\d+(?:[.,]\d+)?\s*(?:KG|GR|G|ML|L))\b", t_up)
    weight_vol = ""
    if m_wv:
        wv = m_wv.group(1).replace(" ", "")
        wv = re.sub(r"(\d+),(\d*?[1-9])0+KG$", r"\1,\2kg", wv, flags=re.I)
        wv = re.sub(r"GR$", "g", wv, flags=re.I)
        if wv.upper().endswith("L") and not wv.upper().endswith("ML"):
            weight_vol = wv[:-1] + " Litro(s)" if wv[:-1] == "1" else wv.upper()
        else:
            weight_vol = wv.lower()

    # 2. Dimensões / Medidas (ex: 21,5x15x8cm, 12mmx40m, 3mmx30cm, 15cm, 140cm)
    # Remove marca 3M isolada antes de buscar dimensões unidimensionais em metros (M)
    t_up_dim = re.sub(r"(?<![X/\d])\b3M\b", "", t_up)
    m_dim = re.search(r"\b(\d+(?:[.,]\d+)?\s*(?:MM|CM|M)?\s*X\s*\d+(?:[.,]\d+)?(?:\s*X\s*\d+(?:[.,]\d+)?)?\s*(?:MM|CM|M))\b", t_up_dim)
    if not m_dim:
        m_dim = re.search(r"\b(\d+(?:[.,]\d+)?\s*(?:MM|CM|M|POL))\b", t_up_dim)
    dimensions = ""
    if m_dim:
        dimensions = m_dim.group(1).lower().replace("x", " x ").replace("  ", " ").replace("pol", " polegadas")

    # 3. Quantidade na Embalagem (ex: C/50UN, PC 24.0, CX 30, 80 FOLHAS, 12 CORES)
    pack_qty = "Unidade individual"
    is_stapler_or_punch = any(w in f_low or w in t_up.lower() for w in ("grampeador", "perfurador"))
    is_bound_stationery = any(w in f_low or w in t_up.lower() for w in ("agenda", "caderno", "bloco", "diário", "diario", "planner"))
    has_multi_blocks = bool(re.search(r"\b(\d+)\s*BLOCOS\b", f"{raw_title} {formatted_title}", re.I))

    if is_bound_stationery and not has_multi_blocks:
        m_int_fls = re.search(r"\b(\d+)\s*Folhas\b", formatted_title, re.I)
        if m_int_fls:
            pack_qty = f"Unidade individual ({m_int_fls.group(1)} folhas internas)"
    else:
        m_pack = (
            re.search(r"((?:Pacote|Caixa)\s+com\s+\d+\s+Unidades)", formatted_title, re.I)
            or re.search(
                r"(com\s+\d+\s+(?:Unidades|Peças|Blocos))"
                if (is_stapler_or_punch or is_bound_stationery)
                else r"(com\s+\d+\s+(?:Unidades|Folhas|Peças|Blocos))",
                formatted_title,
                re.I,
            )
            or (
                None
                if (is_stapler_or_punch or is_bound_stationery)
                else re.search(r"\b(\d+\s+(?:Unidades|Folhas|Peças|Cores))\b", formatted_title, re.I)
            )
        )
        if m_pack:
            pack_qty = m_pack.group(1)
            if pack_qty.lower().startswith("com "):
                pack_qty = "Embalagem " + pack_qty
        elif "guardanapo" in f_low or "guard " in t_up.lower():
            m_guard_qty = re.search(r"\b\d+(?:[.,]\d+)?\s*X\s*\d+(?:[.,]\d+)?\s*CM\s+(\d+)\b", t_up)
            if m_guard_qty and int(m_guard_qty.group(1)) > 1:
                pack_qty = f"Embalagem com {m_guard_qty.group(1)} Folhas"

    # 4. Material Principal detectado (com guarda estrita para alimentos e word boundaries)
    material = ""
    combined_low = f"{t_up.lower()} {f_low}"
    is_food_archetype = arch in (
        "ld_confeitaria_ingredientes",
        "ld_bomboniere_chocolates",
        "ld_bomboniere_balas_gomas",
    )
    if not is_food_archetype:
        if "mdf" in combined_low:
            material = "Madeira MDF de alta densidade com corte de precisão"
        elif any(k in combined_low for k in ("madeira", "bambu")) and "bambu sintet" not in combined_low:
            material = "Madeira / Bambu de reflorestamento"
        elif "fita" in combined_low and any(k in combined_low for k in ("acrilic", "acrílic", "dupla face")):
            material = "Espuma acrílica adesiva de alta fixação"
        elif "acetato" in combined_low:
            material = "Acetato transparente estruturado para confeitaria fina"
        elif any(k in combined_low for k in ("papel kraft", "kraft")):
            material = "Papel Kraft encorpado de alta gramatura"
        elif any(k in combined_low for k in ("papel forneavel", "forneavel", "forneável")):
            material = "Papel forneável especial próprio para forno (dispensa untar)"
        elif "papel manteiga" in combined_low:
            material = "Papel manteiga siliconado antiaderente de grau alimentício"
        elif "papel colorset" in combined_low:
            material = "Papel Colorset colorido na massa (dupla face)"
        elif any(k in combined_low for k in ("papel seda", "seda nacarado")):
            material = "Papel de seda delicado com acabamento especial"
        elif (
            any(
                k in combined_low
                for k in (
                    "forminha papel",
                    "forma papel",
                    "papel n",
                    "guardanapo",
                    "saco p/pipoca",
                    "saco para pipoca",
                    "prato papel",
                    "lugar americano papel",
                    "fundo p/doces",
                    "fundo para doces",
                    "papel p/bala",
                    "papel para bala",
                )
            )
            or ("forminha" in combined_low and "acetato" not in combined_low)
            or ("caixa petit" in combined_low)
        ):
            material = "Celulose / Papel selecionado de alta alvura e maciez"
        elif "sacola" in combined_low and "plast" not in combined_low and "plást" not in combined_low and "tnt" not in combined_low:
            material = "Papel Couchê / Offset encorpado com alça reforçada"
        elif any(k in combined_low for k in ("acrilica", "acrilico", "acrílica", "acrílico")):
            material = "Poliestireno / Acrílico rígido translúcido de alto brilho"
        elif "isopor" in combined_low:
            material = "Poliestireno Expandido (EPS / Isopor) térmico e higiênico"
        elif re.search(r"\b(?:pet|cristal)\b", combined_low):
            material = "Polietileno Tereftalato (PET Cristal) de alta transparência"
        elif (
            re.search(r"\b(?:pp|plast|plástico|plastico|plástica|plastica)\b", combined_low)
            or any(
                k in combined_low
                for k in (
                    "copo ",
                    "prato ",
                    "pote ",
                    "garfo ",
                    "garfos ",
                    "colher ",
                    "faca ",
                    "embalagem torta",
                    "embalagem bolo",
                    "embalagem g",
                    "embalagem mini",
                    "embalagem cupcake",
                    "mini cake",
                    "mini taca",
                    "mini taça",
                    "bomba manual",
                )
            )
        ):
            material = "Polipropileno (PP) / Plástico atóxico de grau alimentício"
        elif "vidro" in combined_low:
            material = "Vidro cristalino espesso de alta resistência"
        elif "veludo" in combined_low:
            material = "Tecido aveludado de toque macio e acabamento luxuoso"
        elif "cetim" in combined_low:
            material = "Cetim de poliéster com brilho acetinado nas faces"
        elif "aramada" in combined_low:
            material = "Tecido decorativo com bordas estruturadas por fio metálico moldável"
        elif any(k in combined_low for k in ("poliresina", "polires")):
            material = "Poliresina esculpida e pintada com riqueza de detalhes"
        elif re.search(r"\btnt\b", combined_low):
            material = "Tecido Não Tecido (TNT) leve e versátil para decoração"
        elif "nylon" in combined_low:
            material = "Poliamida (Nylon) de alta resistência mecânica"
        elif any(k in combined_low for k in ("balao met", "balão met", "metalizado")):
            material = "Filme poliamida metalizado (Foil) com válvula autosselante"
        elif any(
            k in combined_low
            for k in ("latex", "látex", "balao liso", "balão liso", "balao ", "balão ", "sao roque", "são roque", "pic pic", "festcolor")
        ) and "bomba" not in combined_low:
            material = "Látex de borracha natural biodegradável de alta elasticidade"

    # 5. Sabor, Cor ou Variedade
    flavor_or_color = ""
    fc_rules = [
        ("ao leite", "Chocolate ao Leite"),
        ("meio amargo", "Chocolate Meio Amargo"),
        ("blend", "Blend (Equilíbrio entre Ao Leite e Meio Amargo)"),
        ("branco", "Branco"),
        ("laka", "Chocolate Branco Laka"),
        ("avelã", "Creme de Avelã com Cacau"),
        ("morango", "Morango"),
        ("uva", "Uva"),
        ("melancia", "Melancia"),
        ("menta", "Menta Refrescante"),
        ("hortelã", "Hortelã"),
        ("blueberry", "Blueberry (Mirtilo)"),
        ("tutti-frutti", "Tutti-Frutti"),
        ("framboesa", "Framboesa"),
        ("coco", "Coco"),
        ("iogurte", "Iogurte"),
        ("yogurt", "Iogurte"),
        ("baunilha", "Baunilha"),
        ("panetone", "Aroma Tradicional de Panetone"),
        ("50% cacau", "50% Cacau"),
        ("70% cacau", "70% Cacau Intenso"),
        ("preta", "Preto"),
        ("preto", "Preto"),
        ("vermelho e dourado", "Vermelho e Dourado"),
        ("vermelho", "Vermelho"),
        ("vermelha", "Vermelho"),
        ("azul bebê", "Azul Bebê"),
        ("azul claro", "Azul Claro"),
        ("azul escuro", "Azul Escuro"),
        ("azul tiffany", "Azul Tiffany"),
        ("azul turquesa", "Azul Turquesa"),
        ("azul", "Azul"),
        ("rosa bebê", "Rosa Bebê"),
        ("rosa claro", "Rosa Claro"),
        ("rosa", "Rosa"),
        ("amarelo", "Amarelo"),
        ("amarela", "Amarelo"),
        ("verde", "Verde"),
        ("lilás", "Lilás"),
        ("roxo", "Roxo"),
        ("roxa", "Roxo"),
        ("marrom", "Marrom"),
        ("dourado", "Dourado"),
        ("dourada", "Dourado"),
        ("prata", "Prateado"),
        ("prateado", "Prateado"),
        ("vinho", "Vinho"),
        ("transparente", "Transparente / Cristal"),
        ("incolor", "Incolor / Transparente"),
        ("sortido", "Cores / Modelos Sortidos"),
        ("sortida", "Cores / Modelos Sortidos"),
    ]
    for kw, label in fc_rules:
        if kw in f_low:
            flavor_or_color = label
            break

    # 6. Departamento e Subcategoria VTEX limpa (sem expor nome da loja)
    cat_parts = [p.strip().title() for p in (category or "").split("/") if p.strip()]
    dept_name = cat_parts[0] if cat_parts else "Catálogo Geral"
    subcat_name = " > ".join(cat_parts[:3]) if cat_parts else "Linha Oficial"

    clean_brand = normalize_lojadoce_brand(brand, raw_title)

    return {
        "weight_vol": weight_vol,
        "dimensions": dimensions,
        "pack_qty": pack_qty,
        "material": material,
        "flavor_or_color": flavor_or_color,
        "dept_name": dept_name,
        "subcat_name": subcat_name,
        "sku": sku,
        "brand": clean_brand,
    }


def _parse_grams_or_ml(weight_vol: str, raw_title: str) -> Tuple[float, str]:
    """Retorna (valor_em_g_ou_ml, unidade_base 'g' | 'ml' | '')."""
    txt = f"{weight_vol or ''} {raw_title or ''}".upper()
    m = re.search(r"\b(\d+(?:[.,]\d+)?)\s*(KG|GR|G|ML|L)\b", txt)
    if not m:
        return 0.0, ""
    val = float(m.group(1).replace(",", "."))
    unit = m.group(2).upper()
    if unit == "KG":
        return val * 1000.0, "g"
    if unit in ("G", "GR"):
        return val, "g"
    if unit == "L":
        return val * 1000.0, "ml"
    if unit == "ML":
        return val, "ml"
    return 0.0, ""


def calculate_lojadoce_yield_and_equivalence(
    raw_title: str,
    formatted_title: str,
    attrs: Dict[str, str],
    archetype_id: str,
) -> Dict[str, str]:
    """
    Frente 1 da Auditoria VTEX:
    Calcula automaticamente o rendimento prático e a equivalência dimensional real (cm / polegadas / gramas)
    para Chocolates/Coberturas, Leite Condensado/Recheios, Chantilly, Granulados, Formas Forneáveis,
    Forminhas de Doces, Cake Boards, Embalagens e Balões de Látex/Metalizados.
    """
    t_up = (raw_title or "").upper()
    f_low = (formatted_title or "").lower()
    wv = attrs.get("weight_vol", "")
    dim = attrs.get("dimensions", "")
    pack = attrs.get("pack_qty", "")
    grams_or_ml, base_unit = _parse_grams_or_ml(wv, raw_title)

    yield_estimate = ""
    dimensional_equiv = ""
    gas_and_arch = ""

    is_cake_board = any(w in f_low or w in t_up.lower() for w in ("cake board", "tabuleiro", "disco bolo", "disco isopor"))

    # 1. Conversão automática de medidas em milímetros (mm) / metros (m) para centímetros (cm)
    m_mm3 = re.search(r"\b(\d+(?:[.,]\d+)?)\s*X\s*(\d+(?:[.,]\d+)?)\s*X\s*(\d+(?:[.,]\d+)?)\s*MM\b", t_up)
    m_mm2_roll = None if is_cake_board else re.search(r"\b(\d+(?:[.,]\d+)?)\s*MM\s*(?:X|\s+)\s*(\d+(?:[.,]\d+)?)\s*(M|MT|CM|MM)\b", t_up)
    m_mm2_box = re.search(r"\b(\d+(?:[.,]\d+)?)\s*X\s*(\d+(?:[.,]\d+)?)\s*MM\b", t_up)
    m_m_cm = re.search(r"\b(\d+(?:[.,]\d+)?)\s*M\s*X\s*(\d+(?:[.,]\d+)?)\s*CM\b", t_up)
    m_cm_m = re.search(r"\b(\d+(?:[.,]\d+)?)\s*CM\s*X\s*(\d+(?:[.,]\d+)?)\s*M\b", t_up)
    m_single_mm = None if is_cake_board else re.search(r"\b(\d+(?:[.,]\d+)?)\s*MM\b", t_up)

    if m_mm3:
        d1 = float(m_mm3.group(1).replace(",", ".")) / 10.0
        d2 = float(m_mm3.group(2).replace(",", ".")) / 10.0
        d3 = float(m_mm3.group(3).replace(",", ".")) / 10.0
        dimensional_equiv = (
            f"{d1:.1f} x {d2:.1f} x {d3:.1f} cm (equivalente a {m_mm3.group(0).lower()})"
            .replace(".", ",")
        )
    elif m_mm2_roll:
        w_mm = float(m_mm2_roll.group(1).replace(",", "."))
        w_cm = w_mm / 10.0
        len_val = m_mm2_roll.group(2)
        len_u = "m" if m_mm2_roll.group(3).upper() in ("M", "MT") else m_mm2_roll.group(3).lower()
        dimensional_equiv = (
            f"Largura de {w_cm:.1f} cm ({int(w_mm) if w_mm.is_integer() else w_mm} mm) x comprimento de {len_val}{len_u}"
            .replace(".", ",")
        )
    elif m_mm2_box:
        d1 = float(m_mm2_box.group(1).replace(",", ".")) / 10.0
        d2 = float(m_mm2_box.group(2).replace(",", ".")) / 10.0
        dimensional_equiv = f"{d1:.1f} x {d2:.1f} cm (equivalente a {m_mm2_box.group(0).lower()})".replace(".", ",")
    elif m_m_cm:
        m_val = m_m_cm.group(1)
        cm_val = m_m_cm.group(2)
        dimensional_equiv = f"Rolo/folha com {m_val} metros de comprimento x {cm_val} cm de largura"
    elif m_cm_m:
        cm_val = m_cm_m.group(1)
        m_val = m_cm_m.group(2)
        dimensional_equiv = f"Largura de {cm_val} cm x {m_val} metro(s) de comprimento"
    elif m_single_mm:
        mm_v = float(m_single_mm.group(1).replace(",", "."))
        if mm_v >= 10.0:
            dimensional_equiv = f"{mm_v / 10.0:.1f} cm (equivalente a {int(mm_v) if mm_v.is_integer() else mm_v} mm)".replace(".", ",")
        else:
            dimensional_equiv = f"Espessura/ponta de precisão de {m_single_mm.group(1)} mm"

    # Tratamento transversal para Cake Boards, Tabuleiros e Discos de Bolo (qualquer arquétipo)
    if is_cake_board:
        m_diam = re.search(r"(?:X|\b)(\d+(?:[.,]\d+)?)\s*CM\b", t_up)
        m_thick = re.search(r"(?:^|\b)(\d+(?:[.,]\d+)?)\s*MM\s*X", t_up)
        if m_diam:
            d_cm = int(float(m_diam.group(1).replace(",", ".")))
            aro_min = max(10, d_cm - 6)
            aro_max = max(12, d_cm - 4)
            if d_cm >= 30:
                fatias_str = "suporta bolos de 3,5 kg a 4,5 kg (35 a 45 fatias)"
            elif d_cm >= 26:
                fatias_str = "suporta bolos de 2,5 kg a 3,5 kg (25 a 35 fatias)"
            elif d_cm >= 24:
                fatias_str = "suporta bolos de 1,8 kg a 2,5 kg (18 a 25 fatias)"
            else:
                fatias_str = "suporta bolos e mini tortas de até 1,5 kg (10 a 15 fatias)"
            if m_thick:
                dimensional_equiv = (
                    f"Espessura de {m_thick.group(1)} mm x diâmetro real de {d_cm} cm — "
                    f"recomendado para bolos de aro {aro_min} cm a {aro_max} cm (margem técnica de segurança)"
                )
            else:
                dimensional_equiv = (
                    f"Diâmetro real de {d_cm} cm — recomendado para bolos de aro {aro_min} cm a {aro_max} cm (margem técnica de segurança)"
                )
            m_cb_qty = re.search(r"(\d+)\s+Unidades", pack, re.I)
            if m_cb_qty and int(m_cb_qty.group(1)) > 1:
                yield_estimate = f"Pacote com {m_cb_qty.group(1)} discos/tabuleiros de {d_cm} cm (para bolos de {aro_min} cm a {aro_max} cm, {fatias_str})"
            else:
                yield_estimate = f"Base estruturada para 1 bolo confeitado de {aro_min} cm a {aro_max} cm de diâmetro — {fatias_str}"

    # 2. Chocolates, Coberturas, Recheios, Leite Condensado, Creme de Leite, Chantilly e Confeitos
    is_granulado_or_confeito = any(g in f_low for g in ("granulado", "confeito", "flocos", "power ball", "coloreti"))
    if archetype_id == "ld_confeitaria_ingredientes":
        if ("cobertura" in f_low or ("chocolate" in f_low and "pó" not in f_low and "po " not in f_low and not is_granulado_or_confeito)) and base_unit == "g" and grams_or_ml >= 200:
            trufas = max(1, int(round(grams_or_ml / 25.0)))
            cascas_250 = max(1, int(round(grams_or_ml / 250.0)))
            bombons_12 = max(1, int(round(grams_or_ml / 12.0)))
            yield_estimate = (
                f"Rende aprox. {trufas} trufas/pães de mel banhados (25g), {bombons_12} bombons maciços (12g) "
                f"ou {cascas_250} cascas de Ovo de Páscoa de 250g"
            )
        elif ("leite condensado" in f_low or "leite cond" in t_up.lower()) and base_unit == "g" and grams_or_ml >= 200:
            brig_festa = max(1, int(round((grams_or_ml * 1.10) / 15.0)))
            brig_gourmet = max(1, int(round((grams_or_ml * 1.10) / 25.0)))
            yield_estimate = (
                f"Rende aprox. {brig_festa} brigadeiros de festa (15g) ou {brig_gourmet} brigadeiros gourmet (25g) por embalagem ({wv})"
            )
        elif "creme de leite" in f_low and base_unit == "g" and grams_or_ml >= 150:
            receitas_ganache = max(1, int(round(grams_or_ml / 200.0)))
            yield_estimate = (
                f"Rende {receitas_ganache} {'receita base' if receitas_ganache == 1 else 'receitas base'} de 200g para ganaches, mousses, estrogonofes e estabilização de brigadeiros gourmet ({wv})"
            )
        elif ("leite em pó" in f_low or "leite po" in t_up.lower()) and base_unit == "g" and grams_or_ml >= 150:
            litros_leite = round((grams_or_ml / 130.0), 1)
            receitas_docinho = max(1, int(round(grams_or_ml / 50.0)))
            yield_estimate = (
                f"Rende aprox. {str(litros_leite).replace('.', ',')} litros de leite reconstituído ou até {receitas_docinho} receitas/empanamentos de brigadeiro de Leite Ninho ({wv})"
            )
        elif ("leite de coco" in f_low or "leite integral" in f_low or "leite triângulo" in f_low) and base_unit == "ml" and grams_or_ml >= 200:
            copos_200 = max(1, int(round(grams_or_ml / 200.0)))
            yield_estimate = (
                f"Rende {copos_200} medidas culinárias padrão de 200 ml para caldas de molhar bolo, massas, pudins e cremes ({wv})"
            )
        elif any(w in f_low for w in ("recheio", "doce de leite", "avelã", "nutella", "brigadeiro")) and base_unit == "g" and grams_or_ml >= 250:
            trufas_rech = max(1, int(round(grams_or_ml / 20.0)))
            camadas_bolo = max(1, int(round(grams_or_ml / 400.0)))
            yield_estimate = (
                f"Rende aprox. {trufas_rech} trufas/cones recheados (20g) ou {camadas_bolo} a {camadas_bolo + 1} camadas generosas em bolo aro 20 cm"
            )
        elif ("chantilly" in f_low or "chanty" in f_low) and base_unit == "ml" and grams_or_ml >= 150:
            litros_batido = round((grams_or_ml / 1000.0) * 3.5, 1)
            if grams_or_ml >= 500:
                bolos_aro20 = max(1, int(round((grams_or_ml / 1000.0) * 2.5)))
                yield_estimate = (
                    f"Alto rendimento: {wv} rende até {str(litros_batido).replace('.', ',')} litros após batido (cobre e decora de {bolos_aro20} a {bolos_aro20 + 1} bolos aro 20 cm)"
                )
            else:
                cupcakes_q = max(6, int(round((grams_or_ml / 200.0) * 12)))
                yield_estimate = (
                    f"Alto rendimento: {wv} rende até {str(litros_batido).replace('.', ',')} litro após batido (ideal para cobrir 1 bolo aro 15 cm ou decorar até {cupcakes_q} cupcakes/sobremesas)"
                )
        elif "pasta americana" in f_low and base_unit == "g" and grams_or_ml >= 100:
            cupcakes_pa = max(6, int(round((grams_or_ml / 250.0) * 12)))
            yield_estimate = (
                f"Embalagem de {wv} modela de 15 a 25 apliques decorativos 3D ou reveste até {cupcakes_pa} cupcakes/pirulitos decorados"
            )
        elif "desmoldante" in f_low and base_unit == "ml" and grams_or_ml >= 100:
            aplic_min = max(20, int(round(grams_or_ml * 0.20)))
            aplic_max = max(30, int(round(grams_or_ml * 0.25)))
            yield_estimate = f"Alto rendimento profissional: spray de {wv} rende de {aplic_min} a {aplic_max} aplicações em formas médias de bolo"
        elif ("corante" in f_low or "pó para decoração" in f_low or "po p/decor" in t_up.lower()) and base_unit == "g" and grams_or_ml >= 2:
            if "pó" in f_low or "po " in t_up.lower():
                doces_finos = max(20, int(round(grams_or_ml * 16)))
                yield_estimate = f"Alta concentração de brilho: {wv} finaliza aprox. {doces_finos} doces finos/trufas ou 2 a 3 bolos espatulados"
            else:
                gotas_aprox = max(50, int(round(grams_or_ml * 20)))
                kg_base = max(1, int(round(grams_or_ml / 5.0)))
                yield_estimate = f"Pigmentação superconcentrada: {wv} (aprox. {gotas_aprox} gotas) colore até {kg_base} kg de chantilly, glacê ou pasta americana"
        elif "essência" in f_low or "essencia" in t_up.lower():
            rec_min = max(6, int(round((grams_or_ml or 30.0) / 5.0)))
            rec_max = max(10, int(round((grams_or_ml or 30.0) / 3.0)))
            yield_estimate = f"Aroma concentrado: frasco de {wv or '30ml'} aromatiza de {rec_min} a {rec_max} receitas de massas, trufas, recheios ou panetones"
        elif "liga neutra" in f_low and base_unit == "g":
            litros_calda = max(1, int(round(grams_or_ml / 10.0)))
            yield_estimate = f"Estabiliza aprox. {litros_calda} litros de calda base para sorvetes, geladinhos gourmet e picolés (dosagem padrão de 10g por litro)"
        elif "fermento" in f_low and base_unit == "g":
            is_bio_yeast = any(
                w in f_low or w in t_up.lower()
                for w in ("bio", "biológico", "biologico", "instantâneo", "instantaneo", "fleischmann")
            )
            if is_bio_yeast:
                fresco_eq = int(round(grams_or_ml * 3.0))
                kg_farinha_max = max(1, int(round(grams_or_ml / 10.0)))
                yield_estimate = (
                    f"Equivale a {fresco_eq}g de fermento biológico fresco — fermenta de 500g a {kg_farinha_max}kg de farinha de trigo "
                    f"para pães caseiros, pizzas, panetones e massas fermentadas ({wv})"
                )
            else:
                bolos_ferm = max(1, int(round(grams_or_ml / 10.0)))
                yield_estimate = f"Rende aprox. {bolos_ferm} {'receita' if bolos_ferm == 1 else 'receitas'} de bolo caseiro/profissional (medida padrão de 10g / 1 colher de sopa por receita)"
        elif is_granulado_or_confeito and base_unit == "g" and grams_or_ml >= 50:
            doces_enrolados = max(1, int(round(grams_or_ml / 5.0)))
            yield_estimate = f"Rende a finalização de aprox. {doces_enrolados} brigadeiros/docinhos de festa (média de 5g de confeito por unidade)"
        elif ("açúcar" in f_low or "glacucar" in f_low or "glaçúcar" in f_low or "farinha" in f_low or "chocolate em pó" in f_low) and base_unit == "g" and grams_or_ml >= 150:
            porcoes = max(1, int(round(grams_or_ml / 50.0)))
            yield_estimate = f"Rende aprox. {porcoes} aplicações/receitas padrão de 50g na confeitaria ({wv})"

    # 3. Formas Forneáveis, Forminhas de Doces, Bicos, Papel Manteiga e Cake Boards
    elif archetype_id == "ld_confeitaria_formas_utensilios":
        if "panetone" in f_low or "colomba" in f_low or "forneável" in f_low or "forneavel" in f_low:
            if any(k in t_up for k in ("500G", "N.500", "Nº 500", "N 500")):
                cap_str = "Capacidade nominal para 500g de massa (Panetone/Colomba Tradicional Grande)"
                dimensional_equiv = f"{dimensional_equiv} — {cap_str}" if dimensional_equiv else cap_str
            elif any(k in t_up for k in ("400G", "N.400", "Nº 400", "N 400")):
                cap_str = "Capacidade nominal para 400g a 500g de massa (Panetone Padrão)"
                dimensional_equiv = f"{dimensional_equiv} — {cap_str}" if dimensional_equiv else cap_str
            elif any(k in t_up for k in ("250G", "N.250", "Nº 250", "N 250")):
                cap_str = "Capacidade nominal para 250g de massa (Panetone Médio)"
                dimensional_equiv = f"{dimensional_equiv} — {cap_str}" if dimensional_equiv else cap_str
            elif any(k in t_up for k in ("100G", "N.100", "Nº 100", "N 100", "MINI")):
                cap_str = "Capacidade nominal para 100g de massa (Mini Panetone / Lembrancinha)"
                dimensional_equiv = f"{dimensional_equiv} — {cap_str}" if dimensional_equiv else cap_str
            else:
                dimensional_equiv = dimensional_equiv or f"Forma forneável padronizada{f' ({dim})' if dim else ''} pronta para assamento direto sem untar"
            m_qty = re.search(r"(\d+)\s+Unidades", pack, re.I)
            if m_qty:
                yield_estimate = f"Produz {m_qty.group(1)} unidades assadas e prontas para vitrine por pacote"
        elif "forminha" in f_low or "fundo para doces" in f_low:
            if "nº 5" in f_low or "nº 05" in f_low or "n.5" in t_up.lower():
                dimensional_equiv = dimensional_equiv or "Padrão Nº 5 (base aprox. 3,3 cm) — ideal para brigadeiros e beijinhos de festa de 12g a 18g"
            elif "nº 4" in f_low or "nº 04" in f_low or "n.4" in t_up.lower():
                dimensional_equiv = dimensional_equiv or "Padrão Nº 4 (base aprox. 3,7 cm) — ideal para brigadeiros gourmet, trufas e bombons de 20g a 30g"
            elif "nº 0" in f_low or "n.0" in t_up.lower():
                dimensional_equiv = dimensional_equiv or "Padrão Gourmet / Empadinha — ideal para doces finos grandes e salgados de festa"
            elif dimensional_equiv:
                dimensional_equiv = f"{dimensional_equiv} — ideal para doces finos, trufas e brigadeiros gourmet de 15g a 25g"
            m_qty = re.search(r"(\d+)\s+Unidades", pack, re.I)
            if m_qty:
                yield_estimate = f"Acomoda {m_qty.group(1)} doces padronizados para mesas de festa e encomendas"
        elif "papel manteiga" in f_low:
            yield_estimate = "Rolo econômico para forrar múltiplas assadeiras, formas de bolo e bancadas de chocolate sem grudar"
        elif "bico" in f_low:
            dimensional_equiv = dimensional_equiv or "Encaixe profissional compatível com sacos de confeitar e adaptadores grandes/padrão"
            yield_estimate = "Utensílio permanente reutilizável em inox para acabamento contínuo em bolos e cupcakes"

    # 4. Balões de Látex, Metalizados e Acessórios de Inflagem (Polegadas ↔ cm + Gás Hélio/Ar + Arco de Balões)
    elif archetype_id == "ld_artigos_festa_decoracao" and ("balão" in f_low or "balao" in f_low):
        is_balloon_accessory = any(
            w in f_low or w in t_up.lower()
            for w in ("bomba", "inflador", "vareta", "suporte", "medidor", "fita para arco", "cola")
        )
        if is_balloon_accessory:
            dimensional_equiv = "Bico cônico universal anatômico compatível com válvulas de balões metalizados (Foil) e gargalos de látex"
            gas_and_arch = "Inflagem manual a ar normal em dupla ação (envia fluxo de ar contínuo ao empurrar e ao puxar o êmbolo)"
            yield_estimate = (
                "Acessório profissional reutilizável — infla balões de látex (Nº 5 a Nº 16), "
                "balões canudo/modelagem (260) e metalizados sem esforço pulmonar"
            )
        else:
            m_qty = re.search(r"(\d+)\s+Unidades", pack, re.I)
            qty_num = int(m_qty.group(1)) if m_qty else 1
            is_met = "metalizado" in f_low or "balao met" in t_up.lower()

            if is_met:
                m_cm_2d = re.search(r"\b(\d+(?:[.,]\d+)?)\s*[xX]\s*(\d+(?:[.,]\d+)?)\s*CM\b", t_up)
                m_pol = re.search(r"\b(\d+)\s*POLEGADAS\b", f_low, re.I)
                m_cm = re.search(r"\b(\d+(?:[.,]\d+)?)\s*CM\b", t_up)
                if m_cm_2d:
                    w_str = m_cm_2d.group(1).replace(".", ",")
                    h_str = m_cm_2d.group(2).replace(".", ",")
                    max_cm = max(float(w_str.replace(",", ".")), float(h_str.replace(",", ".")))
                    pol_eq = int(round(max_cm / 2.54))
                    dimensional_equiv = f"Dimensões da peça: {w_str} cm x {h_str} cm (porte equivalente a aprox. {pol_eq} polegadas)"
                    gas_and_arch = (
                        "Inflagem com Ar normal (bomba manual/canudo)"
                        if max_cm < 45 else
                        "Compatível com Gás Hélio (flutua) ou Ar normal com válvula autosselante"
                    )
                elif m_pol:
                    pol = int(m_pol.group(1))
                    cm_eq = int(round(pol * 2.54))
                    dimensional_equiv = f"{pol} polegadas (aprox. {cm_eq} cm de altura)"
                    gas_and_arch = (
                        "Inflagem com Ar normal (bomba manual/canudo) para fixação em varetas, painéis e arranjos"
                        if pol < 18 else
                        "Compatível com Gás Hélio (flutua) ou Ar normal com válvula autosselante"
                    )
                elif m_cm:
                    cm_raw = m_cm.group(1).replace(".", ",")
                    cm_v = float(cm_raw.replace(",", "."))
                    pol_eq = int(round(cm_v / 2.54))
                    dimensional_equiv = f"{cm_raw} cm (equivalente a aprox. {pol_eq} polegadas)"
                    gas_and_arch = (
                        "Inflagem com Ar normal (bomba manual/canudo)"
                        if cm_v < 45 else
                        "Compatível com Gás Hélio (flutua) ou Ar normal com válvula autosselante"
                    )
                else:
                    dimensional_equiv = "Tamanho decorativo padrão de festa com válvula autosselante"
                    gas_and_arch = "Compatível com Ar normal ou Gás Hélio (conforme dimensão do modelo)"
            else:
                # Balão de Látex por numeração (Nº 5, Nº 7, Nº 8, Nº 9, Nº 10, Nº 11, Nº 12, Nº 16)
                m_num = (
                    re.search(r"\bN[º°.]?\s*0?(\d{1,2}(?:[.,]5)?)\b", f_low, re.I)
                    or re.search(
                        r"\bBAL[AÃ]O\s+(?:DE\s+L[AÁ]TEX\s+)?(?:PIC\s+PIC\s+|S[AÃ]O\s+ROQUE\s+|SAO\s+ROQUE\s+|QUALATEX\s+|PLATINO\s+|HAPPY\s+DAY\s+|FESTBALL\s+|FESTCOLOR\s+|GRANFESTA\s+|LISO\s+|REDONDO\s+|RED\s+|IMPERIAL\s+|CINTILANTE\s+|CANDY\s+|NEON\s+)*0?(\d{1,2}(?:[.,]5)?)\b",
                        f_low,
                        re.I,
                    )
                )
                b_num = float(m_num.group(1).replace(",", ".")) if m_num else 9.0
                nominal_cm_map = {5: 13, 7: 18, 8: 20, 9: 23, 10: 25, 11: 28, 12: 30, 16: 40}
                cm_inflated = nominal_cm_map.get(int(b_num) if b_num.is_integer() else -1, int(round(b_num * 2.54)))
                b_lbl = f"{int(b_num)}" if b_num.is_integer() else str(b_num).replace(".", ",")
                dimensional_equiv = f"Tamanho Nº {b_lbl} — {b_lbl} polegadas (aprox. {cm_inflated} cm de diâmetro inflado)"
                if b_num <= 5.5:
                    gas_and_arch = "Inflagem exclusiva com Ar normal (não flutua com gás hélio) — ideal para detalhes de arcos orgânicos e mini guirlandas"
                    if qty_num >= 20:
                        yield_estimate = f"Pacote com {qty_num} minibalões Nº {b_lbl} (13 cm) para acabamento orgânico, clusters de detalhe e mini arranjos"
                elif b_num <= 7.5:
                    arch_m = round((qty_num / 40.0) * 1.0, 1) if qty_num >= 20 else 0
                    gas_and_arch = "Inflagem recomendada com Ar normal (alta resistência para arcos, colunas e telas)"
                    if arch_m > 0:
                        yield_estimate = f"Pacote com {qty_num} unidades monta aprox. {str(arch_m).replace('.', ',')} m a {str(round(arch_m * 1.25, 1)).replace('.', ',')} m lineares de arco de balões"
                elif b_num >= 14.0:
                    gas_and_arch = "Compatível com Gás Hélio (alta flutuação) ou Ar normal (bases gigantes e esculturas de destaque)"
                    if qty_num >= 6:
                        yield_estimate = f"Pacote com {qty_num} maxibalões Nº {b_lbl} ({cm_inflated} cm) — compõe bases orgânicas gigantes, nuvens esculturais ou buquês com gás hélio"
                else:
                    arch_m = round((qty_num / 36.0) * 1.0, 1) if qty_num >= 15 else 0
                    gas_and_arch = "Compatível com Gás Hélio (flutuação plena) ou Ar normal (bomba manual / compressor de balões)"
                    if arch_m > 0:
                        yield_estimate = (
                            f"Pacote com {qty_num} unidades monta aprox. {str(arch_m).replace('.', ',')} m a {str(round(arch_m * 1.25, 1)).replace('.', ',')} m lineares "
                            f"de arco orgânico (cerca de {max(1, qty_num // 4)} clusters de 4 balões)"
                        )

    # 5. Bomboniere, Embalagens, Caixas MDF, Sacolas, Papelaria e Demais Categorias
    if not yield_estimate:
        is_bound_stationery = any(w in f_low or w in t_up.lower() for w in ("agenda", "caderno", "bloco", "diário", "diario", "planner"))
        has_multi_blocks = bool(re.search(r"\b(\d+)\s*BLOCOS\b", f"{raw_title} {formatted_title}", re.I))
        m_qty = re.search(r"(\d+)\s+(?:Unidades|Folhas|Peças|Blocos|Cores)", pack, re.I)
        if any(w in f_low for w in ("grampeador", "perfurador")):
            m_cap_fls = re.search(r"\b(\d+)\s*(?:Folhas|FLS?)\b", f"{raw_title} {formatted_title}", re.I)
            if m_cap_fls:
                yield_estimate = f"Capacidade operacional para grampear/perfurar até {m_cap_fls.group(1)} folhas simultaneamente com precisão"
        elif is_bound_stationery and not has_multi_blocks:
            m_int_fls = re.search(r"\b(\d+)\s*Folhas\b", formatted_title, re.I)
            if m_int_fls:
                yield_estimate = f"Volume interno de {m_int_fls.group(1)} folhas para anotações, lembretes e organização diária"
            else:
                yield_estimate = "Unidade pronta para organização comercial, recepção, estudos ou escritório"
        elif m_qty and int(m_qty.group(1)) > 1:
            q_n = int(m_qty.group(1))
            if archetype_id in ("ld_bomboniere_chocolates", "ld_bomboniere_balas_gomas"):
                yield_estimate = f"Embalagem com {q_n} unidades — excelente rendimento para sacolinhas surpresa, festas e revenda unitária em PDV"
            elif has_multi_blocks:
                m_fls_per_b = re.search(r"\b(\d+)\s*Folhas\b", formatted_title, re.I)
                fls_txt = f" ({m_fls_per_b.group(1)} folhas por bloco)" if m_fls_per_b else ""
                yield_estimate = f"Kit econômico com {q_n} blocos{fls_txt} para anotações, lembretes e organização"
            else:
                yield_estimate = f"Rendimento de {q_n} unidades/folhas por embalagem para produção padronizada, eventos ou organização"
        elif ("panetone" in f_low or "panettone" in f_low) and base_unit == "g" and grams_or_ml >= 300:
            fatias_min = max(6, int(round(grams_or_ml / 65.0)))
            fatias_max = max(8, int(round(grams_or_ml / 50.0)))
            yield_estimate = f"Rende de {fatias_min} a {fatias_max} fatias generosas ({wv}) para ceias, cafés especiais e cestas de Natal"
        elif base_unit == "g" and grams_or_ml >= 150 and archetype_id in ("ld_bomboniere_chocolates", "ld_bomboniere_balas_gomas"):
            porcoes_25 = max(1, int(round(grams_or_ml / 25.0)))
            yield_estimate = f"Rende aprox. {porcoes_25} porções de 25g para mesa de guloseimas, lembrancinhas ou consumo ({wv})"
        elif archetype_id in ("ld_bomboniere_chocolates", "ld_bomboniere_balas_gomas"):
            yield_estimate = f"Porção individual prática{f' ({wv})' if wv else ''} pronta para consumo imediato, lembrancinhas de festa, cestas ou display de PDV"
        elif archetype_id == "ld_embalagens_descartaveis":
            if "2kg" in f_low or "p56" in f_low:
                yield_estimate = "Capacidade para acondicionar bolos e tortas confeitadas de até 2 kg (aros de 20 cm a 24 cm)"
            elif "1,7kg" in f_low or "p50" in f_low:
                yield_estimate = "Capacidade para acondicionar bolos e tortas de até 1,7 kg (aros de 18 cm a 22 cm)"
            elif "g35" in f_low:
                yield_estimate = "Capacidade ideal para bolos redondos médios e tortas de até 1,2 kg"
            elif "g16" in f_low or "6 doces" in f_low:
                yield_estimate = "Acomoda 6 cupcakes ou doces gourmet em cavidades individuais protetoras"
            elif wv:
                yield_estimate = f"Capacidade volumétrica nominal de {wv} por unidade para serviço seguro de bebidas ou sobremesas"
            else:
                yield_estimate = "Acondicionamento individual seguro para transporte, vitrine de confeitaria e delivery"

    if not dimensional_equiv and dim:
        dimensional_equiv = f"Dimensões nominais de fábrica: {dim}"

    resumo_parts = [p for p in (yield_estimate, dimensional_equiv, gas_and_arch) if p]
    resumo_rendimento = " | ".join(resumo_parts) if resumo_parts else "Padrão dimensional e rendimento oficial de fábrica"

    return {
        "yield_estimate": yield_estimate,
        "dimensional_equiv": dimensional_equiv,
        "gas_and_arch": gas_and_arch,
        "resumo_rendimento": resumo_rendimento,
    }


calculate_lojadoce_yield_and_dimensions = calculate_lojadoce_yield_and_equivalence


def get_anvisa_allergen_and_safety_info(
    raw_title: str,
    formatted_title: str,
    archetype_id: str,
    attrs: Dict[str, str],
) -> Dict[str, str]:
    """
    Frente 3 da Auditoria VTEX:
    Retorna orientação técnica e alerta de segurança alimentar / alergênicos (Padrão ANVISA RDC 26/2015)
    para produtos comestíveis e selo de Grau Alimentício Atóxico (BPA Free) para utensílios e embalagens.
    """
    f_low = (formatted_title or "").lower()
    t_up = (raw_title or "").upper()

    if archetype_id in ("ld_confeitaria_ingredientes", "ld_bomboniere_chocolates", "ld_bomboniere_balas_gomas"):
        # 1. Essências, aromas, corantes e pós decorativos (antes de "panetone" ou "leite" para não gerar falso positivo de glúten/lactose)
        if any(w in f_low or w in t_up.lower() for w in ("essência", "essencia", "aroma ", "corante", "pó para decoração", "po p/decor", "po para decor")):
            val = "Uso alimentício profissional. Não contém glúten. Seguir dosagem recomendada pelo fabricante no rótulo (Padrão ANVISA)."
            return {
                "label": "Segurança Alimentar & Alergênicos (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 2. Desmoldantes, fermentos e liga neutra
        if any(w in f_low or w in t_up.lower() for w in ("desmoldante", "fermento", "liga neutra")):
            val = "Insumo de grau alimentício regulamentado pela ANVISA. Não contém glúten. Verificar na embalagem original a declaração específica de alergênicos e dosagem máxima recomendada."
            return {
                "label": "Segurança Alimentar & Alergênicos (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 3. Leite de Coco (origem 100% vegetal — naturalmente sem lactose e sem glúten)
        if "leite de coco" in f_low or "leite coco" in t_up.lower():
            val = (
                "Informação Regulatória (Padrão ANVISA): Produto de origem vegetal (derivado do coco). "
                "Naturalmente isento de lactose e não contém glúten. Verifique o rótulo para eventuais alergênicos de linha compartilhada."
            )
            return {
                "label": "Informação Regulatória & Alergênicos (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 4. Farinha de Trigo pura (contém trigo e glúten, sem afirmar lactose como ingrediente primário)
        if "farinha de trigo" in f_low or "farinha trigo" in t_up.lower():
            val = (
                "ALÉRGICOS: CONTÉM TRIGO E DERIVADOS. CONTÉM GLÚTEN. "
                "Pode conter traços de soja, aveia, centeio e cevada conforme lote do fabricante (Padrão ANVISA RDC 26/2015)."
            )
            return {
                "label": "Alerta de Alergênicos & Glúten (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 5. Cremes e pastas com Avelã / Nutella (exige declaração explícita de avelãs, leite e soja)
        if any(w in f_low or w in t_up.lower() for w in ("avelã", "avela", "nutella")):
            val = (
                "ALÉRGICOS: CONTÉM AVELÃS E DERIVADOS DE LEITE E SOJA (lactose). "
                "Consulte a presença de glúten no rótulo oficial (Padrão ANVISA RDC 26/2015)."
            )
            return {
                "label": "Alerta de Alergênicos — Avelã, Leite & Soja (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 6. Chocolates/produtos com Amêndoas, Castanhas, Amendoim ou Nozes
        if any(w in f_low or w in t_up.lower() for w in ("amêndoa", "amendoa", "castanha", "amendoim", "nozes")):
            val = (
                "ALÉRGICOS: CONTÉM AMÊNDOAS/OLEAGINOSAS E DERIVADOS DE LEITE E SOJA (lactose); "
                "pode conter traços de trigo/glúten e outras castanhas conforme rotulagem do fabricante (Padrão ANVISA RDC 26/2015)."
            )
            return {
                "label": "Alerta de Alergênicos — Oleaginosas, Leite & Soja (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 7. Chocolate em pó, cacau em pó e granulados tradicionais (sem leite declarado no nome)
        if any(w in f_low or w in t_up.lower() for w in ("chocolate em pó", "choc po", "choc em po", "cacau", "granulado")) and "leite" not in f_low:
            val = (
                "Alerta de Alergênicos (Padrão ANVISA RDC 26/2015): Pode conter derivados de soja e traços de leite/lactose "
                "devido ao compartilhamento de linha industrial. Consulte a lista oficial de ingredientes na embalagem."
            )
            return {
                "label": "Alerta de Alergênicos (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 8. Biscoitos, Wafers, Panetones e Salgadinhos (Trigo + Glúten)
        if any(w in f_low for w in ("biscoito", "wafer", "kit kat", "bis ", "oreo", "panetone", "panettone", "chocottone", "salgadinho")):
            val = "CONTÉM GLÚTEN. Alérgicos: contém derivados de trigo, soja e leite (lactose), podendo conter traços de ovos, amendoim, avelã e castanhas conforme lote do fabricante (RDC 26/2015)."
            return {
                "label": "Alerta de Alergênicos & Glúten (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        # 9. Chocolates ao leite/branco/meio amargo, coberturas, bombons, lácteos, chantilly, recheios, doce de leite e confeitos lácteos
        if any(w in f_low for w in ("chocolate", "cobertura", "bombom", "leite", "chantilly", "chanty", "recheio", "doce de leite", "brigadeiro", "moça", "laka", "baton", "coloreti", "power ball")):
            gluten_note = (
                "CONTÉM GLÚTEN (cereal crocante/malte — verificar rotulagem do fabricante)."
                if any(w in f_low for w in ("power ball", "crocante", "flocos", "bombom"))
                else "Consulte a presença de glúten no rótulo oficial."
            )
            val = f"ALÉRGICOS: Contém derivados de leite (lactose) e derivados de soja; pode conter traços de oleaginosas. {gluten_note} (Padrão ANVISA RDC 26/2015)."
            return {
                "label": "Alerta de Alergênicos & Lactose (ANVISA)",
                "value": val,
                "alerta_alergenicos": val,
            }
        val = "Produto alimentício lacrado de fábrica. Conferir na embalagem original a lista atualizada de ingredientes, corantes, glúten e alérgicos (ANVISA RDC 26/2015)."
        return {
            "label": "Informação de Alergênicos (ANVISA)",
            "value": val,
            "alerta_alergenicos": val,
        }

    if archetype_id in ("ld_confeitaria_formas_utensilios", "ld_embalagens_descartaveis"):
        val = "Material atóxico de grau alimentício (Livre de BPA / Celulose virgem selecionada), inodoro e seguro para contato com alimentos conforme normas da ANVISA."
        return {
            "label": "Segurança & Grau Alimentício",
            "value": val,
            "alerta_alergenicos": val,
        }

    if archetype_id == "ld_artigos_festa_decoracao" and ("balão" in f_low or "balao" in t_up.lower()):
        val = "Produto certificado para uso festivo. Recomenda-se inflar com bomba manual ou compressor e manter supervisão de um adulto durante o uso por crianças."
        return {
            "label": "Segurança & Certificação",
            "value": val,
            "alerta_alergenicos": val,
        }

    val = "Produto não perecível, atóxico e de procedência original garantida. Manter em local seco e fora do alcance de crianças pequenas quando contiver partes destacáveis."
    return {
        "label": "Segurança & Conformidade",
        "value": val,
        "alerta_alergenicos": val,
    }


get_lojadoce_allergen_and_regulatory_info = get_anvisa_allergen_and_safety_info


def generate_lojadoce_seo_metadata(
    formatted_title: str,
    brand: str,
    attrs: Dict[str, str],
    archetype_id: str,
    yield_info: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Frente 2 da Auditoria VTEX (Anti-Bug Meta Tag VTEX):
    Gera `seo_title` (<= 60 caracteres) e `seo_meta_description` (135 a 155 caracteres)
    100% em texto puro UTF-8, sem tags HTML (<style>, <div>) e sem entidades HTML (&aacute;, &nbsp;).
    """
    clean_title = re.sub(r"<[^>]+>", "", formatted_title or "").strip()
    clean_title = re.sub(r"&[a-zA-Z0-9#]+;", "", clean_title).strip()
    clean_title = re.sub(r"\b(?:BRK|Loja\s+Doce(?:\s+Import)?)\b", "", clean_title, flags=re.I).strip()
    clean_title = " ".join(clean_title.split())

    b_disp = (attrs.get("brand") or brand or "Linha Oficial").strip()
    if b_disp.upper() in ("LOJA DOCE", "LOJA DOCE IMPORT", "BRK"):
        b_disp = "Linha Oficial"

    # 1. SEO Title <= 60 caracteres
    seo_title = clean_title
    if len(seo_title) > 60:
        words = seo_title.split()
        acc: List[str] = []
        for w in words:
            cand = " ".join(acc + [w])
            if len(cand) <= 60:
                acc.append(w)
            else:
                break
        seo_title = " ".join(acc) if acc else seo_title[:60].strip()
    elif b_disp != "Linha Oficial" and b_disp.lower() not in seo_title.lower():
        cand = f"{seo_title} | {b_disp}"
        if len(cand) <= 60:
            seo_title = cand

    # 2. SEO Meta Description (135 a 155 caracteres, texto puro UTF-8)
    wv = attrs.get("weight_vol", "")
    dim = attrs.get("dimensions", "")
    pack = attrs.get("pack_qty", "")
    yi = (yield_info or {}).get("yield_estimate") or (yield_info or {}).get("dimensional_equiv") or ""

    detail_bits: List[str] = []
    if wv and wv.lower() not in clean_title.lower():
        detail_bits.append(wv)
    if dim and dim.lower() not in clean_title.lower():
        detail_bits.append(dim)
    if pack and pack != "Unidade individual" and pack.lower() not in clean_title.lower():
        detail_bits.append(pack)
    if yi:
        short_yi = yi.split("(")[0].strip()
        if len(short_yi) <= 55:
            detail_bits.append(short_yi)

    cat_benefit = {
        "ld_confeitaria_ingredientes": "Alto rendimento, estabilidade e procedência original para confeitaria e receitas.",
        "ld_confeitaria_formas_utensilios": "Padrão profissional, grau alimentício atóxico e acabamento impecável na confeitaria.",
        "ld_bomboniere_chocolates": "Sabor original consagrado, lote fresco lacrado e alto giro para festas e revenda.",
        "ld_bomboniere_balas_gomas": "Cores vibrantes, sabor intenso e pacote econômico para lembrancinhas e eventos.",
        "ld_embalagens_descartaveis": "Estrutura firme de grau alimentício, higiene e apresentação impecável no delivery.",
        "ld_artigos_festa_decoracao": "Cores vivas, alta durabilidade e destaque visual para decoração de festas e eventos.",
        "ld_presentes_caixas_sacolas": "Acabamento reforçado e apresentação sofisticada para presentes, cestas e kits.",
        "ld_papelaria_artesanato": "Qualidade comprovada, precisão e durabilidade para escola, escritório e ateliê.",
    }.get(archetype_id, "Qualidade comprovada, procedência original e pronta entrega imediata.")

    extra_str = f" ({', '.join(detail_bits[:2])})" if detail_bits else ""
    base_meta = f"Compre {clean_title}{extra_str}. {cat_benefit} Envio rápido e seguro!"
    base_meta = re.sub(r"<[^>]+>", "", base_meta)
    base_meta = re.sub(r"&[a-zA-Z0-9#]+;", "", base_meta)
    base_meta = " ".join(base_meta.split())

    if len(base_meta) > 155:
        cut = base_meta[:154]
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0].rstrip(".,;:-")
        while cut.split() and cut.split()[-1].lower() in LOWER_PARTICLES | {"Envio".lower(), "rápido".lower()}:
            cut = " ".join(cut.split()[:-1]).rstrip(".,;:-")
        base_meta = cut + "."
    elif len(base_meta) < 130:
        pad = " Produto 100% original com nota fiscal e pronta entrega."
        if len(base_meta) + len(pad) <= 155:
            base_meta = base_meta + pad

    return {
        "seo_title": seo_title,
        "seo_meta_description": base_meta,
    }


def _parse_brl_price(price_str: Any) -> float:
    """Extrai o valor numérico float de strings de preço como 'R$ 49,90', 'R$ 1.249,90' ou '49.90'."""
    if price_str is None:
        return 0.0
    if isinstance(price_str, (int, float)):
        return max(0.0, float(price_str))
    s = str(price_str).strip()
    if not s:
        return 0.0
    m = re.search(r"(\d{1,3}(?:\.\d{3})+,\d+|\d+[.,]\d+|\d+)", s)
    if not m:
        return 0.0
    token = m.group(1)
    if "." in token and "," in token:
        token = token.replace(".", "").replace(",", ".")
    elif "," in token:
        token = token.replace(",", ".")
    try:
        return max(0.0, float(token))
    except ValueError:
        return 0.0


def _fmt_brl(val: float) -> str:
    """Formata float em moeda brasileira padrão 'R$ X,XX'."""
    v = max(0.0, float(val))
    if 0 < v < 0.01:
        v = 0.01
    formatted = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def calculate_lojadoce_b2b_unit_economics(
    price_str: Any,
    raw_title: str,
    formatted_title: str,
    attrs: Optional[Dict[str, str]] = None,
    yield_info: Optional[Dict[str, str]] = None,
    archetype_id: str = "",
) -> Dict[str, str]:
    """
    Plano 2 — Inteligência Comercial B2B (Cálculo Automático de Custo por Unidade / Porção / 100g):
    Extrai o valor numérico de `price` e calcula métricas comerciais B2B reais e precisas:
    - Quando `pack_qty` > 1 (pacote/caixa com múltiplas unidades/folhas): Custo por Unidade / Folha.
    - Quando `weight_vol` > 0 (g/kg/ml/L): Custo por 100g / 100ml e, para Confeitaria e Bomboniere,
      Custo Estimado por Porção / Trufa / Receita com base no rendimento de `yield_info`.
    - Para itens unitários duráveis/decorativos/utensílios/presentes: Resumo econômico de custo unitário direto.
    """
    attrs_dict = attrs or {}
    yield_dict = yield_info or {}
    price_val = _parse_brl_price(price_str)
    unit_price_formatted = _fmt_brl(price_val) if price_val > 0 else ""

    f_low = (formatted_title or "").lower()
    t_up = (raw_title or "").upper()
    wv = str(attrs_dict.get("weight_vol") or "")
    pack_str = str(attrs_dict.get("pack_qty") or "")
    yield_est = str(yield_dict.get("yield_estimate") or "")

    # 1. Detectar quantidade no pacote/caixa (pack_qty > 1)
    is_stapler_or_punch = any(w in f_low or w in t_up.lower() for w in ("grampeador", "perfurador"))
    is_bound_stationery = any(w in f_low or w in t_up.lower() for w in ("agenda", "caderno", "bloco", "diário", "diario", "planner"))
    has_multi_blocks = bool(re.search(r"\b(\d+)\s*BLOCOS\b", f"{raw_title} {formatted_title}", re.I))
    exclude_sheet_pack = is_stapler_or_punch or (is_bound_stationery and not has_multi_blocks)

    combined_pack_txt = f"{pack_str} {formatted_title or ''}"
    m_pack = (
        re.search(r"\b(\d+)\s*(Blocos)\b", combined_pack_txt, re.I)
        if has_multi_blocks
        else re.search(
            r"\b(\d+)\s*(Unidades|Peças|Pecas|Blocos|Cores|Unid|Und|Un)\b"
            if exclude_sheet_pack
            else r"\b(\d+)\s*(Unidades|Folhas|Peças|Pecas|Blocos|Cores|Unid|Und|Un)\b",
            combined_pack_txt,
            re.I,
        )
    )
    qty_num = 1
    unit_kind = "un"
    if m_pack:
        qty_num = int(m_pack.group(1))
        unit_kind = m_pack.group(2).lower()
    elif raw_title and not exclude_sheet_pack:
        m_raw = (
            re.search(r"\bC/\s*(\d+)\s*(BLOCOS?)\b", raw_title, re.I)
            if has_multi_blocks
            else (
                re.search(r"\bC/\s*(\d+)\s*(FLS?|FOLHAS?|FO|F|PECAS?|PCS?|PC|BLOCOS?|UN|UNIDADES|UND|UNID)?\b", raw_title, re.I)
                or re.search(r"\b(?:PC|CX)\s*(\d+)(?:\.0)?\b", raw_title, re.I)
                or re.search(r"\b(\d+)\s*(FLS?|FOLHAS?|PECAS?|PCS|UN|UNID|UND)\b", raw_title, re.I)
            )
        )
        if m_raw:
            qty_num = int(m_raw.group(1))
            unit_kind = (m_raw.group(2) or "un").lower() if m_raw.lastindex and m_raw.lastindex >= 2 else "un"
        elif "guardanapo" in f_low or "guard " in t_up.lower():
            m_guard_qty = re.search(r"\b\d+(?:[.,]\d+)?\s*X\s*\d+(?:[.,]\d+)?\s*CM\s+(\d+)\b", t_up)
            if m_guard_qty and int(m_guard_qty.group(1)) > 1:
                qty_num = int(m_guard_qty.group(1))
                unit_kind = "folhas"

    if unit_kind.startswith(("fl", "fo", "f")):
        unit_singular = "folha"
        unit_plural = "folhas"
        short_unit = "folha"
    elif unit_kind.startswith("bloc"):
        unit_singular = "bloco"
        unit_plural = "blocos"
        short_unit = "bloco"
    else:
        unit_singular = "unidade"
        unit_plural = "unidades"
        short_unit = "un"

    # 2. Detectar peso ou volume líquido consumível (g / ml), excluindo capacidades nominais de formas/copos/embalagens e gramatura GSM de TNT
    is_container_capacity_or_gsm = bool(
        archetype_id in (
            "ld_confeitaria_formas_utensilios",
            "ld_embalagens_descartaveis",
            "ld_presentes_caixas_sacolas",
            "ld_papelaria_artesanato",
        )
        or any(
            w in f_low or w in t_up.lower()
            for w in ("forma ", "forminha", "embalagem", "copo ", "taça", "taca ", "pote ", "balde ", "tnt ")
        )
    )
    if is_container_capacity_or_gsm:
        grams_or_ml, base_unit = 0.0, ""
    else:
        grams_or_ml, base_unit = _parse_grams_or_ml(wv, f"{raw_title or ''} {formatted_title or ''}")

    # Para displays/pacotes de bomboniere com unidades individuais de até 50g ou marcados como PC/CX (ex: 18g PC 24.0),
    # o peso total da embalagem é qty_num * peso_unitario
    total_grams_or_ml = grams_or_ml
    if qty_num > 1 and grams_or_ml > 0:
        if grams_or_ml <= 50.0 or bool(re.search(r"\b(?:PC|CX)\s*\d+", raw_title or "", re.I)):
            total_grams_or_ml = grams_or_ml * qty_num

    is_granulado_or_confeito = any(g in f_low for g in ("granulado", "confeito", "flocos", "power ball", "coloreti"))

    cost_per_unit = ""
    cost_per_100g_ml = ""
    cost_per_portion = ""
    resumo_economia_b2b = ""

    if price_val > 0:
        if total_grams_or_ml > 0 and base_unit in ("g", "ml"):
            val_100 = (price_val / total_grams_or_ml) * 100.0
            cost_per_100g_ml = f"{_fmt_brl(val_100)} a cada 100{base_unit}"

        # Cálculo de custo por porção/trufa/receita para Confeitaria & Bomboniere
        if grams_or_ml > 0 and archetype_id in (
            "ld_confeitaria_ingredientes",
            "ld_bomboniere_chocolates",
            "ld_bomboniere_balas_gomas",
        ):
            if (
                archetype_id == "ld_confeitaria_ingredientes"
                and (
                    "cobertura" in f_low
                    or ("chocolate" in f_low and "pó" not in f_low and "po " not in t_up.lower() and not is_granulado_or_confeito)
                )
                and base_unit == "g"
                and grams_or_ml >= 200
            ):
                porcoes_20g = grams_or_ml / 20.0
                custo_20g = price_val / porcoes_20g
                cost_per_portion = f"custo aproximado de {_fmt_brl(custo_20g)} por trufa/casquinha de 20g"
            elif (
                archetype_id == "ld_confeitaria_ingredientes"
                and any(w in f_low for w in ("recheio", "doce de leite", "avelã", "nutella", "brigadeiro"))
                and base_unit == "g"
                and grams_or_ml >= 250
            ):
                m_trufas = re.search(r"(\d+)\s+trufas", yield_est, re.I)
                n_trufas = int(m_trufas.group(1)) if m_trufas else max(1, int(round(grams_or_ml / 20.0)))
                cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_trufas)} por trufa/cone recheado de 20g"
            elif (
                archetype_id == "ld_confeitaria_ingredientes"
                and ("leite condensado" in f_low or "leite cond" in t_up.lower())
                and base_unit == "g"
                and grams_or_ml >= 200
            ):
                m_brig = re.search(r"(\d+)\s+brigadeiros\s+de\s+festa", yield_est, re.I)
                n_brig = int(m_brig.group(1)) if m_brig else max(1, int(round((grams_or_ml * 1.10) / 15.0)))
                cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_brig)} por brigadeiro de festa (15g)"
            elif (
                archetype_id == "ld_confeitaria_ingredientes"
                and ("chantilly" in f_low or "chanty" in f_low)
                and base_unit == "ml"
                and grams_or_ml >= 150
            ):
                m_bolos = re.search(r"de\s+(\d+)\s+a\s+(\d+)\s+bolos", yield_est, re.I)
                m_cup = re.search(r"até\s+(\d+)\s+cupcakes", yield_est, re.I)
                if m_bolos:
                    n_bolos = max(1, int(m_bolos.group(2)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_bolos)} por bolo aro 20 cm confeitado"
                elif m_cup:
                    n_cup = max(1, int(m_cup.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_cup)} por cupcake/sobremesa decorada"
                else:
                    porcoes_20ml = max(1.0, grams_or_ml / 20.0)
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / porcoes_20ml)} por porção de 20ml"
            else:
                m_doces = re.search(r"(\d+)\s+(?:brigadeiros/docinhos|doces\s+finos)", yield_est, re.I)
                m_fatias = re.search(r"de\s+(\d+)\s+a\s+(\d+)\s+fatias", yield_est, re.I)
                m_porc25 = re.search(r"(\d+)\s+porções\s+de\s+25g", yield_est, re.I)
                m_cup_pa = re.search(r"até\s+(\d+)\s+cupcakes", yield_est, re.I)
                m_kg_cor = re.search(r"colore\s+até\s+(\d+)\s*kg", yield_est, re.I)
                m_calda = re.search(r"Estabiliza\s+aprox\.\s+(\d+)\s+litros", yield_est, re.I)
                m_ferm_bio = re.search(r"fermenta\s+de\s+500g\s+a\s+(\d+)\s*kg", yield_est, re.I)
                m_rec = re.search(
                    r"(\d+)\s+(?:a\s+(\d+)\s+)?(?:receitas?(?:\s+base)?|aplicações(?:/receitas)?|medidas\s+culinárias)",
                    yield_est,
                    re.I,
                )
                if m_doces:
                    n_d = max(1, int(m_doces.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_d)} por doce finalizado"
                elif m_fatias:
                    n_f = max(1, int(m_fatias.group(2)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_f)} por fatia servida"
                elif m_porc25:
                    n_p25 = max(1, int(m_porc25.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_p25)} por porção de 25g"
                elif m_cup_pa:
                    n_cpa = max(1, int(m_cup_pa.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_cpa)} por cupcake/pirulito decorado"
                elif m_kg_cor:
                    n_kg = max(1, int(m_kg_cor.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_kg)} por kg de receita/cobertura colorida"
                elif m_calda:
                    n_cal = max(1, int(m_calda.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_cal)} por litro de calda/receita estabilizada"
                elif m_ferm_bio:
                    n_fb = max(1, int(m_ferm_bio.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_fb)} por receita de 500g a 1kg de farinha fermentada"
                elif m_rec:
                    n_r = max(1, int(m_rec.group(2) or m_rec.group(1)))
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / n_r)} por receita/aplicação"
                elif grams_or_ml >= 20:
                    porcoes_20 = max(1.0, grams_or_ml / 20.0)
                    cost_per_portion = f"custo aproximado de {_fmt_brl(price_val / porcoes_20)} por porção de 20{base_unit}"
                else:
                    cost_per_portion = f"custo unitário de {_fmt_brl(price_val)} por unidade ({wv or f'{int(grams_or_ml)}{base_unit}'})"

        # Composição da métrica comercial B2B principal
        if qty_num > 1:
            unit_cost_val = price_val / qty_num
            unit_cost_str = _fmt_brl(unit_cost_val)
            cost_per_unit = f"{unit_cost_str} / {short_unit}"
            cost_per_portion = f"{unit_cost_str} por {unit_singular}"
            if cost_per_100g_ml:
                resumo_economia_b2b = (
                    f"Pacote com {qty_num} {unit_plural} → sai a apenas {unit_cost_str} por {unit_singular} "
                    f"({unit_price_formatted} na embalagem • {cost_per_100g_ml})"
                )
            else:
                resumo_economia_b2b = (
                    f"Pacote com {qty_num} {unit_plural} → sai a apenas {unit_cost_str} por {unit_singular} "
                    f"({unit_price_formatted} na embalagem)"
                )
        elif grams_or_ml > 0:
            cost_per_unit = f"{unit_price_formatted} / un"
            if cost_per_portion:
                resumo_economia_b2b = f"{unit_price_formatted} na embalagem ({cost_per_100g_ml} • {cost_per_portion})"
            else:
                resumo_economia_b2b = (
                    f"{unit_price_formatted} na embalagem ({cost_per_100g_ml} • excelente rendimento para uso profissional e comercial)"
                )
        else:
            cost_per_unit = f"{unit_price_formatted} / un"
            resumo_economia_b2b = (
                f"Investimento unitário de {unit_price_formatted} — excelente custo-benefício para uso profissional, revenda ou composição de kits"
            )
    else:
        # Fallback caso price não tenha sido informado (ex: testes sintéticos sem preço)
        if qty_num > 1:
            cost_per_unit = f"Pacote c/ {qty_num} {short_unit}"
            resumo_economia_b2b = (
                f"Pacote com {qty_num} {unit_plural} — excelente diluição de custo por {unit_singular} para produção profissional, festas e revenda"
            )
        elif grams_or_ml > 0:
            wv_disp = wv or f"{int(grams_or_ml)}{base_unit}"
            resumo_economia_b2b = (
                f"Embalagem de {wv_disp} — alto rendimento a cada 100{base_unit} e controle exato de custo por porção/receita"
            )
        else:
            resumo_economia_b2b = (
                "Investimento unitário — excelente custo-benefício para uso profissional, revenda ou composição de kits"
            )

    return {
        "unit_price_formatted": unit_price_formatted,
        "cost_per_unit": cost_per_unit,
        "cost_per_100g_ml": cost_per_100g_ml,
        "cost_per_portion": cost_per_portion,
        "resumo_economia_b2b": resumo_economia_b2b,
        "label": "Economia & Custo Unitário (B2B)",
        "value": resumo_economia_b2b,
    }


def build_vtex_specifications(
    attrs: Dict[str, str],
    archetype_id: str,
    yield_info: Dict[str, str],
    allergen_info: Dict[str, str],
    b2b_economics: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Frente 4 da Auditoria VTEX + Plano 2 (Economia B2B):
    Gera o dicionário estruturado de especificações técnicas pronto para alimentar os
    SpecificationFilters (filtros laterais e ficha técnica nativa) da plataforma VTEX.
    """
    vtex_specs: Dict[str, str] = {
        "Marca": attrs.get("brand") or "Linha Oficial",
        "Departamento VTEX": attrs.get("dept_name") or "Catálogo Geral",
        "Categoria VTEX": attrs.get("subcat_name") or "Linha Oficial",
        "Código SKU": str(attrs.get("sku") or ""),
    }
    if attrs.get("weight_vol"):
        vtex_specs["Peso / Volume"] = attrs["weight_vol"]
    if attrs.get("pack_qty"):
        vtex_specs["Quantidade por Embalagem"] = attrs["pack_qty"]
    if attrs.get("dimensions"):
        vtex_specs["Dimensões / Medidas"] = attrs["dimensions"]
    if yield_info.get("dimensional_equiv"):
        vtex_specs["Equivalência Dimensional"] = yield_info["dimensional_equiv"]
    if yield_info.get("yield_estimate"):
        vtex_specs["Rendimento Estimado"] = yield_info["yield_estimate"]
    if b2b_economics and (b2b_economics.get("resumo_economia_b2b") or b2b_economics.get("value")):
        vtex_specs[b2b_economics.get("label", "Economia & Custo Unitário (B2B)")] = (
            b2b_economics.get("resumo_economia_b2b") or b2b_economics.get("value") or ""
        )
    if yield_info.get("gas_and_arch"):
        vtex_specs["Inflagem / Aplicação"] = yield_info["gas_and_arch"]
    if attrs.get("material"):
        vtex_specs["Material"] = attrs["material"]
    if attrs.get("flavor_or_color"):
        vtex_specs["Sabor / Cor / Tonalidade"] = attrs["flavor_or_color"]
    if allergen_info.get("value"):
        vtex_specs[allergen_info.get("label", "Segurança / Alergênicos")] = allergen_info["value"]
    return vtex_specs


def customize_lojadoce_narrative(
    archetype_id: str,
    formatted_title: str,
    raw_title: str,
    brand: str,
    category: str,
    sku: str,
    act1: Dict[str, Any],
    act2: Dict[str, Any],
    act3: Dict[str, Any],
    template: Dict[str, Any],
    price_str: Any = "",
    b2b_economics: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """
    Verticaliza profundamente os 3 Atos, a Ficha Técnica e as Dicas de Conservação
    para cada subtipo de produto da Loja Doce usando os atributos reais extraídos do SKU,
    incluindo Rendimento Prático, Equivalência Dimensional, Economia B2B e Alerta de Alergênicos ANVISA.
    """
    attrs = extract_lojadoce_attributes(raw_title, formatted_title, brand, category, sku, archetype_id=archetype_id)
    yield_info = calculate_lojadoce_yield_and_equivalence(raw_title, formatted_title, attrs, archetype_id)
    allergen_info = get_anvisa_allergen_and_safety_info(raw_title, formatted_title, archetype_id, attrs)
    b2b_info = b2b_economics or calculate_lojadoce_b2b_unit_economics(
        price_str=price_str,
        raw_title=raw_title,
        formatted_title=formatted_title,
        attrs=attrs,
        yield_info=yield_info,
        archetype_id=archetype_id,
    )

    f_low = formatted_title.lower()
    t_up = (raw_title or "").upper()
    b_disp = attrs["brand"]
    wv = attrs["weight_vol"]
    dim = attrs["dimensions"]
    pack = attrs["pack_qty"]
    mat = attrs["material"]
    fc = attrs["flavor_or_color"]
    yield_est = yield_info.get("yield_estimate", "")
    dim_equiv = yield_info.get("dimensional_equiv", "")
    gas_arch = yield_info.get("gas_and_arch", "")
    b2b_val = b2b_info.get("resumo_economia_b2b") or b2b_info.get("value") or ""

    specs: List[Dict[str, str]] = [
        {"label": "Marca / Fabricante", "value": f"{b_disp} (Produto 100% Original)"},
        {"label": "Código de Referência (SKU)", "value": str(sku or "Consulte no anúncio")},
        {"label": "Departamento / Linha", "value": attrs["subcat_name"]},
    ]
    if wv:
        specs.append({"label": "Peso Líquido / Volume", "value": wv})
    if dim:
        specs.append({"label": "Dimensões / Medidas", "value": dim})
    if dim_equiv:
        specs.append({"label": "Equivalência Dimensional / Capacidade", "value": dim_equiv})
    if pack:
        specs.append({"label": "Apresentação / Quantidade", "value": pack})
    if yield_est:
        specs.append({"label": "Rendimento Prático Estimado", "value": yield_est})
    if b2b_val:
        specs.append({"label": "Economia & Custo Unitário (B2B)", "value": b2b_val})
    if gas_arch:
        specs.append({"label": "Tipo de Inflagem Recomendada", "value": gas_arch})
    if mat:
        specs.append({"label": "Material Principal", "value": mat})
    if fc:
        specs.append({"label": "Sabor / Tonalidade", "value": fc})

    # --- SUBTIPOS ESPECÍFICOS POR ARQUÉTIPO ---
    if archetype_id == "ld_confeitaria_ingredientes":
        if "cobertura" in f_low:
            fmt_choc = "em gotas (fácil dosagem e derretimento rápido)" if "gotas" in f_low else "em barra (ideal para fracionar, ralar ou derreter)"
            act1["tag"] = f"Cobertura Fracionada {b_disp} • Dispensa Temperagem"
            act1["title"] = "DERRETIMENTO RÁPIDO, BRILHO ESPELHADO E PRATICIDADE SEM TEMPERAGEM"
            act1["desc_tmpl"] = (
                f"Desenvolvida para garantir agilidade e acabamento impecável na confeitaria, a {{title}} "
                f"possui formulação fracionada {fmt_choc} que, diferente do chocolate nobre tradicional, dispensa o choque térmico (temperagem). "
                f"Basta derreter entre 45°C e 50°C (em banho-maria ou micro-ondas em potência média de 30 em 30 segundos) para obter excelente fluidez, secagem rápida e casquinhas finas, crocantes e brilhantes."
            )
            act2["tag"] = "Rendimento Prático & Aplicações"
            act2["title"] = "IDEAL PARA BANHAR TRUFAS, PÃO DE MEL, CONES, FRUTAS E MOLDAR OVOS"
            act2["desc_tmpl"] = (
                f"Com rendimento superior{f' na embalagem de {wv} ({yield_est.lower()})' if yield_est else (f' na embalagem de {wv}' if wv else '')}, proporciona cobertura uniforme sem bolhas "
                f"e excelente contração no molde para desenforme fácil de bombons, cascas recheadas, pirulitos de chocolate e decorações."
            )
            act3["tag"] = f"Padrão Profissional {b_disp}"
            act3["title"] = "SABOR EQUILIBRADO E ESTABILIDADE EM TEMPERATURA AMBIENTE"
            act3["desc_tmpl"] = (
                f"Mantém o brilho e a firmeza da cobertura por muito mais tempo após cristalizada, garantindo segurança "
                f"na exposição em vitrines, encomendas de festas e transporte no delivery."
            )
            specs.append({"label": "Classificação Técnica", "value": "Cobertura Fracionada (formulada com gordura vegetal selecionada — dispensa temperagem)"})
            specs.append({"label": "Necessita Temperagem?", "value": "Não (Cobertura Fracionada — derreteu entre 45°C e 50°C, usou)"})
            specs.append({"label": "Uso Recomendado", "value": "Banhos de trufas, pão de mel, cones trufados, bombons e moldes de Páscoa"})
        elif "chocolate" in f_low and "pó" not in f_low and "po " not in t_up.lower() and not any(g in f_low for g in ("granulado", "confeito", "flocos", "power ball", "coloreti")):
            act1["tag"] = f"Chocolate Nobre Puro {b_disp} • Manteiga de Cacau"
            act1["title"] = "SABOR NOBRE AUTÊNTICO, DERRETIMENTO AVELUDADO E PADRÃO GOURMET"
            act1["desc_tmpl"] = (
                f"Elaborado com manteiga de cacau pura e seleção rigorosa de cacau, o {{title}} é um Chocolate Nobre verdadeiro "
                f"que entrega derretimento aveludado na boca, aroma profundo e brilho acetinado incomparável para alta confeitaria e chocolateria."
            )
            act2["tag"] = "Orientação Técnica de Temperagem & Ganaches"
            act2["title"] = "TEMPERAGEM PARA MOLDAGEM DE OVOS/BOMBONS OU USO DIRETO EM GANACHES"
            act2["desc_tmpl"] = (
                f"Por ser Chocolate Nobre (e não cobertura fracionada), requer temperagem (choque térmico entre 28°C e 32°C após derretimento a 45°C) "
                f"quando utilizado para moldar cascas de Ovos de Páscoa, bombons e tabletes com contração e snap perfeitos. "
                f"Para ganaches nobres, trufas, brigadeiros gourmet e mousses, basta derreter e incorporar ao creme{f' ({yield_est.lower()})' if yield_est else ''}."
            )
            specs.append({"label": "Classificação Técnica", "value": "Chocolate Nobre Puro (formulado com manteiga de cacau — requer temperagem para moldagem)"})
            specs.append({"label": "Necessita Temperagem?", "value": "Sim para moldagem de cascas/bombons (choque térmico 28°C–32°C); Não para ganaches e recheios"})
        elif "recheio" in f_low or "nutella" in f_low or "brigadeiro" in f_low or "doce de leite" in f_low or "leite condensado" in f_low:
            is_forn = "forneável" in f_low or "forneavel" in f_low
            act1["tag"] = "Recheio Forneável & Estável" if is_forn else f"Cremosidade & Sabor {b_disp}"
            act1["title"] = (
                "CONSISTÊNCIA FIRME RESISTENTE AO FORNO SEM FERVER OU VAZAR"
                if is_forn else
                "TEXTURA AVELUDADA PRONTA PARA RECHEAR, COBRIR E DECORAR"
            )
            act1["desc_tmpl"] = (
                f"O {{title}} entrega sabor intenso e textura perfeitamente estruturada para uso imediato na confeitaria. "
                + (
                    "Sua tecnologia forneável suporta altas temperaturas de forno em pizzas, croissants, tortas, churros e folhados sem ressecar, sem ferver e sem escapar da massa."
                    if is_forn else
                    "Ideal para ponto de brigadeiro, bico de confeitar ou aplicação direta com espátula em bolos de festa, tortas, copos da felicidade, cones trufados e sobremesas gourmet."
                )
            )
            act2["tag"] = "Produtividade & Rendimento na Cozinha"
            act2["title"] = "PADRONIZAÇÃO DE RECEITAS E ALTO RENDIMENTO POR EMBALAGEM"
            act2["desc_tmpl"] = (
                f"Garante que todas as suas encomendas tenham exatamente o mesmo padrão de ponto, brilho e dulçor"
                f"{f' ({yield_est})' if yield_est else (f' com a embalagem de {wv}' if wv else '')}."
            )
            if is_forn:
                specs.append({"label": "Estabilidade Térmica", "value": "Forneável (suporta assamento em forno doméstico e industrial sem ferver ou vazar)"})
        elif "chantilly" in f_low or "chanty" in f_low:
            act1["tag"] = f"Alto Rendimento & Ponto Firme • {b_disp}"
            act1["title"] = "PONTO PERFEITO PARA BICO DE CONFEITAR E ALISAMENTO DE BOLOS"
            act1["desc_tmpl"] = (
                f"Referência absoluta entre confeiteiras, o {{title}} triplica de volume no batimento e atinge textura cremosa, "
                f"porosidade zero e alta estabilidade para espatulagem lisa, rosetas, babados e trabalhos de bico de alta precisão."
            )
            act2["tag"] = "Estabilidade Térmica & Rendimento"
            act2["title"] = "EXCELENTE RESISTÊNCIA EM BANCADA E ACEITAÇÃO DE CORANTES E SABORIZANTES"
            act2["desc_tmpl"] = (
                f"{f'{yield_est}. ' if yield_est else ''}Aceita coloração intensa com corantes hidrossolúveis em gel sem perder o ponto, além de ser a base ideal para o preparo de "
                "chantininho, mousses aeradas, recheios trufados e coberturas de sobremesas."
            )
            template["care_tips"] = "Conservar em local seco e fresco (não congelar antes de bater). Antes do preparo, resfriar em geladeira entre 4°C e 8°C por pelo menos 12 horas e bater em velocidade média para atingir o rendimento máximo."
        elif "corante" in f_low or "pó para decoração" in f_low or "po p/decor" in t_up.lower():
            is_po = "pó" in f_low or "po " in t_up.lower()
            act1["tag"] = f"Alta Pigmentação & Acabamento • {b_disp}"
            act1["title"] = "CORES INTENSAS E FIDELIDADE DE TOM SEM ALTERAR A CONSISTÊNCIA DA RECEITA"
            act1["desc_tmpl"] = (
                f"Formulado com alta concentração de pigmentos para confeitaria artística, o {{title}} atinge tonalidades vivas e uniformes "
                + (
                    "podendo ser aplicado a seco com pincel macio sobre chocolates, pasta americana e doces finos, ou diluído em álcool de cereais/solução alcoólica para pintura metálica e bombinha borrifadora."
                    if is_po else
                    "com base hidrossolúvel em gel/softgel superconcentrada: utiliza poucas gotas para dispersão imediata sem desandar o ponto do chantilly, chantininho, glacê real, merengue, pasta americana ou massas (para chocolate derretido puro, recomenda-se linha lipossolúvel específica)."
                )
            )
            specs.append({
                "label": "Solubilidade / Base Técnica",
                "value": (
                    "Pó decorativo micronizado não tóxico (aplicação a seco ou diluído em álcool de cereais)"
                    if is_po else
                    "Hidrossolúvel em Gel/Softgel concentrado (ideal para chantilly, glacê, pasta americana e massas; não lipossolúvel)"
                ),
            })
            specs.append({
                "label": "Modo de Aplicação Técnica",
                "value": "Aplicação superficial a seco com pincel ou diluído para borrifador/aerógrafo" if is_po else "Dosagem gradual direta em chantilly, glacê, pasta americana e massas",
            })
        elif "desmoldante" in f_low:
            act1["tag"] = f"Liberação Perfeita sem Resíduos • {b_disp}"
            act1["title"] = "DESENFORME IMPECÁVEL DE BOLOS COMPLEXOS SEM USAR FARINHA E MANTEIGA"
            act1["desc_tmpl"] = (
                f"O {{title}} cria uma película antiaderente invisível que solta bolos, pães e tortas até das formas mais trabalhadas "
                f"(como modelos suíços e espirais) sem deixar crosta esbranquiçada de farinha e sem alterar o sabor da massa."
            )
        elif "fermento" in f_low:
            is_bio_yeast = any(
                w in f_low or w in t_up.lower()
                for w in ("bio", "biológico", "biologico", "instantâneo", "instantaneo", "fleischmann")
            )
            if is_bio_yeast:
                act1["tag"] = f"Fermento Biológico Seco Instantâneo • {b_disp}"
                act1["title"] = "AÇÃO DIRETA NA FARINHA SEM DISSOLVER EM ÁGUA PARA PÃES, PIZZAS E PANETONES"
                act1["desc_tmpl"] = (
                    f"Desenvolvido para panificação profissional e caseira de alta performance, o {{title}} contém leveduras selecionadas "
                    f"que vão direto aos ingredientes secos sem necessidade de hidratação prévia em água morna. "
                    f"{f'{yield_est}, garantindo' if yield_est else 'Garante'} crescimento vigoroso, alvéolos macios e aroma autêntico de padaria."
                )
                act2["tag"] = "Equivalência Técnica & Rendimento"
                act2["title"] = "10G DE FERMENTO SECO EQUIVALEM A 30G DE FERMENTO FRESCO (500G A 1KG DE FARINHA)"
                act2["desc_tmpl"] = (
                    "Proporciona força fermentativa 3x mais concentrada que o fermento biológico fresco tradicional, "
                    "com validade prolongada fora da geladeira enquanto fechado e estabilidade superior em massas doces ou salgadas."
                )
            else:
                act1["tag"] = f"Fermento Químico para Confeitaria • {b_disp}"
                act1["title"] = "CRESCIMENTO UNIFORME E MASSAS FOFINHAS EM BOLOS E TORTAS"
                act1["desc_tmpl"] = (
                    f"O {{title}} garante reação equilibrada no forno para bolos caseiros, tortas e cupcakes mais leves, "
                    f"aerados e simétricos{f' ({yield_est})' if yield_est else ''}."
                )
        elif "leite de coco" in f_low or "leite coco" in t_up.lower():
            act1["tag"] = f"Origem 100% Vegetal • {b_disp}"
            act1["title"] = "CREMOSIDADE INTENSA E SABOR NATURAL DA POLPA DO COCO (SEM LACTOSE)"
            act1["desc_tmpl"] = (
                f"Extraído da polpa selecionada do coco, o {{title}} é um ingrediente de origem 100% vegetal "
                f"(naturalmente isento de lactose e glúten) que confere textura aveludada e sabor tropical autêntico "
                f"para caldas de molhar bolo, brigadeiros gourmet, cocadas, manjares, pudins e pratos salgados{f' ({yield_est})' if yield_est else ''}."
            )

    elif archetype_id == "ld_confeitaria_formas_utensilios":
        if "panetone" in f_low or "colomba" in f_low or "forneável" in f_low:
            act1["tag"] = f"Papel Forneável Especial • {b_disp}"
            act1["title"] = "VAI DIRETO AO FORNO SEM UNTAR E VALORIZA A APRESENTAÇÃO DO PANETONE"
            act1["desc_tmpl"] = (
                f"Confeccionada em papel forneável de grau alimentício{f' ({dim_equiv})' if dim_equiv else (f' nas medidas {dim}' if dim else '')}, a {{title}} "
                f"suporta o crescimento e o forneamento da massa com distribuição homogênea de calor e base microperfurada de respiro."
            )
            act2["tag"] = "Do Forno para a Vitrine"
            act2["title"] = "ESTRUTURA FIRME QUE NÃO DEFORMA E DISPENSA DESENFORME"
            act2["desc_tmpl"] = (
                f"Sua parede estruturada mantém o formato clássico durante e após o assamento, permitindo embalar e "
                f"comercializar o produto diretamente na própria forma decorada ({pack})."
            )
        elif "cake board" in f_low or "tabuleiro" in f_low or "disco bolo" in f_low:
            act1["tag"] = f"Sustentação Rígida & Segurança • {b_disp}"
            act1["title"] = "BASE ESTRUTURADA QUE EVITA RACHADURAS NO TRANSPORTE DE BOLOS"
            act1["desc_tmpl"] = (
                f"Projetado para suportar o peso de bolos confeitados e recheados sem envergar, o {{title}} "
                f"{f'({dim_equiv}) ' if dim_equiv else (f'com medidas {dim} ' if dim else '')}garante estabilidade total durante a espatulagem na bailarina, refrigeração e entrega."
            )
            act2["tag"] = "Acabamento Higiênico Grau Alimentício"
            act2["title"] = "SUPERFÍCIE LAMINADA DE FÁCIL LIMPEZA QUE DESTACA A DECORAÇÃO"
            act2["desc_tmpl"] = (
                "Revestimento superior impermeável que facilita a limpeza do rodapé do bolo com espátula ou pano úmido após o trabalho de bico, "
                "conferindo apresentação limpa e profissional."
            )
        elif "forminha" in f_low or "fundo para doces" in f_low:
            act1["tag"] = f"Mesa de Doces Impecável • {b_disp}"
            act1["title"] = "ACABAMENTO DELICADO E PADRONIZADO PARA BRIGADEIROS E DOCES FINOS"
            act1["desc_tmpl"] = (
                f"A {{title}} ({pack}) acomoda brigadeiros, beijinhos, camafeus e trufas com elegância e higiene"
                f"{f' — {dim_equiv}' if dim_equiv else ''}, destacando as cores da mesa principal em aniversários, casamentos e encomendas."
            )

    elif archetype_id == "ld_presentes_caixas_sacolas":
        if "mdf" in f_low:
            act1["tag"] = f"Madeira MDF de Corte Preciso • {b_disp}"
            act1["title"] = f"ESTRUTURA EM MDF RIGOROSAMENTE ALINHADA ({dim.upper() if dim else 'PADRÃO OFICIAL'})"
            act1["desc_tmpl"] = (
                f"Fabricada em MDF de alta densidade com encaixes precisos{f' e dimensões de {dim}' if dim else ''}, a {{title}} "
                f"oferece resistência superior e superfície lisa pronta para uso natural ou personalização artesanal."
            )
            act2["tag"] = "Fechamento & Acabamento"
            act2["title"] = (
                "DOBRADIÇAS E FECHO METÁLICO DE TRAVAMENTO FIRME"
                if "dobradiça" in f_low else
                "TAMPA MODELO SAPATO DE ENCAIXE FIRME E PRÁTICO"
                if "sapato" in f_low else
                "PEGADORES LATERAIS ANATÔMICOS PARA CESTAS E BANDEJAS"
            )
            act2["desc_tmpl"] = (
                "Ideal para montagem de caixas de padrinhos de casamento, kits de doces gourmet, lembranças corporativas, "
                "porta-joias, organização ou técnicas de pintura, decoupage e gravação a laser."
            )
        elif "sacola" in f_low:
            act1["tag"] = f"Apresentação Pronta para Presentear • {b_disp}"
            act1["title"] = f"GRAMATURA REFORÇADA, FUNDO ESTRUTURADO E ALÇAS FIRMES{f' ({dim.upper()})' if dim else ''}"
            act1["desc_tmpl"] = (
                f"A {{title}} valoriza instantaneamente qualquer presente, lembrancinha ou produto de loja. "
                f"Com medidas bem dimensionadas{f' ({dim})' if dim else ''}, acomoda caixas, roupas, brinquedos, cosméticos ou doces com elegância."
            )

    elif archetype_id == "ld_artigos_festa_decoracao":
        if ("bomba" in f_low or "inflador" in f_low) and ("balão" in f_low or "balao" in f_low):
            act1["tag"] = f"Acessório Profissional de Inflagem • {b_disp}"
            act1["title"] = "INFLAGEM RÁPIDA EM DUPLA AÇÃO PARA BALÕES DE LÁTEX, CANUDO E METALIZADOS"
            act1["desc_tmpl"] = (
                f"Projetada para agilizar a montagem de arcos orgânicos, painéis e decorações de festas sem esforço pulmonar, "
                f"a {{title}} conta com sistema mecânico de dupla ação que injeta ar tanto ao empurrar quanto ao puxar o êmbolo."
            )
            act2["tag"] = "Bico Anatômico Universal"
            act2["title"] = "COMPATÍVEL COM BALÕES Nº 5 A Nº 16, BALÕES 260 (CANUDO) E VÁLVULAS FOIL"
            act2["desc_tmpl"] = (
                "Seu bico cônico escalonado oferece encaixe firme no gargalo de balões de látex de todos os tamanhos e "
                "nas válvulas autosselantes de balões metalizados, garantindo produtividade e conforto ergonômico para decoradores."
            )
        elif "balão" in f_low or "balao" in f_low:
            is_met = "metalizado" in f_low
            act1["tag"] = f"Balão {'Metalizado de Alto Brilho' if is_met else 'de Látex Profissional'} • {b_disp}"
            act1["title"] = (
                "EFEITO ESPELHADO E VÁLVULA PRÁTICA PARA DECORAÇÃO DE IMPACTO"
                if is_met else
                "ELASTICIDADE SUPERIOR, CORES INTENSAS E ALTA DURABILIDADE EM ARCOS"
            )
            act1["desc_tmpl"] = (
                f"O {{title}}{f' ({dim_equiv})' if dim_equiv else ''} é escolha certeira de decoradores para criar painéis, buquês e arcos desconstruídos. "
                + (
                    f"Possui acabamento metalizado refletivo que mantém o formato cheio por longo período ({gas_arch})."
                    if is_met else
                    f"Produzido em látex biodegradável de alta resistência ({pack}) que infla no formato correto, garantindo brilho uniforme e menor índice de estouro."
                )
            )
            if yield_est or gas_arch:
                act2["tag"] = "Rendimento em Arcos & Inflagem"
                act2["title"] = "MEDIDA PADRONIZADA PARA ARCOS ORGÂNICOS, GUIRLANDAS E BUQUÊS"
                act2["desc_tmpl"] = (
                    f"{f'{yield_est}. ' if yield_est else ''}{f'{gas_arch}. ' if gas_arch else ''}"
                    "Excelente retenção de ar para manter a decoração impecável do início ao fim da comemoração."
                )
        elif "fita" in f_low or "fitilho" in f_low or "laço" in f_low:
            act1["tag"] = f"Laços & Acabamentos Decorativos • {b_disp}"
            act1["title"] = "CAIMENTO IMPECÁVEL PARA LAÇOS, ÁRVORES DE NATAL, GUIRLANDAS E EMBALAGENS"
            act1["desc_tmpl"] = (
                f"Com medidas de {dim_equiv if dim_equiv else (dim if dim else 'alto rendimento')}, a {{title}} proporciona acabamento sofisticado "
                + (
                    "com bordas aramadas que permitem moldar laços volumosos que não murcham na decoração natalina ou em cestas."
                    if "aramada" in f_low else
                    "para fechamento de embalagens de confeitaria, panetones, ovos de Páscoa, lembrancinhas e presentes."
                )
            )

    if allergen_info:
        specs.append({"label": allergen_info["label"], "value": allergen_info["value"]})

    return specs


