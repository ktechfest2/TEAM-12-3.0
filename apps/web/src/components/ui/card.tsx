import type { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
};

export function Card({ children, className = "" }: CardProps) {
  return (
    <section
      className={`rounded-[14px] border border-border bg-white p-5 shadow-card ${className}`}
    >
      {children}
    </section>
  );
}
