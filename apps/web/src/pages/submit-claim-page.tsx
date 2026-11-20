import { Card } from "../components/ui/card";
import { Container } from "../components/ui/container";
import { PageHeader } from "../components/ui/page-header";
import { ClaimForm } from "../features/claims/claim-form";

export function SubmitClaimPage() {
  return (
    <section className="bg-canvas">
      <Container width="prose" className="space-y-8 py-12 md:py-16">
        <PageHeader
          title="Is this election message accurate?"
          lead="Paste the claim exactly as you received it. Clarion checks it against available official source passages."
        />
        <Card>
          <ClaimForm />
        </Card>
        <p className="text-sm text-secondary">
          A result is not a final verdict until it cites an official source. Do not share a claim as
          confirmed based on an automated assessment alone.
        </p>
      </Container>
    </section>
  );
}
