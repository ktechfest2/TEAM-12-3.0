import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { Button } from "../../components/ui/button";
import { Textarea } from "../../components/ui/textarea";
import { api } from "../../lib/api/client";
import type { components } from "../../lib/api/schema.gen";
import type { ClaimResult } from "./verdict";
import { VerdictCard } from "./verdict-card";

type ClaimLanguage = components["schemas"]["Language"];

async function submitClaim(input: { text: string; language: ClaimLanguage }): Promise<ClaimResult> {
  const { data, error } = await api.POST("/claims", { body: input });
  if (error || !data) throw new Error("Could not check this claim. Try again.");
  return data;
}

export function ClaimForm() {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState<ClaimLanguage>("en");
  const mutation = useMutation({ mutationFn: submitClaim });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate({ text: text.trim(), language });
  };

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="space-y-3">
        <label htmlFor="claim" className="block font-semibold">
          Paste the message you received
        </label>
        <Textarea
          id="claim"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          minLength={3}
          required
          className="min-h-32"
        />
        <label htmlFor="claim-language" className="block text-sm font-semibold">
          Claim language
        </label>
        <select
          id="claim-language"
          value={language}
          onChange={(event) => setLanguage(event.target.value as ClaimLanguage)}
          className="min-h-11 w-full rounded-[10px] border border-border bg-white px-3"
        >
          <option value="en">English</option>
          <option value="yo">Yoruba</option>
          <option value="ha">Hausa</option>
          <option value="ig">Igbo</option>
          <option value="pcm">Nigerian Pidgin</option>
        </select>
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Checking..." : "Check claim"}
        </Button>
      </form>
      {mutation.error ? <p role="alert">{mutation.error.message}</p> : null}
      {mutation.data ? <VerdictCard result={mutation.data} /> : null}
    </div>
  );
}
