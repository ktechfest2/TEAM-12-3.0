import type { ReactNode } from "react";
import { Icon } from "../icons";

export function Notice({
  tone,
  children,
}: {
  tone: "error" | "info" | "empty";
  children: ReactNode;
}) {
  if (tone === "empty") {
    return (
      <div
        role="status"
        className="flex flex-col items-center gap-2 rounded-card border border-dashed border-border-strong px-6 py-12 text-center text-secondary"
      >
        <Icon name="inbox" size={28} className="text-muted" />
        <p>{children}</p>
      </div>
    );
  }
  const error = tone === "error";
  return (
    <p
      role={error ? "alert" : "status"}
      className={`flex items-start gap-2 rounded-control border px-3 py-3 text-sm ${
        error
          ? "border-contradicted/30 bg-contradicted-soft text-contradicted"
          : "border-brand-line bg-brand-tint text-brand"
      }`}
    >
      <Icon name={error ? "alert" : "clock"} size={18} className="mt-0.5 shrink-0" />
      <span>{children}</span>
    </p>
  );
}

export function Loading({ children = "Loading..." }: { children?: ReactNode }) {
  return (
    <p role="status" className="flex items-center gap-2 text-secondary">
      <span className="size-4 animate-spin rounded-full border-2 border-border-strong border-t-brand" />
      {children}
    </p>
  );
}
