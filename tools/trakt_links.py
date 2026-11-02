"""Link direto do Trakt para filmes e séries da revista, a partir do TMDB.

O app novo do Trakt (app.trakt.tv) não resolve mais /search/imdb/<id>; a página de cada título fica em
trakt.tv/movies/<slug> e trakt.tv/shows/<slug>. O slug é o título em inglês em minúsculas, com hífens no lugar
de espaços e pontuação; nos filmes, seguido do ano de lançamento. O script consulta o TMDB (chave em
~/.tmdb_key, instalada por chave_tmdb.py) pelo id do IMDb ou pelo título e ano, e grava o campo "trakt".

uso: python3 -I tools/trakt_links.py <pasta_dump> <saida.json>
Lê <dump>/cine_itens/*.json e <dump>/cine_guias/*.json; escreve {"cine_itens/<id>": {"trakt": url}, "cine_guias/<id>":
{"filmes": [...]}} só com o que mudou.
"""
import glob, json, os, re, subprocess, sys, unicodedata, urllib.parse

K = open(os.path.expanduser("~/.tmdb_key")).read().strip()


def tmdb(path, params):
    url = f"https://api.themoviedb.org/3{path}?" + urllib.parse.urlencode(params)
    cmd = ["curl", "-s", "--max-time", "20"]
    if len(K) < 40:
        url += "&api_key=" + K
    else:
        cmd += ["-H", f"Authorization: Bearer {K}"]
    try:
        return json.loads(subprocess.run(cmd + [url], capture_output=True).stdout)
    except Exception:
        return {}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"['’`]", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def ano(a):
    m = re.search(r"\d{4}", str(a.get("ano", "")))
    return m.group(0) if m else ""


def link(a):
    serie = a.get("tipo") == "serie"
    r = None
    imdb = str(a.get("imdb", ""))
    if re.fullmatch(r"tt\d+", imdb):
        res = tmdb(f"/find/{imdb}", {"external_source": "imdb_id", "language": "en-US"})
        lst = (res.get("tv_results") or []) if serie else (res.get("movie_results") or [])
        lst = lst or res.get("movie_results") or res.get("tv_results") or []
        r = lst[0] if lst else None
        if r:
            serie = "name" in r and "title" not in r
    if not r:
        for t in [a.get("titulo_original"), a.get("titulo")]:
            if not t:
                continue
            p = {"query": t, "language": "en-US"}
            if ano(a):
                p["first_air_date_year" if serie else "year"] = ano(a)
            res = tmdb("/search/tv" if serie else "/search/movie", p)
            if res.get("results"):
                r = res["results"][0]
                break
    if not r:
        return None
    if serie:
        return f"https://trakt.tv/shows/{slug(r.get('name') or r.get('original_name', ''))}"
    y = str(r.get("release_date", ""))[:4] or ano(a)
    return f"https://trakt.tv/movies/{slug(r.get('title') or r.get('original_title', ''))}-{y}"


dump, saida = sys.argv[1], sys.argv[2]
out = {}
L = lambda f: (lambda x: x["data"] if isinstance(x.get("data"), dict) else x)(json.load(open(f)))
for f in glob.glob(f"{dump}/cine_itens/*.json"):
    a = L(f)
    u = link(a)
    if u and u != a.get("trakt"):
        out[f"cine_itens/{os.path.basename(f)[:-5]}"] = {"trakt": u}
        print(a.get("titulo"), "->", u)
for f in glob.glob(f"{dump}/cine_guias/*.json"):
    g = L(f)
    mudou = False
    for a in g.get("filmes", []):
        u = link(a)
        if u and u != a.get("trakt"):
            a["trakt"] = u
            mudou = True
            print(a.get("titulo"), "->", u)
    if mudou:
        out[f"cine_guias/{os.path.basename(f)[:-5]}"] = {"filmes": g["filmes"]}
json.dump(out, open(saida, "w"), ensure_ascii=False, indent=1)
print(len(out), "documentos para atualizar")
