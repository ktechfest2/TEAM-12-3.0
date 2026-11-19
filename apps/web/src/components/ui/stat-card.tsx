import type { LucideIcon } from "lucide-react";

type Props = {
  label: string;
  value: string | number;
  detail?: string;
  icon: LucideIcon;
};

export function StatCard({ label, value, detail, icon: Icon }: Props) {
  return (
    <article className="rounded-[14px] border border-border bg-white p-5 shadow-[var(--shadow-card)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-muted">{label}</p>
          <p className="mt-2 text-3xl font-bold tabular-nums text-foreground">{value}</p>
        </div>
        <span className="grid size-10 place-items-center rounded-[10px] bg-brand-soft text-brand">
          <Icon size={19} aria-hidden="true" />
        </span>
      </div>
      {detail ? <p className="mt-3 text-xs leading-5 text-muted">{detail}</p> : null}
    </article>
  );
}
