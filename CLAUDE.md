# PURPUR — Projektregeln

Repo für die künftige Website **purpur.berlin**. Aktuell nur Grundgerüst, noch
kein Code und kein Hosting.

## Sync — läuft automatisch, muss nicht angefordert werden

- **Zu Beginn jeder Sitzung**, vor der ersten Änderung: `git pull`.
- **Nach jeder abgeschlossenen Änderung:** committen **und** `git push` — nicht
  erst am Sitzungsende, damit von jedem Rechner aus weitergearbeitet werden kann.
- Direkt auf `main`. Branches und PRs nur, wenn ausdrücklich gewünscht.

## Nichts veröffentlichen ohne Ansage

**Stand:** Die DNS-Einträge bei IONOS zeigen auf GitHub Pages, aber **GitHub Pages
ist bewusst ausgeschaltet**. Die Domain führt deshalb ins Leere (GitHub-404) — genau
so gewollt. Die Leitung liegt, der Hahn ist zu.

Solange nicht ausdrücklich etwas anderes gesagt wird, gilt:

- **Pages nicht aktivieren** (Settings → Pages bleibt auf "None").
- **Keine `CNAME`-Datei** anlegen — die gehört erst dazu, wenn Pages an ist.
- Pushen ist trotzdem jederzeit gefahrlos: ohne Pages wird nichts ausgeliefert.

Die Seite geht online, wenn das gesagt wird, nicht als Nebeneffekt eines Pushs.

## Sprache

Seite und Code-Kommentare auf Deutsch.

## Vor dem öffentlichen Launch

`impressum.html` und `datenschutz.html` müssen existieren und mit echtem Namen und
echter Anschrift ausgefüllt sein — in Deutschland Impressumspflicht.
