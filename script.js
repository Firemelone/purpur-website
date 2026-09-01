// Mobile nav toggle
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const isOpen = navLinks.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });
}

// Die Abschnitte blenden nicht mehr ein — sie stehen von Anfang an und
// schieben sich beim Scrollen ueber die feste Bildebene. Der Beobachter dafuer
// ist deshalb entfallen.

// Nav only appears once the hero section has been scrolled past
const nav = document.querySelector(".nav");
const hero = document.querySelector(".hero");

if (nav && hero) {
  const navObserver = new IntersectionObserver(
    ([entry]) => {
      nav.classList.toggle("is-visible", !entry.isIntersecting);
    },
    { threshold: 0 }
  );
  navObserver.observe(hero);
}

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Text-decode — die Buchstaben stimmen fast sofort, aber sie zappeln noch durch
// verschiedene GC-Furion-Schnitte, bevor sie sich setzen. Vorbild ist das
// Announcement-Reel: ein Wort, mehrere Strichstaerken gleichzeitig.
const DECODE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!<>-_/\\[]{}=+*^?#";
const WOBBLE_CLASSES = [
  "wb-thin", "wb-extralight", "wb-light", "wb-regular",
  "wb-medium", "wb-semibold", "wb-bold", "wb-extrabold", "wb-black",
  "wb-thin wb-oblique", "wb-light wb-oblique", "wb-black wb-oblique",
];
const TINT_CLASSES = ["", "", "", "wb-acid", "wb-mint", "wb-magenta"];

const pick = (arr) => arr[(Math.random() * arr.length) | 0];

// Baut den Text als einzelne <span> auf, damit jeder Buchstabe seinen eigenen
// Schnitt bekommen kann. Leerzeichen bleiben echte Leerzeichen.
function spanify(el, text) {
  el.textContent = "";
  const frag = document.createDocumentFragment();
  const spans = [];
  for (const ch of text) {
    if (ch === " ") {
      frag.appendChild(document.createTextNode(" "));
      spans.push(null);
      continue;
    }
    const s = document.createElement("span");
    s.className = "wb";
    s.textContent = ch;
    frag.appendChild(s);
    spans.push(s);
  }
  el.appendChild(frag);
  return spans;
}

function runDecode(el) {
  if (el.dataset.decoding === "true") return;
  if (!el.dataset.decodeText) el.dataset.decodeText = el.textContent;
  const finalText = el.dataset.decodeText;
  const length = finalText.length;
  el.dataset.decoding = "true";

  const spans = spanify(el, finalText);

  // Reihenfolge, in der die Zeichen ihren echten Wert bekommen — gemischt,
  // damit auch lange Zeilen schnell fertig sind statt von links nach rechts.
  const order = Array.from({ length }, (_, i) => i);
  for (let i = order.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0;
    [order[i], order[j]] = [order[j], order[i]];
  }
  const SCRAMBLE_FRAMES = 12;   // falsche Zeichen
  const WOBBLE_FRAMES = 10;     // richtige Zeichen, noch falscher Schnitt
  const revealAt = new Array(length);
  order.forEach((idx, pos) => {
    revealAt[idx] = Math.floor((pos / length) * SCRAMBLE_FRAMES);
  });

  let frame = 0;
  clearInterval(el._decodeTimer);
  el._decodeTimer = setInterval(() => {
    for (let i = 0; i < length; i++) {
      const s = spans[i];
      if (!s) continue;
      const settled = frame >= revealAt[i];
      s.textContent = settled ? finalText[i] : pick(DECODE_CHARS);
      // Der Schnitt zappelt noch weiter, nachdem das Zeichen richtig ist,
      // und beruhigt sich erst gegen Ende.
      const stillWobbling = frame < revealAt[i] + WOBBLE_FRAMES;
      s.className = stillWobbling ? "wb " + pick(WOBBLE_CLASSES) + " " + pick(TINT_CLASSES) : "wb";
    }
    frame++;
    if (frame > SCRAMBLE_FRAMES + WOBBLE_FRAMES) {
      clearInterval(el._decodeTimer);
      el.textContent = finalText;
      el.dataset.decoding = "false";
    }
  }, 45);
}

const decodeTargets = document.querySelectorAll(".decode");

if (decodeTargets.length) {
  if (prefersReducedMotion) {
    decodeTargets.forEach((el) => {
      el.dataset.decodeText = el.textContent;
    });
  } else {
    const decodeObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) runDecode(entry.target);
        });
      },
      { threshold: 0.4 }
    );
    decodeTargets.forEach((el) => decodeObserver.observe(el));
  }
}

// Bunny cursor — desktop / fine-pointer devices only
const cursor = document.getElementById("cursor");
const supportsFineCursor = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

if (cursor && supportsFineCursor) {
  document.documentElement.classList.add("has-custom-cursor");
  cursor.classList.add("is-loading");

  let targetX = window.innerWidth / 2;
  let targetY = window.innerHeight / 2;
  let x = targetX;
  let y = targetY;
  let hasMoved = false;

  // Der Sticker sitzt direkt unter dem Zeiger. Vorher zog er mit Faktor 0.28
  // hinterher, was sich traege anfuehlte; jetzt folgt er praktisch sofort und
  // behaelt nur einen Hauch Nachlauf, damit die Bewegung nicht hart wirkt.
  let pending = false;

  const positionCursor = () => {
    pending = false;
    x += (targetX - x) * 0.85;
    y += (targetY - y) * 0.85;
    // translate3d haelt die Ebene auf der GPU, statt bei jedem Frame neu
    // zu rastern
    cursor.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`;
    if (Math.abs(targetX - x) > 0.1 || Math.abs(targetY - y) > 0.1) request();
  };

  const request = () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(positionCursor);
  };

  // Nur bei tatsaechlicher Bewegung rechnen, nicht in einer Dauerschleife
  window.addEventListener("mousemove", (e) => {
    targetX = e.clientX;
    targetY = e.clientY;
    if (!hasMoved) {
      x = targetX;
      y = targetY;
      hasMoved = true;
    }
    request();
  }, { passive: true });

  const interactiveSelector =
    'a, button, .btn, input, textarea, select, [role="button"], .nav__toggle, .card, .stampframe';

  document.addEventListener("mouseover", (e) => {
    if (e.target.closest(interactiveSelector)) cursor.classList.add("is-hover");
  });
  document.addEventListener("mouseout", (e) => {
    if (e.target.closest(interactiveSelector)) cursor.classList.remove("is-hover");
  });
  document.addEventListener("mousedown", () => cursor.classList.add("is-active"));
  document.addEventListener("mouseup", () => cursor.classList.remove("is-active"));
  window.addEventListener("blur", () => cursor.classList.remove("is-active", "is-hover"));
}

// Ladesequenz: das Symbol dreht sich einmal, danach glitcht es zum vollen
// Logo. Erst wenn beides durch ist (und die Seite geladen), faellt der
// Vorhang. Dauer der Drehung steckt in --loader-spin, damit CSS und JS nicht
// auseinanderlaufen.
const loader = document.getElementById("loader");

if (loader) {
  document.body.classList.add("is-loading");

  // Das Ladelogo steht sonst genau in der Bildschirmmitte, die Wortmarke im
  // Hero aber hoeher — beim Verschwinden des Vorhangs sprang das Logo also
  // ein Stueck nach oben. Statt den Versatz fest einzutragen, wird er hier
  // gemessen: Beide Elemente sind gleich gross, es fehlt nur die Verschiebung.
  // Gemessen statt gerechnet, damit es bei jeder Fenstergroesse stimmt und
  // auch dann, wenn sich am Aufbau des Hero spaeter etwas aendert.
  const buehne = loader.querySelector(".loader__stage");
  const vollesLogo = loader.querySelector(".loader__full");
  const heldenLogo = document.querySelector(".hero__logo");

  const ausrichten = () => {
    if (!buehne || !vollesLogo || !heldenLogo) return;
    buehne.style.transform = "";
    const versatz =
      heldenLogo.getBoundingClientRect().top - vollesLogo.getBoundingClientRect().top;
    if (Number.isFinite(versatz)) buehne.style.transform = `translateY(${versatz}px)`;
  };

  ausrichten();
  window.addEventListener("resize", ausrichten, { passive: true });
  const SPIN_MS = 700;    // Symbol dreht sich
  const GLITCH_MS = 500;  // Uebergang zum vollen Logo
  const FALLBACK_MS = 5000;

  const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  const windowLoaded = new Promise((resolve) => {
    if (document.readyState === "complete") resolve();
    else window.addEventListener("load", resolve, { once: true });
  });

  // Choreografie laeuft unabhaengig davon, wie schnell die Medien kommen
  const choreography = new Promise((resolve) => {
    setTimeout(() => {
      loader.classList.add("is-glitching");
      setTimeout(resolve, GLITCH_MS);
    }, SPIN_MS);
  });

  const fallback = new Promise((resolve) => setTimeout(resolve, FALLBACK_MS));

  Promise.race([
    Promise.all([fontsReady, windowLoaded, choreography]),
    fallback,
  ]).then(() => {
    loader.classList.add("is-hidden");
    document.body.classList.remove("is-loading");
    if (typeof cursor !== "undefined" && cursor) cursor.classList.remove("is-loading");
    loader.addEventListener("transitionend", () => loader.remove(), { once: true });
    setTimeout(() => loader.remove(), 1200);
  });
}

// ---------------------------------------------------------------------------
// Zeilen im Videoabschnitt neigen sich zur Maus
// ---------------------------------------------------------------------------
// Die drei Zeilen sollen der Maus zugewandt stehen, als wuerden sie sie
// ansehen. Der Ausschlag richtet sich danach, wie weit der Zeiger von der
// Mitte des Blocks entfernt ist — auf eine halbe Blockbreite gerechnet und
// gedeckelt, damit er nicht weiter kippt, je weiter man wegzieht.
// Die unteren Zeilen schwenken etwas weniger als die obere. Dieser Versatz
// laesst die drei wie hintereinanderliegende Ebenen wirken statt wie eine
// starre Platte.
const wortBlock = document.querySelector(".visual__word");
const magNeigen =
  window.matchMedia("(hover: hover)").matches &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (wortBlock && magNeigen) {
  const zeilen = [...wortBlock.querySelectorAll(".fx-line")];
  const MAX_GRAD = 11;
  let angefordert = false;

  const klemmen = (v) => Math.max(-1, Math.min(1, v));

  const neigen = (e) => {
    angefordert = false;
    const r = wortBlock.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const x = klemmen((e.clientX - (r.left + r.width / 2)) / (r.width / 2));
    const y = klemmen((e.clientY - (r.top + r.height / 2)) / (r.height / 2));
    zeilen.forEach((zeile, i) => {
      const tiefe = 1 - i * 0.18;
      const drehY = x * MAX_GRAD * tiefe;
      const drehX = -y * MAX_GRAD * tiefe;
      zeile.style.transform = `rotateX(${drehX.toFixed(2)}deg) rotateY(${drehY.toFixed(2)}deg)`;
    });
  };

  window.addEventListener(
    "mousemove",
    (e) => {
      if (angefordert) return;
      angefordert = true;
      requestAnimationFrame(() => neigen(e));
    },
    { passive: true }
  );

  // Zeiger verlaesst das Fenster: zurueck in die Ruhelage
  document.addEventListener("mouseleave", () => {
    zeilen.forEach((zeile) => (zeile.style.transform = "rotateX(0deg) rotateY(0deg)"));
  });
}

// ---------------------------------------------------------------------------
// Kanalwechsel-Streifen: Neigung wuerfeln
// ---------------------------------------------------------------------------
// CSS kann nicht zufaellig. Damit der Streifen nicht bei jedem Bildwechsel
// identisch liegt, bekommt er hier vor jedem Durchlauf eine neue leichte
// Neigung. animationiteration feuert genau am Rundenwechsel, also unmittelbar
// bevor der naechste Zap aufblitzt.
const zap = document.querySelector(".hero__zap");

if (zap) {
  const neigen = () => {
    const grad = (Math.random() * 5 - 2.5).toFixed(2);
    zap.style.setProperty("--zap-dreh", `${grad}deg`);
  };
  neigen();
  zap.addEventListener("animationiteration", neigen);
}

// ---------------------------------------------------------------------------
// Absperrband mit Countdown
// ---------------------------------------------------------------------------
// Das Band laeuft endlos von rechts nach links. Damit dabei keine Luecke
// entsteht, muss die Spur mindestens doppelt so breit sein wie der Bildschirm:
// verschoben wird um genau die Haelfte, und was links herauslaeuft, muss rechts
// schon wieder dastehen. Wie viele Wiederholungen das sind, haengt von der
// Fensterbreite ab, also wird eine Gruppe gemessen und dann aufgefuellt.

const tapeTrack = document.getElementById("tapeTrack");

function tapeGroup() {
  return `
    <span class="tape__group">
      <span class="tape__item">03-10-26</span>
      <img class="tape__icon" src="/Media/Logo_SVG/PURPUR-Symbol-Purple.svg" alt="" />
      <span class="tape__item">PURPUR #1</span>
      <img class="tape__icon" src="/Media/Logo_SVG/PURPUR-Symbol-Purple.svg" alt="" />
      <span class="tape__item">BERLIN</span>
      <img class="tape__icon" src="/Media/Logo_SVG/PURPUR-Symbol-Purple.svg" alt="" />
    </span>`;
}

if (tapeTrack) {
  function fillTape() {
    tapeTrack.innerHTML = tapeGroup();
    const one = tapeTrack.firstElementChild.getBoundingClientRect().width;
    if (!one) return;
    // Eine Haelfte der Spur muss den Bildschirm ueberdecken, sonst klafft beim
    // Umbruch eine Luecke. Das Band steht schraeg und ist dadurch breiter als
    // das Fenster, deshalb grosszuegig aufrunden.
    const perHalf = Math.max(2, Math.ceil((window.innerWidth * 1.35) / one));
    tapeTrack.innerHTML = tapeGroup().repeat(perHalf * 2);
  }

  fillTape();

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      fillTape();
    }, 200);
  });
}

// Das Hintergrundvideo laedt bewusst nur Metadaten, damit es beim ersten
// Seitenaufbau keine 355 KB mitzieht. Autoplay springt dann aber nicht von
// allein an — also starten wir es, sobald der Abschnitt in Sicht kommt, und
// halten es an, wenn er wieder verschwindet.
const bgVideo = document.querySelector(".visual__img");

if (bgVideo) {
  const videoObserver = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        if (bgVideo.preload !== "auto") bgVideo.preload = "auto";
        const p = bgVideo.play();
        if (p && p.catch) p.catch(() => {});
      } else {
        bgVideo.pause();
      }
    },
    { threshold: 0.15 }
  );
  videoObserver.observe(bgVideo);
}
