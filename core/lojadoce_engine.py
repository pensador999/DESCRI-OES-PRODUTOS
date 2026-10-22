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
}

LOWER_PARTICLES = {
    "de", "da", "do", "das", "dos", "e", "em", "com", "para", "por", "ao", "na", "no", "nas", "nos", "a", "o"
}
UPPER_ACRONYMS = {
    "MDF", "PP", "PET", "PVC", "TNT", "LED", "UHT", "3D", "4D", "3M", "BRW", "YDH", "VMP", "MB", "KAZ", "WEI", "LSC", "NC"
}


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
    s = re.sub(r"\bLOJA\s+DOCE\s+IMPORT\s*$", "", s, flags=re.IGNORECASE).strip()

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
        (r"\bC/\s*(\d+)\s*(?:UN|UNIDADES|UND)\b", r"COM \1 UNIDADES"),
        (r"\bC/\s*(\d+)\s*(?:FLS?|FOLHAS?|FO|F)\b", r"COM \1 FOLHAS"),
        (r"\bC/\s*(\d+)\s*BLOCOS\b", r"COM \1 BLOCOS"),
        (r"\bC/\s*(\d+(?:,\d+)?M)\b", r"COM \1"),
        (r"\bC/\s*(\d+)\b", r"COM \1 UNIDADES"),
        (r"\b(\d+)\s*PCS\b", r"COM \1 PECAS"),
        (r"\b(\d+)\s*FLS?\b", r"\1 FOLHAS"),
        (r"\b(\d+)\s*F\b", r"\1 FOLHAS"),
        (r"\b(\d+)\s*UN\b", r"\1 UNIDADES"),
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
    if b_clean and len(b_clean.split()) == 1 and len(tokens) > 3:
        occurrences = [i for i, t in enumerate(tokens) if t.upper() == b_clean]
        if len(occurrences) >= 2 and occurrences[-1] == len(tokens) - 1:
            tokens.pop(occurrences[0])

    out_words: List[str] = []
    for idx, tok in enumerate(tokens):
        up = tok.upper()
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
        if up in UPPER_ACRONYMS or re.match(r"^[A-Z]{1,3}\d+[A-Z0-9]*$", up):
            out_words.append(up)
            continue
        low = up.lower()
        if idx > 0 and low in LOWER_PARTICLES:
            out_words.append(low)
        else:
            out_words.append(low.capitalize())

    return " ".join(out_words)


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
    all_txt = f"{t} {c}"

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

    # 4. Bomboniere — Balas, Gomas, Marshmallows, Chicletes, Pirulitos & Salgadinhos
    if any(w in t for w in (
        "bala ", "chicle ", "goma de mascar", "marshmallow", "maxmallow", "pirulito",
        "drops halls", "tubes twister", "gelatina fini", "gelatines", "salg skid",
        "coloreti", "ovo toys"
    )) or any(sub in c for sub in ("/balas/", "/chicletes", "/gomas e marshmallow/", "/salgadinhos")):
        return "ld_bomboniere_balas_gomas"

    # 5. Bomboniere — Chocolates de Consumo, Bombons, Wafers & Biscoitos
    if any(w in t for w in (
        "bisc ", "biscoito", "kit kat", "bis lacta", "bis xtra", "bombom ", "choc baton",
        "chocolate barra", "moedas ao leite", "doce de leite tablete", "doce de leite em pasta"
    )) or "/bomboniere/chocolate/" in c or "/bomboniere/doces/" in c:
        return "ld_bomboniere_chocolates"

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


def extract_lojadoce_attributes(raw_title: str, formatted_title: str, brand: str, category: str, sku: str) -> Dict[str, str]:
    """
    Extrai dimensões, peso/volume, quantidade por embalagem, material, sabor/cor e subcategoria
    diretamente do título e árvore VTEX do produto para popular os 3 Atos e a Ficha Técnica.
    """
    t_up = (raw_title or "").upper()
    f_low = (formatted_title or "").lower()

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
    m_dim = re.search(r"\b(\d+(?:[.,]\d+)?\s*(?:MM|CM|M)?\s*X\s*\d+(?:[.,]\d+)?(?:\s*X\s*\d+(?:[.,]\d+)?)?\s*(?:MM|CM|M))\b", t_up)
    if not m_dim:
        m_dim = re.search(r"\b(\d+(?:[.,]\d+)?\s*(?:MM|CM|M|POL))\b", t_up)
    dimensions = ""
    if m_dim:
        dimensions = m_dim.group(1).lower().replace("x", " x ").replace("  ", " ").replace("pol", " polegadas")

    # 3. Quantidade na Embalagem (ex: C/50UN, PC 24.0, CX 30, 80 FOLHAS, 12 CORES)
    pack_qty = "Unidade individual"
    m_pack = (
        re.search(r"((?:Pacote|Caixa)\s+com\s+\d+\s+Unidades)", formatted_title, re.I)
        or re.search(r"(com\s+\d+\s+(?:Unidades|Folhas|Peças|Blocos))", formatted_title, re.I)
        or re.search(r"\b(\d+\s+(?:Unidades|Folhas|Peças|Cores))\b", formatted_title, re.I)
    )
    if m_pack:
        pack_qty = m_pack.group(1)
        if pack_qty.lower().startswith("com "):
            pack_qty = "Embalagem " + pack_qty

    # 4. Material Principal detectado
    material = ""
    mat_rules = [
        (["mdf"], "Madeira MDF de alta densidade com corte de precisão"),
        (["papel kraft", "kraft"], "Papel Kraft encorpado de alta gramatura"),
        (["papel forneavel", "forneavel"], "Papel forneável especial próprio para forno (dispensa untar)"),
        (["papel manteiga"], "Papel manteiga siliconado antiaderente de grau alimentício"),
        (["papel colorset"], "Papel Colorset colorido na massa (dupla face)"),
        (["papel seda", "seda nacarado"], "Papel de seda delicado com acabamento especial"),
        (["forminha papel", "papel n", "guardanapo", "saco p/pipoca", "prato papel", "lugar americano papel"], "Celulose / Papel selecionado de alta alvura e maciez"),
        (["acrilica", "acrilico"], "Poliestireno / Acrílico rígido translúcido de alto brilho"),
        (["isopor"], "Poliestireno Expandido (EPS / Isopor) térmico e higiênico"),
        (["pet", "cristal"], "Polietileno Tereftalato (PET Cristal) de alta transparência"),
        (["pp", "plast", "copo ", "prato ", "pote "], "Polipropileno (PP) / Plástico atóxico de grau alimentício"),
        (["acetato"], "Acetato transparente estruturado para confeitaria fina"),
        (["vidro"], "Vidro cristalino espesso de alta resistência"),
        (["veludo"], "Tecido aveludado de toque macio e acabamento luxuoso"),
        (["cetim"], "Cetim de poliéster com brilho acetinado nas faces"),
        (["aramada"], "Tecido decorativo com bordas estruturadas por fio metálico moldável"),
        (["poliresina", "polires"], "Poliresina esculpida e pintada com riqueza de detalhes"),
        (["tnt"], "Tecido Não Tecido (TNT) leve e versátil para decoração"),
        (["nylon"], "Poliamida (Nylon) de alta resistência mecânica"),
        (["latex", "balao liso", "balao 9", "balao 7", "balao 5", "balao 16", "sao roque", "pic pic", "festcolor"], "Látex de borracha natural biodegradável de alta elasticidade"),
        (["balao met", "metalizado"], "Filme poliamida metalizado (Foil) com válvula autosselante"),
    ]
    for kws, mat_desc in mat_rules:
        if any(k in t_up.lower() or k in f_low for k in kws):
            material = mat_desc
            break

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

    # 6. Departamento e Subcategoria VTEX limpa
    cat_parts = [p.strip().title() for p in (category or "").split("/") if p.strip()]
    dept_name = cat_parts[0] if cat_parts else "Catálogo Loja Doce"
    subcat_name = " > ".join(cat_parts[:3]) if cat_parts else "Linha Oficial Loja Doce"

    return {
        "weight_vol": weight_vol,
        "dimensions": dimensions,
        "pack_qty": pack_qty,
        "material": material,
        "flavor_or_color": flavor_or_color,
        "dept_name": dept_name,
        "subcat_name": subcat_name,
        "sku": sku,
        "brand": (brand or "Loja Doce").strip().title(),
    }


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
) -> List[Dict[str, str]]:
    """
    Verticaliza profundamente os 3 Atos, a Ficha Técnica e as Dicas de Conservação
    para cada subtipo de produto da Loja Doce usando os atributos reais extraídos do SKU.
    """
    attrs = extract_lojadoce_attributes(raw_title, formatted_title, brand, category, sku)
    f_low = formatted_title.lower()
    t_up = (raw_title or "").upper()
    b_disp = attrs["brand"]
    wv = attrs["weight_vol"]
    dim = attrs["dimensions"]
    pack = attrs["pack_qty"]
    mat = attrs["material"]
    fc = attrs["flavor_or_color"]

    specs: List[Dict[str, str]] = [
        {"label": "Marca / Fabricante", "value": f"{b_disp} (Produto 100% Original)"},
        {"label": "Código de Referência (SKU)", "value": str(sku or "Consulte no anúncio")},
        {"label": "Departamento / Linha", "value": attrs["subcat_name"]},
    ]
    if wv:
        specs.append({"label": "Peso Líquido / Volume", "value": wv})
    if dim:
        specs.append({"label": "Dimensões / Medidas", "value": dim})
    if pack:
        specs.append({"label": "Apresentação / Quantidade", "value": pack})
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
                f"possui formulação fracionada {fmt_choc} que dispensa o choque térmico (temperagem). "
                f"Basta derreter para obter excelente fluidez, secagem rápida e casquinhas finas, crocantes e brilhantes."
            )
            act2["tag"] = "Rendimento & Aplicações"
            act2["title"] = "IDEAL PARA BANHAR TRUFAS, PÃO DE MEL, CONES, FRUTAS E MOLDAR OVOS"
            act2["desc_tmpl"] = (
                f"Com rendimento superior{f' na embalagem de {wv}' if wv else ''}, proporciona cobertura uniforme sem bolhas "
                f"e excelente contração no molde para desenforme fácil de bombons, cascas recheadas, pirulitos de chocolate e decorações."
            )
            act3["tag"] = f"Padrão Profissional {b_disp}"
            act3["title"] = "SABOR EQUILIBRADO E ESTABILIDADE EM TEMPERATURA AMBIENTE"
            act3["desc_tmpl"] = (
                f"Mantém o brilho e a firmeza da cobertura por muito mais tempo após cristalizada, garantindo segurança "
                f"na exposição em vitrines, encomendas de festas e transporte no delivery."
            )
            specs.append({"label": "Necessita Temperagem?", "value": "Não (Cobertura Fracionada — derreteu, usou)"})
            specs.append({"label": "Uso Recomendado", "value": "Banhos de trufas, pão de mel, cones trufados, bombons e moldes"})
        elif "recheio" in f_low or "nutella" in f_low or "brigadeiro" in f_low or "doce de leite" in f_low:
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
                    "Sua tecnologia forneável suporta altas temperaturas de forno em pizzas, croissants, tortas, churros e folhados sem ressecar e sem escapar da massa."
                    if is_forn else
                    "Pronto para aplicar com saco de confeitar ou espátula em bolos de festa, tortas, copos da felicidade, cones trufados e sobremesas gourmet."
                )
            )
            act2["tag"] = "Produtividade na Cozinha"
            act2["title"] = "PADRONIZAÇÃO DE RECEITAS E ECONOMIA DE TEMPO DE FOGÃO"
            act2["desc_tmpl"] = (
                f"Elimina etapas demoradas de cozimento e garante que todas as suas encomendas tenham exatamente o mesmo padrão "
                f"de ponto, brilho e dulçor{f' com a embalagem de {wv}' if wv else ''}."
            )
        elif "chantilly" in f_low or "chanty" in f_low:
            act1["tag"] = f"Alto Rendimento & Ponto Firme • {b_disp}"
            act1["title"] = "PONTO PERFEITO PARA BICO DE CONFEITAR E ALISAMENTO DE BOLOS"
            act1["desc_tmpl"] = (
                f"Referência absoluta entre confeiteiras, o {{title}} triplica de volume no batimento e atinge textura cremosa, "
                f"porosa zero e altamente estável para espatulagem lisa, rosetas, babados e trabalhos de bico de alta precisão."
            )
            act2["tag"] = "Estabilidade Térmica & Versatilidade"
            act2["title"] = "EXCELENTE RESISTÊNCIA EM BANCADA E ACEITAÇÃO DE CORANTES E SABORIZANTES"
            act2["desc_tmpl"] = (
                "Aceita coloração intensa com corantes em gel sem perder o ponto, além de ser a base ideal para o preparo de "
                "chantininho, mousses aeradas, recheios trufados e coberturas de sobremesas."
            )
            template["care_tips"] = "Conservar em local seco e fresco (não congelar antes de bater). Antes do preparo, resfriar em geladeira entre 4°C e 8°C por pelo menos 12 horas para atingir o rendimento e ponto ideais."
        elif "corante" in f_low or "pó para decoração" in f_low or "po p/decor" in t_up.lower():
            act1["tag"] = f"Alta Pigmentação & Acabamento • {b_disp}"
            act1["title"] = "CORES INTENSAS E FIDELIDADE DE TOM SEM ALTERAR A CONSISTÊNCIA DA RECEITA"
            act1["desc_tmpl"] = (
                f"Formulado com alta concentração de pigmentos alimentícios, o {{title}} atinge tonalidades vivas e uniformes "
                f"utilizando poucas gotas ou gramas, sem desandar o ponto do chantilly, glacê real, pasta americana ou massas."
            )
        elif "desmoldante" in f_low:
            act1["tag"] = f"Liberação Perfeita sem Resíduos • {b_disp}"
            act1["title"] = "DESENFORME IMPECÁVEL DE BOLOS COMPLEXOS SEM USAR FARINHA E MANTEIGA"
            act1["desc_tmpl"] = (
                f"O {{title}} cria uma película antiaderente invisível que solta bolos, pães e tortas até das formas mais trabalhadas "
                f"(como modelos suíços e espirais) sem deixar crosta esbranquiçada de farinha e sem alterar o sabor da massa."
            )

    elif archetype_id == "ld_confeitaria_formas_utensilios":
        if "panetone" in f_low or "forneável" in f_low:
            act1["tag"] = f"Papel Forneável Especial • {b_disp}"
            act1["title"] = "VAI DIRETO AO FORNO SEM UNTAR E VALORIZA A APRESENTAÇÃO DO PANETONE"
            act1["desc_tmpl"] = (
                f"Confeccionada em papel forneável de grau alimentício{f' nas medidas {dim}' if dim else ''}, a {{title}} "
                f"suporta o crescimento e o forneamento da massa com distribuição homogênea de calor e base microperfurada de respiro."
            )
            act2["tag"] = "Do Forno para a Vitrine"
            act2["title"] = "ESTRUTURA FIRME QUE NÃO DEFORMA E DISPENSA DESENFORME"
            act2["desc_tmpl"] = (
                f"Sua parede estruturada mantém o formato cilíndrico clássico durante e após o assamento, permitindo embalar e "
                f"comercializar o produto diretamente na própria forma decorada ({pack})."
            )
        elif "cake board" in f_low or "tabuleiro" in f_low or "disco bolo" in f_low:
            act1["tag"] = f"Sustentação Rígida & Segurança • {b_disp}"
            act1["title"] = "BASE ESTRUTURADA QUE EVITA RACHADURAS NO TRANSPORTE DE BOLOS"
            act1["desc_tmpl"] = (
                f"Projetado para suportar o peso de bolos confeitados e recheados sem envergar, o {{title}} "
                f"{f'com medidas {dim} ' if dim else ''}garante estabilidade total durante a espatulagem na bailarina, refrigeração e entrega."
            )
            act2["tag"] = "Acabamento Branco Higiênico"
            act2["title"] = "SUPERFÍCIE LAMINADA DE FÁCIL LIMPEZA QUE DESTACA A DECORAÇÃO"
            act2["desc_tmpl"] = (
                "Revestimento superior que facilita a limpeza do rodapé do bolo com espátula ou pano úmido após o trabalho de bico, "
                "conferindo apresentação limpa e profissional."
            )
        elif "forminha" in f_low or "fundo para doces" in f_low:
            act1["tag"] = f"Mesa de Doces Impecável • {b_disp}"
            act1["title"] = "ACABAMENTO DELICADO E PADRONIZADO PARA BRIGADEIROS E DOCES FINOS"
            act1["desc_tmpl"] = (
                f"A {{title}} ({pack}) acomoda brigadeiros, beijinhos, camafeus e trufas com elegância e higiene, "
                f"destacando as cores da mesa principal em aniversários, casamentos e encomendas."
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
        if "balão" in f_low or "balao" in f_low:
            is_met = "metalizado" in f_low
            act1["tag"] = f"Balão {'Metalizado de Alto Brilho' if is_met else 'de Látex Profissional'} • {b_disp}"
            act1["title"] = (
                "EFEITO ESPELHADO E VÁLVULA PRÁTICA PARA DECORAÇÃO DE IMPACTO"
                if is_met else
                "ELASTICIDADE SUPERIOR, CORES INTENSAS E ALTA DURABILIDADE EM ARCOS"
            )
            act1["desc_tmpl"] = (
                f"O {{title}} é escolha certeira de decoradores para criar painéis, buquês e arcos desconstruídos. "
                + (
                    "Possui acabamento metalizado refletivo que mantém o formato cheio por longo período com ar ou gás hélio."
                    if is_met else
                    f"Produzido em látex de alta resistência ({pack}) que infla no formato correto, garantindo brilho uniforme e menor índice de estouro."
                )
            )
        elif "fita" in f_low or "fitilho" in f_low or "laço" in f_low:
            act1["tag"] = f"Laços & Acabamentos Decorativos • {b_disp}"
            act1["title"] = "CAIMENTO IMPECÁVEL PARA LAÇOS, ÁRVORES DE NATAL, GUIRLANDAS E EMBALAGENS"
            act1["desc_tmpl"] = (
                f"Com medidas de {dim if dim else 'alto rendimento'}, a {{title}} proporciona acabamento sofisticado "
                + (
                    "com bordas aramadas que permitem moldar laços volumosos que não murcham na decoração natalina ou em cestas."
                    if "aramada" in f_low else
                    "para fechamento de embalagens de confeitaria, panetones, ovos de Páscoa, lembrancinhas e presentes."
                )
            )

    return specs
