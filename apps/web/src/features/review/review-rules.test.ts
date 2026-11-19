import { describe, expect, it } from "vitest";
import { canApprove, missingApprovals, stageOf } from "./review-rules";
import { approvedTranslation, makeMessage } from "./test-fixtures";

const allApproved = (["yo", "ha", "ig", "pcm"] as const).map(approvedTranslation);

describe("review rules", () => {
  it("lists every language without an approved translation", () => {
    const message = makeMessage({
      localisations: [
        approvedTranslation("yo"),
        { language: "ha", text: "draft", approved_by: null, is_approved: false },
      ],
    });
    expect(missingApprovals(message)).toEqual(["ha", "ig", "pcm"]);
  });

  it("allows approval only when all four languages are approved", () => {
    expect(canApprove(makeMessage())).toBe(false);
    expect(canApprove(makeMessage({ localisations: allApproved.slice(0, 3) }))).toBe(false);
    expect(canApprove(makeMessage({ localisations: allApproved }))).toBe(true);
  });

  it("refuses approval of a cited verdict that has no source passage", () => {
    expect(canApprove(makeMessage({ localisations: allApproved, source: null }))).toBe(false);
    expect(
      canApprove(
        makeMessage({
          localisations: allApproved,
          source: null,
          verdict: "no_official_statement",
        }),
      ),
    ).toBe(true);
  });

  it("names the stage from the review and the seal", () => {
    expect(stageOf(makeMessage())).toBe("draft");
    const review = (status: "approved" | "rejected" | "escalated") => ({
      reviewer_id: "r",
      status,
      note: null,
      created_at: "2026-11-19T00:00:00Z",
    });
    expect(stageOf(makeMessage({ review: review("approved") }))).toBe("approved");
    expect(stageOf(makeMessage({ review: review("rejected") }))).toBe("rejected");
    expect(stageOf(makeMessage({ review: review("escalated") }))).toBe("escalated");
    expect(stageOf(makeMessage({ review: review("approved"), integrity_hash: "sha256:x" }))).toBe(
      "sealed",
    );
  });
});
