import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  timeout: 15_000,
  expect: { timeout: 5_000 },
  use: {
    baseURL: "http://127.0.0.1:4173",
    channel: "chrome",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "pnpm -r build && node e2e/server.mjs",
    url: "http://127.0.0.1:4173/guest/",
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
