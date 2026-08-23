export type BathhouseId = string;
export type ISODate = string;
export type ISODateTime = string;

export interface Bathhouse {
  id: BathhouseId;
  name: string;
  address: string;
  ward: string;
  lat: number;
  lng: number;
  hasSauna: boolean;
  openHour: number;
  closeHour: number;
  unionMember: boolean;
  active: boolean;
}

export type BudgetStatus = "draft" | "confirmed";

export interface Budget {
  bathhouseId: BathhouseId;
  fiscalYear: number;
  status: BudgetStatus;
  confirmedAt: ISODateTime | null;
  confirmedBy: string | null;
  operatingDays: number;
  price: number;
  addon: number;
  annualVisitors: number;
  fuel: number;
  labor: number;
  otherFixed: number;
  depreciation: number;
  subsidy: number;
  asset: number;
  land: number;
  cash: number;
  debt: number;
  yearsToRenewal: number;
  renewalCost: number;
  loanRepayment: number;
}

export type VisitSource = "counter" | "qr" | "pos";

export interface Visit {
  id: string;
  bathhouseId: BathhouseId;
  at: ISODateTime;
  source: VisitSource;
  sessionId: string | null;
  sequence: number | null;
}

export interface DailyCount {
  bathhouseId: BathhouseId;
  date: ISODate;
  total: number;
  first: number;
  hop: number;
  unknown: number;
}
