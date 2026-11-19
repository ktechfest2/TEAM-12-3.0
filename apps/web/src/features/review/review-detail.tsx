import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router";
import { verdictLabel, verdictTone } from "../claims/verdict";
import {
  addReview,
  approveTranslation,
  broadcastMessage,
  draftTranslation,
  getMessage,
  sealMessage,
} from "./review-api";
import {
  canApprove,
  type Language,
  languageName,
  type Message,
  missingApprovals,
  stageLabel,
  stageOf,
} from "./review-rules";
import { TranslationsPanel } from "./translations-panel";

type Props = { messageId: string };

export function ReviewDetail({ messageId }: Props) {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: ["messages", messageId],
    queryFn: () => getMessage(messageId),
  });
  const [summaryEdit, setSummaryEdit] = useState<string | null>(null);
  const [note, setNote] = useState("");

  const store = (message: Message) => {
    queryClient.setQueryData(["messages", messageId], message);
    void queryClient.invalidateQueries({ queryKey: ["messages"], exact: true });
  };

  const saveSummary = useMutation({
    mutationFn: (summary: string) => addReview(messageId, { status: "pending", summary }),
    onSuccess: (message) => {
      setSummaryEdit(null);
      store(message);
    },
  });
  const draft = useMutation({
    mutationFn: (v: { language: Language; text?: string }) =>
      draftTranslation(messageId, v.language, v.text),
    onSuccess: store,
  });
  const approveLanguage = useMutation({
    mutationFn: (language: Language) => approveTranslation(messageId, language),
    onSuccess: store,
  });
  const decide = useMutation({
    mutationFn: (status: "approved" | "rejected" | "escalated") =>
      addReview(messageId, { status, ...(note.trim() ? { note: note.trim() } : {}) }),
    onSuccess: store,
  });
  const seal = useMutation({ mutationFn: () => sealMessage(messageId), onSuccess: store });
  const broadcast = useMutation({ mutationFn: () => broadcastMessage(messageId) });

  if (query.isPending) return <p className="text-muted">Loading...</p>;
  if (query.error) return <p role="alert">{query.error.message}</p>;

  const message = query.data;
  const stage = stageOf(message);
  const busy =
    saveSummary.isPending ||
    draft.isPending ||
    approveLanguage.isPending ||
    decide.isPending ||
    seal.isPending;
  const failure = [saveSummary, draft, approveLanguage, decide, seal, broadcast].find(
    (m) => m.error,
  )?.error;
  const missing = missingApprovals(message);
  const summary = summaryEdit ?? message.summary;
  const summaryChanged = summaryEdit !== null && summaryEdit !== message.summary;

  return (
    <article className="space-y-6" aria-label="Claim review">
      <header className="space-y-1">
        <p className="text-sm text-muted">Claim</p>
        <h2 className="text-xl font-bold">{message.claim_text}</h2>
        <p className="text-sm text-muted">{stageLabel[stage]}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        <section aria-label="Draft answer" className="space-y-2">
          <h3 className="font-bold">Draft answer</h3>
          <p
            className={`inline-block rounded-md border-2 px-2 py-1 ${verdictTone[message.verdict]}`}
          >
            {verdictLabel[message.verdict]}
          </p>
          <label htmlFor="summary" className="block text-sm font-semibold">
            Answer people will read
          </label>
          <textarea
            id="summary"
            value={summary}
            onChange={(e) => setSummaryEdit(e.target.value)}
            rows={5}
            className="w-full rounded-md border border-slate-300 p-2"
          />
          {summaryChanged ? (
            <>
              <button
                type="button"
                disabled={busy || summary.trim().length < 3}
                onClick={() => saveSummary.mutate(summary.trim())}
                className="rounded-md border border-slate-300 px-3 py-1"
              >
                Save answer
              </button>
              <p className="text-sm text-muted">
                Saving a new answer removes existing translations.
              </p>
            </>
          ) : null}
        </section>

        <section aria-label="Official source" className="space-y-2">
          <h3 className="font-bold">Official source</h3>
          {message.source ? (
            <blockquote className="rounded-md border-l-4 border-brand bg-slate-50 p-3">
              <p>{message.source.text}</p>
              <footer className="mt-2 text-sm text-slate-700">
                <a className="underline" href={message.source.url} target="_blank" rel="noreferrer">
                  {message.source.document_title}
                </a>{" "}
                ({message.source.publisher})
              </footer>
            </blockquote>
          ) : (
            <p className="text-muted">
              No official passage was found. The answer can only say that there is no official
              statement.
            </p>
          )}
        </section>
      </div>

      <TranslationsPanel
        message={message}
        busy={busy}
        onDraft={(language, text) =>
          draft.mutate(text === undefined ? { language } : { language, text })
        }
        onApprove={(language) => approveLanguage.mutate(language)}
      />

      <section aria-label="Decision" className="space-y-2">
        <h3 className="font-bold">Decision</h3>
        <label htmlFor="note" className="block text-sm font-semibold">
          Note (optional)
        </label>
        <input
          id="note"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className="w-full rounded-md border border-slate-300 p-2"
        />
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            disabled={busy || summaryChanged || !canApprove(message)}
            onClick={() => decide.mutate("approved")}
            className="rounded-md bg-brand px-4 py-2 font-semibold text-white disabled:opacity-50"
          >
            Approve
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => decide.mutate("escalated")}
            className="rounded-md border border-slate-300 px-4 py-2"
          >
            Escalate
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => decide.mutate("rejected")}
            className="rounded-md border border-slate-300 px-4 py-2"
          >
            Reject
          </button>
        </div>
        {missing.length > 0 ? (
          <p className="text-sm text-muted">
            Approve is available after these languages are approved:{" "}
            {missing.map((language) => languageName[language]).join(", ")}.
          </p>
        ) : null}
      </section>

      {stage === "approved" || stage === "sealed" ? (
        <section aria-label="Send" className="space-y-2">
          <h3 className="font-bold">Send</h3>
          {stage === "approved" ? (
            <button
              type="button"
              disabled={busy}
              onClick={() => seal.mutate()}
              className="rounded-md border border-brand px-4 py-2 font-semibold text-brand"
            >
              Seal this message
            </button>
          ) : (
            <>
              <p className="break-all text-sm">Integrity hash: {message.integrity_hash}</p>
              {broadcast.isSuccess ? (
                <p>
                  Sending started.{" "}
                  <Link to="/dashboard/board" className="underline">
                    Watch the broadcast board
                  </Link>
                </p>
              ) : (
                <button
                  type="button"
                  disabled={broadcast.isPending}
                  onClick={() => broadcast.mutate()}
                  className="rounded-md bg-brand px-4 py-2 font-semibold text-white disabled:opacity-60"
                >
                  {broadcast.isPending ? "Starting..." : "Send to every channel"}
                </button>
              )}
            </>
          )}
        </section>
      ) : null}

      {failure ? <p role="alert">{failure.message}</p> : null}
    </article>
  );
}
