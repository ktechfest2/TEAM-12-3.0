import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router";
import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { Input, Select } from "../components/ui/input";
import { Loading, Notice } from "../components/ui/notice";
import { PageTitle } from "../components/ui/page-header";
import { LoginForm } from "../features/auth/login-form";
import { VerdictBadge } from "../features/claims/verdict-badge";
import { listMessages } from "../features/review/review-api";
import { stageLabel, stageOf } from "../features/review/review-rules";
import { useSession } from "../lib/auth/session";

function submittedOn(iso: string): string {
  return new Date(iso).toLocaleDateString("en-NG");
}

export function ClaimsTablePage() {
  const session = useSession();
  const [queryText, setQueryText] = useState("");
  const [stage, setStage] = useState("all");
  const query = useQuery({
    queryKey: ["messages"],
    queryFn: listMessages,
    enabled: Boolean(session),
    refetchInterval: 15000,
  });

  const results = useMemo(() => {
    if (!query.data) return [];
    const normalized = queryText.trim().toLowerCase();
    return query.data.filter((message) => {
      const matchesSearch =
        normalized.length === 0 ||
        `${message.claim_text} ${message.summary}`.toLowerCase().includes(normalized);
      const matchesStage = stage === "all" || stageOf(message) === stage;
      return matchesSearch && matchesStage;
    });
  }, [query.data, queryText, stage]);

  if (!session) return <LoginForm />;

  return (
    <section className="space-y-4">
      <PageTitle title="Claims" />

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <label htmlFor="search-claims" className="sr-only">
            Search claims
          </label>
          <Icon name="search" size={18} className="absolute left-3 top-3 text-muted" />
          <Input
            id="search-claims"
            type="search"
            value={queryText}
            onChange={(event) => setQueryText(event.target.value)}
            placeholder="Search claim text"
            className="pl-10"
          />
        </div>
        <div className="sm:w-52">
          <label htmlFor="filter-by-stage" className="sr-only">
            Filter by stage
          </label>
          <Select
            id="filter-by-stage"
            value={stage}
            onChange={(event) => setStage(event.target.value)}
          >
            <option value="all">All stages</option>
            <option value="draft">Needs review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="escalated">Escalated</option>
            <option value="sealed">Sealed</option>
          </Select>
        </div>
      </div>

      {query.isPending ? <Loading>Loading claims...</Loading> : null}
      {query.error ? <Notice tone="error">{query.error.message}</Notice> : null}

      {query.data ? (
        <>
          <p className="text-sm text-muted" role="status">
            {results.length} {results.length === 1 ? "claim" : "claims"}
          </p>
          {results.length === 0 ? (
            <Notice tone="empty">No claims found. Try another search or stage.</Notice>
          ) : (
            <>
              {/* Small screens: one card per claim, no sideways scrolling. */}
              <ul className="space-y-3 md:hidden">
                {results.map((message) => (
                  <li key={message.id}>
                    <Link
                      to={`/dashboard/verification/${message.id}`}
                      className="block rounded-card border border-border bg-surface p-4 shadow-card hover:border-border-strong"
                    >
                      <p className="line-clamp-3 text-sm font-semibold">{message.claim_text}</p>
                      <div className="mt-3">
                        <VerdictBadge verdict={message.verdict} />
                      </div>
                      <p className="mt-3 flex items-center justify-between text-xs text-muted">
                        <span>
                          {stageLabel[stageOf(message)]} · {submittedOn(message.created_at)}
                        </span>
                        <span className="flex items-center gap-1 font-semibold text-brand">
                          Review <Icon name="arrowRight" size={16} />
                        </span>
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>

              <Card padding="none" className="hidden overflow-hidden md:block">
                <table className="w-full table-fixed text-left">
                  <thead className="border-b border-border bg-canvas text-xs text-secondary">
                    <tr>
                      <th className="px-6 py-3 font-semibold">Claim</th>
                      <th className="w-72 px-4 py-3 font-semibold">Verdict</th>
                      <th className="w-24 px-4 py-3">
                        <span className="sr-only">Open</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {results.map((message) => (
                      <tr key={message.id} className="text-sm hover:bg-canvas">
                        <td className="px-6 py-4">
                          <p className="line-clamp-2 font-semibold">{message.claim_text}</p>
                          <p className="mt-1 text-xs text-muted">
                            {stageLabel[stageOf(message)]} ·{" "}
                            <span className="tabular-nums">{submittedOn(message.created_at)}</span>
                          </p>
                        </td>
                        <td className="px-4 py-4">
                          <VerdictBadge verdict={message.verdict} />
                        </td>
                        <td className="px-4 py-4 text-right">
                          <Link
                            to={`/dashboard/verification/${message.id}`}
                            className="inline-flex min-h-10 items-center font-semibold text-brand"
                          >
                            Review
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            </>
          )}
        </>
      ) : null}
    </section>
  );
}
