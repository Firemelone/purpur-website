#!/usr/bin/env python3
"""
Macht aus dem Website-Loop der Ausgabe den Hero-Hintergrund.

Der Schnitt selbst entsteht nicht hier, sondern auf Luas Rechner:

    "/Volumes/Silver T7/PURPUR/Posts/0-Announcement Reel #2/web_cut.py"
    shots_web.txt   — Schnittliste, 160 BPM, mit Farbkorrektur und Effekten

Dieses Skript nimmt nur dessen Ergebnis, zieht es auf dreifaches Tempo und
kodiert es fuer das Netz. Farbkorrektur und Effekte stecken bereits in der
Vorlage — deshalb liegt auf dem Videoelement im Hero auch kein CSS-Filter.

Aufruf:  python3 tools/build-hero-video.py /pfad/zu/purpur1-loop-1080.mp4
"""

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
ZIEL = REPO / "Media" / "Hero"

# Dreifaches Tempo: aus 36 Sekunden werden 12. Bei zweifachem Tempo waere die
# Datei rund 8 MB schwer — fuer einen Hintergrund, der sofort laedt, zu viel.
TEMPO = 3.0
BILDRATE = 30
# CRF 26 trifft bei dieser Vorlage knapp 4 Mbit/s und liegt damit ueber der
# Rate des Masters (3,24). Mehr Rate verbessert nichts, was nicht schon in der
# Vorlage fehlt. tune=film, damit der Encoder die Koernung nicht glattbuegelt.
CRF = 26


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    quelle = pathlib.Path(sys.argv[1])
    if not quelle.exists():
        sys.exit(f"fehlt: {quelle}")
    ZIEL.mkdir(parents=True, exist_ok=True)
    film = ZIEL / "hero-montage.mp4"

    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(quelle), "-an",
        "-vf", f"setpts={1 / TEMPO:.4f}*PTS,fps={BILDRATE}",
        "-c:v", "libx264", "-crf", str(CRF), "-preset", "veryslow",
        "-tune", "film", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-level", "4.1", "-g", str(BILDRATE * 2), "-movflags", "+faststart",
        "-y", str(film),
    ], check=True)

    # Plakatbild: steht, bis das Video laeuft, und bleibt bei reduzierter
    # Bewegung dauerhaft stehen.
    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(film), "-frames:v", "1",
        "-vf", "scale=960:-2", "-q:v", "82", "-y", str(ZIEL / "hero-still.webp"),
    ], check=True)

    print(f"Fertig: {film.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
