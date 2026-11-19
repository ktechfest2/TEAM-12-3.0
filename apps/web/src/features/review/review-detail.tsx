import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router";
import { Icon } from "../../components/icons";
import { Button } from "../../components/ui/button";
import {
  Card,
  controlClass,
  Loading,
  Notice,
  Pill,
  SectionTitle,
} from "../../components/ui/surface";
import { VerdictBadge } from "../claims/verdict-badge";
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
  type Stage,
  stageLabel,
  stageOf,
} from "./review-rules";
import { TranslationsPanel } from "./translations-panel";

type Props = { messageId: string };

const stageTone: Record<Stage, "neutral" | "good" | "bad" | "attention"> = {
  draft: "attention",
  approved: "good",
  rejected: "bad",
  escalated: "attention",
  sealed: "good",
};

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

  if (query.isPending) return <Loading />;
  if (query.error) return <Notice tone="error">{query.error.message}</Notice>;

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
    <article className="space-y-8" aria-label="Claim review">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <SectionTitle>Claim</SectionTitle>
          <Pill tone={stageTone[stage]}>{stageLabel[stage]}</Pill>
        </div>
        <h2 className="font-display text-2xl font-bold leading-snug text-ink">
          {message.claim_text}
        </h2>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <section aria-label="Draft answer">
          <Card className="h-full space-y-3">
            <SectionTitle icon="user">Draft answer</SectionTitle>
            <VerdictBadge verdict={message.verdict} />
            <label htmlFor="summary" className="block text-sm font-semibold">
              Answer people will read
            </label>
            <textarea
              id="summary"
              value={summary}
              onChange={(e) => setSummaryEdit(e.target.value)}
              rows={5}
              className={controlClass}
            />
            {summaryChanged ? (
              <div className="space-y-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={busy || summary.trim().length < 3}
                  onClick={() => saveSummary.mutate(summary.trim())}
                >
                  Save answer
                </Button>
                <p className="text-sm text-muted">
                  Saving a new answer removes existing translations.
                </p>
              </div>
            ) : null}
          </Card>
        </section>

        <section aria-label="Official source">
          <Card className="h-full space-y-3">
            <SectionTitle icon="shieldCheck">Official source</SectionTitle>
            {message.source ? (
              <blockquote className="space-y-3 border-l-4 border-beacon pl-4">
                <p className="font-display text-lg leading-snug">{message.source.text}</p>
                <footer className="text-sm text-muted">
                  <a
                    className="inline-flex items-center gap-1 font-semibold text-brand underline decoration-brand-200 underline-offset-2 hover:decoration-brand"
                    href={message.source.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {message.source.document_title}
                    <Icon name="external" size={14} />
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
          </Card>
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

      <section aria-label="Decision">
        <Card className="space-y-4">
          <SectionTitle icon="check">Decision</SectionTitle>
          <div className="space-y-1.5">
            <label htmlFor="note" className="block text-sm font-semibold">
              Note (optional)
            </label>
            <input
              id="note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className={controlClass}
            />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              icon="check"
              disabled={busy || summaryChanged || !canApprove(message)}
              onClick={() => decide.mutate("approved")}
            >
              Approve
            </Button>
            <Button variant="secondary" disabled={busy} onClick={() => decide.mutate("escalated")}>
              Escalate
            </Button>
            <Button variant="secondary" disabled={busy} onClick={() => decide.mutate("rejected")}>
              Reject
            </Button>
          </div>
          {missing.length > 0 ? (
            <p className="text-sm text-muted">
              Approve is available after these languages are approved:{" "}
              {missing.map((language) => languageName[language]).join(", ")}.
            </p>
          ) : null}
        </Card>
      </section>

      {stage === "approved" || stage === "sealed" ? (
        <section aria-label="Send">
          <Card className="space-y-4 border-brand-200 bg-brand-50">
            <SectionTitle icon="send">Send</SectionTitle>
            {stage === "approved" ? (
              <Button variant="secondary" icon="lock" disabled={busy} onClick={() => seal.mutate()}>
                Seal this message
              </Button>
            ) : (
              <>
                <p className="flex items-start gap-2 break-all font-mono text-sm text-brand">
                  <Icon name="fingerprint" size={18} className="mt-0.5" />
                  Integrity hash: {message.integrity_hash}
                </p>
                {broadcast.isSuccess ? (
                  <p className="flex items-center gap-2 font-semibold text-confirmed">
                    <Icon name="checkCircle" size={18} />
                    <span>
                      Sending started.{" "}
                      <Link to="/dashboard/board" className="underline underline-offset-2">
                        Watch the broadcast board
                      </Link>
                    </span>
                  </p>
                ) : (
                  <Button
                    icon="send"
                    disabled={broadcast.isPending}
                    onClick={() => broadcast.mutate()}
                  >
                    {broadcast.isPending ? "Starting..." : "Send to every channel"}
                  </Button>
                )}
              </>
            )}
          </Card>
        </section>
      ) : null}

      {failure ? <Notice tone="error">{failure.message}</Notice> : null}
    </article>
  );
}
