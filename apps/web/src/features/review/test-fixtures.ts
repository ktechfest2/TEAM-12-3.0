import type { Message } from "./review-rules";

/** A drafted, unreviewed message. Override fields per test. */
export function makeMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: "00000000-0000-0000-0000-0000000000a1",
    claim_id: "00000000-0000-0000-0000-0000000000b1",
    claim_text: "INEC has released a new campaign timetable",
    claim_language: "en",
    verdict: "contradicted",
    summary: "INEC did not issue this timetable.",
    confidence: 0.9,
    source: {
      id: "00000000-0000-0000-0000-0000000000c1",
      document_title: "INEC dismisses viral timetable",
      publisher: "INEC",
      url: "https://example.org/statement",
      text: "The graphic circulating online is fake.",
    },
    review: null,
    localisations: [],
    integrity_hash: null,
    created_at: "2026-11-19T00:00:00Z",
    ...overrides,
  };
}

export function approvedTranslation(language: "yo" | "ha" | "ig" | "pcm") {
  return { language, text: `${language} text`, approved_by: "native", is_approved: true };
}
