import { ShieldCheck } from "lucide-react";
import { Card } from "../components/ui/card";
import { ClaimForm } from "../features/claims/claim-form";

export function SubmitClaimPage() {
  return (
    <section className="bg-surface">
      <div className="mx-auto max-w-[1200px] px-5 py-10 sm:px-8 md:py-16">
        <div className="mx-auto max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
            Claim verification
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight md:text-[40px]">
            Is this election message accurate?
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-secondary">
            Paste the claim exactly as you received it. Clarion checks it against available official
            source passages.
          </p>
        </div>
        <div className="mx-auto mt-8 grid max-w-3xl gap-5">
          <Card className="p-5 md:p-7">
            <ClaimForm />
          </Card>
          <div className="flex gap-3 rounded-[14px] border border-border bg-white p-4 text-sm leading-6 text-secondary">
            <ShieldCheck size={18} className="mt-0.5 shrink-0 text-brand" aria-hidden="true" />
            <p>
              A result is not a final verdict until it cites an official source. Do not share a
              claim as confirmed based on an automated assessment alone.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
