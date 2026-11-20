import type { ReactNode } from "react";

/** Title block for public pages: one h1, an optional lead, an optional action on the right. */
export function PageHeader({
  title,
  lead,
  aside,
}: {
  title: string;
  lead?: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-2xl space-y-3">
        <h1 className="text-3xl font-bold text-foreground md:text-4xl">{title}</h1>
        {lead ? <p className="text-lg text-secondary">{lead}</p> : null}
      </div>
      {aside}
    </header>
  );
}

/**
 * Reviewer pages have no visible title: the active sidebar or tab item names the page.
 * Each page still has one h1 for screen readers.
 */
export function PageTitle({ title }: { title: string }) {
  return <h1 className="sr-only">{title}</h1>;
}
