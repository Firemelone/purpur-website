// PURPUR — Startseite "Tape"
// Ladesequenz, Neigung zur Maus / zum Handy, Decode-Text, Sticker-Cursor,
// Navigation nach dem Hero, Slideshow mit Glitch, Hintergrundvideos.
// Kein Framework, keine externen Skripte.

(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hoverFine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var clamp = function (v) { return Math.max(-1, Math.min(1, v)); };
  var pick = function (a) { return a[(Math.random() * a.length) | 0]; };

  // ---------------------------------------------------------------------------
  // Ladesequenz: Symbol dreht sich einmal, glitcht zum vollen Logo, Vorhang faellt
  // ---------------------------------------------------------------------------
  var loader = document.getElementById("loader");
  var loaded = false;
  var onLoaded = [];
  function whenLoaded(fn) { if (loaded) fn(); else onLoaded.push(fn); }
  function finishLoader() {
    loaded = true;
    if (loader) {
      loader.classList.add("is-out");
      setTimeout(function () { loader.remove(); }, 600);
    }
    document.documentElement.classList.remove("is-loading");
    onLoaded.forEach(function (fn) { fn(); });
  }
  if (loader && !reduce) {
    document.documentElement.classList.add("is-loading");
    var fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    var pageLoaded = new Promise(function (r) {
      if (document.readyState === "complete") r(); else window.addEventListener("load", r, { once: true });
    });
    var choreo = new Promise(function (r) {
      setTimeout(function () { loader.classList.add("is-glitching"); setTimeout(r, 320); }, 480);
    });
    var fallback = new Promise(function (r) { setTimeout(r, 4000); });
    Promise.race([Promise.all([fontsReady, pageLoaded, choreo]), fallback]).then(finishLoader);
  } else {
    if (loader) loader.remove();
    loaded = true;
  }

  // ---------------------------------------------------------------------------
  // Navigation erscheint erst, wenn der Hero durchgescrollt ist
  // ---------------------------------------------------------------------------
  var nav = document.getElementById("nav");
  var hero = document.querySelector("[data-hero]");
  if (nav && hero) {
    var navCheck = function () {
      nav.classList.toggle("is-visible", hero.getBoundingClientRect().bottom < 72);
    };
    window.addEventListener("scroll", navCheck, { passive: true });
    window.addEventListener("resize", navCheck);
    navCheck();
  }

  // ---------------------------------------------------------------------------
  // Hintergrundvideos: stumm, Schleife, nur abspielen, wenn sichtbar
  // ---------------------------------------------------------------------------
  var videos = document.querySelectorAll("video[data-bg]");
  videos.forEach(function (v) {
    v.muted = true; v.loop = true; v.playsInline = true;
    var rate = parseFloat(v.getAttribute("data-rate") || "1");
    v.playbackRate = rate; v.defaultPlaybackRate = rate;
  });
  if ("IntersectionObserver" in window) {
    var vo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else v.pause();
      });
    }, { threshold: 0.1 });
    videos.forEach(function (v) { vo.observe(v); });
  }

  // ---------------------------------------------------------------------------
  // Slideshow im Hero mit Glitch-Uebergang (chromatische Aberration)
  // ---------------------------------------------------------------------------
  var slides = document.getElementById("slides");
  if (slides) {
    var imgs = slides.querySelectorAll(".slide");
    var current = 0;
    setInterval(function () {
      if (document.hidden || imgs.length < 2) return;
      var next = (current + 1) % imgs.length;
      var swap = function () {
        imgs[current].classList.remove("is-active");
        imgs[next].classList.add("is-active");
        current = next;
      };
      if (reduce) { swap(); return; }
      slides.classList.add("pp-ca");
      setTimeout(swap, 130);
      setTimeout(function () { slides.classList.remove("pp-ca"); }, 340);
    }, 4200);
  }

  if (reduce) return;

  // ---------------------------------------------------------------------------
  // Neigung: jede Gruppe kippt zur Maus (Desktop) bzw. mit dem Handy
  // ---------------------------------------------------------------------------
  var GROUPS = {
    hero: { max: 8, stufe: 0.45, tiefe: 1200, handy: 0.72, n: 2 },
    photo: { max: 7, stufe: 0.5, tiefe: 1100, handy: 1, n: 1 },
    who: { max: 10, stufe: 0.2, tiefe: 900, handy: 1, n: 2 },
    lineup: { max: 7, stufe: 0.06, tiefe: 1100, handy: 1, n: 5 },
    insight: { max: 7, stufe: 0.5, tiefe: 1100, handy: 1, n: 2 },
    flag: { max: 9, stufe: 0.3, tiefe: 900, handy: 1, n: 2 }
  };
  var groupEls = {};
  Object.keys(GROUPS).forEach(function (k) {
    var el = document.querySelector('[data-tilt="' + k + '"]');
    if (el) groupEls[k] = el;
  });
  // Empfindlichkeit der Neigung: Maus etwas kraeftiger als 1:1, Handy deutlich.
  var MAUS_FAKTOR = 1.35;
  var HANDY_FAKTOR = 2.2;
  var HANDY_GRAD = 18;   // so viel Grad Neigung entsprechen dem Vollausschlag
  function apply(k, x, y, boost) {
    var g = GROUPS[k], el = groupEls[k];
    if (!el) return;
    var m = g.max * (boost ? HANDY_FAKTOR * g.handy : MAUS_FAKTOR);
    for (var i = 0; i < g.n; i++) {
      var a = Math.max(0.2, 1 - i * g.stufe);
      el.style.setProperty("--t-" + k + "-l" + i,
        "perspective(" + g.tiefe + "px) rotateX(" + (-y * m * a).toFixed(2) + "deg) rotateY(" + (x * m * a).toFixed(2) + "deg)");
    }
  }
  var pending = false;
  var throttle = function (fn) {
    return function (arg) {
      if (pending) return; pending = true;
      requestAnimationFrame(function () { pending = false; fn(arg); });
    };
  };

  // Sticker-Cursor (nur mit feiner Maus)
  var cursor = document.getElementById("cursor");
  if (cursor && hoverFine) {
    document.documentElement.classList.add("has-cursor");
    var sel = 'a, button, input, textarea, select, label, [role="button"]';
    document.addEventListener("mouseover", function (e) { if (e.target.closest && e.target.closest(sel)) cursor.classList.add("is-hover"); });
    document.addEventListener("mouseout", function (e) { if (e.target.closest && e.target.closest(sel)) cursor.classList.remove("is-hover"); });
    document.addEventListener("mousedown", function () { cursor.classList.add("is-active"); });
    document.addEventListener("mouseup", function () { cursor.classList.remove("is-active"); });
    document.addEventListener("mouseleave", function () { cursor.classList.remove("is-shown"); });
  } else if (cursor) {
    cursor.remove(); cursor = null;
  }

  if (hoverFine) {
    window.addEventListener("mousemove", throttle(function (e) {
      if (cursor) {
        cursor.style.transform = "translate3d(" + e.clientX + "px," + e.clientY + "px,0) translate(-50%,-50%)";
        if (loaded) cursor.classList.add("is-shown");
      }
      Object.keys(groupEls).forEach(function (k) {
        var r = groupEls[k].getBoundingClientRect();
        if (!r.width || !r.height) return;
        apply(k, clamp((e.clientX - (r.left + r.width / 2)) / (r.width / 2)),
                 clamp((e.clientY - (r.top + r.height / 2)) / (r.height / 2)), false);
      });
    }), { passive: true });
    document.addEventListener("mouseleave", function () {
      Object.keys(groupEls).forEach(function (k) { apply(k, 0, 0, false); });
    });
  } else {
    // Handy: alle Gruppen folgen derselben Lage. Ohne Sensor bewegt das Scrollen.
    var all = function (x, y) { Object.keys(groupEls).forEach(function (k) { apply(k, x, y, true); }); };
    var sensor = false;
    window.addEventListener("scroll", throttle(function () {
      if (sensor) return;
      var t = window.scrollY / 260;
      all(clamp(Math.sin(t) * 0.62 + Math.sin(t * 1.618 + 1.3) * 0.38),
          clamp(Math.cos(t * 0.77 + 2.1) * 0.62 + Math.sin(t * 2.13) * 0.38));
    }), { passive: true });
    window.addEventListener("deviceorientation", throttle(function (e) {
      if (e.gamma == null || e.beta == null) return;
      sensor = true;
      all(clamp(e.gamma / HANDY_GRAD), clamp((e.beta - 45) / HANDY_GRAD));
    }));
    // iOS fragt den Lagesensor erst nach einer Beruehrung frei
    if (typeof DeviceOrientationEvent !== "undefined" && typeof DeviceOrientationEvent.requestPermission === "function") {
      window.addEventListener("touchend", function () {
        DeviceOrientationEvent.requestPermission().catch(function () {});
      }, { once: true });
    }
  }

  // ---------------------------------------------------------------------------
  // Decode-Text: Zeichen wechseln zufaellig durch und zappeln durch die
  // Furion-Schnitte, bevor sie sich setzen. Vorbild ist das Announcement-Reel.
  // ---------------------------------------------------------------------------
  var CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!<>-_/[]{}=+*^?#";
  var WB = ["w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w1 wi", "w3 wi", "w9 wi"];
  var TINT = ["", "", "", "ta", "tm", "tg"];
  function decode(el) {
    if (el._decoding) return;
    el._decoding = true;
    var original = el.innerHTML;
    var text = el.textContent;
    var chars = Array.from(text);
    var n = chars.length;
    var order = chars.map(function (_, i) { return i; });
    for (var i = n - 1; i > 0; i--) { var j = (Math.random() * (i + 1)) | 0; var t = order[i]; order[i] = order[j]; order[j] = t; }
    var S = 12, W = 10, revealAt = [];
    order.forEach(function (idx, pos) { revealAt[idx] = Math.floor((pos / n) * S); });
    // Nur innerhalb eines Wortes nowrap: sonst stuende die ganze Zeile
    // waehrend des Decodens in einer Zeile und ragte auf dem Handy raus.
    var wrap = document.createElement("span");
    var spans = [];
    var wort = null;
    chars.forEach(function (ch) {
      if (ch === " ") {
        wrap.appendChild(document.createTextNode(" "));
        wort = null;
        spans.push(null);
        return;
      }
      if (!wort) {
        wort = document.createElement("span");
        wort.style.whiteSpace = "nowrap";
        wrap.appendChild(wort);
      }
      var s = document.createElement("span");
      s.textContent = ch;
      wort.appendChild(s);
      spans.push(s);
    });
    el.textContent = "";
    el.appendChild(wrap);
    // Jedes Zeichen bekommt die Breite, die es am Ende hat. Sonst aendern die
    // zufaelligen Glyphen die Zeilenlaenge und der Text springt waehrend des
    // Decodens in eine andere Zeile.
    var breiten = spans.map(function (s) { return s ? s.getBoundingClientRect().width : 0; });
    for (var bi = 0; bi < spans.length; bi++) {
      if (!spans[bi]) continue;
      spans[bi].style.display = "inline-block";
      spans[bi].style.width = breiten[bi].toFixed(3) + "px";
      spans[bi].style.textAlign = "center";
    }
    var frame = 0;
    var timer = setInterval(function () {
      if (frame > S + W) {
        clearInterval(timer);
        el.innerHTML = original;
        el._decoding = false;
        return;
      }
      for (var k = 0; k < n; k++) {
        if (chars[k] === " ") continue;
        var settled = frame >= revealAt[k];
        spans[k].textContent = settled ? chars[k] : pick(CHARS);
        spans[k].className = frame < revealAt[k] + W ? "wb " + pick(WB) + " " + pick(TINT) : "";
      }
      frame++;
    }, 45);
  }
  // ---------------------------------------------------------------------------
  // Regel-Tapes rollen nacheinander auf, sobald sie in den Blick kommen.
  // ---------------------------------------------------------------------------
  var tapes = document.querySelectorAll("[data-tape]");
  if (tapes.length) {
    if ("IntersectionObserver" in window) {
      for (var ti = 0; ti < tapes.length; ti++) tapes[ti].className += " tape-roll";
      var letzte = 0;
      var tio = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var el = e.target;
          tio.unobserve(el);
          // Kommen mehrere gleichzeitig herein, laufen sie 110 ms versetzt an.
          var jetzt = (window.performance ? performance.now() : Date.now());
          var versatz = Math.max(0, letzte + 110 - jetzt);
          letzte = jetzt + versatz;
          setTimeout(function () { el.classList.add("is-on"); }, versatz);
        });
      }, { threshold: 0.2, rootMargin: "0px 0px -8% 0px" });
      for (var tj = 0; tj < tapes.length; tj++) tio.observe(tapes[tj]);
    }
  }

  var targets = document.querySelectorAll("[data-decode]");
  if ("IntersectionObserver" in window && targets.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) whenLoaded(function () { decode(e.target); });
      });
    }, { threshold: 0.4 });
    targets.forEach(function (el) { io.observe(el); });
  }
})();
