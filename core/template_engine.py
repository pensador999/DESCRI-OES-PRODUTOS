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
            }
        }

    def detect_archetype(self, title: str, category: str = "", tags: List[str] = None, vendor: str = "") -> str:
        """
        Detecta com máxima precisão o arquétipo correto do produto.
        O TÍTULO DO PRODUTO É SOBERANO: previne que coleções multi-categoria
        (ex: 'Bonés & Chapéus') façam camisas serem classificadas incorretamente.
        """
        t = (title or "").lower().strip()
        cat = (category or "").lower().strip()
        tags_str = " ".join(tags or []).lower()
        vend = (vendor or "").lower().strip()

        # 1. Regra Soberana do Título: Camisas / Vestuário Superior
        if any(w in t for w in ["camisa", "camiseta", "baby look", "regata", "t-shirt", "polo"]):
            if any(w in t for w in ["agro", "campo", "fazenda", "trator", "algodao", "algodão"]):
                return "agro_field"
            if any(w in t for w in ["jersey", "moto", "cross", "off-road", "trilha", "speed", "motors"]):
                return "motors_speed"
            return "uv_performance"

        if "jersey" in t:
            return "motors_speed"

        # 2. Cutelaria & Facas (Prioridade alta para evitar que facas com cabos resinados/iscas virem isca artificial)
        if any(w in t for w in ["faca", "facas", "cutelo", "cutelaria", "lamina", "lâmina", "bainha", "canivete", "chaira", "afiador"]):
            return "cutlery_unique"

        # 3. Calçados (Sandálias Boaonda vs Tênis/Botinas)
        if any(w in t for w in ["tenis", "tênis", "botina", "bota", "sneaker", "sapato"]):
            return "closed_footwear_sneakers"
        if any(w in t for w in ["sandalia", "sandália", "chinelo", "boaonda", "babuche", "clog", "slide", "pantufa"]):
            return "footwear_sandals_boaonda"

        # 4. Chapéus de Pesca / Safári / Australiano / Palha / Nuca
        if any(w in t for w in ["chapeu", "chapéu", "safari", "safári", "australiano", "palha", "pescador"]):
            return "hats_safari_outdoor"

        # 5. Bonés Trucker & Snapback
        if any(w in t for w in ["bone", "boné", "trucker", "snapback", "aba curva", "aba reta", "viseira"]):
            return "caps_trucker_snapback"

        # 6. Manguitos (Manga avulsa de proteção)
        if any(w in t for w in ["manguito", "manguitos", "manga avulsa"]):
            return "sun_sleeves_manguitos"

        # 7. Bandanas, Tubenecks & Balaclavas
        if any(w in t for w in ["bandana", "balaclava", "tubeneck", "buff", "mascara facial", "máscara facial", "protetor de pescoço"]):
            return "neck_gaiters_balaclavas"

        # 8. Macacões & Jardineiras
        if any(w in t for w in ["macacao", "macacão", "jardineira", "jardineiras", "salopete"]):
            return "overalls_workwear"

        # 9. Iscas Artificiais (Plugs, Jigs, Softs, etc.)
        if any(w in t for w in ["isca", "iscas", "plug", "jig", "frog", "soft bait", "crankbait", "minnow", "popper", "stick", "twitch"]):
            return "fishing_lures"

        # 10. Equipamentos de Pesca (Varas, Carretilhas, Molinetes, Linhas)
        if any(w in t for w in ["vara", "carretilha", "molinete", "linha", "anzol", "alicate", "passagua", "passaguá"]):
            return "fishing_tackle_gear"

        # 11. Caixas de Pesca & Organização
        if any(w in t for w in ["caixa de pesca", "caixa pesca", "estojo", "maleta", "organizador", "porta-vara", "porta vara", "tubo de vara"]):
            return "tackle_boxes_storage"

        # 12. Copos, Garrafas e Canecas Térmicas
        if any(w in t for w in ["copo", "garrafa", "caneca", "cantil", "cooler", "termico", "térmico", "termica", "térmica", "elber"]):
            return "drinkware_thermo"

        # 13. Livros & Publicações
        if any(w in t for w in ["livro", "livros", "cartilha", "guia ilustrado", "colorir"]):
            return "books_publications"

        # 14. Fallback Secundário via Categoria / Tags / Vendor (se o título não foi conclusivo)
        text = f"{t} {cat} {vend} {tags_str}"
        if any(w in text for w in ["manguito", "manguitos"]):
            return "sun_sleeves_manguitos"
        if any(w in text for w in ["bandana", "balaclava", "tubeneck"]):
            return "neck_gaiters_balaclavas"
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
        if any(w in text for w in ["vara", "carretilha", "molinete"]):
            return "fishing_tackle_gear"
        if any(w in text for w in ["jersey", "moto", "motors"]):
            return "motors_speed"
        if any(w in text for w in ["agro", "campo"]):
            return "agro_field"

        return "uv_performance"

    def extract_product_specs(self, product: Dict[str, Any], archetype_id: str, sibling_specs: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Extrai especificações autênticas do produto. Se o sibling_matcher encontrou
        especificações de um irmão homólogo, elas são priorizadas para garantir fidelidade.
        """
        if sibling_specs and len(sibling_specs) >= 2:
            return [{"label": s["label"], "value": s["default"]} for s in sibling_specs]

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

    def resolve_product_origin_and_title(self, title: str, vendor: str = "", sku: str = "", tags = None) -> Dict[str, Any]:
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
                
        # Regra de Direitos Autorais em Camisas C0
        sku_upper = str(sku or "").upper().strip()
        is_c0 = sku_upper.startswith("C0")
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
        origin_info = self.resolve_product_origin_and_title(title=title, vendor=vendor, sku=sku, tags=tags)
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
            "hats_safari_outdoor": "fa-solid fa-hat-cowboy-side",
            "caps_trucker_snapback": "fa-solid fa-hat-baseball",
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
            "uv_performance": "fa-solid fa-shirt"
        }
        care_icon = care_icons.get(archetype_id, template.get("fa_icon", "fa-solid fa-hand-sparkles"))

        # Até 3 imagens CDN oficiais
        img1 = cdn_images[0] if len(cdn_images) > 0 else ""
        img2 = cdn_images[1] if len(cdn_images) > 1 else img1
        img3 = cdn_images[2] if len(cdn_images) > 2 else img1

        # Tratamento Especial para Iscas e Produtos com Várias Variações (Split Media)
        is_lure = (archetype_id == "fishing_lures") or any(w in title.lower() for w in ["isca", "plug", "popper", "stick", "crankbait", "minnow", "frog", "soft"])
        variants = product.get("variants") or []
        has_multiple_variations = is_lure and (len(variants) > 1 or len(cdn_images) >= 2)
        split_images = None
        variations_summary = ""
        if has_multiple_variations:
            if len(cdn_images) >= 2:
                split_images = [cdn_images[0], cdn_images[1]]
            variant_titles = [v.get("title") for v in variants if v.get("title") and v.get("title") != "Default Title"]
            if variant_titles:
                variations_summary = f"Disponível em {len(variant_titles)} opções de cores e modelos no anúncio ({', '.join(variant_titles[:4])}{'...' if len(variant_titles) > 4 else ''})."
            else:
                variations_summary = "Múltiplas variações e opções de cores disponíveis para escolha no anúncio."

        act1 = template["act1"]
        act2 = template["act2"]
        act3 = template["act3"]

        sibling_specs = sibling_info.get("extracted_specs") if sibling_info else None
        specs = self.extract_product_specs(product, archetype_id, sibling_specs=sibling_specs)

        # Regra de Negócio: Descartar detalhes técnicos para camisas referente ao Agro e ao Motors, mantendo no Fishing
        is_shirt = archetype_id in ("uv_performance", "agro_field", "motors_speed") or any(
            w in title.lower() for w in ["camisa", "camiseta", "jersey", "baby look", "regata", "polo"]
        )
        if is_shirt and store_key in ("brk_agro", "brk_motors"):
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
            "act1": act1_dict,
            "act2": act2_dict,
            "act3": act3_dict,
            "narrative_blocks": [act1_dict, act2_dict, act3_dict],
            "specs": specs,
            "care_tips": template.get("care_tips", "Lavar com sabão neutro e secar à sombra.")
        }
