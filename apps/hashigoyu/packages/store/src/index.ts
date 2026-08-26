import type {
  Bathhouse,
  BathhouseId,
  Budget,
  DailyCount,
  ISODateTime,
} from "domain/types";

// このファイルの銭湯名・住所・人数・金額はすべて架空のサンプルです。

export interface StoreSnapshot {
  bathhouses: readonly Bathhouse[];
  budgets: Readonly<Record<BathhouseId, Budget>>;
  dailyCounts: Readonly<Record<BathhouseId, readonly DailyCount[]>>;
}

export type StoreListener = (snapshot: StoreSnapshot) => void;

const STORE_CHANNEL = "hashigoyu-store";

export interface HashigoyuStore {
  getSnapshot(): StoreSnapshot;
  subscribe(listener: StoreListener): () => void;
  updateBudget(bathhouseId: BathhouseId, patch: Partial<Budget>): void;
  confirmBudget(bathhouseId: BathhouseId, confirmedAt: ISODateTime, confirmedBy: string): void;
  incrementToday(bathhouseId: BathhouseId): void;
  decrementToday(bathhouseId: BathhouseId): void;
}

const SAMPLE_DATES = [
  "2026-07-24",
  "2026-07-25",
  "2026-07-26",
  "2026-07-27",
  "2026-07-28",
  "2026-07-29",
  "2026-07-30",
  "2026-07-31",
  "2026-08-01",
  "2026-08-02",
  "2026-08-03",
  "2026-08-04",
  "2026-08-05",
  "2026-08-06",
  "2026-08-07",
  "2026-08-08",
  "2026-08-09",
  "2026-08-10",
  "2026-08-11",
  "2026-08-12",
  "2026-08-13",
  "2026-08-14",
  "2026-08-15",
  "2026-08-16",
  "2026-08-17",
  "2026-08-18",
  "2026-08-19",
  "2026-08-20",
  "2026-08-21",
  "2026-08-22",
] as const;

const SAMPLE_BATHHOUSES: readonly Bathhouse[] = [
  {
    id: "B001",
    name: "松の湯",
    address: "東京都墨田区東向島3-2-11",
    ward: "墨田区",
    lat: 35.7196,
    lng: 139.8206,
    hasSauna: true,
    openHour: 15,
    closeHour: 25,
    unionMember: true,
    active: true,
  },
  {
    id: "B002",
    name: "あけぼの湯",
    address: "東京都墨田区京島2-4-8",
    ward: "墨田区",
    lat: 35.7148,
    lng: 139.8172,
    hasSauna: false,
    openHour: 15,
    closeHour: 24,
    unionMember: true,
    active: true,
  },
  {
    id: "B003",
    name: "富士見湯",
    address: "東京都台東区三ノ輪1-9-3",
    ward: "台東区",
    lat: 35.7318,
    lng: 139.7913,
    hasSauna: true,
    openHour: 14,
    closeHour: 24.5,
    unionMember: true,
    active: true,
  },
  {
    id: "B004",
    name: "鶴亀湯",
    address: "東京都荒川区町屋4-6-1",
    ward: "荒川区",
    lat: 35.7443,
    lng: 139.7817,
    hasSauna: true,
    openHour: 15,
    closeHour: 25,
    unionMember: true,
    active: true,
  },
  {
    id: "B005",
    name: "若葉湯",
    address: "東京都江東区森下2-11-5",
    ward: "江東区",
    lat: 35.6899,
    lng: 139.7982,
    hasSauna: false,
    openHour: 13,
    closeHour: 23.5,
    unionMember: true,
    active: true,
  },
  {
    id: "B006",
    name: "日の出湯",
    address: "東京都墨田区錦糸4-3-7",
    ward: "墨田区",
    lat: 35.697,
    lng: 139.814,
    hasSauna: true,
    openHour: 16,
    closeHour: 24,
    unionMember: true,
    active: true,
  },
];

function sampleBudget(
  bathhouseId: BathhouseId,
  values: Omit<Budget, "bathhouseId">,
): Budget {
  return { bathhouseId, ...values };
}

const SAMPLE_BUDGETS: Readonly<Record<BathhouseId, Budget>> = {
  B001: sampleBudget("B001", {
    fiscalYear: 2026,
    status: "confirmed",
    confirmedAt: "2026-04-01T09:00:00+09:00",
    confirmedBy: "東京都浴場組合",
    operatingDays: 312,
    price: 550,
    addon: 180,
    annualVisitors: 36000,
    fuel: 5400000,
    labor: 7200000,
    otherFixed: 2640000,
    depreciation: 2600000,
    subsidy: 900000,
    asset: 22000000,
    land: 180000000,
    cash: 3800000,
    debt: 14000000,
    yearsToRenewal: 7,
    renewalCost: 32000000,
    loanRepayment: 2160000,
  }),
  B002: sampleBudget("B002", {
    fiscalYear: 2026,
    status: "confirmed",
    confirmedAt: "2026-04-01T09:00:00+09:00",
    confirmedBy: "東京都浴場組合",
    operatingDays: 312,
    price: 550,
    addon: 60,
    annualVisitors: 22000,
    fuel: 4600000,
    labor: 5000000,
    otherFixed: 2100000,
    depreciation: 1400000,
    subsidy: 600000,
    asset: 9000000,
    land: 150000000,
    cash: 900000,
    debt: 6000000,
    yearsToRenewal: 3,
    renewalCost: 28000000,
    loanRepayment: 1200000,
  }),
  B003: sampleBudget("B003", {
    fiscalYear: 2026,
    status: "confirmed",
    confirmedAt: "2026-04-01T09:00:00+09:00",
    confirmedBy: "東京都浴場組合",
    operatingDays: 312,
    price: 550,
    addon: 290,
    annualVisitors: 44000,
    fuel: 6200000,
    labor: 9600000,
    otherFixed: 3400000,
    depreciation: 3800000,
    subsidy: 1400000,
    asset: 41000000,
    land: 210000000,
    cash: 7200000,
    debt: 26000000,
    yearsToRenewal: 12,
    renewalCost: 36000000,
    loanRepayment: 3000000,
  }),
  B004: sampleBudget("B004", {
    fiscalYear: 2026,
    status: "confirmed",
    confirmedAt: "2026-04-01T09:00:00+09:00",
    confirmedBy: "東京都浴場組合",
    operatingDays: 312,
    price: 550,
    addon: 340,
    annualVisitors: 48000,
    fuel: 5800000,
    labor: 8800000,
    otherFixed: 3100000,
    depreciation: 3200000,
    subsidy: 1100000,
    asset: 36000000,
    land: 160000000,
    cash: 9400000,
    debt: 19000000,
    yearsToRenewal: 15,
    renewalCost: 34000000,
    loanRepayment: 2400000,
  }),
  B005: sampleBudget("B005", {
    fiscalYear: 2026,
    status: "confirmed",
    confirmedAt: "2026-04-01T09:00:00+09:00",
    confirmedBy: "東京都浴場組合",
    operatingDays: 312,
    price: 480,
    addon: 40,
    annualVisitors: 16000,
    fuel: 4200000,
    labor: 4400000,
    otherFixed: 1900000,
    depreciation: 900000,
    subsidy: 500000,
    asset: 5000000,
    land: 140000000,
    cash: 400000,
    debt: 3000000,
    yearsToRenewal: 1,
    renewalCost: 26000000,
    loanRepayment: 720000,
  }),
  B006: sampleBudget("B006", {
    fiscalYear: 2026,
    status: "confirmed",
    confirmedAt: "2026-04-01T09:00:00+09:00",
    confirmedBy: "東京都浴場組合",
    operatingDays: 312,
    price: 550,
    addon: 120,
    annualVisitors: 28000,
    fuel: 5000000,
    labor: 6200000,
    otherFixed: 2300000,
    depreciation: 1800000,
    subsidy: 700000,
    asset: 15000000,
    land: 130000000,
    cash: 1800000,
    debt: 9000000,
    yearsToRenewal: 5,
    renewalCost: 30000000,
    loanRepayment: 1500000,
  }),
};

const SAMPLE_HISTORIES: Readonly<Record<BathhouseId, readonly number[]>> = {
  B001: [112, 98, 121, 133, 88, 104, 119, 127, 95, 110, 131, 102, 87, 118, 124, 99, 106, 128, 113, 91, 120, 135, 101, 94, 117, 122, 108, 86, 115, 64],
  B002: [62, 55, 71, 48, 66, 59, 74, 51, 63, 45, 68, 57, 49, 72, 54, 61, 47, 66, 52, 58, 70, 44, 60, 53, 67, 49, 56, 62, 41, 38],
  B003: [143, 152, 131, 148, 160, 127, 155, 139, 166, 134, 149, 158, 142, 171, 136, 153, 145, 162, 130, 157, 140, 168, 133, 151, 146, 164, 138, 150, 159, 118],
  B004: [128, 141, 119, 136, 150, 124, 145, 132, 158, 127, 139, 148, 131, 161, 125, 143, 137, 154, 122, 147, 133, 159, 126, 142, 138, 156, 129, 144, 151, 152],
  B005: [51, 44, 58, 39, 53, 47, 61, 36, 49, 42, 56, 33, 48, 40, 54, 37, 45, 51, 34, 46, 38, 52, 31, 43, 49, 35, 41, 47, 30, 29],
  B006: [74, 68, 81, 77, 63, 72, 85, 70, 79, 66, 88, 73, 71, 84, 76, 69, 82, 75, 64, 80, 86, 78, 67, 83, 72, 81, 77, 74, 70, 65],
};

function makeDailyCounts(
  bathhouseId: BathhouseId,
  history: readonly number[],
): readonly DailyCount[] {
  return history.map((total, index) => {
    const hop = Math.round(total * 0.2);
    return {
      bathhouseId,
      date: SAMPLE_DATES[index] ?? SAMPLE_DATES[SAMPLE_DATES.length - 1],
      total,
      first: total - hop,
      hop,
      unknown: 0,
    };
  });
}

const SAMPLE_DAILY_COUNTS: Readonly<Record<BathhouseId, readonly DailyCount[]>> = {
  B001: makeDailyCounts("B001", SAMPLE_HISTORIES.B001),
  B002: makeDailyCounts("B002", SAMPLE_HISTORIES.B002),
  B003: makeDailyCounts("B003", SAMPLE_HISTORIES.B003),
  B004: makeDailyCounts("B004", SAMPLE_HISTORIES.B004),
  B005: makeDailyCounts("B005", SAMPLE_HISTORIES.B005),
  B006: makeDailyCounts("B006", SAMPLE_HISTORIES.B006),
};

export function createSampleSnapshot(): StoreSnapshot {
  return {
    bathhouses: SAMPLE_BATHHOUSES.map((bathhouse) => ({ ...bathhouse })),
    budgets: Object.fromEntries(
      Object.entries(SAMPLE_BUDGETS).map(([id, budget]) => [id, { ...budget }]),
    ),
    dailyCounts: Object.fromEntries(
      Object.entries(SAMPLE_DAILY_COUNTS).map(([id, counts]) => [
        id,
        counts.map((count) => ({ ...count })),
      ]),
    ),
  };
}

function cloneSnapshot(snapshot: StoreSnapshot): StoreSnapshot {
  return {
    bathhouses: snapshot.bathhouses.map((bathhouse) => ({ ...bathhouse })),
    budgets: Object.fromEntries(
      Object.entries(snapshot.budgets).map(([id, budget]) => [id, { ...budget }]),
    ),
    dailyCounts: Object.fromEntries(
      Object.entries(snapshot.dailyCounts).map(([id, counts]) => [
        id,
        counts.map((count) => ({ ...count })),
      ]),
    ),
  };
}

export function createStore(initialSnapshot: StoreSnapshot = createSampleSnapshot()): HashigoyuStore {
  let snapshot = cloneSnapshot(initialSnapshot);
  const listeners = new Set<StoreListener>();
  const channel =
    typeof window !== "undefined" && typeof BroadcastChannel !== "undefined"
      ? new BroadcastChannel(STORE_CHANNEL)
      : null;

  const notify = (): void => {
    for (const listener of listeners) {
      listener(snapshot);
    }
  };

  const publish = (): void => {
    channel?.postMessage(snapshot);
  };

  if (channel) {
    channel.addEventListener("message", (event: MessageEvent<StoreSnapshot>) => {
      snapshot = cloneSnapshot(event.data);
      notify();
    });
  }

  return {
    getSnapshot: () => snapshot,
    subscribe: (listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    updateBudget: (bathhouseId, patch) => {
      const current = snapshot.budgets[bathhouseId];
      if (!current) {
        return;
      }

      snapshot = {
        ...snapshot,
        budgets: {
          ...snapshot.budgets,
          [bathhouseId]: {
            ...current,
            ...patch,
            bathhouseId,
            status: "draft",
            confirmedAt: null,
            confirmedBy: null,
          },
        },
      };
      notify();
      publish();
    },
    confirmBudget: (bathhouseId, confirmedAt, confirmedBy) => {
      const current = snapshot.budgets[bathhouseId];
      if (!current) {
        return;
      }

      snapshot = {
        ...snapshot,
        budgets: {
          ...snapshot.budgets,
          [bathhouseId]: {
            ...current,
            status: "confirmed",
            confirmedAt,
            confirmedBy,
          },
        },
      };
      notify();
      publish();
    },
    incrementToday: (bathhouseId) => {
      updateLatestCount(1, bathhouseId);
    },
    decrementToday: (bathhouseId) => {
      updateLatestCount(-1, bathhouseId);
    },
  };

  function updateLatestCount(delta: 1 | -1, bathhouseId: BathhouseId): void {
    const counts = snapshot.dailyCounts[bathhouseId];
    if (!counts || counts.length === 0) {
      return;
    }
    const lastIndex = counts.length - 1;
    const last = counts[lastIndex];
    if (!last || (delta < 0 && last.total === 0)) {
      return;
    }

    const nextCount: DailyCount = {
      ...last,
      total: last.total + delta,
      unknown: Math.max(0, last.unknown + delta),
    };
    if (delta < 0 && last.unknown === 0) {
      nextCount.first = Math.max(0, last.first - 1);
    }

    snapshot = {
      ...snapshot,
      dailyCounts: {
        ...snapshot.dailyCounts,
        [bathhouseId]: counts.map((count, index) => (index === lastIndex ? nextCount : count)),
      },
    };
    notify();
    publish();
  }
}

export const store = createStore();
