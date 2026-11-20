import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { Icon } from "../../components/icons";
import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { controlClass } from "../../components/ui/input";
import { Notice } from "../../components/ui/notice";
import { api } from "../../lib/api/client";
import { saveSession } from "../../lib/auth/session";

async function exchange(inviteCode: string, reviewerName: string): Promise<void> {
  const { data, error } = await api.POST("/auth/tokens", {
    body: { invite_code: inviteCode, reviewer_name: reviewerName },
  });
  if (error || !data) throw new Error("That invite code was not accepted. Check it and try again.");
  saveSession({ token: data.access_token, reviewerName: data.reviewer_name });
}

export function LoginForm() {
  const [inviteCode, setInviteCode] = useState("");
  const [reviewerName, setReviewerName] = useState("");
  const mutation = useMutation({
    mutationFn: () => exchange(inviteCode.trim(), reviewerName.trim()),
  });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <Card className="max-w-md">
      <form onSubmit={onSubmit} className="space-y-4">
        <p className="flex items-start gap-2 text-muted">
          <Icon name="lock" size={20} className="mt-0.5 text-brand" />
          Only invited reviewers can approve and send corrections.
        </p>
        <div className="space-y-2">
          <label htmlFor="reviewer-name" className="block font-semibold">
            Your name
          </label>
          <input
            id="reviewer-name"
            value={reviewerName}
            onChange={(e) => setReviewerName(e.target.value)}
            required
            autoComplete="name"
            className={controlClass}
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="invite-code" className="block font-semibold">
            Invite code
          </label>
          <input
            id="invite-code"
            type="password"
            value={inviteCode}
            onChange={(e) => setInviteCode(e.target.value)}
            required
            autoComplete="off"
            className={controlClass}
          />
        </div>
        <Button type="submit" disabled={mutation.isPending} className="w-full">
          {mutation.isPending ? "Checking..." : "Sign in"}
        </Button>
        {mutation.error ? <Notice tone="error">{mutation.error.message}</Notice> : null}
      </form>
    </Card>
  );
}
