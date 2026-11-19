import { useState } from "react";
import { LoginForm } from "../features/auth/login-form";
import { ReviewDetail } from "../features/review/review-detail";
import { ReviewQueue } from "../features/review/review-queue";
import { clearSession, useSession } from "../lib/auth/session";

export function ReviewQueuePage() {
  const session = useSession();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  if (!session) {
    return (
      <section className="space-y-4">
        <h1 className="text-2xl font-bold">Review queue</h1>
        <LoginForm />
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Review queue</h1>
        <p className="text-sm text-muted">
          Signed in as {session.reviewerName}{" "}
          <button type="button" onClick={clearSession} className="underline">
            Sign out
          </button>
        </p>
      </div>
      <div className="grid gap-6 md:grid-cols-[18rem_1fr]">
        <ReviewQueue selectedId={selectedId} onSelect={setSelectedId} />
        {selectedId ? (
          <ReviewDetail key={selectedId} messageId={selectedId} />
        ) : (
          <p className="text-muted">Choose a claim to review.</p>
        )}
      </div>
    </section>
  );
}
