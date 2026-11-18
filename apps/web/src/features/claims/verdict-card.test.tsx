import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { ClaimResult } from "./verdict";
import { VerdictCard } from "./verdict-card";

const base: ClaimResult = {
  id: "00000000-0000-0000-0000-000000000001",
  text: "INEC released a new campaign timetable",
  language: "en",
  created_at: "2026-11-19T00:00:00Z",
  verdict: "contradicted",
  rationale: "matched",
  confidence: 0.9,
  source: {
    id: "00000000-0000-0000-0000-000000000002",
    document_title: "INEC dismisses viral timetable",
    publisher: "INEC",
    url: "https://example.org/statement",
    text: "The graphic is fake.",
  },
};

describe("VerdictCard", () => {
  it("shows the verdict in plain words and links the official source", () => {
    render(<VerdictCard result={base} />);
    expect(screen.getByText("Contradicted by an official source")).toBeTruthy();
    const link = screen.getByRole("link", { name: "INEC dismisses viral timetable" });
    expect(link.getAttribute("href")).toBe("https://example.org/statement");
  });

  it("says the claim goes to review when no official statement exists", () => {
    render(<VerdictCard result={{ ...base, verdict: "no_official_statement", source: null }} />);
    expect(screen.getByText("No official statement found yet")).toBeTruthy();
    expect(screen.getByText(/reviewer/)).toBeTruthy();
  });
});
