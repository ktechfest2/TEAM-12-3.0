import type { ReactNode } from "react";
import { Icon, type IconName } from "../icons";

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-card border border-line bg-surface p-5 shadow-card sm:p-6 ${className ?? ""}`}
    >
      {children}
    </div>
  );
}

export function PageHeader({
  title,
  lead,
  aside,
}: {
  title: string;
  lead?: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-2xl space-y-2">
        <h1 className="text-3xl font-bold leading-tight text-brand sm:text-4xl">{title}</h1>
        {lead ? <p className="text-lg text-muted">{lead}</p> : null}
      </div>
      {aside}
    </header>
  );
}

/** Compact page title for the reviewer workspace: one h1, one optional line, one optional action. */
export function WorkspaceHeader({
  title,
  lead,
  aside,
}: {
  title: string;
  lead?: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">{title}</h1>
        {lead ? <p className="mt-1.5 max-w-2xl text-sm leading-6 text-secondary">{lead}</p> : null}
      </div>
      {aside ? <div className="shrink-0">{aside}</div> : null}
    </header>
  );
}

/** Small uppercase label above a block of content. */
export function SectionTitle({ icon, children }: { icon?: IconName; children: ReactNode }) {
  return (
    <h3 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted">
      {icon ? <Icon name={icon} size={16} /> : null}
      {children}
    </h3>
  );
}

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
    attention: "bg-beacon-soft text-beacon-ink",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

export function Notice({
  tone,
  children,
}: {
  tone: "error" | "info" | "empty";
  children: ReactNode;
}) {
  if (tone === "empty") {
    return (
      <div className="flex flex-col items-center gap-2 rounded-card border border-dashed border-line-strong px-6 py-10 text-center text-muted">
        <Icon name="inbox" size={28} className="text-faint" />
        <p>{children}</p>
      </div>
    );
  }
  const error = tone === "error";
  return (
    <p
      role={error ? "alert" : "status"}
      className={`flex items-start gap-2 rounded-control border px-3 py-2.5 text-sm ${
        error
          ? "border-contradicted/30 bg-contradicted-soft text-contradicted"
          : "border-brand-200 bg-brand-50 text-brand"
      }`}
    >
      <Icon name={error ? "alert" : "clock"} size={18} className="mt-0.5" />
      <span>{children}</span>
    </p>
  );
}

export function Loading({ children = "Loading..." }: { children?: ReactNode }) {
  return (
    <p role="status" className="flex items-center gap-2 text-muted">
      <span className="size-4 animate-spin rounded-full border-2 border-line-strong border-t-brand" />
      {children}
    </p>
  );
}

export const controlClass =
  "w-full rounded-control border border-line-strong bg-surface px-3.5 py-2.5 text-ink placeholder:text-faint focus:border-brand";
