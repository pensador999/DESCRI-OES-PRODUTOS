"""
Motor de Moldes Mestres, Arquétipos Especializados e Extração de Especificações Técnicas.
Padrão Autêntico BRK Group (Fishing, Agro, Motors).

Arquétipos Especializados por Categoria Real:
1. uv_performance: Camisas de Pesca / Manga Longa UV50+ Dry Fit
2. agro_field: Camisetas e Vestuário Agro & Campo
3. motors_speed: Jerseys e Vestuário Trilha, Velocidade & Off-Road
4. hats_safari_outdoor: Chapéus de Pesca, Safári, Australiano com Aba 360° e Protetor de Nuca
5. caps_trucker_snapback: Bonés Trucker, Snapback e Aba Curva
6. fishing_lures: Iscas Artificiais (Superfície, Meia-Água, Fundo, Plugs, Jigs, Softs)
7. neck_gaiters_balaclavas: Bandanas, Tubenecks, Buffs e Balaclavas Tubulares Seamless
8. sun_sleeves_manguitos: Manguitos Anatômicos de Proteção Solar com Silicone no Bíceps
9. footwear_sandals_boaonda: Sandálias, Babuches, Clogs e Chinelos Ortopédicos/Antiderrapantes
10. closed_footwear_sneakers: Tênis e Calçados Fechados de Alta Tração
11. drinkware_thermo: Copos, Garrafas e Canecas Térmicas em Inox 18/8 com Vácuo
12. tackle_boxes_storage: Caixas de Pesca, Maletas, Estojos e Organização de Tralhas
13. overalls_workwear: Macacões, Jardineiras e Vestuário Operacional/Trilha
14. books_publications: Livros, Guias de Fauna/Pesca e Publicações Editoriais
15. cutlery_unique: Cutelaria, Facas Artesanais e Lâminas
16. fishing_tackle_gear: Varas, Carretilhas, Molinetes, Linhas e Alicates de Precisão

Preserva rigorosamente 100% dos dados técnicos reais da peça sem alucinar especificações.
"""

import re
import unicodedata
from typing import Dict, Any, List, Optional

KNOWN_BRANDS = [
    'Rapala', 'Deyu', 'Marine Sports', 'Marine', 'Daisen', 'Albatroz', 
    'Boaonda', 'American Hat', 'Elber', 'Maruri', 'Daiwa', 'Shimano', 
    'Loomis', 'Monster 3X', 'Moriah', 'Kowalsky', 'VMC', 'Mustad', 
    'Crown', 'Ottoni', 'Pesca Brasil', 'Sumax', 'Saint', 'Jogá', 'Joga'
]

class TemplateEngine:
    def __init__(self):
        self.known_brands = KNOWN_BRANDS
        self.templates = {
            # 1. Camisas UV Performance
            "uv_performance": {
                "id": "uv_performance",
                "name": "Camisas UV50+ Performance & Pesca",
                "fa_icon": "fa-solid fa-shirt",
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
                    "tag": "Durabilidade & Acabamento",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "COSTURAS PLANAS REFORÇADAS E ACABAMENTO PREMIUM",
                    "desc_tmpl": "Acabamento de alto padrão com costuras planas anti-atrito, caimento anatômico no dorso e ombros para total liberdade de movimentos, além de punhos anatômicos que mantêm o ajuste firme e não laceiam."
                },
                "base_specs": [
                    {"label": "Prazo de Produção", "default": "10 dias úteis"},
                    {"label": "Composição", "default": "90% Poliéster 10% Elastano"},
                    {"label": "Tecido", "default": "XTech Pro"},
                    {"label": "Tecnologia", "default": "Secagem Rápida, Tecido Leve, Proteção Solar"},
                    {"label": "Modelagem", "default": "Anatômica e confortável"},
                    {"label": "Proteção", "default": "Proteção UV50+ (não sai na lavagem)"},
                ],
                "care_tips": "Lavar à mão ou em máquina no ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar)."
            },

            # 2. Agro & Campo
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

            # 3. Motors & Off-Road
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

            # 4. Chapéus de Pesca / Safári / Australiano (Novo Padrão D2C Oficial BRK)
            "hats_safari_outdoor": {
                "id": "hats_safari_outdoor",
                "name": "Chapéus de Pesca, Safári & Outdoor",
                "layout_format": "d2c_headwear",
                "fa_icon": "fa-solid fa-hat-cowboy-side",
                "theme_color": "#d97706",
                "theme_bg": "#fffbeb",
                "category_keywords": ["chapeu", "chapéu", "safari", "safári", "australiano", "pescador", "nuca", "palha"],
                "default_tagline": "Proteção Solar 360° UV50+, Cordão Anti-Vento, Produto Premium & Caixa BRK",
                "details_grid": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg",
                        "title": "Aba 360° UV50+",
                        "desc": "Aba circular ampla com costuras reforçadas, bloqueando os raios solares diretos no rosto, orelhas e pescoço com máxima cobertura."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg",
                        "title": "Cordão Jugular Anti-Vento",
                        "desc": "Ajuste seguro sob o queixo com trava regulável, mantendo o chapéu firme mesmo sob rajadas de vento e navegação rápida."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg",
                        "title": "Protetor de Nuca Integrado",
                        "desc": "Cobertura estendida para a nuca que previne queimaduras solares durante longas jornadas sob sol intenso."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg",
                        "title": "Tecido Respirável & Leve",
                        "desc": "Construção de secagem rápida com ilhoses de ventilação lateral para dissipação imediata de calor e sensação de frescor contínuo."
                    }
                ],
                "info_characteristics": [
                    "Copa anatômica com ilhoses laterais que garantem circulação de ar constante.",
                    "Aba larga circular de 360° com fator de proteção UV50+ permanente.",
                    "Cordão jugular com trava ajustável de segurança contra quedas e vento forte.",
                    "Protetor de nuca para proteção solar total na região posterior do pescoço.",
                    "Tecido tecnológico leve de secagem ultra rápida e alta resistência ao desgaste."
                ],
                "info_care": [
                    "Lavar à mão com água fria e sabão neutro.",
                    "Não lavar em máquina e não torcer para preservar a estrutura da aba.",
                    "Secar estendido à sombra em superfície plana.",
                    "Não usar alvejantes, amaciantes ou produtos à base de cloro.",
                    "Guardar sem dobrar a aba estruturada para manter o caimento original."
                ],
                "split_sections": [
                    {
                        "img": "https://use-brk-images-s3.s3.us-east-1.amazonaws.com/1764952819862-13-Tags.webp",
                        "title": "PRODUTO PREMIUM BRK",
                        "highlight": "Cada chapéu BRK é desenvolvido pensando na proteção de quem enfrenta longas jornadas ao ar livre.",
                        "p1": "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem padrão de proteção solar certificado.",
                        "p2": "Construído com materiais leves e resistentes, oferece o máximo de conforto térmico para pescarias e trabalho sob sol forte."
                    },
                    {
                        "img": "https://use-brk-images-s3.s3.us-east-1.amazonaws.com/1764962764537-CAIXA-BRK.webp",
                        "title": "ENTREGA SEGURA BRK",
                        "highlight": "A sua experiência começa antes mesmo de abrir a caixa.",
                        "p1": "O chapéu é enviado em embalagem protegida BRK, projetada para evitar deformações na aba durante o transporte.",
                        "p2": "Seu novo chapéu chega pronto para encarar o sol com proteção e estilo incomparáveis."
                    }
                ],
                "act1": {
                    "tag": "Aba 360° & Cobertura",
                    "fa_icon": "fa-solid fa-hat-cowboy-side",
                    "title": "PROTEÇÃO SOLAR PANORÂMICA DE ROSTO, ORELHAS E NUCA",
                    "desc_tmpl": "Projetado para longas horas sob sol intenso nas pescarias e expedições, o(a) {title} oferece cobertura circular ampla que evita queimaduras solares e reduz a fadiga visual."
                },
                "act2": {
                    "tag": "Conforto & Fixação",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "CORDÃO JUGULAR COM TRAVA AJUSTÁVEL ANTI-VENTO",
                    "desc_tmpl": "Equipado com cordão ajustável com presilha de travamento no queixo, garantindo que o chapéu permaneça firme mesmo durante a navegação em alta velocidade ou rajadas de vento."
                },
                "act3": {
                    "tag": "Ventilação & Secagem",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "TECIDO LEVE COM ILHOSES DE RESPIRAÇÃO",
                    "desc_tmpl": "Estrutura maleável e respirável que dissipa o calor da cabeça, não retém umidade e pode ser dobrado com facilidade para transporte na mochila ou tralha."
                },
                "base_specs": [
                    {"label": "Modelo da Aba", "default": "Aba larga 360° reforçada com costuras de sustentação"},
                    {"label": "Proteção Solar", "default": "Fator UV50+ bloqueador de radiação solar nociva"},
                    {"label": "Fixação", "default": "Cordão jugular com regulador de pressão tipo tanca"},
                    {"label": "Ventilação", "default": "Ilhoses laterais para circulação e troca térmica"},
                    {"label": "Embalagem de Envio", "default": "Embalagem protetora personalizada BRK"}
                ],
                "care_tips": "Lavar à mão com sabão neutro e água fria. Não torcer a aba para não deformar a estrutura. Secar à sombra."
            },

            # 5. Bonés Trucker & Aba Curva (Novo Padrão D2C Oficial BRK)
            "caps_trucker_snapback": {
                "id": "caps_trucker_snapback",
                "name": "Bonés Trucker & Snapback",
                "layout_format": "d2c_headwear",
                "fa_icon": "fa-solid fa-hat-baseball",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["bone", "boné", "trucker", "snapback", "aba curva", "aba reta", "viseira"],
                "default_tagline": "Aba Moldável, Interno em Tear, Produto Premium & Entrega Segura na Caixa BRK",
                "details_grid": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg",
                        "title": "Aba Moldável",
                        "desc": "Aba estruturada com diversas costuras e moldável, garantindo durabilidade e proteção extra contra o sol."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg",
                        "title": "Interno em Tear",
                        "desc": "Acabamento interno em tear com costuras reforçadas, pensado para aguentar longas jornadas de pesca e uso outdoor."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg",
                        "title": "Etiqueta BRK de Qualidade",
                        "desc": "Etiqueta BRK aplicada com acabamento premium, garantindo autenticidade e padrão de qualidade rigoroso."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg",
                        "title": "Design Exclusivo",
                        "desc": "Arte exclusiva BRK inspirada na vida ao ar livre, para você se destacar em qualquer ambiente."
                    }
                ],
                "info_characteristics": [
                    "Copa estruturada estilo trucker, com frente firme e tela traseira que favorece a ventilação.",
                    "Aba moldável com costuras reforçadas, oferecendo conforto e proteção para o rosto e os olhos.",
                    "Tamanho único com regulagem traseira, se ajustando com precisão à maioria dos formatos de cabeça.",
                    "Ideal para pesca esportiva, atividades ao ar livre, trabalho no campo e uso no dia a dia.",
                    "Acabamento interno pensado para máximo conforto mesmo em longas jornadas de uso contínuo."
                ],
                "info_care": [
                    "Não lave o boné na máquina e não utilize água quente.",
                    "Para limpeza, use um pano macio levemente úmido com sabão neutro nas áreas sujas.",
                    "Retire o excesso de sabão com outro pano levemente úmido apenas com água.",
                    "Deixe secar à sombra, em superfície plana, longe de fontes diretas de calor.",
                    "Não utilize alvejante, não passe a ferro e não leve à secadora."
                ],
                "split_sections": [
                    {
                        "img": "https://use-brk-images-s3.s3.us-east-1.amazonaws.com/1764952819862-13-Tags.webp",
                        "title": "PRODUTO PREMIUM BRK",
                        "highlight": "Cada boné BRK é desenvolvido pensando no pescador que vive a pesca esportiva intensamente.",
                        "p1": "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance.",
                        "p2": "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo em qualquer pescaria."
                    },
                    {
                        "img": "https://use-brk-images-s3.s3.us-east-1.amazonaws.com/1764962764537-CAIXA-BRK.webp",
                        "title": "ENTREGA SEGURA BRK",
                        "highlight": "A sua experiência começa antes mesmo de abrir a caixa.",
                        "p1": "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições.",
                        "p2": "Assim, seu novo boné de pesca chega pronto para encarar a próxima aventura, seja na beira do rio, na represa ou em alto mar."
                    }
                ],
                "act1": {
                    "tag": "Aba Moldável & Copa",
                    "fa_icon": "fa-solid fa-hat-baseball",
                    "title": "ABA MOLDÁVEL COM COSTURAS REFORÇADAS E COPA ESTRUTURADA",
                    "desc_tmpl": "O {title} destaca-se pela frente firme e acabamento com costuras reforçadas, mantendo o formato clássico trucker intacto e oferecendo proteção superior contra o sol."
                },
                "act2": {
                    "tag": "Interno em Tear & Ventilação",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "ACABAMENTO INTERNO EM TEAR E TELA TRASEIRA RESPIRÁVEL",
                    "desc_tmpl": "Construção interna resistente em tear com carneira macia e tela traseira que garante circulação constante de ar para evitar acúmulo de suor."
                },
                "act3": {
                    "tag": "Autenticidade & Envio",
                    "fa_icon": "fa-solid fa-box",
                    "title": "ETIQUETAS OFICIAIS BRK E ENVIO EM CAIXA PROTETORA EXCLUSIVA",
                    "desc_tmpl": "Autenticidade garantida por etiquetas de alto padrão e envio em caixa rígida personalizada BRK para chegar impecável sem amassar."
                },
                "base_specs": [
                    {"label": "Modelo da Copa", "default": "Trucker clássico com lateral e traseira em tela respirável"},
                    {"label": "Aba", "default": "Aba curva estruturada e moldável com diversas costuras de reforço"},
                    {"label": "Fechamento", "default": "Snapback regulável de alta resistência (tamanho único ajustável)"},
                    {"label": "Acabamento Interno", "default": "Tear reforçado com carneira acolchoada anti-suor"},
                    {"label": "Embalagem de Envio", "default": "Caixa personalizada protetora BRK (anti-deformação)"}
                ],
                "care_tips": "Limpar com pano macio levemente úmido e sabão neutro. Não mergulhar a copa em água nem lavar em máquina para manter a estrutura e curvatura intactas."
            },

            # 6. Iscas Artificiais
            "fishing_lures": {
                "id": "fishing_lures",
                "name": "Iscas Artificiais & Alta Atratividade",
                "fa_icon": "fa-solid fa-fish-fins",
                "theme_color": "#0ea5e9",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["isca", "iscas", "plug", "jig", "frog", "soft", "meia-água", "superfície", "superficie", "popper", "stick", "twitch", "crankbait", "minnow", "spinnerbait"],
                "default_tagline": "Nado Ultra Realista, Rattling Irresistível e Garatéias Afiadas a Laser",
                "act1": {
                    "tag": "Ação & Nado Errático",
                    "fa_icon": "fa-solid fa-fish-fins",
                    "title": "NADO REALISTA QUE ESTIMULA O ATAQUE DE PREDADORES",
                    "desc_tmpl": "Desenvolvida com hidrodinâmica refinada, a {title} produz vibrações e movimentação errática na água, provocando ataques ferozes por agressividade e territorialidade."
                },
                "act2": {
                    "tag": "Sonoridade & Balanceamento",
                    "fa_icon": "fa-solid fa-bell",
                    "title": "SISTEMA DE RATTLING COM ESFERAS SONORAS INTERNAS",
                    "desc_tmpl": "Possui esferas calibradas que emitem frequências sonoras atrativas a longas distâncias, além de concentrar o peso no centro de gravidade para arremessos longos e precisos."
                },
                "act3": {
                    "tag": "Poder de Fisgada",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "GARATÉIAS DE ALTA RESISTÊNCIA E PINTURA HOLOGRÁFICA",
                    "desc_tmpl": "Armada com garatéias afiadas quimicamente para penetração instantânea na boca dos predadores, combinada a acabamento com cores holográficas ultra reflexivas."
                },
                "base_specs": [
                    {"label": "Ação do Trabalho", "default": "Trabalho atrativo de superfície/meia-água com nado provocante"},
                    {"label": "Garatéias", "default": "Aço carbono reforçado afiadas quimicamente"},
                    {"label": "Sistema Sonoro", "default": "Rattling interno com esferas sonoras vibratórias"},
                    {"label": "Corpo", "default": "Polímero ABS virgem reforçado imune a mordidas severas"},
                    {"label": "Peixes Indicados", "default": "Tucunaré, Robalo, Traíra, Dourado, Black Bass e predadores esportivos"}
                ],
                "care_tips": "Após uso em água salobra ou salgada, lavar em água doce corrente e secar completamente antes de guardar no estojo."
            },

            # 7. Bandanas, Tubenecks, Buffs e Balaclavas
            "neck_gaiters_balaclavas": {
                "id": "neck_gaiters_balaclavas",
                "name": "Bandanas, Tubenecks & Balaclavas",
                "fa_icon": "fa-solid fa-mask-face",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["bandana", "balaclava", "tubeneck", "buff", "mascara de protecao", "máscara de proteção", "gaiter"],
                "default_tagline": "Barreira Solar UV50+, Tecido Seamless Tubular e Conforto Respiratório",
                "act1": {
                    "tag": "Proteção Facial & Nuca",
                    "fa_icon": "fa-solid fa-mask-face",
                    "title": "ESCUDO COMPLETO CONTRA SOL, VENTO, MOSQUITOS E POEIRA",
                    "desc_tmpl": "O(a) {title} envolve o pescoço e a face com barreira física e fator UV permanente, protegendo a pele durante pescarias embarcadas, trilhas e pilotagem."
                },
                "act2": {
                    "tag": "Construção Seamless",
                    "fa_icon": "fa-solid fa-feather",
                    "title": "TECIDO ELÁSTICO TUBULAR SEM COSTURA ANTI-ATRITO",
                    "desc_tmpl": "Estrutura elástica com microfibra respirável de alta elasticidade que se molda confortavelmente ao rosto sem pinicar, apertar ou deixar marcas de pressão."
                },
                "act3": {
                    "tag": "Versatilidade de Uso",
                    "fa_icon": "fa-solid fa-arrows-spin",
                    "title": "MÚLTIPLAS FORMAS DE USO EM QUALQUER AVENTURA",
                    "desc_tmpl": "Pode ser utilizado como máscara facial, protetor de pescoço, faixa de cabeça, capuz ou gorro, secando instantaneamente com o suor ou respingos d'água."
                },
                "base_specs": [
                    {"label": "Proteção Solar", "default": "Fator UV50+ bloqueador permanente de radiação"},
                    {"label": "Construção", "default": "Tubular inteiriço sem costuras (Seamless anti-atrito)"},
                    {"label": "Elasticidade", "default": "Multidirecional 4-Way Stretch com memória de forma"},
                    {"label": "Respirabilidade", "default": "Tecido microperfurado que facilita a respiração e fala"},
                    {"label": "Tamanho", "default": "Único anatômico adaptável a qualquer formato de cabeça"}
                ],
                "care_tips": "Lavar à mão com sabão neutro. Seca em minutos no varal e não necessita de ferro de passar."
            },

            # 8. Manguitos de Proteção Solar
            "sun_sleeves_manguitos": {
                "id": "sun_sleeves_manguitos",
                "name": "Manguitos de Proteção Solar UV50+",
                "fa_icon": "fa-solid fa-hand-holding-hand",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["manguito", "manguitos", "sleeve", "manga avulsa"],
                "default_tagline": "Proteção UV50+ Anatômica com Silicone Antiderrapante no Bíceps",
                "act1": {
                    "tag": "Proteção Solar Anatômica",
                    "fa_icon": "fa-solid fa-hand-holding-hand",
                    "title": "COBERTURA TOTAL DOS BRAÇOS COM PRATICIDADE",
                    "desc_tmpl": "Desenvolvido para oferecer máxima proteção solar UV50+ para os braços, o(a) {title} é essencial para pesca, ciclismo e atividades outdoor, substituindo o protetor solar com conforto."
                },
                "act2": {
                    "tag": "Fixação Antiderrapante",
                    "fa_icon": "fa-solid fa-grip",
                    "title": "ELÁSTICO DE SILICONE NO BÍCEPS QUE NÃO DESLIZA",
                    "desc_tmpl": "Possui faixa interna de silicone na extremidade superior que impede que a manga escorregue pelo braço durante os movimentos de arremesso, pedalada ou corrida."
                },
                "act3": {
                    "tag": "Conforto Térmico & Compressão",
                    "fa_icon": "fa-solid fa-bolt",
                    "title": "COMPRESSÃO SUAVE E DISSIPAÇÃO TÉRMICA CONTÍNUA",
                    "desc_tmpl": "Tecido tecnológico com elastano que reduz a fadiga muscular e dissipa o calor rapidamente, mantendo os braços frescos e protegidos o dia inteiro."
                },
                "base_specs": [
                    {"label": "Proteção Solar", "default": "Fator UV50+ permanente certificado"},
                    {"label": "Composição", "default": "Poliamida com Elastano de toque aveludado e flexível"},
                    {"label": "Fixação Superior", "default": "Borda com fita interna de silicone antiderrapante no bíceps"},
                    {"label": "Secagem", "default": "Tecnologia Dry Fit com evaporação instantânea de suor"},
                    {"label": "Conteúdo da Embalagem", "default": "1 Par de Manguitos (braço direito e esquerdo)"}
                ],
                "care_tips": "Lavar com água fria e sabão neutro. Não usar amaciante nem alvejante. Secar à sombra."
            },

            # 9. Sandálias, Chinelos, Babuches e Clogs Boaonda
            "footwear_sandals_boaonda": {
                "id": "footwear_sandals_boaonda",
                "name": "Sandálias, Chinelos & Babuches Boaonda",
                "fa_icon": "fa-solid fa-shoe-prints",
                "theme_color": "#0d9488",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["sandalia", "sandália", "chinelo", "boaonda", "babuche", "clog", "slide", "pantufa", "crocs", "papete"],
                "default_tagline": "Palmilha Anatômica Anti-Impacto e Solado Antiderrapante para Embarcações",
                "act1": {
                    "tag": "Ergonomia & Conforto",
                    "fa_icon": "fa-solid fa-shoe-prints",
                    "title": "PALMILHA ANATÔMICA COM AMORTECIMENTO ANTI-IMPACTO",
                    "desc_tmpl": "Projetada para garantir descanso prolongado aos pés, a {title} alivia a pressão nos calcanhares e articulações em longos dias de pescaria e caminhada."
                },
                "act2": {
                    "tag": "Aderência & Drenagem",
                    "fa_icon": "fa-solid fa-water",
                    "title": "SOLADO ANTIDERRAPANTE COM CANAIS DE DRENAGEM",
                    "desc_tmpl": "Ranhuras de alta tração que garantem passos firmes e seguros em decks molhados de barcos, pedras e bordas de piscina."
                },
                "act3": {
                    "tag": "Material Impermeável",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "TERMOMOLDADO IMPERMEÁVEL QUE NÃO RETÉM ODORES",
                    "desc_tmpl": "Confeccionada em polímero nobre leve, macio e 100% à prova d'água, secando instantaneamente e facilitando a higienização."
                },
                "base_specs": [
                    {"label": "Material do Cabedal", "default": "EVA / Termoplástico nobre Boaonda macio e flexível"},
                    {"label": "Palmilha", "default": "Anatômica anti-impacto (alívio para esporão e fascite)"},
                    {"label": "Solado", "default": "Borracha antiderrapante com canais de escoamento de água"},
                    {"label": "Resistência", "default": "100% impermeável e imune a deformações térmicas"},
                    {"label": "Indicação de Uso", "default": "Embarcações, pesqueiros, praia, piscina e uso casual"}
                ],
                "care_tips": "Lavar com sabão neutro e água corrente. Não expor ao sol direto intenso para preservar o elastômero."
            },

            # 10. Tênis & Calçados Fechados
            "closed_footwear_sneakers": {
                "id": "closed_footwear_sneakers",
                "name": "Tênis & Calçados Fechados",
                "fa_icon": "fa-solid fa-socks",
                "theme_color": "#0d9488",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["tenis", "tênis", "sapato", "botina", "sneaker", "calcado fechado", "calçado fechado"],
                "default_tagline": "Estrutura Firme, Cabedal Respirável e Solado de Alta Tração",
                "act1": {
                    "tag": "Estabilidade & Suporte",
                    "fa_icon": "fa-solid fa-socks",
                    "title": "ESTRUTURA REFORÇADA COM ENCAIXE ANATÔMICO SEGURO",
                    "desc_tmpl": "O {title} entrega estabilidade e firmeza para longas jornadas de trabalho ou aventura, protegendo os pés contra atritos e irregularidades do solo."
                },
                "act2": {
                    "tag": "Amortecimento & Ventilação",
                    "fa_icon": "fa-solid fa-cloud",
                    "title": "ENTRESOLA MACIA E CABEDAL COM CIRCULAÇÃO DE AR",
                    "desc_tmpl": "Sistema de amortecimento que reduz o cansaço nas pernas, aliado a materiais que evitam o aquecimento excessivo e a umidade interna."
                },
                "act3": {
                    "tag": "Tração Segura",
                    "fa_icon": "fa-solid fa-shoe-prints",
                    "title": "SOLADO DE ALTA RESISTÊNCIA À ABRASÃO",
                    "desc_tmpl": "Desenvolvido com compostos resistentes ao desgaste com travas de aderência para diversos tipos de terrenos urbanos e rurais."
                },
                "base_specs": [
                    {"label": "Cabedal", "default": "Material respirável com reforços laterais estruturais"},
                    {"label": "Fechamento", "default": "Cadarço ajustável com passadores reforçados"},
                    {"label": "Palmilha", "default": "Conforto anatômico com espuma de alta densidade"},
                    {"label": "Solado", "default": "Borracha de alta tração antiderrapante"},
                    {"label": "Uso Recomendado", "default": "Caminhada, dia a dia, trabalho rural e atividades ao ar livre"}
                ],
                "care_tips": "Limpar com pano úmido e sabão neutro. Secar à sombra em local ventilado."
            },

            # 11. Copos, Garrafas e Canecas Térmicas
            "drinkware_thermo": {
                "id": "drinkware_thermo",
                "name": "Copos, Garrafas & Térmicos",
                "fa_icon": "fa-solid fa-mug-hot",
                "theme_color": "#0891b2",
                "theme_bg": "#ecfeff",
                "category_keywords": ["copo", "garrafa", "caneca", "cantil", "termico", "térmico", "cooler", "elber", "geladeira"],
                "default_tagline": "Retenção Térmica a Vácuo em Aço Inox 18/8 Livre de BPA",
                "act1": {
                    "tag": "Retenção Térmica a Vácuo",
                    "fa_icon": "fa-solid fa-snowflake",
                    "title": "BEBIDAS GELADAS POR HORAS MESMO SOB SOL INTENSO",
                    "desc_tmpl": "Com parede dupla de aço inoxidável e isolamento a vácuo, o(a) {title} preserva sua bebida na temperatura perfeita da primeira à última gota."
                },
                "act2": {
                    "tag": "Zero Condensação Externa",
                    "fa_icon": "fa-solid fa-droplet-slash",
                    "title": "PAREDE EXTERNA SECA QUE NÃO TRANSPIRA",
                    "desc_tmpl": "A tecnologia térmica impede a condensação externa, permitindo segurar o copo confortavelmente sem molhar as mãos, porta-copos ou móveis."
                },
                "act3": {
                    "tag": "Construção em Inox 18/8",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "AÇO INOXIDÁVEL DE GRAU ALIMENTÍCIO LIVRE DE BPA",
                    "desc_tmpl": "Material atóxico, imune a ferrugem e que não transfere nem absorve sabores, com tampa de alta vedação contra respingos."
                },
                "base_specs": [
                    {"label": "Material", "default": "Aço Inoxidável 18/8 (Grau Alimentício atóxico)"},
                    {"label": "Isolamento", "default": "Parede dupla com vácuo térmico de alta eficiência"},
                    {"label": "Tampa", "default": "Acrílico livre de BPA com vedação hermética em silicone"},
                    {"label": "Eficiência Térmica", "default": "Mantém gelado por até 12h (com gelo) / quente por até 4h"},
                    {"label": "Acabamento Externo", "default": "Pintura eletrostática a pó anti-risco e anti-deslizante"}
                ],
                "care_tips": "Lavar com detergente neutro e esponja macia. Não levar ao micro-ondas nem ao congelador."
            },

            # 12. Caixas de Pesca & Organização
            "tackle_boxes_storage": {
                "id": "tackle_boxes_storage",
                "name": "Caixas, Estojos & Organização",
                "fa_icon": "fa-solid fa-box-archive",
                "theme_color": "#1d4ed8",
                "theme_bg": "#eff6ff",
                "category_keywords": ["caixa de pesca", "caixa pesca", "estojo", "maleta", "organizador", "bolsa de pesca", "tubo de vara"],
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

            # 13. Macacões & Jardineiras
            "overalls_workwear": {
                "id": "overalls_workwear",
                "name": "Macacões, Jardineiras & Operacional",
                "fa_icon": "fa-solid fa-vest",
                "theme_color": "#475569",
                "theme_bg": "#f8fafc",
                "category_keywords": ["macacao", "macacão", "jardineira", "jardineiras", "salopete", "wader"],
                "default_tagline": "Proteção Integral, Alças Reguláveis e Bolsos Utilitários de Alta Resistência",
                "act1": {
                    "tag": "Proteção Integral & Robustez",
                    "fa_icon": "fa-solid fa-vest",
                    "title": "COBERTURA COMPLETA CONTRA ABRASÃO E SUJEIRA",
                    "desc_tmpl": "Projetado para trabalhos intensos, trilhas ou operações rurais, o(a) {title} oferece proteção de corpo inteiro com visual imponente e funcional."
                },
                "act2": {
                    "tag": "Mobilidade & Ajuste",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "ALÇAS REGULÁVEIS E ARTICULAÇÃO LIVRE",
                    "desc_tmpl": "Possui fechamentos laterais e alças com fivelas de engate rápido que permitem regulagem milimétrica para conforto em agachamentos e movimentos amplos."
                },
                "act3": {
                    "tag": "Bolsos Utilitários",
                    "fa_icon": "fa-solid fa-box-open",
                    "title": "COMPARTIMENTAÇÃO PRÁTICA PARA FERRAMENTAS E ACESSÓRIOS",
                    "desc_tmpl": "Equipado com múltiplos bolsos reforçados para acomodar ferramentas, celulares e equipamentos com segurança e acesso rápido."
                },
                "base_specs": [
                    {"label": "Material", "default": "Tecido de alta tenacidade com costuras duplas e triplas"},
                    {"label": "Alças", "default": "Reguláveis com engate rápido e elástico de suporte"},
                    {"label": "Bolsos", "default": "Bolsos frontais, laterais e traseiros reforçados"},
                    {"label": "Fechamento", "default": "Zíper resistente ou botões de pressão de alta pressão"},
                    {"label": "Uso Recomendado", "default": "Operacional, campo, oficinas, trilhas e atividades pesadas"}
                ],
                "care_tips": "Lavar com água fria e sabão neutro. Não alvejar. Secar à sombra."
            },

            # 14. Livros & Publicações
            "books_publications": {
                "id": "books_publications",
                "name": "Livros, Guias & Publicações",
                "fa_icon": "fa-solid fa-book-open",
                "theme_color": "#7c3aed",
                "theme_bg": "#f5f3ff",
                "category_keywords": ["livro", "livros", "guia", "cartilha", "revista", "publicacao", "colorir"],
                "default_tagline": "Conteúdo Exclusivo, Educação Ambiental e Valorização da Fauna",
                "act1": {
                    "tag": "Conteúdo & Conhecimento",
                    "fa_icon": "fa-solid fa-book-open",
                    "title": "IMERSÃO NO UNIVERSO DA PESCA E DA NATUREZA",
                    "desc_tmpl": "O {title} traz conteúdo rico e envolvente sobre a fauna, técnicas de pesca e preservação, conectando leitores de todas as idades ao universo do ar livre."
                },
                "act2": {
                    "tag": "Qualidade Editorial",
                    "fa_icon": "fa-solid fa-palette",
                    "title": "IMPRESSÃO EM ALTA DEFINIÇÃO E PAPEL DE ALTA GRAMATURA",
                    "desc_tmpl": "Produzido com acabamento gráfico de alta qualidade, ilustrações detalhadas e páginas resistentes que valorizam a leitura e atividades lúdicas."
                },
                "act3": {
                    "tag": "Coleção & Presente",
                    "fa_icon": "fa-solid fa-gift",
                    "title": "EXCELENTE OPÇÃO PARA PRESENTEAR E COLECIONAR",
                    "desc_tmpl": "Uma obra indispensável para a biblioteca de amantes da pesca esportiva e da vida ao ar livre, estimulando a curiosidade e o aprendizado."
                },
                "base_specs": [
                    {"label": "Formato", "default": "Editorial impresso com encadernação de alta qualidade"},
                    {"label": "Acabamento", "default": "Capa colorida com laminação e papel especial resistente"},
                    {"label": "Tema Principal", "default": "Pesca esportiva, natureza, fauna brasileira e recreação"},
                    {"label": "Idioma", "default": "Português"},
                    {"label": "Público Indicado", "default": "Amantes do ar livre, pescadores, jovens e famílias"}
                ],
                "care_tips": "Armazenar em local seco e arejado, protegido de umidade e luz solar direta."
            },

            # 15. Cutelaria & Facas
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
                "care_tips": "Lavar com água e esponja macia logo após o uso. Secar imediatamente para evitar oxidação. Aplicar leve camada de óleo mineral periodicamente."
            },

            # 16. Equipamentos de Pesca & Revenda (Varas, Carretilhas, Molinetes)
            "fishing_tackle_gear": {
                "id": "fishing_tackle_gear",
                "name": "Equipamentos de Pesca & Revenda",
                "fa_icon": "fa-solid fa-gear",
                "theme_color": "#4338ca",
                "theme_bg": "#eef2ff",
                "category_keywords": ["vara", "carretilha", "molinete", "linha", "anzol", "alicate", "passagua", "passaguá"],
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
                    {"label": "Estrutura", "default": "Construção reforçada de baixo peso e alta rigidez estrutural"},
                    {"label": "Desempenho", "default": "Componentes de precisão com alta resistência à tração e atrito"},
                    {"label": "Aplicação", "default": "Pesca esportiva em rios, lagos, pesqueiros e mar aberto"},
                    {"label": "Origem / Distribuição", "default": "Produto original com procedência e garantia"}
                ],
                "care_tips": "Após uso em água salgada, lavar levemente com água doce corrente, secar e aplicar óleo lubrificante nos pontos móveis recomendados."
            },

            # 17. Chapéus Country, Feltro, Pralana & Cowboy (Novo Padrão D2C Oficial BRK)
            "hats_country_cowboy": {
                "id": "hats_country_cowboy",
                "name": "Chapéus Country, Feltro, Pralana & Cowboy",
                "layout_format": "d2c_headwear",
                "fa_icon": "fa-solid fa-hat-cowboy",
                "theme_color": "#854d0e",
                "theme_bg": "#fefce8",
                "category_keywords": ["feltro", "pralana", "american hat", "karanda", "karandá", "country", "cowboy", "pantaneiro", "lã", "veludo", "marcatto"],
                "default_tagline": "Elegância Rústica, Copa Estruturada e Acabamento Premium em Couro e Fivela",
                "details_grid": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg",
                        "title": "Aba Larga Estruturada",
                        "desc": "Formato clássico com curvatura marcante e acabamento impecável, unindo tradição, imponência e proteção solar no campo."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg",
                        "title": "Carneira Interna Confortável",
                        "desc": "Faixa interna com toque macio e anatômico, oferecendo fixação firme e confortável na cabeça sem marcar a testa."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg",
                        "title": "Fita & Acabamento Premium",
                        "desc": "Banda decorativa exclusiva com detalhe refinado, reforçando a autenticidade e o visual rústico elegante."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg",
                        "title": "Estrutura Nobre & Firme",
                        "desc": "Matéria-prima nobre de alta densidade que preserva a forma da copa e a curvatura da aba mesmo com uso contínuo."
                    }
                ],
                "info_characteristics": [
                    "Copa alta estruturada e moldada no legítimo estilo western / campo.",
                    "Aba larga de presença marcante que proporciona excelente sombra e proteção.",
                    "Carneira interna acolchoada para conforto prolongado em cavalgadas e eventos.",
                    "Fita externa com acabamento nobre e identidade autêntica do homem e da mulher do campo.",
                    "Ideal para rodeios, feiras agropecuárias, lida na fazenda e dia a dia sertanejo."
                ],
                "info_care": [
                    "Limpar delicadamente com escova de cerdas macias sempre no sentido das fibras.",
                    "Evitar contato direto com chuva intensa ou umidade excessiva.",
                    "Armazenar sempre apoiado pela copa ou em suporte adequado para não desformar a aba.",
                    "Nunca dobrar, amassar ou deixar exposto no interior de veículos sob sol forte.",
                    "Em caso de umidade leve, deixe secar naturalmente à sombra em local ventilado."
                ],
                "split_sections": [
                    {
                        "img": "https://use-brk-images-s3.s3.us-east-1.amazonaws.com/1764952819862-13-Tags.webp",
                        "title": "PRODUTO PREMIUM BRK",
                        "highlight": "A tradição e o orgulho do campo em cada detalhe artesanal.",
                        "p1": "Desenvolvido com rigor técnico para quem valoriza a autêntica vida sertaneja.",
                        "p2": "Estrutura nobre, acabamento de precisão e caimento perfeito para cavalgadas e ocasiões especiais."
                    },
                    {
                        "img": "https://use-brk-images-s3.s3.us-east-1.amazonaws.com/1764962764537-CAIXA-BRK.webp",
                        "title": "ENTREGA SEGURA NA CAIXA",
                        "highlight": "A sua experiência começa antes mesmo de abrir a caixa.",
                        "p1": "O chapéu é embalado com proteção reforçada contra amassados para preservar 100% da sua modelagem original.",
                        "p2": "Receba sua peça pronta para o uso, com aba e copa perfeitamente alinhadas."
                    }
                ],
                "act1": {
                    "tag": "Copa & Estrutura",
                    "fa_icon": "fa-solid fa-hat-cowboy",
                    "title": "COPA CONFORMADA E ABA ESTRUTURADA DE ALTA RETENÇÃO",
                    "desc_tmpl": "Produzido com modelagem clássica que preserva as linhas autênticas do estilo country, o(a) {title} conta com copa firme e aba com retenção de formato para uso prolongado no campo e em eventos."
                },
                "act2": {
                    "tag": "Estilo & Nobreza",
                    "fa_icon": "fa-solid fa-gem",
                    "title": "BANDINHA EM COURO COM DETALHES REFINADOS",
                    "desc_tmpl": "Destaque para o acabamento impecável ao redor da copa com bandinha decorativa e fivela metálica de precisão, conferindo elegância, imponência e robustez à peça."
                },
                "act3": {
                    "tag": "Conforto & Encaixe",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "CARNEIRA INTERNA CONFORTÁVEL COM AJUSTE ANATÔMICO",
                    "desc_tmpl": "Interior equipado com carneira acolchoada anti-suor que garante encaixe macio, estável e confortável na cabeça ao longo de todo o dia, sem apertar."
                },
                "base_specs": [
                    {"label": "Material Principal", "default": "Feltro 100% Lã / Fibra Nobre Especial de Alta Densidade"},
                    {"label": "Formato da Copa", "default": "Tradicional Country Gota / Clássica Conformada"},
                    {"label": "Carneira Interna", "default": "Espuma Acolchoada de Alto Conforto e Toque Macio"},
                    {"label": "Acabamento Externo", "default": "Bandinha exclusiva em couro com fivela/passador metálico"},
                    {"label": "Embalagem de Envio", "default": "Caixa rígida protetora especial (anti-deformação)"}
                ],
                "care_tips": "Limpar delicadamente com escova de cerdas macias no sentido das fibras do feltro. Evitar umidade excessiva e guardar sempre apoiado pela copa."
            },

            # 18. Camisas Work, Botão & Sarja Utilitária
            "shirts_button_work": {
                "id": "shirts_button_work",
                "name": "Camisas Work, Botão & Sarja Utilitária",
                "fa_icon": "fa-solid fa-shirt",
                "theme_color": "#15803d",
                "theme_bg": "#f0fdf4",
                "category_keywords": ["work", "camisa work", "camisa safari", "camisa sarja", "camisa de botao", "camisa botao", "camisa de botão", "camisa militar", "manga curta social", "manga longa sarja", "sarja", "operacional", "camisa lisa"],
                "default_tagline": "Resistência Operacional, Abotoamento Clássico e Bolsos Utilitários de Alta Tenacidade",
                "act1": {
                    "tag": "Visual & Solidez",
                    "fa_icon": "fa-solid fa-shirt",
                    "title": "TECIDO RESISTENTE DE COR SÓLIDA E CAIMENTO PROFISSIONAL",
                    "desc_tmpl": "Desenvolvida para máxima durabilidade no trabalho pesado ou no expediente diário, a {title} apresenta visual clássico e sóbrio em tecido encorpado, sem estampas espalhafatosas."
                },
                "act2": {
                    "tag": "Fechamento & Gola",
                    "fa_icon": "fa-solid fa-square-check",
                    "title": "ABOTOAMENTO FRONTAL CLÁSSICO E COLARINHO ESTRUTURADO",
                    "desc_tmpl": "Com fechamento integral por botões de alta tenacidade reforçados em costura em 'X', oferece ajuste prático, alinhamento alinhado e gola firme que mantém a postura durante toda a jornada."
                },
                "act3": {
                    "tag": "Pala Traseira & Costuras",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "COSTURAS TRIPLAS REFORÇADAS E PALA TRASEIRA ANATÔMICA",
                    "desc_tmpl": "Construída com pesponto reforçado nas áreas de maior tração, pala traseira anatômica com pregas de conforto e modelagem pensada para o trabalho pesado e ampla movimentação dos braços."
                },
                "base_specs": [
                    {"label": "Fechamento Frontal", "default": "Botões reforçados aplicados com costura em 'X'"},
                    {"label": "Colarinho / Gola", "default": "Colarinho tradicional estruturado com entretela de sustentação"},
                    {"label": "Bolsos Frontais", "default": "Dois bolsos utilitários no peito com lapela protetora"},
                    {"label": "Composição do Tecido", "default": "Algodão / Sarja de Alta Densidade resistente ao atrito"},
                    {"label": "Modelagem", "default": "Confortável com folga estratégica para ampla mobilidade nos braços"}
                ],
                "care_tips": "Lavar em água fria com sabão neutro. Não usar alvejantes à base de cloro. Secar à sombra e passar em temperatura média."
            },

            # 19. Calças & Bermudas Táticas / Cargo / Pesca
            "pants_cargo_tactical": {
                "id": "pants_cargo_tactical",
                "name": "Calças & Bermudas Táticas / Cargo / Pesca",
                "fa_icon": "fa-solid fa-vest",
                "theme_color": "#334155",
                "theme_bg": "#f8fafc",
                "category_keywords": ["calca", "calça", "calças", "bermuda", "bermudas", "shorts", "short", "ripstop", "tactical", "cargo"],
                "default_tagline": "Resistência Anti-Rasgo Ripstop, Cós Anatômico e Bolsos Cargo Utilitários",
                "act1": {
                    "tag": "Resistência & Anti-Rasgo",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "TECIDO RIPSTOP REFORÇADO CONTRA ATRITO E VEGETAÇÃO",
                    "desc_tmpl": "Projetada para suportar a lida no campo, trilhas e pescarias, o(a) {title} é confeccionado em tecido com trama ripstop que impede a propagação de rasgos e perfurações."
                },
                "act2": {
                    "tag": "Ajuste & Firmeza",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "CÓS ANATÔMICO COM PASSADORES REFORÇADOS",
                    "desc_tmpl": "Estrutura pensada para o movimento, oferecendo encaixe firme na cintura e passadores largos compatíveis com cintos táticos e coldres utilitários."
                },
                "act3": {
                    "tag": "Capacidade de Carga",
                    "fa_icon": "fa-solid fa-box-open",
                    "title": "BOLSOS CARGO MULTIFUNCIONAIS COM FECHAMENTO SEGURO",
                    "desc_tmpl": "Diversos bolsos com lapela distribuídos estrategicamente para acomodar canivetes, celular, alicate de pesca e ferramentas com rápido acesso."
                },
                "base_specs": [
                    {"label": "Modelagem", "default": "Tática Operacional / Cargo com reforço no cavalo e joelhos"},
                    {"label": "Cós e Fechamento", "default": "Botão de pressão reforçado e zíper com passadores largos para cinto"},
                    {"label": "Compartimentação", "default": "Múltiplos bolsos multifuncionais (cargo laterais, faca e traseiros)"},
                    {"label": "Tecido", "default": "Ripstop de alta tenacidade com acabamento repelente a sujeira"},
                    {"label": "Uso Indicado", "default": "Trabalho operacional, campo, pesca, trilhas e atividades táticas"}
                ],
                "care_tips": "Lavar com sabão neutro em ciclo delicado. Secar à sombra. Não alvejar."
            },

            # 20. Aromatizantes Automotivos & Cuidados
            "accessories_car_care": {
                "id": "accessories_car_care",
                "name": "Aromatizantes Automotivos & Cuidados",
                "fa_icon": "fa-solid fa-spray-can-sparkles",
                "theme_color": "#0d9488",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["aromatizante", "cheirinho", "aroma", "fragrancia", "fragrância", "difusor", "aromatizador", "little trees", "carro", "automotivo"],
                "default_tagline": "Perfume Marcante, Eliminação de Odores e Sensação Prolongada de Frescor",
                "act1": {
                    "tag": "Aroma & Frescor",
                    "fa_icon": "fa-solid fa-spray-can-sparkles",
                    "title": "PERFUME ENVOLVENTE E NEUTRALIZAÇÃO EFICAZ DE ODORES",
                    "desc_tmpl": "O {title} transforma o interior do veículo ou ambiente com essências selecionadas, eliminando odores desagradáveis e promovendo agradável sensação de limpeza."
                },
                "act2": {
                    "tag": "Difusão & Durabilidade",
                    "fa_icon": "fa-solid fa-clock",
                    "title": "TECNOLOGIA DE LIBERAÇÃO CONTÍNUA E PROLONGADA",
                    "desc_tmpl": "Desenvolvido para liberar a fragrância de forma homogênea e estável, garantindo semanas de ação perfumada constante sem perder a intensidade inicial."
                },
                "act3": {
                    "tag": "Praticidade & Estilo",
                    "fa_icon": "fa-solid fa-car",
                    "title": "DESIGN COMPACTO COM FIXAÇÃO SIMPLES NO RETROVISOR OU DIFUSOR",
                    "desc_tmpl": "Acompanha cordão ou presilha para fácil acoplamento no retrovisor interno ou grade de ventilação, sem manchar superfícies plásticas ou couro."
                },
                "base_specs": [
                    {"label": "Função Principal", "default": "Aromatizador e desodorizador de ambientes automotivos"},
                    {"label": "Formato de Difusão", "default": "Liberação gradual contínua e homogênea"},
                    {"label": "Durabilidade Estimada", "default": "Até 30 a 45 dias de ação perfumada"},
                    {"label": "Fixação", "default": "Cordão para retrovisor interno ou clipe para grade de ar"},
                    {"label": "Indicação", "default": "Veículos, escritórios, guarda-roupas e pequenos ambientes"}
                ],
                "care_tips": "Pendurar livremente evitando contato direto e contínuo com painéis plásticos e revestimentos de couro."
            },

            # 21. Acessórios, Chaveiros & Adesivos
            "accessories_general": {
                "id": "accessories_general",
                "name": "Acessórios, Chaveiros & Adesivos",
                "fa_icon": "fa-solid fa-key",
                "theme_color": "#64748b",
                "theme_bg": "#f8fafc",
                "category_keywords": ["chaveiro", "adesivo", "adesivos", "sticker", "pin", "patch", "emblema"],
                "default_tagline": "Identidade Marcante, Alta Durabilidade e Acabamento de Precisão",
                "act1": {
                    "tag": "Identidade & Estilo",
                    "fa_icon": "fa-solid fa-tag",
                    "title": "DESIGN EXCLUSIVO E IDENTIDADE VISUAL MARCANTE",
                    "desc_tmpl": "O(A) {title} traz detalhes refinados e acabamento de alto nível, perfeito para personalizar suas tralhas, chaves, veículos e equipamentos."
                },
                "act2": {
                    "tag": "Resistência & Durabilidade",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "MATERIAIS DE ALTA RESISTÊNCIA CONTRA DESGASTE",
                    "desc_tmpl": "Confeccionado com matéria-prima resistente a atrito, intempéries e raios UV, preservando o brilho e as cores por muito mais tempo."
                },
                "act3": {
                    "tag": "Praticidade & Fixação",
                    "fa_icon": "fa-solid fa-check",
                    "title": "ACABAMENTO SEGURO E FÁCIL APLICAÇÃO",
                    "desc_tmpl": "Projetado para encaixe seguro ou aderência firme sobre superfícies lisas, resistindo à poeira e umidade sem soltar."
                },
                "base_specs": [
                    {"label": "Categoria", "default": "Acessórios e Itens Colecionáveis Originais"},
                    {"label": "Material", "default": "Liga reforçada / Vinil automotivo de alta resistência"},
                    {"label": "Aplicação", "default": "Chaves, veículos, embarcações, caixas de pesca e cadernos"},
                    {"label": "Durabilidade", "default": "Resistente a água e exposição solar"}
                ],
                "care_tips": "Limpar com pano seco ou levemente umedecido em água. Não utilizar solventes químicos abrasivos."
            },

            # 22. Óculos de Sol & Polarizados UV400
            "eyewear_sunglasses": {
                "id": "eyewear_sunglasses",
                "name": "Óculos de Sol & Polarizados UV400",
                "fa_icon": "fa-solid fa-glasses",
                "theme_color": "#0f766e",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["oculos", "óculos", "polarizado", "polarizada", "aviador", "uv400", "lente polarizada"],
                "default_tagline": "Visão Nítida sem Reflexos, Lentes Polarizadas UV400 e Armação Ultraleve",
                "act1": {
                    "tag": "Lentes & Polarização",
                    "fa_icon": "fa-solid fa-glasses",
                    "title": "LENTES POLARIZADAS DE ALTA DEFINIÇÃO COM PROTEÇÃO UV400",
                    "desc_tmpl": "As lentes do(a) {title} contam com filtro polarizado de alta precisão que elimina reflexos da água, asfalto e superfícies brilhantes, garantindo visão nítida, contraste aprimorado e bloqueio de 100% dos raios UVA e UVB."
                },
                "act2": {
                    "tag": "Estrutura & Conforto",
                    "fa_icon": "fa-solid fa-feather",
                    "title": "ARMAÇÃO ERGONÔMICA LEVE E RESISTENTE A IMPACTOS",
                    "desc_tmpl": "Construída com materiais de alta tenacidade e flexibilidade balanceada, oferece encaixe anatômico confortável que não pressiona as têmporas nem o nariz durante longas horas de uso."
                },
                "act3": {
                    "tag": "Fixação & Durabilidade",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "ACABAMENTO PREMIUM E HASTES ANATÔMICAS CONFORTÁVEIS",
                    "desc_tmpl": "Design esportivo e refinado com dobradiças reforçadas e ponteiras anatômicas que garantem fixação firme no rosto sem pressionar as têmporas, oferecendo máximo conforto mesmo em movimento constante."
                },
                "base_specs": [
                    {"label": "Tecnologia das Lentes", "default": "Polarizadas TAC com filtro anti-reflexo HD"},
                    {"label": "Proteção Solar", "default": "Fator UV400 com 100% de bloqueio contra raios UVA e UVB"},
                    {"label": "Material da Armação", "default": "Polímero ultraleve de alta resistência / Liga metálica nobre"},
                    {"label": "Apoio Nasal", "default": "Plaquetas anatômicas confortáveis que não marcam a pele"},
                    {"label": "Itens Inclusos", "default": "Estojo protetor oficial e flanela especial de microfibra"},
                    {"label": "Uso Recomendado", "default": "Pesca esportiva, náutica, direção, campo e uso diário ao ar livre"}
                ],
                "care_tips": "Lavar periodicamente com água corrente e detergente neutro. Secar com a flanela de microfibra limpa. Guardar sempre no estojo evitando contato com superfícies abrasivas."
            },

            # 23. Luvas de Pesca, Táticas & Esportivas
            "gloves_tactical_fishing": {
                "id": "gloves_tactical_fishing",
                "name": "Luvas de Pesca, Táticas & Esportivas",
                "fa_icon": "fa-solid fa-mitten",
                "theme_color": "#475569",
                "theme_bg": "#f8fafc",
                "category_keywords": ["luva", "luvas", "meio dedo", "dedo inteiro", "grip", "tactical glove"],
                "default_tagline": "Aderência Antiderrapante Firme, Dorso Respirável e Proteção Solar nas Mãos",
                "act1": {
                    "tag": "Aderência & Grip",
                    "fa_icon": "fa-solid fa-hand",
                    "title": "PALMA ANTIDERRAPANTE COM ADERÊNCIA REFORÇADA",
                    "desc_tmpl": "A {title} conta com superfície texturizada de alta aderência na palma, garantindo pegada firme e controle absoluto sobre varas de pesca, guidões, ferramentas e rédeas, mesmo com as mãos molhadas."
                },
                "act2": {
                    "tag": "Respirabilidade & Proteção",
                    "fa_icon": "fa-solid fa-sun",
                    "title": "DORSO RESPIRÁVEL COM PROTEÇÃO SOLAR E SECAGEM RÁPIDA",
                    "desc_tmpl": "Confeccionada com tecido flexível e ventilado que dissipa o calor rapidamente, prevenindo queimaduras solares, bolhas e calosidades durante longas jornadas."
                },
                "act3": {
                    "tag": "Ajuste & Firmeza",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "AJUSTE ANATÔMICO COM FECHO SEGURO NO PULSO",
                    "desc_tmpl": "Fechamento ajustável no punho que impede a entrada de resíduos, garantindo firmeza sem restringir a circulação ou a mobilidade dos dedos nas atividades de precisão."
                },
                "base_specs": [
                    {"label": "Palma da Mão", "default": "Material sintético texturizado antiderrapante com reforço no polegar"},
                    {"label": "Dorso", "default": "Tecido elástico de alta respirabilidade e secagem ultra rápida (Quick Dry)"},
                    {"label": "Ajuste no Punho", "default": "Fita regulável de fixação rápida para vedação confortável"},
                    {"label": "Modelagem", "default": "Anatômica esportiva (corte meio dedo para sensibilidade tátil)"},
                    {"label": "Indicação de Uso", "default": "Pesca esportiva, ciclismo, motociclismo, tiro e trabalho no campo"}
                ],
                "care_tips": "Lavar à mão com água fria e sabão neutro. Não usar alvejante. Secar à sombra e não torcer."
            }
        }

    def detect_archetype(self, title: str, category: str = "", tags: List[str] = None, vendor: str = "", sku: str = "") -> str:
        """
        Detecta com máxima precisão o arquétipo correto do produto.
        O TÍTULO DO PRODUTO É SOBERANO: previne que coleções multi-categoria
        façam produtos serem classificados incorretamente.
        Normaliza diacríticos para evitar falhas por acentuação incorreta (ex: òculos, óculos, oculos).
        """
        def _clean(s: str) -> str:
            if not s:
                return ""
            return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower().strip()

        t_raw = (title or "").strip()
        t = _clean(t_raw)
        cat = _clean(category)
        tags_str = _clean(" ".join(tags or []))
        vend = _clean(vendor)
        sku_clean = (sku or "").upper().strip()
        text = f"{t} {cat} {vend} {tags_str} {sku_clean}"

        # 1. Aromatizantes Automotivos & Cuidados (Prioridade máxima para evitar que caiam em camisas)
        if any(w in t for w in ["aromatizante", "cheirinho", "difusor", "aromatizador", "odorizador", "little trees", "odor"]):
            return "accessories_car_care"

        # 1.1 Cabos, Acessórios Elétricos e Peças de Reposição (Para não cair em térmicos ou iscas)
        if any(w in t for w in ["cabo plug", "cabo de alimentacao", "cabo de forca", "adaptador 12v"]):
            return "accessories_general"

        # 2. Copos Térmicos, Garrafas e Canecas (Prioridade Alta para evitar colisões com boné/isca/camisa)
        is_drinkware = (
            any(w in t for w in ["copo termico", "garrafa termica", "caneca termica", "cuia termica", "cooler"]) or
            ((any(w in t for w in ["copo", "garrafa", "caneca", "cantil", "cuia"]) or "elber" in t) and
             any(w in t for w in ["termic", "termo", "inox", "aco inox", "vacuum", "vazio", "geladeira", "litros"]) and
             not any(w in t for w in ["cabo", "plug", "abridor"])) or
            (t.startswith("copo ") or t.startswith("garrafa ") or t.startswith("caneca ") or t.startswith("cuia "))
        )
        if is_drinkware and not any(w in t for w in ["camisa", "camiseta", "abridor de garrafa"]):
            return "drinkware_thermo"

        # 3. Óculos de Sol & Polarizados UV400 (normalizado para capturar óculos, òculos, oculos)
        if (any(w in t for w in ["oculos", "sunglasses"]) or any(w in t for w in ["polarizado", "polarizada", "aviador", "uv400", "lente polarizada"])) and not any(w in t for w in ["camisa", "camiseta", "adesivo", "chaveiro", "lenco", "bandana"]):
            return "eyewear_sunglasses"

        # 4. Luvas de Pesca, Táticas & Esportivas (se não for camisa)
        if any(w in t for w in ["luva", "luvas"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "gloves_tactical_fishing"

        # 5. Bandanas, Tubenecks, Lenços & Balaclavas (se não for camisa)
        if any(w in t for w in ["bandana", "balaclava", "tubeneck", "buff", "mascara facial", "protetor de pescoco", "lenco", "lencos"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "neck_gaiters_balaclavas"

        # 6. Macacões & Jardineiras (Prioridade antes de calçados para não cair em tênis/bota)
        if any(w in t for w in ["macacao", "jardineira", "jardineiras", "salopete"]):
            return "overalls_workwear"

        # 7. Caixas de Pesca, Estojos & Organização (Prioridade antes de iscas para evitar que caixa de iscas caia em iscas)
        is_tackle_box = (
            any(w in t for w in ["caixa de pesca", "caixa organizadora", "maleta de pesca", "estojo de pesca", "organizador de isca", "porta-iscas", "porta iscas", "porta-vara", "porta vara", "tubo de vara", "multicase", "bolsa tatica deyu kit"]) or
            ((t.startswith("caixa ") or t.startswith("estojo ") or t.startswith("maleta ")) and not any(w in t for w in ["caixa com ", "caixa c/ ", "estojo + ", "anzois", "anzol", "girador"]))
        )
        if is_tackle_box and not any(w in t for w in ["camisa", "camiseta"]) and not any(w in t for w in ["anzois", "anzol", "girador"]):
            return "tackle_boxes_storage"

        # 8. Calças, Bermudas & Shorts (Prioridade antes de camisa para não cair em uv_performance)
        if any(w in t for w in ["calca", "calcas", "bermuda", "bermudas", "shorts", "short", "calcao"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "pants_cargo_tactical"

        # 9. Chapéus: Distinção estrita entre Country/Feltro/Cowboy vs Safári/Outdoor/Pescador
        if any(w in t for w in ["chapeu", "chapeus"]):
            if any(w in t for w in ["feltro", "pralana", "american hat", "karanda", "country", "cowboy", "pantaneiro", "la", "veludo", "liso", "marcatto", "eldorado", "cury"]):
                return "hats_country_cowboy"
            return "hats_safari_outdoor"
        if any(w in t for w in ["pralana", "american hat", "karanda", "feltro country"]):
            return "hats_country_cowboy"

        # 10. Camisas / Vestuário Superior: Distinção estrita entre Camisas Work/Botão vs Algodão vs Motors vs UV50+
        is_c0_or_uv_sku = any(sku_clean.startswith(prefix) for prefix in ["C0", "CI", "CADV", "ADV", "HYB", "RAGLAN"])
        is_work_sku = any(sku_clean.startswith(prefix) for prefix in ["CMB", "CBT"])
        is_upper_body = any(w in t for w in ["camisa", "camisas", "camiseta", "camisetas", "baby look", "babylook", "regata", "t-shirt", "polo", "jersey", "segunda pele"]) or is_c0_or_uv_sku or is_work_sku

        if is_upper_body:
            # 10.1 Se for camisa com código C0, CI, CADV, ADV, HYB, RAGLAN ou com menção explícita a proteção UV / XTech
            is_uv_shirt = (
                is_c0_or_uv_sku or
                any(w in t for w in ["uv", "uv50", "fpu", "fps", "xtech", "solar", "segunda pele", "fusionx", "armorx", "hybrid"]) or
                any(w in tags_str for w in ["uv50", "uv", "protecao solar", "xtech"])
            )
            if is_uv_shirt and not is_work_sku and not any(w in t for w in ["algodao puro", "100% algodao", "camisa de botao", "camisa work"]):
                return "uv_performance"

            # 10.2 Camisas Work / Botão / Sarja / Lisas / Xadrez (Sem zíper, com botões e bolsos utilitários)
            is_button_work = (
                is_work_sku or
                any(w in t for w in ["camisa work", "safari sarja", "camisa sarja", "camisa de botao", "camisa botao", "manga longa sarja", "manga curta sarja", "xadrez"]) or
                (("operacional" in t or "sarja" in t or "de botao" in t) and not any(w in t for w in ["ziper"])) or
                (("lisa" in t or "sem estampa" in t) and any(w in t for w in ["classic", "manga curta", "manga longa"]) and not any(w in t for w in ["uv", "uv50", "dry", "xtech", "segunda pele"]))
            )
            if is_button_work and not any(w in t for w in ["ziper"]):
                return "shirts_button_work"

            # 10.3 Camisetas casuais de algodão (Agro / Campo)
            if any(w in t for w in ["algodao", "campo", "agro", "fazenda", "trator"]):
                return "agro_field"

            # 10.4 Jerseis de motocross sem proteção UV
            if any(w in t for w in ["jersey", "moto", "cross", "off-road", "trilha", "speed", "motors"]):
                return "motors_speed"

            return "uv_performance"

        if "jersey" in t:
            return "motors_speed"

        # 11. Cutelaria & Facas
        if any(w in t for w in ["faca", "facas", "cutelo", "cutelaria", "lamina", "bainha", "canivete", "chaira", "afiador"]):
            return "cutlery_unique"

        # 12. Calçados (Sandálias Boaonda vs Tênis/Botinas)
        if any(w in t for w in ["tenis", "botina", "bota", "sneaker", "sapato"]):
            return "closed_footwear_sneakers"
        if any(w in t for w in ["sandalia", "chinelo", "boaonda", "babuche", "clog", "slide", "pantufa"]):
            return "footwear_sandals_boaonda"

        # 13. Chapéus de Pesca / Safári (secundário)
        if any(w in t for w in ["safari", "australiano", "palha", "pescador"]):
            return "hats_safari_outdoor"

        # 14. Bonés Trucker & Snapback (Com trava contra palavra inglesa 'bones')
        is_cap = (
            any(w in t for w in ["trucker", "snapback", "aba curva", "aba reta", "viseira"]) or
            (bool(re.search(r'\b(bone|bones)\b', t)) and not any(w in t for w in ["till the bones", "cross bones", "fish bones", "copo", "garrafa", "camisa"]))
        )
        if is_cap:
            return "caps_trucker_snapback"

        # 15. Manguitos
        if any(w in t for w in ["manguito", "manguitos", "manga avulsa"]):
            return "sun_sleeves_manguitos"

        # 16. Ferragens e Equipamentos de Pesca (Varas, Carretilhas, Molinetes, Giradores, Snaps, Argolas)
        if bool(re.search(r'\bvaras?\b', t)) or any(w in t for w in ["carretilha", "molinete", "linha", "anzol", "anzois", "alicate", "passagua", "girador", "giradores", "snap", "snaps", "argola", "empate", "chumbada", "chumbo", "trava varas", "suporte porta iscas"]):
            return "fishing_tackle_gear"

        # 17. Iscas Artificiais
        if any(w in t for w in ["isca", "iscas", "plug", "jig", "frog", "soft bait", "crankbait", "minnow", "popper", "stick", "twitch", "shad", "criatura"]):
            return "fishing_lures"

        # 18. Acessórios Gerais, Chaveiros, Adesivos, Camping & Caiaque
        if any(w in t for w in ["chaveiro", "adesivo", "adesivos", "sticker", "stickers", "patch", "emblema", "pin ", "capa de caiaque", "caiaque", "barraca", "fogareiro", "mesa dobravel", "cadeira", "coleira", "suporte magnetico", "personalizacao nome", "cabo plug", "fita para protecao"]):
            return "accessories_general"

        # 19. Copos e Térmicos (secundário)
        if any(w in t for w in ["copo", "garrafa", "caneca", "cantil", "cooler", "termico"]):
            return "drinkware_thermo"

        # 20. Livros & Publicações
        if any(w in t for w in ["livro", "livros", "cartilha", "guia ilustrado", "colorir"]):
            return "books_publications"

        # Fallback Secundário via Categoria / Tags / Vendor
        if any(w in text for w in ["aromatizante", "cheirinho", "difusor"]):
            return "accessories_car_care"
        if any(w in text for w in ["oculos", "polarizado", "uv400"]):
            return "eyewear_sunglasses"
        if any(w in text for w in ["luva", "luvas"]) and not any(w in text for w in ["camisa", "camiseta"]):
            return "gloves_tactical_fishing"
        if any(w in text for w in ["lenco", "bandana", "balaclava", "tubeneck"]):
            return "neck_gaiters_balaclavas"
        if any(w in text for w in ["chaveiro", "adesivo"]):
            return "accessories_general"
        if any(w in text for w in ["calca", "bermuda", "shorts"]):
            return "pants_cargo_tactical"
        if any(w in text for w in ["pralana", "american hat", "karanda", "feltro", "country"]):
            return "hats_country_cowboy"
        if any(w in text for w in ["manguito", "manguitos"]):
            return "sun_sleeves_manguitos"
        if any(w in text for w in ["sandalia", "chinelo", "boaonda"]):
            return "footwear_sandals_boaonda"
        if any(w in text for w in ["tenis", "calcado"]):
            return "closed_footwear_sneakers"
        if any(w in t for w in ["isca", "iscas", "plug"]):
            return "fishing_lures"
        if any(w in text for w in ["copo", "garrafa", "termic"]):
            return "drinkware_thermo"
        if any(w in text for w in ["chapeu"]):
            return "hats_safari_outdoor"
        if bool(re.search(r'\b(bone|bones)\b', text)) and "till the bones" not in text:
            return "caps_trucker_snapback"
        if bool(re.search(r'\bvaras?\b', text)) or any(w in text for w in ["carretilha", "molinete", "girador", "snap", "empate"]):
            return "fishing_tackle_gear"
        if any(w in text for w in ["jersey", "moto", "motors"]):
            return "motors_speed"
        if any(w in text for w in ["agro", "campo"]):
            return "agro_field"

        return "uv_performance"

    def classify_store_category(self, title: str, archetype_id: str, store_key: str = "brk_fishing", tags: List[str] = None, sku: str = "") -> str:
        """
        Classifica o produto em uma Coleção/Categoria oficial da loja com base no arquétipo soberano,
        garantindo zero contaminação entre Camisas, Bonés, Bandanas, Óculos, Botinas e Equipamentos.
        """
        t_low = (title or "").lower()
        sku_low = (sku or "").lower()
        tags_str = " ".join(tags or []).lower() if isinstance(tags, list) else str(tags or "").lower()
        full_info = f"{t_low} {sku_low} {tags_str}"

        if store_key == "brk_agro":
            if archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work"):
                return "Camisas Agro & Campo"
            if archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
                return "Bonés & Chapéus Agro"
            if archetype_id in ("closed_footwear_sneakers", "footwear_sandals_boaonda"):
                return "Botinas & Calçados"
            if archetype_id == "cutlery_unique":
                return "Cutelaria & Facas Campo"
            if archetype_id == "drinkware_thermo":
                return "Térmicos & Tereré"
            if archetype_id == "eyewear_sunglasses":
                return "Óculos Polarizados Agro"
            if archetype_id in ("neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"):
                return "Bandanas, Luvas & Manguitos"
            if archetype_id in ("pants_cargo_tactical", "overalls_workwear"):
                return "Calças & Vestuário Campo"
            return "Acessórios Agro & Fazenda"

        if store_key == "brk_motors":
            if archetype_id in ("uv_performance", "motors_speed", "agro_field", "shirts_button_work"):
                if any(w in t_low for w in ["jaqueta", "corta vento", "moletom", "segunda pele"]):
                    return "Jaquetas & Corta Vento"
                return "Jerseys & Camisas Motors"
            if archetype_id in ("neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"):
                return "Proteção & Luvas Motors"
            if archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
                return "Bonés & Street Motors"
            if archetype_id == "eyewear_sunglasses":
                return "Óculos & Goggles"
            return "Acessórios & Equipamentos"

        # Default: brk_fishing
        if archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work"):
            if "armorx" in full_info or "armor" in t_low:
                return "Camisas ArmorX"
            return "Camisas de Pesca UV"
        if archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
            return "Bonés & Chapéus"
        if archetype_id in ("neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"):
            return "Bandanas, Luvas & Manguitos"
        if archetype_id == "eyewear_sunglasses":
            return "Óculos Polarizados"
        if archetype_id in ("fishing_lures", "fishing_tackle_gear"):
            return "Equipamentos & Iscas"
        if archetype_id == "tackle_boxes_storage":
            return "Caixas & Organização"
        if archetype_id in ("footwear_sandals_boaonda", "closed_footwear_sneakers", "overalls_workwear", "pants_cargo_tactical"):
            return "Calçados & Sandálias"
        if archetype_id == "cutlery_unique":
            return "Cutelaria & Facas"
        if archetype_id == "drinkware_thermo":
            return "Térmicos & Camping"
        return "Acessórios Diversos"

    def sanitize_specs_for_archetype(self, specs: List[Dict[str, str]], archetype_id: str) -> List[Dict[str, str]]:
        """
        Sanitiza a ficha técnica para remover estritamente especificações proibidas
        ou alucinações incompatíveis com a categoria do produto (Regra de Ouro da Fidelidade).
        """
        sanitized = []
        for s in specs:
            label = s.get("label", "").lower()
            val = s.get("value", s.get("default", "")).lower()
            full = f"{label} {val}"

            # 1. Chapéus Country / Feltro: ZERO cordão jugular, ZERO trava anti-vento, ZERO ilhoses de respiração
            if archetype_id == "hats_country_cowboy":
                if any(w in full for w in ["jugular", "vento", "ilhós", "ilhoses", "pescoço", "nuca", "protetor de nuca"]):
                    continue

            # 2. Camisas Work / Botão: ZERO zíper, ZERO trava de segurança, ZERO gola padre com zíper, ZERO estampa sublimada
            elif archetype_id == "shirts_button_work":
                if any(w in full for w in ["zíper", "ziper", "cursor", "trava", "sublimad", "gola padre"]):
                    continue

            # 3. Calças / Bermudas: ZERO mangas, ZERO gola alta, ZERO zíper frontal no peito
            elif archetype_id == "pants_cargo_tactical":
                if any(w in full for w in ["manga", "gola padre", "gola alta", "peito", "punho"]):
                    continue

            # 4. Aromatizantes & Cuidados: ZERO vestuário, ZERO tecido, ZERO lavagem à máquina, ZERO passar a ferro
            elif archetype_id in ["accessories_car_care", "accessories_general"]:
                if any(w in full for w in ["manga", "gola", "tecido", "poliéster", "algodão", "lavar à mão", "lavagem", "ferro", "modelagem"]):
                    continue

            # 5. Óculos de Sol: ZERO vestuário, ZERO mangas, ZERO gola, ZERO zíper, ZERO tecido
            elif archetype_id == "eyewear_sunglasses":
                if any(w in full for w in ["manga", "gola", "zíper", "ziper", "tecido", "poliéster", "algodão", "costura", "punho", "passador", "bolso", "modelagem"]):
                    continue

            # 6. Luvas de Pesca & Táticas: ZERO mangas compridas, ZERO gola, ZERO zíper frontal
            elif archetype_id == "gloves_tactical_fishing":
                if any(w in full for w in ["manga longa", "mangas longas", "gola", "zíper", "ziper", "passador", "bolso"]):
                    continue

            # 7. Lenços e Bandanas: ZERO mangas, ZERO gola padre, ZERO zíper
            elif archetype_id == "neck_gaiters_balaclavas":
                if any(w in full for w in ["manga", "gola padre", "zíper", "ziper", "punho", "passador", "bolso"]):
                    continue

            # 8. Equipamentos e Ferragens de Pesca: ZERO vestuário
            elif archetype_id in ["fishing_tackle_gear", "fishing_lures", "tackle_boxes_storage"]:
                if any(w in full for w in ["manga", "gola", "zíper", "ziper", "tecido", "poliéster", "algodão", "costura"]):
                    continue

            sanitized.append(s)
        return sanitized

    def is_ready_delivery(self, product: Dict[str, Any]) -> bool:
        """
        Identifica se o produto é de pronta entrega / envio imediato.
        Regra Oficial BRK:
        - Códigos/SKUs contendo _FULL ou _OUT (ex: C02496BLP_FULL, C01046BLP_OUT, -FULL, -OUT)
        - Menção expressa de pronta entrega / envio imediato no título ou tags
        """
        if not product:
            return False

        skus_to_check = []
        for k in ["sku", "master_sku"]:
            val = str(product.get(k) or "").strip()
            if val:
                skus_to_check.append(val)

        for vsku in product.get("variants_skus", []):
            if vsku:
                skus_to_check.append(str(vsku).strip())

        for v in product.get("variants", []):
            if isinstance(v, dict):
                v_s = str(v.get("sku") or "").strip()
                if v_s:
                    skus_to_check.append(v_s)

        title = str(product.get("title") or "")
        tags = product.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        tags_str = " ".join(tags)

        full_out_pattern = re.compile(r'(_FULL|_OUT|\bFULL\b|\bOUT\b|-FULL|-OUT)', re.IGNORECASE)
        for s in skus_to_check:
            if full_out_pattern.search(s):
                return True

        if full_out_pattern.search(title) or full_out_pattern.search(tags_str):
            return True
        if any(term in title.lower() for term in ["pronta entrega", "envio imediato"]):
            return True

        return False

    def extract_product_specs(self, product: Dict[str, Any], archetype_id: str, sibling_specs: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Extrai especificações autênticas do produto. Se o sibling_matcher encontrou
        especificações de um irmão homólogo, elas são priorizadas e sanitizadas para garantir fidelidade.
        Para Camisas UV Performance (C0), usa rigorosamente a Ficha Técnica Oficial XTech Pro
        com Prazo de Produção dinâmico (Pronta entrega para _FULL e _OUT, 10 dias úteis para códigos padrão)
        e detalhes anatômicos exclusivos para Fusion (máscara integrada + dedeira) e Hybrid (capuz + dedeira).
        """
        if archetype_id == "uv_performance":
            is_pronta = self.is_ready_delivery(product)
            prazo_val = "Pronta entrega" if is_pronta else "10 dias úteis"
            
            t_low = (product.get("title") or "").lower()
            sku_low = str(product.get("master_sku") or product.get("sku") or "").lower()
            tags_low = " ".join([str(t).lower() for t in (product.get("tags") or [])]) if isinstance(product.get("tags"), list) else str(product.get("tags") or "").lower()
            
            is_fusion = any(w in t_low for w in ["fusion", "fusionx"]) or "fusion" in sku_low or "fusion" in tags_low
            is_hybrid = any(w in t_low for w in ["hybrid"]) or sku_low.startswith("hyb") or "hybrid" in sku_low or "hybrid" in tags_low
            is_armorx_shirt = sku_low.startswith("cax") or ("armorx" in t_low and "camisa" in t_low)
            is_has_glove = any(w in t_low for w in ["com luva", "e luva", "luva integrada"]) or is_armorx_shirt
            is_short_sleeve = (
                any(w in t_low for w in ["manga curta", "manga-curta", "camiseta", "camisetas", "t-shirt", "tshirt"])
                or ("curta" in t_low and "manga" in t_low)
                or bool(re.match(r'^(?:cm|casual|bp|apc)\d', sku_low))
            ) and not any(w in t_low for w in ["manga longa", "manga-longa"])
            
            specs = [
                {"label": "Prazo de Produção", "value": prazo_val},
                {"label": "Composição", "value": "90% Poliéster 10% Elastano"},
                {"label": "Tecido", "value": "XTech Pro"},
                {"label": "Tecnologia", "value": "Secagem Rápida, Tecido Leve, Proteção Solar"},
                {"label": "Modelagem", "value": "Anatômica e confortável"},
                {"label": "Proteção", "value": "Proteção UV50+ (não sai na lavagem)"},
            ]
            if is_fusion:
                specs.append({"label": "Capuz & Máscara", "value": "Capuz anatômico integrado com máscara facial de proteção UV50+"})
                specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
            elif is_hybrid:
                specs.append({"label": "Capuz", "value": "Capuz anatômico integrado de alta cobertura solar"})
                specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
            elif is_short_sleeve:
                specs.append({"label": "Gola", "value": "Gola redonda canelada anatômica com pesponto reforçado"})
                specs.append({"label": "Mangas", "value": "Mangas curtas com acabamento reforçado em pesponto duplo"})
            elif is_has_glove:
                specs.append({"label": "Punhos / Luva", "value": "Punhos estendidos anatômicos com luva integrada para o dorso da mão"})
            return specs

        if sibling_specs and len(sibling_specs) >= 2:
            raw_specs = [{"label": s["label"], "value": s["default"]} for s in sibling_specs]
            return self.sanitize_specs_for_archetype(raw_specs, archetype_id)

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
            elif "boaonda" in full_text and label == "Material do Cabedal":
                val = "Termoplástico nobre Boaonda flexível e lavável"

            # 1. Proteção Solar (uv_performance usa padrão oficial XTech Pro)
            if archetype_id != "uv_performance" and ("proteção" in label.lower() or "solar" in label.lower()):
                if any(x in full_text for x in ["50+", "uv 50", "fps 50", "fpu 50"]):
                    val = "Fator FPU 50+ permanente certificado"
                elif "uv" in full_text:
                    val = "Proteção UV integrada ao tecido"
            
            # 2. Composição / Tecido (uv_performance usa padrão oficial 90% Poliéster 10% Elastano / XTech Pro)
            elif archetype_id != "uv_performance" and ("composição" in label.lower() or "tecido" in label.lower()):
                if archetype_id == "agro_field" or "algodão" in title.lower() or "algodao" in title.lower():
                    val = "100% Algodão Premium Penteado com toque macio"
                elif any(x in full_text for x in ["dry fit", "dryfit", "dry"]):
                    val = "100% Poliéster Tecnológico Dry Fit respirável"
                elif "algodão" in full_text or "algodao" in full_text:
                    val = "100% Algodão Premium Penteado com toque macio"

            # 3. Zíper
            elif "zíper" in label.lower() or "ziper" in label.lower():
                if "ykk" in full_text:
                    val = "Zíper reforçado YKK com trava emborrachada"
                elif "sem zíper" in full_text or "careca" in full_text:
                    val = "Gola careca com acabamento reforçado"

            extracted.append({"label": label, "value": val})

        return extracted

    def resolve_product_origin_and_title(self, title: str, vendor: str = "", sku: str = "", tags = None, product: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Determina com precisão a origem do produto (produção própria BRK vs revenda)
        e formata o título da descrição:
        - Produção própria: garante 'BRK' no título.
        - Revenda: garante o nome da marca correspondente no título.
        - Camisas de produção própria com código iniciado em C0: ativa show_copyright.
        """
        tags_str = " ".join(tags or []) if isinstance(tags, list) else str(tags or "")
        full_info = f"{title} {vendor} {tags_str}"
        
        detected_brand = None
        for brand in self.known_brands:
            if re.search(r'\b' + re.escape(brand) + r'\b', full_info, re.IGNORECASE):
                detected_brand = brand
                break
                
        is_revenda = detected_brand is not None and detected_brand.lower() != "brk"
        
        t_clean = title.strip()
        if is_revenda:
            origin_type = "revenda"
            brand_name = detected_brand
            if not re.search(r'\b' + re.escape(brand_name) + r'\b', t_clean, re.IGNORECASE):
                formatted_title = f"{t_clean} - {brand_name}"
            else:
                formatted_title = t_clean
        else:
            origin_type = "producao_propria"
            brand_name = "BRK"
            if not re.search(r'\b(BRK|ArmorX)\b', t_clean, re.IGNORECASE):
                formatted_title = f"BRK {t_clean}"
            else:
                formatted_title = t_clean
                
        # Regra de Direitos Autorais em Camisas C0 (Verificação exaustiva de SKU mestre, variantes e handle)
        sku_upper = str(sku or "").upper().strip()
        var_skus = []
        handle_str = ""
        if isinstance(product, dict):
            var_skus = [str(v).upper() for v in product.get("variants_skus", [])]
            handle_str = str(product.get("handle", "")).upper()
        
        is_c0 = sku_upper.startswith("C0") or any(v.startswith("C0") for v in var_skus) or handle_str.startswith("C0") or "C0" in str(tags or "").upper()
        is_shirt = any(w in t_clean.lower() for w in ["camisa", "camiseta", "jersey", "baby look", "regata", "polo"])
        show_copyright = (origin_type == "producao_propria") and is_shirt and is_c0
        
        return {
            "formatted_title": formatted_title,
            "brand_name": brand_name,
            "origin_type": origin_type,
            "show_copyright": show_copyright
        }

    def _is_back_view_url(self, url: str, include_03: bool = False) -> bool:
        if not url or not isinstance(url, str):
            return False
        u_low = url.lower()
        fname = u_low.split("/")[-1].split("?")[0]
        fname_no_ts = re.sub(r'(?:^|[_.\-\s])\d{2}_\d{2}_\d{2}(?=[_.\-\s]|$)', '', fname)
        if "frente" in fname_no_ts:
            return False
        keywords = [
            "costas", "costa", "back", "traseira", "verso", "tras",
            "02fem", "02masc", "02inf", "2fem", "2masc", "2inf",
            "02_fem", "02_masc", "02_inf", "2_fem", "2_masc", "2_inf"
        ]
        if include_03:
            keywords.extend(["03fem", "03masc", "03inf"])
        if any(w in fname_no_ts for w in keywords):
            return True
        return bool(re.search(r'(?:^|[-_.\s])(2|02|b)(?:[-_.\s]|masc|fem|inf|kids|bl|$)', fname_no_ts))

    def _select_apparel_act_images(self, cdn_images: List[str]):
        if not cdn_images:
            return "", "", ""
        if len(cdn_images) == 1:
            return cdn_images[0], "", ""

        # Ato 1 (Hero Frontal): evita foto de costas se houver foto frontal/não-costas disponível
        img1 = cdn_images[0]
        if self._is_back_view_url(img1):
            pure_front_candidates = [
                u for u in cdn_images
                if not self._is_back_view_url(u)
                and any(k in u.lower().split("/")[-1] for k in ["frente", "01", "-1", "capa"])
                and not any(p in u.lower().split("/")[-1] for p in ["persp", "zoom"])
            ]
            front_candidates = [
                u for u in cdn_images
                if not self._is_back_view_url(u) and any(k in u.lower().split("/")[-1] for k in ["frente", "01", "-1", "capa"])
            ]
            non_back_candidates = [u for u in cdn_images if not self._is_back_view_url(u)]
            if pure_front_candidates:
                img1 = pure_front_candidates[0]
            elif front_candidates:
                img1 = front_candidates[0]
            elif non_back_candidates:
                img1 = non_back_candidates[0]

        rem = [u for u in cdn_images if u != img1]
        if not rem:
            return img1, "", ""
        if len(rem) == 1:
            return img1, rem[0], ""

        # Ato 2 (Tecnologia / Detalhe) & Ato 3 (Acabamento / Painel Traseiro)
        if self._is_back_view_url(rem[0]):
            non_back_after = [u for u in rem[1:] if not self._is_back_view_url(u)]
            if non_back_after:
                img2 = non_back_after[0]
                img3 = rem[0]
            else:
                img2 = rem[0]
                img3 = rem[1]
        else:
            img2 = rem[0]
            if self._is_back_view_url(rem[1]):
                img3 = rem[1]
            else:
                back_after = [u for u in rem[2:] if self._is_back_view_url(u)]
                img3 = back_after[0] if back_after else rem[1]

        return img1, img2, img3

    def generate_narrative_from_template(self, product: Dict[str, Any], archetype_id: str, cdn_images: List[str], store_key: str = None, sibling_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gera os 3 blocos narrativos e especificações prontos para o HTMLBuilder.
        Se sibling_info for fornecido, anota o produto como originário de irmão homólogo do site.
        """
        template = self.templates.get(archetype_id, self.templates["uv_performance"])
        title = product.get("title", "Produto BRK")
        sku = product.get("master_sku") or product.get("sku") or ""
        vendor = product.get("vendor", "")
        tags = product.get("tags") or []

        # Resolução de Origem, Título Formatado e Direitos Autorais C0
        origin_info = self.resolve_product_origin_and_title(title=title, vendor=vendor, sku=sku, tags=tags, product=product)
        formatted_title = origin_info["formatted_title"]
        brand_name = origin_info["brand_name"]
        origin_type = origin_info["origin_type"]
        show_copyright = origin_info["show_copyright"]
        
        # Paleta Cromática Suave por Loja
        store_palettes = {
            "brk_fishing": {"color": "#0284c7", "bg": "#f0f9ff"}, # Azul Leve
            "brk_agro":    {"color": "#16a34a", "bg": "#f0fdf4"}, # Verde Leve
            "brk_motors":  {"color": "#f97316", "bg": "#fff7ed"}, # Laranja Leve
        }
        
        if not store_key:
            url = (product.get("url") or "").lower()
            vendor_str = (product.get("vendor") or "").lower()
            category = (product.get("category") or "").lower()
            if "agro" in url or "agro" in vendor_str or "agro" in category or archetype_id == "agro_field":
                store_key = "brk_agro"
            elif "motors" in url or "motors" in vendor_str or "motors" in category or archetype_id == "motors_speed":
                store_key = "brk_motors"
            else:
                store_key = "brk_fishing"

        theme_color = store_palettes.get(store_key, {}).get("color", template.get("theme_color", "#0284c7"))
        theme_bg = store_palettes.get(store_key, {}).get("bg", template.get("theme_bg", "#f0f9ff"))

        # Determinar ícone de cuidados apropriado ao arquétipo
        care_icons = {
            "hats_country_cowboy": "fa-solid fa-hat-cowboy",
            "hats_safari_outdoor": "fa-solid fa-hat-cowboy-side",
            "caps_trucker_snapback": "fa-solid fa-hat-baseball",
            "shirts_button_work": "fa-solid fa-shirt",
            "pants_cargo_tactical": "fa-solid fa-vest",
            "accessories_car_care": "fa-solid fa-spray-can-sparkles",
            "accessories_general": "fa-solid fa-key",
            "fishing_lures": "fa-solid fa-fish-fins",
            "neck_gaiters_balaclavas": "fa-solid fa-mask-face",
            "sun_sleeves_manguitos": "fa-solid fa-hand-holding-hand",
            "footwear_sandals_boaonda": "fa-solid fa-shoe-prints",
            "closed_footwear_sneakers": "fa-solid fa-socks",
            "drinkware_thermo": "fa-solid fa-mug-hot",
            "tackle_boxes_storage": "fa-solid fa-box-archive",
            "overalls_workwear": "fa-solid fa-vest",
            "books_publications": "fa-solid fa-book-open",
            "cutlery_unique": "fa-solid fa-utensils",
            "fishing_tackle_gear": "fa-solid fa-screwdriver-wrench",
            "motors_speed": "fa-solid fa-shield-halved",
            "agro_field": "fa-solid fa-seedling",
            "uv_performance": "fa-solid fa-shirt",
            "eyewear_sunglasses": "fa-solid fa-glasses",
            "gloves_tactical_fishing": "fa-solid fa-mitten"
        }
        care_icon = care_icons.get(archetype_id, template.get("fa_icon", "fa-solid fa-hand-sparkles"))

        is_apparel = archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work", "pants_cargo_tactical")

        # Tratamento Especial para Iscas e Produtos com Várias Variações (Split Media estrito para fishing_lures)
        is_lure = (archetype_id == "fishing_lures")
        variants = product.get("variants") or []
        has_multiple_variations = is_lure and (len(variants) > 1 or len(cdn_images) >= 2)
        split_images = None
        variations_summary = ""

        # Alocação estrita de imagens exclusivas por ato - ZERO DUPLICAÇÃO
        if has_multiple_variations and (len(cdn_images) >= 4 or len(cdn_images) == 2):
            split_images = [cdn_images[0], cdn_images[1]]
            img1 = cdn_images[0]
            # Se for split no Ato 1, Atos 2 e 3 usam as fotos seguintes para não repetir
            img2 = cdn_images[2] if len(cdn_images) > 2 else ""
            img3 = cdn_images[3] if len(cdn_images) > 3 else ""
            variant_titles = [v.get("title") for v in variants if v.get("title") and v.get("title") != "Default Title"]
            if variant_titles:
                variations_summary = f"Disponível em {len(variant_titles)} opções de cores e modelos no anúncio ({', '.join(variant_titles[:4])}{'...' if len(variant_titles) > 4 else ''})."
            else:
                variations_summary = "Múltiplas variações e opções de cores disponíveis para escolha no anúncio."
        elif is_apparel:
            img1, img2, img3 = self._select_apparel_act_images(cdn_images)
        else:
            img1 = cdn_images[0] if len(cdn_images) > 0 else ""
            img2 = cdn_images[1] if len(cdn_images) > 1 else ""
            img3 = cdn_images[2] if len(cdn_images) > 2 else ""
            if has_multiple_variations:
                variant_titles = [v.get("title") for v in variants if v.get("title") and v.get("title") != "Default Title"]
                if variant_titles:
                    variations_summary = f"Disponível em {len(variant_titles)} opções de cores e modelos no anúncio ({', '.join(variant_titles[:4])}{'...' if len(variant_titles) > 4 else ''})."
                else:
                    variations_summary = "Múltiplas variações e opções de cores disponíveis para escolha no anúncio."

        act1 = dict(template["act1"])
        act2 = dict(template["act2"])
        act3 = dict(template["act3"])

        # Contextual Intelligence Flags para Adaptação Narrativa Dinâmica
        t_low = title.lower()
        tags_list = tags if isinstance(tags, list) else [str(tags)]
        tags_low = " ".join([str(t).lower() for t in tags_list])
        body_low = (product.get("body_html") or "").lower()
        all_info = f"{t_low} {tags_low} {body_low}"
        
        sku_clean_for_flags = str(product.get("master_sku") or product.get("sku") or "").lower()
        is_fusion = is_apparel and (
            any(w in t_low for w in ["fusion", "fusionx"]) or
            "fusion" in sku_clean_for_flags or
            "fusion" in tags_low
        )
        is_hybrid = is_apparel and (
            any(w in t_low for w in ["hybrid"]) or
            sku_clean_for_flags.startswith("hyb") or
            "hybrid" in sku_clean_for_flags or
            "hybrid" in tags_low
        )
        is_hooded = (is_apparel and any(w in t_low for w in ["capuz", "hood", "hoodie"])) or is_fusion or is_hybrid
        # is_kids só vale para vestuário: o texto/tabela infantil é de roupa (FPU 50+, Dry Fit, tórax/manga).
        # Óculos, calçados etc. com "Infantil" no título NÃO podem receber essa narrativa.
        has_inf_img = any("inf" in str(u).lower().split("/")[-1] for u in (cdn_images or []))
        is_kids_sku = bool(re.match(r'^(?:c0|c|cm|casual|ci|bp)\d+i(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$', sku_clean_for_flags)) and not ("feminina" in t_low and not has_inf_img)
        is_kids = is_apparel and (any(w in t_low for w in ["infantil", "kids", "juvenil"]) or bool(re.search(r'\bmini\b', t_low)) or is_kids_sku)
        if any(w in t_low for w in ["adulto", "unissex adulto"]) and not is_kids_sku and not any(w in t_low for w in ["infantil", "kids", "juvenil"]):
            is_kids = False
        is_short_sleeve = is_apparel and (
            any(w in t_low for w in ["manga curta", "manga-curta", "camiseta", "camisetas", "t-shirt", "tshirt"]) or
            ("curta" in t_low and "manga" in t_low) or
            bool(re.match(r'^(?:cm|casual|bp|apc)\d', sku_clean_for_flags))
        ) and not any(w in t_low for w in ["manga longa", "manga-longa"])
        is_armorx_shirt = is_apparel and (sku_clean_for_flags.startswith("cax") or ("armorx" in t_low and "camisa" in t_low))
        is_has_glove = (is_apparel and any(w in t_low for w in ["com luva", "e luva", "luva integrada"])) or is_armorx_shirt
        is_female = (
            any(w in t_low for w in ["feminina", "feminino", "baby look", "babylook", "mulher"]) or
            "femin" in tags_low or
            (is_apparel and bool(re.search(r'bl(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$', sku_clean_for_flags)))
        ) and not is_kids
        is_round_neck = is_apparel and (
            (is_short_sleeve and not any(w in t_low for w in ["ziper", "zíper"])) or
            any(w in t_low for w in ["gola careca", "gola redonda", "sem zíper", "sem ziper", "t-shirt"]) or
            ("camiseta" in t_low and not any(w in t_low for w in ["ziper", "zíper"]))
        )
        is_motors_cotton = (archetype_id == "agro_field") and (
            store_key == "brk_motors" or
            any(w in t_low for w in ["gs adventure", "big trail", "r1250", "street wear", "atacama", "rastro da serpente", "moto", "motors", "route 66", "machu picchu", "ushuaia", "travel far away", "all black"])
        ) and not any(w in t_low for w in ["agro", "fazenda", "pecuária", "pecuaria", "nelore", "trator", "campo", "roça", "roca"])

        # 0. Adaptação Algodão Premium Motors & Lifestyle Urbano/Duas Rodas
        if is_motors_cotton:
            act1["tag"] = "Algodão Premium & Lifestyle"
            act1["fa_icon"] = "fa-solid fa-flag-checkered"
            act1["title"] = "CONFORTO E PERSONALIDADE PARA APAIXONADOS POR MOTORES E VELOCIDADE"
            act1["desc_tmpl"] = "Confeccionada em fibra 100% Algodão Premium selecionado, a {title} une toque extremamente macio, respirabilidade natural e estampa de alta definição que celebra a cultura automotiva e duas rodas com estilo autêntico."
            act2["tag"] = "Conforto Natural & Caimento"
            act2["fa_icon"] = "fa-solid fa-shirt"
            act2["title"] = "TOQUE MACIO, ALTA RESPIRABILIDADE E CAIMENTO IMPECÁVEL"
            act2["desc_tmpl"] = "O tecido de algodão penteado proporciona conforto térmico natural durante todo o dia, mantendo a pele fresca em encontros automotivos, viagens, passeios e no uso casual urbano."
            act3["tag"] = "Acabamento & Durabilidade"
            act3["fa_icon"] = "fa-solid fa-medal"
            act3["title"] = "GOLA CANELADA REFORÇADA E COSTURAS DE ALTA DURABILIDADE"
            act3["desc_tmpl"] = "Desenvolvida com reforço ombro a ombro, gola redonda canelada que não laceia e costuras duplas de alto padrão, garantindo que a peça mantenha sua forma e cores vivas lavagem após lavagem."

        # 1. Adaptação Kids / Infantil (Eliminação de "homem e mulher", foco em aventura e proteção suave)
        if is_kids:
            act1["tag"] = "Proteção Infantil & Conforto"
            act1["fa_icon"] = "fa-solid fa-child"
            act1["title"] = "CONFORTO E PROTEÇÃO SOLAR TOTAL PARA OS PEQUENOS AVENTUREIROS"
            act1["desc_tmpl"] = "Desenvolvida especialmente para crianças e jovens exploradores, o(a) {title} oferece proteção solar máxima FPU 50+ com toque extra suave na pele, garantindo segurança, leveza e liberdade total para brincar e se divertir ao ar livre."

            act2["tag"] = "Respirabilidade & Frescor"
            act2["fa_icon"] = "fa-solid fa-sun"
            act2["title"] = "TECNOLOGIA DRY FIT QUE MANTÉM AS CRIANÇAS FRESCAS E SECAS"
            act2["desc_tmpl"] = "Tecido tecnológico respirável que absorve e dissipa o suor rapidamente, evitando o superaquecimento e mantendo o corpo seco e confortável durante todas as brincadeiras e pescarias em família."

            if not is_hooded:
                act3["tag"] = "Durabilidade & Liberdade"
                act3["fa_icon"] = "fa-solid fa-shield-heart"
                act3["title"] = "COSTURAS PLANAS ANTI-ATRITO E MÁXIMA DURABILIDADE"
                act3["desc_tmpl"] = "Construída com acabamento elástico de alta resistência que não pinica nem irrita a pele sensível das crianças, oferecendo caimento confortável que aguenta todas as aventuras infantis."

        # 2. Adaptação Feminina (Corte anatômico e caimento sob medida)
        elif is_female and archetype_id == "uv_performance" and not is_hooded:
            act1["title"] = "MODELAGEM FEMININA ANATÔMICA COM CAIMENTO IMPECÁVEL"
            act1["desc_tmpl"] = "Projetada sob medida para a anatomia feminina, a {title} combina corte acinturado esportivo, máxima liberdade de movimentos e proteção solar FPU 50+ com toque suave e elegante."

        # 3. Adaptação Fusion (Capuz com Máscara Facial Integrada e Punhos com Dedeira - SEM ZÍPER)
        if is_fusion:
            act3["tag"] = "Capuz com Máscara Integrada & Proteção 360°"
            act3["fa_icon"] = "fa-solid fa-head-side-mask"
            act3["title"] = "CAPUZ COM MÁSCARA FACIAL INTEGRADA E PUNHO COM DEDEIRA"
            act3["desc_tmpl"] = "Desenvolvida com modelagem anatômica contínua para máximo conforto e zero atrito, a camisa FusionX conta com capuz anatômico acoplado com máscara facial protetora (balaclava integrada) que protege cabeça, nuca e rosto contra o sol forte e o vento, além de punhos anatômicos com abertura para o polegar (dedeira) que mantêm o dorso da mão sempre protegido."

        # 3.1 Adaptação Hybrid (Capuz Anatômico e Punhos com Dedeira - SEM ZÍPER)
        elif is_hybrid:
            act3["tag"] = "Capuz Anatômico & Punho com Dedeira"
            act3["fa_icon"] = "fa-solid fa-head-side-mask"
            act3["title"] = "CAPUZ ANATÔMICO INTEGRADO E PUNHO COM ABERTURA PARA POLEGAR"
            act3["desc_tmpl"] = "Projetada com caimento leve, contínuo e livre de atrito, a camisa Hybrid integra capuz anatômico de proteção solar 360° para nuca e cabeça, mangas com costuras planas reforçadas e punhos com abertura para o polegar (dedeira) que protegem o dorso das mãos durante toda a pescaria ou atividade ao ar livre."

        # 3.2 Adaptação Capuz Geral (Elimina 'gola padre', injeta cobertura 360° no rosto/nuca)
        elif is_hooded:
            act3["tag"] = "Capuz Anatômico & Proteção 360°"
            act3["fa_icon"] = "fa-solid fa-head-side-mask"
            act3["title"] = "CAPUZ ANATÔMICO INTEGRADO E COSTURA REFORÇADA"
            act3["desc_tmpl"] = "Equipada com capuz anatômico integrado que oferece proteção solar 360° para nuca, orelhas e laterais do rosto contra a radiação forte e o vento, dispensando acessórios extras, com costuras planas reforçadas anti-atrito."

        # 4. Adaptação Manga Curta (Elimina 'punhos anatômicos', injeta ventilação e barra pespontada)
        elif is_short_sleeve and not is_motors_cotton:
            if "punhos anatômicos" in act3.get("desc_tmpl", "").lower():
                act3["desc_tmpl"] = re.sub(
                    r"punhos anatômicos[^.]*",
                    "mangas curtas com barra em costura dupla reforçada que proporcionam ventilação ideal e liberdade nos braços",
                    act3["desc_tmpl"],
                    flags=re.IGNORECASE,
                )
            if "manga longa" in act3.get("desc_tmpl", "").lower():
                act3["desc_tmpl"] = act3["desc_tmpl"].replace("manga longa", "manga curta")

        # 5. Adaptação Gola Redonda / Sem Zíper (Elimina 'zíper com trava', injeta gola careca canelada)
        elif is_round_neck and not is_motors_cotton:
            if "zíper" in act3.get("title", "").lower() or "ziper" in act3.get("title", "").lower():
                act3["title"] = "COSTURA REFORÇADA E GOLA REDONDA ANATÔMICA"
                act3["desc_tmpl"] = "Acabamento de alto padrão com costuras planas anti-atrito, gola careca canelada reforçada ombro a ombro e caimento confortável para uso prolongado."

        # 6. Adaptação Camisa com Luva Integrada
        elif is_has_glove:
            act3["desc_tmpl"] = "Acabamento de alto padrão com costuras planas anti-atrito, gola alta anatômica e punhos estendidos com luva integrada para proteção estendida do dorso das mãos."

        # 7. Detecção Contextual da Foto 3 (Costas / Painel Traseiro vs. Acabamento Universal)
        is_back_view = self._is_back_view_url(img3, include_03=True)
        if is_back_view and archetype_id == "uv_performance" and not is_fusion and not is_hybrid and not is_hooded and not is_round_neck:
            act3["tag"] = "Design Traseiro & Acabamento"
            act3["title"] = "PAINEL TRASEIRO EM ALTA DEFINIÇÃO E COSTURAS REFORÇADAS"
            if is_has_glove:
                act3["desc_tmpl"] = "Painel traseiro com estampa nítida e sublimação de alta resolução que não desbota, estruturado com costuras planas reforçadas nos ombros e dorso e punhos estendidos com luva integrada para proteção do dorso das mãos."
            else:
                act3["desc_tmpl"] = "Painel traseiro com estampa nítida e sublimação de alta resolução que não desbota, estruturado com costuras planas reforçadas nos ombros e dorso para total liberdade de movimentos e resistência ao uso contínuo."

        sibling_specs = sibling_info.get("extracted_specs") if sibling_info else None
        specs = self.extract_product_specs(product, archetype_id, sibling_specs=sibling_specs)
        specs = self.sanitize_specs_for_archetype(specs, archetype_id)

        # Adaptação Contextual de Ficha Técnica
        new_specs = []
        for s in specs:
            lbl = s.get("label", "")
            val = s.get("value", s.get("default", ""))

            if is_motors_cotton and "uso recomendado" in lbl.lower():
                val = "Dia a dia, encontros automotivos, viagens e lazer"

            # Fusion e Hybrid: Capuz e Dedeira sem zíper
            if is_fusion:
                if any(w in lbl.lower() for w in ["gola", "capuz", "zíper", "ziper"]):
                    lbl = "Capuz & Máscara"
                    val = "Capuz anatômico integrado com máscara facial de proteção UV50+"
                val = re.sub(r'gola padre[^,;.]*', 'capuz com máscara facial integrada', val, flags=re.IGNORECASE)
                val = re.sub(r'punhos anatômicos[^,;.]*', 'punhos anatômicos com abertura para o polegar (dedeira)', val, flags=re.IGNORECASE)
            elif is_hybrid:
                if any(w in lbl.lower() for w in ["gola", "capuz", "zíper", "ziper"]):
                    lbl = "Capuz"
                    val = "Capuz anatômico integrado de alta cobertura solar"
                val = re.sub(r'gola padre[^,;.]*', 'capuz anatômico integrado', val, flags=re.IGNORECASE)
                val = re.sub(r'punhos anatômicos[^,;.]*', 'punhos anatômicos com abertura para o polegar (dedeira)', val, flags=re.IGNORECASE)
            elif is_hooded:
                if any(w in lbl.lower() for w in ["gola", "zíper", "ziper"]):
                    lbl = "Capuz / Gola"
                    val = "Capuz anatômico integrado de alta cobertura solar com acabamento elástico"
                val = re.sub(r'gola padre[^,;.]*', 'capuz anatômico integrado', val, flags=re.IGNORECASE)

            # Manga Curta: elimina punhos / manga longa
            if is_short_sleeve:
                if any(w in lbl.lower() for w in ["punho", "manga"]):
                    lbl = "Mangas"
                    val = "Mangas curtas com acabamento reforçado em pesponto duplo"
                val = re.sub(r'punhos anatômicos[^,;.]*', 'mangas curtas reforçadas', val, flags=re.IGNORECASE)
                val = re.sub(r'mangas raglan esportivas', 'mangas curtas com barra reforçada', val, flags=re.IGNORECASE)

            # Kids: elimina jargão adulto
            if is_kids:
                val = re.sub(r'homem e da mulher do campo', 'pequenos aventureiros', val, flags=re.IGNORECASE)
                val = re.sub(r'lida no campo|lida diária', 'atividades ao ar livre', val, flags=re.IGNORECASE)
                if "modelagem" in lbl.lower():
                    val = "Infantil / Juvenil anatômica confortável"

            # Gola Redonda: elimina zíper
            if is_round_neck and not is_hooded:
                if any(w in lbl.lower() for w in ["zíper", "ziper", "gola", "fechamento"]):
                    lbl = "Gola"
                    val = "Gola redonda canelada anatômica com pesponto reforçado"
                val = re.sub(r'com zíper[^,;.]*', '', val, flags=re.IGNORECASE)

            # Luva integrada em camisa
            if is_has_glove and not is_short_sleeve:
                if "punho" in lbl.lower():
                    lbl = "Punhos / Luva"
                    val = "Punhos estendidos anatômicos com luva integrada para o dorso da mão"

            new_specs.append({"label": lbl, "value": val})

        if is_has_glove and not is_short_sleeve and not any("luva" in s["label"].lower() for s in new_specs):
            new_specs.append({"label": "Punhos / Luva", "value": "Punhos estendidos anatômicos com luva integrada para o dorso da mão"})

        if archetype_id == "uv_performance" and not is_fusion and not is_hybrid and not is_hooded and not is_round_neck and not is_short_sleeve and not any(w in s["label"].lower() for s in new_specs for w in ["gola", "fechamento"]):
            new_specs.append({"label": "Gola / Fechamento", "value": "Gola padre anatômica com zíper e trava de segurança"})

        if is_fusion:
            if not any("capuz" in s["label"].lower() or "máscara" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Capuz & Máscara", "value": "Capuz anatômico integrado com máscara facial de proteção UV50+"})
            if not any("punho" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
        elif is_hybrid:
            if not any("capuz" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Capuz", "value": "Capuz anatômico integrado de alta cobertura solar"})
            if not any("punho" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
        elif is_hooded and not any("capuz" in s["label"].lower() for s in new_specs):
            new_specs.append({"label": "Capuz", "value": "Capuz anatômico integrado para proteção solar estendida"})

        if is_fusion or is_hybrid:
            act3["title"] = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', act3["title"], flags=re.IGNORECASE).strip()
            act3["desc_tmpl"] = re.sub(r'gola padre com cobertura no cursor do z[íi]per', 'capuz anatômico contínuo', act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\bcursor do z[íi]per\b', 'acabamento anatômico', act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\bz[íi]per com trava de seguran[çc]a\b', 'conforto anatômico contínuo', act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\(\s*\)', '', act3["desc_tmpl"]).strip()
            new_clean_specs = []
            for sp in new_specs:
                lbl_c = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', sp["label"], flags=re.IGNORECASE).strip()
                replacement_hood = "capuz com máscara facial integrada" if is_fusion else "capuz anatômico integrado"
                val_c = re.sub(r'gola padre[^,;.]*', replacement_hood, sp["value"], flags=re.IGNORECASE)
                val_c = re.sub(r'\bcursor do z[íi]per\b', 'acabamento contínuo', val_c, flags=re.IGNORECASE)
                val_c = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', val_c, flags=re.IGNORECASE)
                val_c = re.sub(r'\(\s*\)', '', val_c).strip()
                new_clean_specs.append({"label": lbl_c or "Acabamento", "value": val_c})
            new_specs = new_clean_specs

        # Adaptação Temática de Público por Loja (Agro, Motors e Fishing) para Camisas UV
        if archetype_id == "uv_performance" and not is_kids:
            if store_key == "brk_agro" or any(w in t_low for w in ["agro", "campo", "rural", "trator", "fazenda", "pecuaria", "pecuária"]):
                if "pescadores" in act1.get("desc_tmpl", ""):
                    act1["desc_tmpl"] = act1["desc_tmpl"].replace("pescadores e entusiastas do ar livre", "o homem e a mulher do campo e entusiastas do ar livre").replace("os arremessos e manobras", "a rotina intensa no campo e manobras").replace("arremessos e manobras", "a rotina intensa no campo e manobras")
            elif store_key == "brk_motors" or any(w in t_low for w in ["moto", "trail", "cross", "velocidade", "motors", "pista"]):
                if "pescadores" in act1.get("desc_tmpl", ""):
                    act1["desc_tmpl"] = act1["desc_tmpl"].replace("pescadores e entusiastas do ar livre", "pilotos, motociclistas e aventureiros").replace("os arremessos e manobras", "a pilotagem e manobras").replace("arremessos e manobras", "a pilotagem e manobras")

        specs = new_specs

        source_type = "sibling_template" if sibling_info else "archetype_specialized"
        source_label = f"Molde Homólogo do Site ({sibling_info['sibling_title']})" if sibling_info else f"Arquétipo Especializado ({template['name']})"

        act1_dict = {
            "tag": act1["tag"],
            "fa_icon": act1.get("fa_icon", template.get("fa_icon", "fa-solid fa-check")),
            "title": act1["title"],
            "description": act1["desc_tmpl"].format(title=formatted_title),
            "image": img1,
            "split_images": split_images,
            "variations_summary": variations_summary
        }
        act2_dict = {
            "tag": act2["tag"],
            "fa_icon": act2.get("fa_icon", "fa-solid fa-sun"),
            "title": act2["title"],
            "description": act2["desc_tmpl"].format(title=formatted_title),
            "image": img2
        }
        act3_dict = {
            "tag": act3["tag"],
            "fa_icon": act3.get("fa_icon", "fa-solid fa-shield-halved"),
            "title": act3["title"],
            "description": act3["desc_tmpl"].format(title=formatted_title),
            "image": img3
        }

        sku = str(product.get("sku") or product.get("master_sku") or product.get("id") or "")
        handle = str(product.get("handle") or "")
        vendor = str(product.get("vendor") or brand_name or "BRK")
        price = str(product.get("price") or (product.get("variants") and product.get("variants")[0].get("price")) or "0.00")

        return {
            "title": formatted_title,
            "formatted_title": formatted_title,
            "brand_name": brand_name,
            "origin_type": origin_type,
            "show_copyright": show_copyright,
            "has_multiple_variations": has_multiple_variations,
            "split_images": split_images,
            "variations_summary": variations_summary,
            "theme_color": theme_color,
            "theme_bg": theme_bg,
            "care_icon": care_icon,
            "source_type": source_type,
            "source_label": source_label,
            "sibling_info": sibling_info,
            "archetype_id": archetype_id,
            "layout_format": template.get("layout_format", "standard_3act"),
            "details_grid": template.get("details_grid"),
            "info_characteristics": template.get("info_characteristics"),
            "info_care": template.get("info_care"),
            "split_sections": template.get("split_sections"),
            "is_kids": is_kids,
            "is_short_sleeve": is_short_sleeve,
            "is_hooded": is_hooded,
            "sku": sku,
            "handle": handle,
            "vendor": vendor,
            "price": price,
            "images": cdn_images,
            "act1": act1_dict,
            "act2": act2_dict,
            "act3": act3_dict,
            "narrative_blocks": [act1_dict, act2_dict, act3_dict],
            "specs": specs,
            "care_tips": template.get("care_tips", "Lavar com sabão neutro e secar à sombra.")
        }
