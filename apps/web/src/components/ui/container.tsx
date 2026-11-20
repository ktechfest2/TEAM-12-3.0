import type { ReactNode } from "react";

type ContainerProps = {
  children: ReactNode;
  /** page: 1200 px marketing and listings. prose: 768 px forms and reading. workspace: 1120 px reviewer pages. */
  width?: "page" | "prose" | "workspace";
  className?: string;
};

const widths = {
  page: "max-w-page",
  prose: "max-w-3xl",
  workspace: "max-w-workspace",
} as const;

/** Centres content and sets the page gutters: 16 px, 24 px from `sm`, 32 px from `lg`. */
export function Container({ children, width = "page", className = "" }: ContainerProps) {
  return (
    <div className={`mx-auto w-full min-w-0 px-4 sm:px-6 lg:px-8 ${widths[width]} ${className}`}>
      {children}
    </div>
  );
}
