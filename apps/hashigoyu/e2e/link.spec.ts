import { expect, test } from "@playwright/test";

const sampleNotice = "銭湯名・住所・人数・金額はすべて架空のサンプルです";

test("管理の現金目標変更が番台へリロードなしで反映される", async ({ browser, baseURL }) => {
  const context = await browser.newContext();
  const counter = await context.newPage();
  const admin = await context.newPage();

  await counter.goto(`${baseURL}/counter/`);
  await expect(counter.locator(".counter-kpis").getByText("目標 227", { exact: true })).toBeVisible();

  await admin.goto(`${baseURL}/admin/`);
  await admin.getByRole("button", { name: /若葉湯/ }).click();
  await admin.getByRole("spinbutton", { name: "残したい現金", exact: true }).fill("10000000");

  await expect(counter.locator(".counter-kpis").getByText("目標 286", { exact: true })).toBeVisible();
  await context.close();
});

test("管理の現金目標変更が顧客の2軒目提案へ反映される", async ({ browser, baseURL }) => {
  const context = await browser.newContext();
  const guest = await context.newPage();
  const admin = await context.newPage();

  await guest.goto(`${baseURL}/guest/`);
  await guest.getByLabel("入る時間", { exact: true }).fill("16:00");
  await guest.getByRole("button", { name: "3軒", exact: true }).click();
  await expect(guest.locator(".route-card h3").nth(1)).toHaveText("若葉湯");

  await admin.goto(`${baseURL}/admin/`);
  await admin.getByRole("button", { name: /日の出湯/ }).click();
  await admin.getByRole("spinbutton", { name: "残したい現金", exact: true }).fill("100000000");

  await expect(guest.locator(".route-card h3").nth(1)).toHaveText("日の出湯");
  await context.close();
});

test("3画面に架空サンプルの免責表示がある", async ({ page, baseURL }) => {
  for (const app of ["guest", "counter", "admin"]) {
    await page.goto(`${baseURL}/${app}/`);
    await expect(page.getByText(sampleNotice, { exact: true })).toBeVisible();
  }
});

test("銭湯管理で新規登録と基本情報の編集ができる", async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/admin/`);
  await page.getByRole("button", { name: "銭湯管理", exact: true }).click();
  await expect(page.getByRole("heading", { name: "銭湯一覧", exact: true })).toBeVisible();

  await page.getByRole("button", { name: "新規登録", exact: true }).click();
  const editor = page.locator(".master-editor-panel");
  await editor.getByLabel("銭湯名").fill("新町湯");
  await editor.getByLabel("住所").fill("東京都新宿区新町1-2-3");
  await editor.getByLabel("区市町村").fill("新宿区");
  await editor.getByLabel("緯度").fill("35.69");
  await editor.getByLabel("経度").fill("139.71");
  await editor.getByLabel("営業開始").fill("15");
  await editor.getByLabel("営業終了").fill("24");
  await page.getByRole("button", { name: "保存", exact: true }).click();

  await expect(page.getByText("保存しました", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: /新町湯/ })).toBeVisible();
  await expect(page.getByText("未登録", { exact: true })).toBeVisible();

  await editor.getByLabel("銭湯名").fill("新町温泉");
  await page.getByRole("button", { name: "保存", exact: true }).click();
  await expect(page.getByRole("button", { name: /新町温泉/ })).toBeVisible();
});
