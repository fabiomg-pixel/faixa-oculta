"""Junta as marcações e avaliações do leitor vindas de dois lugares, chave a chave (o carimbo mais novo vence):
o documento data/users/me/estado do artefato (claude.ai) e o estado.json que o site do GitHub grava no repositório
privado fabiomg-pixel/faixa-oculta-estado. Saída: um estado.json no formato do artefato, para sync_radar.py --estado
e para as rotinas lerem `avaliacoes` e `marcas`.

uso: python3 -I tools/juntar_estado.py --saida estado.json [--claude estado_claude.json] [--github estado_github.json]
"""
import argparse, json, os


def ler(caminho):
    if not caminho or not os.path.exists(caminho):
        return {}
    with open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    if isinstance(d.get("data"), dict):  # export do ArtifactData
        d = d["data"]
    return d if isinstance(d, dict) else {}


def obj(v):
    return v if isinstance(v, dict) else {}


def juntar(base, base_em, novo, novo_em):
    out, em = dict(obj(base)), dict(obj(base_em))
    for k in set(obj(novo)) | set(obj(novo_em)):
        quando = str(obj(novo_em).get(k, ""))
        if quando >= str(em.get(k, "")):
            if obj(novo).get(k):
                out[k] = novo[k]
            else:
                out.pop(k, None)
            em[k] = quando
    return out, em


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude")
    ap.add_argument("--github")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    c, g = ler(a.claude), ler(a.github)
    out = dict(c)
    out["marcas"], out["marcas_em"] = juntar(c.get("marcas"), c.get("marcas_em"), g.get("marcas"), g.get("marcas_em"))
    out["avaliacoes"], out["avaliacoes_em"] = juntar(c.get("avaliacoes"), c.get("avaliacoes_em"), g.get("avaliacoes"), g.get("avaliacoes_em"))
    with open(a.saida, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    up = sum(1 for v in out["avaliacoes"].values() if v == "up")
    down = sum(1 for v in out["avaliacoes"].values() if v == "down")
    print(json.dumps({"marcas": len(out["marcas"]), "avaliacoes_up": up, "avaliacoes_down": down,
                      "fontes": [n for n, d in (("claude", c), ("github", g)) if d]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
