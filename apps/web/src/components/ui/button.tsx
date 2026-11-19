import type { ReactNode } from "react";
import { NavLink } from "react-router";

type CommonProps = {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "destructive";
  size?: "sm" | "md";
  className?: string;
  children: ReactNode;
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
  }[variant];
  const sizes = {
    sm: "min-h-11 px-3 text-sm",
    md: "min-h-11 px-4 text-sm",
  }[size];
  const className = `inline-flex items-center justify-center gap-2 rounded-[10px] border font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${sizes} ${styles} ${props.className ?? ""}`;

  if ("as" in props && props.as === "link") {
    return (
      <NavLink to={props.to} className={className}>
        {props.children}
      </NavLink>
    );
  }

  const { children, variant: _variant, size: _size, className: _className, ...buttonProps } = props;
  return (
    <button type="button" {...buttonProps} className={className}>
      {children}
    </button>
  );
}
