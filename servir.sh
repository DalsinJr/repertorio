#!/bin/bash
# Sobe um servidor local. Necessario para o app ler data/repertorio.json sozinho
# e para o navegador liberar o armazenamento local (file:// bloqueia).
cd "$(dirname "$0")"
PORTA=${1:-8080}
echo "→ http://localhost:$PORTA"
command -v open >/dev/null && (sleep 1; open "http://localhost:$PORTA") &
python3 -m http.server "$PORTA"
