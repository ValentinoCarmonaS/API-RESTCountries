import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    // AÑADE ESTA LÍNEA
    baseUrl: 'http://localhost:5174',
    
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
