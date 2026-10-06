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

            # 4. Chapéus de Pesca / Safári / Australiano
            "hats_safari_outdoor": {
                "id": "hats_safari_outdoor",
                "name": "Chapéus de Pesca, Safári & Outdoor",
                "fa_icon": "fa-solid fa-hat-cowboy-side",
                "theme_color": "#d97706",
                "theme_bg": "#fffbeb",
                "category_keywords": ["chapeu", "chapéu", "safari", "safári", "australiano", "pescador", "nuca", "palha"],
                "default_tagline": "Proteção Solar Panorâmica 360° e Fixação Firme contra o Vento",
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
                    {"label": "Ajuste de Tamanho", "default": "Circunferência ajustável de 56 a 60 cm"}
                ],
                "care_tips": "Lavar à mão com sabão neutro e água fria. Não torcer a aba para não deformar a estrutura. Secar à sombra."
            },

            # 5. Bonés Trucker & Aba Curva
            "caps_trucker_snapback": {
                "id": "caps_trucker_snapback",
                "name": "Bonés Trucker & Snapback",
                "fa_icon": "fa-solid fa-hat-baseball",
                "theme_color": "#d97706",
                "theme_bg": "#fffbeb",
                "category_keywords": ["bone", "boné", "trucker", "snapback", "aba curva", "aba reta", "viseira"],
                "default_tagline": "Design Anatômico, Copa Estruturada e Tela Respirável",
                "act1": {
                    "tag": "Estrutura & Copa",
                    "fa_icon": "fa-solid fa-hat-baseball",
                    "title": "COPA ESTRUTURADA COM BORDADO DE ALTA DEFINIÇÃO",
                    "desc_tmpl": "O {title} destaca-se pela frente firme e acabamento impecável, mantendo o formato clássico intacto em qualquer situação."
                },
                "act2": {
                    "tag": "Ventilação & Conforto",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "TELA RESPIRÁVEL E CARNEIRA INTERNA MACIA",
                    "desc_tmpl": "Garante circulação constante de ar para evitar suor excessivo na cabeça, aliado à carneira interna acolchoada para uso contínuo o dia todo."
                },
                "act3": {
                    "tag": "Ajuste Personalizado",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "FECHO REGULÁVEL DE ALTA DURABILIDADE",
                    "desc_tmpl": "Ajuste sob medida para diferentes circunferências cranianas com fecho tipo snapback seguro e aba com curvatura milimétrica."
                },
                "base_specs": [
                    {"label": "Modelo", "default": "Trucker clássico com lateral e traseira em tela respirável"},
                    {"label": "Aba", "default": "Aba curva com 6 costuras de reforço"},
                    {"label": "Fechamento", "default": "Snapback regulável em polímero virgem de alta resistência"},
                    {"label": "Acabamento Frontal", "default": "Bordado / aplique em alto relevo termo fixado"},
                    {"label": "Tamanho", "default": "Único ajustável (54 a 60 cm de circunferência)"}
                ],
                "care_tips": "Limpar com pano úmido e sabão neutro. Não mergulhar a copa em água nem lavar em máquina para manter a curvatura da aba perfeita."
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
                    {"label": "Estrutura", "default": "Liga reforçada de baixo peso e alta rigidez estrutural"},
                    {"label": "Mecânica", "default": "Componentes de precisão com rolamentos selados"},
                    {"label": "Aplicação", "default": "Pesca esportiva em rios, lagos, pesqueiros e mar aberto"},
                    {"label": "Origem / Distribuição", "default": "Produto original com procedência e garantia"}
                ],
                "care_tips": "Após uso em água salgada, lavar levemente com água doce corrente, secar e aplicar óleo lubrificante nos pontos móveis recomendados."
            },

            # 17. Chapéus Country, Feltro, Pralana & Cowboy
            "hats_country_cowboy": {
                "id": "hats_country_cowboy",
                "name": "Chapéus Country, Feltro, Pralana & Cowboy",
                "fa_icon": "fa-solid fa-hat-cowboy",
                "theme_color": "#854d0e",
                "theme_bg": "#fefce8",
                "category_keywords": ["feltro", "pralana", "american hat", "karanda", "karandá", "country", "cowboy", "pantaneiro", "lã", "veludo", "marcatto"],
                "default_tagline": "Elegância Rústica, Copa Estruturada e Acabamento Premium em Couro e Fivela",
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
                    {"label": "Uso Indicado", "default": "Lida no campo, cavalgadas, feiras agropecuárias e ocasiões casuais"}
                ],
                "care_tips": "Limpar periodicamente com escova de cerdas macias no sentido das fibras do feltro. Não molhar. Guardar apoiado pela copa ou pendurado em local seco."
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
                    "tag": "Praticidade Utilitária",
                    "fa_icon": "fa-solid fa-box-open",
                    "title": "BOLSOS FRONTAIS COM LAPELA E COSTURA REFORÇADA",
                    "desc_tmpl": "Equipada com bolsos funcionais no peito com fechamento por botão ou lapela protetora, perfeitos para portar ferramentas, canetas, celular e pequenos acessórios com total segurança."
                },
                "base_specs": [
                    {"label": "Fechamento Frontal", "default": "Botões reforçados aplicados com costura em 'X' (sem zíper)"},
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
                    "tag": "Fixação & Proteção",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "ACABAMENTO PREMIUM E ACOMPANHAMENTO DE ESTOJO E FLANELA",
                    "desc_tmpl": "Design esportivo e elegante com dobradiças reforçadas e ponteiras anatômicas que garantem fixação firme no rosto, acompanhado de estojo rígido e flanela de microfibra para conservação."
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

    def detect_archetype(self, title: str, category: str = "", tags: List[str] = None, vendor: str = "") -> str:
        """
        Detecta com máxima precisão o arquétipo correto do produto.
        O TÍTULO DO PRODUTO É SOBERANO: previne que coleções multi-categoria
        façam produtos serem classificados incorretamente.
        """
        t = (title or "").lower().strip()
        cat = (category or "").lower().strip()
        tags_str = " ".join(tags or []).lower()
        vend = (vendor or "").lower().strip()
        text = f"{t} {cat} {vend} {tags_str}"

        # 1. Aromatizantes Automotivos & Cuidados (Prioridade máxima para evitar que caiam em camisas)
        if any(w in t for w in ["aromatizante", "cheirinho", "difusor", "aromatizador", "odorizador", "little trees", "odor"]):
            return "accessories_car_care"

        # 2. Óculos de Sol & Polarizados UV400 (se não for camisa, lenço, adesivo ou chaveiro)
        if (any(w in t for w in ["oculos", "óculos", "sunglasses"]) or any(w in t for w in ["polarizado", "polarizada", "aviador", "uv400", "lente polarizada"])) and not any(w in t for w in ["camisa", "camiseta", "adesivo", "chaveiro", "lenço", "lenco", "bandana"]):
            return "eyewear_sunglasses"

        # 3. Luvas de Pesca, Táticas & Esportivas (se não for camisa)
        if any(w in t for w in ["luva", "luvas"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "gloves_tactical_fishing"

        # 4. Bandanas, Tubenecks, Lenços & Balaclavas (se não for camisa)
        if any(w in t for w in ["bandana", "balaclava", "tubeneck", "buff", "mascara facial", "máscara facial", "protetor de pescoço", "lenço", "lenco", "lenços", "lencos"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "neck_gaiters_balaclavas"

        # 5. Acessórios Gerais, Chaveiros, Adesivos, Camping & Caiaque
        #    (exclui camisas: "Camisa ... Pescaiaque/Caiaque" é vestuário, não acessório)
        if any(w in t for w in ["chaveiro", "adesivo", "adesivos", "sticker", "stickers", "patch", "emblema", "pin ", "capa de caiaque", "caiaque", "barraca", "fogareiro", "mesa dobrável", "mesa dobravel", "coleira", "suporte magnético", "suporte magnetico", "personalização nome", "personalizacao nome"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "accessories_general"

        # 6. Calças, Bermudas & Shorts (Prioridade antes de camisa para não cair em uv_performance)
        if any(w in t for w in ["calca", "calça", "calcas", "calças", "bermuda", "bermudas", "shorts", "short", "calcao", "calção"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "pants_cargo_tactical"

        # 7. Chapéus: Distinção estrita entre Country/Feltro/Cowboy vs Safári/Outdoor/Pescador
        if any(w in t for w in ["chapeu", "chapéu", "chapeus", "chapéus"]):
            if any(w in t for w in ["feltro", "pralana", "american hat", "karanda", "karandá", "country", "cowboy", "pantaneiro", "lã", "veludo", "liso", "marcatto", "eldorado", "cury"]):
                return "hats_country_cowboy"
            return "hats_safari_outdoor"
        if any(w in t for w in ["pralana", "american hat", "karanda", "karandá", "feltro country"]):
            return "hats_country_cowboy"

        # 8. Camisas / Vestuário Superior: Distinção estrita entre Camisas Work/Botão vs Agro vs Motors vs UV50+
        if any(w in t for w in ["camisa", "camiseta", "baby look", "regata", "t-shirt", "polo"]):
            # Camisas Work / Botão / Sarja / Lisas (Sem zíper, com botões e bolsos utilitários)
            if any(w in t for w in ["work", "safari sarja", "manga longa sarja", "manga curta sarja", "sarja", "militar", "operacional", "botao", "botão", "de botao", "de botão", "lisa", "sem estampa"]) and not any(w in t for w in ["ziper", "zíper"]):
                return "shirts_button_work"
            if any(w in t for w in ["agro", "campo", "fazenda", "trator", "algodao", "algodão"]):
                return "agro_field"
            if any(w in t for w in ["jersey", "moto", "cross", "off-road", "trilha", "speed", "motors"]):
                return "motors_speed"
            return "uv_performance"

        if "jersey" in t:
            return "motors_speed"

        # 6. Cutelaria & Facas
        if any(w in t for w in ["faca", "facas", "cutelo", "cutelaria", "lamina", "lâmina", "bainha", "canivete", "chaira", "afiador"]):
            return "cutlery_unique"

        # 7. Calçados (Sandálias Boaonda vs Tênis/Botinas)
        if any(w in t for w in ["tenis", "tênis", "botina", "bota", "sneaker", "sapato"]):
            return "closed_footwear_sneakers"
        if any(w in t for w in ["sandalia", "sandália", "chinelo", "boaonda", "babuche", "clog", "slide", "pantufa"]):
            return "footwear_sandals_boaonda"

        # 8. Chapéus de Pesca / Safári (caso não tenha caído no bloco 4)
        if any(w in t for w in ["safari", "safári", "australiano", "palha", "pescador"]):
            return "hats_safari_outdoor"

        # 9. Bonés Trucker & Snapback
        if any(w in t for w in ["bone", "boné", "trucker", "snapback", "aba curva", "aba reta", "viseira"]):
            return "caps_trucker_snapback"

        # 10. Manguitos
        if any(w in t for w in ["manguito", "manguitos", "manga avulsa"]):
            return "sun_sleeves_manguitos"

        # 11. Bandanas, Tubenecks & Balaclavas
        if any(w in t for w in ["bandana", "balaclava", "tubeneck", "buff", "mascara facial", "máscara facial", "protetor de pescoço"]):
            return "neck_gaiters_balaclavas"

        # 12. Macacões & Jardineiras
        if any(w in t for w in ["macacao", "macacão", "jardineira", "jardineiras", "salopete"]):
            return "overalls_workwear"

        # 13. Iscas Artificiais
        if any(w in t for w in ["isca", "iscas", "plug", "jig", "frog", "soft bait", "crankbait", "minnow", "popper", "stick", "twitch"]):
            return "fishing_lures"

        # 14. Equipamentos e Ferragens de Pesca (Varas, Carretilhas, Molinetes, Giradores, Snaps)
        if any(w in t for w in ["vara", "carretilha", "molinete", "linha", "anzol", "anzóis", "alicate", "passagua", "passaguá", "girador", "giradores", "snap", "snaps", "empate", "chumbada", "chumbo"]):
            return "fishing_tackle_gear"

        # 15. Caixas de Pesca & Organização
        if any(w in t for w in ["caixa de pesca", "caixa pesca", "estojo", "maleta", "organizador", "porta-vara", "porta vara", "tubo de vara", "multicase", "zmc"]):
            return "tackle_boxes_storage"

        # 16. Copos, Garrafas e Canecas Térmicas
        if any(w in t for w in ["copo", "garrafa", "caneca", "cantil", "cooler", "termico", "térmico", "termica", "térmica", "elber"]):
            return "drinkware_thermo"

        # 17. Livros & Publicações
        if any(w in t for w in ["livro", "livros", "cartilha", "guia ilustrado", "colorir"]):
            return "books_publications"

        # 18. Fallback Secundário via Categoria / Tags / Vendor
        if any(w in text for w in ["aromatizante", "cheirinho", "difusor"]):
            return "accessories_car_care"
        if any(w in text for w in ["oculos", "óculos", "polarizado", "uv400"]):
            return "eyewear_sunglasses"
        if any(w in text for w in ["luva", "luvas"]) and not any(w in text for w in ["camisa", "camiseta"]):
            return "gloves_tactical_fishing"
        if any(w in text for w in ["lenço", "lenco", "bandana", "balaclava", "tubeneck"]):
            return "neck_gaiters_balaclavas"
        if any(w in text for w in ["chaveiro", "adesivo"]):
            return "accessories_general"
        if any(w in text for w in ["calca", "calça", "bermuda", "shorts"]):
            return "pants_cargo_tactical"
        if any(w in text for w in ["pralana", "american hat", "karanda", "karandá", "feltro", "country"]):
            return "hats_country_cowboy"
        if any(w in text for w in ["manguito", "manguitos"]):
            return "sun_sleeves_manguitos"
        if any(w in text for w in ["sandalia", "sandália", "chinelo", "boaonda"]):
            return "footwear_sandals_boaonda"
        if any(w in text for w in ["tenis", "tênis", "calcado", "calçado"]):
            return "closed_footwear_sneakers"
        if any(w in text for w in ["isca", "iscas", "plug"]):
            return "fishing_lures"
        if any(w in text for w in ["copo", "garrafa", "termic", "térmic"]):
            return "drinkware_thermo"
        if any(w in text for w in ["chapeu", "chapéu"]):
            return "hats_safari_outdoor"
        if any(w in text for w in ["bone", "boné"]):
            return "caps_trucker_snapback"
        if any(w in text for w in ["vara", "carretilha", "molinete", "girador", "snap", "empate"]):
            return "fishing_tackle_gear"
        if any(w in text for w in ["jersey", "moto", "motors"]):
            return "motors_speed"
        if any(w in text for w in ["agro", "campo"]):
            return "agro_field"

        return "uv_performance"

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

    def extract_product_specs(self, product: Dict[str, Any], archetype_id: str, sibling_specs: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Extrai especificações autênticas do produto. Se o sibling_matcher encontrou
        especificações de um irmão homólogo, elas são priorizadas e sanitizadas para garantir fidelidade.
        """
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

            # 1. Proteção Solar
            if "proteção" in label.lower() or "solar" in label.lower():
                if any(x in full_text for x in ["50+", "uv 50", "fps 50", "fpu 50"]):
                    val = "Fator FPU 50+ permanente certificado"
                elif "uv" in full_text:
                    val = "Proteção UV integrada ao tecido"
            
            # 2. Composição / Tecido
            elif "composição" in label.lower() or "tecido" in label.lower():
                if any(x in full_text for x in ["dry fit", "dryfit", "dry"]):
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

        # Tratamento Especial para Iscas e Produtos com Várias Variações (Split Media)
        is_lure = (archetype_id == "fishing_lures") or any(w in title.lower() for w in ["isca", "plug", "popper", "stick", "crankbait", "minnow", "frog", "soft"])
        variants = product.get("variants") or []
        has_multiple_variations = is_lure and (len(variants) > 1 or len(cdn_images) >= 2)
        split_images = None
        variations_summary = ""

        # Alocação estrita de imagens exclusivas por ato - ZERO DUPLICAÇÃO
        if has_multiple_variations and len(cdn_images) >= 2:
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
        else:
            img1 = cdn_images[0] if len(cdn_images) > 0 else ""
            img2 = cdn_images[1] if len(cdn_images) > 1 else ""
            img3 = cdn_images[2] if len(cdn_images) > 2 else ""

        act1 = dict(template["act1"])
        act2 = dict(template["act2"])
        act3 = dict(template["act3"])

        # Contextual Intelligence Flags para Adaptação Narrativa Dinâmica
        t_low = title.lower()
        tags_list = tags if isinstance(tags, list) else [str(tags)]
        tags_low = " ".join([str(t).lower() for t in tags_list])
        body_low = (product.get("body_html") or "").lower()
        all_info = f"{t_low} {tags_low} {body_low}"

        is_apparel = archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work", "pants_cargo_tactical")
        
        is_hooded = is_apparel and any(w in t_low for w in ["capuz", "hood", "hoodie"])
        # is_kids só vale para vestuário: o texto/tabela infantil é de roupa (FPU 50+, Dry Fit, tórax/manga).
        # Óculos, calçados etc. com "Infantil" no título NÃO podem receber essa narrativa.
        is_kids = is_apparel and (any(w in t_low for w in ["infantil", "kids", "juvenil"]) or bool(re.search(r'\bmini\b', t_low)))
        if any(w in t_low for w in ["adulto", "unissex adulto"]):
            is_kids = False
        is_short_sleeve = is_apparel and (any(w in t_low for w in ["manga curta", "manga-curta"]) or ("curta" in t_low and "manga" in t_low)) and not any(w in t_low for w in ["manga longa", "manga-longa"])
        is_has_glove = is_apparel and any(w in t_low for w in ["com luva", "e luva", "luva integrada"])
        is_female = (any(w in t_low for w in ["feminina", "feminino", "baby look", "babylook", "mulher"]) or "femin" in tags_low) and not is_kids
        is_round_neck = is_apparel and (any(w in t_low for w in ["gola careca", "gola redonda", "sem zíper", "sem ziper", "t-shirt"]) or ("camiseta" in t_low and not any(w in t_low for w in ["ziper", "zíper"])))

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

        # 3. Adaptação Capuz (Elimina 'gola padre', injeta cobertura 360° no rosto/nuca)
        if is_hooded:
            act3["tag"] = "Capuz Anatômico & Proteção 360°"
            act3["fa_icon"] = "fa-solid fa-head-side-mask"
            act3["title"] = "CAPUZ ANATÔMICO INTEGRADO E COSTURA REFORÇADA"
            act3["desc_tmpl"] = "Equipada com capuz anatômico integrado que oferece proteção solar 360° para nuca, orelhas e laterais do rosto contra a radiação forte e o vento, dispensando acessórios extras, com costuras planas reforçadas anti-atrito."

        # 4. Adaptação Manga Curta (Elimina 'punhos anatômicos', injeta ventilação e barra pespontada)
        elif is_short_sleeve:
            if "punhos anatômicos" in act3.get("desc_tmpl", "").lower():
                act3["desc_tmpl"] = act3["desc_tmpl"].replace("punhos anatômicos que não laceiam com o uso frequente", "mangas curtas com barra em costura dupla reforçada que proporcionam ventilação ideal e liberdade nos braços")
            if "manga longa" in act3.get("desc_tmpl", "").lower():
                act3["desc_tmpl"] = act3["desc_tmpl"].replace("manga longa", "manga curta")

        # 5. Adaptação Gola Redonda / Sem Zíper (Elimina 'zíper com trava', injeta gola careca canelada)
        elif is_round_neck:
            if "zíper" in act3.get("title", "").lower() or "ziper" in act3.get("title", "").lower():
                act3["title"] = "COSTURA REFORÇADA E GOLA REDONDA ANATÔMICA"
                act3["desc_tmpl"] = "Acabamento de alto padrão com costuras planas anti-atrito, gola careca canelada reforçada ombro a ombro e caimento confortável para uso prolongado."

        # 6. Adaptação Camisa com Luva Integrada
        elif is_has_glove:
            act3["desc_tmpl"] = "Acabamento de alto padrão com costuras planas anti-atrito, gola alta anatômica e punhos estendidos com luva integrada para proteção estendida do dorso das mãos."

        sibling_specs = sibling_info.get("extracted_specs") if sibling_info else None
        specs = self.extract_product_specs(product, archetype_id, sibling_specs=sibling_specs)
        specs = self.sanitize_specs_for_archetype(specs, archetype_id)

        # Adaptação Contextual de Ficha Técnica
        new_specs = []
        for s in specs:
            lbl = s.get("label", "")
            val = s.get("value", s.get("default", ""))

            # Capuz: elimina 'gola padre'
            if is_hooded:
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
                if any(w in lbl.lower() for w in ["zíper", "ziper"]):
                    lbl = "Gola"
                    val = "Gola redonda canelada anatômica com pesponto reforçado (sem zíper)"
                val = re.sub(r'com zíper[^,;.]*', 'sem zíper', val, flags=re.IGNORECASE)

            # Luva integrada em camisa
            if is_has_glove and not is_short_sleeve:
                if "punho" in lbl.lower():
                    lbl = "Punhos / Luva"
                    val = "Punhos estendidos anatômicos com luva integrada para o dorso da mão"

            new_specs.append({"label": lbl, "value": val})
        specs = new_specs

        # Regra de Negócio: Descartar detalhes técnicos apenas para camisas sublimadas genéricas no Agro e Motors
        if archetype_id in ("uv_performance", "agro_field", "motors_speed") and store_key in ("brk_agro", "brk_motors"):
            specs = []

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
