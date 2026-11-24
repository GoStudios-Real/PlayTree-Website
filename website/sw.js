const CACHE_NAME = 'playtree-v16';
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
  'tv.html',\n  'web.html',\n  'voice.html',\n  'web/index.html',\n  'web/playtree.tar.gz',
  'connect.html',
  'studio.html',
  'trailer.html',
  'robots.txt',
  'downloads/index.html',
  'styles.css',
  'script.js',
  'shared.js',
  'store-config.js',
  'manifest.json',
  'assets/trailer.gif',
  'assets/banner_x.png',
  'assets/x_icon.png',
  'assets/icon32.png',
  'assets/icon48.png',
  'assets/icon128.png',
  'icon192.png',
  'icon512.png'
];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await Promise.all(ASSETS.map(async (a) => {
      try { await cache.add(a); } catch (_) { /* ignore missing assets */ }
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith((async () => {
    const cached = await caches.match(e.request);
    if (cached) return cached;
    try { return await fetch(e.request); } catch (_) { return cached || Response.error(); }
  })());
});










