"""Rastreio dos principais jornais internacionais para o quadro "Imprensa internacional" do boletim da manhã.

Uso:
  python3 -I tools/imprensa_mundo.py --data AAAA-MM-DD --saida DIR

Para cada jornal de JORNAIS abre a página inicial (curl simples, sem disfarce; página recusada é pulada) e lista,
em ordem de aparição, as chamadas com link (as primeiras costumam ser a manchete e os destaques do dia). Quando o
jornal tem capa impressa do dia no acervo público do Freedom Forum, guarda o endereço da imagem.

Grava DIR/mundo.json = [{"jornal","pais","idioma","site","capa_impressa","chamadas":[{"titulo","url"}]}]
e DIR/sem_acesso.json = [{"jornal","motivo"}]. As páginas baixadas ficam em DIR/html/ só para conferência; nada
disso é publicado. A rotina lê as chamadas, abre as matérias principais e escreve o quadro (ver tools/BOLETIM.md, 3c).
"""
import argparse, html, json, os, re, subprocess
from urllib.parse import urljoin, urlparse

# (nome, país, idioma, página inicial, código da capa impressa no Freedom Forum ou None)
JORNAIS = [
    ("The New York Times", "EUA", "en", "https://www.nytimes.com/", "ny_nyt"),
    ("The Wall Street Journal", "EUA", "en", "https://www.wsj.com/", "wsj"),
    ("The Guardian", "Reino Unido", "en", "https://www.theguardian.com/international", None),
    ("BBC News", "Reino Unido", "en", "https://www.bbc.com/news", None),
    ("Le Monde", "França", "fr", "https://www.lemonde.fr/", None),
    ("Le Figaro", "França", "fr", "https://www.lefigaro.fr/", None),
    ("El País", "Espanha", "es", "https://elpais.com/", None),
    ("Der Spiegel", "Alemanha", "de", "https://www.spiegel.de/", None),
    ("Frankfurter Allgemeine", "Alemanha", "de", "https://www.faz.net/", None),
    ("Corriere della Sera", "Itália", "it", "https://www.corriere.it/", None),
    ("Al Jazeera", "Catar", "en", "https://www.aljazeera.com/", None),
    ("Haaretz", "Israel", "en", "https://www.haaretz.com/", None),
    ("The Times of India", "Índia", "en", "https://timesofindia.indiatimes.com/", None),
    ("The Japan Times", "Japão", "en", "https://www.japantimes.co.jp/", None),
    ("The Globe and Mail", "Canadá", "en", "https://www.theglobeandmail.com/", None),
    ("Toronto Star", "Canadá", "en", "https://www.thestar.com/", "can_ts"),
    ("Reforma", "México", "es", "https://www.reforma.com/", "mex_ref"),
    ("La Nación", "Argentina", "es", "https://www.lanacion.com.ar/", None),
    ("The Sydney Morning Herald", "Austrália", "en", "https://www.smh.com.au/", None),
]
FF = "https://d2dr22b2lm4tvw.cloudfront.net/{code}/{data}/front-page-large.jpg"
LIXO = re.compile(r"(newsletter|subscribe|sign in|log in|assine|abonnez|suscr|abonn|cookie|podcast|crossword|wordle|horoscope|games?\b|shop|menu|skip to)", re.I)


def baixar(url):
    r = subprocess.run(["curl", "-sSfL", "--compressed", "--max-time", "30", url], capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip() or f"curl {r.returncode}")
    return r.stdout


def existe(url):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-I", "-w", "%{http_code}", "--max-time", "20", url], capture_output=True, text=True)
    return r.stdout.strip() == "200"


def chamadas(pagina, base, limite=15):
    s = re.sub(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", "", pagina, flags=re.S | re.I)
    host = urlparse(base).netloc.replace("www.", "")
    vistos, out = set(), []
    for m in re.finditer(r'<a\b[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', s, re.S | re.I):
        texto = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        url = urljoin(base, html.unescape(m.group(1)))
        if not (35 <= len(texto) <= 220) or LIXO.search(texto) or LIXO.search(url):
            continue
        if host not in urlparse(url).netloc or urlparse(url).path.count("/") < 2:
            continue
        chave = texto.lower()[:80]
        if chave in vistos or url in vistos:
            continue
        vistos.update([chave, url])
        out.append({"titulo": texto, "url": url})
        if len(out) >= limite:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.data):
        raise SystemExit(f"Data inválida (use AAAA-MM-DD): {a.data}")
    os.makedirs(os.path.join(a.saida, "html"), exist_ok=True)
    res, sem = [], []
    for nome, pais, idioma, site, ff in JORNAIS:
        capa = FF.format(code=ff, data=a.data) if ff else None
        if capa and not existe(capa):
            capa = None
        try:
            pag = baixar(site).decode("utf-8", "replace")
        except Exception as e:
            if capa:
                res.append({"jornal": nome, "pais": pais, "idioma": idioma, "site": site, "capa_impressa": capa, "chamadas": []})
            sem.append({"jornal": nome, "motivo": f"página inicial não abriu: {e}"[:200]})
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", nome.lower()).strip("-")
        open(os.path.join(a.saida, "html", slug + ".html"), "w", encoding="utf-8").write(pag)
        ch = chamadas(pag, site)
        if not ch and not capa:
            sem.append({"jornal": nome, "motivo": "nenhuma chamada reconhecida na página"})
            continue
        res.append({"jornal": nome, "pais": pais, "idioma": idioma, "site": site, "capa_impressa": capa, "chamadas": ch})
    json.dump(res, open(os.path.join(a.saida, "mundo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sem, open(os.path.join(a.saida, "sem_acesso.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"jornais lidos: {len(res)}; sem acesso: {[x['jornal'] for x in sem]}")


if __name__ == "__main__":
    main()
