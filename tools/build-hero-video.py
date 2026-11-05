#!/usr/bin/env python3
"""
Baut den Hero-Hintergrund aus Mitschnitten neu auf.

Ein einziges Video statt vieler Einzeldateien: ein Dekoder, ein Ladevorgang,
und die Schnitte stecken schon drin. Die Clips laufen in Zeitlupe und wechseln
im Zwei-Sekunden-Takt — der Kanalwechsel-Streifen blitzt alle vier Sekunden
auf und trifft damit jeden zweiten Schnitt.

Quellen liegen in QUELLE, die Auswahl steht in SCHNITT. Aufruf:
    python3 tools/build-hero-video.py
"""

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
QUELLE = pathlib.Path.home() / "Documents" / "Claude" / "purpur-videos"
ZIEL = REPO / "Media" / "Hero"

# 4:5 ist der Kompromiss: die meisten Aufnahmen sind hochkant vom Handy.
# object-fit: cover nimmt am Rechner den mittleren Streifen und am Handy die
# Mitte in der Breite. Volles Hochformat waere am Rechner zu stark
# beschnitten, Querformat auf dem Handy.
BREITE, HOEHE = 1080, 1350
TAKT = 2.0          # Sekunden je Schnitt, im Ausgabetempo
BILDRATE = 30

# Datei, Startzeit in der Quelle, Tempofaktor.
# Die Quelldauer ergibt sich aus TAKT / Tempofaktor.
# Faktor 2.0 nur bei 60-Bilder-Quellen — daraus werden saubere 30.
# Bei 30-Bilder-Quellen wuerde 2.0 auf 15 Bilder fallen und ruckeln, deshalb
# dort 1.7 und Zwischenbilder von minterpolate.
SCHNITT = [
    ("Alexander_Performance.mp4",   0.70, 2.0),
    ("Bene_Piggy_Performance.mp4",  5.25, 1.7),
    ("Alexander_Performance.mp4",   1.45, 2.0),
    ("FLOSS_Performance.mp4",       2.00, 1.7),
    ("Bene_Piggy_Performance.mp4",  4.05, 1.7),
    ("Alexander_Performance.mp4",   4.10, 2.0),
]

# Farbkorrektur fest ins Bild statt als CSS-Filter: ein filter auf einem
# laufenden Video zwingt den Browser, jedes dekodierte Bild noch einmal
# durchzurechnen. Entspricht grayscale(.12) contrast(1.12) saturate(1.25)
# brightness(.88) aus dem frueheren Stylesheet.
GRADE = ("eq=saturation=1.10:contrast=1.12,"
         "colorlevels=romax=0.88:gomax=0.88:bomax=0.88")
# Gegen die Weichheit des Aufnahmematerials, das durchweg aus dunklen
# Handyaufnahmen besteht.
SCHAERFE = "unsharp=5:5:0.7:5:5:0.0"


def lauf(*args):
    subprocess.run(args, check=True)


def hochkant(datei):
    """Hochformat auch dann erkennen, wenn es nur in der Drehung steckt."""
    roh = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-show_entries", "side_data=rotation",
         "-of", "default=nw=1:nk=1", str(datei)],
        capture_output=True, text=True, check=True).stdout.split()
    b, h = int(roh[0]), int(roh[1])
    dreh = abs(int(roh[2])) if len(roh) > 2 else 0
    if dreh in (90, 270):
        b, h = h, b
    return h > b


def main():
    if not QUELLE.is_dir():
        sys.exit(f"Quellordner fehlt: {QUELLE}")
    ZIEL.mkdir(parents=True, exist_ok=True)
    arbeit = ZIEL / "_bau"
    arbeit.mkdir(exist_ok=True)

    liste = arbeit / "liste.txt"
    zeilen = []
    for n, (name, start, tempo) in enumerate(SCHNITT, 1):
        quelle = QUELLE / name
        if not quelle.exists():
            sys.exit(f"fehlt: {quelle}")
        zuschnitt = ("crop=in_w:in_w*5/4" if hochkant(quelle)
                     else f"scale=-2:{HOEHE},crop={BREITE}:{HOEHE}")
        zeit = (f"setpts={tempo}*PTS,fps={BILDRATE}" if tempo == 2.0 else
                f"setpts={tempo}*PTS,minterpolate=fps={BILDRATE}:mi_mode=mci:"
                f"mc_mode=aobmc:vsbmc=1")
        ziel = arbeit / f"clip-{n}.mp4"
        lauf("ffmpeg", "-nostdin", "-v", "error", "-ss", str(start),
             "-t", f"{TAKT / tempo:.3f}", "-i", str(quelle), "-an",
             "-vf", f"{zuschnitt},scale={BREITE}:{HOEHE},{GRADE},{SCHAERFE},{zeit}", "-c:v", "libx264", "-crf", "23",
             "-preset", "slow", "-pix_fmt", "yuv420p", "-y", str(ziel))
        zeilen.append(f"file '{ziel.name}'")
        print(f"Clip {n}: {ziel.stat().st_size // 1024} KB")

    liste.write_text("\n".join(zeilen) + "\n")

    film = ZIEL / "hero-montage.mp4"
    lauf("ffmpeg", "-nostdin", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(liste), "-an", "-c:v", "libx264", "-crf", "22",
         "-preset", "veryslow", "-tune", "film", "-pix_fmt", "yuv420p", "-profile:v", "high",
         "-level", "4.1", "-g", str(BILDRATE * 2), "-movflags", "+faststart",
         "-y", str(film))

    # Plakatbild: steht, bis das Video laeuft, und bleibt bei reduzierter
    # Bewegung dauerhaft stehen.
    lauf("ffmpeg", "-nostdin", "-v", "error", "-i", str(film), "-frames:v", "1",
         "-vf", "scale=640:-2", "-q:v", "80", "-y", str(ZIEL / "hero-still.webp"))

    for d in arbeit.iterdir():
        d.unlink()
    arbeit.rmdir()
    print(f"\nFertig: {film.stat().st_size // 1024} KB, "
          f"{len(SCHNITT) * TAKT:.0f} s, {BREITE}x{HOEHE}")


if __name__ == "__main__":
    main()
