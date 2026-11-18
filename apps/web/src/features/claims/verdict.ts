import type { components } from "../../lib/api/schema.gen";

export type ClaimResult = components["schemas"]["ClaimOut"];
export type Verdict = ClaimResult["verdict"];

/** Plain words for each of the three verdicts. Never add opinion labels. */
export const verdictLabel: Record<Verdict, string> = {
  confirmed: "Confirmed by an official source",
  contradicted: "Contradicted by an official source",
  no_official_statement: "No official statement found yet",
};

export const verdictTone: Record<Verdict, string> = {
  confirmed: "border-brand text-brand",
  contradicted: "border-contradicted text-contradicted",
  no_official_statement: "border-slate-300 text-muted",
};
