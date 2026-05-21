import { defineConfig } from "vite";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [
    TanStackRouterVite({ autoCodeSplitting: true }),
    react(),
    tailwindcss(),
    tsconfigPaths(),
  ],
  server: {
    port: 5173,
    proxy: {
      "/start":    { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/answer":   { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/feedback": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/session":  { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
