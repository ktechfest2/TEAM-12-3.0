import { ClaimForm } from "../features/claims/claim-form";

export function SubmitClaimPage() {
  return (
    <section className="space-y-8">
      <header className="max-w-2xl space-y-3">
        <p className="text-sm font-bold uppercase tracking-wider text-beacon-ink">
          Election claim check
        </p>
        <h1 className="text-4xl font-bold leading-tight text-brand sm:text-5xl">
          Is this election message true?
        </h1>
        <p className="text-lg text-muted">
          Clarion checks it against official INEC statements and tells you what the official source
          says.
        </p>
      </header>
      <ClaimForm />
    </section>
  );
}
