import { useEffect, useMemo, useState, useSyncExternalStore } from "react";
import { achievementRate, requiredDailyVisitors, unitRevenue } from "domain/calc";
import { adviceFor } from "domain/advice";
import type { Budget, DailyCount } from "domain/types";
import { store } from "store";
import { counterText as text } from "./counter.ja";

type Tab = "counter" | "management";
const COUNTER_BATHHOUSE_ID = "B005";

function subscribe(onStoreChange: () => void): () => void {
  return store.subscribe(() => onStoreChange());
}

function useStoreSnapshot() {
  return useSyncExternalStore(subscribe, store.getSnapshot, store.getSnapshot);
}

function yen(value: number): string {
  return `${Math.round(value).toLocaleString("ja-JP")}円`;
}

function formatDate(value: string | null): string {
  return value ? value.slice(0, 10).replaceAll("-", "/") : "—";
}

function latestCount(counts: readonly DailyCount[]): DailyCount {
  return counts[counts.length - 1] ?? {
    bathhouseId: "B001",
    date: "2026-08-22",
    total: 0,
    first: 0,
    hop: 0,
    unknown: 0,
  };
}

function monthTotal(counts: readonly DailyCount[], date: string): number {
  const month = date.slice(0, 7);
  return counts
    .filter((count) => count.date.slice(0, 7) === month)
    .reduce((total, count) => total + count.total, 0);
}

function monthEndEstimate(counts: readonly DailyCount[]): number {
  const last = latestCount(counts);
  const currentMonthTotal = monthTotal(counts, last.date);
  const elapsedDays = Math.max(1, Number(last.date.slice(8, 10)));
  const daysInMonth = 31;
  return Math.round((currentMonthTotal / elapsedDays) * daysInMonth);
}

function breakdown(count: DailyCount): { first: number; hop: number } {
  const known = count.first + count.hop;
  if (known === 0) {
    return { first: 0, hop: count.total };
  }

  const first = Math.round((count.total * count.first) / known);
  return { first, hop: Math.max(0, count.total - first) };
}

function BudgetGroup({ title, fields }: { title: string; fields: Array<[string, string]> }) {
  return (
    <section className="budget-group">
      <h3>{title}</h3>
      <dl>
        {fields.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
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

function CounterView({ budget, count }: { budget: Budget; count: DailyCount }) {
  const required = requiredDailyVisitors(budget);
  const remaining = Math.max(0, required - count.total);
  const progress = Math.min(100, achievementRate(count.total, required) * 100);
  const share = breakdown(count);
  return (
    <section className="counter-view">
      <div className="remaining-panel">
        <div className="remaining-label">{text.remainingLabel}</div>
        <div className={remaining === 0 ? "remaining achieved" : "remaining"}>{remaining}</div>
        <div className="people-unit">{text.people}</div>
        <div className="progress-track" aria-label={`${text.target} ${required}${text.people}`}>
          <i style={{ width: `${progress}%` }} />
        </div>
        <div className="counter-kpis">
          <span>{text.today} <b>{count.total}</b></span>
          <span>{text.target} <b>{required}</b></span>
          <span>{text.sales} <b>{yen(unitRevenue(budget) * count.total)}</b></span>
        </div>
      </div>
      <div className="counter-actions">
        <button className="add-button" type="button" onClick={() => store.incrementToday(budget.bathhouseId)}>
          {text.addOne}<small>{text.addOneSub}</small>
        </button>
        <button className="subtract-button" type="button" onClick={() => store.decrementToday(budget.bathhouseId)}>
          {text.subtractOne}
        </button>
        <div className="breakdown">
          <h2>{text.firstHop}</h2>
          <div className="breakdown-values">
            <span>{text.first} <b>{share.first}</b></span>
            <span>{text.hop} <b>{share.hop}</b></span>
          </div>
          <div className="breakdown-bar">
            <i className="first-segment" style={{ width: `${count.total ? (share.first / count.total) * 100 : 0}%` }} />
            <i className="hop-segment" style={{ width: `${count.total ? (share.hop / count.total) * 100 : 0}%` }} />
          </div>
        </div>
      </div>
    </section>
  );
}

function ManagementView({ budget, counts }: { budget: Budget; counts: readonly DailyCount[] }) {
  const count = latestCount(counts);
  const required = requiredDailyVisitors(budget);
  const hopRate = count.total > 0 ? count.hop / count.total : 0;
  const advice = adviceFor(budget, count.total, hopRate);
  const currentMonth = monthTotal(counts, count.date);
  const estimate = monthEndEstimate(counts);
  return (
    <section className="management-view">
      <div className="management-kpis">
        <div><span>{text.todayVisitors}</span><b>{count.total}{text.people}</b></div>
        <div><span>{text.requiredVisitors}</span><b>{required}{text.people}</b></div>
        <div><span>{text.monthTotal}</span><b>{currentMonth}{text.people}</b></div>
        <div><span>{text.monthEstimate}</span><b>{estimate}{text.people}</b></div>
      </div>

      <section className="management-section">
        <div className="section-title-row"><h2>{text.historyTitle}</h2><span>{text.targetLine}</span></div>
        <HistoryChart counts={counts} required={required} />
      </section>

      <section className="management-section">
        <div className="section-title-row">
          <h2>{text.budgetTitle}</h2>
          <span className="confirmed-badge">{text.confirmed} {formatDate(budget.confirmedAt)}</span>
        </div>
        <div className="confirmed-by">{text.confirmedBy}: {budget.confirmedBy ?? "—"}</div>
        <div className="budget-grid">
          <BudgetGroup title={text.pl} fields={[
            [text.price, yen(budget.price)],
            [text.addon, yen(budget.addon)],
            [text.annualVisitors, `${budget.annualVisitors.toLocaleString("ja-JP")}${text.people}`],
            [text.fuel, yen(budget.fuel)],
            [text.labor, yen(budget.labor)],
            [text.otherFixed, yen(budget.otherFixed)],
            [text.depreciation, yen(budget.depreciation)],
            [text.subsidy, yen(budget.subsidy)],
          ]} />
          <BudgetGroup title={text.bs} fields={[
            [text.asset, yen(budget.asset)],
            [text.land, yen(budget.land)],
            [text.cash, yen(budget.cash)],
            [text.debt, yen(budget.debt)],
            [text.yearsToRenewal, `${budget.yearsToRenewal}年`],
            [text.renewalCost, yen(budget.renewalCost)],
          ]} />
          <BudgetGroup title={text.cf} fields={[[text.loanRepayment, yen(budget.loanRepayment)]]} />
        </div>
      </section>

      <section className="management-section advice-section">
        <h2>{text.adviceTitle}</h2>
        {advice.length > 0 ? (
          <ul className="advice-list">
            {advice.map((item) => (
              <li key={item.id}>
                <span className={`priority priority-${item.priority}`}>{item.priority}</span>
                <div><h3>{item.title}</h3><p>{item.reason}</p><strong>{item.action}</strong></div>
              </li>
            ))}
          </ul>
        ) : <p className="empty-advice">{text.noAdvice}</p>}
      </section>
    </section>
  );
}

export function App() {
  const snapshot = useStoreSnapshot();
  const [tab, setTab] = useState<Tab>("counter");
  const bathhouse = snapshot.bathhouses.find((item) => item.id === COUNTER_BATHHOUSE_ID) ?? snapshot.bathhouses[0];
  const budget = bathhouse ? snapshot.budgets[bathhouse.id] : undefined;
  const counts = bathhouse ? snapshot.dailyCounts[bathhouse.id] ?? [] : [];
  const count = latestCount(counts);

  useEffect(() => {
    document.body.classList.toggle("counter-locked", tab === "counter");
    return () => document.body.classList.remove("counter-locked");
  }, [tab]);

  if (!bathhouse || !budget) {
    return <main className="counter-app"><p>{text.noAdvice}</p></main>;
  }

  return (
    <main className="counter-app">
      <header className="counter-header">
        <h1>{bathhouse.name}</h1>
        <nav className="tabs" aria-label="画面">
          <button type="button" className={tab === "counter" ? "active" : ""} onClick={() => setTab("counter")}>{text.counterTab}</button>
          <button type="button" className={tab === "management" ? "active" : ""} onClick={() => setTab("management")}>{text.managementTab}</button>
        </nav>
      </header>
      {tab === "counter" ? <CounterView budget={budget} count={count} /> : <ManagementView budget={budget} counts={counts} />}
      <p className="sample-notice">{text.sampleNotice}</p>
    </main>
  );
}
