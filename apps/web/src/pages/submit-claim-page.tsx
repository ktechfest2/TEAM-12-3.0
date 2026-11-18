import { ClaimForm } from "../features/claims/claim-form";

export function SubmitClaimPage() {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Is this election message true?</h1>
      <p className="text-muted">
        Clarion checks it against official INEC statements and tells you what the official source
        says.
      </p>
      <ClaimForm />
    </section>
  );
}
