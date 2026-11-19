import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
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
    <form onSubmit={onSubmit} className="max-w-md space-y-4">
      <p className="text-muted">Only invited reviewers can approve and send corrections.</p>
      <div>
        <label htmlFor="reviewer-name" className="block font-semibold">
          Your name
        </label>
        <input
          id="reviewer-name"
          value={reviewerName}
          onChange={(e) => setReviewerName(e.target.value)}
          required
          autoComplete="name"
          className="mt-1 w-full rounded-md border border-slate-300 p-2"
        />
      </div>
      <div>
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
          className="mt-1 w-full rounded-md border border-slate-300 p-2"
        />
      </div>
      <button
        type="submit"
        disabled={mutation.isPending}
        className="rounded-md bg-brand px-4 py-2 font-semibold text-white disabled:opacity-60"
      >
        {mutation.isPending ? "Checking..." : "Sign in"}
      </button>
      {mutation.error ? <p role="alert">{mutation.error.message}</p> : null}
    </form>
  );
}
