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
# Je Stufe: laengste Kante, Budget je Pixel, unterste Qualitaet, Pixeldeckel.
#
# Der Pixeldeckel ist wegen der Hochformate noetig. Ein hochkantes Bild muss
# auf einem querformatigen Schirm ueber die Breite skaliert werden — die volle
# Hoehe wird nie gezeigt, zaehlt aber voll bei Dateigroesse und Speicher. Ohne
# Deckel wuerde ein Hochformat in der groessten Stufe ueber 12 Megapixel haben
# und allein 1,7 MB wiegen.
#
# Die unterste Qualitaet sinkt mit der Groesse: Bei 3200 Pixeln liegen die
# Kompressionsartefakte unter dem, was auf dem Schirm noch aufgeloest wird,
# und die koernigen Aufnahmen brauchen sonst absurd viel Platz.
GROESSEN = (
    (1600, 0.130, 72, None),        # Handys und einfache Bildschirme
    (2400, 0.095, 68, 4_200_000),   # Mittelgrosse Schirme
    (3200, 0.075, 60, 6_200_000),   # Retina-Rechner: ein 1440er Schirm
)                                   # braucht 2880 echte Pixel Breite
SEKUNDEN_PRO_BILD = 4
# Ablauf des Zaps in Millisekunden: Aufblitzen ueber die volle Hoehe,
# Zusammenfallen zur Linie, Erloeschen.
ZAP_AUF_MS = 45
ZAP_LINIE_MS = 55
ZAP_GESAMT_MS = 170

# Helligkeitsausgleich. Die Bilder kommen aus ganz unterschiedlichen Quellen —
# Infrarot-Aufnahmen sind fast weiss, Latex-Motive fast schwarz. Der feste
# Abdunklungsverlauf im Hero kann beides nicht gleichzeitig tragen: was fuer
# das helle Bild reicht, verschluckt das dunkle komplett. Darum bekommt jedes
# Bild einen eigenen Faktor, der es in die Naehe des Zielwerts rueckt.
ZIEL_HELLIGKEIT = 95    # mittlere Leuchtdichte (0-255) in der Logo-Zone
HELLIGKEIT_MIN = 0.55   # Grenzen, damit ein Extrembild nicht flach wird
HELLIGKEIT_MAX = 1.9
LICHTER_GRENZE = 235   # so hell duerfen die hellsten 5 % hoechstens werden

MARKE_A = "  <!-- DIASHOW-ANFANG (erzeugt von tools/build-diashow.py) -->"
MARKE_E = "  <!-- DIASHOW-ENDE -->"
CSS_A = "/* DIASHOW-ANFANG (erzeugt von tools/build-diashow.py) */"
CSS_E = "/* DIASHOW-ENDE */"


def konvertiere(quelle: pathlib.Path, ziel: pathlib.Path, maxdim: int,
                bpp: float, minq: int, deckel) -> tuple[int, int, int]:
    """Nach WebP wandeln. Gibt Qualitaet, Breite und Hoehe zurueck.

    Hochgerechnet wird nie: ist die Vorlage kleiner als maxdim, bleibt sie
    wie sie ist. Kuenstlich aufgeblasene Pixel bringen keine Schaerfe, nur
    Dateigroesse.
    """
    im = Image.open(quelle)
    w, h = im.size
    faktor = min(1.0, maxdim / max(w, h))
    if deckel and w * h * faktor * faktor > deckel:
        faktor = (deckel / (w * h)) ** 0.5
    breite, hoehe = round(w * faktor), round(h * faktor)
    eingabe = quelle
    temp = None
    if faktor < 1.0:
        temp = pathlib.Path(tempfile.mkstemp(suffix=".png")[1])
        im.convert("RGB").resize((breite, hoehe), Image.LANCZOS).save(temp)
        eingabe = temp
    budget = breite * hoehe * bpp
    stufen = [q for q in (88, 84, 80, 76, 72, 68, 64, minq) if q >= minq]
    for q in stufen:
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
    """Faktor, der die Logo-Zone des Bildes auf ZIEL_HELLIGKEIT bringt.

    Der Mittelwert allein reicht nicht: Bei einem Motiv, das absichtlich auf
    schwarzem Grund steht, zieht die schwarze Flaeche ihn nach unten, obwohl
    das Motiv selbst schon hell ist. Aufhellen wuerde dann nur die Lichter
    ausbrennen, ohne im Schwarz etwas sichtbar zu machen. Darum begrenzt ein
    zweiter Wert den Faktor: die hellsten fuenf Prozent duerfen nicht ueber
    LICHTER_GRENZE steigen.
    """
    im = Image.open(ziel).convert("L")
    w, h = im.size
    zone = im.crop((int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.7)))
    px = sorted(zone.getdata())
    mittel = sum(px) / len(px)
    p95 = px[int(len(px) * 0.95)]
    if mittel <= 0:
        return HELLIGKEIT_MAX
    nach_mittel = ZIEL_HELLIGKEIT / mittel
    nach_lichtern = LICHTER_GRENZE / p95 if p95 > 0 else HELLIGKEIT_MAX
    # Abdunkeln darf der Lichterschutz nie verhindern, nur das Aufhellen
    # bremsen — deshalb greift er erst oberhalb von 1.
    obergrenze = min(HELLIGKEIT_MAX, max(1.0, nach_lichtern))
    return round(min(obergrenze, max(HELLIGKEIT_MIN, nach_mittel)), 2)


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
    """Harter Schnitt statt Ueberblendung, dazu ein Zap wie am Roehrenfernseher.

    Die Bilder loesen sich ohne Blende ab: jedes ist genau seinen Abschnitt
    lang zu sehen, dann sofort das naechste. Damit der Schnitt nicht bloss wie
    ein Ruckler wirkt, blitzt im selben Moment ein lilafarbener Streifen auf,
    faellt in eine waagerechte Linie zusammen und erlischt.

    Der Zap laeuft in einer eigenen Animation auf einer eigenen Ebene. Ihre
    Dauer ist die eines einzelnen Bildes, nicht die des ganzen Durchlaufs —
    dadurch trifft sie jeden Wechsel, ohne dass die Keyframes von der Anzahl
    der Bilder abhaengen.
    """
    dauer = anzahl * SEKUNDEN_PRO_BILD
    anteil = 100 / anzahl               # Anteil eines Bildes am Durchlauf
    ms = SEKUNDEN_PRO_BILD * 1000       # ein Bildabschnitt in Millisekunden

    def pz(millis):
        return f"{millis / ms * 100:.4f}%"

    zeilen = [
        CSS_A,
        "@media (prefers-reduced-motion: no-preference) {",
        f"  .hero__slide {{ animation: hero-slideshow {dauer}s step-end infinite; }}",
    ]
    for i in range(anzahl):
        zeilen.append(
            f"  .hero__slide:nth-child({i + 1}) {{ animation-delay: {i * SEKUNDEN_PRO_BILD}s; }}"
        )
    zeilen += [
        f"  .hero__zap {{ animation: hero-zap {SEKUNDEN_PRO_BILD}s linear infinite; }}",
        "}",
        "@keyframes hero-slideshow {",
        "  0%              { opacity: 1; }",
        f"  {anteil:.4f}%   {{ opacity: 0; }}",
        "  100%            { opacity: 0; }",
        "}",
        "/* --zap-dreh setzt script.js bei jedem Durchlauf neu, damit der",
        "   Streifen nicht jedes Mal gleich liegt. Die Drehung steht vor dem",
        "   Stauchen, sonst kippt nicht der Streifen, sondern seine Achse. */",
        "@keyframes hero-zap {",
        "  0%       { opacity: 1; transform: rotate(var(--zap-dreh, 0deg)) scaleY(1); }",
        f"  {pz(ZAP_AUF_MS)}  {{ opacity: 1; transform: rotate(var(--zap-dreh, 0deg)) scaleY(.06); }}",
        f"  {pz(ZAP_AUF_MS + ZAP_LINIE_MS)}  {{ opacity: .9; transform: rotate(var(--zap-dreh, 0deg)) scaleY(.014); }}",
        f"  {pz(ZAP_GESAMT_MS)}  {{ opacity: 0; transform: rotate(var(--zap-dreh, 0deg)) scaleY(.005); }}",
        "  100%     { opacity: 0; transform: rotate(var(--zap-dreh, 0deg)) scaleY(.005); }",
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
        for stufe, (maxdim, bpp, minq, deckel) in enumerate(GROESSEN):
            anhang = "" if stufe == 0 else f"@{maxdim}"
            ziel = ZIEL / f"{p.stem}{anhang}.webp"
            q, b, h = konvertiere(p, ziel, maxdim, bpp, minq, deckel)
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
    for (maxdim, *_), summe in zip(GROESSEN, je_fassung):
        print(f"Fassung bis {maxdim}px: {summe / 1048576:.2f} MB "
              f"— so viel laedt ein Geraet, das diese Stufe waehlt.")
    print(f"Ein Durchlauf dauert {len(eintraege) * SEKUNDEN_PRO_BILD} Sekunden.")
    print("index.html und styles.css sind aktualisiert. Jetzt pruefen und pushen.")


if __name__ == "__main__":
    main()
