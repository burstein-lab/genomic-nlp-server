import { defineNuxtConfig } from "nuxt";

// https://v3.nuxtjs.org/api/configuration/nuxt.config
// https://codybontecou.com/how-to-use-vuetify-with-nuxt-3.html#installation
export default defineNuxtConfig({
  css: [
    "vuetify/lib/styles/main.sass",
    "@mdi/font/css/materialdesignicons.css",
  ],
  build: {
    transpile: ["vuetify"],
  },
  vite: {
    define: {
      "process.env.DEBUG": "false",
    },
  },
  runtimeConfig: {
    public: {
      apiBase: "http://127.0.0.1:5000",
    },
  },
});
