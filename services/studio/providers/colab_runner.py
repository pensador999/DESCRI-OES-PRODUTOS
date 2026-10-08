"""
BRK Studio - Google Colab VTON Runner (services/studio/providers/colab_runner.py)

Permite conectar o BRK Studio a uma instância gratuita do Google Colab (GPU T4)
rodando o repositório oficial yisol/IDM-VTON via túnel Gradio ou ngrok.
"""

import urllib.request
import json
import os
from typing import Dict, Optional

class ColabVTONProvider:
    def __init__(self, endpoint_url: Optional[str] = None):
        # Pode ser definido via variável de ambiente COLAB_GRADIO_URL ou passado diretamente
        self.endpoint_url = endpoint_url or os.environ.get("COLAB_GRADIO_URL")

    def is_configured(self) -> bool:
        return bool(self.endpoint_url and self.endpoint_url.startswith("http"))

    def get_setup_instructions(self) -> str:
        """Retorna o código Python completo pronto para rodar no Google Colab gratuitamente"""
        return """# =====================================================================
# BRK STUDIO - SERVIDOR GRATUITO VIRTUAL TRY-ON (GOOGLE COLAB GPU T4)
# 1. No Google Colab, vá em: Ambiente de Execução > Alterar Tipo de Ambiente > T4 GPU
# 2. Cole este código em uma célula e clique em Play
# =====================================================================

!git clone https://github.com/yisol/IDM-VTON.git
%cd IDM-VTON
!pip install -r requirements.txt
!pip install gradio_client torchvision diffusers accelerate

# Rodar o servidor Gradio com link público gratuito (share=True)
!python app.py --share
"""

    def generate_tryon(
        self,
        human_image_url: str,
        garment_image_url: str,
        description: str
    ) -> Dict:
        """Chama a instância do Google Colab via API"""
        if not self.is_configured():
            return {
                "success": False,
                "provider": "colab_idm_vton",
                "error": "COLAB_GRADIO_URL não configurada no ambiente.",
                "colab_instructions": self.get_setup_instructions(),
                "is_dry_run": True
            }

        api_url = f"{self.endpoint_url.rstrip('/')}/api/predict"
        payload = {
            "data": [
                {"background": human_image_url, "layers": [], "composite": None},
                garment_image_url,
                description,
                True,  # is_checked
                True,  # is_checked_crop
                30,    # denoise_steps
                42     # seed
            ]
        }

        try:
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            output = data.get("data", [])
            output_url = output[0] if output else None

            return {
                "success": True,
                "provider": "colab_idm_vton",
                "output_url": output_url,
                "human_input": human_image_url,
                "garment_input": garment_image_url
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "colab_idm_vton",
                "error": str(e)
            }
