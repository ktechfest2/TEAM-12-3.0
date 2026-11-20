import type { ReactNode } from "react";
import { Icon, type IconName } from "../icons";

/** Small uppercase label above a block of content. */
export function SectionTitle({ icon, children }: { icon?: IconName; children: ReactNode }) {
  return (
    <h3 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted">
      {icon ? <Icon name={icon} size={16} /> : null}
      {children}
    </h3>
  );
}
