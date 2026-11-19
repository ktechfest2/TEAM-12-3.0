import { Icon } from "../components/icons";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { ClaimForm } from "../features/claims/claim-form";
import { FactCheckCard } from "../features/public/public-cards";
import { demonstrationNotice, factChecks } from "../features/public/public-demo";

const steps = [
  ["Send a claim", "Paste a message in English, Yoruba, Hausa, Igbo or Pidgin."],
  ["Match an official source", "Clarion finds the official passage that speaks to it."],
  [
    "Get one of three answers",
    "Confirmed, contradicted or no official statement, with the source.",
  ],
  ["A person approves", "A reviewer approves every language. Nothing is sent without it."],
  ["Sealed and sent", "Each correction gets a fingerprint anyone can check."],
] as const;

export function Homepage() {
  return (
    <>
      <section className="border-b border-border bg-surface">
        <div className="mx-auto grid max-w-[1200px] gap-10 px-5 py-14 sm:px-8 md:grid-cols-[1.1fr_.9fr] md:items-center md:py-20">
          <div>
            <h1 className="max-w-[640px] text-[34px] leading-[1.1] font-bold tracking-tight text-foreground md:text-[48px]">
              Is that election message true? Check it against the official source.
            </h1>
            <p className="mt-5 max-w-[520px] text-base leading-7 text-secondary">
              Every answer cites an official statement and is approved by a person before it is
              sent.
            </p>
            <Button as="link" to="/guide" variant="quiet" className="mt-4 -ml-4">
              How Clarion works <Icon name="arrowRight" size={16} />
            </Button>
          </div>
          <Card className="p-5 md:p-6">
            <h2 className="text-lg font-bold">Check a message you received</h2>
            <p className="mb-4 mt-1 text-sm text-secondary">
              Nothing is sent to anyone. You only get an answer.
            </p>
            <ClaimForm />
          </Card>
        </div>
      </section>

      <section className="mx-auto max-w-[1200px] px-5 py-14 sm:px-8">
        <h2 className="text-2xl font-bold">From rumour to correction</h2>
        <ol className="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-5">
          {steps.map(([title, copy], index) => (
            <li key={title} className="border-t-2 border-brand pt-4">
              <span className="text-sm font-bold text-brand">{index + 1}</span>
              <h3 className="mt-1 font-bold">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-secondary">{copy}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="border-t border-border bg-surface">
        <div className="mx-auto max-w-[1200px] px-5 py-14 sm:px-8">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold">Recent fact-checks</h2>
              <p className="mt-2 text-sm text-muted">{demonstrationNotice}</p>
            </div>
            <Button as="link" to="/fact-checks" variant="ghost" className="hidden sm:inline-flex">
              View all <Icon name="arrowRight" size={16} />
            </Button>
          </div>
          <div className="mt-7 grid gap-4 md:grid-cols-3">
            {factChecks.map((factCheck) => (
              <FactCheckCard key={factCheck.slug} factCheck={factCheck} />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
