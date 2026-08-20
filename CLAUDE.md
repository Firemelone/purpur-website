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

**Die Website ist durchgaengig englisch** — jede Seite, jeder Text, jedes neue
Element. Kein deutscher Fliesstext, auch nicht in den Rechtstexten. `lang="en"`
auf jeder Seite.

Code-Kommentare, Commit-Nachrichten und die Doku in diesem Repo bleiben deutsch;
das ist die Arbeitssprache, nicht die Sprache des Produkts.

## Konventionen

- HTML in `lang="de"`, semantische Tags, jede Seite mit `<title>` und
  `<meta name="description">`.
- Farben, Maße und Schriften als CSS-Custom-Properties in `:root`
  (`assets/css/style.css`) — nicht hart im Regelwerk verstreuen. Dark Mode läuft
  über `prefers-color-scheme`; neue Farben dort mitpflegen.
- Interne Links absolut ab Root (`/impressum.html`), damit sie in jeder
  Verzeichnistiefe stimmen. Zum lokalen Ansehen deshalb einen Server starten,
  nicht die Datei direkt öffnen.
- Schriften: Titel und Wortmarke in `var(--font-titel)` (Mosher), alles übrige
  in `var(--font-text)` (GC Furion). Nie direkt den Schriftnamen schreiben.
- Keine externen CDN-Skripte, keine Tracker ohne Consent-Banner — die Seite
  liefert aktuell keine personenbezogenen Daten an Dritte aus, und das soll so
  bleiben, bis wir uns aktiv anders entscheiden.
- Bilder als WebP/AVIF, mit `width`/`height` im Tag gegen Layout-Shift.

## Schriften

Zwei lizenzierte Schriften, selbst gehostet in `assets/fonts/`:

- **Mosher** (Pixelbuddha) — Display-Schrift, ausschließlich für Titel und die
  Wortmarke. Nur ein Schnitt (400). Die Schrift kennt nur Großbuchstaben:
  Kleinbuchstaben werden auf Versalien abgebildet. Ihr fehlen ß und §.
- **GC Furion** (Glyphonic) — Grundschrift, Schnitte 400/600/700.

Regeln dazu:

- **Nur `.woff2` ins Repo.** `.ttf` und `.otf` sind Desktop-Formate; sie sind
  zwei- bis dreimal so groß und gehören nicht auf einen Webserver.
- Neue Schnitte nur aufnehmen, wenn sie wirklich gebraucht werden — jede Datei
  kostet Ladezeit. Aktuell sind es 144 KB.
- `font-display: swap` bei jedem `@font-face` beibehalten, sonst bleibt die
  Seite beim Laden leer.
- Die kritischen Schnitte werden im `<head>` per `rel="preload"` vorgeladen. Wer
  eine neue Seite anlegt, übernimmt die Preload-Zeilen mit.

**Lizenz:** Beide Schriften sind kommerziell und lagen ohne Lizenzdatei bei. Vor
weiterer kommerzieller Nutzung ist zu prüfen, ob die erworbene Lizenz Webfont-
Einbettung abdeckt und ob die Ablage in einem öffentlichen Repository zulässig
ist. Siehe `README.md`.

## Rechtstexte

`imprint.html` und `privacy.html` sind ausgefüllt und öffentlich. Sie sind
Pflichtangaben (§ 5 DDG, Art. 13 DSGVO) und müssen erreichbar bleiben — die
Links im Footer jeder Seite also nicht entfernen.

Wenn sich am Aufbau der Seite etwas ändert, muss die Datenschutzerklärung
mitgepflegt werden: Sobald Cookies, externe Schriften, Karten, eingebettete
Videos, ein Kontaktformular oder Analyse-Werkzeuge dazukommen, stimmt der
aktuelle Text nicht mehr. Er beschreibt ausdrücklich eine Seite ohne all das.
