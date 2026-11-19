import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Clock3, MessageSquareText, Radio } from "lucide-react";
import { Link } from "react-router";
import { Card } from "../components/ui/card";
import { StatCard } from "../components/ui/stat-card";
import { VerdictBadge } from "../components/ui/verdict-badge";
import { LoginForm } from "../features/auth/login-form";
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
        <h1 className="text-3xl font-bold">Reviewer overview</h1>
        <div className="mt-6">
          <LoginForm />
        </div>
      </section>
    );
  }

  if (query.isPending) {
    return (
      <section aria-busy="true">
        <h1 className="text-3xl font-bold">Overview</h1>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="h-32 animate-pulse rounded-[14px] bg-white" />
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
    <section>
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">Workspace</p>
        <h1 className="mt-2 text-3xl font-bold">Overview</h1>
        <p className="mt-2 text-sm text-muted">Live claim and verification activity.</p>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total claims"
          value={messages.length}
          detail="Available to this workspace"
          icon={MessageSquareText}
        />
        <StatCard
          label="Needs review"
          value={draft}
          detail="Waiting for a reviewer decision"
          icon={Clock3}
        />
        <StatCard
          label="Approved"
          value={approved}
          detail="Ready for sealing"
          icon={CheckCircle2}
        />
        <StatCard
          label="Sealed"
          value={sealed}
          detail="Prepared for controlled broadcast"
          icon={Radio}
        />
      </div>

      <Card className="mt-6 p-0">
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <h2 className="font-bold">Recent claims</h2>
          <Link
            to="/dashboard/claims"
            className="min-h-11 flex items-center text-sm font-semibold text-brand"
          >
            View all
          </Link>
        </div>
        {messages.length === 0 ? (
          <p className="p-5 text-sm text-muted">No claims are available.</p>
        ) : (
          <div className="divide-y divide-border">
            {messages.slice(0, 5).map((message) => (
              <Link
                key={message.id}
                to={`/dashboard/verification/${message.id}`}
                className="flex min-h-[72px] items-center justify-between gap-4 px-5 py-3 hover:bg-surface"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">{message.claim_text}</p>
                  <p className="mt-1 text-xs text-muted">{stageLabel[stageOf(message)]}</p>
                </div>
                <VerdictBadge verdict={message.verdict} />
              </Link>
            ))}
          </div>
        )}
      </Card>
    </section>
  );
}
