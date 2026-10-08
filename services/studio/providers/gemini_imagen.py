"""
BRK Studio - Gemini / Imagen Provider (services/studio/providers/gemini_imagen.py)

Driver para geração de cenas e fotos lifestyle com Google Imagen 3 / Gemini API.
Permite criar o modelo humano no cenário hiper-realista com iluminação natural.
"""

import os
import json
import urllib.request
from typing import Dict, Optional

class GeminiImagenProvider:
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate_lifestyle_scene(
        self,
        prompt: str,
        aspect_ratio: str = "3:4",
        sample_count: int = 1
    ) -> Dict:
        """
        Gera cena de lifestyle fotográfica a partir do prompt com Imagen 3.
        """
        if not self.is_configured():
            return {
                "success": False,
                "provider": "google_imagen_3",
                "error": "GEMINI_API_KEY não configurada no ambiente (.env).",
                "is_dry_run": True
            }

        url = f"{self.API_URL}?key={self.api_key}"
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": sample_count,
                "aspectRatio": aspect_ratio,
                "personGeneration": "ALLOW_ADULT",
                "safetySetting": "BLOCK_ONLY_HIGH"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "BRK-Studio-Imagen/1.0"
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            predictions = data.get("predictions", [])
            if predictions and "bytesBase64Encoded" in predictions[0]:
                return {
                    "success": True,
                    "provider": "google_imagen_3",
                    "image_base64": predictions[0]["bytesBase64Encoded"],
                    "mime_type": predictions[0].get("mimeType", "image/jpeg"),
                    "prompt": prompt
                }
            return {
                "success": False,
                "provider": "google_imagen_3",
                "error": "Nenhuma imagem retornada na resposta da API.",
                "raw_response": data
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "google_imagen_3",
                "error": str(e)
            }
