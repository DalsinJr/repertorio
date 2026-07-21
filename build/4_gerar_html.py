# -*- coding: utf-8 -*-
"""
Atualiza o SONGS embutido no index.html a partir de data/repertorio.json.

MODELO ATUAL: data/repertorio.json é a ÚNICA fonte da verdade. O app carrega
os dados por `fetch` em runtime (e guarda um cache no navegador pra funcionar
offline no palco). O bloco `let SONGS=[...]` dentro do index.html é só um
FALLBACK — usado quando se abre o arquivo direto (file://) sem servidor.

Este script NÃO reescreve o index.html inteiro (o template não vive mais aqui).
O index.html é o artefato mantido à mão: UI, CSS e lógica. Aqui só trocamos a
linha de dados embutida, mantendo o fallback offline em sincronia com o JSON.

Uso:
    python3 4_gerar_html.py
"""
import json, io, os, re

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
IDX  = os.path.join(RAIZ, "index.html")

d    = json.load(io.open(os.path.join(RAIZ, "data", "repertorio.json"), encoding="utf-8"))
data = json.dumps(d["musicas"], ensure_ascii=False)
novo = "let SONGS=" + data + ", LS='blackShow_v4';"

html = io.open(IDX, encoding="utf-8").read()

# troca apenas a linha de dados embutida. `LS='blackShow_v4'` é único no arquivo,
# então o casamento preguiçoso encontra exatamente o fim do bloco de dados.
padrao = re.compile(r"let SONGS=\[.*?\], LS='blackShow_v4';", re.S)
# função de replace evita que o re interprete os \n / \u dentro do JSON.
html2, n = padrao.subn(lambda m: novo, html, count=1)

if n != 1:
    raise SystemExit(
        "Não achei `let SONGS=[...], LS='blackShow_v4';` no index.html.\n"
        "Se você mudou essa linha ou a chave LS, ajuste o padrão neste script."
    )

io.open(IDX, "w", encoding="utf-8").write(html2)
print("index.html: fallback offline atualizado com %d músicas." % len(d["musicas"]))
