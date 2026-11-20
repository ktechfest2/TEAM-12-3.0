import type { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
  /** Use "lift" for the one card on a page that matters most (a verdict). Never stack shadows. */
  elevation?: "rest" | "lift";
};

/** The one card. White surface, hairline border, one shadow. Padding is 16 px, 24 px from `sm`. */
export function Card({ children, className = "", elevation = "rest" }: CardProps) {
  const shadow = elevation === "lift" ? "shadow-lift" : "shadow-card";
  return (
    <div
      className={`rounded-card border border-border bg-surface p-4 sm:p-6 ${shadow} ${className}`}
    >
      {children}
    </div>
  );
}
