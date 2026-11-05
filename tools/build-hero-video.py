#!/usr/bin/env python3
"""
Macht aus dem Website-Loop der Ausgabe den Hero-Hintergrund.

Der Schnitt selbst entsteht nicht hier, sondern auf Luas Rechner:

    "/Volumes/Silver T7/PURPUR/Posts/0-Announcement Reel #2/web_cut.py"
    shots_web.txt   — Schnittliste, 160 BPM, mit Farbkorrektur und Effekten

Dieses Skript schneidet daraus nur noch einen Ausschnitt heraus. Tempo und
Bilddaten bleiben unangetastet: bei Sekunde 12 sitzt ein Keyframe, deshalb
laesst sich der Abschnitt ohne Neukodierung herauskopieren. Farbkorrektur und Effekte stecken bereits in der
Vorlage — deshalb liegt auf dem Videoelement im Hero auch kein CSS-Filter.

Aufruf:  python3 tools/build-hero-video.py /pfad/zu/purpur1-loop-1080.mp4
"""

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
ZIEL = REPO / "Media" / "Hero"

# Ausschnitt: 12 bis 30 Sekunden sind erster Druck, Atempause, zweiter
# Aufbau und Hoehepunkt. Die Grenzen liegen auf Taktschlaegen (160 BPM, ein
# Schlag = 0,375 s), damit der Sprung am Ende der Schleife nicht auffaellt.
# In Frames statt Sekunden, weil -t auf die naechste ganze Gruppe aufrundet
# und die Schleife dann zwei Bilder zu lang waere.
AB, FRAMES = 12.0, 540
BILDRATE = 30


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    quelle = pathlib.Path(sys.argv[1])
    if not quelle.exists():
        sys.exit(f"fehlt: {quelle}")
    ZIEL.mkdir(parents=True, exist_ok=True)
    film = ZIEL / "hero-montage.mp4"

    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error",
        "-ss", str(AB), "-i", str(quelle), "-an",
        "-frames:v", str(FRAMES), "-c:v", "copy",
        "-movflags", "+faststart", "-y", str(film),
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
