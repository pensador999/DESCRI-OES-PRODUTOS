"""
BRK Studio - Persona Manager (services/studio/persona_manager.py)

Gerencia o catálogo de personas humanas padronizadas e cenários de lifestyle
para as 3 lojas do ecossistema BRK (Fishing, Agro e Motors).
"""

from typing import Dict, List, Optional

class Persona:
    def __init__(
        self,
        persona_id: str,
        store_key: str,
        gender: str,
        name: str,
        setting: str,
        prompt_scene: str,
        recommended_for: List[str],
        base_model_url: Optional[str] = None
    ):
        self.persona_id = persona_id
        self.store_key = store_key
        self.gender = gender
        self.name = name
        self.setting = setting
        self.prompt_scene = prompt_scene
        self.recommended_for = recommended_for
        self.base_model_url = base_model_url

    def to_dict(self) -> Dict:
        return {
            "persona_id": self.persona_id,
            "store_key": self.store_key,
            "gender": self.gender,
            "name": self.name,
            "setting": self.setting,
            "prompt_scene": self.prompt_scene,
            "recommended_for": self.recommended_for,
            "base_model_url": self.base_model_url
        }

class PersonaManager:
    def __init__(self):
        self._personas: Dict[str, Persona] = {}
        self._register_default_personas()

    def _register_default_personas(self):
        # -------------------------------------------------------------
        # BRK FISHING: Cenários de Pesca Esportiva & Águas Brasileiras
        # -------------------------------------------------------------
        self.register(Persona(
            persona_id="fishing_male_boat",
            store_key="brk_fishing",
            gender="masculino",
            name="Pescador Esportivo no Barco (Golden Hour)",
            setting="Barco de alumínio ou Bass Boat em rio brasileiro",
            prompt_scene=(
                "Photorealistic professional lifestyle commercial shot of an athletic Brazilian male sport fisherman "
                "(35 years old), tanned skin, standing on an aluminum bass boat in the middle of a calm Amazonian or Pantanal river. "
                "Warm golden hour sunset lighting, clear reflections on the water, lush riverbank rainforest in soft background bokeh. "
                "He is wearing polar sunglasses resting on the collar or forehead, smiling naturally looking at the horizon. "
                "Ultra-realistic textile folds, crisp fabric weave, dynamic natural outdoor posture."
            ),
            recommended_for=["uv_performance", "caps_trucker_snapback", "neck_gaiters_balaclavas"],
            base_model_url="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=1000&q=80"
        ))

        self.register(Persona(
            persona_id="fishing_female_boat",
            store_key="brk_fishing",
            gender="feminina",
            name="Pescadora Esportiva em Ação",
            setting="Deck de embarcação esportiva com sol suave",
            prompt_scene=(
                "Photorealistic commercial outdoor fashion shot of an energetic Brazilian female sport angler "
                "(28 years old), athletic posture, ponytail hair, standing on the deck of a modern fishing boat. "
                "Gentle morning sun lighting, blue lake water background with soft natural blur. "
                "Confident cheerful expression, natural hands resting comfortably, authentic outdoor fishing atmosphere. "
                "Perfect tailored fit, clean clothing seams, photorealistic skin and fabric texture."
            ),
            recommended_for=["uv_performance", "caps_trucker_snapback", "sun_sleeves_manguitos"],
            base_model_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1000&q=80"
        ))

        # -------------------------------------------------------------
        # BRK AGRO: Campo, Fazenda, Pasto e Lavoura
        # -------------------------------------------------------------
        self.register(Persona(
            persona_id="agro_male_farm",
            store_key="brk_agro",
            gender="masculino",
            name="Produtor Rural no Campo & Pecuária",
            setting="Pasto verdejante ou lavoura com caminhonete 4x4",
            prompt_scene=(
                "Photorealistic lifestyle commercial photograph of a rugged Brazilian agribusiness farmer and rancher "
                "(38 years old), strong posture, standing in a vast green pasture with high-grade cattle and a modern 4x4 pickup truck in the background. "
                "Crisp natural daylight with soft clouds, wide agricultural horizon. Leather belt, confident respectful country look. "
                "The shirt fits comfortably with realistic cotton-polyester tension, sharp collars and cuffs."
            ),
            recommended_for=["uv_performance", "shirts_button_work", "caps_trucker_snapback", "hats_country_cowboy"],
            base_model_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=1000&q=80"
        ))

        self.register(Persona(
            persona_id="agro_female_field",
            store_key="brk_agro",
            gender="feminina",
            name="Mulher do Agronegócio na Lavoura",
            setting="Plantação de soja ou milho com maquinário moderno",
            prompt_scene=(
                "Photorealistic commercial shot of an active Brazilian woman working in agribusiness "
                "(32 years old), standing by the edge of an expansive golden grain field with modern green agricultural machinery softly blurred behind. "
                "Warm natural sunlight, proud and welcoming smile, authentic country lifestyle ambiance. "
                "Flawless tailored fit of the garment, vibrant colors and sharp graphic details."
            ),
            recommended_for=["uv_performance", "caps_trucker_snapback", "hats_safari_outdoor"],
            base_model_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=1000&q=80"
        ))

        # -------------------------------------------------------------
        # BRK MOTORS: Estrada, Serra e Motociclismo de Aventura
        # -------------------------------------------------------------
        self.register(Persona(
            persona_id="motors_male_serra",
            store_key="brk_motors",
            gender="masculino",
            name="Piloto de Aventura na Serra (Big Trail)",
            setting="Curvas de serra montanhosa (Serra do Rio do Rastro)",
            prompt_scene=(
                "High-octane commercial lifestyle photograph of an adventure motorcycle rider "
                "(36 years old), athletic build, leaning with confidence beside a modern adventure big-trail motorcycle on a winding mountain road lookout (Serra do Rio do Rastro). "
                "Dramatic mountain peaks, misty winding asphalt, cool alpine afternoon lighting. "
                "Helmet resting casually on the seat or in hand, adventure rider gloves, high-performance tech apparel posture. "
                "Exceptional fabric drape, breathable mesh side panels visible, razor-sharp details."
            ),
            recommended_for=["uv_performance", "caps_trucker_snapback", "neck_gaiters_balaclavas", "sun_sleeves_manguitos"],
            base_model_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=1000&q=80"
        ))

        self.register(Persona(
            persona_id="motors_female_trail",
            store_key="brk_motors",
            gender="feminina",
            name="Pilota de Estrada & Aventura",
            setting="Mirante de estrada cênica com moto esportiva/trail",
            prompt_scene=(
                "Dynamic professional commercial photography of a stylish female motorcycle enthusiast "
                "(30 years old), standing proud next to an adventure touring motorcycle overlooking a scenic valley. "
                "Crisp clean mountain air lighting, confident road trip warrior demeanor. "
                "Sporty ergonomic fit, vivid graphic sublimation pattern, cinematic outdoor aesthetic."
            ),
            recommended_for=["uv_performance", "caps_trucker_snapback", "neck_gaiters_balaclavas"],
            base_model_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=1000&q=80"
        ))

    def register(self, persona: Persona):
        self._personas[persona.persona_id] = persona

    def get(self, persona_id: str) -> Optional[Persona]:
        return self._personas.get(persona_id)

    def list_by_store(self, store_key: str) -> List[Persona]:
        return [p for p in self._personas.values() if p.store_key == store_key]

    def get_default_for_product(self, product: dict, store_key: str) -> Persona:
        """Seleciona a persona mais recomendada com base no título (feminino vs masculino) e loja"""
        title = (product.get("title") or "").lower()
        is_female = any(w in title for w in ["feminina", "feminino", "baby look", "mulher", "babylook"])
        
        target_gender = "feminina" if is_female else "masculino"
        candidates = [p for p in self.list_by_store(store_key) if p.gender == target_gender]
        if candidates:
            return candidates[0]
        all_store = self.list_by_store(store_key)
        return all_store[0] if all_store else list(self._personas.values())[0]

    def all_personas(self) -> List[Persona]:
        return list(self._personas.values())

persona_manager = PersonaManager()
