# purpur-website

Website für **purpur.berlin**. Statisches HTML/CSS/JS, kein Framework, kein
Build-Schritt: was im Repo liegt, ist exakt das, was später ausgeliefert wird.

## Stand

- [x] Repo angelegt und mit Claude Code verbunden
- [x] Technik entschieden: statisches HTML/CSS/JS, Hosting über GitHub Pages
- [x] DNS bei IONOS auf GitHub Pages gestellt (autoritativ geprüft, siehe unten)
- [x] Grundgerüst der Seite: Startseite, Impressum, Datenschutz, Stylesheet
- [ ] Inhalt der Startseite — aktuell nur ein Platzhalter
- [ ] Impressum und Datenschutz ausfüllen (Pflicht vor dem Livegang)
- [ ] Hosting einschalten — Settings → Pages, bewusst noch **aus**

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

**GitHub Pages ist ausgeschaltet**, die Domain führt deshalb vorerst auf einen
GitHub-404 — so gewollt, siehe `CLAUDE.md`. Die Seite liegt in der Repo-Wurzel,
damit der Livegang ohne Actions-Workflow auskommt.

Das Repo ist seit dem 19.08.2026 **öffentlich** — Voraussetzung dafür, dass
GitHub Pages ohne bezahlten Plan nutzbar ist. Quelltext und Commit-Historie sind
damit für jeden lesbar; die Historie wurde vorher auf die GitHub-Noreply-Adresse
umgeschrieben, damit keine private Mailadresse darin steht. Commits deshalb
weiterhin mit der Noreply-Adresse anlegen (im Repo als `user.email` gesetzt).

Zum Livegang fehlt dann nur noch:

1. Impressum und Datenschutz ausfüllen — Pflicht, siehe `CLAUDE.md`
2. Settings → Pages → Source: „Deploy from a branch", Branch `main`, Ordner `/`
3. Custom domain: `purpur.berlin` — GitHub legt die `CNAME`-Datei selbst an
4. „Enforce HTTPS" anhaken, sobald das Zertifikat ausgestellt ist (dauert ein
   paar Minuten)
