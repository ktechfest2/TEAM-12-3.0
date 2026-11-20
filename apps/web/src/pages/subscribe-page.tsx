import { Card } from "../components/ui/card";
import { Container } from "../components/ui/container";
import { PageHeader } from "../components/ui/page-header";
import { SubscribeForm } from "../features/subscribe/subscribe-form";

export function SubscribePage() {
  return (
    <section className="bg-canvas">
      <Container width="prose" className="space-y-8 py-12 md:py-16">
        <PageHeader
          title="Get official corrections by text"
          lead="When a rumour is corrected, we text you the answer in your language, with a link to the official source. You choose what you get and how often."
        />
        <Card>
          <SubscribeForm />
        </Card>
        <p className="text-sm text-secondary">
          We text a code first to check the number is yours. We store it encrypted, use it only for
          corrections a person has approved, and delete it when you stop. We never share it.
        </p>
      </Container>
    </section>
  );
}
