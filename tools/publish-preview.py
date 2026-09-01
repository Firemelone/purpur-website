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

ROBOTS = """User-agent: *
Disallow: /preview/
"""


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
        neu = re.sub(r'(src|href)="/(?!/)', r'\1="', neu)
        neu = neu.replace('url("/', 'url("')
        if neu != alt:
            p.write_text(neu)
            geaendert += 1
    return geaendert


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
        print(f"{n} Dateien auf relative Pfade umgeschrieben.")

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
