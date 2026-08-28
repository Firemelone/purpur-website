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

// Scroll-triggered reveals + the concept "stamp" frame
const revealTargets = document.querySelectorAll(".reveal, .stampframe");

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
      }
    });
  },
  { threshold: 0.3 }
);

revealTargets.forEach((el) => revealObserver.observe(el));

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

// Hero title: periodic auto-glitch pulse, on top of the existing hover glitch
const heroGlitchTargets = document.querySelectorAll(".hero__title .glitch");

if (heroGlitchTargets.length && !prefersReducedMotion) {
  setInterval(() => {
    const el = heroGlitchTargets[Math.floor(Math.random() * heroGlitchTargets.length)];
    el.classList.add("is-active");
    setTimeout(() => el.classList.remove("is-active"), 500);
  }, 2600);
}

// Text-decode scramble — headings glitch through random characters before
// resolving to their real text, replaying every time they scroll into view
const DECODE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!<>-_/\\[]{}=+*^?#";

function runDecode(el) {
  if (el.dataset.decoding === "true") return;
  if (!el.dataset.decodeText) el.dataset.decodeText = el.textContent;
  const finalText = el.dataset.decodeText;
  const length = finalText.length;
  // fixed short duration regardless of text length — characters resolve in a
  // shuffled (not left-to-right) order so long headings still finish quickly
  const totalFrames = 26;
  el.dataset.decoding = "true";

  const order = Array.from({ length }, (_, i) => i);
  for (let i = order.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0;
    [order[i], order[j]] = [order[j], order[i]];
  }
  const revealedAtFrame = new Array(length);
  order.forEach((charIndex, orderPos) => {
    revealedAtFrame[charIndex] = Math.floor((orderPos / length) * totalFrames);
  });

  let frame = 0;
  clearInterval(el._decodeTimer);
  el._decodeTimer = setInterval(() => {
    let out = "";
    for (let i = 0; i < length; i++) {
      const ch = finalText[i];
      out += ch === " " || frame >= revealedAtFrame[i] ? ch : DECODE_CHARS[(Math.random() * DECODE_CHARS.length) | 0];
    }
    el.textContent = out;
    frame++;
    if (frame > totalFrames) {
      el.textContent = finalText;
      clearInterval(el._decodeTimer);
      el.dataset.decoding = "false";
    }
  }, 28);
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

  const positionCursor = () => {
    x += (targetX - x) * 0.28;
    y += (targetY - y) * 0.28;
    // offset so the shard's drawn tip (not the box center) sits at the
    // actual pointer position — matches the transform-origin set in CSS
    cursor.style.transform = `translate(${x}px, ${y}px) translate(-15%, -10%)`;
    requestAnimationFrame(positionCursor);
  };
  requestAnimationFrame(positionCursor);

  window.addEventListener("mousemove", (e) => {
    targetX = e.clientX;
    targetY = e.clientY;
    if (!hasMoved) {
      x = targetX;
      y = targetY;
      hasMoved = true;
    }
  });

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

// Page loader — real bunny while fonts/media load, minimum display time to avoid flicker
const loader = document.getElementById("loader");

if (loader) {
  document.body.classList.add("is-loading");
  const loadStart = performance.now();
  const MIN_VISIBLE_MS = 600;
  const FALLBACK_MS = 4000;

  const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  const windowLoaded = new Promise((resolve) => {
    if (document.readyState === "complete") {
      resolve();
    } else {
      window.addEventListener("load", resolve, { once: true });
    }
  });
  const fallback = new Promise((resolve) => setTimeout(resolve, FALLBACK_MS));

  Promise.race([Promise.all([fontsReady, windowLoaded]), fallback]).then(() => {
    const elapsed = performance.now() - loadStart;
    const wait = Math.max(0, MIN_VISIBLE_MS - elapsed);
    setTimeout(() => {
      loader.classList.add("is-hidden");
      document.body.classList.remove("is-loading");
      if (cursor) cursor.classList.remove("is-loading");
      loader.addEventListener("transitionend", () => loader.remove(), { once: true });
    }, wait);
  });
}
