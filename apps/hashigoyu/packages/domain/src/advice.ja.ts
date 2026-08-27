import type { AdviceId } from "./advice";

export interface AdviceCopyContext {
  reserveGap: number;
  yearsToRenewal: number;
  todayCount: number;
  requiredDailyVisitors: number;
  addon: number;
  hopRate: number;
  fuelRate: number;
}

interface AdviceCopy {
  title: string;
  reason: (context: AdviceCopyContext) => string;
  action: string;
}

function yen(value: number): string {
  return Math.round(Math.abs(value)).toLocaleString("ja-JP");
}

function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export const adviceCopy: Record<AdviceId, AdviceCopy> = {
  RENEWAL_URGENT: {
    title: "更新積立不足（緊急）",
    reason: (context) =>
      `次の更新まで${context.yearsToRenewal}年、積立との差額は${yen(context.reserveGap)}円です。`,
    action: "更新資金を確保",
  },
  RENEWAL_SHORT: {
    title: "更新積立不足",
    reason: (context) => `更新費用に対して${yen(context.reserveGap)}円不足しています。`,
    action: "更新資金を確認",
  },
  VISITORS_SHORT: {
    title: "必要客数不足",
    reason: (context) =>
      `今日の来客は${context.todayCount}人、必要客数は${context.requiredDailyVisitors}人です。`,
    action: "はしご提案の受入先に設定",
  },
  ADDON_LOW: {
    title: "客単価上乗せ低",
    reason: (context) => `1人あたりの上乗せは${context.addon}円です。`,
    action: "サウナ・物販の構成を確認",
  },
  HOP_LOW: {
    title: "はしご率低",
    reason: (context) => `はしご率は${percent(context.hopRate)}です。`,
    action: "2軒め候補としての掲載条件を確認",
  },
  FUEL_HIGH: {
    title: "燃料費比率高",
    reason: (context) => `固定費に占める燃料費は${percent(context.fuelRate)}です。`,
    action: "燃料・水道費を確認",
  },
};
