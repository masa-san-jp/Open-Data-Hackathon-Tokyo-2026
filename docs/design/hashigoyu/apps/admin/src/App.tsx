import { useMemo, useState, useSyncExternalStore } from "react";
import {
  achievementRate,
  annualSales,
  consecutiveShortfallDays,
  requiredDailyVisitors,
  reserveGap,
} from "domain/calc";
import { adviceFor } from "domain/advice";
import type { Bathhouse, Budget, DailyCount } from "domain/types";
import { store } from "store";
import { adminText as text } from "./admin.ja";

type View = "dashboard" | "bathhouse";
type EditableBudgetField =
  | "price"
  | "addon"
  | "annualVisitors"
  | "fuel"
  | "labor"
  | "otherFixed"
  | "depreciation"
  | "subsidy"
  | "asset"
  | "land"
  | "cash"
  | "debt"
  | "yearsToRenewal"
  | "renewalCost"
  | "loanRepayment";

const EDITABLE_FIELDS: Record<EditableBudgetField, string> = {
  price: text.price,
  addon: text.addon,
  annualVisitors: text.annualVisitors,
  fuel: text.fuel,
  labor: text.labor,
  otherFixed: text.otherFixed,
  depreciation: text.depreciation,
  subsidy: text.subsidy,
  asset: text.asset,
  land: text.land,
  cash: text.cash,
  debt: text.debt,
  yearsToRenewal: text.yearsToRenewal,
  renewalCost: text.renewalCost,
  loanRepayment: text.loanRepayment,
};

const PL_FIELDS: readonly EditableBudgetField[] = [
  "price",
  "addon",
  "annualVisitors",
  "fuel",
  "labor",
  "otherFixed",
  "depreciation",
  "subsidy",
];
const BS_FIELDS: readonly EditableBudgetField[] = [
  "asset",
  "land",
  "cash",
  "debt",
  "yearsToRenewal",
  "renewalCost",
];
const CF_FIELDS: readonly EditableBudgetField[] = ["loanRepayment"];

function subscribe(onStoreChange: () => void): () => void {
  return store.subscribe(() => onStoreChange());
}

function useStoreSnapshot() {
  return useSyncExternalStore(subscribe, store.getSnapshot, store.getSnapshot);
}

function yen(value: number): string {
  return `${Math.round(value).toLocaleString("ja-JP")}円`;
}

function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function latestCount(counts: readonly DailyCount[]): DailyCount {
  return counts[counts.length - 1] ?? {
    bathhouseId: "B000",
    date: "2026-08-22",
    total: 0,
    first: 0,
    hop: 0,
    unknown: 0,
  };
}

function statsFor(
  bathhouse: Bathhouse,
  budget: Budget,
  counts: readonly DailyCount[],
) {
  const today = latestCount(counts);
  const required = requiredDailyVisitors(budget);
  const hopRate = today.total > 0 ? today.hop / today.total : 0;
  return {
    bathhouse,
    today,
    required,
    achievement: achievementRate(today.total, required),
    hopRate,
    sales: annualSales({ ...budget, annualVisitors: today.total }),
    streak: consecutiveShortfallDays(counts, required),
  };
}

function HistoryChart({ counts, required }: { counts: readonly DailyCount[]; required: number }) {
  const max = Math.max(required, ...counts.map((count) => count.total), 1);
  const targetBottom = Math.min(96, (required / max) * 100);
  return (
    <div className="chart-wrap">
      <div className="chart" aria-label={text.historyTitle}>
        <div className="target-line" style={{ bottom: `${targetBottom}%` }} aria-hidden="true" />
        {counts.map((count) => (
          <div className="bar-column" key={count.date}>
            <div
              className={count.total >= required ? "bar achieved" : "bar"}
              style={{ height: `${Math.max(3, (count.total / max) * 100)}%` }}
              title={`${count.date}: ${count.total}${text.people}`}
            />
          </div>
        ))}
      </div>
      <div className="chart-caption">{text.targetLine}</div>
    </div>
  );
}

function BudgetFields({
  budget,
  fields,
  onChange,
}: {
  budget: Budget;
  fields: readonly EditableBudgetField[];
  onChange: (field: EditableBudgetField, value: number) => void;
}) {
  return (
    <div className="budget-fields">
      {fields.map((field) => (
        <label key={field}>
          <span>{EDITABLE_FIELDS[field]}</span>
          <input
            type="number"
            value={budget[field]}
            min={0}
            onChange={(event) => onChange(field, Number(event.target.value))}
          />
        </label>
      ))}
    </div>
  );
}

function BudgetGroup({
  title,
  budget,
  fields,
  onChange,
}: {
  title: string;
  budget: Budget;
  fields: readonly EditableBudgetField[];
  onChange: (field: EditableBudgetField, value: number) => void;
}) {
  return (
    <section className="budget-group">
      <h3>{title}</h3>
      <BudgetFields budget={budget} fields={fields} onChange={onChange} />
    </section>
  );
}

function Dashboard({
  stats,
  onSelect,
}: {
  stats: ReturnType<typeof statsFor>[];
  onSelect: (bathhouseId: string) => void;
}) {
  const totalVisitors = stats.reduce((sum, item) => sum + item.today.total, 0);
  const totalHops = stats.reduce((sum, item) => sum + item.today.hop, 0);
  const reached = stats.filter((item) => item.today.total >= item.required).length;
  const longShortfall = stats.filter((item) => item.streak >= 30).length;
  return (
    <section className="dashboard-view">
      <div className="summary-grid">
        <div><span>{text.participants}</span><b>{stats.length}</b></div>
        <div><span>{text.reached}</span><b>{reached}</b></div>
        <div><span>{text.longShortfall}</span><b>{longShortfall}</b></div>
        <div><span>{text.hopRate}</span><b>{percent(totalVisitors ? totalHops / totalVisitors : 0)}</b></div>
      </div>
      <section className="dashboard-panel">
        <div className="section-title-row"><h2>{text.today}</h2></div>
        <div className="table-scroll">
          <table>
            <thead><tr>
              <th>{text.bathhouse}</th><th>{text.today}</th><th>{text.target}</th><th>{text.achievement}</th>
              <th>{text.first}</th><th>{text.hop}</th><th>{text.sales}</th><th>{text.streak}</th>
            </tr></thead>
            <tbody>
              {stats.map((item) => (
                <tr key={item.bathhouse.id} className={item.streak >= 30 ? "critical" : ""} onClick={() => onSelect(item.bathhouse.id)}>
                  <td><button type="button" className="row-button">{item.bathhouse.name}<small>{item.bathhouse.address}</small></button></td>
                  <td>{item.today.total}</td><td>{item.required}</td><td className={item.achievement >= 1 ? "good" : ""}>{percent(item.achievement)}</td>
                  <td>{Math.max(0, item.today.total - item.today.hop)}</td><td>{item.today.hop}</td>
                  <td>{yen(item.sales)}</td><td className={item.streak >= 30 ? "bad" : "muted"}>{item.streak || text.noValue}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

function Detail({
  bathhouse,
  budget,
  counts,
  onBack,
  onSelect,
}: {
  bathhouse: Bathhouse;
  budget: Budget;
  counts: readonly DailyCount[];
  onBack: () => void;
  onSelect: (bathhouseId: string) => void;
}) {
  const today = latestCount(counts);
  const required = requiredDailyVisitors(budget);
  const hopRate = today.total > 0 ? today.hop / today.total : 0;
  const advice = adviceFor(budget, today.total, hopRate);
  const update = (field: EditableBudgetField, value: number): void => {
    store.updateBudget(bathhouse.id, { [field]: value });
  };
  const confirm = (): void => {
    store.confirmBudget(bathhouse.id, new Date().toISOString(), "東京都浴場組合");
  };
  return (
    <section className="detail-view">
      <div className="detail-toolbar">
        <button type="button" className="back-button" onClick={onBack}>← {text.dashboard}</button>
        <label className="bathhouse-selector">
          <span>{text.selectorLabel}</span>
          <select value={bathhouse.id} onChange={(event) => onSelect(event.target.value)}>
            {/* 選択肢の銭湯名・住所・人数・金額はすべて架空のサンプルです。 */}
            {store.getSnapshot().bathhouses.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
        </label>
      </div>
      <div className="detail-kpis">
        <div><span>{text.kpiToday}</span><b>{today.total}{text.people}</b></div>
        <div><span>{text.kpiRequired}</span><b>{required}{text.people}</b></div>
        <div><span>{text.kpiAchievement}</span><b>{percent(achievementRate(today.total, required))}</b></div>
        <div><span>{text.kpiReserve}</span><b className={reserveGap(budget) < 0 ? "bad" : "good"}>{yen(reserveGap(budget))}</b></div>
      </div>
      <section className="detail-panel">
        <div className="section-title-row"><h2>{text.historyTitle}</h2><span>{text.targetLine}</span></div>
        <HistoryChart counts={counts} required={required} />
      </section>
      <section className="detail-panel">
        <div className="section-title-row">
          <h2>{text.budgetTitle}</h2>
          <span className={budget.status === "confirmed" ? "confirmed" : "draft"}>
            {budget.status === "confirmed" ? text.confirmed : text.draft}
          </span>
        </div>
        <div className="budget-meta">{text.confirmedDate}: {budget.confirmedAt?.slice(0, 10) ?? text.noValue} ／ {text.confirmedBy}: {budget.confirmedBy ?? text.noValue}</div>
        <div className="budget-edit-grid">
          <BudgetGroup title={text.pl} budget={budget} fields={PL_FIELDS} onChange={update} />
          <BudgetGroup title={text.bs} budget={budget} fields={BS_FIELDS} onChange={update} />
          <BudgetGroup title={text.cf} budget={budget} fields={CF_FIELDS} onChange={update} />
        </div>
        <button type="button" className="confirm-button" onClick={confirm}>{text.confirm}</button>
      </section>
      <section className="detail-panel">
        <h2>{text.adviceTitle}</h2>
        {advice.length > 0 ? <ul className="advice-list">{advice.map((item) => <li key={item.id}><span className={`priority priority-${item.priority}`}>{item.priority}</span><div><h3>{item.title}</h3><p>{item.reason}</p><strong>{item.action}</strong></div></li>)}</ul> : <p className="empty-advice">{text.noAdvice}</p>}
      </section>
    </section>
  );
}

export function App() {
  const snapshot = useStoreSnapshot();
  const [view, setView] = useState<View>("dashboard");
  const [selectedId, setSelectedId] = useState("B001");
  const stats = useMemo(
    () => snapshot.bathhouses.filter((bathhouse) => bathhouse.active).map((bathhouse) => statsFor(bathhouse, snapshot.budgets[bathhouse.id]!, snapshot.dailyCounts[bathhouse.id] ?? [])),
    [snapshot],
  );
  const selectedBathhouse = snapshot.bathhouses.find((bathhouse) => bathhouse.id === selectedId) ?? snapshot.bathhouses[0];

  const openDetail = (bathhouseId: string): void => {
    setSelectedId(bathhouseId);
    setView("bathhouse");
  };

  return (
    <main className="admin-app">
      <header className="admin-header">
        <h1>{text.title}</h1>
        <nav aria-label="画面">
          <button type="button" className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}>{text.dashboard}</button>
          <button type="button" className={view === "bathhouse" ? "active" : ""} onClick={() => setView("bathhouse")} disabled={!selectedBathhouse}>{text.bathhouse}</button>
        </nav>
      </header>
      {view === "dashboard" ? <Dashboard stats={stats} onSelect={openDetail} /> : selectedBathhouse ? <Detail bathhouse={selectedBathhouse} budget={snapshot.budgets[selectedBathhouse.id]!} counts={snapshot.dailyCounts[selectedBathhouse.id] ?? []} onBack={() => setView("dashboard")} onSelect={openDetail} /> : null}
      <p className="sample-notice">{text.sampleNotice}</p>
    </main>
  );
}
