import type { ReactNode } from "react";
import { NavLink } from "react-router";
import { Icon, type IconName } from "../icons";

type CommonProps = {
  /** primary: the one main action. secondary: soft green. outline: neutral. quiet: text only. */
  variant?: "primary" | "secondary" | "outline" | "quiet";
  size?: "sm" | "md";
  className?: string;
  children: ReactNode;
  icon?: IconName;
};

type ButtonProps = CommonProps &
  Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "children" | "className">;

type LinkProps = CommonProps & {
  as: "link";
  to: string;
};

const variants = {
  primary: "border-brand bg-brand text-on-brand hover:bg-brand-hover",
  secondary:
    "border-brand-soft bg-brand-soft text-brand hover:border-brand-line hover:bg-brand-line",
  outline: "border-border-strong bg-surface text-foreground hover:bg-canvas",
  quiet: "border-transparent bg-transparent text-brand hover:bg-brand-soft",
} as const;

const sizes = {
  sm: "min-h-10 px-3 text-sm",
  md: "min-h-11 px-4 text-sm",
} as const;

const disabled =
  "disabled:cursor-not-allowed disabled:border-border disabled:bg-sunken disabled:text-muted";

export function Button(props: ButtonProps | LinkProps) {
  const variant = props.variant ?? "primary";
  const size = props.size ?? "md";
  const className = `inline-flex items-center justify-center gap-2 rounded-control border font-semibold transition-colors ${disabled} ${sizes[size]} ${variants[variant]} ${props.className ?? ""}`;
  const iconSize = size === "sm" ? 16 : 18;

  if ("as" in props && props.as === "link") {
    return (
      <NavLink to={props.to} className={className}>
        {props.icon ? <Icon name={props.icon} size={iconSize} /> : null}
        {props.children}
      </NavLink>
    );
  }

  const {
    children,
    variant: _variant,
    size: _size,
    className: _className,
    icon,
    ...buttonProps
  } = props;
  return (
    <button type="button" {...buttonProps} className={className}>
      {icon ? <Icon name={icon} size={iconSize} /> : null}
      {children}
    </button>
  );
}
