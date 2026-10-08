"""
BRK Studio: Módulo de Verticalização para Geração de Fotos Humanizadas (Lifestyle & Virtual Try-On)
"""

from .persona_manager import persona_manager
from .garment_processor import garment_processor
from .studio_orchestrator import studio_orchestrator

__all__ = ["persona_manager", "garment_processor", "studio_orchestrator"]
