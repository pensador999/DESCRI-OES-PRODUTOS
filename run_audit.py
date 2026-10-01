"""
Script Principal de Execução: Agente Auditor de Catálogo Shopify.
Executa a varredura, diagnóstico de links quebrados e classificação por arquétipos.
"""

import sys
import os
import argparse
import pandas as pd
from datetime import datetime

# Assegura suporte a UTF-8 no console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Garante que o diretório raiz esteja no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.shopify_public_api import ShopifyPublicAPI
from core.auditor import CatalogAuditor
from core.config import STORES

def run_catalog_audit(store_key: str = "brk", limit: int = 50, output_csv: str = None):
    print("=" * 70)
    print(f"[AGENTE] AUDITORIA SHOPIFY - INICIANDO ANALISE DE PRODUTOS")
    print(f"Loja Alvo: {STORES[store_key]['name']} ({STORES[store_key]['base_url']})")
    print(f"Limite de Produtos para Amostragem: {limit if limit else 'Catalogo Completo'}")
    print("=" * 70)

    # 1. Conexão com API Pública
    api = ShopifyPublicAPI(store_key=store_key)
    auditor = CatalogAuditor()

    # 2. Coleta de Produtos
    products = api.fetch_all_products(max_products=limit)
    if not products:
        print("[!] Nenhum produto retornado. Verifique a conexão com a loja.")
        return

    print(f"\n[*] Auditando {len(products)} produtos... (verificando links de imagens e conversão)")

    results = []
    for idx, prod in enumerate(products, 1):
        diag = auditor.audit_product(prod)
        results.append(diag)
        
        status_icons = {
            "SAUDAVEL": "[OK]",
            "IMAGENS_QUEBRADAS": "[ERRO_FOTO]",
            "BAIXA_CONVERSAO": "[ALERTA]",
            "SEM_DESCRICAO": "[VAZIO]"
        }
        icon = status_icons.get(diag["status"], "[INFO]")
        print(f"[{idx:03d}/{len(products):03d}] {icon:<11} Score: {diag['score']:02d} | [{diag['archetype']}] {diag['title'][:40]}... ({diag['status']})")

    # 3. Consolidação dos Resultados
    df = pd.DataFrame(results)
    
    total = len(df)
    broken_count = len(df[df["status"] == "IMAGENS_QUEBRADAS"])
    missing_count = len(df[df["status"] == "SEM_DESCRICAO"])
    low_conv_count = len(df[df["status"] == "BAIXA_CONVERSAO"])
    healthy_count = len(df[df["status"] == "SAUDAVEL"])

    print("\n" + "=" * 70)
    print("RESUMO DO DIAGNOSTICO DO CATALOGO")
    print("=" * 70)
    print(f"Total de Produtos Analisados: {total}")
    print(f"  [ERRO_FOTO] Com Imagens Quebradas / 404: {broken_count} ({broken_count/total*100:.1f}%)")
    print(f"  [VAZIO]     Sem Descricao Cadastrada:    {missing_count} ({missing_count/total*100:.1f}%)")
    print(f"  [ALERTA]    Baixa Conversao / Raso:      {low_conv_count} ({low_conv_count/total*100:.1f}%)")
    print(f"  [OK]        Descricoes Saudaveis:        {healthy_count} ({healthy_count/total*100:.1f}%)")
    print("-" * 70)
    print("Distribuição por Arquétipos:")
    archetype_counts = df["archetype"].value_counts().to_dict()
    for arch, count in archetype_counts.items():
        print(f" • {arch}: {count} produtos")
    print("=" * 70)

    # 4. Exportação do Relatório
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    if not output_csv:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_csv = os.path.join(reports_dir, f"auditoria_{store_key}_{timestamp}.csv")
    
    # Prepara dataframe para salvar
    df_export = df.copy()
    df_export["issues"] = df_export["issues"].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
    df_export["broken_urls"] = df_export["broken_urls"].apply(lambda x: " , ".join(x) if isinstance(x, list) else x)
    df_export.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[✓] Relatório detalhado salvo em: {output_csv}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auditor de Descrições Shopify")
    parser.add_argument("--site", default="brk", help="Identificador da loja em config.py (default: brk)")
    parser.add_argument("--limit", type=int, default=25, help="Quantidade de produtos para auditar (default: 25)")
    parser.add_argument("--export", type=str, default=None, help="Caminho do arquivo CSV de saída")
    args = parser.parse_args()

    run_catalog_audit(store_key=args.site, limit=args.limit, output_csv=args.export)
