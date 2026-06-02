import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En producción los assets se sirven bajo /static/ (Django + WhiteNoise).
// En desarrollo usamos la raíz y un proxy hacia el backend de Django.
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === "build" ? "/static/" : "/",
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
}));
