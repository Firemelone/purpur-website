# purpur-website

Website für **purpur.berlin**. Statisches HTML/CSS/JS, kein Framework, kein
Build-Schritt: was im Repo liegt, ist exakt das, was später ausgeliefert wird.

## Stand

- [x] Repo angelegt und mit Claude Code verbunden
- [x] Technik entschieden: statisches HTML/CSS/JS, Hosting über GitHub Pages
- [x] DNS bei IONOS auf GitHub Pages gestellt (autoritativ geprüft, siehe unten)
- [x] Grundgerüst der Seite: Startseite, Impressum, Datenschutz, Stylesheet
- [x] Imprint und Privacy Policy ausgefüllt
- [x] Eigene Schriften eingebunden (Mosher, GC Furion)
- [x] Seite auf Englisch umgestellt
- [x] Live: <https://purpur.berlin> seit dem 19.08.2026
- [ ] Inhalt der Startseite — aktuell nur ein Platzhalter

## Arbeiten

```bash
git clone https://github.com/Firemelone/purpur-website.git
cd purpur-website
```

Danach Claude Code in diesem Ordner öffnen. Pull und Push laufen automatisch,
siehe `CLAUDE.md`.

Lokal ansehen — die Seite braucht einen Server, weil die Links absolut ab Root
gesetzt sind (`/impressum.html`), über `file://` also ins Leere zeigen:

```bash
python3 -m http.server 8080
```

## Domain und DNS

`purpur.berlin` liegt bei IONOS. Die Zone zeigt seit dem 19.08.2026 auf GitHub
Pages:

| Typ   | Hostname | Wert                                   |
|-------|----------|----------------------------------------|
| A     | `@`      | 185.199.108.153 … 185.199.111.153      |
| CNAME | `www`    | `firemelone.github.io`                 |

Der frühere IONOS-Parkeintrag (A `217.160.0.71`, AAAA, TXT `_dep_ws_mutex`) ist
entfernt — IONOS hat dazu den Service „Default Site" deaktiviert.

**Die Mail-Records sind unberührt und müssen es bleiben:** MX auf `mx00`/`mx01
.ionos.de`, SPF-TXT, DKIM (`s1-ionos`/`s2-ionos._domainkey`), DMARC und
`autodiscover`. An `purpur.berlin` hängen die Postfächer `info@` und `booking@`;
wer diese Records anfasst, legt die Mail lahm.

## Hosting

Die Seite ist live unter <https://purpur.berlin>. GitHub Pages liefert den
`main`-Branch aus: Source „Deploy from a branch", Branch `main`, Ordner `/`,
Custom Domain `purpur.berlin`, „Enforce HTTPS" aktiv. Das Zertifikat stellt
Let's Encrypt aus und GitHub erneuert es selbst. `www.purpur.berlin` leitet per
301 auf die Hauptdomain.

**Jeder Push auf `main` geht damit binnen ein bis zwei Minuten live** — es gibt
keine Staging-Stufe. Vor dem Push lokal prüfen:

```bash
python3 -m http.server 8080
```

Das Repo ist öffentlich; das ist Voraussetzung für GitHub Pages ohne bezahlten
Plan. Quelltext und Commit-Historie sind für jeden lesbar, deshalb gehören
Zugangsdaten niemals in einen Commit. Die Historie wurde vor dem
Öffentlichmachen auf die GitHub-Noreply-Adresse umgeschrieben; Commits laufen
weiterhin darüber (im Repo als `user.email` gesetzt).

Die Datei `CNAME` hat GitHub selbst angelegt — nicht löschen, sonst fällt die
Custom Domain aus.

## Schriften und deren Lizenz

`assets/fonts/` enthält **Mosher** (© 2026 Pixelbuddha) und **GC Furion**
(© 2025 Glyphonic) als `.woff2`. Beide sind kommerzielle Schriften und wurden
ohne Lizenzdatei geliefert.

Zwei Punkte sind vor weiterer kommerzieller Nutzung zu klären:

1. Deckt die erworbene Lizenz **Webfont-Einbettung** ab? Reine Desktop-Lizenzen
   erlauben nur die Nutzung in Grafikprogrammen, nicht das Ausliefern per
   `@font-face`. Manche Webfont-Lizenzen sind zusätzlich auf eine Zahl von
   Seitenaufrufen im Monat begrenzt.
2. Dieses Repository ist **öffentlich**. Die Schriftdateien sind damit für jeden
   herunterladbar — das geht über das bloße Ausliefern an Website-Besucher
   hinaus und ist in manchen Lizenzen ausgeschlossen.

Falls einer der Punkte nicht passt: Dateien aus `assets/fonts/` entfernen, die
`@font-face`-Blöcke in `assets/css/style.css` löschen. Die Ersatzschriften in
`--font-titel` und `--font-text` greifen dann automatisch, die Seite bleibt
funktionsfähig.
