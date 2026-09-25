/*
 * AIGA hero card loader. The one script both hosts include: the Railway page
 * at /card/ and the WordPress page at aiga.networkgrey.co.za/card/.
 *
 * It mounts into #aiga-hero-card (or creates it where this script sits), adds
 * the web fonts to the host page, then loads the engine, the generated data
 * and the card in order from this script's own folder. card.js renders into a
 * shadow root, so the host site's CSS and the card's CSS never meet.
 */
(function () {
  "use strict";

  const script = document.currentScript;
  const base = new URL(".", script.src).href;
  const FONTS = "https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Source+Sans+3:wght@400;600;700&display=swap";

  // Fonts must be declared on the document; a shadow root can use them but not load them.
  if (!document.querySelector('link[href="' + FONTS + '"]')) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = FONTS;
    document.head.appendChild(link);
  }

  let host = document.getElementById("aiga-hero-card");
  if (!host) {
    host = document.createElement("div");
    host.id = "aiga-hero-card";
    script.parentNode.insertBefore(host, script);
  }
  window.AIGA_CARD = { base: base, host: host };

  ["diff_rules.js", "card_data.js", "card.js"].forEach(function (file) {
    const s = document.createElement("script");
    s.src = base + file;
    s.async = false; // keep execution order for dynamically added scripts
    document.head.appendChild(s);
  });
})();
