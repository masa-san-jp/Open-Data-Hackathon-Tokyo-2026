import { describe, expect, it } from "vitest";
import { adviceFor, buildAdvice } from "../src/advice";
import type { Budget } from "../src/types";

const baseBudget: Budget = {
  bathhouseId: "B001",
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
  debt: 12000000,
  yearsToRenewal: 7,
  renewalCost: 32000000,
  loanRepayment: 2160000,
};

describe("advice", () => {
  it("returns urgent renewal advice without the short renewal duplicate", () => {
    const result = adviceFor(
      { ...baseBudget, yearsToRenewal: 1, renewalCost: 32000000 },
      100,
      0.2,
    );

    expect(result.map((item) => item.id)).toContain("RENEWAL_URGENT");
    expect(result.map((item) => item.id)).not.toContain("RENEWAL_SHORT");
  });

  it("returns advice in priority order", () => {
    const result = buildAdvice({
      budget: { ...baseBudget, addon: 40, fuel: 10000000, yearsToRenewal: 1, renewalCost: 32000000 },
      todayCount: 0,
      requiredDailyVisitors: 100,
      hopRate: 0,
    });

    expect(result.map((item) => item.priority)).toEqual([1, 1, 2, 2, 3]);
  });

  it("returns no advice when every condition is clear", () => {
    const result = buildAdvice({
      budget: { ...baseBudget, addon: 100, fuel: 1000000, yearsToRenewal: 10 },
      todayCount: 100,
      requiredDailyVisitors: 100,
      hopRate: 0.12,
    });

    expect(result).toEqual([]);
  });
});
