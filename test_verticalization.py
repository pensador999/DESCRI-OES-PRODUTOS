"""
Script de Teste de Validação dos 3 Pilares.
Testa:
1. HTMLReplacer (Modo A)
2. TemplateEngine e Extrator de Especificações (Pilar 2)
3. BatchMassGenerator e geração de CSV (Pilar 3)
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from core.html_replacer import HTMLReplacer
from core.template_engine import TemplateEngine
from core.batch_mass_generator import BatchMassGenerator

def test_all():
    print("[TESTE 1] Validando HTMLReplacer (Modo A)...")
    replacer = HTMLReplacer()
    dummy_broken_html = """
    <p>A melhor camisa de pesca esportiva do Brasil.</p>
    <p><img src="https://use-brk-images-s3.s3.us-east-1.amazonaws.com/armorx-detalhe.jpg" alt="Foto Quebrada"></p>
    <ul>
      <li>Tecido UV50+</li>
      <li>Zíper frontal</li>
    </ul>
    """
    sample_cdn = [
        "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/camisa-brk-oficial.jpg?v=1700000001",
        "https://cdn.shopify.com/s/files/1/0612/8068/2177/files/camisa-brk-costas.jpg?v=1700000002"
    ]
    replaced = replacer.replace_images_preserve_html(dummy_broken_html, sample_cdn, "Camisa ArmorX")
    assert "use-brk-images-s3" not in replaced, "Falha: Link morto da AWS ainda presente no HTML!"
    assert "cdn.shopify.com" in replaced, "Falha: Link oficial CDN Shopify não inserido!"
    assert "A melhor camisa de pesca esportiva" in replaced, "Falha: Texto original foi perdido!"
    print("  -> [OK] Modo A testado com sucesso! Links mortos eliminados e texto preservado.")

    print("\n[TESTE 2] Validando TemplateEngine & Moldes Mestres (Pilar 2)...")
    engine = TemplateEngine()
    
    # Teste de detecção de arquétipos
    assert engine.detect_archetype("Camisa de Pesca Dourado UV50+") == "uv_performance"
    assert engine.detect_archetype("Camiseta Agro Massey Ferguson Campo") == "agro_field"
    assert engine.detect_archetype("Jersey Motocross Trilha Off-Road") == "motors_speed"
    assert engine.detect_archetype("Boné Trucker Bordado Aba Curva") == "caps_accessories"
    assert engine.detect_archetype("Faca Artesanal Churrasco Aço 5160") == "cutlery_unique"
    print("  -> [OK] Todos os 5 arquétipos detectados com precisão!")

    # Teste de extração de especificações
    sample_prod = {
        "title": "Camisa Pesca Monster UV50+ Dry Fit",
        "body_html": "<p>Confeccionada em tecido Dry Fit com proteção FPU 50+ e zíper com trava.</p>",
        "tags": ["pesca", "uv50", "dry fit"]
    }
    narrative = engine.generate_narrative_from_template(sample_prod, "uv_performance", sample_cdn)
    assert len(narrative["narrative_blocks"]) == 3, "Falha: Deve ter exatamente 3 blocos narrativos!"
    specs = {s["label"]: s["value"] for s in narrative["specs"]}
    print("  -> Especificações extraídas:")
    for k, v in specs.items():
        print(f"     * {k}: {v}")
    assert "50+" in specs.get("Proteção Solar", ""), "Falha: Proteção solar não preservada!"
    assert "Dry Fit" in specs.get("Composição", ""), "Falha: Tecido Dry Fit não preservado!"
    print("  -> [OK] Moldes mestres e extração de dados técnicos validados!")

    print("\n[TESTE 3] Validando BatchMassGenerator (Pilar 3)...")
    generator = BatchMassGenerator()
    result = generator.process_store_mass(
        store_key="brk_fishing",
        catalog_data_path="reports/catalog_ui_data.json",
        output_dir="reports/test_batch",
        mode="mode_b_conversion",
        target_filter="broken_or_empty"
    )
    print(f"  -> Processados {result['total_processed']} produtos alvo em lote.")
    print(f"  -> CSV gerado em: {result['csv_path']}")
    assert result["total_processed"] > 0, "Falha: Nenhum produto processado no lote!"
    print("  -> [OK] Geração em massa por SKU e exportação de CSV validados com sucesso!")

    print("\n=== TODOS OS TESTES PASSARAM COM 100% DE SUCESSO! ===")

if __name__ == "__main__":
    test_all()
