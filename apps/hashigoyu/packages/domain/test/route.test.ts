import { describe, expect, it } from "vitest";
import { buildRoute, isOpen, suggestionScore } from "../src/route";
import type { Bathhouse, Budget } from "../src/types";

const point = { lat: 35.7, lng: 139.7 };

function bathhouse(
  id: string,
  lat: number,
  lng: number,
  overrides: Partial<Bathhouse> = {},
): Bathhouse {
  return {
    id,
    name: id,
    address: `${id}の住所`,
    ward: "墨田区",
    lat,
    lng,
    hasSauna: false,
    openHour: 15,
    closeHour: 25,
    unionMember: true,
    active: true,
    ...overrides,
  };
}

function budget(bathhouseId: string): Budget {
  return {
    bathhouseId,
    fiscalYear: 2026,
    status: "confirmed",
    confirmedAt: "2026-04-01T00:00:00+09:00",
    confirmedBy: "東京都浴場組合",
    operatingDays: 312,
    price: 550,
    addon: 180,
    annualVisitors: 30000,
    fuel: 5400000,
    labor: 7200000,
    otherFixed: 2640000,
    depreciation: 1000000,
    subsidy: 900000,
    asset: 30000000,
    land: 50000000,
    cash: 4000000,
    targetCash: 4000000,
    yearsToCashTarget: 1,
    debt: 12000000,
    yearsToRenewal: 7,
    renewalCost: 32000000,
    loanRepayment: 2160000,
  };
}

describe("route selection", () => {
  it("selects the closest open active bathhouse first", () => {
    const result = buildRoute({
      from: point,
      startHour: 15,
      count: 1,
      bathhouses: [
        bathhouse("B001", 35.72, 139.7),
        bathhouse("B002", 35.701, 139.7),
        bathhouse("B003", 35.702, 139.7, { active: false }),
        bathhouse("B004", 35.703, 139.7, { openHour: 20 }),
      ],
      budgets: { B001: budget("B001"), B002: budget("B002") },
      todayCounts: { B001: 0, B002: 0 },
    });

    expect(result).toHaveLength(1);
    expect(result[0]?.bathhouse.id).toBe("B002");
  });

  it("uses the suggestion score after the first bathhouse", () => {
    const result = buildRoute({
      from: point,
      startHour: 15,
      count: 3,
      bathhouses: [
        bathhouse("B001", 35.701, 139.7),
        bathhouse("B002", 35.702, 139.7),
        bathhouse("B003", 35.73, 139.7),
      ],
      budgets: {
        B001: budget("B001"),
        B002: budget("B002"),
        B003: { ...budget("B003"), yearsToRenewal: 1, renewalCost: 100000000 },
      },
      todayCounts: { B001: 100, B002: 100, B003: 0 },
    });

    expect(result.map((leg) => leg.bathhouse.id)).toEqual(["B001", "B003", "B002"]);
  });

  it("does not repeat a bathhouse and returns fewer legs when candidates run out", () => {
    const result = buildRoute({
      from: point,
      startHour: 15,
      count: 3,
      bathhouses: [bathhouse("B001", 35.701, 139.7)],
      budgets: { B001: budget("B001") },
      todayCounts: { B001: 0 },
    });

    expect(result).toHaveLength(1);
    expect(new Set(result.map((leg) => leg.bathhouse.id)).size).toBe(result.length);
  });

  it("returns an empty route when all bathhouses are closed", () => {
    const result = buildRoute({
      from: point,
      startHour: 10,
      count: 3,
      bathhouses: [bathhouse("B001", 35.701, 139.7, { openHour: 15 })],
      budgets: { B001: budget("B001") },
      todayCounts: { B001: 0 },
    });

    expect(result).toEqual([]);
  });
});

describe("route helpers", () => {
  it("calculates and orders suggestion scores", () => {
    expect(suggestionScore(1, 5)).toBeGreaterThan(suggestionScore(0, 5));
    expect(isOpen(bathhouse("B001", 35.7, 139.7), 15)).toBe(true);
    expect(isOpen(bathhouse("B001", 35.7, 139.7), 25)).toBe(false);
  });
});
