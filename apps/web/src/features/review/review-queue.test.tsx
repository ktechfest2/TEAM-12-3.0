import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ReviewQueue } from "./review-queue";
import { makeMessage } from "./test-fixtures";

vi.mock("./review-api", () => ({ listMessages: vi.fn() }));

import { listMessages } from "./review-api";

function renderQueue(onSelect = vi.fn()) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <ReviewQueue selectedId={null} onSelect={onSelect} />
    </QueryClientProvider>,
  );
  return onSelect;
}

afterEach(cleanup);

describe("ReviewQueue", () => {
  it("lists each claim with its verdict and stage, and selects on click", async () => {
    vi.mocked(listMessages).mockResolvedValue([makeMessage()]);
    const onSelect = renderQueue();
    const item = await screen.findByRole("button", {
      name: /INEC has released a new campaign timetable/,
    });
    expect(item.textContent).toContain("Contradicted by an official source");
    expect(item.textContent).toContain("Needs review");
    fireEvent.click(item);
    expect(onSelect).toHaveBeenCalledWith("00000000-0000-0000-0000-0000000000a1");
  });

  it("says so when nothing is waiting", async () => {
    vi.mocked(listMessages).mockResolvedValue([]);
    renderQueue();
    expect(await screen.findByText(/No claims are waiting/)).toBeTruthy();
  });

  it("shows the error when the list cannot load", async () => {
    vi.mocked(listMessages).mockRejectedValue(new Error("Your session ended. Sign in again."));
    renderQueue();
    expect((await screen.findByRole("alert")).textContent).toContain("Sign in again");
  });
});
