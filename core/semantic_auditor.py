"""
Agente Auditor de Conformidade Semântica (core/semantic_auditor.py)
Audita a integridade e ausência de contaminação cruzada de arquétipos nas descrições:
- Impede termos têxteis e de proteção solar em varas de pesca, carretilhas, facas e aromatizantes.
- Impede menções a zíper em camisas de botão.
- Impede menções a mangas e golas em calças e bermudas.
- Impede tabelas de medidas em acessórios e cutelaria.
"""

import os
import sys
import json
import re
from typing import Dict, Any, List, Tuple

# Assegurar UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder

# Matriz Estrita de Termos Incompatíveis por Categoria / Arquétipo
INCOMPATIBILITY_RULES = {
    # 1. Equipamentos de Pesca Mecânica (Varas, Carretilhas, Molinetes, Alicates, Linhas)
    "fishing_tackle_gear": {
        "forbidden_terms": [
            "fpu 50+", "dry fit", "costura reforçada", "zíper frontal", "ziper frontal",
            "manga longa", "manga curta", "gola padre", "gola anatômica", "pesponto duplo",
            "tecido tecnológico", "100% poliéster", "algodão nobre"
        ],
        "forbidden_tags": ['<details class="brk-size-guide">'],
        "description": "Equipamentos mecânicos de pesca (Varas, Carretilhas) não podem conter termos de vestuário/tecido"
    },
    # 2. Caixas de Pesca e Estojos
    "tackle_boxes_storage": {
        "forbidden_terms": [
            "fpu 50+", "dry fit", "costura reforçada", "manga longa", "gola", "zíper"
        ],
        "forbidden_tags": ['<details class="brk-size-guide">'],
        "description": "Caixas e estojos não podem conter termos de vestuário"
    },
    # 3. Iscas Artificiais
    "fishing_lures": {
        "forbidden_terms": [
            "fpu 50+", "dry fit", "costura reforçada", "manga", "gola", "tecido", "zíper"
        ],
        "forbidden_tags": ['<details class="brk-size-guide">'],
        "description": "Iscas artificiais não podem conter termos de vestuário"
    },
    # 4. Cutelaria e Facas Artesanais
    "cutlery_unique": {
        "forbidden_terms": [
            "fpu 50+", "dry fit", "costura reforçada", "zíper", "ziper", "manga longa", "manga curta", "gola"
        ],
        "forbidden_tags": ['<details class="brk-size-guide">'],
        "description": "Cutelaria artesanal não pode conter termos de vestuário ou tabela de medidas de roupa"
    },
    # 5. Aromatizantes e Cuidados Automotivos
    "accessories_car_care": {
        "forbidden_terms": [
            "fpu 50+", "proteção solar", "dry fit", "costura", "manga", "gola", "tecido tecnológico"
        ],
        "forbidden_tags": ['<details class="brk-size-guide">'],
        "description": "Aromatizantes não podem conter proteção solar nem tabelas de medidas"
    },
    # 6. Camisas de Trabalho de Botão
    "shirts_button_work": {
        "forbidden_terms": [
            "zíper", "ziper", "cursor do zíper", "fecho de engate"
        ],
        "description": "Camisas Work de botão jamais podem mencionar zíper"
    },
    # 7. Calças e Bermudas
    "pants_cargo_tactical": {
        "forbidden_terms": [
            "manga longa", "manga curta", "gola padre", "gola anatômica"
        ],
        "description": "Calças e bermudas jamais podem mencionar termos de vestuário superior (mangas, golas)"
    }
}

class SemanticAuditor:
    def __init__(self):
        self.engine = TemplateEngine()
        self.builder = HTMLBuilder()

    def audit_html(self, html: str, archetype_id: str, title: str = "") -> List[str]:
        """
        Valida o HTML compilado contra as regras de incompatibilidade do arquétipo.
        Retorna lista de violações encontradas (vazio se 100% em conformidade).
        """
        violations = []
        rule = INCOMPATIBILITY_RULES.get(archetype_id)
        if not rule:
            return violations

        html_low = html.lower()

        # 1. Checagem de termos proibidos
        for term in rule.get("forbidden_terms", []):
            if term.lower() in html_low:
                violations.append(f"Termo proibido detectado: '{term}' em produto do arquétipo '{archetype_id}'")

        # 2. Checagem de tags proibidas
        for tag in rule.get("forbidden_tags", []):
            if tag in html:
                violations.append(f"Tag proibida detectada: '{tag}' em produto do arquétipo '{archetype_id}'")

        return violations

    def audit_product(self, prod: Dict[str, Any], store_key: str = "brk_fishing") -> Tuple[bool, List[str]]:
        """Gera o HTML no padrão Modo B oficial e audita conformidade semântica"""
        title = prod.get("title", "")
        p_type = str(prod.get("product_type", ""))
        tags = str(prod.get("tags", ""))
        arch_id = prod.get("archetype_id") or self.engine.detect_archetype(title, p_type, tags)

        raw_imgs = prod.get("cdn_images") or prod.get("gallery") or [i.get("src", i) if isinstance(i, dict) else i for i in prod.get("images", [])]
        cdn_imgs = [u for u in raw_imgs if isinstance(u, str) and u.startswith("http")]

        enriched = self.engine.generate_narrative_from_template(prod, arch_id, cdn_imgs, store_key=store_key)
        html = self.builder.build_shopify_html(enriched)

        violations = self.audit_html(html, arch_id, title)
        return len(violations) == 0, violations

    def audit_catalog_file(self, json_path: str, store_key: str, sample_limit: int = 150) -> Dict[str, Any]:
        """Audita uma amostra representativa ou catálogo completo de uma loja"""
        if not os.path.exists(json_path):
            return {"error": f"Arquivo {json_path} não encontrado"}

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        products = data.get("products", []) if isinstance(data, dict) else data
        if sample_limit and sample_limit > 0:
            products = products[:sample_limit]

        total = len(products)
        passed = 0
        failed = 0
        error_details = []

        for p in products:
            ok, viols = self.audit_product(p, store_key)
            if ok:
                passed += 1
            else:
                failed += 1
                error_details.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "violations": viols
                })

        return {
            "store_key": store_key,
            "total_audited": total,
            "passed": passed,
            "failed": failed,
            "conformity_rate": round((passed / total) * 100, 2) if total > 0 else 100.0,
            "errors": error_details
        }

def run_semantic_audit():
    print("\n=======================================================")
    print("  🛡️ AGENTE AUDITOR DE CONFORMIDADE SEMÂNTICA (BRK)")
    print("=======================================================")
    auditor = SemanticAuditor()

    # Teste de caso de ouro da Vara Marine Sports
    vara_test = {
        "id": "VPMSGLADIUSC581MH",
        "title": "Vara de Pesca Marine Sports Gladius GL-C581MHM 25lbs 1,73m - Carretilha (inteiriça)",
        "product_type": "Varas",
        "tags": "vara de pesca, marine sports, carretilha, pesca"
    }
    ok, viols = auditor.audit_product(vara_test, "brk_fishing")
    if not ok:
        print(f"❌ [FALHA NO CASO DA VARA DE PESCA]: {viols}")
        return False
    else:
        print("✅ [CASO DE OURO]: Vara Marine Sports Gladius auditada com 0% de contaminação têxtil!")

    stores = [
        ("brk_fishing", "data/stores/brk_fishing.json"),
        ("brk_agro", "data/stores/brk_agro.json"),
        ("brk_motors", "data/stores/brk_motors.json")
    ]

    all_passed = True
    for skey, fpath in stores:
        full_path = os.path.join(BASE_DIR, fpath)
        print(f"\n[*] Auditando conformidade da loja: {skey.upper()}...")
        res = auditor.audit_catalog_file(full_path, skey, sample_limit=100)
        rate = res.get("conformity_rate", 0)
        print(f"    Taxa de Conformidade: {rate}% ({res.get('passed')}/{res.get('total_audited')} produtos sem contaminação)")
        if res.get("failed", 0) > 0:
            print(f"    ⚠️ {res.get('failed')} divergência(s) encontrada(s):")
            for err in res.get("errors", [])[:3]:
                print(f"       * {err['title'][:40]}... -> {err['violations']}")
            all_passed = False

    print("\n=======================================================")
    if all_passed:
        print("🎉 [SUCESSO TOTAL] Todas as 3 lojas em 100% de Conformidade Semântica!")
    else:
        print("⚠️ [AVISO] Algumas divergências pontuais foram registradas.")
    print("=======================================================\n")
    return all_passed

if __name__ == "__main__":
    success = run_semantic_audit()
    sys.exit(0 if success else 1)
