"""
==============================================================================
CLI MESTRE UNIFICADO - CENTRAL DE OPERAÇÕES BRK SHOPIFY (cli.py)
==============================================================================
Ponto único de orquestração para auditoria, testes de regressão, compilação
modular e sincronização direta cirúrgica com a Shopify Admin API.

Comandos disponíveis:
  py -3.14 cli.py status       # Diagnóstico completo de tokens, catálogos e saúde
  py -3.14 cli.py test         # Executa a suíte de testes de regressão e guardrails
  py -3.14 cli.py audit        # Executa o Sentinela Diário de Catálogo (08:00)
  py -3.14 cli.py build        # Compila a distribuição modular otimizada para Vercel
  py -3.14 cli.py sync         # Sincronização direta com a Shopify (Dry-run ou Produção)

Exemplos de uso:
  py -3.14 cli.py sync --store brk_fishing --dry-run --limit 5
  py -3.14 cli.py sync --store brk_agro --production --limit 10
  py -3.14 cli.py sync --store all --dry-run
==============================================================================
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Assegurar UTF-8 no console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Adicionar raiz ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.config import STORES, load_env

# Carregar variáveis locais .env
load_env()

def cmd_status(args):
    """Exibe o diagnóstico geral do ecossistema, arquivos e tokens"""
    print("\n" + "=" * 65)
    print("  🚀 CENTRAL MESTRE BRK - DIAGNÓSTICO DO ECOSSISTEMA")
    print("=" * 65)

    # 1. Checagem de Tokens de Ambiente
    tokens = {
        "BRK Fishing": ("SHOPIFY_FISHING_TOKEN", os.getenv("SHOPIFY_FISHING_TOKEN")),
        "BRK Agro":    ("SHOPIFY_AGRO_TOKEN",    os.getenv("SHOPIFY_AGRO_TOKEN")),
        "BRK Motors":  ("SHOPIFY_MOTORS_TOKEN",  os.getenv("SHOPIFY_MOTORS_TOKEN"))
    }
    print("\n[🔑 Tokens de Acesso Shopify Admin API]")
    for store_name, (env_key, val) in tokens.items():
        if val and len(val) > 8:
            masked = val[:6] + "..." + val[-4:]
            print(f"  ✅ {store_name:12}: Configurado ({env_key} = {masked})")
        else:
            print(f"  ⚠️ {store_name:12}: Não configurado ({env_key}) -> Use .env ou flag --token")

    # 2. Catálogos e Produtos em data/stores/
    print("\n[📦 Catálogos Modulares (data/stores/)]")
    store_files = [
        ("brk_fishing", "BRK Fishing"),
        ("brk_agro", "BRK Agro"),
        ("brk_motors", "BRK Motors")
    ]
    total_products = 0
    for key, name in store_files:
        json_path = os.path.join(BASE_DIR, "data", "stores", f"{key}.json")
        js_path = os.path.join(BASE_DIR, "data", "stores", f"{key}.js")
        count = 0
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prods = data.get("products", []) if isinstance(data, dict) else data
                    count = len(prods)
                    total_products += count
            except Exception:
                pass
        
        status_ico = "✅" if count > 0 else "❌"
        size_mb = os.path.getsize(json_path) / (1024 * 1024) if os.path.exists(json_path) else 0.0
        print(f"  {status_ico} {name:12}: {count:5d} produtos ({size_mb:.1f} MB)")

    print(f"  👉 Total de Produtos Carregados: {total_products}")

    # 3. Histórico de Saúde do Sentinela
    print("\n[📊 Histórico de Saúde & Vigilante Diário]")
    hist_file = os.path.join(BASE_DIR, "reports", "historico_saude.json")
    if os.path.exists(hist_file):
        try:
            with open(hist_file, "r", encoding="utf-8") as f:
                hist = json.load(f)
            last_entry = hist[-1] if hist else {}
            last_time = last_entry.get("timestamp") or last_entry.get("date") or "N/A"
            total_corr = last_entry.get("total_corrections_ready", 0)
            print(f"  ✅ Última auditoria registrada: {last_time} ({total_corr} correções detectadas)")
            print(f"  ✅ Total de ciclos arquivados no histórico: {len(hist)}")
        except Exception as e:
            print(f"  ⚠️ Erro ao ler histórico: {e}")
    else:
        print("  ⚠️ Arquivo reports/historico_saude.json ainda não criado.")

    # 4. Planilhas Diárias Disponíveis
    fixes_dir = os.path.join(BASE_DIR, "reports", "daily_fixes")
    csvs = [f for f in os.listdir(fixes_dir) if f.endswith(".csv")] if os.path.exists(fixes_dir) else []
    print(f"\n[📁 Planilhas Diárias Segmentadas (reports/daily_fixes/)]: {len(csvs)} arquivo(s)")
    for c in sorted(csvs, reverse=True)[:3]:
        cpath = os.path.join(fixes_dir, c)
        csize = os.path.getsize(cpath) / 1024
        print(f"  📄 {c} ({csize:.1f} KB)")

    print("\n" + "=" * 65 + "\n")

def cmd_test(args):
    """Executa a suíte de testes de regressão e guardrails"""
    print("\n[🧪] Executando Suíte de Testes de Regressão e Guardrails...")
    from tests.test_regression_guardrails import run_tests
    success = run_tests()
    if not success:
        sys.exit(1)

def cmd_audit(args):
    """Executa o ciclo do Sentinela Diário"""
    print("\n[🛡️] Disparando Ciclo do Vigilante Diário (Sentinela)...")
    from core.daily_sentinel import DailySentinel
    sentinel = DailySentinel(base_dir=BASE_DIR)
    summary = sentinel.run_daily_cycle()
    print("\n[+] Ciclo do Vigilante Diário concluído com sucesso!")
    print(json.dumps(summary.get("stores_summary", {}), indent=2, ensure_ascii=False))

def cmd_build(args):
    """Compila a distribuição modular otimizada para a Vercel"""
    print("\n[🔨] Executando Compilação Modular Vercel v5.0...")
    from build_modular_dist import build_dist
    build_dist()

def cmd_sync(args):
    """Executa a sincronização direta com a Shopify"""
    from core.shopify_direct_sync import ShopifyDirectSync, STORE_DOMAINS

    is_dry_run = not args.production
    syncer = ShopifyDirectSync(dry_run=is_dry_run, delay=args.delay)

    stores_to_sync = list(STORE_DOMAINS.keys()) if args.store == "all" else [args.store]

    reports = []
    for s in stores_to_sync:
        report = syncer.sync_store(s, limit=args.limit, token_override=args.token)
        reports.append(report)

    # Salvar log
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file = os.path.join(reports_dir, f"sync_report_{int(datetime.now().timestamp())}.json")

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Relatório de sincronização salvo em: {report_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Central Mestre BRK - CLI Unificado de Operações Shopify",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ser executado")

    # Comando status
    p_status = subparsers.add_parser("status", help="Exibe o status geral de tokens, catálogos e saúde")
    p_status.set_defaults(func=cmd_status)

    # Comando test
    p_test = subparsers.add_parser("test", help="Executa os testes de regressão das Regras de Ouro")
    p_test.set_defaults(func=cmd_test)

    # Comando audit
    p_audit = subparsers.add_parser("audit", help="Executa o Sentinela Diário de catálogo")
    p_audit.set_defaults(func=cmd_audit)

    # Comando build
    p_build = subparsers.add_parser("build", help="Compila a distribuição modular otimizada para a Vercel")
    p_build.set_defaults(func=cmd_build)

    # Comando sync
    p_sync = subparsers.add_parser("sync", help="Sincroniza descrições diretamente com a Shopify Admin API")
    p_sync.add_argument("--store", type=str, default="brk_fishing", choices=["brk_fishing", "brk_agro", "brk_motors", "all"], help="Loja alvo")
    p_sync.add_argument("--dry-run", action="store_true", default=False, help="Executar em modo simulado (padrão)")
    p_sync.add_argument("--production", action="store_true", default=False, help="Executar em modo produção real com gravação")
    p_sync.add_argument("--limit", type=int, default=None, help="Limite máximo de produtos para atualizar")
    p_sync.add_argument("--delay", type=float, default=0.5, help="Intervalo em segundos entre requisições (padrão: 0.5s)")
    p_sync.add_argument("--token", type=str, default=None, help="Sobrescrever token de acesso da loja")
    p_sync.set_defaults(func=cmd_sync)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()
