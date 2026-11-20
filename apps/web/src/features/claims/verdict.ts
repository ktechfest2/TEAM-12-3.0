import type { components } from "../../lib/api/schema.gen";

export type ClaimResult = components["schemas"]["ClaimOut"];
export type Verdict = ClaimResult["verdict"];

/** Plain words for each of the three verdicts. Never add opinion labels. */
export const verdictLabel: Record<Verdict, string> = {
  confirmed: "Confirmed by an official source",
  contradicted: "Contradicted by an official source",
  no_official_statement: "No official statement found yet",
};

/** Colour pairs for each verdict. The badge also adds an icon so colour is never the only signal. */
export const verdictTone: Record<Verdict, string> = {
  confirmed: "border-confirmed/30 bg-confirmed-soft text-confirmed",
  contradicted: "border-contradicted/30 bg-contradicted-soft text-contradicted",
  no_official_statement:
    "border-no-official-statement/30 bg-no-official-statement-soft text-no-official-statement",
};

/** Accent used for the stripe on a verdict card. */
export const verdictAccent: Record<Verdict, string> = {
  confirmed: "bg-confirmed",
  contradicted: "bg-contradicted",
  no_official_statement: "bg-no-official-statement",
};
