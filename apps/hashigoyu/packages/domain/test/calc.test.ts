import { describe, expect, it } from "vitest";
import {
  achievementRate,
  annualCashIncrease,
  annualFixed,
  annualRequiredRevenue,
  annualRenewalReserve,
  annualSales,
  consecutiveShortfallDays,
  freeCash,
  haversineKm,
  netAssets,
  operatingCF,
  operatingProfit,
  requiredDailyVisitors,
  reserveGap,
  shortfallRate,
  travelMinutes,
  travelMode,
  unitRevenue,
  walkMinutes,
} from "../src/calc";
import type { Budget, DailyCount } from "../src/types";

const budgetA: Budget = {
  bathhouseId: "B001",
  fiscalYear: 2026,
  status: "draft",
  confirmedAt: null,
  confirmedBy: null,
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

const budgetB: Budget = {
  ...budgetA,
  price: 480,
  addon: 40,
  fuel: 4200000,
  labor: 4400000,
  otherFixed: 1900000,
  subsidy: 500000,
  loanRepayment: 720000,
  yearsToRenewal: 1,
  renewalCost: 26000000,
};

describe("budget calculations", () => {
  it("calculates the specified budget A values", () => {
    expect(unitRevenue(budgetA)).toBe(730);
    expect(annualFixed(budgetA)).toBe(15240000);
    expect(annualRenewalReserve(budgetA)).toBeCloseTo(32000000 / 7);
    expect(requiredDailyVisitors(budgetA)).toBe(93);
  });

  it("calculates the specified budget B values", () => {
    expect(unitRevenue(budgetB)).toBe(520);
    expect(annualFixed(budgetB)).toBe(10500000);
    expect(annualRenewalReserve(budgetB)).toBe(26000000);
    expect(requiredDailyVisitors(budgetB)).toBe(227);
  });

  it("returns one visitor when unit revenue is not positive", () => {
    expect(requiredDailyVisitors({ ...budgetA, price: -550, addon: 550 })).toBe(1);
    expect(requiredDailyVisitors({ ...budgetA, price: 0, addon: 0 })).toBe(1);
  });

  it("uses the full renewal cost when renewal is due this year", () => {
    expect(annualRenewalReserve({ ...budgetA, yearsToRenewal: 0 })).toBe(32000000);
  });

  it("spreads the cash gap over the years to the cash target", () => {
    expect(
      annualCashIncrease({
        ...budgetA,
        cash: 4000000,
        targetCash: 10000000,
        yearsToCashTarget: 2,
      }),
    ).toBe(3000000);
  });

  it("uses the full cash gap when the cash target is due this year", () => {
    expect(
      annualCashIncrease({
        ...budgetA,
        cash: 4000000,
        targetCash: 10000000,
        yearsToCashTarget: 0,
      }),
    ).toBe(6000000);
  });

  it("does not increase cash when the current cash meets the target", () => {
    expect(annualCashIncrease({ ...budgetA, targetCash: 4000000 })).toBe(0);
    expect(annualCashIncrease({ ...budgetA, targetCash: 3000000 })).toBe(0);
  });

  it("includes the cash increase in annual required revenue and daily visitors", () => {
    const withCashTarget = {
      ...budgetA,
      targetCash: 10000000,
      yearsToCashTarget: 2,
    };

    expect(annualRequiredRevenue(withCashTarget)).toBeCloseTo(
      annualFixed(budgetA) +
        budgetA.loanRepayment +
        annualRenewalReserve(budgetA) +
        3000000 -
        budgetA.subsidy,
    );
    expect(requiredDailyVisitors(withCashTarget)).toBeGreaterThan(
      requiredDailyVisitors(budgetA),
    );
  });

  it("calculates PL, BS and CF values", () => {
    expect(annualSales(budgetA)).toBe(21900000);
    expect(operatingProfit(budgetA)).toBe(6560000);
    expect(netAssets(budgetA)).toBe(22000000);
    expect(operatingCF(budgetA)).toBe(7560000);
    expect(freeCash(budgetA)).toBe(5400000);
    expect(reserveGap(budgetA)).toBeCloseTo(5400000 - 32000000 / 7);
  });

  it("calculates achievement and shortfall rates", () => {
    expect(achievementRate(50, 100)).toBe(0.5);
    expect(shortfallRate(50, 100)).toBe(0.5);
    expect(shortfallRate(120, 100)).toBe(0);
  });
});

describe("daily counts", () => {
  it("counts consecutive shortfall days from the most recent date", () => {
    const counts: DailyCount[] = [
      { bathhouseId: "B001", date: "2026-08-20", total: 100, first: 70, hop: 30, unknown: 0 },
      { bathhouseId: "B001", date: "2026-08-22", total: 0, first: 0, hop: 0, unknown: 0 },
      { bathhouseId: "B001", date: "2026-08-21", total: 90, first: 80, hop: 10, unknown: 0 },
    ];

    expect(consecutiveShortfallDays(counts, 100)).toBe(2);
  });
});

describe("travel calculations", () => {
  const near = { lat: 35.7000, lng: 139.7000 };
  const far = { lat: 35.8000, lng: 139.7000 };

  it("calculates a zero distance and enforces the two-minute minimum", () => {
    expect(haversineKm(near, near)).toBe(0);
    expect(walkMinutes(near, near)).toBe(2);
  });

  it("uses walking for short trips and transit for long trips", () => {
    expect(travelMode(near, { lat: 35.7010, lng: 139.7000 })).toBe("walk");
    expect(travelMinutes(near, far)).toBe(Math.round(walkMinutes(near, far) * 0.55));
    expect(travelMode(near, far)).toBe("transit");
  });

});
