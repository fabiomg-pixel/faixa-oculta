"""Prepare clean readings (our summaries of news articles and reviews) for the `leituras` collection.

Usage:
  python3 -I tools/leituras.py --saida DIR ARQUIVO.json [ARQUIVO.json ...]

Each input file is {"leituras": [...], "pulados": [...]} as described in tools/LEITURAS.md. Writes one JSON per
reading to DIR/<doc_id>.json (doc_id = first 16 hex chars of sha1 of the normalized URL, so the same article always
maps to the same doc) and prints a summary plus warnings for readings that break the rules (missing url/fonte/resumo,
summary too long, quote of 15 words or more).
"""
import argparse, hashlib, json, os, re, sys, urllib.parse


def limpar_url(url):
    s = urllib.parse.urlsplit(str(url).strip())
    q = [(k, v) for k, v in urllib.parse.parse_qsl(s.query, keep_blank_values=True)
         if not k.lower().startswith(("utm_", "fbclid", "gclid"))]
    return urllib.parse.urlunsplit((s.scheme, s.netloc, s.path, urllib.parse.urlencode(q), ""))


def chave(url):
    u = limpar_url(url).rstrip("/")
    return re.sub(r"^https?://(www\.)?", "", u).lower()


def doc_id(url):
    return hashlib.sha1(chave(url).encode()).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", required=True)
    ap.add_argument("arquivos", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    feitos, avisos = {}, []
    for arq in a.arquivos:
        for l in json.load(open(arq, encoding="utf-8")).get("leituras", []):
            if not (l.get("url") and l.get("fonte") and l.get("resumo")):
                avisos.append(f"sem url/fonte/resumo: {l.get('url') or l.get('titulo')}")
                continue
            l["url"] = limpar_url(l["url"])
            palavras = len(" ".join(map(str, l["resumo"])).split())
            if palavras > 320:
                avisos.append(f"resumo com {palavras} palavras: {l['url']}")
            if l.get("citacao") and len(str(l["citacao"]).split()) >= 15:
                avisos.append(f"citação longa removida: {l['url']}")
                l.pop("citacao")
            l = {k: v for k, v in l.items() if v not in (None, "", [])}
            i = doc_id(l["url"])
            feitos[i] = l
    for i, l in feitos.items():
        json.dump(l, open(os.path.join(a.saida, f"{i}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(json.dumps({"leituras": len(feitos), "ids": sorted(feitos), "avisos": avisos}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
