"""
BRK Studio - Replicate VTON Provider (services/studio/providers/replicate_vton.py)

Driver para o modelo oficial do GitHub yisol/IDM-VTON hospedado na nuvem.
Permite executar Virtual Try-On de alta definição em ~5 a 8 segundos.
"""

import os
import json
import time
import urllib.request
from typing import Dict, Optional

class ReplicateVTONProvider:
    # IDM-VTON versão oficial no Replicate
    MODEL_VERSION = "c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d054d3ff8"
    API_URL = "https://api.replicate.com/v1/predictions"

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.environ.get("REPLICATE_API_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.api_token and len(self.api_token.strip()) > 10)

    def generate_tryon(
        self,
        human_image_url: str,
        garment_image_url: str,
        description: str,
        category: str = "upper_body",
        denoise_steps: int = 30
    ) -> Dict:
        """
        Submete o par (modelo humano + peça BRK) para o modelo IDM-VTON.
        Retorna o dicionário de status com a URL da imagem humanizada final.
        """
        if not self.is_configured():
            return {
                "success": False,
                "provider": "replicate_idm_vton",
                "error": "REPLICATE_API_TOKEN não configurado no ambiente (.env).",
                "is_dry_run": True,
                "simulated_output_url": garment_image_url
            }

        payload = {
            "version": self.MODEL_VERSION,
            "input": {
                "human_img": human_image_url,
                "garm_img": garment_image_url,
                "garment_des": description,
                "category": category,
                "denoise_steps": denoise_steps,
                "crop": True,
                "auto_mask": True
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "BRK-Studio-VTON/1.0"
        }

        # 1. Iniciar predição
        req = urllib.request.Request(self.API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        prediction_id = data.get("id")
        get_url = data.get("urls", {}).get("get") or f"{self.API_URL}/{prediction_id}"

        # 2. Polling rápido até conclusão (média: 6 a 12 segundos)
        start_time = time.time()
        timeout_seconds = 120

        while time.time() - start_time < timeout_seconds:
            poll_req = urllib.request.Request(get_url, headers=headers)
            with urllib.request.urlopen(poll_req, timeout=20) as p_resp:
                p_data = json.loads(p_resp.read().decode("utf-8"))

            status = p_data.get("status")
            if status == "succeeded":
                output_url = p_data.get("output")
                if isinstance(output_url, list) and output_url:
                    output_url = output_url[0]

                return {
                    "success": True,
                    "provider": "replicate_idm_vton",
                    "prediction_id": prediction_id,
                    "output_url": output_url,
                    "duration_seconds": round(time.time() - start_time, 2),
                    "human_input": human_image_url,
                    "garment_input": garment_image_url
                }
            elif status == "failed":
                return {
                    "success": False,
                    "provider": "replicate_idm_vton",
                    "error": p_data.get("error", "Falha na geração do VTON"),
                    "prediction_id": prediction_id
                }

            time.sleep(2)

        return {
            "success": False,
            "provider": "replicate_idm_vton",
            "error": "Timeout aguardando processamento da GPU no Replicate.",
            "prediction_id": prediction_id
        }
