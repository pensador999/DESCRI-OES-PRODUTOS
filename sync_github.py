"""
Script de Sincronizacao Continua com o Repositorio GitHub oficial.
Repositorio: https://github.com/pensador999/DESCRI-OES-PRODUTOS.git
Pasta do Projeto: C:\\Users\\lucas\\OneDrive\\Documentos\\DESCRIÇOES
"""

import os
import sys
import subprocess
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_PATH = r"C:\Users\lucas\OneDrive\Documentos\DESCRIÇOES"
REMOTE_URL = "https://github.com/pensador999/DESCRI-OES-PRODUTOS.git"

def run_cmd(cmd, cwd=REPO_PATH):
    try:
        res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def sync_to_github(custom_message=None):
    print("=" * 65)
    print("[SYNC] SINCRONIZADOR AUTOMATICO GITHUB - DESCRICOES BRK")
    print(f"Diretorio Local: {REPO_PATH}")
    print(f"Repositorio Remoto: {REMOTE_URL}")
    print("=" * 65)

    if not os.path.exists(REPO_PATH):
        print(f"[ERRO] Diretorio {REPO_PATH} nao encontrado!")
        return False

    # 1. Verificar se .git existe
    git_dir = os.path.join(REPO_PATH, ".git")
    if not os.path.exists(git_dir):
        print("[1/5] Inicializando repositorio Git local...")
        code, out, err = run_cmd("git init -b main")
        if code != 0:
            run_cmd("git init")
            run_cmd("git branch -M main")
        print("  -> Git inicializado com sucesso!")
    else:
        print("[1/5] Repositorio Git ja inicializado.")

    # 2. Configurar remote origin
    code, remotes, _ = run_cmd("git remote -v")
    if "origin" not in remotes:
        print("[2/5] Adicionando remote origin...")
        run_cmd(f'git remote add origin "{REMOTE_URL}"')
    else:
        # Garante que o origin está com a URL correta
        run_cmd(f'git remote set-url origin "{REMOTE_URL}"')
        print("[2/5] Remote origin verificado.")

    # 3. Adicionar arquivos (respeitando o .gitignore)
    print("[3/5] Adicionando arquivos modificados (git add -A)...")
    run_cmd("git add -A")

    # 4. Checar status
    code, status, _ = run_cmd("git status --porcelain")
    if not status:
        print("[4/5] Nenhuma alteracao pendente para commit.")
    else:
        print("[4/5] Criando commit...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = custom_message or f"feat(catalog): atualizacao automatica das descricoes [{timestamp}]"
        code, out, err = run_cmd(f'git commit -m "{commit_msg}"')
        if code == 0:
            print(f"  -> Commit realizado: {commit_msg}")
        else:
            print(f"  [AVISO] Commit output: {out or err}")

    # 5. Push para o GitHub
    print("[5/5] Enviando alteracoes para o GitHub (git push -u origin main)...")
    code, out, err = run_cmd("git push -u origin main")
    if code == 0:
        print("=" * 65)
        print("[SUCESSO] PROJETO SINCRONIZADO COM O GITHUB COM SUCESSO!")
        print(f"Link: {REMOTE_URL}")
        print("=" * 65)
        return True
    else:
        print(f"  [ERRO no Push]: {err or out}")
        # Tenta git push origin main caso upstream dê algum conflito
        code2, out2, err2 = run_cmd("git push origin main")
        if code2 == 0:
            print("[SUCESSO] Push concluido via fallback!")
            return True
        return False

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    sync_to_github(msg)
