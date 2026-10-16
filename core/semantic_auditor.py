"""
Agente Auditor de Conformidade Semantica (core/semantic_auditor.py).

Gera o HTML oficial (Modo B) de cada produto e confere se ele contem informacoes
INCOMPATIVEIS com a categoria do produto (ex.: selo "FPU 50+" numa vara de pesca).

As regras sao dados (lista RULES), faceis de ler e de ampliar. Cada achado tem:
  - severity "ERROR"   : conteudo comprovadamente errado -> bloqueia (exit code 1)
  - severity "WARNING" : suspeito, exige revisao humana  -> nao bloqueia por padrao

Uso:
  py -3.14 cli.py validate                       # todas as lojas
  py -3.14 cli.py validate --store brk_fishing --limit 200
  py -3.14 cli.py validate --strict              # WARNING tambem reprova
"""

import os
import re
import sys
import json
from collections import Counter
from typing import Any, Callable, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder, QUICK_BADGES_BY_ARCHETYPE

# Arquetipos de vestuario/acessorios vestiveis: unicos que podem ter tabela de medidas.
SIZE_GUIDE_OK = {
    "uv_performance", "agro_field", "motors_speed", "shirts_button_work",
    "pants_cargo_tactical", "overalls_workwear", "sun_sleeves_manguitos",
    "neck_gaiters_balaclavas", "gloves_tactical_fishing", "hats_safari_outdoor",
    "hats_country_cowboy", "caps_trucker_snapback",
    "footwear_sandals_boaonda", "closed_footwear_sneakers",
}

# Arquetipos onde NAO pode haver vocabulario textil/de camisa (tecido, FPU, costura, manga...).
NON_TEXTILE = {
    "fishing_tackle_gear", "fishing_lures", "tackle_boxes_storage", "cutlery_unique",
    "drinkware_thermo", "accessories_car_care", "accessories_general",
    "books_publications", "eyewear_sunglasses",
    "footwear_sandals_boaonda", "closed_footwear_sneakers",
}

TEXTILE_RE = re.compile(
    r"dry ?fit|fpu ?50|pesponto|costura refor|z[ií]per|manga (?:longa|curta)|\bgola\b|"
    r"algod[aã]o|poli[eé]ster|quick dry",
    re.IGNORECASE,
)
# Vocabulário inequivocamente de camisa (sem poliéster/zíper/algodão, que existem em barracas etc.)
TEXTILE_STRICT_RE = re.compile(r"dry ?fit|fpu ?50|pesponto|costura refor|manga (?:longa|curta)|quick dry", re.IGNORECASE)
# A tabela infantil é de camisa (tórax/comprimento/manga)
KIDS_SHIRT_TABLE_OK = {"uv_performance", "agro_field", "motors_speed", "shirts_button_work"}
UPPER_BODY_RE = re.compile(r"\bmangas?\b|\bgola\b|colarinho", re.IGNORECASE)
ZIPPER_RE = re.compile(r"z[ií]per", re.IGNORECASE)
NEGATED_ZIPPER_RE = re.compile(r"sem\s+z[ií]per(?:es)?", re.IGNORECASE)
ROD_RE = re.compile(r"\bvaras?\b", re.IGNORECASE)
BADGE_TITLE_RE = re.compile(r'brk-badge-title">([^<]+)<')

GENERIC_BADGE_TITLES = {"Qualidade Oficial", "Acabamento Premium", "Envio Rápido & Seguro", "Garantia Oficial BRK"}


def _first(regex: "re.Pattern", text: str) -> Optional[str]:
    m = regex.search(text)
    return m.group(0) if m else None


def _rule_textile_in_non_textile(arch: str, title: str, body: str) -> Optional[str]:
    if arch == "accessories_general":
        # camping/chaveiros podem ter poliéster ou zíper (barraca): só acusa o que é inequivocamente de camisa
        return _first(TEXTILE_STRICT_RE, body)
    if arch in NON_TEXTILE:
        return _first(TEXTILE_RE, body)
    return None


def _rule_kids_shirt_table_in_non_shirt(arch: str, title: str, body: str) -> Optional[str]:
    if arch not in KIDS_SHIRT_TABLE_OK and "Guia de Tamanhos Infantil" in body:
        return "Guia de Tamanhos Infantil (tabela de camisa: tórax/manga)"
    return None


def _rule_dryfit_in_cotton_shirt(arch: str, title: str, body: str) -> Optional[str]:
    if arch == "agro_field" and re.search(r"dry ?fit", body, re.IGNORECASE) and re.search(r"algod[aã]o", body, re.IGNORECASE):
        return "Dry Fit e Algodão no mesmo produto (contraditório)"
    return None


def _rule_size_guide_in_non_wearable(arch: str, title: str, body: str) -> Optional[str]:
    if arch not in SIZE_GUIDE_OK and '<details class="brk-size-guide"' in body:
        return "tabela de medidas <details class=brk-size-guide>"
    return None


def _rule_zipper_in_button_shirt(arch: str, title: str, body: str) -> Optional[str]:
    if arch == "shirts_button_work":
        return _first(ZIPPER_RE, NEGATED_ZIPPER_RE.sub("", body))
    return None


def _rule_upper_body_in_pants(arch: str, title: str, body: str) -> Optional[str]:
    if arch == "pants_cargo_tactical":
        return _first(UPPER_BODY_RE, body)
    return None


def _rule_foreign_badge(arch: str, title: str, body: str) -> Optional[str]:
    allowed = {b["title"] for b in QUICK_BADGES_BY_ARCHETYPE.get(arch, [])} | GENERIC_BADGE_TITLES
    foreign = [t for t in BADGE_TITLE_RE.findall(body) if t not in allowed]
    return ", ".join(foreign) if foreign else None


def _rule_bearings_in_rod(arch: str, title: str, body: str) -> Optional[str]:
    # Vara nao tem rolamentos; o molde "fishing_tackle_gear" e compartilhado com carretilhas/molinetes.
    if arch == "fishing_tackle_gear" and ROD_RE.search(title) and "rolamento" in body.lower():
        return "rolamentos (molde generico de equipamento aplicado a uma vara)"
    return None


# (id, severidade, descricao, funcao(arq, titulo, corpo_html) -> trecho_encontrado | None)
RULES: List[Dict[str, Any]] = [
    {"id": "textil_em_nao_textil", "severity": "ERROR",
     "desc": "Vocabulario de roupa (Dry Fit, FPU 50+, costura, zíper, manga, gola, tecido) em produto que nao e roupa",
     "check": _rule_textile_in_non_textile},
    {"id": "tabela_medidas_em_nao_vestuario", "severity": "ERROR",
     "desc": "Tabela de medidas em produto que nao se veste",
     "check": _rule_size_guide_in_non_wearable},
    {"id": "ziper_em_camisa_botao", "severity": "ERROR",
     "desc": "Camisa de botao mencionando zíper/fecho de engate",
     "check": _rule_zipper_in_button_shirt},
    {"id": "vestuario_superior_em_calca", "severity": "ERROR",
     "desc": "Calca/bermuda com termos de vestuario superior (manga, gola, colarinho)",
     "check": _rule_upper_body_in_pants},
    {"id": "selo_de_outro_arquetipo", "severity": "ERROR",
     "desc": "Quick Badge que nao pertence ao arquetipo do produto",
     "check": _rule_foreign_badge},
    {"id": "rolamento_em_vara", "severity": "WARNING",
     "desc": "Ficha tecnica de vara citando rolamentos",
     "check": _rule_bearings_in_rod},
    {"id": "tabela_infantil_de_camisa_em_nao_camisa", "severity": "ERROR",
     "desc": "Tabela infantil de camisa (torax/manga) em produto que nao e camisa",
     "check": _rule_kids_shirt_table_in_non_shirt},
    {"id": "dryfit_em_camisa_de_algodao", "severity": "WARNING",
     "desc": "Camisa Agro (algodao) com selo/texto Dry Fit (poliester)",
     "check": _rule_dryfit_in_cotton_shirt},
]


def strip_non_visible(html: str) -> str:
    """Remove <style> e <script> (CSS/JSON-LD) para auditar apenas o texto visivel ao cliente."""
    html = re.sub(r"<style\b.*?</style>", "", html, flags=re.S | re.I)
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S | re.I)
    return html


class SemanticAuditor:
    def __init__(self):
        self.engine = TemplateEngine()
        self.builder = HTMLBuilder()

    def render_mode_b(self, prod: Dict[str, Any], store_key: str) -> Dict[str, str]:
        """Mesmo caminho de geracao usado pela sincronizacao direta (shopify_direct_sync)."""
        title = prod.get("title", "")
        vendor = prod.get("vendor", "")
        sku_code = prod.get("master_sku") or prod.get("sku") or (prod.get("variants_skus") and prod.get("variants_skus")[0]) or ""
        arch = prod.get("archetype_id") or self.engine.detect_archetype(
            title, str(prod.get("product_type", "")), str(prod.get("tags", "")), vendor=vendor, sku=sku_code
        )
        raw_imgs = prod.get("cdn_images") or prod.get("gallery") or [
            (i.get("src", i) if isinstance(i, dict) else i) for i in prod.get("images", [])
        ]
        imgs = [u for u in raw_imgs if isinstance(u, str) and u.startswith("http")]
        enriched = self.engine.generate_narrative_from_template(prod, arch, imgs, store_key=store_key)
        return {"archetype": arch, "html": self.builder.build_shopify_html(enriched)}

    def audit_html(self, arch: str, title: str, html: str) -> List[Dict[str, str]]:
        body = strip_non_visible(html)
        found = []
        for rule in RULES:
            evidence = rule["check"](arch, title, body)
            if evidence:
                found.append({"rule": rule["id"], "severity": rule["severity"],
                              "desc": rule["desc"], "evidence": evidence})
        return found

    def audit_products(self, products: List[Dict[str, Any]], store_key: str,
                       limit: Optional[int] = None) -> Dict[str, Any]:
        if limit and limit > 0:
            products = products[:limit]
        findings: List[Dict[str, Any]] = []
        by_rule: Counter = Counter()
        errors = warnings = crashed = 0
        for prod in products:
            try:
                out = self.render_mode_b(prod, store_key)
            except Exception as exc:  # um produto com dado ruim nao pode derrubar a auditoria
                crashed += 1
                findings.append({"store": store_key, "id": prod.get("id"), "title": prod.get("title", ""),
                                 "archetype": "?", "rule": "falha_ao_gerar_html", "severity": "ERROR",
                                 "desc": "Excecao ao gerar o HTML do produto", "evidence": repr(exc)[:200]})
                errors += 1
                by_rule["falha_ao_gerar_html"] += 1
                continue
            for f in self.audit_html(out["archetype"], prod.get("title", ""), out["html"]):
                f.update({"store": store_key, "id": prod.get("id"),
                          "title": prod.get("title", ""), "archetype": out["archetype"]})
                findings.append(f)
                by_rule[f["rule"]] += 1
                if f["severity"] == "ERROR":
                    errors += 1
                else:
                    warnings += 1
        return {"store": store_key, "audited": len(products), "errors": errors,
                "warnings": warnings, "crashed": crashed, "by_rule": dict(by_rule), "findings": findings}


def load_store_products(store_key: str) -> List[Dict[str, Any]]:
    path = os.path.join(BASE_DIR, "data", "stores", f"{store_key}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Catalogo nao encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("products", []) if isinstance(data, dict) else data
