import type { ReactNode } from "react";
import { NavLink } from "react-router";
import { Icon, type IconName } from "../icons";

type CommonProps = {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "quiet" | "destructive";
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

export function Button(props: ButtonProps | LinkProps) {
  const variant = props.variant ?? "primary";
  const size = props.size ?? "md";
  const styles = {
    primary: "border-brand bg-brand text-white hover:bg-brand-hover",
    secondary: "border-brand-soft bg-brand-soft text-brand hover:bg-[#cbeecf]",
    outline: "border-border-strong bg-white text-foreground hover:bg-surface",
    ghost: "border-transparent bg-transparent text-secondary hover:bg-surface",
    destructive: "border-[#dc2626] bg-[#dc2626] text-white hover:bg-[#b91c1c]",
    quiet: "border-transparent bg-transparent text-brand hover:bg-brand-soft",
  }[variant === "quiet" ? "quiet" : variant];
  const sizes = {
    sm: "min-h-11 px-3 text-sm",
    md: "min-h-11 px-4 text-sm",
  }[size];
  const className = `inline-flex items-center justify-center gap-2 rounded-[10px] border font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${sizes} ${styles} ${props.className ?? ""}`;

  if ("as" in props && props.as === "link") {
    const icon = props.icon;
    return (
      <NavLink to={props.to} className={className}>
        {icon ? <Icon name={icon} size={size === "sm" ? 16 : 18} /> : null}
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
      {icon ? <Icon name={icon} size={size === "sm" ? 16 : 18} /> : null}
      {children}
    </button>
  );
}
