import { annualFixed, requiredDailyVisitors, reserveGap } from "./calc";
import { adviceCopy, type AdviceCopyContext } from "./advice.ja";
import type { Budget } from "./types";

export type AdviceId =
  | "RENEWAL_URGENT"
  | "RENEWAL_SHORT"
  | "VISITORS_SHORT"
  | "ADDON_LOW"
  | "HOP_LOW"
  | "FUEL_HIGH";

export type AdvicePriority = 1 | 2 | 3;

export interface AdviceInput {
  budget: Budget;
  todayCount: number;
  requiredDailyVisitors: number;
  hopRate: number;
}

export interface Advice {
  id: AdviceId;
  priority: AdvicePriority;
  title: string;
  reason: string;
  action: string;
}

interface AdviceCandidate {
  id: AdviceId;
  priority: AdvicePriority;
}

export function buildAdvice(input: AdviceInput): Advice[] {
  const gap = reserveGap(input.budget);
  const fixed = annualFixed(input.budget);
  const context: AdviceCopyContext = {
    reserveGap: gap,
    yearsToRenewal: input.budget.yearsToRenewal,
    todayCount: input.todayCount,
    requiredDailyVisitors: input.requiredDailyVisitors,
    addon: input.budget.addon,
    hopRate: input.hopRate,
    fuelRate: input.budget.fuel / fixed,
  };
  const candidates: AdviceCandidate[] = [];

  if (gap < 0 && input.budget.yearsToRenewal <= 3) {
    candidates.push({ id: "RENEWAL_URGENT", priority: 1 });
  } else if (gap < 0) {
    candidates.push({ id: "RENEWAL_SHORT", priority: 1 });
  }

  if (input.todayCount < input.requiredDailyVisitors * 0.6) {
    candidates.push({ id: "VISITORS_SHORT", priority: 1 });
  }
  if (input.budget.addon < 100) {
    candidates.push({ id: "ADDON_LOW", priority: 2 });
  }
  if (input.hopRate < 0.12) {
    candidates.push({ id: "HOP_LOW", priority: 2 });
  }
  if (input.budget.fuel / fixed > 0.34) {
    candidates.push({ id: "FUEL_HIGH", priority: 3 });
  }

  return candidates
    .sort((a, b) => a.priority - b.priority)
    .map((candidate) => {
      const copy = adviceCopy[candidate.id];
      return {
        ...candidate,
        title: copy.title,
        reason: copy.reason(context),
        action: copy.action,
      };
    });
}

export function adviceFor(
  budget: Budget,
  todayCount: number,
  hopRate: number,
): Advice[] {
  return buildAdvice({
    budget,
    todayCount,
    requiredDailyVisitors: requiredDailyVisitors(budget),
    hopRate,
  });
}
