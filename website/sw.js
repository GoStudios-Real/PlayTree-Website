const CACHE_NAME = 'playtree-v4';
const ASSETS = [
  './',
  'index.html',
  'playstore.html',
  'xbox.html',
  'privacy.html',
  'tos.html',
  'redeem.html',
  'profile.html',
  'store.html',
  'servers.html',
  'minigames.html',
  'tv.html',
  'robots.txt',
  'downloads/index.html',
  'styles.css',
  'script.js',
  'shared.js',
  'manifest.json',
  'icon192.png',
  'icon512.png'
];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await Promise.all(ASSETS.map(async (a) => {
      try { await cache.add(a); } catch (_) { /* ignore missing assets */ }
    }));
  })());
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});