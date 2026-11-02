"""Pôsteres de filmes e séries e capas de livros para os lotes JSON da revista.

uso: python3 -I capas_obras.py <pasta_saida> <lote.json> [<lote.json> ...]
Cada lote: {"itens": [...], "guias": [{"filmes"|"livros": [...]}]}. Grava <slug>.jpg e imprime OK/MISS por obra,
e anota a origem de cada imagem em <pasta_saida>/fontes.json.

Ordem das fontes, da mais confiável para a de reserva:
- Filmes e séries:
  1. TMDB, se houver chave (variável TMDB_API_KEY ou arquivo ~/.tmdb_key): busca pelo id do IMDb e, sem ele, por
     título e ano. Pôster em 500 px.
  2. Wikipedia pela API REST (/page/summary), uma chamada por título candidato, en e pt, aceitando só a página cujo
     texto cita o ano ou o sobrenome do diretor. User-Agent com contato, uma chamada por segundo, e espera o tempo
     pedido quando o servidor responde 429 (a API "action" da Wikipedia bloqueava o robô antigo).
  3. iTunes (filme ou temporada de série) com título e ano.
  4. Miniatura do trailer oficial no YouTube (campo trailer_url), como último recurso; a origem fica marcada.
- Livros:
  1. iTunes (e-book ou audiolivro) com título e sobrenome do autor.
  2. Open Library (busca por título e autor, capa em tamanho grande).
  3. Google Books (quando a cota sem chave deixar).
Um campo "capa_url" na obra, se existir, é usado antes de tudo.
"""
import json, os, re, subprocess, sys, time, unicodedata, urllib.parse

UA = "FaixaOculta/1.1 (revista pessoal; contato fabiomg@biof.ufrj.br)"
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
_ultimo = {}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def slug(s):
    return norm(s).replace(" ", "-")[:70]


def pausa(host, seg):
    t = time.time() - _ultimo.get(host, 0)
    if t < seg:
        time.sleep(seg - t)
    _ultimo[host] = time.time()


def get(url, seg=0.3, tentativas=4):
    """GET com User-Agent de contato, intervalo mínimo por host e respeito ao 429/Retry-After."""
    host = urllib.parse.urlparse(url).netloc
    for i in range(tentativas):
        pausa(host, seg)
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "20", "-A", UA, "-D", "-", url], capture_output=True)
        bruto = r.stdout.decode("utf-8", "replace")
        cab, _, corpo = bruto.rpartition("\r\n\r\n") if "\r\n\r\n" in bruto else ("", "", bruto)
        status = re.findall(r"HTTP/[\d.]+ (\d{3})", cab)
        st = int(status[-1]) if status else 0
        if st == 429 or st == 503:
            m = re.search(r"(?im)^retry-after:\s*(\d+)", cab)
            espera = min(int(m.group(1)) if m else 5 * (i + 1), 60)
            time.sleep(espera)
            continue
        return st, corpo
    return 429, ""


def get_json(url, seg=0.3):
    st, corpo = get(url, seg)
    try:
        return json.loads(corpo) if st == 200 else {}
    except Exception:
        return {}


def baixar(url, fn):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "30", "-A", UA, "-o", os.path.join(out, fn), "-w", "%{http_code} %{size_download} %{content_type}", url], capture_output=True)
    code, size, ctype = (r.stdout.decode().split(" ") + ["", "", ""])[:3]
    if code != "200" or int(float(size or 0)) < 4000 or "image" not in ctype:
        try:
            os.remove(os.path.join(out, fn))
        except OSError:
            pass
        return False
    return True


def titulos(a):
    ts = []
    for t in [a.get("titulo_original"), a.get("titulo")]:
        if t:
            for v in (t, re.split(r"\s[–—-]\s|:\s", t)[0]):
                if v and v not in ts:
                    ts.append(v)
    return ts


def ano(a):
    m = re.search(r"\d{4}", str(a.get("ano", "")))
    return m.group(0) if m else ""


def sobrenomes(a):
    nomes = re.split(r",| e |;|\(|\)", str(a.get("autor", "")))
    return [norm(n).split(" ")[-1] for n in nomes if norm(n)]


# ---------- filmes e séries ----------
def tmdb_chave():
    k = os.environ.get("TMDB_API_KEY", "").strip()
    if not k and os.path.exists(os.path.expanduser("~/.tmdb_key")):
        k = open(os.path.expanduser("~/.tmdb_key")).read().strip()
    return k


def tmdb(a):
    k = tmdb_chave()
    if not k:
        return None, None
    base = "https://api.themoviedb.org/3"
    auth = ("api_key=" + k) if len(k) < 40 else None
    def q(path, params):
        params = dict(params)
        if auth:
            params["api_key"] = k
        url = f"{base}{path}?{urllib.parse.urlencode(params)}"
        if auth:
            return get_json(url)
        r = subprocess.run(["curl", "-s", "--max-time", "20", "-H", f"Authorization: Bearer {k}", url], capture_output=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            return {}
    serie = a.get("tipo") == "serie"
    imdb = str(a.get("imdb", ""))
    if re.match(r"^tt\d+$", imdb):
        res = q(f"/find/{imdb}", {"external_source": "imdb_id", "language": "pt-BR"})
        for chave in ("tv_results", "movie_results") if serie else ("movie_results", "tv_results"):
            for r in res.get(chave, []):
                if r.get("poster_path"):
                    return f"https://image.tmdb.org/t/p/w500{r['poster_path']}", f"tmdb:{imdb}"
    for t in titulos(a):
        params = {"query": t, "language": "pt-BR"}
        if ano(a):
            params["first_air_date_year" if serie else "year"] = ano(a)
        res = q("/search/tv" if serie else "/search/movie", params)
        for r in res.get("results", [])[:3]:
            nome = norm(r.get("title") or r.get("name") or "") + " " + norm(r.get("original_title") or r.get("original_name") or "")
            if norm(t) in nome and r.get("poster_path"):
                return f"https://image.tmdb.org/t/p/w500{r['poster_path']}", f"tmdb:{r.get('id')}"
    return None, None


def wiki(a):
    serie = a.get("tipo") == "serie"
    y = ano(a)
    provas = [y] + sobrenomes(a)
    cands = []
    for t in titulos(a):
        en = [f"{t} ({y} film)", f"{t} (film)", f"{t} ({y} TV series)", f"{t} (TV series)", f"{t} (miniseries)", t] if not serie else \
             [f"{t} ({y} TV series)", f"{t} (TV series)", f"{t} (miniseries)", t]
        pt = [f"{t} (filme)", f"{t} ({y})", f"{t} (série)", f"{t} (minissérie)", t]
        cands += [("en", x) for x in en] + [("pt", x) for x in pt]
    vistos = set()
    for lang, t in cands:
        if (lang, t) in vistos:
            continue
        vistos.add((lang, t))
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(t.replace(" ", "_"), safe="")
        j = get_json(url, seg=1.0)
        if not j or j.get("type") == "disambiguation":
            continue
        texto = norm(" ".join([j.get("description", ""), j.get("extract", "")]))
        if not any(p and p in texto for p in provas):
            continue
        img = (j.get("originalimage") or j.get("thumbnail") or {}).get("source")
        if img and not re.search(r"\.svg", img, re.I):
            if "thumbnail" in j and j["thumbnail"].get("source"):
                img = re.sub(r"/\d+px-", "/500px-", j["thumbnail"]["source"]) if "/thumb/" in j["thumbnail"]["source"] else img
            return img, f"wikipedia-{lang}:{j.get('title')}"
    return None, None


def itunes(a, entities):
    ts = [t for t in [a.get("titulo"), a.get("titulo_original")] if t]
    sob = sobrenomes(a)
    for entity in entities:
        for country in ("br", "us"):
            for t in ts:
                term = f"{t} {a.get('autor', '')}" if entity in ("ebook", "audiobook") else t
                res = get_json("https://itunes.apple.com/search?" + urllib.parse.urlencode({"term": term, "entity": entity, "limit": 15, "country": country}))
                for r in res.get("results", []):
                    name = norm(r.get("trackName") or r.get("collectionName") or "")
                    if not (norm(t) and (norm(t) in name or name in norm(t))):
                        continue
                    if entity in ("ebook", "audiobook") and sob and not any(s in norm(r.get("artistName", "")) for s in sob):
                        continue
                    if entity == "movie" and ano(a) and ano(a) not in str(r.get("releaseDate", ""))[:4]:
                        continue
                    art = r.get("artworkUrl100", "")
                    if art:
                        return art.replace("100x100bb", "600x600bb"), f"itunes:{r.get('trackName') or r.get('collectionName')}"
    return None, None


def trailer(a):
    m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", str(a.get("trailer_url", "")))
    if not m:
        return None, None
    for q in ("maxresdefault", "hqdefault"):
        url = f"https://i.ytimg.com/vi/{m.group(1)}/{q}.jpg"
        st, _ = get(url)
        if st == 200:
            return url, f"trailer:{m.group(1)}"
    return None, None


# ---------- livros ----------
def openlibrary(a):
    sob = sobrenomes(a)
    for t in titulos(a):
        res = get_json("https://openlibrary.org/search.json?" + urllib.parse.urlencode({"title": t, "author": a.get("autor", ""), "limit": 5, "fields": "title,author_name,cover_i"}), seg=1.0)
        for d in res.get("docs", []):
            if not d.get("cover_i") or norm(t) not in norm(d.get("title", "")):
                continue
            if sob and not any(s in norm(" ".join(d.get("author_name", []))) for s in sob):
                continue
            return f"https://covers.openlibrary.org/b/id/{d['cover_i']}-L.jpg", f"openlibrary:{d['cover_i']}"
    return None, None


def googlebooks(a):
    sob = sobrenomes(a)
    for t in titulos(a):
        res = get_json("https://www.googleapis.com/books/v1/volumes?" + urllib.parse.urlencode({"q": f'intitle:"{t}" {a.get("autor", "")}', "maxResults": 5}), seg=1.0)
        for v in res.get("items", []):
            info = v.get("volumeInfo", {})
            if norm(t) not in norm(info.get("title", "")):
                continue
            if sob and not any(s in norm(" ".join(info.get("authors", []))) for s in sob):
                continue
            img = (info.get("imageLinks") or {}).get("thumbnail")
            if img:
                return img.replace("http://", "https://").replace("&edge=curl", "").replace("zoom=1", "zoom=2"), f"googlebooks:{v.get('id')}"
    return None, None


FILME = [tmdb, wiki, lambda a: itunes(a, ["movie", "tvSeason"]), trailer]
LIVRO = [lambda a: itunes(a, ["ebook", "audiobook"]), openlibrary, googlebooks]

obras = []
for b in sys.argv[2:]:
    j = json.load(open(b))
    obras += j.get("itens", [])
    for g in j.get("guias", []):
        obras += g.get("filmes", []) + g.get("livros", [])

fontes_fn = os.path.join(out, "fontes.json")
fontes = json.load(open(fontes_fn)) if os.path.exists(fontes_fn) else {}
vistos = set()
for a in obras:
    fn = slug(f"{a.get('titulo')} {a.get('ano', '')}") + ".jpg"
    if fn in vistos:
        continue
    vistos.add(fn)
    if os.path.exists(os.path.join(out, fn)):
        print("HAVE", fn)
        continue
    livro = a.get("tipo") in ("ficcao", "contos", "nao_ficcao")
    ok = False
    tentativas = ([lambda a: (a.get("capa_url"), "capa_url")] if a.get("capa_url") else []) + (LIVRO if livro else FILME)
    for busca in tentativas:
        url, fonte = busca(a)
        if url and baixar(url, fn):
            fontes[fn] = fonte
            json.dump(fontes, open(fontes_fn, "w"), ensure_ascii=False, indent=1)
            print("OK  ", fn, "<=", fonte, flush=True)
            ok = True
            break
    if not ok:
        print("MISS", fn, "|", a.get("titulo"), "|", a.get("autor"), flush=True)
json.dump(fontes, open(fontes_fn, "w"), ensure_ascii=False, indent=1)
