// Service Worker for VGC Team Analyzer PWA
const CACHE_NAME = 'vgc-analyzer-v1';
const PRECACHE = [
  '/',
];

// Cache sprites and fonts on fetch
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Cache Pokemon sprites (GIFs and PNGs) and Google Fonts
  const shouldCache =
    url.hostname === 'play.pokemonshowdown.com' ||
    url.hostname === 'raw.githubusercontent.com' ||
    url.hostname === 'fonts.googleapis.com' ||
    url.hostname === 'fonts.gstatic.com';

  if (shouldCache) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) =>
        cache.match(event.request).then((cached) => {
          if (cached) return cached;
          return fetch(event.request).then((response) => {
            if (response.ok) {
              cache.put(event.request, response.clone());
            }
            return response;
          });
        })
      )
    );
  }
});

// Clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener('install', (event) => {
  self.skipWaiting();
});
