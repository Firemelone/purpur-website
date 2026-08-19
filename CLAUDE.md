# PURPUR — Projektregeln

Repo für die künftige Website **purpur.berlin**. Aktuell nur Grundgerüst, noch
kein Code und kein Hosting.

## Sync — läuft automatisch, muss nicht angefordert werden

- **Zu Beginn jeder Sitzung**, vor der ersten Änderung: `git pull`.
- **Nach jeder abgeschlossenen Änderung:** committen **und** `git push` — nicht
  erst am Sitzungsende, damit von jedem Rechner aus weitergearbeitet werden kann.
- Direkt auf `main`. Branches und PRs nur, wenn ausdrücklich gewünscht.

## Nichts veröffentlichen ohne Ansage

Solange nicht ausdrücklich etwas anderes gesagt wird, gilt:

- **Kein Hosting aktivieren** (kein GitHub Pages, kein Deploy).
- **Keine DNS-Einträge** bei IONOS ändern oder vorschlagen zu ändern.
- **Keine `CNAME`-Datei** anlegen — die würde die Domain mit GitHub Pages verknüpfen.

Die Seite geht online, wenn das gesagt wird, nicht als Nebeneffekt eines Pushs.

## Sprache

Seite und Code-Kommentare auf Deutsch.

## Vor dem öffentlichen Launch

`impressum.html` und `datenschutz.html` müssen existieren und mit echtem Namen und
echter Anschrift ausgefüllt sein — in Deutschland Impressumspflicht.
