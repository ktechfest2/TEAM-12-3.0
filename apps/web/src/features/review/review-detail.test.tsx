import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ReviewDetail } from "./review-detail";
import { approvedTranslation, makeMessage } from "./test-fixtures";

vi.mock("./review-api", () => ({
  getMessage: vi.fn(),
  addReview: vi.fn(),
  draftTranslation: vi.fn(),
  approveTranslation: vi.fn(),
  sealMessage: vi.fn(),
  broadcastMessage: vi.fn(),
}));

import {
  addReview,
  approveTranslation,
  draftTranslation,
  getMessage,
  sealMessage,
} from "./review-api";

function renderDetail() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <ReviewDetail messageId="00000000-0000-0000-0000-0000000000a1" />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

const approveButton = () => screen.getByRole("button", { name: "Approve" }) as HTMLButtonElement;

afterEach(cleanup);

describe("ReviewDetail", () => {
  it("shows the official passage beside the draft answer", async () => {
    vi.mocked(getMessage).mockResolvedValue(makeMessage());
    renderDetail();
    const draft = await screen.findByRole("region", { name: "Draft answer" });
    const source = screen.getByRole("region", { name: "Official source" });
    expect(draft.textContent).toContain("Contradicted by an official source");
    expect(source.textContent).toContain("The graphic circulating online is fake.");
    const link = screen.getByRole("link", { name: "INEC dismisses viral timetable" });
    expect(link.getAttribute("href")).toBe("https://example.org/statement");
  });

  it("keeps Approve disabled and names the missing languages until all are approved", async () => {
    vi.mocked(getMessage).mockResolvedValue(
      makeMessage({ localisations: [approvedTranslation("yo"), approvedTranslation("ha")] }),
    );
    renderDetail();
    await screen.findByRole("region", { name: "Draft answer" });
    expect(approveButton().disabled).toBe(true);
    expect(screen.getByText(/Igbo, Pidgin/)).toBeTruthy();
  });

  it("enables Approve once every target language is approved", async () => {
    const all = (["yo", "ha", "ig", "pcm"] as const).map(approvedTranslation);
    vi.mocked(getMessage).mockResolvedValue(makeMessage({ localisations: all }));
    renderDetail();
    await screen.findByRole("region", { name: "Draft answer" });
    expect(approveButton().disabled).toBe(false);
  });

  it("drafts a translation and approves it through the API", async () => {
    const drafted = makeMessage({
      localisations: [{ language: "yo", text: "yo draft", approved_by: null, is_approved: false }],
    });
    vi.mocked(getMessage).mockResolvedValue(makeMessage());
    vi.mocked(draftTranslation).mockResolvedValue(drafted);
    vi.mocked(approveTranslation).mockResolvedValue(
      makeMessage({ localisations: [approvedTranslation("yo")] }),
    );
    renderDetail();

    fireEvent.click(await screen.findByRole("button", { name: "Draft Yoruba translation" }));
    await waitFor(() =>
      expect(draftTranslation).toHaveBeenCalledWith(
        "00000000-0000-0000-0000-0000000000a1",
        "yo",
        undefined,
      ),
    );
    fireEvent.click(await screen.findByRole("button", { name: "Approve Yoruba" }));
    await waitFor(() =>
      expect(approveTranslation).toHaveBeenCalledWith("00000000-0000-0000-0000-0000000000a1", "yo"),
    );
    expect(await screen.findByText("Approved by native")).toBeTruthy();
  });

  it("approves the review, then offers to seal it", async () => {
    const all = (["yo", "ha", "ig", "pcm"] as const).map(approvedTranslation);
    const approved = makeMessage({
      localisations: all,
      review: {
        reviewer_id: "reviewer",
        status: "approved",
        note: null,
        created_at: "2026-11-19T00:00:00Z",
      },
    });
    vi.mocked(getMessage).mockResolvedValue(makeMessage({ localisations: all }));
    vi.mocked(addReview).mockResolvedValue(approved);
    vi.mocked(sealMessage).mockResolvedValue({ ...approved, integrity_hash: "sha256:abc" });
    renderDetail();
    await screen.findByRole("region", { name: "Draft answer" });

    fireEvent.click(approveButton());
    await waitFor(() =>
      expect(addReview).toHaveBeenCalledWith("00000000-0000-0000-0000-0000000000a1", {
        status: "approved",
      }),
    );
    fireEvent.click(await screen.findByRole("button", { name: "Seal this message" }));
    expect(await screen.findByText(/sha256:abc/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Send to every channel" })).toBeTruthy();
  });

  it("can escalate without any translations", async () => {
    vi.mocked(getMessage).mockResolvedValue(makeMessage());
    vi.mocked(addReview).mockResolvedValue(
      makeMessage({
        review: {
          reviewer_id: "reviewer",
          status: "escalated",
          note: null,
          created_at: "2026-11-19T00:00:00Z",
        },
      }),
    );
    renderDetail();
    fireEvent.click(await screen.findByRole("button", { name: "Escalate" }));
    await waitFor(() =>
      expect(addReview).toHaveBeenCalledWith("00000000-0000-0000-0000-0000000000a1", {
        status: "escalated",
      }),
    );
    expect(await screen.findByText("Escalated")).toBeTruthy();
  });
});
