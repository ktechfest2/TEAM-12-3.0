import { Icon, type IconName } from "../icons";
import { Card } from "./card";

type Props = {
  label: string;
  value: string | number;
  detail?: string;
  icon: IconName;
};

export function StatCard({ label, value, detail, icon }: Props) {
  return (
    <Card>
      <p className="flex items-center gap-2 text-sm font-semibold text-secondary">
        <Icon name={icon} size={16} className="shrink-0 text-brand" />
        <span className="truncate">{label}</span>
      </p>
      <p className="mt-2 text-2xl font-bold tabular-nums text-foreground">{value}</p>
      {detail ? <p className="mt-1 text-xs text-muted">{detail}</p> : null}
    </Card>
  );
}
