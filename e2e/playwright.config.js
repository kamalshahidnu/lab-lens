// @ts-check
const { defineConfig } = require("@playwright/test");

const baseURL =
  process.env.BASE_URL ||
  process.env.LAB_LENS_WEB_URL ||
  process.env.SERVICE_URL ||
  "http://localhost:8501";

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure"
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" }
    }
  ]
});

