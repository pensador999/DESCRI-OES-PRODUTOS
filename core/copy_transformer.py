"""
Motor de Refinamento de Copywriting em 3 Atos de Alta Conversão Multi-Nicho.
Gera narrativas altamente especializadas para os 3 pilares da marca:
- BRK Fishing (Pesca Esportiva & Vestuário UV)
- BRK Agro (Campo, Agronegócio, Pecuária & Lida)
- BRK Motors (Off-road, Motocross, Trilha & Velocidade)
"""

import re
from typing import Dict, Any, List

class CopyTransformer:
    def __init__(self):
        pass

    def extract_clean_text(self, html_text: str) -> str:
        """Remove tags HTML e normaliza espaços."""
        if not html_text:
            return ""
        clean = re.sub(r'<[^>]+>', ' ', html_text)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def detect_color_and_details(self, title: str, body: str) -> Dict[str, str]:
        """Detecta variações de cor, gênero e características especiais."""
        combined = f"{title} {body}".lower()
        
        gender = "Masculina"
        if "feminin" in combined:
            gender = "Feminina"
        elif "infantil" in combined or "mirim" in combined:
            gender = "Infantil"

        color = "Exclusiva"
        colors_map = [
            ("azul claro", "Azul Claro"),
            ("azul marinho", "Azul Marinho"),
            ("azul", "Azul"),
            ("verde militar", "Verde Militar"),
            ("verde oliva", "Verde Oliva"),
            ("verde", "Verde"),
            ("preto", "Preto"),
            ("preta", "Preta"),
            ("cinza claro", "Cinza Claro"),
            ("cinza grafite", "Cinza Grafite"),
            ("cinza", "Cinza"),
            ("camuflada verde", "Camuflada Verde"),
            ("camuflada azul", "Camuflada Azul"),
            ("camuflada", "Camuflada"),
            ("areia", "Areia"),
            ("marrom", "Marrom"),
            ("bege", "Bege"),
            ("branca", "Branca"),
            ("barkeiro", "Barkeiro"),
            ("pinhal", "Pinhal"),
        ]
        for term, label in colors_map:
            if term in combined:
                color = label
                break

        return {
            "gender": gender,
            "color": color,
            "has_glove": ("luva" in combined or "punho" in combined or "passa-dedo" in combined or "armor" in combined),
            "has_zipper": ("zíper" in combined or "ziper" in combined or "gola" in combined or "armor" in combined),
            "is_bandana": ("bandana" in combined or "tubeneck" in combined or "buff" in combined)
        }

    def generate_3_act_copy(self, product_data: Dict[str, Any], images_metadata: List[Dict[str, str]], store_key: str = "brk_fishing") -> Dict[str, Any]:
        """
        Gera os 3 blocos narrativos alinhados perfeitamente com o nicho da loja e as imagens fornecidas.
        """
        title = product_data.get("title", "")
        raw_body = product_data.get("body_html", "") or ""
        clean_existing = self.extract_clean_text(raw_body)
        details = self.detect_color_and_details(title, clean_existing)

        # ----------------------------------------------------
        # 1. NICHO: BRK AGRO (Campo / Fazenda / Lida)
        # ----------------------------------------------------
        if "agro" in store_key:
            block_1 = {
                "tag": "Proteção Solar UV50+ Homologada",
                "title": "BLINDAGEM PARA A ROTINA NO CAMPO",
                "description": (
                    f"Desenvolvida para o produtor e para quem vive a lida pesada de sol a sol, a **{title}** oferece bloqueio permanente de até 98% dos raios UVA e UVB (FPU 50+). "
                    "Segurança essencial para longas horas na lavoura, manejo de gado ou operação de máquinas sem desgaste da fibra nas lavagens frequentes."
                )
            }
            block_2 = {
                "tag": "Construção de Alta Resistência",
                "title": "DURABILIDADE CONTRA O ATRITO DA LIDA",
                "description": (
                    f"Com acabamento na cor **{details['color']}**, possui costuras reforçadas ponto-a-ponto que suportam a abrasão do dia a dia no campo. "
                    "Recorte anatômico confortável que não puxa nem aperta durante o trabalho braçal, garantindo liberdade total de movimentos."
                )
            }
            block_3 = {
                "tag": "Tecido Respirável & Conforto Térmico",
                "title": "SECAGEM RÁPIDA E TOQUE SUAVE",
                "description": (
                    "O tecido com tecnologia Dry dissipa o suor e a umidade com rapidez extrema, mantendo a sensação térmica agradável mesmo sob o calor forte do cerrado e pasto. "
                    "Tratamento antibacteriano que inibe odores e poeira, além de dispensar o uso de ferro de passar."
                )
            }
            line_name = "BRK Agro Heavy Duty"

        # ----------------------------------------------------
        # 2. NICHO: BRK MOTORS (Motocross / Trilha / Off-Road)
        # ----------------------------------------------------
        elif "motors" in store_key:
            if details["is_bandana"]:
                block_1 = {
                    "tag": "Proteção Térmica & UV50+",
                    "title": "ESCUDO CONTRA VENTO, SOL E POEIRA",
                    "description": (
                        f"A **{title}** foi projetada para pilotos de moto, trilha e esportes de velocidade. "
                        "Oferece proteção solar homologada FPU 50+ e atua como barreira contra o vento forte, poeira da pista e insetos, mantendo o rosto e pescoço totalmente protegidos."
                    )
                }
                block_2 = {
                    "tag": "Elasticidade & Ajuste Anatômico",
                    "title": "VERSATILIDADE MULTIUSO",
                    "description": (
                        f"Estampa exclusiva **{details['color']}** em microfibra elástica sem costura de toque sedoso. "
                        "Pode ser usada como bandana, balaclava, máscara sob o capacete, faixa ou pescoceira, adaptando-se sem apertar ou escorregar durante a pilotagem."
                    )
                }
                block_3 = {
                    "tag": "Tecnologia Dry Respirável",
                    "title": "FLUXO DE AR E SECAGEM INSTANTÂNEA",
                    "description": (
                        "Permite respiração fluida sem embaçar os óculos ou a viseira do capacete. "
                        "A tecnologia de evaporação térmica impede o acúmulo de suor, mantendo o piloto focado e com sensação refrescante na pilotagem."
                    )
                }
                line_name = "BRK Motors Performance Gear"
            else:
                block_1 = {
                    "tag": "Proteção UV50+ & Fluxo Aerodinâmico",
                    "title": "PERFORMANCE E VELOCIDADE OFF-ROAD",
                    "description": (
                        f"Projetada para encarar pistas de motocross, trilhas fechadas e estradas, a **{title}** combina proteção solar FPU 50+ homologada com tecido de alta vazão de ar, "
                        "ideal para uso sob coletes e equipamentos de segurança sem superaquecer o corpo."
                    )
                }
                block_2 = {
                    "tag": "Engenharia de Movimento",
                    "title": "PUNHOS E COSTURAS ANATÔMICAS",
                    "description": (
                        f"Visual marcante na cor **{details['color']}** com punhos confortáveis que se adaptam perfeitamente sob luvas de pilotagem. "
                        "Costuras flexíveis resistentes à tração e ao barro, desenhadas para manter o posicionamento ideal sobre a moto."
                    )
                }
                block_3 = {
                    "tag": "Tecnologia XTech Pro Air Flow",
                    "title": "SECAGEM EXPRESSA & RESISTÊNCIA",
                    "description": (
                        "A microfibra técnica com ação Dry garante dissipação imediata da umidade e suor, mesmo nas provas e treinos mais intensos. "
                        "Não desbota com barro ou lavagens pesadas e conta com tratamento anti-odor de longa duração."
                    )
                }
                line_name = "BRK Motors Off-Road Series"

        # ----------------------------------------------------
        # 3. NICHO: BRK FISHING (Pesca Esportiva & Vestuário UV)
        # ----------------------------------------------------
        else:
            block_1 = {
                "tag": "Proteção Solar UV50+ Homologada",
                "title": "BLINDAGEM TOTAL CONTRA O SOL",
                "description": (
                    f"A **{title}** foi desenvolvida para pescadores e aventureiros que enfrentam longas jornadas sob sol intenso. "
                    "Sua tecnologia têxtil com certificação permanente bloqueia até 98% dos raios UVA e UVB (FPU 50+), "
                    "garantindo segurança absoluta para a sua pele sem sair nas lavagens."
                )
            }
            if details["has_glove"]:
                block_2 = {
                    "tag": "Luva Integrada no Punho Passa-Dedo",
                    "title": "PROTEÇÃO ATÉ O DORSO DAS MÃOS",
                    "description": (
                        f"Com acabamento na tonalidade **{details['color']}**, o punho inteligente com encaixe para o polegar mantém a manga perfeitamente posicionada "
                        "durante arremessos, recolhimentos ou pilotagem do barco. Protege o dorso das mãos contra queimaduras solares e atrito, "
                        "preservando total sensibilidade no manuseio da carretilha."
                    )
                }
            else:
                block_2 = {
                    "tag": "Engenharia & Modelagem Anatômica",
                    "title": "LIBERDADE TOTAL DE MOVIMENTOS",
                    "description": (
                        f"Costuras planas reforçadas com recorte ergonômico na cor **{details['color']}** que acompanham a movimentação natural do corpo. "
                        "Zero atrito na pele, proporcionando conforto contínuo mesmo nas pescarias mais ativas."
                    )
                }
            block_3 = {
                "tag": "Tecido XTech Pro Respirável",
                "title": "TOQUE MACIO E SECAGEM ULTRARRÁPIDA",
                "description": (
                    "Confeccionada com microfibra técnica com tecnologia Dry, a peça evapora o suor quase instantaneamente, "
                    "mantendo o corpo sempre seco e com sensação térmica agradável. Possui ação antibacteriana que inibe odores indesejados."
                )
            }
            line_name = "BRK Fishing Performance"

        # Especificações Técnicas Estruturadas
        specs = [
            {"label": "Linha", "value": line_name},
            {"label": "Proteção Solar", "value": "FPU 50+ Homologado (Bloqueia até 98% dos raios UV)"},
            {"label": "Tecido", "value": "Microfibra Técnica com Tecnologia Dry de Secagem Rápida"},
            {"label": "Acabamento", "value": f"Costuras Reforçadas • Tonalidade {details['color']}"},
            {"label": "Sensação Térmica", "value": "Toque Suave, Respirabilidade Elevada e Ação Anti-odor"},
            {"label": "Conservação", "value": "Lavagem simples, secagem rápida à sombra, não requer ferro de passar"}
        ]

        blocks = [block_1, block_2, block_3]
        narrative_items = []
        for i, img in enumerate(images_metadata):
            if i < len(blocks):
                narrative_items.append({
                    "image": img["src"],
                    "alt": img.get("alt", title),
                    "tag": blocks[i]["tag"],
                    "title": blocks[i]["title"],
                    "description": blocks[i]["description"]
                })

        return {
            "title": title,
            "color": details["color"],
            "gender": details["gender"],
            "narrative_blocks": narrative_items,
            "specs": specs
        }
