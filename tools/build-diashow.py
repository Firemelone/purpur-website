#!/usr/bin/env python3
"""
Baut die Hero-Diashow aus ~/Documents/Claude/purpur-diashow neu auf.

Wandelt die Originale nach WebP, traegt sie in index.html ein und schreibt den
dazugehoerigen CSS-Block neu. Die Uebergangszeiten haengen an der Anzahl der
Bilder, deshalb wird das CSS mitgeneriert und nicht von Hand gepflegt.

Aufruf:  python3 tools/build-diashow.py
"""

import pathlib
import re
import subprocess
import sys
import tempfile

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow fehlt.  python3 -m pip install --user Pillow")

REPO = pathlib.Path(__file__).resolve().parent.parent
QUELLE = pathlib.Path.home() / "Documents" / "Claude" / "purpur-diashow"
ZIEL = REPO / "Media" / "Diashow"

# Zwei Groessen je Bild. Ein Handy braucht bei dreifacher Pixeldichte rund
# 1200 echte Pixel Breite, ein Rechner mit Retina-Schirm ueber 2800. Eine
# einzige Datei kann beides nicht: 1600 Pixel wurden auf dem Rechner um mehr
# als das Doppelte hochgerechnet und sahen matschig aus, waehrend eine grosse
# Datei fuers Handy reine Verschwendung waere. Der Browser sucht sich per
# srcset selbst die passende aus und laedt nur die.
#
# Statt einer festen Zielgroesse in Bytes gilt ein Budget je Pixel. Sonst
# bekommt ein hochkantes Bild mit mehr Flaeche automatisch weniger Qualitaet
# als ein flaches — genau daran sind vorher zwei koernige Fotos auf die
# schlechteste Stufe gerutscht.
GROESSEN = (
    (1600, 0.130),   # Handys und einfache Bildschirme
    (2200, 0.100),   # Retina-Rechner; grob koennen wir hier sparen, weil
)                    # Artefakte auf mehr Pixeln weniger auffallen
MINQ = 72          # darunter wird die Kompression sichtbar
SEKUNDEN_PRO_BILD = 4

# Helligkeitsausgleich. Die Bilder kommen aus ganz unterschiedlichen Quellen —
# Infrarot-Aufnahmen sind fast weiss, Latex-Motive fast schwarz. Der feste
# Abdunklungsverlauf im Hero kann beides nicht gleichzeitig tragen: was fuer
# das helle Bild reicht, verschluckt das dunkle komplett. Darum bekommt jedes
# Bild einen eigenen Faktor, der es in die Naehe des Zielwerts rueckt.
ZIEL_HELLIGKEIT = 95    # mittlere Leuchtdichte (0-255) in der Logo-Zone
HELLIGKEIT_MIN = 0.55   # Grenzen, damit ein Extrembild nicht flach wird
HELLIGKEIT_MAX = 1.9

MARKE_A = "  <!-- DIASHOW-ANFANG (erzeugt von tools/build-diashow.py) -->"
MARKE_E = "  <!-- DIASHOW-ENDE -->"
CSS_A = "/* DIASHOW-ANFANG (erzeugt von tools/build-diashow.py) */"
CSS_E = "/* DIASHOW-ENDE */"


def konvertiere(quelle: pathlib.Path, ziel: pathlib.Path,
                maxdim: int, bpp: float) -> tuple[int, int, int]:
    """Nach WebP wandeln. Gibt Qualitaet, Breite und Hoehe zurueck.

    Hochgerechnet wird nie: ist die Vorlage kleiner als maxdim, bleibt sie
    wie sie ist. Kuenstlich aufgeblasene Pixel bringen keine Schaerfe, nur
    Dateigroesse.
    """
    im = Image.open(quelle)
    w, h = im.size
    faktor = min(1.0, maxdim / max(w, h))
    breite, hoehe = round(w * faktor), round(h * faktor)
    eingabe = quelle
    temp = None
    if faktor < 1.0:
        temp = pathlib.Path(tempfile.mkstemp(suffix=".png")[1])
        im.convert("RGB").resize((breite, hoehe), Image.LANCZOS).save(temp)
        eingabe = temp
    budget = breite * hoehe * bpp
    for q in (88, 84, 80, 76, MINQ):
        subprocess.run(
            ["cwebp", "-q", str(q), "-m", "6", "-quiet", str(eingabe), "-o", str(ziel)],
            check=True,
        )
        if ziel.stat().st_size <= budget:
            break
    if temp:
        temp.unlink()
    return q, breite, hoehe


def helligkeit(ziel: pathlib.Path) -> float:
    """Faktor, der die Logo-Zone des Bildes auf ZIEL_HELLIGKEIT bringt."""
    im = Image.open(ziel).convert("L")
    w, h = im.size
    zone = im.crop((int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.7)))
    px = list(zone.getdata())
    mittel = sum(px) / len(px)
    if mittel <= 0:
        return HELLIGKEIT_MAX
    return round(min(HELLIGKEIT_MAX, max(HELLIGKEIT_MIN, ZIEL_HELLIGKEIT / mittel)), 2)


def bild_block(eintraege: list[dict]) -> str:
    """Das <img> mit srcset: der Browser waehlt selbst die passende Groesse.

    sizes="100vw" sagt ihm, dass das Bild den ganzen Schirm fuellt. Zusammen
    mit der Pixeldichte des Geraets rechnet er sich daraus die noetige Breite
    aus und laedt genau eine der angebotenen Dateien.
    """
    zeilen = [MARKE_A, '  <div class="hero__slideshow" aria-hidden="true">']
    for i, e in enumerate(eintraege):
        prio = "high" if i == 0 else "low"
        srcset = ", ".join(f"/Media/Diashow/{n} {b}w" for n, b in e["fassungen"])
        zeilen.append(
            f'      <img class="hero__slide" src="/Media/Diashow/{e["fassungen"][0][0]}" '
            f'srcset="{srcset}" sizes="100vw" '
            f'width="{e["breite"]}" height="{e["hoehe"]}" alt="" '
            f'style="--slide-hell: {e["hell"]}" '
            f'fetchpriority="{prio}" decoding="async" />'
        )
    zeilen += ["    </div>", MARKE_E]
    return "\n".join(zeilen)


def css_block(anzahl: int) -> str:
    """Uebergaenge so setzen, dass nie Schwarz durchscheint.

    Jedes Bild blendet genau dann auf, wenn das vorherige abblendet. Die
    Ausblendphase reicht deshalb ueber den eigenen Anteil hinaus in den des
    naechsten Bildes hinein — sonst klafft dazwischen eine schwarze Luecke.
    """
    dauer = anzahl * SEKUNDEN_PRO_BILD
    anteil = 100 / anzahl          # Anteil eines Bildes am Durchlauf
    blende = min(anteil * 0.3, 2)  # Dauer der Blende in Prozent
    zeilen = [
        CSS_A,
        "@media (prefers-reduced-motion: no-preference) {",
        f"  .hero__slide {{ animation: hero-slideshow {dauer}s linear infinite; }}",
    ]
    for i in range(anzahl):
        zeilen.append(
            f"  .hero__slide:nth-child({i + 1}) {{ animation-delay: {i * SEKUNDEN_PRO_BILD}s; }}"
        )
    zeilen += [
        "}",
        "@keyframes hero-slideshow {",
        "  0%              { opacity: 0; }",
        f"  {blende:.3f}%   {{ opacity: 1; }}",
        f"  {anteil:.3f}%   {{ opacity: 1; }}",
        f"  {anteil + blende:.3f}%   {{ opacity: 0; }}",
        "  100%            { opacity: 0; }",
        "}",
        CSS_E,
    ]
    return "\n".join(zeilen)


def ersetze(text: str, anfang: str, ende: str, neu: str, datei: str) -> str:
    if anfang not in text or ende not in text:
        sys.exit(f"Markierungen in {datei} nicht gefunden. Wurden sie geloescht?")
    vor = text[: text.index(anfang)]
    nach = text[text.index(ende) + len(ende):]
    return vor + neu + nach


def main() -> None:
    if not QUELLE.is_dir():
        sys.exit(f"Quellordner fehlt: {QUELLE}")

    bilder = sorted(
        p for p in QUELLE.iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")
    )
    if not bilder:
        sys.exit(f"Keine Bilder in {QUELLE}. Lies die README.txt dort.")

    print(f"{len(bilder)} Bilder gefunden.\n")

    ZIEL.mkdir(parents=True, exist_ok=True)
    for alt in ZIEL.glob("*.webp"):
        alt.unlink()

    eintraege = []
    je_fassung = [0] * len(GROESSEN)
    for p in bilder:
        fassungen, zeile = [], f"  {p.name:<26}"
        for stufe, (maxdim, bpp) in enumerate(GROESSEN):
            anhang = "" if stufe == 0 else f"@{maxdim}"
            ziel = ZIEL / f"{p.stem}{anhang}.webp"
            q, b, h = konvertiere(p, ziel, maxdim, bpp)
            groesse = ziel.stat().st_size
            je_fassung[stufe] += groesse
            fassungen.append((ziel.name, b))
            zeile += f"  {b}x{h} q{q} {groesse / 1024:4.0f}KB"
            if stufe == 0:
                erste = (b, h, helligkeit(ziel))
        # Doppelte Breiten wuerden das srcset unbrauchbar machen: der Browser
        # koennte die Fassungen nicht auseinanderhalten. Passiert, wenn die
        # Vorlage kleiner ist als die groessere Stufe.
        fassungen = list({b: (n, b) for n, b in fassungen}.values())
        eintraege.append({"fassungen": fassungen, "breite": erste[0],
                          "hoehe": erste[1], "hell": erste[2]})
        print(zeile + f"  Helligkeit x{erste[2]}")

    html = REPO / "index.html"
    css = REPO / "styles.css"
    html.write_text(ersetze(html.read_text(), MARKE_A, MARKE_E, bild_block(eintraege), "index.html"))
    css.write_text(ersetze(css.read_text(), CSS_A, CSS_E, css_block(len(eintraege)), "styles.css"))

    print()
    for (maxdim, _), summe in zip(GROESSEN, je_fassung):
        print(f"Fassung bis {maxdim}px: {summe / 1048576:.2f} MB "
              f"— so viel laedt ein Geraet, das diese Stufe waehlt.")
    print(f"Ein Durchlauf dauert {len(eintraege) * SEKUNDEN_PRO_BILD} Sekunden.")
    print("index.html und styles.css sind aktualisiert. Jetzt pruefen und pushen.")


if __name__ == "__main__":
    main()
