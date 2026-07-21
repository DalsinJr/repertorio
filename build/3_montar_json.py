# -*- coding: utf-8 -*-
"""Monta data/repertorio.json a partir do setlist + estruturas + cifras extraidas dos PDFs."""
import json, io, os, re, sys, unicodedata, datetime
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

def slug(t):
    t = unicodedata.normalize('NFD', t)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', t.lower()))[:40]

# qual PDF alimenta qual posicao do repertorio
MAPA = {"alegria-demais":"alegria", "voz-do-vento":"vozvento", "esverdear":"esverdear", "mais-um-homem-apaixonado":"homem", "esse-e-meu-preco":"preco", "erro-eu":"erroeu", "heranca-do-meu-pai":"heranca", "lucro":"lucro", "sanfona-fuxiqueira":"fuxiqueira", "sete-menina":"sete", "to-nem-ai":"tonem", "galope-razante-estrela-miuda-sujeito-de-":"galope", "como-dois-animais":"animais", "zum-zum-zum":"zumzum", "enquanto-engomo-a-calca":"engoma", "espumas-ao-vento":"espumas", "carcara-festa":"carcara"}

def main():
    import importlib
    ST = importlib.import_module('2_estruturas').ST if os.path.exists(os.path.join(AQUI,'2_estruturas.py')) else {}
    cifras  = json.load(io.open(os.path.join(AQUI, '_cache_cifras.json'), encoding='utf-8'))
    setlist = json.load(io.open(os.path.join(AQUI, '_setlist.json'), encoding='utf-8'))

    musicas = []
    for i, s in enumerate(setlist):
        k = MAPA.get(slug(s["t"]))
        mid = slug(s["t"])
        sug, secs = ST.get(mid, (True, []))
        musicas.append({
            "id":   mid,
            "t":    s["t"], "a": s["a"], "k": s["k"],
            "tag":  s.get("tag"), "note": s.get("note"),
            "bl": None, "sug":  sug,                                   # True = progressao sugerida, nao conferida
            "st":   secs,                                  # estrutura: partes com acordes
            "c":    cifras[k]["clean"] if k else "",       # cifra completa (letra + acordes)
            "sk":   cifras[k]["skip"]  if k else [],       # linhas de fala de palco, ocultas por padrao
            "tr":   0,
        })

    # blocos do show, como no PDF do repertorio: abertura / participacao / retomada
    part = [i for i, m in enumerate(musicas) if m["note"]]
    ini, fim = (part[0], part[-1]) if part else (len(musicas), -1)
    for i, m in enumerate(musicas):
        m["bl"] = "1ª PARTE" if i < ini else ("PARTICIPAÇÃO — ANDRÉ PRANDO" if i <= fim else "2ª PARTE")

    pacote = {"v": 5, "atualizado": datetime.datetime.now().isoformat(timespec='seconds'),
              "musicas": musicas, "cifra": {}, "estr": {}, "tr": {}}
    destino = os.path.join(RAIZ, 'data', 'repertorio.json')
    io.open(destino, 'w', encoding='utf-8').write(json.dumps(pacote, ensure_ascii=False, indent=1))
    print("ok:", len(musicas), "musicas ->", destino)
    print("   com cifra:", sum(1 for m in musicas if m["c"]),
          "| estrutura real:", sum(1 for m in musicas if not m["sug"]))

if __name__ == '__main__':
    main()
