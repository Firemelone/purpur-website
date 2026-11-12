// Reichweitenmessung mit Umami -- selbst gehostet unter anal.rys.network,
// cookielos, speichert keine IP-Adressen.
//
// Das Skript wird bewusst erst nach window.load nachgeladen: der Ladevorhang
// der Startseite wartet auf load, und jedes <script> im Dokument haelt load
// auf. Ein langsamer oder ausgefallener Analyse-Server darf die Seite nie
// aufhalten.
//
// data-domains begrenzt die Zaehlung auf die echte Domain. Lokale Tests
// (python3 -m http.server) zaehlen dadurch nicht mit.
//
// Wer nicht gezaehlt werden will: Knopf auf /privacy.html, setzt
// localStorage "umami.disabled". Das Skript prueft das Flag selbst.
(function () {
  function laden() {
    var s = document.createElement("script");
    s.src = "https://anal.rys.network/script.js";
    s.async = true;
    s.setAttribute("data-website-id", "bb47f4b1-1f34-4694-b2bf-174a8c95349d");
    s.setAttribute("data-domains", "purpur.berlin");
    document.head.appendChild(s);
  }
  if (document.readyState === "complete") laden();
  else window.addEventListener("load", laden, { once: true });
})();
