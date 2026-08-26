import { describe, expect, it } from "vitest";
import { createStore } from "../src/index";

describe("store", () => {
  it("contains six sample bathhouses and thirty daily counts per bathhouse", () => {
    const snapshot = createStore().getSnapshot();

    expect(snapshot.bathhouses).toHaveLength(6);
    expect(snapshot.dailyCounts.B001).toHaveLength(30);
  });

  it("notifies subscribers when a budget is updated", () => {
    const testStore = createStore();
    const snapshots: number[] = [];
    const unsubscribe = testStore.subscribe((snapshot) => {
      snapshots.push(snapshot.budgets.B001?.yearsToRenewal ?? -1);
    });

    testStore.updateBudget("B001", { yearsToRenewal: 10 });

    expect(snapshots).toEqual([10]);
    expect(testStore.getSnapshot().budgets.B001?.status).toBe("draft");
    unsubscribe();
  });

  it("changes today's count without allowing a negative total", () => {
    const testStore = createStore();
    const before = testStore.getSnapshot().dailyCounts.B001?.at(-1)?.total ?? 0;

    testStore.incrementToday("B001");
    expect(testStore.getSnapshot().dailyCounts.B001?.at(-1)?.total).toBe(before + 1);

    testStore.decrementToday("B001");
    expect(testStore.getSnapshot().dailyCounts.B001?.at(-1)?.total).toBe(before);
  });

  it("adds and updates a bathhouse without creating a budget", () => {
    const testStore = createStore();
    const id = testStore.addBathhouse({
      name: "新町湯",
      address: "東京都新宿区新町1-2-3",
      ward: "新宿区",
      lat: 35.69,
      lng: 139.71,
      hasSauna: false,
      openHour: 15,
      closeHour: 24,
      unionMember: false,
      active: true,
    });

    expect(id).toBe("B007");
    expect(testStore.getSnapshot().bathhouses.at(-1)).toMatchObject({ id, name: "新町湯" });
    expect(testStore.getSnapshot().budgets[id]).toBeUndefined();

    testStore.updateBathhouse(id, { name: "新町温泉", closeHour: 25 });

    expect(testStore.getSnapshot().bathhouses.at(-1)).toMatchObject({
      id,
      name: "新町温泉",
      closeHour: 25,
    });
  });
});
