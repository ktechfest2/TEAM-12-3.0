import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { makeMessage } from "../review/test-fixtures";
import type { Delivery } from "./board-model";
import { BroadcastBoard } from "./broadcast-board";

vi.mock("../review/review-api", () => ({ listMessages: vi.fn() }));
vi.mock("./use-delivery-stream", () => ({ useDeliveryStream: vi.fn() }));

import { listMessages } from "../review/review-api";
import { useDeliveryStream } from "./use-delivery-stream";

const sealedMessage = makeMessage({
  integrity_hash: "sha256:abc",
  review: {
    reviewer_id: "reviewer",
    status: "approved",
    note: null,
    created_at: "2026-11-19T10:00:00Z",
  },
});

function delivery(overrides: Partial<Delivery>): Delivery {
  return {
    id: "d1",
    message_id: sealedMessage.id,
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

function renderBoard() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <BroadcastBoard />
    </QueryClientProvider>,
  );
}

afterEach(cleanup);

describe("BroadcastBoard", () => {
  it("asks for a sealed correction when none exists", async () => {
    vi.mocked(listMessages).mockResolvedValue([makeMessage()]);
    vi.mocked(useDeliveryStream).mockReturnValue({ deliveries: [], status: "idle", error: null });
    renderBoard();
    expect(await screen.findByText(/No approved corrections yet/)).toBeTruthy();
  });

  it("shows no tiles before anything has been planned", async () => {
    vi.mocked(listMessages).mockResolvedValue([sealedMessage]);
    vi.mocked(useDeliveryStream).mockReturnValue({
      deliveries: [],
      status: "live",
      error: null,
    });
    renderBoard();
    expect(await screen.findByText(/Nothing has been sent yet/)).toBeTruthy();
    expect(screen.queryByRole("table")).toBeNull();
    expect(screen.getByText("0 of 0 sent")).toBeTruthy();
  });

  it("shows a tile per channel and language from real receipts only", async () => {
    vi.mocked(listMessages).mockResolvedValue([sealedMessage]);
    vi.mocked(useDeliveryStream).mockReturnValue({
      deliveries: [
        delivery({
          id: "1",
          channel: "telegram",
          language: "en",
          status: "sent",
          sent_at: "2026-11-19T10:00:20Z",
        }),
        delivery({ id: "2", channel: "telegram", language: "yo", status: "queued" }),
        delivery({ id: "3", channel: "sms", language: "en", status: "failed", error: "down" }),
      ],
      status: "live",
      error: null,
    });
    renderBoard();

    const table = await screen.findByRole("table");
    const telegramRow = within(table).getByRole("row", { name: /Telegram/ });
    const smsRow = within(table).getByRole("row", { name: /SMS/ });
    const telegramTiles = within(telegramRow).getAllByRole("cell");
    expect(telegramTiles[0]?.getAttribute("data-state")).toBe("sent");
    expect(telegramTiles[0]?.textContent).toContain("Sent");
    expect(telegramTiles[1]?.getAttribute("data-state")).toBe("waiting");
    const smsTiles = within(smsRow).getAllByRole("cell");
    expect(smsTiles[0]?.getAttribute("data-state")).toBe("failed");
    expect(smsTiles[1]?.textContent).toBe("-");
    expect(screen.getByText("1 of 3 sent")).toBeTruthy();
  });

  it("shows time from approval to the last receipt when every channel is sent", async () => {
    vi.mocked(listMessages).mockResolvedValue([sealedMessage]);
    vi.mocked(useDeliveryStream).mockReturnValue({
      deliveries: [
        delivery({ id: "1", status: "sent", sent_at: "2026-11-19T10:00:20Z" }),
        delivery({ id: "2", channel: "sms", status: "sent", sent_at: "2026-11-19T10:01:12Z" }),
      ],
      status: "done",
      error: null,
    });
    renderBoard();
    expect((await screen.findByTestId("elapsed")).textContent).toBe("1 min 12 s");
    expect(screen.getByText("from approval until every channel was sent")).toBeTruthy();
    expect(screen.getByText("2 of 2 sent")).toBeTruthy();
  });

  it("shows a stream error", async () => {
    vi.mocked(listMessages).mockResolvedValue([sealedMessage]);
    vi.mocked(useDeliveryStream).mockReturnValue({
      deliveries: [],
      status: "error",
      error: "Your session ended. Sign in again.",
    });
    renderBoard();
    expect((await screen.findByRole("alert")).textContent).toContain("Sign in again");
  });
});
