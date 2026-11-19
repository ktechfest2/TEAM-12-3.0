import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Icon } from "../components/icons";
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
    <section>
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">Evidence</p>
        <h1 className="mt-2 text-3xl font-bold">Evidence library</h1>
        <p className="mt-2 text-sm text-muted">
          Official source passages associated with current claims.
        </p>
      </div>
      <label className="relative mt-6 block">
        <span className="sr-only">Search evidence</span>
        <Icon name="search" size={18} className="absolute left-3 top-3.5 text-muted" />
        <input
          type="search"
          value={queryText}
          onChange={(event) => setQueryText(event.target.value)}
          placeholder="Search source title, publisher or passage"
          className="min-h-11 w-full rounded-[10px] border border-border bg-white pl-10 pr-3"
        />
      </label>

      <p className="mt-5 text-sm text-muted" role="status">
        {sources.length} sources
      </p>
      {sources.length === 0 ? (
        <div className="mt-4 rounded-[14px] border border-border bg-white p-8 text-center">
          <Icon name="archive" size={24} className="mx-auto text-muted" />
          <h2 className="mt-3 font-bold">No evidence found</h2>
          <p className="mt-2 text-sm text-muted">
            Sources appear here after a claim has a matching official passage.
          </p>
        </div>
      ) : (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {sources.map((source) => (
            <article
              key={source.url}
              className="rounded-[14px] border border-border bg-white p-5 shadow-card"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold text-brand">{source.publisher}</p>
                  <h2 className="mt-2 font-bold leading-6">{source.document_title}</h2>
                </div>
                <span className="grid size-9 shrink-0 place-items-center rounded-[10px] bg-brand-soft text-brand">
                  <Icon name="archive" size={17} />
                </span>
              </div>
              <blockquote className="mt-4 border-l-2 border-brand pl-3 text-sm leading-6 text-secondary">
                {source.text}
              </blockquote>
              <a
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 flex min-h-11 items-center gap-2 text-sm font-semibold text-brand"
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
