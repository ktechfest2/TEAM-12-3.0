import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { SubscribeForm } from "../features/subscribe/subscribe-form";

export function SubscribePage() {
  return (
    <section className="bg-surface">
      <div className="mx-auto max-w-[1200px] px-5 py-10 sm:px-8 md:py-16">
        <div className="mx-auto max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
            Text alerts
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight md:text-[40px]">
            Get official corrections by text
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-secondary">
            When a rumour is corrected, we text you the answer in your language, with a link to the
            official source. You choose what you get and how often.
          </p>
        </div>
        <div className="mx-auto mt-8 grid max-w-3xl gap-5">
          <Card className="p-5 md:p-7">
            <SubscribeForm />
          </Card>
          <div className="flex gap-3 rounded-[14px] border border-border bg-white p-4 text-sm leading-6 text-secondary">
            <Icon name="shieldCheck" size={18} className="mt-0.5 shrink-0 text-brand" />
            <p>
              We text a code first to check the number is yours. We store it encrypted, use it only
              for corrections a person has approved, and delete it when you stop. We never share it.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
