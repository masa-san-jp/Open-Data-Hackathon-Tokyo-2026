import { useMemo, useState, useSyncExternalStore } from "react";
import {
  buildRoute,
  isOpen,
  type Leg,
} from "domain/route";
import { haversineKm, type GeoPoint } from "domain/calc";
import { store } from "store";
import type { Bathhouse } from "domain/types";
import { guestText as text } from "./guest.ja";

const DEFAULT_LOCATION: GeoPoint = { lat: 35.71, lng: 139.813 };

function currentTime(): string {
  const date = new Date();
  return `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}

function hourFromTime(value: string): number {
  const [hours, minutes] = value.split(":").map(Number);
  return (hours ?? 0) + (minutes ?? 0) / 60;
}

function displayHour(hour: number): string {
  const normalized = ((hour % 24) + 24) % 24;
  const hours = Math.floor(normalized);
  const minutes = Math.round((normalized - hours) * 60);
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

function displayHours(bathhouse: Bathhouse): string {
  return `${displayHour(bathhouse.openHour)}〜${displayHour(bathhouse.closeHour)}`;
}

function mapUrl(address: string): string {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
}

function subscribe(onStoreChange: () => void): () => void {
  return store.subscribe(() => onStoreChange());
}

function useStoreSnapshot() {
  return useSyncExternalStore(subscribe, store.getSnapshot, store.getSnapshot);
}

function modeLabel(leg: Leg): string {
  return leg.travelMode === "walk" ? text.walk : text.transit;
}

function BathhouseMeta({ bathhouse, hour }: { bathhouse: Bathhouse; hour: number }) {
  const open = isOpen(bathhouse, hour);
  return (
    <div className="bathhouse-meta">
      <span className={open ? "state open" : "state closed"}>{open ? text.open : text.closed}</span>
      <span>{displayHours(bathhouse)}</span>
    </div>
  );
}

function RouteCard({ leg, index }: { leg: Leg; index: number }) {
  return (
    <li className="route-card">
      <div className="route-number">{index + 1}</div>
      <div className="route-content">
        <div className="route-title-row">
          <h3>{leg.bathhouse.name}</h3>
          <span className="arrival">
            {text.arrival} {displayHour(leg.arrivalHour)}
          </span>
        </div>
        <div className="route-travel">
          {modeLabel(leg)} {leg.travelMinutes}{text.minutes}
        </div>
        <BathhouseMeta bathhouse={leg.bathhouse} hour={leg.arrivalHour} />
        <div className="route-address">{leg.bathhouse.address}</div>
        <div className="route-footer">
          <a href={mapUrl(leg.bathhouse.address)} target="_blank" rel="noreferrer">
            {text.map}
          </a>
          <span>{text.price}</span>
        </div>
      </div>
    </li>
  );
}

export function App() {
  const snapshot = useStoreSnapshot();
  const [locationText, setLocationText] = useState("東京都墨田区");
  const [location, setLocation] = useState<GeoPoint>(DEFAULT_LOCATION);
  const [time, setTime] = useState(currentTime);
  const [count, setCount] = useState<1 | 2 | 3>(2);
  const [locationError, setLocationError] = useState("");

  const startHour = hourFromTime(time);
  const todayCounts = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(snapshot.dailyCounts).map(([id, counts]) => [id, counts.at(-1)?.total ?? 0]),
      ),
    [snapshot],
  );
  const route = useMemo(
    () =>
      buildRoute({
        from: location,
        startHour,
        count,
        bathhouses: snapshot.bathhouses,
        budgets: snapshot.budgets,
        todayCounts,
      }),
    [count, location, snapshot, startHour, todayCounts],
  );
  const list = useMemo(
    () =>
      snapshot.bathhouses
        .filter((bathhouse) => bathhouse.active)
        .map((bathhouse) => ({
          bathhouse,
          distance: haversineKm(location, { lat: bathhouse.lat, lng: bathhouse.lng }),
        }))
        .sort((a, b) => a.distance - b.distance),
    [location, snapshot.bathhouses],
  );

  const useCurrentLocation = (): void => {
    if (!navigator.geolocation) {
      setLocationError(text.currentLocationError);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({ lat: position.coords.latitude, lng: position.coords.longitude });
        setLocationText("現在地");
        setLocationError("");
      },
      () => setLocationError(text.currentLocationError),
    );
  };

  return (
    <main className="guest-app">
      <header className="topbar">
        <h1>{text.title}</h1>
      </header>

      <section className="controls" aria-label="ルート条件">
        <div className="control location-control">
          <label htmlFor="location">{text.locationLabel}</label>
          <div className="location-row">
            <input
              id="location"
              value={locationText}
              placeholder={text.locationPlaceholder}
              onChange={(event) => {
                setLocationText(event.target.value);
                setLocationError("");
              }}
            />
            <button type="button" onClick={useCurrentLocation}>
              {text.currentLocation}
            </button>
          </div>
          {locationError ? <p className="form-error" role="alert">{locationError}</p> : null}
        </div>
        <div className="control">
          <label htmlFor="time">{text.timeLabel}</label>
          <input id="time" type="time" value={time} onChange={(event) => setTime(event.target.value)} />
        </div>
        <div className="control">
          <span className="control-label">{text.countLabel}</span>
          <div className="count-buttons" role="group" aria-label={text.countLabel}>
            {[1, 2, 3].map((value) => (
              <button
                type="button"
                key={value}
                className={count === value ? "selected" : ""}
                aria-pressed={count === value}
                onClick={() => setCount(value as 1 | 2 | 3)}
              >
                {value}軒
              </button>
            ))}
          </div>
        </div>
      </section>

      <div className="content-grid">
        <section className="panel route-panel">
          <div className="panel-heading">
            <h2>{text.routeTitle}</h2>
            <span>{route.length}軒</span>
          </div>
          {route.length > 0 ? (
            <ol className="route-list">
              {route.map((leg, index) => <RouteCard key={leg.bathhouse.id} leg={leg} index={index} />)}
            </ol>
          ) : (
            <p className="empty">{text.unavailable}</p>
          )}
        </section>

        <section className="panel list-panel">
          <div className="panel-heading">
            <h2>{text.listTitle}</h2>
            <span>{list.length}軒</span>
          </div>
          <ul className="bathhouse-list">
            {list.map(({ bathhouse, distance }) => {
              const open = isOpen(bathhouse, startHour);
              return (
                <li key={bathhouse.id} className={open ? "" : "dimmed"}>
                  <div className="list-main">
                    <h3>{bathhouse.name}</h3>
                    <BathhouseMeta bathhouse={bathhouse} hour={startHour} />
                    <p>{bathhouse.address}</p>
                  </div>
                  <div className="list-side">
                    <span>{distance.toFixed(1)}km</span>
                    <a href={mapUrl(bathhouse.address)} target="_blank" rel="noreferrer">
                      {text.map}
                    </a>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      </div>

      <p className="sample-notice">{text.sampleNotice}</p>
    </main>
  );
}
