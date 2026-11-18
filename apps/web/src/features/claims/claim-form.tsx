import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
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
      <form onSubmit={onSubmit} className="space-y-3">
        <label htmlFor="claim" className="block font-semibold">
          Paste the message you received
        </label>
        <textarea
          id="claim"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          minLength={3}
          required
          className="w-full rounded-md border border-slate-300 p-3"
        />
        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-brand px-4 py-2 font-semibold text-white disabled:opacity-60"
        >
          {mutation.isPending ? "Checking..." : "Check it"}
        </button>
      </form>
      {mutation.error ? <p role="alert">{mutation.error.message}</p> : null}
      {mutation.data ? <VerdictCard result={mutation.data} /> : null}
    </div>
  );
}
