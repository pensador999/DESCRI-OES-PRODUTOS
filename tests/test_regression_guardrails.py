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
        old = html.replace("BRK-MODO-B v1", "BRK-MODO-B v0", 1)
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
        self.assertIn("1764962764537-CAIXA-BRK.webp", html_bone)

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
