#!/bin/zsh
# Lokale Vorschau des preview-Branches. Doppelklick genuegt.
# Laeuft nur auf diesem Rechner und im eigenen WLAN — nichts davon ist oeffentlich.
cd "$(dirname "$0")"
BRANCH=$(git branch --show-current)
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
echo "PURPUR — Vorschau (Branch: $BRANCH)"
echo
echo "  Auf diesem Mac:   http://localhost:8099"
[ -n "$IP" ] && echo "  Im WLAN (Handy):  http://$IP:8099"
echo
echo "  Beenden mit Strg-C."
echo
python3 -m http.server 8099
