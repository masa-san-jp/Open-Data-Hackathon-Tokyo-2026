import {
  requiredDailyVisitors,
  shortfallRate,
  travelMinutes,
  travelMode,
  type GeoPoint,
  type TravelMode,
} from "./calc";
import type { Bathhouse, Budget, BathhouseId } from "./types";

export const BATHE_HOURS = 1.1;
export const ALLOCATION_WEIGHT = 0.7;

export type RouteCount = 1 | 2 | 3;

export interface RouteInput {
  from: GeoPoint;
  startHour: number;
  count: RouteCount;
  bathhouses: readonly Bathhouse[];
  budgets: Readonly<Record<BathhouseId, Budget>>;
  todayCounts: Readonly<Record<BathhouseId, number>>;
}

export interface Leg {
  bathhouse: Bathhouse;
  travelMinutes: number;
  travelMode: TravelMode;
  arrivalHour: number;
}

export function suggestionScore(shortfall: number, minutes: number): number {
  return (
    ALLOCATION_WEIGHT * shortfall +
    (1 - ALLOCATION_WEIGHT) * (1 - Math.min(1, minutes / 35))
  );
}

export function isOpen(bathhouse: Bathhouse, hour: number): boolean {
  return hour >= bathhouse.openHour && hour < bathhouse.closeHour;
}

function pointOf(bathhouse: Bathhouse): GeoPoint {
  return { lat: bathhouse.lat, lng: bathhouse.lng };
}

function shortfallOf(
  bathhouse: Bathhouse,
  budgets: Readonly<Record<BathhouseId, Budget>>,
  todayCounts: Readonly<Record<BathhouseId, number>>,
): number {
  const budget = budgets[bathhouse.id];
  if (!budget) {
    return 0;
  }

  return shortfallRate(todayCounts[bathhouse.id] ?? 0, requiredDailyVisitors(budget));
}

export function buildRoute(input: RouteInput): Leg[] {
  let current = input.from;
  let hour = input.startHour;
  const visited = new Set<BathhouseId>();
  const legs: Leg[] = [];

  for (let index = 0; index < input.count; index += 1) {
    const candidates = input.bathhouses.filter((bathhouse) => {
      if (!bathhouse.active || visited.has(bathhouse.id)) {
        return false;
      }

      const minutes = travelMinutes(current, pointOf(bathhouse));
      return isOpen(bathhouse, hour + minutes / 60 + 0.1);
    });

    if (candidates.length === 0) {
      break;
    }

    const ranked = candidates.map((bathhouse, candidateIndex) => ({
      bathhouse,
      candidateIndex,
      minutes: travelMinutes(current, pointOf(bathhouse)),
    }));

    ranked.sort((a, b) => {
      if (index === 0) {
        return a.minutes - b.minutes || a.candidateIndex - b.candidateIndex;
      }

      const scoreDifference =
        suggestionScore(
          shortfallOf(a.bathhouse, input.budgets, input.todayCounts),
          a.minutes,
        ) -
        suggestionScore(
          shortfallOf(b.bathhouse, input.budgets, input.todayCounts),
          b.minutes,
        );
      return scoreDifference * -1 || a.candidateIndex - b.candidateIndex;
    });

    const pick = ranked[0];
    if (!pick) {
      break;
    }

    hour += pick.minutes / 60;
    legs.push({
      bathhouse: pick.bathhouse,
      travelMinutes: pick.minutes,
      travelMode: travelMode(current, pointOf(pick.bathhouse)),
      arrivalHour: hour,
    });
    hour += BATHE_HOURS;
    current = pointOf(pick.bathhouse);
    visited.add(pick.bathhouse.id);
  }

  return legs;
}
