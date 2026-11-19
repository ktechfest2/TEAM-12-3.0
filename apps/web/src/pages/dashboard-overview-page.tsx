import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { Icon } from "../components/icons";
import { StatCard } from "../components/ui/stat-card";
import { PageTitle } from "../components/ui/surface";
import { LoginForm } from "../features/auth/login-form";
import { VerdictBadge } from "../features/claims/verdict-badge";
import { listMessages } from "../features/review/review-api";
import { stageLabel, stageOf } from "../features/review/review-rules";
import { useSession } from "../lib/auth/session";

export function DashboardOverviewPage() {
  const session = useSession();
  const query = useQuery({
    queryKey: ["messages"],
    queryFn: listMessages,
    enabled: Boolean(session),
    refetchInterval: 15000,
  });

  if (!session) {
    return (
      <section>
        <PageTitle title="Reviewer sign in" />
        <LoginForm />
      </section>
    );
  }

  if (query.isPending) {
    return (
      <section aria-busy="true" className="space-y-6">
        <PageTitle title="Overview" />
        <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="h-24 animate-pulse rounded-card bg-white sm:h-28" />
          ))}
        </div>
      </section>
    );
  }

  if (query.error) return <p role="alert">{query.error.message}</p>;

  const messages = query.data;
  const draft = messages.filter((message) => stageOf(message) === "draft").length;
  const approved = messages.filter((message) => stageOf(message) === "approved").length;
  const sealed = messages.filter((message) => stageOf(message) === "sealed").length;

  return (
    <section className="space-y-6">
      <PageTitle title="Overview" />

      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        <StatCard label="Total claims" value={messages.length} icon="messages" />
        <Link
          to="/dashboard/verification"
          className="block rounded-card transition-colors hover:border-brand-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
        >
          <StatCard label="Needs review" value={draft} icon="clock" />
        </Link>
        <StatCard label="Approved" value={approved} icon="checkCircle" />
        <StatCard label="Sealed" value={sealed} icon="lock" />
      </div>

      <div className="rounded-card border border-border bg-white shadow-card">
        <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-2 sm:px-5">
          <h2 className="font-bold">Recent claims</h2>
          <Link
            to="/dashboard/claims"
            className="flex min-h-11 items-center gap-1 text-sm font-semibold text-brand"
          >
            View all <Icon name="arrowRight" size={16} />
          </Link>
        </div>
        {messages.length === 0 ? (
          <p role="status" className="px-5 py-10 text-center text-sm text-muted">
            No claims yet. New submissions will appear here.
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {messages.slice(0, 5).map((message) => (
              <li key={message.id}>
                <Link
                  to={`/dashboard/verification/${message.id}`}
                  className="flex flex-col gap-2 px-4 py-3.5 hover:bg-surface sm:flex-row sm:items-center sm:justify-between sm:gap-4 sm:px-5"
                >
                  <div className="min-w-0">
                    <p className="line-clamp-2 text-sm font-semibold sm:line-clamp-1">
                      {message.claim_text}
                    </p>
                    <p className="mt-0.5 text-xs text-muted">{stageLabel[stageOf(message)]}</p>
                  </div>
                  <span className="shrink-0">
                    <VerdictBadge verdict={message.verdict} />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
