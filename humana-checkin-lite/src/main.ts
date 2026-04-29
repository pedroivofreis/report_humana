import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')

if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      await navigator.serviceWorker.register('/sw.js')
    } catch (error) {
      console.warn('Falha ao registrar Service Worker', error)
    }
  })
}
