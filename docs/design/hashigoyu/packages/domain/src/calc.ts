import type { Budget, DailyCount } from "./types";

export type TravelMode = "walk" | "transit";

export interface GeoPoint {
  lat: number;
  lng: number;
}

export function unitRevenue(budget: Budget): number {
  return budget.price + budget.addon;
}

export function annualFixed(budget: Budget): number {
  return budget.fuel + budget.labor + budget.otherFixed;
}

export function annualRenewalReserve(budget: Budget): number {
  return budget.yearsToRenewal > 0
    ? budget.renewalCost / budget.yearsToRenewal
    : budget.renewalCost;
}

export function requiredDailyVisitors(budget: Budget): number {
  const revenue = unitRevenue(budget);
  if (revenue <= 0) {
    return 1;
  }

  return Math.max(
    1,
    Math.ceil(
      (annualFixed(budget) +
        budget.loanRepayment +
        annualRenewalReserve(budget) -
        budget.subsidy) /
        budget.operatingDays /
        revenue,
    ),
  );
}

export function annualSales(budget: Budget): number {
  return unitRevenue(budget) * budget.annualVisitors;
}

export function operatingProfit(budget: Budget): number {
  return annualSales(budget) - annualFixed(budget) - budget.depreciation + budget.subsidy;
}

export function netAssets(budget: Budget): number {
  return budget.asset + budget.cash - budget.debt;
}

export function operatingCF(budget: Budget): number {
  return operatingProfit(budget) + budget.depreciation;
}

export function freeCash(budget: Budget): number {
  return operatingCF(budget) - budget.loanRepayment;
}

export function reserveGap(budget: Budget): number {
  return freeCash(budget) - annualRenewalReserve(budget);
}

export function achievementRate(today: number, required: number): number {
  return today / required;
}

export function shortfallRate(today: number, required: number): number {
  return Math.max(0, (required - today) / required);
}

export function consecutiveShortfallDays(
  counts: readonly DailyCount[],
  required: number,
): number {
  const recentFirst = [...counts].sort((a, b) => b.date.localeCompare(a.date));
  let days = 0;

  for (const count of recentFirst) {
    if (count.total >= required) {
      break;
    }
    days += 1;
  }

  return days;
}

export function haversineKm(a: GeoPoint, b: GeoPoint): number {
  const earthRadiusKm = 6371;
  const toRadians = (degrees: number): number => (degrees * Math.PI) / 180;
  const latitudeDifference = toRadians(b.lat - a.lat);
  const longitudeDifference = toRadians(b.lng - a.lng);
  const latitudeA = toRadians(a.lat);
  const latitudeB = toRadians(b.lat);
  const halfChord =
    Math.sin(latitudeDifference / 2) ** 2 +
    Math.cos(latitudeA) * Math.cos(latitudeB) * Math.sin(longitudeDifference / 2) ** 2;

  return earthRadiusKm * 2 * Math.atan2(Math.sqrt(halfChord), Math.sqrt(1 - halfChord));
}

export function walkMinutes(a: GeoPoint, b: GeoPoint): number {
  return Math.max(2, Math.round(haversineKm(a, b) * 13));
}

export function travelMinutes(a: GeoPoint, b: GeoPoint): number {
  const walkingMinutes = walkMinutes(a, b);
  return walkingMinutes <= 18 ? walkingMinutes : Math.round(walkingMinutes * 0.55);
}

export function travelMode(a: GeoPoint, b: GeoPoint): TravelMode {
  return walkMinutes(a, b) <= 18 ? "walk" : "transit";
}
