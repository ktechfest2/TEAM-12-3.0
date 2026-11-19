import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { Button } from "../../components/ui/button";
import { Card, controlClass, Notice } from "../../components/ui/surface";
import { api } from "../../lib/api/client";
import type { ClaimResult } from "./verdict";
import { VerdictCard } from "./verdict-card";

async function submitClaim(text: string): Promise<ClaimResult> {
  const { data, error } = await api.POST("/claims", { body: { text, language: "en" } });
  if (error || !data) throw new Error("Could not check this claim. Try again.");
  return data;
}

export function ClaimForm() {
  const [text, setText] = useState("");
  const mutation = useMutation({ mutationFn: submitClaim });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate(text);
  };

  return (
    <div className="space-y-6">
      <Card>
        <form onSubmit={onSubmit} className="space-y-4">
          <label htmlFor="claim" className="block text-lg font-semibold text-brand">
            Paste the message you received
          </label>
          <textarea
            id="claim"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            minLength={3}
            required
            placeholder="For example: INEC has moved the election to next month."
            className={`${controlClass} resize-y text-lg`}
          />
          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={mutation.isPending} icon="search">
              {mutation.isPending ? "Checking..." : "Check it"}
            </Button>
            <p className="text-sm text-muted">Nothing is sent to anyone. You only get an answer.</p>
          </div>
        </form>
      </Card>
      {mutation.error ? <Notice tone="error">{mutation.error.message}</Notice> : null}
      {mutation.data ? <VerdictCard result={mutation.data} /> : null}
    </div>
  );
}
