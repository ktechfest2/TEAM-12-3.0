import { describe, expect, it } from "vitest";
import {
  allSent,
  applyDelivery,
  channelsIn,
  type Delivery,
  deliveryFor,
  elapsedSinceApproval,
  formatElapsed,
  languagesIn,
  tileState,
} from "./board-model";

function delivery(overrides: Partial<Delivery>): Delivery {
  return {
    id: "d1",
    message_id: "m1",
    channel: "telegram",
    language: "en",
    status: "queued",
    external_id: null,
    error: null,
    sent_at: null,
    created_at: "2026-11-19T10:00:00Z",
    ...overrides,
  };
}

const APPROVED = "2026-11-19T10:00:00Z";

describe("board model", () => {
  it("builds rows and columns only from real deliveries", () => {
    const list = [
      delivery({ id: "1", channel: "telegram", language: "en" }),
      delivery({ id: "2", channel: "telegram", language: "yo" }),
      delivery({ id: "3", channel: "sms", language: "en" }),
    ];
    expect(channelsIn(list)).toEqual(["telegram", "sms"]);
    expect(languagesIn(list)).toEqual(["en", "yo"]);
    expect(deliveryFor(list, "sms", "yo")).toBeUndefined();
    expect(deliveryFor(list, "sms", "en")?.id).toBe("3");
    expect(channelsIn([])).toEqual([]);
  });

  it("maps a delivery status to a tile state", () => {
    expect(tileState(delivery({ status: "queued" }))).toBe("waiting");
    expect(tileState(delivery({ status: "sent" }))).toBe("sent");
    expect(tileState(delivery({ status: "failed" }))).toBe("failed");
    expect(tileState(delivery({ status: "retracted" }))).toBe("retracted");
  });

  it("applies a live update by id and adds new deliveries", () => {
    const start = [delivery({ id: "1" })];
    const sent = applyDelivery(start, delivery({ id: "1", status: "sent" }));
    expect(sent).toHaveLength(1);
    expect(sent[0]?.status).toBe("sent");
    expect(applyDelivery(sent, delivery({ id: "2" }))).toHaveLength(2);
  });

  it("counts elapsed time up to the last receipt once everything is sent", () => {
    const list = [
      delivery({ id: "1", status: "sent", sent_at: "2026-11-19T10:00:20Z" }),
      delivery({ id: "2", status: "sent", sent_at: "2026-11-19T10:01:12Z" }),
    ];
    const later = Date.parse("2026-11-19T10:30:00Z");
    expect(allSent(list)).toBe(true);
    expect(elapsedSinceApproval(APPROVED, list, later)).toEqual({ ms: 72000, final: true });
  });

  it("keeps counting from approval while any delivery is still waiting", () => {
    const list = [
      delivery({ id: "1", status: "sent", sent_at: "2026-11-19T10:00:05Z" }),
      delivery({ id: "2", status: "queued" }),
    ];
    const now = Date.parse("2026-11-19T10:00:30Z");
    expect(elapsedSinceApproval(APPROVED, list, now)).toEqual({ ms: 30000, final: false });
  });

  it("does not report a finished broadcast when there are no deliveries", () => {
    expect(allSent([])).toBe(false);
    expect(elapsedSinceApproval(APPROVED, [], Date.parse(APPROVED)).final).toBe(false);
  });

  it("formats elapsed time for a projector", () => {
    expect(formatElapsed(0)).toBe("0 s");
    expect(formatElapsed(59_900)).toBe("59 s");
    expect(formatElapsed(72_000)).toBe("1 min 12 s");
  });
});
