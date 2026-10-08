"""
BRK Studio - Master Orchestrator (services/studio/studio_orchestrator.py)

Orquestrador central do Estúdio de Fotos Humanizadas da BRK.
Conecta o catálogo da Shopify, o processador de mockups, as personas e os
motores de IA (IDM-VTON, CatVTON e Imagen 3).
"""

import os
import json
import base64
import urllib.request
from typing import Dict, Optional, List

from .persona_manager import persona_manager, Persona
from .garment_processor import garment_processor
from .providers.replicate_vton import ReplicateVTONProvider
from .providers.gemini_imagen import GeminiImagenProvider
from .providers.colab_runner import ColabVTONProvider

class StudioOrchestrator:
    def __init__(self, output_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.output_dir = output_dir or os.path.join(base_dir, "data", "studio_output")
        os.makedirs(self.output_dir, exist_ok=True)

        self.replicate_provider = ReplicateVTONProvider()
        self.gemini_provider = GeminiImagenProvider()
        self.colab_provider = ColabVTONProvider()

    def generate_humanized_photo(
        self,
        product: dict,
        store_key: str = "brk_fishing",
        persona_id: Optional[str] = None,
        provider: str = "auto"
    ) -> Dict:
        """
        Gera uma foto humanizada de alta definição para o produto.
        """
        sku = str(product.get("master_sku") or product.get("sku") or "ITEM")
        title = product.get("title", "")

        # 1. Seleção da Persona
        if persona_id:
            persona = persona_manager.get(persona_id)
            if not persona:
                raise ValueError(f"Persona '{persona_id}' não encontrada no catálogo.")
        else:
            persona = persona_manager.get_default_for_product(product, store_key)

        # 2. Processamento do Mockup / Peça
        garment_info = garment_processor.download_and_prepare_garment(product)
        garment_url = garment_info["original_url"]

        # Descrição rica da peça para guiar o modelo de IA
        garment_desc = f"{title}. Vestuário técnico oficial BRK com proteção UV50+, estampas nítidas e modelagem esportiva."

        # 3. Execução pelo Provedor Selecionado
        selected_provider = provider
        if selected_provider == "auto":
            if self.replicate_provider.is_configured():
                selected_provider = "replicate"
            elif self.colab_provider.is_configured():
                selected_provider = "colab"
            elif self.gemini_provider.is_configured():
                selected_provider = "gemini"
            else:
                # Simulação / Dry-Run orientada
                selected_provider = "dry_run"

        sku_dir = os.path.join(self.output_dir, store_key, sku)
        os.makedirs(sku_dir, exist_ok=True)

        if selected_provider == "replicate":
            result = self.replicate_provider.generate_tryon(
                human_image_url=persona.base_model_url,
                garment_image_url=garment_url,
                description=garment_desc
            )
            if result.get("success") and result.get("output_url"):
                # Baixar e salvar foto final
                out_filename = f"{sku}_{persona.persona_id}_humanized.jpg"
                out_path = os.path.join(sku_dir, out_filename)
                self._download_file(result["output_url"], out_path)
                result["local_path"] = out_path

        elif selected_provider == "colab":
            result = self.colab_provider.generate_tryon(
                human_image_url=persona.base_model_url,
                garment_image_url=garment_url,
                description=garment_desc
            )
            if result.get("success") and result.get("output_url"):
                out_filename = f"{sku}_{persona.persona_id}_colab.jpg"
                out_path = os.path.join(sku_dir, out_filename)
                self._download_file(result["output_url"], out_path)
                result["local_path"] = out_path

        elif selected_provider == "gemini":
            full_prompt = f"{persona.prompt_scene} The person is wearing: {title}, with vivid high-resolution graphics, realistic cloth physics and accurate colors."
            result = self.gemini_provider.generate_lifestyle_scene(prompt=full_prompt)
            if result.get("success") and result.get("image_base64"):
                out_filename = f"{sku}_{persona.persona_id}_gemini.jpg"
                out_path = os.path.join(sku_dir, out_filename)
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(result["image_base64"]))
                result["local_path"] = out_path

        else: # dry_run
            out_filename = f"{sku}_{persona.persona_id}_dryrun.json"
            out_path = os.path.join(sku_dir, out_filename)
            result = {
                "success": True,
                "provider": "dry_run_simulation",
                "message": "Simulação de pipeline realizada com sucesso. Para gerar a imagem real, configure REPLICATE_API_TOKEN ou COLAB_GRADIO_URL.",
                "human_model": persona.base_model_url,
                "garment_url": garment_url,
                "persona": persona.to_dict(),
                "sku": sku,
                "title": title
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            result["local_path"] = out_path

        result["sku"] = sku
        result["persona_id"] = persona.persona_id
        result["store_key"] = store_key
        result["garment_processed"] = garment_info
        return result

    def _download_file(self, url: str, target_path: str):
        req = urllib.request.Request(url, headers={"User-Agent": "BRK-Studio/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(target_path, "wb") as f:
                f.write(resp.read())

    def list_available_personas(self, store_key: Optional[str] = None) -> List[Dict]:
        if store_key:
            return [p.to_dict() for p in persona_manager.list_by_store(store_key)]
        return [p.to_dict() for p in persona_manager.all_personas()]

studio_orchestrator = StudioOrchestrator()
