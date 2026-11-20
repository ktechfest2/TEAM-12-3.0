import type { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
  /** "lift" for the one card on a page that matters most (a verdict). "flat" for tinted panels and cards inside cards. Never stack shadows. */
  elevation?: "flat" | "rest" | "lift";
  /** "none" for cards whose rows or tables run edge to edge. */
  padding?: "md" | "none";
};

/** The one card. White surface, hairline border, one shadow. Padding is 16 px, 24 px from `sm`. */
export function Card({ children, className = "", elevation = "rest", padding = "md" }: CardProps) {
  const shadow = { flat: "", rest: "shadow-card", lift: "shadow-lift" }[elevation];
  return (
    <div
      className={`rounded-card border border-border bg-surface ${padding === "md" ? "p-4 sm:p-6" : ""} ${shadow} ${className}`}
    >
      {children}
    </div>
  );
}
