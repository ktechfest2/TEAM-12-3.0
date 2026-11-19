import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router";
import { VerdictBadge } from "../components/ui/verdict-badge";
import { LoginForm } from "../features/auth/login-form";
import { listMessages } from "../features/review/review-api";
import { stageLabel, stageOf } from "../features/review/review-rules";
import { useSession } from "../lib/auth/session";

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
  if (query.isPending) return <p className="text-muted">Loading claims...</p>;
  if (query.error) return <p role="alert">{query.error.message}</p>;

  return (
    <section>
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">Claims</p>
        <h1 className="mt-2 text-3xl font-bold">Claim management</h1>
      </div>
      <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_200px]">
        <label className="relative">
          <span className="sr-only">Search claims</span>
          <Search size={18} className="absolute left-3 top-3.5 text-muted" aria-hidden="true" />
          <input
            type="search"
            value={queryText}
            onChange={(event) => setQueryText(event.target.value)}
            placeholder="Search claim text"
            className="min-h-11 w-full rounded-[10px] border border-border bg-white pl-10 pr-3"
          />
        </label>
        <label>
          <span className="sr-only">Filter by stage</span>
          <select
            value={stage}
            onChange={(event) => setStage(event.target.value)}
            className="min-h-11 w-full rounded-[10px] border border-border bg-white px-3"
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

      <p className="mt-5 text-sm text-muted" role="status">
        {results.length} claims
      </p>
      {results.length === 0 ? (
        <div className="mt-4 rounded-[14px] border border-border bg-white p-8 text-center">
          <h2 className="font-bold">No claims found</h2>
          <p className="mt-2 text-sm text-muted">Try another search or stage.</p>
        </div>
      ) : (
        <div className="mt-4 overflow-x-auto rounded-[14px] border border-border bg-white">
          <table className="w-full min-w-[720px] text-left">
            <thead className="border-b border-border bg-surface text-xs text-muted">
              <tr>
                <th className="px-5 py-3 font-semibold">Claim</th>
                <th className="px-5 py-3 font-semibold">Verdict</th>
                <th className="px-5 py-3 font-semibold">Stage</th>
                <th className="px-5 py-3 font-semibold">Submitted</th>
                <th className="px-5 py-3">
                  <span className="sr-only">Open</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {results.map((message) => (
                <tr key={message.id} className="text-sm">
                  <td className="max-w-[360px] px-5 py-4 font-medium">{message.claim_text}</td>
                  <td className="px-5 py-4">
                    <VerdictBadge verdict={message.verdict} />
                  </td>
                  <td className="px-5 py-4 text-secondary">{stageLabel[stageOf(message)]}</td>
                  <td className="px-5 py-4 text-muted">
                    {new Date(message.created_at).toLocaleDateString("en-NG")}
                  </td>
                  <td className="px-5 py-4">
                    <Link
                      to={`/dashboard/verification/${message.id}`}
                      className="min-h-11 flex items-center font-semibold text-brand"
                    >
                      Review
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
