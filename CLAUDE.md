# PURPUR — Projektregeln

Repo für die Website **purpur.berlin**. Statisches HTML/CSS/JS ohne Framework
und ohne Build-Schritt; die Dateien in der Repo-Wurzel sind 1:1 das, was GitHub
Pages später ausliefert.

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
- **Keine `CNAME`-Datei** anlegen — die legt GitHub selbst an, sobald die Custom
  Domain gesetzt wird, und das gehört zum Livegang.
- Pushen ist trotzdem jederzeit gefahrlos: ohne Pages wird nichts ausgeliefert.

Die Seite geht online, wenn das gesagt wird, nicht als Nebeneffekt eines Pushs.

## DNS nicht anfassen

Die Zone bei IONOS ist eingerichtet (siehe `README.md`). Die Mail-Records — MX,
SPF, DKIM, DMARC, `autodiscover` — tragen die Postfächer `info@purpur.berlin`
und `booking@purpur.berlin`. Wer daran etwas ändert, legt die Mail lahm. Ohne
ausdrücklichen Auftrag bleibt die Zone, wie sie ist.

## Sprache

Seite und Code-Kommentare auf Deutsch.

## Konventionen

- HTML in `lang="de"`, semantische Tags, jede Seite mit `<title>` und
  `<meta name="description">`.
- Farben und Maße als CSS-Custom-Properties in `:root` (`assets/css/style.css`)
  — nicht hart im Regelwerk verstreuen. Dark Mode läuft über
  `prefers-color-scheme`; neue Farben dort mitpflegen.
- Interne Links absolut ab Root (`/impressum.html`), damit sie in jeder
  Verzeichnistiefe stimmen. Zum lokalen Ansehen deshalb einen Server starten,
  nicht die Datei direkt öffnen.
- Keine externen CDN-Skripte, keine Tracker ohne Consent-Banner — die Seite
  liefert aktuell keine personenbezogenen Daten an Dritte aus, und das soll so
  bleiben, bis wir uns aktiv anders entscheiden.
- Bilder als WebP/AVIF, mit `width`/`height` im Tag gegen Layout-Shift.

## Vor dem öffentlichen Launch

`impressum.html` und `datenschutz.html` sind derzeit Platzhalter mit TODO. Sie
müssen mit echtem Namen und echter Anschrift ausgefüllt sein, bevor die Seite
öffentlich geht — in Deutschland Impressumspflicht (§ 5 DDG), und ein fehlendes
Impressum ist abmahnfähig. Beide Seiten stehen bis dahin auf
`<meta name="robots" content="noindex">`.
