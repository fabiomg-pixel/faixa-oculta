"""Build the static GitHub Pages copy of Faixa Oculta from an export of the artifact database.

Usage:
  python3 -I tools/montar_site.py --dump DIR --assets DIR [--pagina faixa-oculta.html] [--saida .]

--dump    folder written by ArtifactData list with out_dir: DIR/<collection>/<doc_id>.json
          (collections: edicoes, itens, guias, semanas, cultura, dias). Never include data/users.
--assets  folder with the artifact's cover assets, one file per asset id (<id> or <id>.<ext>).
--pagina  the page source as published on claude.ai (no doctype; the skeleton is added here).
          Defaults to the existing pagina.html in the site root.
--saida   site root (default: current folder). Writes index.html, data/revista.json, capas/<id>.jpg.

Prints the asset ids referenced by the data but missing from --assets, so they can be fetched
(Artifact tool, action "read", path=<asset id>) and the script run again.
"""
import argparse, glob, json, os, re, shutil, sys

COLECOES = ["edicoes", "itens", "guias", "semanas", "cultura", "dias",
            "cine_edicoes", "cine_itens", "cine_guias", "livro_edicoes", "livro_itens", "livro_guias", "agenda", "leituras"]
SKELETON_HEAD = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<link rel="icon" type="image/svg+xml" href="icone.svg">
<link rel="icon" type="image/png" sizes="512x512" href="icone-512.png">
<link rel="apple-touch-icon" href="icone-180.png">
<meta name="theme-color" content="#F3EEE4">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.4 system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""
SKELETON_TAIL = "\n</body>\n</html>\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--assets", required=True)
    ap.add_argument("--pagina")
    ap.add_argument("--saida", default=".")
    a = ap.parse_args()

    saida = os.path.abspath(a.saida)
    pagina = a.pagina or os.path.join(saida, "pagina.html")
    src = open(pagina, encoding="utf-8").read()
    if os.path.abspath(pagina) != os.path.join(saida, "pagina.html"):
        shutil.copy(pagina, os.path.join(saida, "pagina.html"))

    bundle = {}
    for col in COLECOES:
        bundle[col] = {}
        for f in sorted(glob.glob(os.path.join(a.dump, col, "*.json"))):
            doc = json.load(open(f, encoding="utf-8"))
            if isinstance(doc, dict) and "data" in doc and "version" in doc:
                doc = doc["data"]
            bundle[col][os.path.basename(f)[:-5]] = doc

    txt = json.dumps(bundle, ensure_ascii=False)
    ids = sorted(set(re.findall(r"(?:/_blob/|capas/)([0-9a-f]{32})", txt)))
    disponiveis = {}
    for f in os.listdir(a.assets):
        m = re.match(r"([0-9a-f]{32})", f)
        if m:
            disponiveis[m.group(1)] = os.path.join(a.assets, f)
    os.makedirs(os.path.join(saida, "capas"), exist_ok=True)
    faltando = []
    for i in ids:
        if i in disponiveis:
            dst = os.path.join(saida, "capas", i + ".jpg")
            if os.path.abspath(disponiveis[i]) != os.path.abspath(dst):
                shutil.copy(disponiveis[i], dst)
        else:
            faltando.append(i)
    txt = re.sub(r"/_blob/([0-9a-f]{32})", r"capas/\1.jpg", txt)

    os.makedirs(os.path.join(saida, "data"), exist_ok=True)
    open(os.path.join(saida, "data", "revista.json"), "w", encoding="utf-8").write(txt)
    open(os.path.join(saida, "index.html"), "w", encoding="utf-8").write(SKELETON_HEAD + src + SKELETON_TAIL)
    open(os.path.join(saida, ".nojekyll"), "w").close()

    print("documentos:", {k: len(v) for k, v in bundle.items()}, "| capas:", len(ids) - len(faltando), "de", len(ids))
    if faltando:
        print("FALTANDO:", " ".join(faltando))
        sys.exit(2)


if __name__ == "__main__":
    main()
