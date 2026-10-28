/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:8000" } },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
    // Cổng L0: coverage ≥ 70% (docs/07-verification/test-plan.md §7)
    coverage: {
      provider: "v8",
      include: ["src/**"],
      exclude: ["src/**/*.test.*", "src/test-setup.ts", "src/api-client/generated.ts"],
      reporter: ["text-summary", "json-summary"],
      reportsDirectory: "../var/coverage/web",
      thresholds: { lines: 70, statements: 70, branches: 70, functions: 70 },
    },
  },
});
