import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router";
import { LoginForm } from "../features/auth/login-form";
import { getMessage, listMessages } from "../features/review/review-api";
import { ReviewDetail } from "../features/review/review-detail";
import { stageLabel, stageOf } from "../features/review/review-rules";
import { useSession } from "../lib/auth/session";

export function VerificationPage() {
  const session = useSession();
  const { messageId } = useParams();
  const [selectedId, setSelectedId] = useState<string | null>(messageId ?? null);
  const [tab, setTab] = useState<"claim" | "investigation" | "actions">("claim");
  const queue = useQuery({
    queryKey: ["messages"],
    queryFn: listMessages,
    enabled: Boolean(session),
  });
  const detail = useQuery({
    queryKey: ["messages", selectedId],
    queryFn: () => getMessage(selectedId as string),
    enabled: Boolean(session && selectedId),
  });

  const selected = useMemo(
    () => queue.data?.find((message) => message.id === selectedId),
    [queue.data, selectedId],
  );

  if (!session) return <LoginForm />;

  return (
    <section>
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">Verification</p>
        <h1 className="mt-2 text-3xl font-bold">Verification workspace</h1>
      </div>

      {queue.isPending ? <p className="mt-6 text-muted">Loading claims...</p> : null}
      {queue.error ? (
        <p className="mt-6" role="alert">
          {queue.error.message}
        </p>
      ) : null}

      {queue.data && queue.data.length === 0 ? (
        <div className="mt-6 rounded-[14px] border border-border bg-white p-8 text-center">
          <h2 className="font-bold">No claims are waiting</h2>
          <p className="mt-2 text-sm text-muted">New submissions will appear here.</p>
        </div>
      ) : (
        <div className="mt-6 grid gap-5 xl:grid-cols-[260px_1fr]">
          <aside className="h-fit rounded-[14px] border border-border bg-white p-3">
            <h2 className="px-2 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-muted">
              Claims
            </h2>
            <div className="grid gap-1">
              {queue.data?.map((message) => (
                <button
                  type="button"
                  key={message.id}
                  onClick={() => setSelectedId(message.id)}
                  aria-current={selectedId === message.id ? "true" : undefined}
                  className={`min-h-14 rounded-[10px] px-3 py-2 text-left ${
                    selectedId === message.id ? "bg-brand-soft" : "hover:bg-surface"
                  }`}
                >
                  <span className="block truncate text-sm font-semibold">{message.claim_text}</span>
                  <span className="mt-1 block text-xs text-muted">
                    {stageLabel[stageOf(message)]}
                  </span>
                </button>
              ))}
            </div>
          </aside>

          <div className="min-w-0">
            {!selectedId ? (
              <div className="rounded-[14px] border border-border bg-white p-8 text-center text-muted">
                Choose a claim to begin verification.
              </div>
            ) : (
              <>
                <div className="mb-4 grid grid-cols-3 rounded-[10px] border border-border bg-white p-1 xl:hidden">
                  {(["claim", "investigation", "actions"] as const).map((item) => (
                    <button
                      type="button"
                      key={item}
                      onClick={() => setTab(item)}
                      className={`min-h-11 rounded-[8px] text-xs font-semibold capitalize ${
                        tab === item ? "bg-brand-soft text-brand" : "text-secondary"
                      }`}
                    >
                      {item}
                    </button>
                  ))}
                </div>
                {detail.isPending ? <p className="text-muted">Loading claim details...</p> : null}
                {detail.error ? <p role="alert">{detail.error.message}</p> : null}
                {detail.data ? (
                  <div className="rounded-[14px] border border-border bg-white p-5 md:p-6">
                    <div className="xl:hidden">
                      {tab === "claim" ? (
                        <section aria-label="Claim">
                          <p className="text-xs font-semibold text-muted">Original claim</p>
                          <h2 className="mt-2 text-xl font-bold">{detail.data.claim_text}</h2>
                          <p className="mt-3 text-sm text-muted">
                            Submitted {new Date(detail.data.created_at).toLocaleString("en-NG")}
                          </p>
                        </section>
                      ) : tab === "investigation" ? (
                        <section aria-label="Investigation">
                          <h2 className="text-lg font-bold">Investigation</h2>
                          {detail.data.source ? (
                            <blockquote className="mt-3 border-l-4 border-brand bg-surface p-4 text-sm leading-6">
                              {detail.data.source.text}
                              <footer className="mt-3 text-xs text-muted">
                                {detail.data.source.publisher}
                              </footer>
                            </blockquote>
                          ) : (
                            <p className="mt-3 text-sm text-muted">
                              No official source passage has been found yet.
                            </p>
                          )}
                        </section>
                      ) : (
                        <section aria-label="Reviewer actions">
                          <ReviewDetail key={detail.data.id} messageId={detail.data.id} />
                        </section>
                      )}
                    </div>
                    <div className="hidden xl:grid xl:grid-cols-[220px_1fr] xl:gap-6">
                      <section aria-label="Claim" className="border-r border-border pr-5">
                        <p className="text-xs font-semibold text-muted">Original claim</p>
                        <h2 className="mt-2 font-bold">{detail.data.claim_text}</h2>
                        {selected ? (
                          <p className="mt-3 text-xs text-muted">{stageLabel[stageOf(selected)]}</p>
                        ) : null}
                      </section>
                      <section aria-label="Investigation">
                        <h2 className="font-bold">Investigation</h2>
                        {detail.data.source ? (
                          <blockquote className="mt-3 border-l-4 border-brand bg-surface p-4 text-sm leading-6">
                            {detail.data.source.text}
                            <footer className="mt-3 text-xs text-muted">
                              {detail.data.source.publisher}
                            </footer>
                          </blockquote>
                        ) : (
                          <p className="mt-3 text-sm text-muted">
                            No official source passage has been found yet.
                          </p>
                        )}
                        <div className="mt-5 border-t border-border pt-5">
                          <ReviewDetail key={detail.data.id} messageId={detail.data.id} />
                        </div>
                      </section>
                    </div>
                  </div>
                ) : null}
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
