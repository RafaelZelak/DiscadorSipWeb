self.addEventListener('install', event => {
    console.log('Service Worker installing.');
    event.waitUntil(
        caches.open('static-cache').then(cache => {
            return cache.addAll([
                '/',
                '/static/js/script.js',
                '/static/style/style.css',
                '/manifest.json',
                '/static/icons/icon-192x192.png',
                '/static/icons/icon-512x512.png'
            ]);
        })
    );
});

self.addEventListener('activate', event => {
    console.log('Service Worker activating.');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== 'static-cache') {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
