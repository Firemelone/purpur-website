#!/usr/bin/env python3
"""Den Stand des preview-Zweigs auf die Live-Seite bringen.

Setzt den Inhalt von main auf den von preview. Zwei Dinge bleiben dabei
stehen, weil sie nur auf main existieren:

  robots.txt   sperrt die Vorschau gegen Suchmaschinen
  preview/     der Unterordner, dessen Adresse im Team herumgereicht wurde

Anders als bei der Vorschau werden hier KEINE Pfade umgeschrieben: Auf der
Wurzel der Domain sind die absoluten Pfade genau richtig.

Aufruf:  python3 tools/go-live.py
"""

import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
ZWEIG = "preview"
BLEIBT = ("robots.txt", "preview", ".git")


def lauf(*args, cwd=None, still=False):
    e = subprocess.run(args, cwd=cwd or REPO, capture_output=True, text=True)
    if e.returncode and not still:
        sys.exit(f"Fehlgeschlagen: {' '.join(args)}\n{e.stderr}")
    return e.stdout.strip()


def main() -> None:
    offen = lauf("git", "status", "--porcelain")
    if offen:
        sys.exit("Es liegen ungesicherte Aenderungen vor. Erst committen.\n" + offen)

    with tempfile.TemporaryDirectory() as tmp:
        baum = pathlib.Path(tmp) / "main"
        lauf("git", "fetch", "-q", "origin", "main")
        lauf("git", "worktree", "add", "-q", "--detach", str(baum), "origin/main")
        try:
            for eintrag in baum.iterdir():
                if eintrag.name in BLEIBT:
                    continue
                if eintrag.is_dir():
                    shutil.rmtree(eintrag)
                else:
                    eintrag.unlink()

            tar = subprocess.run(["git", "archive", ZWEIG], cwd=REPO, capture_output=True)
            subprocess.run(["tar", "-x", "-C", str(baum)], input=tar.stdout, check=True)

            # Ohne CNAME faellt die eigene Domain aus und die Seite ist nur
            # noch unter firemelone.github.io erreichbar.
            cname = baum / "CNAME"
            if not cname.exists() or cname.read_text().strip() != "purpur.berlin":
                sys.exit("CNAME fehlt oder stimmt nicht — abgebrochen.")

            lauf("git", "add", "-A", cwd=baum)
            if not lauf("git", "status", "--porcelain", cwd=baum):
                print("Nichts geaendert, die Live-Seite ist schon auf diesem Stand.")
                return

            sha = lauf("git", "rev-parse", ZWEIG)[:7]
            print("Diese Dateien aendern sich auf der Live-Seite:")
            print(lauf("git", "diff", "--cached", "--stat", cwd=baum))
            lauf("git", "commit", "-q", "-m", f"Seite live schalten (preview {sha})", cwd=baum)
            lauf("git", "push", "-q", "origin", "HEAD:main", cwd=baum)
        finally:
            lauf("git", "worktree", "remove", "--force", str(baum), still=True)

    print("\nLive: https://purpur.berlin")
    print("Es dauert ein bis zwei Minuten, bis GitHub Pages das ausliefert.")


if __name__ == "__main__":
    main()
