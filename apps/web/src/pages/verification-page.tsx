import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { Loading, Notice } from "../components/ui/notice";
import { PageTitle } from "../components/ui/page-header";
import { LoginForm } from "../features/auth/login-form";
import { listMessages } from "../features/review/review-api";
import { ReviewDetail } from "../features/review/review-detail";
import { stageLabel, stageOf } from "../features/review/review-rules";
import { useSession } from "../lib/auth/session";

export function VerificationPage() {
  const session = useSession();
  const { messageId } = useParams();
  const queue = useQuery({
    queryKey: ["messages"],
    queryFn: listMessages,
    enabled: Boolean(session),
  });

  if (!session) return <LoginForm />;

  return (
    <section className="space-y-6">
      <PageTitle title="Verification" />

      <p className="flex gap-2 text-sm text-secondary">
        <Icon name="shieldCheck" size={18} className="mt-0.5 shrink-0 text-brand" />
        Nothing is sent until a reviewer approves every language and seals it.
      </p>

      {queue.isPending ? <Loading>Loading claims...</Loading> : null}
      {queue.error ? <Notice tone="error">{queue.error.message}</Notice> : null}

      {queue.data && queue.data.length === 0 ? (
        <Notice tone="empty">No claims are waiting. New submissions will appear here.</Notice>
      ) : null}

      {queue.data && queue.data.length > 0 ? (
        <div className="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)]">
          {/* Below xl the list and the detail take turns, so neither is squeezed. */}
          <aside
            aria-label="Claims"
            className={`h-fit rounded-card border border-border bg-surface p-2 xl:sticky xl:top-8 ${
              messageId ? "hidden xl:block" : ""
            }`}
          >
            <h2 className="px-3 py-2 text-xs font-bold uppercase tracking-wider text-muted">
              Claims · {queue.data.length}
            </h2>
            <ul className="grid gap-0.5 xl:max-h-[calc(100vh-12rem)] xl:overflow-y-auto">
              {queue.data.map((message) => {
                const current = messageId === message.id;
                return (
                  <li key={message.id}>
                    <Link
                      to={`/dashboard/verification/${message.id}`}
                      aria-current={current ? "true" : undefined}
                      className={`block min-h-14 rounded-control px-3 py-3 ${
                        current ? "bg-brand-soft" : "hover:bg-canvas"
                      }`}
                    >
                      <span className="line-clamp-2 text-sm font-semibold xl:line-clamp-1">
                        {message.claim_text}
                      </span>
                      <span className="mt-1 block text-xs text-muted">
                        {stageLabel[stageOf(message)]}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </aside>

          {messageId ? (
            <div className="min-w-0 space-y-3">
              <Link
                to="/dashboard/verification"
                className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-brand xl:hidden"
              >
                <Icon name="arrowLeft" size={16} /> All claims
              </Link>
              <Card>
                <ReviewDetail key={messageId} messageId={messageId} />
              </Card>
            </div>
          ) : (
            <div className="hidden xl:block">
              <Notice tone="empty">Choose a claim to review it.</Notice>
            </div>
          )}
        </div>
      ) : null}
    </section>
  );
}
