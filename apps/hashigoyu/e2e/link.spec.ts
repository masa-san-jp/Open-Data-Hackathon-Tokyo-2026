import { expect, test } from "@playwright/test";

const sampleNotice = "銭湯名・住所・人数・金額はすべて架空のサンプルです";

test("管理の予算変更が番台へリロードなしで反映される", async ({ browser, baseURL }) => {
  const context = await browser.newContext();
  const counter = await context.newPage();
  const admin = await context.newPage();

  await counter.goto(`${baseURL}/counter/`);
  await expect(counter.locator(".counter-kpis").getByText("目標 227", { exact: true })).toBeVisible();

  await admin.goto(`${baseURL}/admin/`);
  await admin.getByRole("button", { name: /若葉湯/ }).click();
  await admin.getByRole("spinbutton", { name: "更新まで", exact: true }).fill("10");

  await expect(counter.locator(".counter-kpis").getByText("目標 83", { exact: true })).toBeVisible();
  await context.close();
});

test("3画面に架空サンプルの免責表示がある", async ({ page, baseURL }) => {
  for (const app of ["guest", "counter", "admin"]) {
    await page.goto(`${baseURL}/${app}/`);
    await expect(page.getByText(sampleNotice, { exact: true })).toBeVisible();
  }
});
