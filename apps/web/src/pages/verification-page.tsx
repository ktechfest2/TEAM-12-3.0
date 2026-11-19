import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { Icon } from "../components/icons";
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
    <section>
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">Verification</p>
      <h1 className="mt-2 text-3xl font-bold">Review and approve</h1>
      <p className="mt-2 flex max-w-3xl gap-2 text-sm leading-6 text-secondary">
        <Icon name="shieldCheck" size={18} className="mt-0.5 text-brand" />
        Nothing is sent until a reviewer approves the answer in every language and seals it. Each
        verdict must cite an official source.
      </p>

      {queue.isPending ? <p className="mt-6 text-muted">Loading claims...</p> : null}
      {queue.error ? (
        <p className="mt-6" role="alert">
          {queue.error.message}
        </p>
      ) : null}

      {queue.data && queue.data.length === 0 ? (
        <div className="mt-6 rounded-card border border-border bg-white p-8 text-center">
          <h2 className="font-bold">No claims are waiting</h2>
          <p className="mt-2 text-sm text-muted">New submissions will appear here.</p>
        </div>
      ) : null}

      {queue.data && queue.data.length > 0 ? (
        <div className="mt-6 grid gap-5 xl:grid-cols-[280px_1fr]">
          <aside
            aria-label="Claims"
            className="h-fit rounded-card border border-border bg-white p-3"
          >
            <h2 className="px-2 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-muted">
              Claims
            </h2>
            <ul className="grid max-h-72 gap-1 overflow-y-auto xl:max-h-[70vh]">
              {queue.data.map((message) => (
                <li key={message.id}>
                  <Link
                    to={`/dashboard/verification/${message.id}`}
                    aria-current={messageId === message.id ? "true" : undefined}
                    className={`block min-h-14 rounded-control px-3 py-2 ${
                      messageId === message.id ? "bg-brand-soft" : "hover:bg-surface"
                    }`}
                  >
                    <span className="block truncate text-sm font-semibold">
                      {message.claim_text}
                    </span>
                    <span className="mt-1 block text-xs text-muted">
                      {stageLabel[stageOf(message)]}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </aside>

          <div className="min-w-0 rounded-card border border-border bg-white p-5 md:p-6">
            {messageId ? (
              <ReviewDetail key={messageId} messageId={messageId} />
            ) : (
              <p className="text-center text-muted">Choose a claim to review it.</p>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
