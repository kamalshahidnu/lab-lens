const { test, expect } = require("@playwright/test");

test("Streamlit UI loads (smoke)", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });

  // Streamlit apps can take a moment to finish hydrating/rendering.
  await expect(page.getByRole("heading", { name: /lab lens/i })).toBeVisible();
  await expect(page.getByText(/file q&a/i)).toBeVisible();
});

