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

type View = "dashboard" | "bathhouse" | "master";

type BathhouseForm = {
  name: string;
  address: string;
  ward: string;
  latitude: string;
  longitude: string;
  hasSauna: boolean;
  openHour: string;
  closeHour: string;
  unionMember: boolean;
  active: boolean;
};

type BathhouseFormErrors = Partial<Record<keyof BathhouseForm, string>>;

function formFromBathhouse(bathhouse: Bathhouse): BathhouseForm {
  return {
    name: bathhouse.name,
    address: bathhouse.address,
    ward: bathhouse.ward,
    latitude: String(bathhouse.lat),
    longitude: String(bathhouse.lng),
    hasSauna: bathhouse.hasSauna,
    openHour: String(bathhouse.openHour),
    closeHour: String(bathhouse.closeHour),
    unionMember: bathhouse.unionMember,
    active: bathhouse.active,
  };
}

function emptyBathhouseForm(): BathhouseForm {
  return {
    name: "",
    address: "",
    ward: "",
    latitude: "",
    longitude: "",
    hasSauna: false,
    openHour: "15",
    closeHour: "24",
    unionMember: false,
    active: true,
  };
}

function validateBathhouseForm(form: BathhouseForm): BathhouseFormErrors {
  const errors: BathhouseFormErrors = {};
  if (!form.name.trim()) errors.name = text.invalidName;
  if (!form.address.trim()) errors.address = text.invalidAddress;
  if (!form.ward.trim()) errors.ward = text.invalidWard;

  const latitude = Number(form.latitude);
  if (!form.latitude.trim() || !Number.isFinite(latitude) || latitude < -90 || latitude > 90) {
    errors.latitude = text.invalidLatitude;
  }

  const longitude = Number(form.longitude);
  if (!form.longitude.trim() || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
    errors.longitude = text.invalidLongitude;
  }

  const openHour = Number(form.openHour);
  if (!form.openHour.trim() || !Number.isFinite(openHour) || openHour < 0 || openHour > 24) {
    errors.openHour = text.invalidOpenHour;
  }

  const closeHour = Number(form.closeHour);
  if (!form.closeHour.trim() || !Number.isFinite(closeHour) || closeHour < 0 || closeHour > 48) {
    errors.closeHour = text.invalidCloseHour;
  }
  if (!errors.openHour && !errors.closeHour && closeHour <= openHour) {
    errors.closeHour = text.invalidHours;
  }

  return errors;
}
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
  return `${Math.round(value).toLocaleString("ja-JP")}${text.yen}`;
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

function MasterView({
  bathhouses,
  budgets,
}: {
  bathhouses: readonly Bathhouse[];
  budgets: Readonly<Record<string, Budget>>;
}) {
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<string | null>(() => bathhouses[0]?.id ?? null);
  const [isCreating, setIsCreating] = useState(false);
  const [draft, setDraft] = useState<BathhouseForm | null>(() => {
    const first = bathhouses[0];
    return first ? formFromBathhouse(first) : null;
  });
  const [errors, setErrors] = useState<BathhouseFormErrors>({});
  const [notice, setNotice] = useState("");

  const normalizedSearch = search.trim().toLocaleLowerCase("ja-JP");
  const filteredBathhouses = bathhouses.filter((bathhouse) => {
    if (!normalizedSearch) return true;
    return [bathhouse.name, bathhouse.address, bathhouse.ward]
      .join(" ")
      .toLocaleLowerCase("ja-JP")
      .includes(normalizedSearch);
  });

  const updateField = <K extends keyof BathhouseForm>(field: K, value: BathhouseForm[K]): void => {
    setDraft((current) => (current ? { ...current, [field]: value } : current));
    setErrors({});
    setNotice("");
  };

  const selectBathhouse = (bathhouse: Bathhouse): void => {
    setEditingId(bathhouse.id);
    setIsCreating(false);
    setDraft(formFromBathhouse(bathhouse));
    setErrors({});
    setNotice("");
  };

  const startNew = (): void => {
    setEditingId(null);
    setIsCreating(true);
    setDraft(emptyBathhouseForm());
    setErrors({});
    setNotice("");
  };

  const cancel = (): void => {
    const first = bathhouses[0];
    if (first) {
      selectBathhouse(first);
    } else {
      setDraft(null);
      setIsCreating(false);
    }
  };

  const save = (): void => {
    if (!draft) return;
    const nextErrors = validateBathhouseForm(draft);
    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      setNotice("");
      return;
    }

    const bathhouseInput: Omit<Bathhouse, "id"> = {
      name: draft.name.trim(),
      address: draft.address.trim(),
      ward: draft.ward.trim(),
      lat: Number(draft.latitude),
      lng: Number(draft.longitude),
      hasSauna: draft.hasSauna,
      openHour: Number(draft.openHour),
      closeHour: Number(draft.closeHour),
      unionMember: draft.unionMember,
      active: draft.active,
    };

    if (isCreating) {
      const id = store.addBathhouse(bathhouseInput);
      setEditingId(id);
      setIsCreating(false);
      setDraft(formFromBathhouse({ id, ...bathhouseInput }));
    } else if (editingId) {
      store.updateBathhouse(editingId, bathhouseInput);
    }
    setErrors({});
    setNotice(text.saved);
  };

  return (
    <section className="master-view">
      <div className="master-heading">
        <div>
          <h2>{text.masterTitle}</h2>
          <p>{text.masterDescription}</p>
        </div>
        <button type="button" className="primary-button" onClick={startNew}>{text.newBathhouse}</button>
      </div>
      <div className="master-layout">
        <section className="master-list-panel">
          <div className="master-list-toolbar">
            <label className="search-field">
              <span className="visually-hidden">{text.searchBathhouses}</span>
              <input
                type="search"
                value={search}
                placeholder={text.searchBathhouses}
                aria-label={text.searchBathhouses}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
            <span className="master-count">{text.masterCount} {filteredBathhouses.length}/{bathhouses.length}</span>
          </div>
          <div className="master-list">
            <div className="master-list-head" aria-hidden="true">
              <span>{text.masterName}</span><span>{text.masterStatus}</span><span>{text.masterBudget}</span>
            </div>
            {filteredBathhouses.length > 0 ? filteredBathhouses.map((bathhouse) => (
              <button
                type="button"
                className={`master-row ${bathhouse.id === editingId && !isCreating ? "selected" : ""}`}
                key={bathhouse.id}
                aria-pressed={bathhouse.id === editingId && !isCreating}
                onClick={() => selectBathhouse(bathhouse)}
              >
                <span className="master-row-name"><strong>{bathhouse.name}</strong><small>{bathhouse.address}</small></span>
                <span className={bathhouse.active ? "master-status active" : "master-status retired"}>{bathhouse.active ? text.activeStatus : text.retiredStatus}</span>
                <span className={budgets[bathhouse.id] ? "master-status active" : "master-status pending"}>{budgets[bathhouse.id] ? text.budgetRegistered : text.budgetNotRegistered}</span>
              </button>
            )) : <p className="master-empty">{text.noBathhouses}</p>}
          </div>
        </section>

        <section className="master-editor-panel">
          {draft ? (
            <form onSubmit={(event) => { event.preventDefault(); save(); }}>
              <div className="editor-heading">
                <div>
                  <h2>{isCreating ? text.newBathhouse : text.editBasicInfo}</h2>
                  {!isCreating && editingId ? <p>{editingId}</p> : null}
                </div>
                {notice ? <span className="save-notice" role="status">{notice}</span> : null}
              </div>
              {Object.keys(errors).length > 0 ? (
                <div className="form-errors" role="alert">
                  <ul>{Object.values(errors).map((error) => <li key={error}>{error}</li>)}</ul>
                </div>
              ) : null}
              <div className="master-form-grid">
                <label className="form-field wide">
                  <span>{text.name}<em>{text.required}</em></span>
                  <input value={draft.name} aria-invalid={Boolean(errors.name)} onChange={(event) => updateField("name", event.target.value)} />
                </label>
                <label className="form-field wide">
                  <span>{text.address}<em>{text.required}</em></span>
                  <input value={draft.address} aria-invalid={Boolean(errors.address)} onChange={(event) => updateField("address", event.target.value)} />
                </label>
                <label className="form-field">
                  <span>{text.ward}<em>{text.required}</em></span>
                  <input value={draft.ward} aria-invalid={Boolean(errors.ward)} onChange={(event) => updateField("ward", event.target.value)} />
                </label>
                <label className="form-field">
                  <span>{text.latitude}<em>{text.required}</em></span>
                  <input type="number" step="0.0001" value={draft.latitude} aria-invalid={Boolean(errors.latitude)} onChange={(event) => updateField("latitude", event.target.value)} />
                </label>
                <label className="form-field">
                  <span>{text.longitude}<em>{text.required}</em></span>
                  <input type="number" step="0.0001" value={draft.longitude} aria-invalid={Boolean(errors.longitude)} onChange={(event) => updateField("longitude", event.target.value)} />
                </label>
                <label className="form-field">
                  <span>{text.openHour}<em>{text.required}</em></span>
                  <div className="number-with-unit"><input type="number" min="0" max="24" step="0.5" value={draft.openHour} aria-invalid={Boolean(errors.openHour)} onChange={(event) => updateField("openHour", event.target.value)} /><small>{text.hour}</small></div>
                </label>
                <label className="form-field">
                  <span>{text.closeHour}<em>{text.required}</em></span>
                  <div className="number-with-unit"><input type="number" min="0" max="48" step="0.5" value={draft.closeHour} aria-invalid={Boolean(errors.closeHour)} onChange={(event) => updateField("closeHour", event.target.value)} /><small>{text.hour}</small></div>
                </label>
              </div>
              <div className="form-options">
                <label className="check-field"><input type="checkbox" checked={draft.hasSauna} onChange={(event) => updateField("hasSauna", event.target.checked)} /><span>{text.hasSauna}</span><small>{draft.hasSauna ? text.on : text.off}</small></label>
                <label className="check-field"><input type="checkbox" checked={draft.unionMember} onChange={(event) => updateField("unionMember", event.target.checked)} /><span>{text.unionMember}</span><small>{draft.unionMember ? text.on : text.off}</small></label>
                <label className="check-field"><input type="checkbox" checked={draft.active} onChange={(event) => updateField("active", event.target.checked)} /><span>{text.operating}</span><small>{draft.active ? text.activeStatus : text.retiredStatus}</small></label>
              </div>
              <div className="form-actions">
                <button type="button" className="secondary-button" onClick={cancel}>{text.cancel}</button>
                <button type="submit" className="primary-button">{text.save}</button>
              </div>
            </form>
          ) : <div className="editor-empty"><p>{text.selectBathhouse}</p></div>}
        </section>
      </div>
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
  const snapshot = store.getSnapshot();
  const update = (field: EditableBudgetField, value: number): void => {
    store.updateBudget(bathhouse.id, { [field]: value });
  };
  const confirm = (): void => {
    store.confirmBudget(bathhouse.id, new Date().toISOString(), text.sampleConfirmedBy);
  };
  return (
    <section className="detail-view">
      <div className="detail-toolbar">
        <button type="button" className="back-button" onClick={onBack}>← {text.dashboard}</button>
        <label className="bathhouse-selector">
          <span>{text.selectorLabel}</span>
          <select value={bathhouse.id} onChange={(event) => onSelect(event.target.value)}>
            {/* 選択肢の銭湯名・住所・人数・金額はすべて架空のサンプルです。 */}
            {snapshot.bathhouses.filter((item) => snapshot.budgets[item.id]).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
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
    () => snapshot.bathhouses.filter((bathhouse) => bathhouse.active).flatMap((bathhouse) => {
      const budget = snapshot.budgets[bathhouse.id];
      return budget ? [statsFor(bathhouse, budget, snapshot.dailyCounts[bathhouse.id] ?? [])] : [];
    }),
    [snapshot],
  );
  const selectedBathhouse = snapshot.bathhouses.find((bathhouse) => bathhouse.id === selectedId) ?? snapshot.bathhouses[0];
  const selectedBudget = selectedBathhouse ? snapshot.budgets[selectedBathhouse.id] : undefined;

  const openDetail = (bathhouseId: string): void => {
    setSelectedId(bathhouseId);
    setView("bathhouse");
  };

  return (
    <main className="admin-app">
      <header className="admin-header">
        <h1>{text.title}</h1>
        <nav aria-label={text.screen}>
          <button type="button" className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}>{text.dashboard}</button>
          <button type="button" className={view === "bathhouse" ? "active" : ""} onClick={() => setView("bathhouse")} disabled={!selectedBathhouse || !selectedBudget}>{text.bathhouse}</button>
          <button type="button" className={view === "master" ? "active" : ""} onClick={() => setView("master")}>{text.master}</button>
        </nav>
      </header>
      {view === "dashboard" ? <Dashboard stats={stats} onSelect={openDetail} /> : view === "master" ? <MasterView bathhouses={snapshot.bathhouses} budgets={snapshot.budgets} /> : selectedBathhouse && selectedBudget ? <Detail bathhouse={selectedBathhouse} budget={selectedBudget} counts={snapshot.dailyCounts[selectedBathhouse.id] ?? []} onBack={() => setView("dashboard")} onSelect={openDetail} /> : null}
      <p className="sample-notice">{text.sampleNotice}</p>
    </main>
  );
}
