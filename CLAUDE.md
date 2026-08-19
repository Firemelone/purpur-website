# PURPUR — Projektregeln

Repo für die Website **purpur.berlin**. Statisches HTML/CSS/JS ohne Framework
und ohne Build-Schritt; die Dateien in der Repo-Wurzel sind 1:1 das, was GitHub
Pages ausliefert.

## Sync — läuft automatisch, muss nicht angefordert werden

- **Zu Beginn jeder Sitzung**, vor der ersten Änderung: `git pull`.
- **Nach jeder abgeschlossenen Änderung:** committen **und** `git push` — nicht
  erst am Sitzungsende, damit von jedem Rechner aus weitergearbeitet werden kann.
- Direkt auf `main`. Branches und PRs nur, wenn ausdrücklich gewünscht.

## Die Seite ist live

**Stand 19.08.2026: <https://purpur.berlin> ist öffentlich erreichbar.** GitHub
Pages liefert den `main`-Branch aus (Source „Deploy from a branch", Ordner `/`),
Custom Domain `purpur.berlin`, „Enforce HTTPS" aktiv, Zertifikat von Let's
Encrypt. `www.purpur.berlin` leitet per 301 auf die Hauptdomain.

Daraus folgt die wichtigste Regel für alle weiteren Sitzungen:

- **Jeder Push auf `main` geht binnen ein bis zwei Minuten live.** Es gibt keine
  Staging-Umgebung und keinen Review-Schritt dazwischen. Wer committet,
  veröffentlicht.
- Vor dem Push lokal prüfen: `python3 -m http.server 8080` im Repo-Ordner.
- Bei größeren Umbauten lieber auf einem Branch arbeiten und erst nach Sichtung
  nach `main` mergen — Branches deployen nicht.
- Die Datei `CNAME` im Repo-Wurzelverzeichnis enthält `purpur.berlin` und wurde
  von GitHub selbst angelegt. **Nicht löschen und nicht ändern** — ohne sie
  fällt die Custom Domain aus und die Seite ist nur noch unter
  `firemelone.github.io` erreichbar.
- Das Repo ist **öffentlich**. Niemals Zugangsdaten, Keys oder Tokens
  committen; so etwas gehört in GitHub-Secrets.

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

## Rechtstexte

`impressum.html` und `datenschutz.html` sind ausgefüllt und öffentlich. Sie sind
Pflichtangaben (§ 5 DDG, Art. 13 DSGVO) und müssen erreichbar bleiben — die
Links im Footer jeder Seite also nicht entfernen.

Wenn sich am Aufbau der Seite etwas ändert, muss die Datenschutzerklärung
mitgepflegt werden: Sobald Cookies, externe Schriften, Karten, eingebettete
Videos, ein Kontaktformular oder Analyse-Werkzeuge dazukommen, stimmt der
aktuelle Text nicht mehr. Er beschreibt ausdrücklich eine Seite ohne all das.
