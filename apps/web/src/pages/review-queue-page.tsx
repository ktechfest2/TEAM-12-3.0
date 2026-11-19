import { useState } from "react";
import { Icon } from "../components/icons";
import { Button } from "../components/ui/button";
import { Notice, PageHeader } from "../components/ui/surface";
import { LoginForm } from "../features/auth/login-form";
import { ReviewDetail } from "../features/review/review-detail";
import { ReviewQueue } from "../features/review/review-queue";
import { clearSession, useSession } from "../lib/auth/session";

const lead = "A person approves every correction before anything is sent.";

export function ReviewQueuePage() {
  const session = useSession();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  if (!session) {
    return (
      <section className="space-y-8">
        <PageHeader title="Review queue" lead={lead} />
        <LoginForm />
      </section>
    );
  }

  return (
    <section className="space-y-8">
      <PageHeader
        title="Review queue"
        lead={lead}
        aside={
          <p className="flex items-center gap-2 text-sm text-muted">
            <Icon name="user" size={18} />
            Signed in as {session.reviewerName}
            <Button variant="quiet" size="sm" icon="logout" onClick={clearSession}>
              Sign out
            </Button>
          </p>
        }
      />
      <div className="grid items-start gap-6 md:grid-cols-[20rem_1fr]">
        <ReviewQueue selectedId={selectedId} onSelect={setSelectedId} />
        {selectedId ? (
          <ReviewDetail key={selectedId} messageId={selectedId} />
        ) : (
          <Notice tone="empty">Choose a claim to review.</Notice>
        )}
      </div>
    </section>
  );
}
