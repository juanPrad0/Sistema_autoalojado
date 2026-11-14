/* Panel personal: the shell is cached, pages stay fresh, stale cache is dropped on activate. */
const VERSION = "panel-v2";
const SHELL = [
  "/",
  "/static/css/app.css",
  "/static/vendor/taste/system.css",
  "/static/vendor/taste/ui/cards.css",
  "/static/vendor/taste/motion/motion.css",
  "/static/vendor/taste/layout/layout.css",
  "/static/vendor/taste/system.js",
  "/static/vendor/taste/motion/motion.js",
  "/static/vendor/taste/layout/layout.js",
  "/static/vendor/htmx.min.js",
  "/static/fonts/mona-sans-latin.woff2",
  "/static/fonts/geist-mono-latin.woff2",
  "/static/icons/icon.svg",
  "/static/manifest.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(VERSION)
      .then((cache) => cache.addAll(SHELL))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== VERSION).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(VERSION).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request).then((hit) => hit || caches.match("/"))),
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(
      (hit) =>
        hit ||
        fetch(request).then((response) => {
          if (response.ok && url.pathname.startsWith("/static/")) {
            const copy = response.clone();
            caches.open(VERSION).then((cache) => cache.put(request, copy));
          }
          return response;
        }),
    ),
  );
});
