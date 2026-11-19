import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router";
import { Icon } from "../components/icons";
import { Loading, PageTitle } from "../components/ui/surface";
import { LoginForm } from "../features/auth/login-form";
import { VerdictBadge } from "../features/claims/verdict-badge";
import { listMessages } from "../features/review/review-api";
import { stageLabel, stageOf } from "../features/review/review-rules";
import { useSession } from "../lib/auth/session";

const fieldClass =
  "min-h-11 w-full rounded-control border border-border bg-white text-sm focus:border-brand";

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
    <section className="space-y-5">
      <PageTitle title="Claims" />

      <div className="flex flex-col gap-3 sm:flex-row">
        <label className="relative flex-1">
          <span className="sr-only">Search claims</span>
          <Icon name="search" size={18} className="absolute left-3 top-3.5 text-muted" />
          <input
            type="search"
            value={queryText}
            onChange={(event) => setQueryText(event.target.value)}
            placeholder="Search claim text"
            className={`${fieldClass} pl-10 pr-3`}
          />
        </label>
        <label className="sm:w-52">
          <span className="sr-only">Filter by stage</span>
          <select
            value={stage}
            onChange={(event) => setStage(event.target.value)}
            className={`${fieldClass} px-3`}
          >
            <option value="all">All stages</option>
            <option value="draft">Needs review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="escalated">Escalated</option>
            <option value="sealed">Sealed</option>
          </select>
        </label>
      </div>

      {query.isPending ? <Loading>Loading claims...</Loading> : null}
      {query.error ? <p role="alert">{query.error.message}</p> : null}

      {query.data ? (
        <>
          <p className="text-sm text-muted" role="status">
            {results.length} {results.length === 1 ? "claim" : "claims"}
          </p>
          {results.length === 0 ? (
            <div className="rounded-card border border-border bg-white px-6 py-10 text-center">
              <h2 className="font-bold">No claims found</h2>
              <p className="mt-1 text-sm text-muted">Try another search or stage.</p>
            </div>
          ) : (
            <>
              {/* Small screens: one card per claim, no sideways scrolling. */}
              <ul className="space-y-3 md:hidden">
                {results.map((message) => (
                  <li key={message.id}>
                    <Link
                      to={`/dashboard/verification/${message.id}`}
                      className="block rounded-card border border-border bg-white p-4 shadow-card hover:border-border-strong"
                    >
                      <p className="line-clamp-3 text-sm font-semibold leading-6">
                        {message.claim_text}
                      </p>
                      <div className="mt-3">
                        <VerdictBadge verdict={message.verdict} />
                      </div>
                      <p className="mt-3 flex items-center justify-between text-xs text-muted">
                        <span>
                          {stageLabel[stageOf(message)]} · {submittedOn(message.created_at)}
                        </span>
                        <span className="flex items-center gap-1 font-semibold text-brand">
                          Review <Icon name="arrowRight" size={14} />
                        </span>
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>

              <div className="hidden overflow-hidden rounded-card border border-border bg-white shadow-card md:block">
                <table className="w-full table-fixed text-left">
                  <thead className="border-b border-border bg-surface text-xs text-muted">
                    <tr>
                      <th className="px-5 py-3 font-semibold">Claim</th>
                      <th className="w-72 px-4 py-3 font-semibold">Verdict</th>
                      <th className="w-24 px-4 py-3">
                        <span className="sr-only">Open</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {results.map((message) => (
                      <tr key={message.id} className="text-sm hover:bg-surface">
                        <td className="px-5 py-3.5">
                          <p className="line-clamp-2 font-medium leading-6">{message.claim_text}</p>
                          <p className="mt-0.5 text-xs text-muted">
                            {stageLabel[stageOf(message)]} ·{" "}
                            <span className="tabular-nums">{submittedOn(message.created_at)}</span>
                          </p>
                        </td>
                        <td className="px-4 py-3.5">
                          <VerdictBadge verdict={message.verdict} />
                        </td>
                        <td className="px-4 py-3.5 text-right">
                          <Link
                            to={`/dashboard/verification/${message.id}`}
                            className="inline-flex min-h-11 items-center font-semibold text-brand"
                          >
                            Review
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      ) : null}
    </section>
  );
}
