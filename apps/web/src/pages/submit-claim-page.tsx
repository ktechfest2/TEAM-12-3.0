import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { ClaimForm } from "../features/claims/claim-form";

export function SubmitClaimPage() {
  return (
    <section className="bg-canvas">
      <div className="mx-auto max-w-page px-6 py-12 sm:px-8 md:py-16">
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
        <div className="mx-auto mt-8 grid max-w-3xl gap-4">
          <Card className="p-6 md:p-8">
            <ClaimForm />
          </Card>
          <div className="flex gap-3 rounded-card border border-border bg-surface p-4 text-sm leading-6 text-secondary">
            <Icon name="shieldCheck" size={18} className="mt-0.5 shrink-0 text-brand" />
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
