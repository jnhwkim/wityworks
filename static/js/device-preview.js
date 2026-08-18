/* Device-frame preview: append ?device=iphone to the URL to reload the
   page as a side-by-side compare view — a mobile-width pane (393px,
   iPhone 15/16 logical size) next to a full-width desktop pane — so the
   real @media (max-width: ...) breakpoints actually engage on the left
   (a desktop browser resized narrower doesn't fake a phone's viewport
   quirks as well as an honest-to-god narrow iframe does), while the
   right pane shows the normal layout for direct comparison. Each pane is
   its own <iframe>, so each scrolls independently — that's the whole
   point of using two iframes instead of, say, a single resized div. The
   outer wrapper page itself is pinned to exactly 100vh with no scrolling
   of its own, so it never fights with either pane's internal scroll.
   Must run as the very first thing in <head>, before anything else
   parses, so document.write() can cleanly replace the whole document
   instead of fighting with content that already started rendering. */
(function () {
  var device = new URLSearchParams(location.search).get("device");
  var MOBILE_WIDTHS = { iphone: 393 };
  var mobileWidth = MOBILE_WIDTHS[device];
  if (!mobileWidth) return;
  var cleanUrl = location.pathname + location.hash;
  document.open();
  document.write(
    '<!doctype html><html><head><meta charset="utf-8"><title>Device preview — ' +
      device +
      "</title>" +
      "<style>" +
      "html,body{margin:0;height:100vh;overflow:hidden;background:#2b2b2b;font-family:sans-serif;}" +
      ".panes{display:flex;flex-direction:row;height:100%;}" +
      ".pane{display:flex;flex-direction:column;height:100%;}" +
      ".pane--mobile{flex:0 0 " +
      mobileWidth +
      "px;border-right:1px solid #444;}" +
      ".pane--desktop{flex:1 1 auto;min-width:0;}" +
      ".pane-label{flex:0 0 auto;padding:8px 0;text-align:center;color:#ccc;font-size:12px;letter-spacing:.05em;background:#1c1c1c;}" +
      ".pane iframe{flex:1 1 auto;width:100%;height:100%;border:0;}" +
      "</style>" +
      "</head><body>" +
      '<div class="panes">' +
      '<div class="pane pane--mobile"><div class="pane-label">' +
      mobileWidth +
      "px — " +
      device +
      '</div><iframe src="' +
      cleanUrl +
      '"></iframe></div>' +
      '<div class="pane pane--desktop"><div class="pane-label">Desktop</div><iframe src="' +
      cleanUrl +
      '"></iframe></div>' +
      "</div>" +
      "</body></html>",
  );
  document.close();
})();
