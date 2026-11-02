"""Instala a chave do TMDB que o leitor colou na revista, para capas_obras.py usar.

A página grava a chave em data/users/<uid>/segredos (claude.ai) ou em segredos.json no repositório privado
fabiomg-pixel/faixa-oculta-estado (site do GitHub). A rotina exporta um desses arquivos e roda:

    python3 -I tools/chave_tmdb.py <arquivo.json> [<outro.json> ...]

O script pega o primeiro {"tmdb": ...} válido, testa a chave na API do TMDB, grava em ~/.tmdb_key com permissão 600
e imprime só os quatro últimos caracteres. Nunca ponha a chave em commit, log, documento do banco ou relatório.
"""
import json, os, re, subprocess, sys


def ler(caminho):
    try:
        d = json.load(open(caminho, encoding="utf-8"))
    except Exception:
        return ""
    if isinstance(d.get("data"), dict):  # export do ArtifactData
        d = d["data"]
    k = str(d.get("tmdb", "")).strip()
    return k if re.fullmatch(r"[A-Za-z0-9._-]{20,400}", k) else ""


def testa(k):
    url = "https://api.themoviedb.org/3/configuration"
    if len(k) < 40:  # API Key (v3)
        cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", f"{url}?api_key={k}"]
    else:  # API Read Access Token (v4, Bearer)
        cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", "-H", f"Authorization: Bearer {k}", url]
    return subprocess.run(cmd, capture_output=True).stdout.decode().strip()


for caminho in sys.argv[1:]:
    k = ler(caminho)
    if not k:
        continue
    st = testa(k)
    if st != "200":
        print(f"chave encontrada em {os.path.basename(caminho)} (…{k[-4:]}), mas o TMDB respondeu {st}; não instalei")
        continue
    alvo = os.path.expanduser("~/.tmdb_key")
    fd = os.open(alvo, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(k)
    print(f"chave do TMDB instalada (…{k[-4:]}), testada com sucesso")
    sys.exit(0)
print("nenhuma chave do TMDB válida encontrada; capas_obras.py segue sem o TMDB")
sys.exit(1)
