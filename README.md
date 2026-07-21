# Repertório Show

App de palco para acompanhar o show. Abre no iPad ou no navegador, funciona offline.

## Usar

**No computador:**

```bash
./servir.sh
```

Abre em `http://localhost:8080`, lê `data/repertorio.json` e guarda as edições no
navegador.

**No iPad (recomendado):** abra a **URL publicada** (GitHub Pages) no Safari e use
"Adicionar à Tela de Início" para rodar em tela cheia. Depois de carregar uma vez com
internet, o app funciona offline no palco — ele guarda uma cópia local dos dados.

> Abrir o `index.html` por duplo clique (`file://`) funciona pra ver, mas o navegador
> bloqueia o salvamento — o app avisa com uma tarja. Prefira a URL publicada ou o
> `servir.sh`.

## Editar e salvar (do próprio app)

`data/repertorio.json` é a fonte da verdade, versionada no git. O app salva direto lá.

1. Edite a parte/cifra (botão ✎).
2. Toque em **☁️ Salvar** (o botão flutuante que aparece quando há edições) — o app
   faz o commit no `data/repertorio.json` pela API do GitHub e o site republica em ~1 min.

**Configurar uma vez** (⚙︎ › *Conexão com o GitHub*): cole um **token fine-grained** do
GitHub. Crie em <https://github.com/settings/personal-access-tokens/new>:

- *Resource owner*: sua conta · *Repository access*: **Only select repositories** → `repertorio`
- *Permissions › Repository › Contents*: **Read and write**

O token fica guardado só no aparelho (localStorage). Dá pra revogar quando quiser na
mesma página do GitHub. Sem token, dá pra usar ⚙︎ › **Exportar .json** e commitar à mão.

### Publicação (GitHub Pages)

Já configurado: **Settings › Pages › Source: GitHub Actions**. O workflow
`.github/workflows/deploy.yml` republica a cada push na `main` (o "Salvar" do app é um push).
No iPad, recarregue uma vez com internet para pegar a versão nova (e atualizar a cópia offline).

## No palco

| | |
|---|---|
| Trocar de música | deslizar o dedo, ou tocar nas bordas ‹ › |
| Repertório completo | ☰ |
| Estrutura ↔ Cifra | ◧ |
| Falas de palco | 🎤 |
| Editar partes | ✎ |
| Tamanho, transpor, auto-scroll, tela ligada | ⚙︎ |

Teclado e pedal Bluetooth: setas trocam de música, espaço liga o auto-scroll, `V` alterna
a visão.

## Editar

Botão ✎ → cada parte ganha controles de mover (↑↓), duplicar (⧉), remover (🗑) e inserir.
Tocando no card abre o editor com paleta dos acordes do tom da música — dá pra montar uma
parte inteira sem teclado.

## Dados

As músicas ficam em `data/repertorio.json`. As que têm cifra completa e estrutura
conferida vieram dos PDFs em `fontes/`. As demais trazem uma progressão **sugerida**,
marcada com aviso laranja — precisa conferir de ouvido.

Editar e regenerar: veja `CLAUDE.md`.
