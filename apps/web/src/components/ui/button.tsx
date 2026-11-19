import type { ButtonHTMLAttributes } from "react";
import { Icon, type IconName } from "../icons";

type Variant = "primary" | "secondary" | "quiet";

const variants: Record<Variant, string> = {
  primary: "bg-brand text-paper shadow-card enabled:hover:bg-brand-600 enabled:active:bg-brand-800",
  secondary:
    "border border-line-strong bg-surface text-brand enabled:hover:border-brand enabled:hover:bg-brand-50",
  quiet: "text-brand enabled:hover:bg-brand-50",
};

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: "md" | "sm";
  icon?: IconName;
};

export function Button({
  variant = "primary",
  size = "md",
  icon,
  className,
  children,
  type = "button",
  ...rest
}: Props) {
  const pad = size === "sm" ? "min-h-9 px-3 text-sm" : "min-h-11 px-5";
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 rounded-control font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${pad} ${variants[variant]} ${className ?? ""}`}
      {...rest}
    >
      {icon ? <Icon name={icon} size={size === "sm" ? 16 : 18} /> : null}
      {children}
    </button>
  );
}
