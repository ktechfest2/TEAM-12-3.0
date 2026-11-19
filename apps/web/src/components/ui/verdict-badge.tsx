import { BadgeCheck, CircleHelp, ShieldAlert } from "lucide-react";
import type { Verdict } from "../../features/claims/verdict";

export function VerdictBadge({ verdict }: { verdict: Verdict }) {
  if (verdict === "confirmed") {
    return (
      <span className="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-[#bbf7d0] bg-brand-soft px-3 py-1 text-xs font-semibold text-verdict-true">
        <BadgeCheck size={15} aria-hidden="true" /> Confirmed by an official source
      </span>
    );
  }
  if (verdict === "contradicted") {
    return (
      <span className="inline-flex min-h-8 items-center gap-1.5 rounded-full bg-verdict-false-bg px-3 py-1 text-xs font-semibold text-verdict-false">
        <ShieldAlert size={15} aria-hidden="true" /> Contradicted by an official source
      </span>
    );
  }
  return (
    <span className="inline-flex min-h-8 items-center gap-1.5 rounded-full bg-verdict-unverified-bg px-3 py-1 text-xs font-semibold text-verdict-unverified">
      <CircleHelp size={15} aria-hidden="true" /> No official statement found yet
    </span>
  );
}
