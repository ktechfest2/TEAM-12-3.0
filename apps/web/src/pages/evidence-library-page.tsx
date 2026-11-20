import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Loading, Notice } from "../components/ui/notice";
import { PageTitle } from "../components/ui/page-header";
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
  if (query.isPending) return <Loading>Loading evidence...</Loading>;
  if (query.error) return <Notice tone="error">{query.error.message}</Notice>;

  return (
    <section className="space-y-4">
      <PageTitle title="Evidence library" />
      <div className="relative block">
        <label htmlFor="search-evidence" className="sr-only">
          Search evidence
        </label>
        <Icon name="search" size={18} className="absolute left-3 top-3 text-muted" />
        <Input
          id="search-evidence"
          type="search"
          value={queryText}
          onChange={(event) => setQueryText(event.target.value)}
          placeholder="Search title, publisher or passage"
          className="pl-10"
        />
      </div>

      <p className="text-sm text-muted" role="status">
        {sources.length} {sources.length === 1 ? "source" : "sources"}
      </p>
      {sources.length === 0 ? (
        <Notice tone="empty">
          No evidence found. Sources appear here after a claim has a matching official passage.
        </Notice>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {sources.map((source) => (
            <Card key={source.url} className="flex flex-col">
              <p className="text-xs font-semibold uppercase tracking-wider text-brand">
                {source.publisher}
              </p>
              <h2 className="mt-2 font-bold">{source.document_title}</h2>
              <blockquote className="mt-3 line-clamp-5 border-l-2 border-brand-line pl-3 text-sm text-secondary">
                {source.text}
              </blockquote>
              <a
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="mt-auto flex min-h-10 items-center gap-2 pt-3 text-sm font-semibold text-brand"
              >
                Open official source <Icon name="external" size={16} />
              </a>
            </Card>
          ))}
        </div>
      )}
    </section>
  );
}
