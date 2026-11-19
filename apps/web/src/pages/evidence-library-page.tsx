import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Icon } from "../components/icons";
import { WorkspaceHeader } from "../components/ui/surface";
import { LoginForm } from "../features/auth/login-form";
import { listMessages } from "../features/review/review-api";
import { useSession } from "../lib/auth/session";

export function EvidenceLibraryPage() {
  const session = useSession();
  const [queryText, setQueryText] = useState("");
  const query = useQuery({
    queryKey: ["messages"],
    queryFn: listMessages,
    enabled: Boolean(session),
  });

  const sources = useMemo(() => {
    if (!query.data) return [];
    const byUrl = new Map<string, NonNullable<(typeof query.data)[number]["source"]>>();
    for (const message of query.data) {
      if (message.source) byUrl.set(message.source.url, message.source);
    }
    const normalized = queryText.trim().toLowerCase();
    return Array.from(byUrl.values()).filter(
      (source) =>
        normalized.length === 0 ||
        `${source.document_title} ${source.publisher} ${source.text}`
          .toLowerCase()
          .includes(normalized),
    );
  }, [query.data, queryText]);

  if (!session) return <LoginForm />;
  if (query.isPending) return <p className="text-muted">Loading evidence...</p>;
  if (query.error) return <p role="alert">{query.error.message}</p>;

  return (
    <section className="space-y-5">
      <WorkspaceHeader
        title="Evidence library"
        lead="Official source passages cited by current claims."
      />
      <label className="relative block">
        <span className="sr-only">Search evidence</span>
        <Icon name="search" size={18} className="absolute left-3 top-3.5 text-muted" />
        <input
          type="search"
          value={queryText}
          onChange={(event) => setQueryText(event.target.value)}
          placeholder="Search title, publisher or passage"
          className="min-h-11 w-full rounded-control border border-border bg-white pl-10 pr-3 text-sm focus:border-brand"
        />
      </label>

      <p className="text-sm text-muted" role="status">
        {sources.length} {sources.length === 1 ? "source" : "sources"}
      </p>
      {sources.length === 0 ? (
        <div className="rounded-card border border-border bg-white px-6 py-10 text-center">
          <Icon name="archive" size={24} className="mx-auto text-muted" />
          <h2 className="mt-3 font-bold">No evidence found</h2>
          <p className="mt-1 text-sm text-muted">
            Sources appear here after a claim has a matching official passage.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {sources.map((source) => (
            <article
              key={source.url}
              className="flex flex-col rounded-card border border-border bg-white p-4 shadow-card sm:p-5"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-brand">
                {source.publisher}
              </p>
              <h2 className="mt-1.5 font-bold leading-6">{source.document_title}</h2>
              <blockquote className="mt-3 line-clamp-5 border-l-2 border-brand-200 pl-3 text-sm leading-6 text-secondary">
                {source.text}
              </blockquote>
              <a
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="mt-auto flex min-h-11 items-center gap-1.5 pt-3 text-sm font-semibold text-brand"
              >
                Open official source <Icon name="external" size={15} />
              </a>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
