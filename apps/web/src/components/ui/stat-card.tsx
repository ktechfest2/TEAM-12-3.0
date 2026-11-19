import { Icon, type IconName } from "../icons";

type Props = {
  label: string;
  value: string | number;
  detail?: string;
  icon: IconName;
};

export function StatCard({ label, value, detail, icon }: Props) {
  return (
    <article className="rounded-card border border-border bg-white p-4 shadow-card sm:p-5">
      <p className="flex items-center gap-2 text-sm font-medium text-secondary">
        <Icon name={icon} size={16} className="shrink-0 text-brand" />
        <span className="truncate">{label}</span>
      </p>
      <p className="mt-2 text-2xl font-bold tabular-nums text-foreground sm:text-3xl">{value}</p>
      {detail ? <p className="mt-1 text-xs leading-5 text-muted">{detail}</p> : null}
    </article>
  );
}
