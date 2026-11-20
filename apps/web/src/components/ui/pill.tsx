import type { ReactNode } from "react";

/** Pill for stages and statuses. Always carries words, never colour alone. */
export function Pill({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "good" | "bad" | "attention";
}) {
  const tones = {
    neutral: "bg-sunken text-muted",
    good: "bg-confirmed-soft text-confirmed",
    bad: "bg-contradicted-soft text-contradicted",
    attention: "bg-brand-soft text-brand",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-0.5 text-xs font-semibold ${tones[tone]}`}
    >
      {children}
    </span>
  );
}
