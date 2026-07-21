# repertorio-show

App de palco para acompanhar o repertório durante o show. Roda no iPad e no navegador,
100% offline, arquivo único. Feito para o Black do Acordeon — show FENFIT 2026.

## O que é

`index.html` é um app autocontido (HTML + CSS + JS inline, sem build, sem dependências).
Ele exibe 35 músicas em duas visões:

- **Estrutura** (padrão): cards por seção — INTRO, VERSO, REFRÃO… — com os acordes em
  fonte grande e uma deixa curta da letra em itálico. É o que se usa no palco.
- **Cifra completa**: letra corrida com acordes acima, para as músicas que têm PDF.

## Arquitetura

Ponto central: **`data/repertorio.json` é a ÚNICA fonte da verdade**, versionada no git.
Não existe backend. O app é hospedado estático (GitHub Pages) e publicar = `git push`.

Fluxo de dados no boot (`index.html`):

1. `let SONGS = [...]` embutido no HTML — **fallback offline**, usado só quando não há
   cache nem rede (ex.: abrir o arquivo direto por `file://`). Mantido em sincronia com o
   JSON pelo `4_gerar_html.py`.
2. **Cache** em `localStorage['blackShow_dados']` — a última versão oficial do JSON já
   baixada. Faz o app funcionar offline no palco depois de ter carregado uma vez online.
3. **`fetch('data/repertorio.json')`** — a fonte da verdade. Ao carregar com sucesso,
   substitui o `SONGS` e regrava o cache. É o passo (3) que faz um `git push` no JSON
   aparecer pra todo mundo.

Por cima dessa base ficam as **edições locais** (rascunho), indexadas por id em
`localStorage['blackShow_v4']` → `store.cifra` / `store.estr` / `store.tr`. Elas
sobrescrevem a base na tela, mas **só viram oficiais** quando o usuário exporta o
`repertorio.json` (⚙︎ › Exportar) e dá commit/push. `pacote()` gera esse JSON com as
edições já mescladas dentro de `musicas`.

### Persistência: o ponto delicado

Este app já quebrou por causa disso. Leia antes de mexer.

- `file://` e iframes isolados (o preview do Cowork) **bloqueiam `localStorage`** e lançam
  `SecurityError`. O app faz um teste real de escrita/leitura no boot (`STORAGE_OK`) e
  mostra uma tarja vermelha quando não dá. **Nunca engula esse erro em silêncio** — foi
  exatamente esse `try/catch` vazio que fez o usuário achar que salvava e não salvava.
  Servido por https (GitHub Pages) ou pelo `servir.sh`, o `localStorage` funciona e a
  tarja some.
- Tudo é indexado por **id estável** (slug do título: `carcara-festa`, `esverdear`), nunca
  por posição no array. Indexar por posição quebra tudo quando se adiciona uma música.
- `pacote()` espalha a música inteira (`...s`) antes de sobrescrever campos editados —
  assim nenhum campo (ex.: `bl`) se perde no export. Não volte a listar campo por campo.
- O botão **🧹 Limpar rascunho** zera `store.cifra/estr/tr`. É o que se usa depois de
  publicar, pra o rascunho local não brigar com uma edição feita direto no JSON.

## Estrutura de pastas

```
index.html              o app (UI + lógica), mantido à mão
data/repertorio.json    FONTE DA VERDADE (36 músicas, estruturas, cifras)
fontes/*.pdf            cifras originais do Moises.ai + repertório FENFIT
build/                  scripts de apoio
  1_extrair_pdfs.py     PDF -> texto, separa medleys, filtra fala de palco
  2_estruturas.py       ST = {} — estruturas por seção, escritas à mão
  3_montar_json.py      junta tudo -> data/repertorio.json
  4_gerar_html.py       atualiza SÓ o embed de fallback no index.html a partir do JSON
  teste.js              suíte jsdom (rodar sempre antes de entregar)
servir.sh               servidor local em http://localhost:8080
```

## Editar e publicar (fluxo normal)

Para mudar uma cifra, há dois caminhos — os dois acabam no mesmo lugar:

1. **No app**: edita a parte/cifra → ⚙︎ › **Exportar repertorio.json** → substitui o
   arquivo em `data/` → `git commit && git push`. O GitHub Pages republica sozinho.
2. **Direto no JSON**: edita `data/repertorio.json` (ou pelo editor web do GitHub) e
   commita. O app lê de lá no próximo carregamento online.

## Regenerar a partir dos PDFs

```bash
cd build
python3 1_extrair_pdfs.py     # precisa de pdfplumber
python3 3_montar_json.py      # -> data/repertorio.json  (a fonte da verdade)
python3 4_gerar_html.py       # sincroniza o fallback offline embutido no index.html
node teste.js                 # precisa de jsdom
```

`4_gerar_html.py` **não** reescreve mais o `index.html` inteiro — só troca a linha
`let SONGS=[...]` (o fallback offline). Mudanças de UI/lógica são feitas direto no
`index.html`, que é o artefato mantido. Só cuide de não alterar o formato dessa linha
de dados sem ajustar o padrão de replace do script.

## Convenções dos dados

Cada música em `data/repertorio.json`:

```json
{ "id":"carcara-festa", "t":"Carcará + Festa", "a":"João do Vale / Gonzaguinha",
  "k":"Dm", "tag":"BAIÃO", "note":"Participação André Prando",
  "sug": false,
  "st": [ {"s":"REFRÃO", "c":"Dm · G · Dm", "q":"“Bela é o Recife…”", "r":"repete"} ],
  "c":  "linha de acordes\nlinha de letra\n…",
  "sk": [12, 47],
  "tr": 0 }
```

- `sug: true` → progressão sugerida, **não conferida de ouvido**. O app mostra um aviso
  tracejado laranja. Vira `false` assim que o usuário edita a estrutura.
- `st[].c` → acordes separados por `·`, `|` vira barra de compasso.
- `sk` → índices das linhas de `c` que são **fala de palco**, ocultas por padrão
  (botão 🎤 mostra em cinza). Ex.: "Toca demais esse baixista!", "Oi Glau".
- As letras vêm de transcrição automática do Moises.ai e **têm erro de palavra**
  ("papaguê" em vez de "pobre pra roer"). A visão de estrutura é a confiável.

## Cuidados

- **Não reproduzir letras completas de terceiros.** As cifras aqui vieram dos PDFs do
  próprio usuário. Para as 23 músicas sem PDF, a estrutura traz só a progressão de
  acordes e uma deixa curta — de propósito. Não preencher buscando letra na web.
- `4_gerar_html.py` troca a linha `let SONGS=[...], LS='blackShow_v4';` por regex. A chave
  `LS='blackShow_v4'` é o âncora que marca o fim do bloco de dados — é única no arquivo.
  Se mudar essa linha, ajuste o padrão no script (ele aborta se não casar, não corrompe).
- Transposição: `SH`/`FL` escolhem sustenido ou bemol pelo tom. Tom de F pede B♭, não A♯.
  O bVII sempre sai em bemol.
- O swipe é desativado no modo de edição para não trocar de música sem querer.

## Ideias em aberto

- Preencher as 23 estruturas ainda marcadas como `sug: true` conferindo de ouvido.
- Modo setlist com cronômetro / duração acumulada.
- Pedal Bluetooth já funciona (setas e espaço), mas sem configuração de tecla.
- Dois iPads sincronizados (banda inteira vendo a mesma parte).
