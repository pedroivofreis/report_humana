const CACHE_NAME = 'humana-checkin-lite-v2'
const APP_SHELL = ['/', '/index.html', '/manifest.webmanifest', '/icon-humana.svg', '/logo.png', '/favicon.ico']

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)),
  )
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key)
          return Promise.resolve()
        }),
      ),
    ),
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return
  event.respondWith((async () => {
    try {
      const response = await fetch(event.request)
      const cache = await caches.open(CACHE_NAME)
      cache.put(event.request, response.clone())
      return response
    } catch {
      const cached = await caches.match(event.request)
      if (cached) return cached
      return caches.match('/') || Response.error()
    }
  })())
})
