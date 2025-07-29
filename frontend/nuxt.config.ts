export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxt/icon',
    '@pinia/nuxt'
  ],
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'CalcNest - Online Calculator Platform',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'CalcNest - Free online calculators for mathematics, health, construction, finance, and unit conversion.' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api/v1'
    }
  },
  ssr: true
})
