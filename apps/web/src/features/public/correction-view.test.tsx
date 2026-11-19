import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { PublicCorrection } from "./correction";
import { CorrectionView } from "./correction-view";

const correction: PublicCorrection = {
  message_id: "00000000-0000-0000-0000-0000000000a1",
  claim_text: "INEC has released a new campaign timetable",
  verdict: "contradicted",
  summary: "INEC did not issue this timetable.",
  source: {
    id: "00000000-0000-0000-0000-0000000000c1",
    document_title: "INEC dismisses viral timetable",
    publisher: "INEC",
    url: "https://example.org/statement",
    text: "The graphic circulating online is fake.",
  },
  translations: [{ language: "yo", text: "yo text" }],
  approved_by: "Ada Reviewer",
  approved_at: "2026-11-19T10:30:00Z",
  sealed_at: "2026-11-19T10:31:00Z",
  integrity_hash: "sha256:abc123",
  previous_hash: null,
  hash_algorithm: "sha256",
  canonical_json: '{"claim_id":"x"}',
  integrity_verified: true,
};

afterEach(cleanup);

describe("CorrectionView", () => {
  it("shows claim, verdict, official source, approver, time and hash", () => {
    render(<CorrectionView correction={correction} />);
    expect(screen.getByText("INEC has released a new campaign timetable")).toBeTruthy();
    expect(screen.getByText("Contradicted by an official source")).toBeTruthy();
    expect(screen.getByText("The graphic circulating online is fake.")).toBeTruthy();
    const link = screen.getByRole("link", { name: "INEC dismisses viral timetable" });
    expect(link.getAttribute("href")).toBe("https://example.org/statement");
    expect(screen.getByText(/Approved by Ada Reviewer on/)).toBeTruthy();
    expect(screen.getByText(/19 November 2026/)).toBeTruthy();
    expect(screen.getByText("sha256:abc123")).toBeTruthy();
  });

  it("shows approved translations by language name", () => {
    render(<CorrectionView correction={correction} />);
    expect(screen.getByText("Yoruba:")).toBeTruthy();
    expect(screen.getByText("yo text")).toBeTruthy();
  });

  it("explains how to verify and publishes the exact record text", () => {
    render(<CorrectionView correction={correction} />);
    expect(screen.getByText("How to check it yourself")).toBeTruthy();
    expect(screen.getByLabelText("Record text").textContent).toBe('{"claim_id":"x"}');
    expect(screen.getByText(/it matches/)).toBeTruthy();
    expect(screen.getByText("none (this was the first)")).toBeTruthy();
  });

  it("says plainly when the server check fails", () => {
    render(<CorrectionView correction={{ ...correction, integrity_verified: false }} />);
    expect(screen.getByText(/it does not match/)).toBeTruthy();
  });

  it("handles a message with no official source", () => {
    render(
      <CorrectionView
        correction={{ ...correction, source: null, verdict: "no_official_statement" }}
      />,
    );
    expect(screen.getByText("No official statement found yet")).toBeTruthy();
    expect(screen.getByText("We found no official statement on this yet.")).toBeTruthy();
  });
});
