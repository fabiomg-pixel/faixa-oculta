"""Find the day's newspaper front pages on vercapas.com.br for the morning bulletin.

Usage:
  python3 -I tools/capas_dia.py --data AAAA-MM-DD --saida DIR

For each paper in JORNAIS, opens https://www.vercapas.com.br/capa/<slug>/ and looks for the cover image of that date.
Writes DIR/capas.json = [{"jornal", "slug", "data", "imagem", "pagina", "site", "arquivo"}] ("pagina" is the dated cover image itself; the vercapas paper page always shows the latest cover) and downloads each cover to
DIR/<slug>.jpg (only so the routine can look at it and transcribe the headline; the images are not published).
Papers without a cover for the date are listed in DIR/sem_capa.json. Uses plain curl, no disguise; a refused page is skipped.
"""
import argparse, json, os, re, subprocess

JORNAIS = [
    ("O Globo", "o-globo", "https://oglobo.globo.com/"),
    ("Folha de S.Paulo", "folha-de-s-paulo", "https://www.folha.uol.com.br/"),
    ("Estadão", "estadao", "https://www.estadao.com.br/"),
    ("Valor Econômico", "valor-economico", "https://valor.globo.com/"),
    ("Extra", "extra", "https://extra.globo.com/"),
    ("O Dia", "o-dia", "https://odia.ig.com.br/"),
    ("Correio Braziliense", "correio-braziliense", "https://www.correiobraziliense.com.br/"),
]


def baixar(url):
    r = subprocess.run(["curl", "-sSfL", "--compressed", "--max-time", "30", url], capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip() or f"curl {r.returncode}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    m_data = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", a.data)
    if not m_data:
        raise SystemExit(f"Data inválida (use AAAA-MM-DD): {a.data}")
    ano, mes, dia = m_data.groups()
    marca = f"{dia}{mes}{ano}"
    capas, sem = [], []
    for nome, slug, site in JORNAIS:
        pagina = f"https://www.vercapas.com.br/capa/{slug}/"
        try:
            html = baixar(pagina).decode("utf-8", "replace")
        except Exception as e:
            sem.append({"jornal": nome, "motivo": f"página não abriu: {e}"})
            continue
        achadas = re.findall(rf"https://cdn\.vercapas\.com\.br/covers/{re.escape(slug)}/\d{{4}}/capa-jornal-{re.escape(slug)}-{marca}-[0-9a-f]+\.(?:jpe?g|webp)", html)
        if not achadas:
            sem.append({"jornal": nome, "motivo": "sem capa desta data"})
            continue
        img = achadas[0]
        arq = os.path.join(a.saida, f"{slug}.jpg")
        try:
            open(arq, "wb").write(baixar(img))
        except Exception as e:
            arq = None
        capas.append({"jornal": nome, "slug": slug, "data": a.data, "imagem": img, "pagina": img, "site": site, "arquivo": arq})
    json.dump(capas, open(os.path.join(a.saida, "capas.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(sem, open(os.path.join(a.saida, "sem_capa.json"), "w"), ensure_ascii=False, indent=1)
    print(f"capas: {len(capas)}; sem capa: {[s['jornal'] for s in sem]}")


if __name__ == "__main__":
    main()
