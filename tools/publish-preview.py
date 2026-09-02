#!/usr/bin/env python3
"""Den preview-Zweig als Unterordner nach main veroeffentlichen.

Die Seite liegt dann unter purpur.berlin/preview/ und ist ohne Konto
erreichbar, waehrend die eigentliche Startseite unberuehrt bleibt.

Der Haken an einem Unterordner: die Seite verlinkt alles absolut
(/styles.css, /Media/...). Unter /preview/ zeigen solche Pfade auf die
Wurzel der Domain und laufen ins Leere. Darum schreibt dieses Werkzeug
in der Kopie alle absoluten Pfade auf relative um. Das Original auf dem
preview-Zweig bleibt unveraendert — dort ist absolut ja richtig.

Aufruf:  python3 tools/publish-preview.py
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
ZWEIG = "preview"
ORDNER = "preview"

# Die Vorschau soll nicht in Suchmaschinen auftauchen — aber sehr wohl
# abrufbar bleiben. Frueher stand hier ein "Disallow: /preview/", und genau
# das war falsch: Disallow verbietet nicht das Indexieren, sondern das
# Abrufen. Damit blieben auch alle Linkvorschauen leer, denn Messenger holen
# sich die Seite ueber dieselben Regeln. Nur eine Handvoll namentlich
# freigegebener Dienste kam durch; iMessage, Signal, Instagram, LinkedIn und
# Teams sahen weder Text noch Bild.
#
# Herausgehalten wird die Vorschau jetzt ueber "noindex" in den Seiten selbst
# (siehe nicht_indexieren). Das erlaubt das Abrufen und verbietet nur die
# Aufnahme in den Index — also genau das, was gemeint war.
ROBOTS = """User-agent: *
Allow: /
"""

# Wird in jede Vorschauseite eingesetzt.
NOINDEX = '<meta name="robots" content="noindex, nofollow" />'


def lauf(*args, cwd=None, still=False):
    e = subprocess.run(args, cwd=cwd or REPO, capture_output=True, text=True)
    if e.returncode and not still:
        sys.exit(f"Fehlgeschlagen: {' '.join(args)}\n{e.stderr}")
    return e.stdout.strip()


def relativ(ordner: pathlib.Path) -> int:
    """Absolute Pfade in der Kopie auf relative umschreiben."""
    geaendert = 0
    for p in ordner.rglob("*"):
        if p.suffix not in (".html", ".css", ".js") or not p.is_file():
            continue
        alt = p.read_text()
        neu = alt.replace('href="/"', 'href="index.html"')
        neu = re.sub(r'(src|href|poster)="/(?!/)', r'\1="', neu)
        # srcset ist eine Liste aus "Adresse Breitenangabe", durch Kommas
        # getrennt. Die einfache Ersetzung oben fasst nur den ersten Eintrag
        # und laesst die uebrigen absolut stehen — genau daran ist die
        # Diashow in der Vorschau schon einmal ins Leere gelaufen.
        neu = re.sub(
            r'srcset="([^"]*)"',
            lambda m: 'srcset="' + re.sub(r'(^|,\s*)/(?!/)', r'\1', m.group(1)) + '"',
            neu,
        )
        neu = neu.replace('url("/', 'url("')
        # Die Linkvorschau braucht volle Adressen, relative Pfade werten
        # viele Scraper nicht aus. Die zeigen bisher auf die Wurzel und
        # muessen auf den Unterordner umgebogen werden.
        neu = neu.replace('content="https://purpur.berlin/',
                          f'content="https://purpur.berlin/{ORDNER}/')
        if neu != alt:
            p.write_text(neu)
            geaendert += 1
    return geaendert


def nicht_indexieren(ordner: pathlib.Path) -> int:
    """noindex in jede Vorschauseite setzen.

    Haelt die Vorschau aus Suchergebnissen heraus, laesst sie aber abrufbar —
    anders als eine Sperre in der robots.txt, die auch Linkvorschauen
    verhungern liesse.
    """
    gesetzt = 0
    for p in sorted(ordner.rglob("*.html")):
        text = p.read_text()
        if 'name="robots"' in text:
            continue
        # Direkt hinter das erste <meta>, damit es weit oben im Kopf steht:
        # Manche Scraper lesen nur die ersten Kilobytes.
        marke = '<meta charset="UTF-8" />'
        if marke not in text:
            sys.exit(f"Kein <meta charset> in {p.name} gefunden — abgebrochen.")
        p.write_text(text.replace(marke, f"{marke}\n{NOINDEX}", 1))
        gesetzt += 1
    return gesetzt


def pruefe(ordner: pathlib.Path) -> None:
    """Abbrechen, wenn noch ein Pfad auf die Domainwurzel zeigt.

    Unter /preview/ laeuft jeder verbliebene absolute Pfad ins Leere. Lieber
    hier abbrechen als eine halb kaputte Vorschau veroeffentlichen.
    """
    treffer = []
    for p in sorted(ordner.rglob("*")):
        if p.suffix not in (".html", ".css", ".js") or not p.is_file():
            continue
        for n, zeile in enumerate(p.read_text().splitlines(), 1):
            for fund in re.findall(r'(?:[a-zA-Z-]+="|url\(")/(?!/)[^"\s]*', zeile):
                treffer.append(f"  {p.relative_to(ordner)}:{n}  {fund[:80]}")
    if treffer:
        sys.exit("Es zeigen noch Pfade auf die Domainwurzel:\n" + "\n".join(treffer[:20]))


def main() -> None:
    offen = lauf("git", "status", "--porcelain")
    if offen:
        sys.exit("Es liegen ungesicherte Aenderungen vor. Erst committen.\n" + offen)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        inhalt, baum = tmp / "inhalt", tmp / "baum"
        inhalt.mkdir()

        # Stand des preview-Zweigs auspacken
        tar = subprocess.run(["git", "archive", ZWEIG], cwd=REPO, capture_output=True)
        subprocess.run(["tar", "-x", "-C", str(inhalt)], input=tar.stdout, check=True)

        # was nur die Entwicklung betrifft, gehoert nicht in die Vorschau
        for weg in ("tools", "CLAUDE.md", "README.md", "CNAME", ".gitignore"):
            ziel = inhalt / weg
            if ziel.is_dir():
                shutil.rmtree(ziel)
            elif ziel.exists():
                ziel.unlink()

        n = relativ(inhalt)
        m = nicht_indexieren(inhalt)
        pruefe(inhalt)
        print(f"{n} Dateien auf relative Pfade umgeschrieben, keine Wurzelpfade uebrig.")
        print(f"{m} Seiten auf noindex gesetzt.")

        # main in einem eigenen Arbeitsbaum, damit der preview-Zweig
        # hier ausgecheckt bleiben kann
        lauf("git", "fetch", "-q", "origin", "main")
        lauf("git", "worktree", "add", "-q", "--detach", str(baum), "origin/main")
        try:
            ziel = baum / ORDNER
            if ziel.exists():
                shutil.rmtree(ziel)
            shutil.copytree(inhalt, ziel)
            (baum / "robots.txt").write_text(ROBOTS)

            lauf("git", "add", "-A", cwd=baum)
            if not lauf("git", "status", "--porcelain", cwd=baum):
                print("Nichts geaendert, die Vorschau ist schon aktuell.")
                return
            sha = lauf("git", "rev-parse", ZWEIG)[:7]
            lauf("git", "commit", "-q", "-m",
                 f"Vorschau aktualisiert (preview {sha})", cwd=baum)
            lauf("git", "push", "-q", "origin", "HEAD:main", cwd=baum)
        finally:
            lauf("git", "worktree", "remove", "--force", str(baum), still=True)

    print("Veroeffentlicht: https://purpur.berlin/preview/")
    print("Es dauert ein bis zwei Minuten, bis GitHub Pages das ausliefert.")


if __name__ == "__main__":
    main()
