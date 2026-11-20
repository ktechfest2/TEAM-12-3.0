import type { ReactNode } from "react";
import { Icon, type IconName } from "../icons";

/** Small uppercase label above a block of content. Use `as="h2"` when it heads a page section. */
export function SectionTitle({
  icon,
  children,
  as: Tag = "h3",
  id,
}: {
  icon?: IconName;
  children: ReactNode;
  as?: "h2" | "h3";
  id?: string;
}) {
  return (
    <Tag
      id={id}
      className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted"
    >
      {icon ? <Icon name={icon} size={16} /> : null}
      {children}
    </Tag>
  );
}
