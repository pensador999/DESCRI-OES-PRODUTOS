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
        ("brk_motors", "BRK Motors"),
        ("loja_doce", "Loja Doce (VTEX)")
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

def cmd_validate(args):
    """Agente Auditor de Conformidade Semântica: valida o Modo B de todo o catálogo"""
    from core.semantic_auditor import SemanticAuditor, load_store_products
    print("\n[🔎] Agente Auditor de Conformidade Semântica (Modo B)...")
    stores = ["brk_fishing", "brk_agro", "brk_motors", "loja_doce"] if args.store == "all" else [args.store]
    auditor = SemanticAuditor()
    all_findings = []
    tot_err = tot_warn = 0
    for sk in stores:
        prods = load_store_products(sk)
        if args.limit:
            prods = prods[:args.limit]
        r = auditor.audit_products(prods, sk)
        tot_err += r["errors"]
        tot_warn += r["warnings"]
        all_findings += r["findings"]
        print(f"  {sk:12}: {r['audited']:5d} auditados | ERROR={r['errors']} WARNING={r['warnings']}")
        for rule, n in sorted(r["by_rule"].items(), key=lambda kv: -kv[1]):
            print(f"      - {rule}: {n}")
    errs = [f for f in all_findings if f.get("severity") == "ERROR"]
    for f in errs[:10]:
        print(f"  ❌ [{f['rule']}] {f['title'][:70]} -> {f['evidence']}")
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    out = os.path.join(reports_dir, f"semantic_audit_{int(datetime.now().timestamp())}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(all_findings, fh, indent=1, ensure_ascii=False)
    print(f"\n  Total: ERROR={tot_err} WARNING={tot_warn} | Relatório: {out}")
    if tot_err or (args.strict and tot_warn):
        sys.exit(1)
    print("  ✅ Nenhuma violação crítica encontrada.")

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

def cmd_studio(args):
    """Executa o estúdio de fotos humanizadas (BRK Studio)"""
    from services.studio import persona_manager, studio_orchestrator
    from api.product_db import load_store_database

    if getattr(args, "list_personas", False):
        print("\n" + "=" * 65)
        print("  🎨 BRK STUDIO - CATÁLOGO DE PERSONAS & CENÁRIOS HUMANIZADOS")
        print("=" * 65)
        personas = persona_manager.all_personas()
        for p in personas:
            print(f"\n[{p.persona_id}] {p.name}")
            print(f"  Loja: {p.store_key} | Gênero: {p.gender}")
            print(f"  Cenário: {p.setting}")
            print(f"  Recomendado para: {', '.join(p.recommended_for)}")
        print("\n" + "=" * 65)
        return

    store_key = args.store
    sp = load_store_database(store_key)
    if not sp:
        print(f"[-] Erro: Loja '{store_key}' não encontrada.")
        return

    sku = (args.sku or "").strip()
    if not sku:
        print("[-] Erro: Informe o SKU do produto via --sku (ex: --sku C01005P) ou use --list-personas.")
        return

    product = sp["by_sku"].get(sku.upper()) or sp["by_sku"].get(sku)
    if not product:
        for s_key, p_obj in sp["by_sku"].items():
            if sku.upper() in s_key.upper():
                product = p_obj
                break

    if not product:
        print(f"[-] Erro: Produto com SKU '{sku}' não encontrado na loja {store_key}.")
        return

    print(f"\n[🎨 BRK Studio] Iniciando geração humanizada para:")
    print(f"  Produto : {product.get('title')}")
    print(f"  SKU     : {product.get('master_sku')}")
    print(f"  Loja    : {store_key}")
    print(f"  Provedor: {args.provider}")

    try:
        res = studio_orchestrator.generate_humanized_photo(
            product=product,
            store_key=store_key,
            persona_id=args.persona,
            provider=args.provider
        )
        print("\n" + "=" * 65)
        if res.get("success"):
            print("  ✅ SUCESSO NA GERAÇÃO HUMANIZADA!")
            print(f"  Provedor Utilizado : {res.get('provider')}")
            print(f"  Persona Aplicada   : {res.get('persona_id')}")
            if res.get("output_url"):
                print(f"  URL da Imagem      : {res.get('output_url')}")
            if res.get("local_path"):
                print(f"  Arquivo Salvo      : {res.get('local_path')}")
            if res.get("duration_seconds"):
                print(f"  Tempo de Processamento: {res.get('duration_seconds')}s")
        else:
            print(f"  ⚠️ Aviso: {res.get('error')}")
        print("=" * 65)
    except Exception as e:
        print(f"[-] Falha na execução do Studio: {e}")

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

    # Comando validate
    p_val = subparsers.add_parser("validate", help="Agente Auditor de Conformidade Semântica do Modo B")
    p_val.add_argument("--store", type=str, default="all", choices=["brk_fishing", "brk_agro", "brk_motors", "loja_doce", "all"], help="Loja alvo")
    p_val.add_argument("--limit", type=int, default=None, help="Limite de produtos por loja")
    p_val.add_argument("--strict", action="store_true", default=False, help="Falha também com WARNINGs")
    p_val.set_defaults(func=cmd_validate)

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

    # Comando studio (Fotos Humanizadas & Virtual Try-On)
    p_studio = subparsers.add_parser("studio", help="BRK Studio: Fotos Humanizadas e Virtual Try-On de alta conversão")
    p_studio.add_argument("--store", type=str, default="brk_fishing", choices=["brk_fishing", "brk_agro", "brk_motors"], help="Loja alvo")
    p_studio.add_argument("--sku", type=str, default=None, help="SKU do produto para gerar foto humanizada")
    p_studio.add_argument("--persona", type=str, default=None, help="ID da persona (opcional, ex: fishing_male_boat)")
    p_studio.add_argument("--provider", type=str, default="auto", choices=["auto", "replicate", "colab", "gemini", "dry_run"], help="Provedor de IA")
    p_studio.add_argument("--list-personas", action="store_true", default=False, help="Lista todas as personas e cenários cadastrados")
    p_studio.set_defaults(func=cmd_studio)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()
