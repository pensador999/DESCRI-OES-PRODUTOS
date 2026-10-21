"""
Suíte Oficial de Testes de Regressão e Guardrails de Qualidade (tests/test_regression_guardrails.py)
Garante 100% de conformidade com as Regras de Ouro e Pilares Estratégicos do Ecossistema BRK:

1. Zero Quebra de Layout (CSS inline, SVGs autônomos, zero CDN Font Awesome externa).
2. Fidelidade Cirúrgica de Arquétipos (Work botão sem zíper, calça sem termos superiores, aromatizante sem tabela/UV).
3. Schema.org JSON-LD (Microdados Product com priceCurrency BRL e JSON válido).
4. Quick Badges Tecnológicos (Grid de 4 selos dinâmicos com SVGs embutidos).
5. Tabela de Medidas Expansível em <details>/<summary> HTML5 nativo (Adulto, Kids, Calças, Calçados, Bonés).
6. Isolamento e Segurança de Payload Shopify (transmissão estrita e exclusiva de body_html).
"""

import os
import sys
import json
import re
import unittest
from typing import Dict, Any

# Assegurar UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Adicionar raiz do projeto ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.template_engine import TemplateEngine
from core.html_builder import HTMLBuilder
from core.shopify_direct_sync import ShopifyDirectSync

class TestBRKRegressionGuardrails(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = TemplateEngine()
        cls.builder = HTMLBuilder()
        cls.sample_cdn_imgs = [
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/img-1.jpg?v=1",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/img-2.jpg?v=2"
        ]

    def _generate_html(self, prod_dict: Dict[str, Any], store_key: str = "brk_fishing") -> str:
        arch_id = prod_dict.get("archetype_id") or self.engine.detect_archetype(
            prod_dict.get("title", ""),
            str(prod_dict.get("product_type", "")),
            str(prod_dict.get("tags", ""))
        )
        enriched = self.engine.generate_narrative_from_template(
            prod_dict, arch_id, self.sample_cdn_imgs, store_key=store_key
        )
        return self.builder.build_shopify_html(enriched)

    # --------------------------------------------------------------------------
    # 1. TESTE DE AUTONOMIA DE LAYOUT & ZERO QUEBRA
    # --------------------------------------------------------------------------
    def test_layout_autonomy_and_inline_css(self):
        """O HTML gerado deve ser 100% autônomo com bloco <style> e sem CDNs externas."""
        prod = {
            "id": 1001,
            "title": "Camisa BRK Fishing Tucunaré Azul UV50+",
            "product_type": "Camisas",
            "tags": "camisa, uv50, pesca"
        }
        html = self._generate_html(prod, "brk_fishing")

        # Deve conter <style> interno
        self.assertIn("<style>", html, "HTML gerado deve conter bloco <style> embutido.")
        self.assertIn(".brk-desc-wrapper", html, "CSS deve conter escopo .brk-desc-wrapper.")
        self.assertIn(".brk-quick-badges", html, "CSS deve conter estilos para quick badges.")

        # Não pode depender de CDN de Font Awesome externa na Shopify
        self.assertNotIn("kit.fontawesome.com", html, "HTML não pode carregar Font Awesome via kit CDN externo.")
        self.assertNotIn("cdnjs.cloudflare.com/ajax/libs/font-awesome", html, "HTML não pode usar CDN externa.")

        # Deve conter SVGs embutidos
        self.assertIn("<svg", html, "Ícones devem ser SVGs inline.")
        self.assertIn("</svg>", html, "SVGs devem fechar corretamente.")

    # --------------------------------------------------------------------------
    # 2. TESTES DE FIDELIDADE CIRÚRGICA DE ARQUÉTIPOS (REGRAS DE OURO)
    # --------------------------------------------------------------------------
    def test_shirts_button_work_anti_zipper_rule(self):
        """Camisas Work de Botão JAMAIS podem mencionar zíper ou fecho de engate."""
        prod = {
            "id": 2001,
            "title": "Camisa Manga Curta Masculina Trabalho Botao BRK Agro",
            "product_type": "Camisas",
            "tags": "camisa, botao, trabalho, agro",
            "body_html": "<p>Camisa com abotoamento frontal reforçado e bolsos com aba.</p>"
        }
        html = self._generate_html(prod, "brk_agro")

        html_low = html.lower()
        self.assertNotIn("zíper", html_low, "Camisa de botão não pode ter menção a zíper!")
        self.assertNotIn("ziper", html_low, "Camisa de botão não pode ter menção a ziper!")
        self.assertNotIn("fecho de engate", html_low, "Camisa de botão não pode ter fecho de engate!")

    def test_camisas_xtech_detalhes_tecnicos_specs(self):
        """Camisas XTech (uv_performance) padrão devem ter 10 dias úteis e _FULL/_OUT pronta entrega."""
        # 1. Padrão (sem _FULL / sem _OUT) -> 10 dias úteis
        prod_std = {
            "id": 1005,
            "title": "Camisa ArmorX BRK Barkeiro Azul com Proteção UV50+",
            "product_type": "Camisas",
            "tags": "camisa, uv50, xtech, pesca",
            "body_html": "",
            "sku": "C01005P"
        }
        html_std = self._generate_html(prod_std, "brk_fishing")

        self.assertIn("Detalhes Técnicos & Cuidados de Conservação", html_std)
        self.assertIn("Prazo de Produção", html_std)
        self.assertIn("10 dias úteis", html_std)
        self.assertNotIn("Pronta entrega", html_std)
        self.assertIn("Composição", html_std)
        self.assertIn("90% Poliéster 10% Elastano", html_std)
        self.assertIn("Tecido", html_std)
        self.assertIn("XTech Pro", html_std)
        self.assertIn("Tecnologia", html_std)
        self.assertIn("Secagem Rápida, Tecido Leve, Proteção Solar", html_std)
        self.assertIn("Modelagem", html_std)
        self.assertIn("Anatômica e confortável", html_std)
        self.assertIn("Proteção", html_std)
        self.assertIn("Proteção UV50+ (não sai na lavagem)", html_std)

        # 2. Com _FULL -> Pronta entrega
        prod_full = {
            "id": 1006,
            "title": "Camisa ArmorX BRK Barkeiro Azul com Proteção UV50+",
            "product_type": "Camisas",
            "tags": "camisa, uv50, xtech, pesca",
            "body_html": "",
            "sku": "C01005P_FULL"
        }
        html_full = self._generate_html(prod_full, "brk_fishing")
        self.assertIn("Prazo de Produção", html_full)
        self.assertIn("Pronta entrega", html_full)
        self.assertNotIn("10 dias úteis", html_full)

        # 3. Com _OUT -> Pronta entrega
        prod_out = {
            "id": 1007,
            "title": "Camisa ArmorX BRK Barkeiro Azul com Proteção UV50+",
            "product_type": "Camisas",
            "tags": "camisa, uv50, xtech, pesca",
            "body_html": "",
            "sku": "C01005P_OUT"
        }
        html_out = self._generate_html(prod_out, "brk_fishing")
        self.assertIn("Prazo de Produção", html_out)
        self.assertIn("Pronta entrega", html_out)
        self.assertNotIn("10 dias úteis", html_out)

    def test_camisas_c0_size_guide_masculino(self):
        """Camisas padrão C0 Masculino / Unissex devem conter rigorosamente as 7 linhas oficiais."""
        prod = {
            "id": 1006,
            "title": "Camisa de Pesca BRK Azul Ocean com Proteção UV50+",
            "master_sku": "C01349P_FULL",
            "product_type": "Camisas",
            "tags": "camisa, uv50, pesca",
            "body_html": ""
        }
        html = self._generate_html(prod, "brk_fishing")
        self.assertIn("Tabela de Medidas Masculino / Unissex (PP ao G2)", html)
        self.assertIn("MASCULINO", html)
        self.assertIn("ALTURA", html)
        self.assertIn("TÓRAX", html)
        self.assertIn("MANGA", html)
        self.assertIn("49,5 cm", html)
        self.assertIn("51,5 cm", html)
        self.assertIn("54 cm", html)
        self.assertIn("56 cm", html)
        self.assertIn("59 cm", html)
        self.assertIn("62 cm", html)
        self.assertIn("65 cm", html)
        self.assertIn("76,5 cm", html)
        self.assertIn("As medidas podem variar de 2cm a 3cm", html)

    def test_camisas_c0_size_guide_feminino_baby_look(self):
        """Camisas padrão C0 Feminino / Baby Look devem conter rigorosamente as 7 linhas oficiais."""
        prod = {
            "id": 1007,
            "title": "Camisa Feminina Brk Basic Cinza Claro com Proteção Solar UV50 Envio Imediato",
            "master_sku": "C01046BLPP_FULL",
            "product_type": "Camisas",
            "tags": "camisa, feminina, uv50",
            "body_html": ""
        }
        html = self._generate_html(prod, "brk_fishing")
        self.assertIn("Tabela de Medidas Feminina - Baby Look (PP ao G2)", html)
        self.assertIn("FEMININO", html)
        self.assertIn("ALTURA", html)
        self.assertIn("Baby Look PP", html)
        self.assertIn("Baby Look P", html)
        self.assertIn("Baby Look M", html)
        self.assertIn("Baby Look G", html)
        self.assertIn("Baby Look GG", html)
        self.assertIn("Baby Look G1", html)
        self.assertIn("Baby Look G2", html)
        self.assertIn("33 cm", html)
        self.assertIn("37 cm", html)
        self.assertIn("43 cm", html)
        self.assertIn("47 cm", html)
        self.assertIn("50 cm", html)
        self.assertIn("55 cm", html)

    def test_camisas_c0_size_guide_infantil(self):
        """Camisas padrão C0 Infantil devem conter rigorosamente as 7 faixas etárias oficiais."""
        prod = {
            "id": 1008,
            "title": "Camisa Infantil BRK Dourado Kids UV50+",
            "master_sku": "C0777KIDS",
            "product_type": "Camisas",
            "tags": "camisa, infantil, kids, uv50",
            "body_html": ""
        }
        html = self._generate_html(prod, "brk_fishing")
        self.assertIn("Guia de Tamanhos Infantil (1 a 13 Anos)", html)
        self.assertIn("INFANTIL", html)
        self.assertIn("ALTURA", html)
        self.assertIn("1 a 2 Anos (PP)", html)
        self.assertIn("2 a 3 Anos (P)", html)
        self.assertIn("4 a 5 Anos (M)", html)
        self.assertIn("6 a 7 Anos (G)", html)
        self.assertIn("8 a 9 Anos (GG)", html)
        self.assertIn("10 a 11 Anos (G1)", html)
        self.assertIn("12 a 13 Anos (G2)", html)
        self.assertIn("31 cm", html)
        self.assertIn("43 cm", html)

    def test_camisas_button_work_and_cotton_isolation(self):
        """Camisas Work de Botão NÃO devem receber medidas de elastano/baby look C0."""
        prod = {
            "id": 1009,
            "title": "Camisa Work Verde Oliva com Proteção UV50+",
            "master_sku": "CMB08",
            "product_type": "Camisas",
            "tags": "work, sarja, botão, operacional",
            "body_html": ""
        }
        html = self._generate_html(prod, "brk_fishing")
        self.assertIn("Tabela de Medidas - Camisas Work & Utilitárias de Botão (P ao G2)", html)
        self.assertNotIn("Baby Look", html)
        self.assertNotIn("49,5 cm", html)
        """Calças e Bermudas JAMAIS podem ter termos de vestuário superior (manga, gola)."""
        prod = {
            "id": 2002,
            "title": "Calça Tática Ripstop Cargo BRK Motors Trilha",
            "product_type": "Calças",
            "tags": "calça, tática, ripstop, cargo",
            "body_html": "<p>Calça com 6 bolsos reforçados para trilha e operações de campo.</p>"
        }
        html = self._generate_html(prod, "brk_motors")

        # Excluir o bloco do size-guide (onde pode haver regras gerais de tabela) da análise de texto descritivo
        desc_body = html.split('<details class="brk-size-guide">')[0]
        desc_low = desc_body.lower()

        self.assertNotIn("manga longa", desc_low, "Calça tática não pode ter menção a manga longa!")
        self.assertNotIn("manga curta", desc_low, "Calça tática não pode ter menção a manga curta!")
        self.assertNotIn("gola padre", desc_low, "Calça tática não pode ter menção a gola padre!")
        self.assertNotIn("gola redonda", desc_low, "Calça tática não pode ter menção a gola redonda!")

    def test_air_freshener_and_accessories_exclusions(self):
        """Aromatizantes e itens de revenda NUNCA recebem tabela de medidas ou atributos têxteis/UV."""
        prod = {
            "id": 2003,
            "title": "Aromatizante Folha Cheirinho Automotivo Carro BRK Motors",
            "product_type": "Acessórios",
            "tags": "aromatizante, carro, perfume, automotivo",
            "body_html": "<p>Fragrância duradoura para o interior do seu veículo.</p>"
        }
        html = self._generate_html(prod, "brk_motors")

        # Não pode ter tabela de medidas no corpo
        self.assertNotIn('<details class="brk-size-guide">', html, "Aromatizante JAMAIS pode ter accordion de medidas!")
        self.assertNotIn('<table class="brk-sg-table">', html, "Aromatizante JAMAIS pode ter tabela de medidas!")

        # Não pode ter selo ou especificação de proteção solar
        html_low = html.lower()
        self.assertNotIn("fpu 50+", html_low, "Aromatizante não pode ter FPU 50+!")
        self.assertNotIn("proteção solar", html_low, "Aromatizante não pode ter proteção solar!")
        self.assertNotIn("dry fit", html_low, "Aromatizante não pode ter Dry Fit!")

    def test_cutlery_and_knives_exclusions(self):
        """Facas artesanais NUNCA recebem tabela de medidas de vestuário."""
        prod = {
            "id": 2004,
            "title": "Faca Artesanal Campeira 8 Polegadas Aço Carbono BRK Agro",
            "product_type": "Cutelaria",
            "tags": "faca, cutelaria, churrasco, artesanal",
            "body_html": "<p>Lâmina de alta retenção de fio forjada à mão.</p>"
        }
        html = self._generate_html(prod, "brk_agro")

        self.assertNotIn('<details class="brk-size-guide">', html, "Faca artesanal não pode ter tabela de medidas!")
        self.assertIn("Aço", html, "Faca artesanal deve destacar especificações de aço e lâmina.")

    # --------------------------------------------------------------------------
    # 3. TESTE DE SCHEMA.ORG MICRODATA JSON-LD (PILAR 2)
    # --------------------------------------------------------------------------
    def test_schema_org_json_ld_validity(self):
        """Todo HTML deve conter Schema.org JSON-LD válido com @type Product e moeda BRL."""
        prod = {
            "id": 3001,
            "title": "Camisa BRK Agro Manga Longa Soja Ouro",
            "product_type": "Camisas",
            "tags": "agro, camisa, uv50",
            "price": "149.90",
            "sku": "AGR-SOJA-01"
        }
        html = self._generate_html(prod, "brk_agro")

        self.assertIn('<script type="application/ld+json">', html, "Deve conter tag de script JSON-LD.")
        
        # Extrair e fazer parse do JSON
        json_match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.DOTALL)
        self.assertIsNotNone(json_match, "Bloco JSON-LD deve ser encontrado via regex.")

        parsed = json.loads(json_match.group(1))
        self.assertEqual(parsed.get("@context"), "https://schema.org/", "Contexto deve ser schema.org.")
        self.assertEqual(parsed.get("@type"), "Product", "Tipo deve ser Product.")
        self.assertIn("Camisa BRK Agro", parsed.get("name", ""))
        self.assertEqual(parsed.get("offers", {}).get("priceCurrency"), "BRL", "Moeda deve ser estritamente BRL.")

    # --------------------------------------------------------------------------
    # 4. TESTE DE QUICK BADGES TECNOLÓGICOS (PILAR 3)
    # --------------------------------------------------------------------------
    def test_quick_badges_structure_and_count(self):
        """O HTML deve conter exatamente 4 selos de alta conversão dinâmicos com SVGs inline."""
        prod = {
            "id": 4001,
            "title": "Camisa de Pesca BRK Fishing Dourado UV50+",
            "product_type": "Camisas",
            "tags": "camisa, uv50, pesca"
        }
        html = self._generate_html(prod, "brk_fishing")

        self.assertIn('<div class="brk-quick-badges">', html, "Deve conter container dos Quick Badges.")
        badge_count = html.count('class="brk-badge-item"')
        self.assertEqual(badge_count, 4, f"Deve conter exatamente 4 badges tecnológicos, encontrado: {badge_count}")

    # --------------------------------------------------------------------------
    # 5. TESTE DE TABELAS DE MEDIDAS EXPANSÍVEIS EM <details>/<summary> (PILAR 1)
    # --------------------------------------------------------------------------
    def test_size_guide_accordion_types(self):
        """Valida que vestuário adulto, feminino baby look, infantil, calças e calçados recebem seus respectivos guias."""
        # Adulto Masculino / Unissex C0
        prod_adulto = {"id": 5001, "title": "Camisa BRK Adulto Gola Padre", "tags": "camisa, adulto"}
        html_adulto = self._generate_html(prod_adulto)
        self.assertIn('<details class="brk-size-guide">', html_adulto)
        self.assertIn("Tabela de Medidas Masculino / Unissex (PP ao G2)", html_adulto)
        self.assertIn("49,5 cm", html_adulto)
        self.assertIn("As medidas podem variar de 2cm a 3cm", html_adulto)

        # Feminino Baby Look C0
        prod_fem = {"id": 50012, "title": "Camisa Feminina BRK Tropical Baby Look", "tags": "camisa, feminina"}
        html_fem = self._generate_html(prod_fem)
        self.assertIn('<details class="brk-size-guide">', html_fem)
        self.assertIn("Tabela de Medidas Feminina - Baby Look (PP ao G2)", html_fem)
        self.assertIn("Baby Look PP", html_fem)
        self.assertIn("33 cm", html_fem)

        # Infantil (Kids) C0
        prod_kids = {"id": 5002, "title": "Camisa BRK Kids Infantil Manga Longa Peixinho", "tags": "camisa, kids, infantil"}
        html_kids = self._generate_html(prod_kids)
        self.assertIn('<details class="brk-size-guide">', html_kids)
        self.assertIn("Guia de Tamanhos Infantil (1 a 13 Anos)", html_kids)
        self.assertIn("1 a 2 Anos (PP)", html_kids)
        self.assertIn("12 a 13 Anos (G2)", html_kids)

        # Calças
        prod_calca = {"id": 5003, "title": "Calça Tática Ripstop Operacional", "tags": "calça, ripstop"}
        html_calca = self._generate_html(prod_calca)
        self.assertIn('<details class="brk-size-guide">', html_calca)
        self.assertIn("Tabela de Medidas - Calças & Bermudas (38 ao 52)", html_calca)

        # Calçados Boaonda
        prod_sapato = {"id": 5004, "title": "Babuche Sandália Boaonda Antiestresse", "tags": "sandalia, babuche, calçado"}
        html_sapato = self._generate_html(prod_sapato)
        self.assertIn('<details class="brk-size-guide">', html_sapato)
        self.assertIn("Guia de Tamanhos de Calçados (Medida da Palmilha)", html_sapato)

        # Bonés e Chapéus recebem o novo layout D2C especializado
        prod_bone = {"id": 5005, "title": "Boné Trucker BRK Snapback Aba Curva", "tags": "boné, trucker"}
        html_bone = self._generate_html(prod_bone)
        self.assertIn('brk-cap-description', html_bone)
        self.assertIn('Aba Moldável', html_bone)
        self.assertIn('Tamanho único com regulagem traseira', html_bone)

    # --------------------------------------------------------------------------
    # 6. TESTE DE ISOLAMENTO E SEGURANÇA DE PAYLOAD NA SHOPIFY (REGRA DE OURO 3)
    # --------------------------------------------------------------------------
    def test_direct_sync_payload_safety_and_scope(self):
        """As chamadas à Shopify Admin API devem alterar EXCLUSIVAMENTE o campo body_html."""
        syncer = ShopifyDirectSync(dry_run=True)
        
        # Testar chamada de dry-run
        res = syncer.update_product_body_html("brk_fishing", 12345678, "<div>HTML Teste</div>", "token_fake")
        self.assertTrue(res.get("success"), "Dry-run deve retornar sucesso.")
        self.assertTrue(res.get("dry_run"), "Dry-run flag deve ser True.")
        self.assertEqual(res.get("product_id"), 12345678)

        # Inspecionar construção do payload no código fonte de update_product_body_html
        import inspect
        src = inspect.getsource(syncer.update_product_body_html)
        self.assertIn('"body_html": new_html', src, "Payload deve conter body_html.")
        self.assertNotIn('"title":', src, "Payload JAMAIS pode enviar title na sincronização de descrição!")
        self.assertNotIn('"variants":', src, "Payload JAMAIS pode alterar variantes!")
        self.assertNotIn('"images":', src, "Payload JAMAIS pode alterar imagens!")
        self.assertNotIn('"price":', src, "Payload JAMAIS pode alterar preços!")

class TestSemanticConformity(unittest.TestCase):
    """Anti-contaminacao semantica: selos/tabelas/narrativa coerentes com o arquetipo."""

    @classmethod
    def setUpClass(cls):
        cls.engine = TemplateEngine()
        cls.builder = HTMLBuilder()
        cls.imgs = ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/img-1.jpg?v=1"]

    def _html(self, prod):
        arch = self.engine.detect_archetype(prod.get("title", ""), str(prod.get("product_type", "")), str(prod.get("tags", "")))
        enriched = self.engine.generate_narrative_from_template(prod, arch, self.imgs, store_key="brk_fishing")
        return arch, self.builder.build_shopify_html(enriched)

    def test_vara_nao_recebe_selos_de_camisa(self):
        arch, html = self._html({"id": 9001, "title": "Vara de Pesca Marine Sports Gladius 1,68m", "tags": "vara, pesca"})
        low = html.lower()
        for bad in ("fpu 50", "dry fit", "costura reforçada", "costura reforcada"):
            self.assertNotIn(bad, low, f"Vara contaminada com selo de camisa: {bad}")
        for good in ("Sensibilidade", "Anti-Corros", "100% Original"):
            self.assertIn(good, html)

    def test_camisa_caiaque_e_vestuario(self):
        arch = self.engine.detect_archetype("Camisa de Pesca Proteção UV50+ Pescaiaque Caiaque", "", "")
        self.assertEqual(arch, "uv_performance")

    def test_oculos_infantil_sem_guia_de_camisa(self):
        arch, html = self._html({"id": 9002, "title": "Óculos de Sol Polarizado Infantil BRK", "tags": "oculos, infantil"})
        self.assertNotIn("Guia de Tamanhos Infantil", html)
        self.assertNotIn("FPU 50", html)

    def test_paridade_badges_python_js(self):
        from core.html_builder import QUICK_BADGES_BY_ARCHETYPE
        js = open(os.path.join(BASE_DIR, "js", "modal.js"), encoding="utf-8").read()
        m = re.search(r"const QUICK_BADGES_BY_ARCHETYPE\s*=\s*(\{.*?\n\});", js, re.S)
        self.assertIsNotNone(m, "Mapa JS de badges nao encontrado em modal.js")
        js_map = json.loads(m.group(1))
        py_map = json.loads(json.dumps(QUICK_BADGES_BY_ARCHETYPE))
        self.assertEqual(set(js_map), set(py_map), "Arquetipos divergentes entre Python e JS")

    def test_catalogo_real_sem_erros_semanticos(self):
        from core.semantic_auditor import SemanticAuditor, load_store_products
        aud = SemanticAuditor()
        total = 0
        for sk in ("brk_fishing", "brk_agro", "brk_motors"):
            prods = load_store_products(sk)
            if not prods:
                continue
            r = aud.audit_products(prods, sk)
            total += r["errors"]
        self.assertEqual(total, 0, "Auditor semantico encontrou ERROs no catalogo (rode: py -3.14 cli.py validate)")

class TestLiveAgentAndTracking(unittest.TestCase):
    """Rastreio invisivel no Modo B + classificador do Agente ao Vivo + busca global de SKU."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location("live_status", os.path.join(BASE_DIR, "api", "live_status.py"))
        cls.live = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.live)
        cls.engine = TemplateEngine()
        cls.builder = HTMLBuilder()

    def _mode_b(self, sku="C02846BL", title="Camisa de Pesca Brk Proteção Solar UV50+"):
        prod = {"id": 1, "title": title, "master_sku": sku, "handle": "x", "tags": "camisa"}
        arch = self.engine.detect_archetype(title, "", "")
        enriched = self.engine.generate_narrative_from_template(
            prod, arch, ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/a.jpg?v=1"], store_key="brk_fishing")
        return arch, self.builder.build_shopify_html(enriched)

    def test_modo_b_comeca_com_marcador_de_rastreio(self):
        arch, html = self._mode_b()
        self.assertTrue(html.lstrip().startswith("<!-- BRK-MODO-B v"), "Marcador deve ser a 1a linha")
        m = self.live.MARKER_RE.search(html)
        self.assertIsNotNone(m, "Marcador deve ser reconhecido pelo agente")
        self.assertEqual(m.group(2).strip(), "C02846BL")
        self.assertEqual(m.group(3).strip(), arch)
        self.assertNotIn("--", m.group(0)[4:-3].replace(" | ", "").replace("BRK-MODO-B", ""), "Comentario HTML nao pode ter '--' no corpo")

    def test_versao_paritaria_python_agente_js(self):
        from core.html_builder import MODO_B_VERSION
        self.assertEqual(MODO_B_VERSION, self.live.MODO_B_VERSION, "Versao do agente deve ser igual a do builder")
        js = open(os.path.join(BASE_DIR, "js", "modal.js"), encoding="utf-8").read()
        m = re.search(r'const MODO_B_VERSION = "(\d+)"', js)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), MODO_B_VERSION, "Versao do modal.js diverge do html_builder.py")
        self.assertIn("BRK-MODO-B v${MODO_B_VERSION} | sku:", js)

    def test_classificador_estados(self):
        c = self.live.classify
        self.assertEqual(c("")["s"], "SEM_DESCRICAO")
        self.assertEqual(c("A")["s"], "SEM_DESCRICAO")
        self.assertEqual(c("<p>A</p>")["s"], "SEM_DESCRICAO")
        legacy = "<p>" + "Camisa muito boa para pescaria com proteção solar. " * 8 + "</p>"
        self.assertEqual(c(legacy)["s"], "SAUDAVEL")
        self.assertEqual(c(legacy + '<img src="https://use-brk-images-s3.s3.amazonaws.com/a.jpg">')["s"], "IMAGENS_QUEBRADAS")
        _, html = self._mode_b()
        self.assertEqual(c(html)["s"], "COLADO_ATUAL")
        old = html.replace(f"BRK-MODO-B v{self.live.MODO_B_VERSION}", "BRK-MODO-B v0", 1)
        self.assertEqual(c(old)["s"], "COLADO_DESATUALIZADO")
        stripped = self.live.MARKER_RE.sub("", html)  # editor da Shopify removeu o comentario
        self.assertEqual(c(stripped)["s"], "COLADO_SEM_MARCADOR")

    def test_api_somente_leitura_e_cobre_3_lojas(self):
        src = open(os.path.join(BASE_DIR, "api", "live_status.py"), encoding="utf-8").read()
        self.assertEqual(set(self.live.PUBLIC_DOMAINS), {"brk_fishing", "brk_agro", "brk_motors"})
        for forbidden in ('method="PUT"', 'method="POST"', "X-Shopify-Access-Token", "def do_POST"):
            self.assertNotIn(forbidden, src, f"Agente ao vivo deve ser somente leitura: {forbidden}")

    def test_front_tem_busca_sku_global_e_agente(self):
        idx = open(os.path.join(BASE_DIR, "build_modular_dist.py"), encoding="utf-8").read()
        for needle in ('id="sku-global-input"', 'id="sku-global-results"', 'data-filter="colado"',
                       'data-filter="recolar"', 'id="btn-live-agent"', "js/live_agent.js"):
            self.assertIn(needle, idx, f"Template do index sem: {needle}")
        js = open(os.path.join(BASE_DIR, "js", "live_agent.js"), encoding="utf-8").read()
        self.assertIn("/api/live_status", js)
        self.assertIn("switchStore(storeKey)", js, "Resultado da busca deve trocar de loja automaticamente")


class TestTampermonkeyIntegration(unittest.TestCase):
    """Garante integridade e conformidade do Userscript Tampermonkey e da ponte no Portal."""

    def test_userscript_metadata_and_matches(self):
        script_path = os.path.join(BASE_DIR, "tampermonkey", "brk_assistente_shopify.user.js")
        self.assertTrue(os.path.exists(script_path), "Arquivo do userscript deve existir em tampermonkey/")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("// ==UserScript==", content)
        self.assertIn("@match        https://admin.shopify.com/store/*/products*", content)
        self.assertIn("@match        https://1025-ten.vercel.app/*", content)
        self.assertIn("@grant        GM_setValue", content)
        self.assertIn("@grant        GM_getValue", content)
        self.assertIn("brkfishing", content)
        self.assertIn("brkagro", content)
        self.assertIn("brkmotors25", content)

    def test_userscript_html_injection_and_tracking(self):
        script_path = os.path.join(BASE_DIR, "tampermonkey", "brk_assistente_shopify.user.js")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("injectDescriptionIntoShopify", content)
        self.assertIn("highlightSaveButton", content)
        self.assertIn("advanceToNextProduct", content)
        self.assertIn("appendBackup", content, "Script deve conter rotina de backup antes de alterar")
        self.assertIn("delaySeconds: 4", content, "Delay padrão deve ser de 4 segundos")

    def test_portal_integration_buttons_and_functions(self):
        app_js_path = os.path.join(BASE_DIR, "js", "app.js")
        with open(app_js_path, "r", encoding="utf-8") as f:
            app_js = f.read()

        self.assertIn("function sendBatchToTampermonkey", app_js)
        self.assertIn("function sendSelectedMassToTampermonkey", app_js)
        self.assertIn("function openTampermonkeyModal", app_js)

        build_dist_path = os.path.join(BASE_DIR, "build_modular_dist.py")
        with open(build_dist_path, "r", encoding="utf-8") as f:
            build_dist = f.read()

        self.assertIn('id="btn-tm-queue"', build_dist)
        self.assertIn('onclick="sendBatchToTampermonkey(25)"', build_dist)
        self.assertIn('onclick="sendSelectedMassToTampermonkey()"', build_dist)


class TestProductDBApiAndDirectConnection(unittest.TestCase):
    """Garante a conexão direta entre o userscript Tampermonkey e o banco de dados oficial (Vercel API)."""

    def test_product_db_loading_and_indexing(self):
        from api.product_db import load_store_database, sanitize_product, ALLOWED_STORES, STORE_SLUG_MAP

        # Assegurar que as 3 lojas estão mapeadas
        self.assertIn("brk_fishing", ALLOWED_STORES)
        self.assertIn("brk_agro", ALLOWED_STORES)
        self.assertIn("brk_motors", ALLOWED_STORES)
        self.assertEqual(STORE_SLUG_MAP["brkfishing"], "brk_fishing")
        self.assertEqual(STORE_SLUG_MAP["brkagro"], "brk_agro")
        self.assertEqual(STORE_SLUG_MAP["brkmotors25"], "brk_motors")

        # Carregar banco da BRK Fishing
        db = load_store_database("brk_fishing")
        self.assertIsNotNone(db, "Banco brk_fishing deve carregar com sucesso.")
        self.assertGreater(db["total"], 2000, "BRK Fishing deve ter mais de 2.000 produtos.")
        self.assertGreater(len(db["empty"]), 0, "Deve haver produtos com status SEM_DESCRICAO na BRK Fishing.")

        # Verificar produto de amostra
        sample_prod = db["empty"][0]
        sanitized = sanitize_product(sample_prod)
        self.assertIn("id", sanitized)
        self.assertIn("master_sku", sanitized)
        self.assertIn("title", sanitized)
        self.assertIn("status", sanitized)
        self.assertIn("mode_b_html", sanitized)
        self.assertTrue(len(sanitized["mode_b_html"]) > 100, "Produto deve conter mode_b_html preenchido.")

    def test_userscript_direct_db_headers(self):
        script_path = os.path.join(BASE_DIR, "tampermonkey", "brk_assistente_shopify.user.js")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("@grant        GM_xmlhttpRequest", content, "Userscript deve ter permissão GM_xmlhttpRequest para consultar a API.")
        self.assertIn("@connect      1025-ten.vercel.app", content, "Userscript deve ter @connect liberado para o domínio da Vercel.")
        self.assertIn("fetchFromBRKDatabase", content, "Userscript deve implementar a busca direta ao banco BRK.")
        self.assertIn("setReactInputValue", content, "Userscript deve usar o descriptor nativo do React para input no Polaris.")
        self.assertIn("startQueueFromDatabase", content, "Userscript deve permitir puxar a fila diretamente do banco.")

    def test_vercel_config_includes_data_files(self):
        vercel_json_path = os.path.join(BASE_DIR, "vercel.json")
        self.assertTrue(os.path.exists(vercel_json_path))
        with open(vercel_json_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        fn_cfg = cfg.get("functions", {}).get("api/*.py", {})
        self.assertIn("includeFiles", fn_cfg, "vercel.json deve configurar includeFiles para funções Python.")
        self.assertIn("data/stores", fn_cfg["includeFiles"], "includeFiles deve incluir data/stores no pacote serverless.")
        self.assertIn("core", fn_cfg["includeFiles"], "includeFiles deve incluir core no pacote serverless.")


class TestDeepFlowAuditGuardrails(unittest.TestCase):
    """Garante que colisões de substrings (ex: capivara vs vara, jeansfit vs jeans) nunca quebrem guias de tamanho."""

    @classmethod
    def setUpClass(cls):
        cls.engine = TemplateEngine()
        cls.builder = HTMLBuilder()

    def test_capivara_shirt_not_blocked_by_vara(self):
        prod = {"id": 1, "title": "Camisa de Pesca Feminina Brk Amazon Capivara Floral com Proteção UV50", "master_sku": "C02492BLP_FULL"}
        arch = self.engine.detect_archetype(prod["title"], "", [], "BRK", sku=prod["master_sku"])
        narrative = self.engine.generate_narrative_from_template(prod, arch, [], store_key="brk_fishing")
        html = self.builder.build_shopify_html(narrative)
        self.assertIn("brk-size-guide", html, "Camisa Capivara deve possuir guia de tamanhos")
        self.assertIn("ALTURA", html, "Camisa Capivara deve possuir coluna ALTURA")
        self.assertIn("FEMININO", html, "Camisa Capivara Feminina deve possuir badge FEMININO")

    def test_jeansfit_shirt_gets_shirt_guide_not_pants(self):
        prod = {"id": 2, "title": "Camisa de Pesca Infantil Brk Select Pursuit Jeansfit com Proteção UV50+", "master_sku": "C01325I"}
        arch = self.engine.detect_archetype(prod["title"], "", [], "BRK", sku=prod["master_sku"])
        narrative = self.engine.generate_narrative_from_template(prod, arch, [], store_key="brk_fishing")
        html = self.builder.build_shopify_html(narrative)
        self.assertIn("INFANTIL", html, "Camisa Jeansfit Infantil deve receber guia infantil")
        self.assertIn("ALTURA", html, "Camisa Jeansfit Infantil deve possuir coluna ALTURA")
        self.assertNotIn("Calças & Bermudas", html, "Camisa Jeansfit não pode cair em Calças")

    def test_hard_work_c0_shirt_gets_c0_guide(self):
        prod = {"id": 3, "title": "Camisa de Pesca Brk Kayak Fishing Hard Work com Proteção UV50", "master_sku": "C02402"}
        arch = self.engine.detect_archetype(prod["title"], "", [], "BRK", sku=prod["master_sku"])
        narrative = self.engine.generate_narrative_from_template(prod, arch, [], store_key="brk_fishing")
        html = self.builder.build_shopify_html(narrative)
        self.assertIn("MASCULINO", html, "Camisa C0 Hard Work deve receber guia C0 Masculino")
        self.assertIn("ALTURA", html, "Camisa C0 Hard Work deve possuir coluna ALTURA")
        self.assertNotIn("Camisas Work & Utilitárias de Botão", html, "Camisa C0 não pode receber guia de botão")

    def test_c0_shirts_have_official_xtech_pro_specs(self):
        # 1. Com _FULL -> Pronta entrega
        prod_full = {"id": 4, "title": "Camisa Agro Brk São Bento e Colheitadeira com Proteção UV50", "master_sku": "C02281P_FULL"}
        arch_full = self.engine.detect_archetype(prod_full["title"], "", [], "BRK", sku=prod_full["master_sku"])
        narrative_full = self.engine.generate_narrative_from_template(prod_full, arch_full, [], store_key="brk_agro")
        specs_full = {s["label"]: s["value"] for s in narrative_full.get("specs", [])}
        self.assertEqual(specs_full.get("Prazo de Produção"), "Pronta entrega")
        self.assertEqual(specs_full.get("Composição"), "90% Poliéster 10% Elastano")
        self.assertEqual(specs_full.get("Tecido"), "XTech Pro")
        self.assertEqual(specs_full.get("Tecnologia"), "Secagem Rápida, Tecido Leve, Proteção Solar")
        self.assertEqual(specs_full.get("Modelagem"), "Anatômica e confortável")
        self.assertEqual(specs_full.get("Proteção"), "Proteção UV50+ (não sai na lavagem)")

        # 2. Padrão (sem _FULL e sem _OUT) -> 10 dias úteis
        prod_std = {"id": 5, "title": "Camisa Agro Brk São Bento e Colheitadeira com Proteção UV50", "master_sku": "C02281P"}
        arch_std = self.engine.detect_archetype(prod_std["title"], "", [], "BRK", sku=prod_std["master_sku"])
        narrative_std = self.engine.generate_narrative_from_template(prod_std, arch_std, [], store_key="brk_agro")
        specs_std = {s["label"]: s["value"] for s in narrative_std.get("specs", [])}
        self.assertEqual(specs_std.get("Prazo de Produção"), "10 dias úteis")

        # 3. Com _OUT -> Pronta entrega
        prod_out = {"id": 6, "title": "Camisa Agro Brk São Bento e Colheitadeira com Proteção UV50", "master_sku": "C02281P_OUT"}
        arch_out = self.engine.detect_archetype(prod_out["title"], "", [], "BRK", sku=prod_out["master_sku"])
        narrative_out = self.engine.generate_narrative_from_template(prod_out, arch_out, [], store_key="brk_agro")
        specs_out = {s["label"]: s["value"] for s in narrative_out.get("specs", [])}
        self.assertEqual(specs_out.get("Prazo de Produção"), "Pronta entrega")

        # 4. Produto Não-C0 (Chapéu / Acessório) -> NÃO recebe 10 dias úteis nem Prazo de Produção têxtil
        prod_hat = {"id": 7, "title": "Chapéu BRK Agro Campo Aba Larga", "master_sku": "CHP100"}
        arch_hat = self.engine.detect_archetype(prod_hat["title"], "", [], "BRK", sku=prod_hat["master_sku"])
        narrative_hat = self.engine.generate_narrative_from_template(prod_hat, arch_hat, [], store_key="brk_agro")
        specs_hat = {s["label"]: s["value"] for s in narrative_hat.get("specs", [])}
        self.assertNotIn("Prazo de Produção", specs_hat)
        self.assertNotIn("10 dias úteis", str(specs_hat))

    def test_caps_and_hats_dedicated_d2c_layout(self):
        """Valida que bonés e chapéus recebem o layout D2C especializado com isolamento mútuo e sem vazamentos."""
        # 1. Boné Trucker
        prod_bone = {"id": 20, "title": "Boné Trucker BRK Fishing Peacemaker", "master_sku": "BA01"}
        arch_bone = self.engine.detect_archetype(prod_bone["title"], "", [], "BRK", sku=prod_bone["master_sku"])
        narrative_bone = self.engine.generate_narrative_from_template(prod_bone, arch_bone, [], store_key="brk_fishing")
        html_bone = self.builder.build_shopify_html(narrative_bone)

        self.assertIn("brk-cap-description", html_bone)
        self.assertIn("Aba Moldável", html_bone)
        self.assertIn("Interno em Tear", html_bone)
        self.assertIn("Etiqueta BRK de Qualidade", html_bone)
        self.assertIn("Design Exclusivo", html_bone)
        self.assertIn("PRODUTO PREMIUM BRK", html_bone)
        self.assertIn("ENTREGA SEGURA BRK", html_bone)
        self.assertIn("CAIXA-BRK.webp", html_bone)
        self.assertNotIn("use-brk-images-s3", html_bone)

        # 2. Chapéu Safári
        prod_safari = {"id": 21, "title": "Chapéu de Pesca Australiano BRK com Protetor de Nuca UV50+", "master_sku": "CHP01"}
        arch_safari = self.engine.detect_archetype(prod_safari["title"], "", [], "BRK", sku=prod_safari["master_sku"])
        narrative_safari = self.engine.generate_narrative_from_template(prod_safari, arch_safari, [], store_key="brk_fishing")
        html_safari = self.builder.build_shopify_html(narrative_safari)

        self.assertIn("brk-cap-description", html_safari)
        self.assertIn("Aba 360° UV50+", html_safari)
        self.assertIn("Cordão Jugular Anti-Vento", html_safari)
        self.assertIn("Protetor de Nuca Integrado", html_safari)
        self.assertNotIn("estilo trucker", html_safari)

        # 3. Chapéu Country
        prod_country = {"id": 22, "title": "Chapéu American Hat Cattleman Chocolate Feltro", "master_sku": "CHC01"}
        arch_country = self.engine.detect_archetype(prod_country["title"], "", [], "BRK", sku=prod_country["master_sku"])
        narrative_country = self.engine.generate_narrative_from_template(prod_country, arch_country, [], store_key="brk_agro")
        html_country = self.builder.build_shopify_html(narrative_country)

        self.assertIn("brk-cap-description", html_country)
        self.assertIn("Aba Larga Estruturada", html_country)
        self.assertIn("Carneira Interna Confortável", html_country)
        self.assertIn("Fita & Acabamento Premium", html_country)
        self.assertNotIn("estilo trucker", html_country)

        # 4. Camisa C0 NÃO recebe brk-cap-description
        prod_shirt = {"id": 23, "title": "Camisa de Pesca Dourado com Proteção UV50", "master_sku": "C0100"}
        arch_shirt = self.engine.detect_archetype(prod_shirt["title"], "", [], "BRK", sku=prod_shirt["master_sku"])
        narrative_shirt = self.engine.generate_narrative_from_template(prod_shirt, arch_shirt, [], store_key="brk_fishing")
        html_shirt = self.builder.build_shopify_html(narrative_shirt)
        self.assertNotIn("brk-cap-description", html_shirt)

    def test_caixa_de_pesca_and_containers_not_lures(self):
        """Valida que caixas organizadoras de iscas são tackle_boxes_storage e JAMAIS recebem specs de isca viva ou nado."""
        prod_caixa = {
            "id": 991,
            "title": "Caixa de Pesca Organizadora de Iscas Artificiais Brk - até 80 Iscas",
            "category": "Equipamentos & Iscas",
            "master_sku": "CX01"
        }
        arch = self.engine.detect_archetype(prod_caixa["title"], prod_caixa["category"], [], "BRK", sku=prod_caixa["master_sku"])
        self.assertEqual(arch, "tackle_boxes_storage")
        
        narrative = self.engine.generate_narrative_from_template(prod_caixa, arch, [], store_key="brk_fishing")
        html = self.builder.build_shopify_html(narrative)
        
        # Não pode alucinar atributos de isca
        self.assertNotIn("NADO REALISTA", html)
        self.assertNotIn("Garatéias", html)
        self.assertNotIn("Rattling", html)
        self.assertNotIn("brk-cap-description", html)
        self.assertNotIn("<details class=\"brk-size-guide\"", html)
        self.assertIn("DIVISÓRIAS MODULARES", html)
        self.assertIn("TRAVAS DUPLAS", html)

    def test_copos_termicos_and_sunglasses_disambiguation(self):
        """Valida que Copo Térmico com 'iscas' ou 'bones' não cai em isca ou boné, e óculos com acento grave são detectados."""
        # Copo Térmico com Iscas no título
        arch_copo_iscas = self.engine.detect_archetype("Copo Térmico Iscas BRK", "Térmicos", [], "BRK")
        self.assertEqual(arch_copo_iscas, "drinkware_thermo")

        # Copo Térmico com Bones em inglês
        arch_copo_bones = self.engine.detect_archetype("Copo Térmico Hooked Till The Bones BRK", "Térmicos", [], "BRK")
        self.assertEqual(arch_copo_bones, "drinkware_thermo")

        # Óculos com acento grave Ò
        arch_oculos = self.engine.detect_archetype("\xd2culos de Sol Retro Black", "Acessórios", [], "BRK")
        self.assertEqual(arch_oculos, "eyewear_sunglasses")

    def test_headwear_d2c_moldes_and_products_conformity(self):
        """Valida que os moldes de Bonés e Chapéus possuem layout_format d2c_headwear e os produtos têm mode_b_html 100% preenchido."""
        # 1. Verifica moldes mestres no template_engine
        for arch_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
            tmpl = self.engine.templates.get(arch_id)
            self.assertIsNotNone(tmpl)
            self.assertEqual(tmpl.get("layout_format"), "d2c_headwear")
            self.assertEqual(len(tmpl.get("details_grid", [])), 4)
            self.assertEqual(len(tmpl.get("info_characteristics", [])), 5)
            self.assertEqual(len(tmpl.get("info_care", [])), 5)
            self.assertEqual(len(tmpl.get("split_sections", [])), 2)

        # 2. Verifica exportação em moldes.json
        moldes_path = os.path.join(BASE_DIR, "data", "stores", "moldes.json")
        if os.path.exists(moldes_path):
            with open(moldes_path, "r", encoding="utf-8") as f:
                moldes_data = json.load(f)
            cap_m = moldes_data.get("caps_trucker_snapback", {})
            self.assertEqual(cap_m.get("layout_format"), "d2c_headwear")
            self.assertEqual(len(cap_m.get("details_grid", [])), 4)

        # 3. Verifica que o produto 'Boné Trucker de Pesca Brk Isca Artificial - Preto e Vermelho' tem o HTML D2C oficial
        fishing_path = os.path.join(BASE_DIR, "data", "stores", "brk_fishing.json")
        if os.path.exists(fishing_path):
            with open(fishing_path, "r", encoding="utf-8") as f:
                fishing_data = json.load(f)
            prod = next((p for p in fishing_data.get("products", []) if "Boné Trucker de Pesca Brk Isca Artificial - Preto e Vermelho" in p.get("title", "")), None)
            self.assertIsNotNone(prod)
            self.assertEqual(prod.get("archetype_id"), "caps_trucker_snapback")
            self.assertEqual(prod.get("layout_format"), "d2c_headwear")
            self.assertTrue(len(prod.get("mode_b_html", "")) > 1000)
            self.assertIn("brk-cap-description", prod.get("mode_b_html", ""))
            self.assertIn("Aba Moldável", prod.get("mode_b_html", ""))
            self.assertIn("Interno em Tear", prod.get("mode_b_html", ""))
            self.assertIn("CAIXA-BRK", prod.get("mode_b_html", ""))

    def test_fusion_and_hybrid_anti_zipper_and_hood_rules(self):
        """Valida que camisas Fusion e Hybrid JAMAIS contêm menção a zíper e possuem capuz/máscara/dedeira e regras de prazo."""
        # 1. Fusion Padrão (sem zíper, com máscara facial integrada, dedeira e 10 dias úteis)
        prod_fusion = {
            "id": 8801,
            "title": "Camisa de Pesca FusionX BRK Tucunaré Azul UV50+",
            "category": "Camisas",
            "master_sku": "C0FUSION01"
        }
        arch_fusion = self.engine.detect_archetype(prod_fusion["title"], prod_fusion["category"], [], "BRK", sku=prod_fusion["master_sku"])
        narrative_fusion = self.engine.generate_narrative_from_template(prod_fusion, arch_fusion, [], store_key="brk_fishing")
        html_fusion = self.builder.build_shopify_html(narrative_fusion)
        html_fusion_low = html_fusion.lower()

        self.assertNotIn("zíper", html_fusion_low, "Fusion NÃO pode conter palavra zíper!")
        self.assertNotIn("ziper", html_fusion_low, "Fusion NÃO pode conter palavra ziper!")
        self.assertIn("máscara facial", html_fusion_low)
        self.assertIn("dedeira", html_fusion_low)
        self.assertIn("Capuz & Máscara", html_fusion)
        self.assertIn("Punhos", html_fusion)
        self.assertIn("10 dias úteis", html_fusion)
        self.assertNotIn("Pronta entrega", html_fusion)

        # 2. Fusion com _FULL (Pronta entrega e sem zíper)
        prod_fusion_full = {
            "id": 8802,
            "title": "Camisa Fusion BRK Robalo Cinza com Proteção Solar",
            "category": "Camisas",
            "master_sku": "C0FUSION02_FULL"
        }
        narrative_ff = self.engine.generate_narrative_from_template(prod_fusion_full, arch_fusion, [], store_key="brk_fishing")
        html_ff = self.builder.build_shopify_html(narrative_ff)
        self.assertNotIn("zíper", html_ff.lower())
        self.assertNotIn("ziper", html_ff.lower())
        self.assertIn("Pronta entrega", html_ff)
        self.assertNotIn("10 dias úteis", html_ff)

        # 3. Hybrid Padrão (sem zíper, com capuz integrado, dedeira e 10 dias úteis)
        prod_hybrid = {
            "id": 8803,
            "title": "Camisa Hybrid BRK Bass Hunter UV50+",
            "category": "Camisas",
            "master_sku": "C0HYBRID01"
        }
        arch_hybrid = self.engine.detect_archetype(prod_hybrid["title"], prod_hybrid["category"], [], "BRK", sku=prod_hybrid["master_sku"])
        narrative_hybrid = self.engine.generate_narrative_from_template(prod_hybrid, arch_hybrid, [], store_key="brk_fishing")
        html_hybrid = self.builder.build_shopify_html(narrative_hybrid)
        html_hybrid_low = html_hybrid.lower()

        self.assertNotIn("zíper", html_hybrid_low, "Hybrid NÃO pode conter palavra zíper!")
        self.assertNotIn("ziper", html_hybrid_low, "Hybrid NÃO pode conter palavra ziper!")
        self.assertIn("capuz anatômico integrado", html_hybrid_low)
        self.assertIn("dedeira", html_hybrid_low)
        self.assertIn("Punhos", html_hybrid)
        self.assertIn("10 dias úteis", html_hybrid)
        self.assertNotIn("Pronta entrega", html_hybrid)

    def test_act3_image_semantic_alignment_and_no_back_zipper(self):
        """Valida que o Ato 3 de camisas UV recebe sempre foto Frontal (deslocando Costas para o Ato 2) e preserva foco em Gola, Zíper e Punhos."""
        prod = {
            "id": 999901,
            "title": "Camisa de Pesca BRK Patriota Masculina UV50+",
            "category": "Camisas de Pesca UV",
            "master_sku": "C0PATRIOTA01"
        }
        gallery_with_back = [
            "https://cdn.shopify.com/files/frente.jpg",
            "https://cdn.shopify.com/files/tecido.jpg",
            "https://cdn.shopify.com/files/1786018701234-09_MASC_COSTAS.jpg"
        ]
        arch = self.engine.detect_archetype(prod["title"], prod["category"], [], "BRK", sku=prod["master_sku"])
        narrative = self.engine.generate_narrative_from_template(prod, arch, gallery_with_back, store_key="brk_fishing")
        
        # Validar blocos narrativos: Ato 2 recebe a foto de Costas e Ato 3 recebe a foto Frontal/Detalhe
        blocks = narrative["narrative_blocks"]
        act2 = blocks[1]
        act3 = blocks[2]
        self.assertEqual(act2["image"], gallery_with_back[2])
        self.assertEqual(act3["image"], gallery_with_back[1])
        self.assertNotIn("TRASEIRO", act3["title"].upper())

        # Validar HTML final
        html = self.builder.build_shopify_html(narrative)
        # O zíper deve constar nas specs técnicas (Gola / Fechamento)
        self.assertIn("Gola padre anatômica com zíper", html)
        self.assertIn("trava de segurança", html)

    def test_smart_3_act_apparel_image_ordering_and_python_js_parity(self):
        """Valida que fotos de Costas (02 / -2 / COSTAS) vão para o Ato 2, Frente para o Ato 1 e 3/4 Frontal/Detalhe para o Ato 3, com paridade Python/JS."""
        from core.html_replacer import HTMLReplacer

        # 1. Galeria padrão BRK de estúdio onde a 2ª foto é Costas (-2 / 02FEM) e a 3ª é Perspectiva Frontal (-3 / 03FEM)
        prod = {
            "id": 999902,
            "title": "Camisa de Pesca Feminina BRK Capivara Floral UV50+",
            "category": "Camisas de Pesca UV",
            "master_sku": "C02846BL"
        }
        gallery_123 = [
            "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1784823571109-1.jpg",
            "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1784823571109-2.jpg",
            "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1784823571109-3.jpg"
        ]
        arch = self.engine.detect_archetype(prod["title"], prod["category"], [], "BRK", sku=prod["master_sku"])
        narrative = self.engine.generate_narrative_from_template(prod, arch, gallery_123, store_key="brk_fishing")
        blocks = narrative["narrative_blocks"]

        # Ato 1 = Foto 1 (Frente), Ato 2 = Foto 2 (Costas), Ato 3 = Foto 3 (3/4 Frontal)
        self.assertEqual(blocks[0]["image"], gallery_123[0])
        self.assertEqual(blocks[1]["image"], gallery_123[1])
        self.assertEqual(blocks[2]["image"], gallery_123[2])
        self.assertNotIn("PAINEL TRASEIRO", blocks[2]["title"])
        self.assertIn("MODELAGEM FEMININA ANATÔMICA", blocks[0]["title"])

        # 2. Galeria invertida onde Costas foi subida como 1ª foto (ex: C02822BL)
        gallery_inverted = [
            "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/COSTAS_FEM.jpg",
            "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/FRENTEPERSPECTIVA_FEM.jpg",
            "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/FRENTE_FEM.jpg"
        ]
        narrative_inv = self.engine.generate_narrative_from_template(prod, arch, gallery_inverted, store_key="brk_agro")
        blocks_inv = narrative_inv["narrative_blocks"]
        self.assertEqual(blocks_inv[0]["image"], gallery_inverted[1], "Ato 1 deve promover foto frontal")
        self.assertEqual(blocks_inv[1]["image"], gallery_inverted[0], "Ato 2 deve receber a foto de costas COSTAS_FEM.jpg")
        self.assertEqual(blocks_inv[2]["image"], gallery_inverted[2], "Ato 3 deve receber a foto frontal FRENTE_FEM.jpg")
        self.assertNotIn("PAINEL TRASEIRO", blocks_inv[2]["title"])

        # 3. Timestamp HH_MM_SS com _02_ não pode ser confundido com foto de costas
        self.assertFalse(self.engine._is_back_view_url("https://cdn.shopify.com/files/ChatGPT_Image_24_de_set._de_2026_10_02_34.png"))

        # 4. HTMLReplacer não pode deixar imgur.com ou postimg.cc sobrando no Modo A
        replacer = HTMLReplacer()
        dirty_html = (
            '<p>Texto</p>'
            '<img src="https://i.imgur.com/1.jpg">'
            '<img src="https://i.imgur.com/2.jpg">'
            '<img src="https://i.imgur.com/3.jpg">'
            '<img src="https://i.imgur.com/4.jpg">'
            '<img src="https://i.postimg.cc/5.png">'
        )
        clean_mode_a = replacer.replace_images_preserve_html(dirty_html, gallery_123, prod["title"])
        self.assertNotIn("imgur.com", clean_mode_a)
        self.assertNotIn("postimg.cc", clean_mode_a)

        # 5. Paridade JS (js/modal.js)
        js_path = os.path.join(BASE_DIR, "js", "modal.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()
        self.assertIn("function isClientBackViewUrl", js_code)
        self.assertIn("function selectClientApparelActImages", js_code)
        self.assertIn("delete p.narrative_blocks;", js_code)
        self.assertIn("delete p.split_images;", js_code)

    def test_store_category_classification_and_full_3_store_sync(self):
        """Valida que as categorias das 3 lojas não misturam produtos díspares e que 100% do catálogo das 3 lojas está sincronizado."""
        engine = TemplateEngine()
        # 1. Casos críticos que antes vazavam de categoria
        cases = [
            ("Camisa de Pesca Proteção Solar UV50+ Capivara Pescadora Brk", "brk_fishing", "Camisas de Pesca UV"),
            ("Camisa De Pesca Infantil Brk Caramelo De Óculos Com Proteção Solar Uv50+", "brk_fishing", "Camisas de Pesca UV"),
            ("Camisa de Pesca Brk Manga Longa FusionX", "brk_fishing", "Camisas de Pesca UV"),
            ("Boné Trucker Brk Fishing Bass", "brk_fishing", "Bonés & Chapéus"),
            ("Vara de Pesca Marine Sports Gladius", "brk_fishing", "Equipamentos & Iscas"),
            ("Botina Country Masculina Couro Legítimo Brk Agro", "brk_agro", "Botinas & Calçados"),
            ("Chapéu Country Pralana Feltro", "brk_agro", "Bonés & Chapéus Agro"),
            ("Faca Artesanal Inox 8 Polegadas", "brk_agro", "Cutelaria & Facas Campo"),
            ("Jersey Motocross Trilha Brk Motors", "brk_motors", "Jerseys & Camisas Motors"),
            ("Camisa Masculina Brk Motors Dakar Com Proteção Solar UV50+", "brk_motors", "Jerseys & Camisas Motors"),
        ]
        for title, sk, expected_cat in cases:
            arch = engine.detect_archetype(title, "", "")
            cat = engine.classify_store_category(title, arch, sk)
            self.assertEqual(cat, expected_cat, f"Falha na categoria de '{title}' ({sk}): {cat} != {expected_cat}")

        # 2. Verificar catálogos compilados das 3 lojas
        min_counts = {"brk_fishing": 2100, "brk_agro": 2500, "brk_motors": 1400}
        for sk, min_total in min_counts.items():
            store_path = os.path.join(BASE_DIR, "data", "stores", f"{sk}.json")
            self.assertTrue(os.path.exists(store_path), f"Store compilada ausente: {store_path}")
            with open(store_path, "r", encoding="utf-8") as f:
                sdata = json.load(f)
            prods = sdata.get("products", [])
            self.assertGreaterEqual(len(prods), min_total, f"Catálogo {sk} incompleto: {len(prods)} < {min_total}")
            cats = sdata.get("categories", {})
            cats_list = list(cats.values()) if isinstance(cats, dict) else cats
            self.assertGreaterEqual(len(cats_list), 4, f"Loja {sk} deve ter categorias estruturadas")
            for c in cats_list:
                self.assertTrue(c.get("thumb", "").startswith("https://cdn.shopify.com/"), f"Thumb inválida em {sk}/{c.get('name')}")

    def test_phase5_apparel_gender_kids_age_sizing_and_store_theme_colors(self):
        """Valida regras da Fase 5: filtro de fotos Fem/Inf/Masc, tabela Infantil por Idade+Tamanho, Camisa Work CMB, Corta-Vento e cores por loja."""
        engine = TemplateEngine()
        builder = HTMLBuilder()

        # 1. Filtro de fotos de família mista (Feminina vs Infantil vs Masculina)
        mixed_gallery = [
            "https://cdn.shopify.com/s/files/1/0595/3185/3999/files/C0253_MASC_FRENTE.jpg",
            "https://cdn.shopify.com/s/files/1/0595/3185/3999/files/C0253_MASC_COSTAS.jpg",
            "https://cdn.shopify.com/s/files/1/0595/3185/3999/files/C0253_FEM_FRENTE.jpg",
            "https://cdn.shopify.com/s/files/1/0595/3185/3999/files/C0253_FEM_COSTAS.jpg",
            "https://cdn.shopify.com/s/files/1/0595/3185/3999/files/C0253_INF_FRENTE.jpg",
            "https://cdn.shopify.com/s/files/1/0595/3185/3999/files/C0253_INF_COSTAS.jpg",
        ]
        fem_acts = [u for u in engine._select_apparel_act_images(mixed_gallery, is_female=True, is_kids=False) if u]
        self.assertTrue(len(fem_acts) >= 2 and all("_FEM_" in u for u in fem_acts), f"Camisa feminina recebeu foto masculina/infantil: {fem_acts}")
        kids_acts = [u for u in engine._select_apparel_act_images(mixed_gallery, is_female=False, is_kids=True) if u]
        self.assertTrue(len(kids_acts) >= 2 and all("_INF_" in u for u in kids_acts), f"Camisa infantil recebeu foto adulta: {kids_acts}")
        masc_acts = [u for u in engine._select_apparel_act_images(mixed_gallery, is_female=False, is_kids=False) if u]
        self.assertTrue(len(masc_acts) >= 2 and all("_MASC_" in u for u in masc_acts), f"Camisa masculina recebeu foto fem/inf: {masc_acts}")

        # 2. Camisa Infantil por Idade + Tamanho (1 a 13 Anos | PP ao G2) e detecção por SKU (C0612I / CI0040)
        prod_kids = {"id": 9901, "title": "Camisa de Pesca BRK UV50+", "category": "Camisas de Pesca UV", "master_sku": "C0612I"}
        arch_kids = engine.detect_archetype(prod_kids["title"], prod_kids["category"], [], "BRK", sku=prod_kids["master_sku"])
        nar_kids = engine.generate_narrative_from_template(prod_kids, arch_kids, mixed_gallery, store_key="brk_fishing")
        html_kids = builder.build_shopify_html(nar_kids)
        self.assertIn("IDADE / TAMANHO", html_kids)
        self.assertIn("1 a 2 Anos (PP)", html_kids)
        self.assertIn("12 a 13 Anos (G2)", html_kids)
        self.assertIn("1 a 13 Anos | PP ao G2", html_kids)

        # 3. Camisa Work (CMB011) não deve ter gola redonda duplicada
        prod_work = {"id": 9902, "title": "Camisa Work Brk Agro UV50+ Verde Militar", "category": "Camisas Agro", "master_sku": "CMB011"}
        arch_work = engine.detect_archetype(prod_work["title"], prod_work["category"], [], "BRK", sku=prod_work["master_sku"])
        nar_work = engine.generate_narrative_from_template(prod_work, arch_work, [], store_key="brk_agro")
        specs_work_str = json.dumps(nar_work.get("specs", []), ensure_ascii=False)
        self.assertNotIn("Gola redonda anatômica", specs_work_str)
        self.assertIn("Abotoamento frontal reforçado", specs_work_str)

        # 4. Corta-Vento (Windbreaker)
        prod_wb = {"id": 9903, "title": "Corta Vento Impermeável Brk Motors", "category": "Jaquetas", "master_sku": "CV001"}
        arch_wb = engine.detect_archetype(prod_wb["title"], prod_wb["category"], [], "BRK", sku=prod_wb["master_sku"])
        nar_wb = engine.generate_narrative_from_template(prod_wb, arch_wb, [], store_key="brk_motors")
        self.assertIn("VENTO", nar_wb["narrative_blocks"][0]["title"])
        self.assertIn("Corta-Vento", nar_wb["narrative_blocks"][0]["tag"])

        # 5. Coerência estrita de cores nos 3 sites (Azul = Fishing, Verde = Agro, Laranja = Motors)
        expected_colors = {
            "brk_fishing": ("#0284c7", "#00a8ff"),
            "brk_agro": ("#16a34a", "#15803d"),
            "brk_motors": ("#f97316", "#ea580c"),
        }
        for sk, (hex_color, cap_color) in expected_colors.items():
            prod_st = {"id": 9904, "title": "Camisa UV50+ Teste", "category": "Camisas", "master_sku": "C0999"}
            arch_st = engine.detect_archetype(prod_st["title"], prod_st["category"], [], "BRK", sku=prod_st["master_sku"])
            nar_st = engine.generate_narrative_from_template(prod_st, arch_st, [], store_key=sk)
            html_st = builder.build_shopify_html(nar_st)
            self.assertIn(hex_color, html_st, f"Cor oficial {hex_color} ausente no HTML da loja {sk}")
            self.assertNotIn("#2e7d32", html_st, f"Verde legado #2e7d32 vazou no HTML da loja {sk}")
            prod_cap = {"id": 9905, "title": "Boné Trucker Oficial", "category": "Bonés", "master_sku": "BN999"}
            arch_cap = engine.detect_archetype(prod_cap["title"], prod_cap["category"], [], "BRK", sku=prod_cap["master_sku"])
            nar_cap = engine.generate_narrative_from_template(prod_cap, arch_cap, [], store_key=sk)
            html_cap = builder.build_shopify_html(nar_cap)
            self.assertIn(cap_color, html_cap, f"Cor oficial {cap_color} ausente no Boné D2C da loja {sk}")




class TestBRKStudioVerticalization(unittest.TestCase):
    def test_persona_manager_coverage(self):
        """Valida que todas as 3 lojas possuem personas masculinas e femininas cadastradas com prompts de alta fidelidade."""
        from services.studio import persona_manager
        for st in ("brk_fishing", "brk_agro", "brk_motors"):
            personas = persona_manager.list_by_store(st)
            self.assertTrue(len(personas) >= 2, f"Loja {st} deve ter pelo menos 2 personas (masculina e feminina)")
            genders = {p.gender for p in personas}
            self.assertIn("masculino", genders)
            self.assertIn("feminina", genders)
            for p in personas:
                self.assertTrue(len(p.prompt_scene) > 50)
                self.assertTrue(p.base_model_url.startswith("http"))

    def test_garment_processor_extraction(self):
        """Valida que o extrator de peças identifica a URL primária da Shopify e define o cache."""
        from services.studio import garment_processor
        prod = {
            "master_sku": "C099TEST",
            "title": "Camisa Teste UV50+",
            "gallery": ["https://cdn.shopify.com/s/files/1/0628/1445/3826/files/test.jpg"]
        }
        url = garment_processor.extract_primary_image_url(prod)
        self.assertEqual(url, "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/test.jpg")

    def test_studio_orchestrator_pipeline_dryrun(self):
        """Valida que o orquestrador do BRK Studio executa o ciclo completo em dry_run e salva resultado."""
        from services.studio import studio_orchestrator
        prod = {
            "master_sku": "C099DRY",
            "title": "Camisa Feminina Brk Agro Teste UV50+",
            "gallery": ["https://cdn.shopify.com/s/files/1/0628/1445/3826/files/pBekKbx.jpg?v=1758912299"]
        }
        res = studio_orchestrator.generate_humanized_photo(prod, store_key="brk_agro", provider="dry_run")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("persona_id"), "agro_female_field")
        self.assertTrue(os.path.exists(res.get("local_path")))

    def test_phase6_headwear_unique_gallery_images_and_store_vocabulary_isolation(self):
        """
        Fase 6:
        1. Bonés e Chapéus utilizam suas próprias 4 fotos reais da galeria nos 4 Cards de Detalhes (sem repetir eQxQuY7/k2bupYT/BYAO1Oj/cjeqbhc quando há galeria própria).
        2. Tabelas/gráficos .png são filtrados quando há >= 4 fotos reais (.jpg/.webp) na galeria do boné/chapéu.
        3. Isolamento semântico de vocabulário entre lojas (zero vazamento de 'pescaria' em Infantil/Hybrid/Bandanas/Cutelaria de brk_agro e brk_motors).
        4. Isolamento de fotos por público em famílias CASUAL* com SKU embutido (casual13bl, casual13ip, casual13g).
        5. Reclassificação de overalls_workwear (Jardineira Wader) para 'Equipamentos & Iscas' em brk_fishing.
        """
        cap_a = {
            "id": 9901,
            "sku": "BA010",
            "title": "Boné BRK Agro Country Edition Verde",
            "images": [
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/tabela_medidas_bone.png",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/ba010_foto1.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/ba010_foto2.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/ba010_foto3.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/ba010_foto4.jpg",
            ],
        }
        cap_b = {
            "id": 9902,
            "sku": "BM005",
            "title": "Boné BRK Motors Racing Preto",
            "images": [
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/bm005_foto1.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/bm005_foto2.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/bm005_foto3.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/bm005_foto4.jpg",
            ],
        }
        template_engine = TemplateEngine()
        html_builder = HTMLBuilder()
        enr_a = template_engine.generate_narrative_from_template(cap_a, "caps_trucker_snapback", cap_a["images"], store_key="brk_agro")
        enr_b = template_engine.generate_narrative_from_template(cap_b, "caps_trucker_snapback", cap_b["images"], store_key="brk_motors")
        html_a = html_builder.build_shopify_html(enr_a)
        html_b = html_builder.build_shopify_html(enr_b)

        for idx in range(1, 5):
            self.assertIn(f"ba010_foto{idx}.jpg", html_a)
            self.assertIn(f"bm005_foto{idx}.jpg", html_b)
            self.assertNotIn(f"bm005_foto{idx}.jpg", html_a)
        self.assertNotIn('src="https://cdn.shopify.com/s/files/1/0628/1445/3826/files/tabela_medidas_bone.png"', html_a)
        self.assertNotIn("eQxQuY7.jpg", html_a)
        self.assertNotIn("eQxQuY7.jpg", html_b)

        # Isolamento de vocabulário em brk_agro e brk_motors
        kids_agro = {
            "id": 9903,
            "sku": "C0200I",
            "title": "Camisa Infantil Brk Agro Trator Com Proteção Solar UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0628/1445/3826/files/c0200i_1.jpg"],
        }
        enr_kids_agro = template_engine.generate_narrative_from_template(kids_agro, "uv_performance", kids_agro["images"], store_key="brk_agro")
        self.assertNotIn("pescaria", enr_kids_agro["act2"]["description"].lower())
        self.assertIn("fazenda", enr_kids_agro["act2"]["description"].lower())

        gaiter_motors = {
            "id": 9904,
            "sku": "BM100",
            "title": "Bandana Tubeneck Brk Motors Racing Com Proteção Solar UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0628/1445/3826/files/bm100_1.jpg"],
        }
        enr_gaiter_motors = template_engine.generate_narrative_from_template(gaiter_motors, "neck_gaiters_balaclavas", gaiter_motors["images"], store_key="brk_motors")
        self.assertNotIn("pescaria", enr_gaiter_motors["act1"]["description"].lower())
        self.assertIn("pilotagem", enr_gaiter_motors["act1"]["description"].lower())

        # Isolamento de galeria mista CASUAL*
        mixed_casual = [
            "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/casual13g-1.jpg",
            "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/casual13blp-1.jpg",
            "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/casual13blp-2.jpg",
            "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/casual13ip-1.jpg",
        ]
        fem_imgs = template_engine._select_apparel_act_images(mixed_casual, is_female=True, is_kids=False)
        self.assertTrue(all("casual13blp" in u for u in fem_imgs if u))

        # Reclassificação de Jardineira Wader em brk_fishing
        cat_wader = template_engine.classify_store_category(
            "Macacão Jardineira de Pesca Com Bota de Silicone Impermeável",
            "overalls_workwear",
            store_key="brk_fishing",
        )
        self.assertEqual(cat_wader, "Equipamentos & Iscas")

    def test_phase7_shopify_duplicate_first_photo_contingency(self):
        """
        Fase 7 (Contingência Anti-Duplicação da 1ª Foto na Shopify):
        1. Garante que FUSION197 (e similares onde o ERP envia 1ª foto de capa isolada + lote com 1ª foto repetida)
           jamais duplica a 1ª foto entre Ato 1 e Ato 2.
        2. Garante desduplicação por prefixo de timestamp (1743615730371-1_MASC.jpg vs 1_MASC.jpg),
           sufixos de re-exportação (_-_JPG.jpg vs .png) e múltiplos mockups de frente.
        3. Garante colapso de capas repetidas por variante de tamanho (RAGLAN306BL / CADV176BL / MT060).
        """
        template_engine = TemplateEngine()
        html_builder = HTMLBuilder()

        # Caso 1: FUSION197 (4 URLs originais da Shopify onde pos 1 e pos 2 eram a mesma foto de capa com 79.109 bytes)
        fusion197_raw_urls = [
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/https_3A_2F_2Ffile-upload-service-production.s3.amazonaws.com_2FproductOnChannel_2Fimages_2F9dd84323-a39d-4c8f-8b0d-9b3df45e78c8_2F785073fe67084624b010164a4c158a4b.jpg?v=1774636895",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/https_3A_2F_2Ffile-upload-service-production.s3.amazonaws.com_2FproductOnChannel_2Fimages_2F626a5a68-6ba1-4429-a8df-d8420ca1fc47_2Ffb17213952f84ecca5ec7b02ec3304be_ec8f9a1f-df51-4e78-9d2a-d7db80d4e21b.jpg?v=1774903025",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/https_3A_2F_2Ffile-upload-service-production.s3.amazonaws.com_2FproductOnChannel_2Fimages_2F626a5a68-6ba1-4429-a8df-d8420ca1fc47_2Fed712d1d226e41c7accf7162507c92a4.jpg?v=1774903028",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/https_3A_2F_2Ffile-upload-service-production.s3.amazonaws.com_2FproductOnChannel_2Fimages_2F626a5a68-6ba1-4429-a8df-d8420ca1fc47_2Fb7c4a9e674bd4f97bb32e5488b434005.jpg?v=1774903030",
        ]
        fusion_prod = {
            "id": 9183938609217,
            "sku": "FUSION197",
            "title": "Camisa FusionX Brk Pescaiaque Azul e Amarelo com Proteção UV50+",
            "images": fusion197_raw_urls,
        }
        enr_f197 = template_engine.generate_narrative_from_template(
            fusion_prod, "uv_performance", fusion197_raw_urls, store_key="brk_fishing"
        )
        html_f197 = html_builder.build_shopify_html(enr_f197)
        self.assertNotIn("fb17213952f84ecca5ec7b02ec3304be", html_f197)
        self.assertIn("785073fe67084624b010164a4c158a4b", enr_f197["act1"]["image"])
        self.assertIn("ed712d1d226e41c7accf7162507c92a4", enr_f197["act2"]["image"])
        self.assertIn("b7c4a9e674bd4f97bb32e5488b434005", enr_f197["act3"]["image"])

        # Caso 2: Desduplicação por prefixo de timestamp e sufixo _-_JPG
        ts_urls = [
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/1_MASC.jpg?v=1",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/1743615730371-1_MASC.jpg?v=2",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/Mockup_Fem_MASTER_01_FRENTE_-_JPG.jpg?v=3",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/Mockup_Fem_MASTER_01_FRENTE.png?v=4",
            "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/2_MASC_COSTAS.jpg?v=5",
        ]
        deduped_ts = template_engine._sanitize_and_dedup_images(ts_urls, archetype_id="uv_performance", title="Camisa BRK UV50+")
        self.assertEqual(len(deduped_ts), 3)
        self.assertNotIn("https://cdn.shopify.com/s/files/1/0612/8068/2177/files/1743615730371-1_MASC.jpg?v=2", deduped_ts)
        self.assertNotIn("https://cdn.shopify.com/s/files/1/0612/8068/2177/files/Mockup_Fem_MASTER_01_FRENTE.png?v=4", deduped_ts)

        # Caso 3: Colapso de variant_ids repetidos por tamanho (Camada 1)
        shopify_img_objs = [
            {"src": "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/capa_p.jpg", "variant_ids": [101], "width": 1080, "height": 1080},
            {"src": "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/capa_m.jpg", "variant_ids": [102], "width": 1080, "height": 1080},
            {"src": "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/capa_g.jpg", "variant_ids": [103], "width": 1080, "height": 1080},
            {"src": "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/costas.jpg", "variant_ids": [], "width": 1080, "height": 1080},
            {"src": "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/detalhe.jpg", "variant_ids": [], "width": 1080, "height": 1080},
        ]
        deduped_var = template_engine._sanitize_and_dedup_images(shopify_img_objs, archetype_id="uv_performance", title="Camisa Segunda Pele BRK")
        self.assertEqual(len(deduped_var), 3)
        self.assertEqual(deduped_var[0], "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/capa_p.jpg")
        self.assertEqual(deduped_var[1], "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/costas.jpg")

        # Caso 4: Camisa ArmorX "com Luva" deve receber Tabela de Camisa (Masculina/Feminina) e NUNCA Tabela de Luvas
        cax_fem = {
            "id": 8424114192450,
            "sku": "CAX050BL",
            "title": "Camisa ArmorX Feminina Brk Pescaiaque Chumbo com Listra Amarela e Luva Proteção UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/cax050bl_1.jpg"],
        }
        enr_cax = template_engine.generate_narrative_from_template(cax_fem, "uv_performance", cax_fem["images"], store_key="brk_fishing")
        html_cax = html_builder.build_shopify_html(enr_cax)
        self.assertIn("Tabela de Medidas Feminina - Baby Look (PP ao G2)", html_cax)
        self.assertNotIn("Tabela de Medidas de Luvas", html_cax)

        # Caso 5: Kit Camisas Casal exibe ambas as tabelas (MASCULINO + FEMININO BABY LOOK)
        kit_casal = {
            "id": 9970013831463,
            "sku": "C0492PP_C0492BLPP",
            "title": "Kit Camisas UV50 Casal Bandeira do Brasil",
            "images": ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/kit_casal.webp"],
        }
        enr_casal = template_engine.generate_narrative_from_template(kit_casal, "uv_performance", kit_casal["images"], store_key="brk_motors")
        html_casal = html_builder.build_shopify_html(enr_casal)
        self.assertIn("Tabela de Medidas Kit Casal - Masculino & Feminino Baby Look (PP ao G2)", html_casal)
        self.assertIn("MASCULINO", html_casal)
        self.assertIn("FEMININO (BABY LOOK)", html_casal)

        # Caso 6: Camisa Feminina "Casal de Araras" (estampa) recebe apenas Tabela Feminina Baby Look
        araras_fem = {
            "id": 80001,
            "sku": "C02493BL",
            "title": "Camisa Feminina Brk Amazon Casal de Araras com Proteção UV50",
            "images": ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/araras.jpg"],
        }
        enr_araras = template_engine.generate_narrative_from_template(araras_fem, "uv_performance", araras_fem["images"], store_key="brk_fishing")
        html_araras = html_builder.build_shopify_html(enr_araras)
        self.assertIn("Tabela de Medidas Feminina - Baby Look (PP ao G2)", html_araras)
        self.assertNotIn("Kit Casal", html_araras)

    def test_phase8_marine_knife_hooded_size_guide_and_guideline_filter(self):
        """
        Fase 8:
        1. Faca Marine Sports Fillet Knife MFK75T 19cm (SKU 79081379076) NÃO menciona bainha (destaca Revestimento Teflon & Olhal para Fiel).
        2. Camisas com Capuz / Bandana Embutida (FusionX / Hybrid) e Luva Integrada (ArmorX) trazem subtítulo específico e instrução explícita na Tabela de Medidas ("sem contar a altura do capuz e da bandana embutida").
        3. Avaliador de diretrizes (evaluate_guideline_compliance) filtra 100% os produtos conformes e sinaliza violações em MODO_B_DESATUALIZADO.
        """
        from api.product_db import evaluate_guideline_compliance
        template_engine = TemplateEngine()
        html_builder = HTMLBuilder()

        # 1. Faca Marine Sports Fillet Knife MFK75T 19cm — sem bainha
        faca_mfk = {
            "id": 8370981961794,
            "master_sku": "79081379076",
            "title": "Faca Marine Sports Fillet Knife MFK75T 19cm",
            "vendor": "MARINE SPORTS",
            "images": ["https://cdn.shopify.com/s/files/1/0628/1445/3826/files/Faca_de_file_marine_sports_teflon_7_5_19cm_mfk75t-1.webp"],
        }
        arch_mfk = template_engine.detect_archetype(faca_mfk["title"], "", [], faca_mfk["vendor"], sku=faca_mfk["master_sku"])
        self.assertEqual(arch_mfk, "cutlery_unique")
        enr_mfk = template_engine.generate_narrative_from_template(faca_mfk, arch_mfk, faca_mfk["images"], store_key="brk_fishing")
        html_mfk = html_builder.build_shopify_html(enr_mfk)
        self.assertNotIn("bainha", html_mfk.lower(), "Faca Marine MFK75T não acompanha bainha e jamais deve mencionar bainha!")
        self.assertIn("Revestimento Teflon & Olhal para Fiel", html_mfk)
        self.assertIn("Acabamento da Lâmina", html_mfk)

        # 2. FusionX — Tabela de Medidas com Capuz + Bandana Embutida + Dedeira
        fusion_p = {
            "id": 9183938609217,
            "master_sku": "FUSION197",
            "title": "Camisa FusionX Brk Pescaiaque Azul e Amarelo com Proteção UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/f197_1.jpg"],
        }
        enr_fus = template_engine.generate_narrative_from_template(fusion_p, "uv_performance", fusion_p["images"], store_key="brk_fishing")
        html_fus = html_builder.build_shopify_html(enr_fus)
        self.assertIn("Camisa UV50+ FusionX (Capuz + Bandana Embutida + Dedeira)", html_fus)
        self.assertIn("sem contar o capuz e a bandana/máscara facial embutida", html_fus)

        # 3. Hybrid — Tabela de Medidas com Capuz Anatômico + Punho com Dedeira
        hyb_p = {
            "id": 8417633534018,
            "master_sku": "HYB092",
            "title": "Camisa de Pesca Brk Hybrid Verde Musgo UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/hyb092_1.jpg"],
        }
        enr_hyb = template_engine.generate_narrative_from_template(hyb_p, "uv_performance", hyb_p["images"], store_key="brk_fishing")
        html_hyb = html_builder.build_shopify_html(enr_hyb)
        self.assertIn("Camisa UV50+ Hybrid (Capuz Anatômico + Punho com Dedeira)", html_hyb)
        self.assertIn("sem contar a altura do capuz integrado", html_hyb)

        # 4. ArmorX — Tabela de Medidas com Punho Estendido com Luva Integrada + Ato 3 específico
        cax_p = {
            "id": 8424112226370,
            "master_sku": "CAX050",
            "title": "Camisa ArmorX Brk Pescaiaque Chumbo com Listra Amarela e Luva Proteção UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/cax050_1.jpg",
                "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/cax050_2.jpg",
                "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/cax050_3.jpg",
            ],
        }
        enr_cax2 = template_engine.generate_narrative_from_template(cax_p, "uv_performance", cax_p["images"], store_key="brk_fishing")
        html_cax2 = html_builder.build_shopify_html(enr_cax2)
        self.assertIn("Camisa UV50+ ArmorX (Punho Estendido com Luva Integrada)", html_cax2)
        self.assertIn("PUNHOS ESTENDIDOS COM LUVA INTEGRADA E COSTURAS REFORÇADAS", html_cax2)
        self.assertNotIn("Tabela de Medidas de Luvas", html_cax2)

        # 5. Avaliador de conformidade (evaluate_guideline_compliance)
        faca_mfk["body_html"] = html_mfk
        faca_mfk["status"] = "SAUDAVEL"
        is_comp_ok, g_stat_ok, _ = evaluate_guideline_compliance(faca_mfk, "brk_fishing")
        self.assertTrue(is_comp_ok)
        self.assertEqual(g_stat_ok, "CONFORME_MODO_B")

        faca_mfk_bad = dict(faca_mfk, body_html=html_mfk + "<p>Acompanha bainha rígida</p>")
        is_comp_bad, g_stat_bad, g_reason_bad = evaluate_guideline_compliance(faca_mfk_bad, "brk_fishing")
        self.assertFalse(is_comp_bad)
        self.assertEqual(g_stat_bad, "MODO_B_DESATUALIZADO")
        self.assertIn("bainha", g_reason_bad.lower())

        # 6. Card Infográfico Técnico c/ Giro 360° (Ato 1) e Lupa Óptica 2.4x (Atos 2 e 3) sem selos no topo e ZERO duplicação
        fusion_3imgs = {
            "id": 9183938609999,
            "master_sku": "FUSION159BL",
            "title": "Camisa Feminina FusionX Brk Capivara Rosa com Proteção UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/f159_1.jpg",
                "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/f159_2.jpg",
                "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/f159_3.jpg",
                "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/f159_4.jpg",
            ],
        }
        enr_f159 = template_engine.generate_narrative_from_template(fusion_3imgs, "uv_performance", fusion_3imgs["images"], store_key="brk_fishing")
        html_f159 = html_builder.build_shopify_html(enr_f159)
        self.assertIn("brk-media-card", html_f159)
        self.assertIn("brk-media-infobar", html_f159)
        self.assertIn("brk-card-360", html_f159)
        self.assertIn("brk-360-rotator", html_f159)
        self.assertIn("180° Costas", html_f159)
        self.assertIn("brk-loupe-lens", html_f159)
        self.assertIn("Lupa 2.4x", html_f159)
        self.assertIn("Foco Frontal: Capuz, Máscara Facial & Dedeira", html_f159)
        self.assertNotIn("brk-media-view-pill", html_f159, "Nomenclaturas do topo das 3 imagens devem ser removidas!")
        self.assertNotIn("ZOOM DE ACABAMENTO • ATO 03", html_f159)

        # 7. Mapeamento de Capa Humanizada de Costas (ex: C02894BL) vs. Capa Humanizada de Frente (ex: FUSION53) com ZERO fotos duplicadas
        c02894bl = {
            "id": 9974611804487,
            "master_sku": "C02894BL",
            "title": "Camisa Feminina Brk Motors Freddy It's Closer Com Proteção Solar UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/c1bd5af8-660e-442e-8fa6-8aa10be287bd.png?v=1776186801",
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/246708f34b714adb975e4f56237d4841_2FproductOnChannel_2Fimages_2F187989328_2F7b43fa894fa84b36afce86cf504eb5e1.jpg?v=1774011343",
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/246708f34b714adb975e4f56237d4841_2FproductOnChannel_2Fimages_2F187989328_2Fdca252fa584e4376901980d0e004f87b.jpg?v=1774011346",
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/246708f34b714adb975e4f56237d4841_2FproductOnChannel_2Fimages_2F187989328_2F4f88725a70334433bfeb288acde54b2c.jpg?v=1774011348",
            ],
        }
        enr_2894 = template_engine.generate_narrative_from_template(c02894bl, "uv_performance", c02894bl["images"], store_key="brk_motors")
        html_2894 = html_builder.build_shopify_html(enr_2894)
        self.assertTrue(enr_2894["act1"]["is_back_cover_360"])
        self.assertIn("c1bd5af8", enr_2894["act1"]["image"])
        self.assertIn("7b43fa89", enr_2894["act1"]["back_360_image"])
        self.assertIn("dca252fa", enr_2894["act2"]["image"])
        self.assertIn("4f88725a", enr_2894["act3"]["image"])
        self.assertIn('class="brk-360-btn brk-360-b1">180° Costas</label>', html_2894)
        self.assertIn('class="brk-360-btn brk-360-b2">0° Frente</label>', html_2894)
        srcs_2894 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_2894, re.I)
        bgs_2894 = re.findall(r'brk-360-back["\'][^>]*style=["\'][^"\']*url\(["\']?([^"\'\)]+)["\']?\)', html_2894, re.I)
        all_4_2894 = [u.split("?")[0] for u in (srcs_2894 + bgs_2894)]
        self.assertEqual(len(all_4_2894), 4)
        self.assertEqual(len(set(all_4_2894)), 4, "As 4 fotos visuais (Ato 1 Face 1, Ato 1 Face 2, Ato 2 e Ato 3) devem ser 100% distintas!")

        # 8. Camisas com Capa Humanizada de Costas e apenas 1 Frente + 2 Costas (ex: C02895): Close-up Lateral em Mangas/Punhos no Ato 3
        c02895 = {
            "id": 9974610952519,
            "master_sku": "C02895",
            "title": "BRK Camisa Halloween Freddy Ride Or Die Com Proteção Solar UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/a588a417-2055-4337-aa46-5738eb7cf201.png?v=1776186259",
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/246708f34b714adb975e4f56237d4841_2FproductOnChannel_2Fimages_2F187989331_2Fc2e7849ff97e46c2a8dc9652315f3fc4.jpg?v=1774011350",
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/246708f34b714adb975e4f56237d4841_2FproductOnChannel_2Fimages_2F187989331_2F59c6e4c0949c4b00bf3c8ba658c588e1.jpg?v=1774011353",
                "https://cdn.shopify.com/s/files/1/0920/4799/9271/files/246708f34b714adb975e4f56237d4841_2FproductOnChannel_2Fimages_2F187989331_2F9170d7b1e7b84122a406150ec0250427.jpg?v=1774011355",
            ],
        }
        enr_2895 = template_engine.generate_narrative_from_template(c02895, "uv_performance", c02895["images"], store_key="brk_motors")
        html_2895 = html_builder.build_shopify_html(enr_2895)
        self.assertTrue(enr_2895["act3"].get("crop_sleeve_detail"))
        self.assertIn("brk-crop-sleeve-detail", html_2895)
        self.assertIn("Detalhe Lateral: Mangas, Punhos & Costura", html_2895)
        self.assertIn("MANGAS ANATÔMICAS, PUNHOS FIRMES E COSTURAS PLANAS ANTI-ATRITO", html_2895)
        self.assertNotIn("Foco Frontal:", html_2895)

        # 9. Kits Multi-Produtos (Camisa + Botina em Couro Legítimo): Tema Verde Agro, Ato 1 Camisa, Ato 2 Botina e Guia de Medidas Duplo
        kit_agro = {
            "id": 15412614168873,
            "sku": "15412614168873",
            "title": "Kit Camisa Agro Brk Camuflada Bandeira do Brasil + Botina Couro Legítimo Chocolate",
            "images": [
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/C02546_1.png?v=1761233389",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/botina-couro-legitimo-chocolate-1.jpg?v=1761233391",
            ],
        }
        arch_kit = template_engine.detect_archetype(kit_agro["title"], "", [], "BRK", sku=kit_agro["sku"])
        self.assertEqual(arch_kit, "uv_performance")
        enr_kit = template_engine.generate_narrative_from_template(kit_agro, arch_kit, kit_agro["images"])
        self.assertEqual(enr_kit["store_key"], "brk_agro")
        self.assertEqual(enr_kit["theme_color"], "#16a34a")
        html_kit = html_builder.build_shopify_html(enr_kit)
        self.assertIn("Item 01 do Kit: Camisa Técnica BRK UV50+", html_kit)
        self.assertIn("Item 02 do Kit: Botina em Couro Bovino Legítimo", html_kit)
        self.assertIn("BOTINA EM COURO BOVINO LEGÍTIMO COM SOLADO ANTIDERRAPANTE E CALCE FÁCIL", html_kit)
        self.assertIn("ITEM 01 — TABELA DE MEDIDAS DA CAMISA (PP AO G2)", html_kit)
        self.assertIn("ITEM 02 — GUIA DE TAMANHOS DA BOTINA / CALÇADO (34 AO 45)", html_kit)
        self.assertIn("Kit Completo 2 em 1", html_kit)
        self.assertNotIn("durante os a ", html_kit.lower())

        # 10. Varredura Global das 3 Lojas: Xadrez Sublimado UV50+ (C0/CI), Camisetas Manga Curta sem punhos, Sonho de Criança adulto, Algodão Sombreado UV50+ e Selos Especializados
        c_xadrez_uv = {
            "id": 99001,
            "master_sku": "C0923",
            "title": "Camisa Country Brk Xadrez Verde com Proteção Solar UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0887/2083/4857/files/C0923_1.jpg"],
        }
        arch_xadrez = template_engine.detect_archetype(c_xadrez_uv["title"], "", [], "BRK", sku=c_xadrez_uv["master_sku"])
        self.assertEqual(arch_xadrez, "uv_performance")

        camiseta_mc = {
            "id": 99002,
            "master_sku": "CASUAL436",
            "title": "Camiseta de Pesca Brk Brasil Independência Azul com com Proteção Solar UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0612/8068/2177/files/CASUAL436_1.jpg"],
        }
        arch_mc = template_engine.detect_archetype(camiseta_mc["title"], "", [], "BRK", sku=camiseta_mc["master_sku"])
        enr_mc = template_engine.generate_narrative_from_template(camiseta_mc, arch_mc, camiseta_mc["images"], store_key="brk_fishing")
        html_mc = html_builder.build_shopify_html(enr_mc)
        self.assertNotIn("com com", html_mc.lower())
        self.assertNotIn("punho", html_mc.lower())
        self.assertNotIn("punhos", html_mc.lower())
        self.assertIn("Manga do ombro à barra da manga curta", html_mc)

        sonho_crianca_adulto = {
            "id": 99003,
            "master_sku": "C01684",
            "title": "Camisa Agro Brk Carreta Sonho de Criança com Proteção Solar UV50+",
            "images": ["https://cdn.shopify.com/s/files/1/0887/2083/4857/files/C01684_1.jpg"],
        }
        enr_sc = template_engine.generate_narrative_from_template(sonho_crianca_adulto, "uv_performance", sonho_crianca_adulto["images"], store_key="brk_agro")
        html_sc = html_builder.build_shopify_html(enr_sc)
        self.assertFalse(enr_sc["is_kids"])
        self.assertNotIn("Guia de Tamanhos Infantil (1 a 13 Anos)", html_sc)
        self.assertIn("Tabela de Medidas Masculino / Unissex (PP ao G2)", html_sc)
        self.assertIn('<div class="brk-sg-card-title">MASCULINO</div>', html_sc)

        algodao_sombreado_uv = {
            "id": 99004,
            "master_sku": "C02724",
            "title": "Camisa Agro BRK Força do Agro Algodão Sombreado com Proteção UV50+ Preta",
            "images": [
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/C02724_1.jpg",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/C02724_2.jpg",
            ],
        }
        enr_as = template_engine.generate_narrative_from_template(algodao_sombreado_uv, "uv_performance", algodao_sombreado_uv["images"], store_key="brk_agro")
        html_as = html_builder.build_shopify_html(enr_as)
        self.assertNotIn("Malha 100% Algodão", html_as)
        self.assertIn("Painel Dorsal & Tecido Tecnológico UV50+", html_as)

        geladeira_motors = {
            "id": 99005,
            "master_sku": "BL35",
            "title": "Geladeira Portátil Elber 35 Litros 12V/24V BL35",
            "images": ["https://cdn.shopify.com/s/files/1/0920/4799/9271/files/BL35_1.jpg"],
        }
        enr_gel = template_engine.generate_narrative_from_template(geladeira_motors, "drinkware_thermo", geladeira_motors["images"], store_key="brk_motors")
        html_gel = html_builder.build_shopify_html(enr_gel)
        self.assertIn("Compressor 12V/24V", html_gel)
        self.assertNotIn("Inox 18/8 com Vácuo", html_gel)
        self.assertNotIn("pescarias", html_gel.lower())

        # 11. Produtos de Revenda / Únicos sem frente-e-costas (ex: Faca Artesanal Gaúcha Cutelaria D'Avila): sem botão 180° Giro 3D e com selo Revenda
        faca_davila = {
            "id": 99006,
            "master_sku": "CARBONO",
            "title": 'Faca Artesanal Gaúcha Churrasco Aço Carbono 12" Cabo Hibrido',
            "images": [
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/faca-artesanal-gaucha-churrasco-aco-carbono-12-cabo-hibrido-carbono23-faca-artesanal-7908456420584-brk-agro-default-title-41251635626281.png?v=1787681134",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/faca-artesanal-gaucha-churrasco-aco-carbono-12-cabo-hibrido-carbono23-faca-artesanal-7908456420584-brk-agro-default-title-41251635659049.png?v=1787680936",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/faca-artesanal-gaucha-churrasco-aco-carbono-12-cabo-hibrido-carbono23-faca-artesanal-7908456420584-brk-agro-default-title-41251635691817.png?v=1787681325",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/nqWudRJ.png?v=1741789942",
            ],
        }
        arch_davila = template_engine.detect_archetype(faca_davila["title"], "", [], "", sku=faca_davila["master_sku"])
        enr_davila = template_engine.generate_narrative_from_template(faca_davila, arch_davila, faca_davila["images"], store_key="brk_agro")
        html_davila = html_builder.build_shopify_html(enr_davila)
        self.assertEqual(enr_davila["origin_type"], "revenda")
        self.assertEqual(enr_davila["brand_name"], "Cutelaria D'Avila")
        self.assertEqual(enr_davila["act1"].get("back_360_image", ""), "")
        self.assertNotIn("brk-card-360", html_davila)
        self.assertNotIn("180° Giro 3D", html_davila)
        self.assertNotIn("BRK Faca Artesanal", html_davila)
        self.assertNotIn("41251635691817", html_davila, "O banner de pergaminho com texto ([2]) nunca deve ser exibido!")

    def test_phase10_humanized_hands_glove_and_model_mapping(self):
        """
        Fase 10:
        1. Camisas ArmorX (CAX039BL, CAX038, CAX005) com foto humanizada de mãos/dedeira posicionam a foto de mãos exclusivamente no Ato 3, costas no Giro 360° e Ato 2, e usam título/infobar focados 100% no furo anatômico do polegar (sem mencionar 'Gola' na legenda do Ato 3).
        2. Coleção Apache Agro (C02841 e C02833BL) aloca corretamente 0° Frente, 180° Costas e foto humanizada de modelo.
        3. Bandanas Amazon (T660) alocam 3D no Ato 2 e foto humanizada em uso real no Ato 3.
        """
        template_engine = TemplateEngine()
        html_builder = HTMLBuilder()

        cax039bl = {
            "id": 8500001,
            "master_sku": "CAX039BL",
            "title": "Camisa ArmorX Feminina Degradê Azul Marinho com Proteção UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1723039660484-01FEM_942466ab-93d4-46da-bc6f-94643f594695.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/https___s3.amazonaws.com_appforest_uf_f1623699781775x777656534115487200_productOnChannel_2Fimages_2F9574074_2F44c44e9612c4-54cc-422c-b19b-3bd83c72b8b3.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1723039667628-02FEM_e6d735b0-3803-45d2-b89f-73eb2bb6a1be.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1723039675365-03FEM_64e7833a-a47d-4dc7-b849-410fb67fc1c0.jpg",
            ],
        }
        enr_39 = template_engine.generate_narrative_from_template(cax039bl, "uv_performance", cax039bl["images"], store_key="brk_fishing")
        html_39 = html_builder.build_shopify_html(enr_39)
        self.assertIn("01FEM", enr_39["act1"]["image"])
        self.assertIn("02FEM", enr_39["act1"]["back_360_image"])
        self.assertIn("03FEM", enr_39["act2"]["image"])
        self.assertIn("44c44e9612c4", enr_39["act3"]["image"])
        self.assertIn("PUNHOS ALONGADOS COM ABERTURA ANATÔMICA PARA O POLEGAR (LUVA INTEGRADA)", html_39)
        self.assertIn("Detalhe Humanizado: Furo Anatômico p/ Polegar", html_39)
        self.assertNotIn("Foco Frontal: Punho c/ Luva Integrada & Gola", html_39)

        cax038 = {
            "id": 8500002,
            "master_sku": "CAX038",
            "title": "Camisa ArmorX Masculina Degradê Azul Royal com Proteção UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1722959656648-01MASC.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cax38.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1722959661717-02MASC.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/1722959667456-03MASC.jpg",
            ],
        }
        enr_38 = template_engine.generate_narrative_from_template(cax038, "uv_performance", cax038["images"], store_key="brk_fishing")
        self.assertIn("01MASC", enr_38["act1"]["image"])
        self.assertIn("02MASC", enr_38["act1"]["back_360_image"])
        self.assertIn("03MASC", enr_38["act2"]["image"])
        self.assertIn("cax38.jpg", enr_38["act3"]["image"])

        c02833bl = {
            "id": 8500003,
            "master_sku": "C02833BL",
            "title": "Camisa Agro Feminina BRK Cavalos Apache com Proteção UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/C02833BL.webp",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/1739300001-01FEM.png",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/1739300002-02FEM.png",
                "https://cdn.shopify.com/s/files/1/0887/2083/4857/files/1739300003-03FEM.png",
            ],
        }
        enr_apache = template_engine.generate_narrative_from_template(c02833bl, "uv_performance", c02833bl["images"], store_key="brk_agro")
        self.assertIn("03FEM", enr_apache["act1"]["image"])
        self.assertIn("02FEM", enr_apache["act3"]["image"])

        t660 = {
            "id": 8500004,
            "master_sku": "T660",
            "title": "Bandana Tubular BRK Amazon Tucunaré com Proteção UV50+",
            "images": [
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/t660_1.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/t660_modelo.jpg",
                "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/t660_3d.jpg",
            ],
        }
        enr_t660 = template_engine.generate_narrative_from_template(t660, "neck_gaiters_balaclavas", t660["images"], store_key="brk_fishing")
        html_t660 = html_builder.build_shopify_html(enr_t660)
        self.assertIn("t660_3d.jpg", enr_t660["act2"]["image"])
        self.assertIn("t660_modelo.jpg", enr_t660["act3"]["image"])
        self.assertIn("Ajuste Anatômico no Rosto & Pescoço em Uso Real", html_t660)


def run_tests():
    suite = unittest.TestSuite()
    for case in (TestBRKRegressionGuardrails, TestSemanticConformity, TestLiveAgentAndTracking, TestTampermonkeyIntegration, TestProductDBApiAndDirectConnection, TestDeepFlowAuditGuardrails, TestBRKStudioVerticalization):
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(case))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
