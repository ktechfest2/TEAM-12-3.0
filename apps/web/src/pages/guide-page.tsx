import { Icon } from "../components/icons";
import { Button } from "../components/ui/button";
import type { Verdict } from "../features/claims/verdict";
import { VerdictBadge } from "../features/claims/verdict-badge";

const steps = [
  {
    title: "A claim arrives",
    copy: "Anyone can paste a message on the web, in English, Yoruba, Hausa, Igbo or Pidgin.",
  },
  {
    title: "It is matched to an official source",
    copy: "Clarion looks for the passage in an official statement that speaks to the claim. It never answers from its own opinion.",
  },
  {
    title: "A person reviews it",
    copy: "A reviewer checks the cited passage and approves the answer in every language. Nothing is sent without that approval.",
  },
  {
    title: "The correction is sealed",
    copy: "Approved text is sealed with a fingerprint, so any later change can be detected.",
  },
  {
    title: "It reaches the people who saw the rumour",
    copy: "The same approved correction goes out as text, voice note and shareable card, and has its own public page.",
  },
] as const;

const verdicts: readonly { verdict: Verdict; meaning: string }[] = [
  {
    verdict: "confirmed",
    meaning: "An official source says the same thing. The passage is shown with a link.",
  },
  {
    verdict: "contradicted",
    meaning: "An official source says something different. The passage is shown with a link.",
  },
  {
    verdict: "no_official_statement",
    meaning:
      "Clarion found no official passage about it. This is not a ruling that the claim is true or false.",
  },
];

export function GuidePage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 md:py-16">
      <header>
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">How Clarion works</h1>
        <p className="mt-3 text-base leading-7 text-secondary sm:text-lg">
          Every answer cites an official source and is approved by a person before anyone receives
          it.
        </p>
      </header>

      <section aria-labelledby="steps-title" className="mt-10 sm:mt-12">
        <h2 id="steps-title" className="text-xs font-bold uppercase tracking-wider text-muted">
          From rumour to correction
        </h2>
        <ol className="mt-4 divide-y divide-border rounded-card border border-border bg-white">
          {steps.map((step, index) => (
            <li key={step.title} className="flex gap-4 p-4 sm:p-5">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand-soft text-sm font-bold text-brand tabular-nums">
                {index + 1}
              </span>
              <div className="min-w-0">
                <h3 className="font-semibold leading-8">{step.title}</h3>
                <p className="mt-0.5 text-sm leading-6 text-secondary">{step.copy}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="verdicts-title" className="mt-10 sm:mt-12">
        <h2 id="verdicts-title" className="text-xs font-bold uppercase tracking-wider text-muted">
          The three answers
        </h2>
        <ul className="mt-4 grid gap-3">
          {verdicts.map((item) => (
            <li
              key={item.verdict}
              className="rounded-card border border-border bg-white p-4 sm:flex sm:items-start sm:gap-5 sm:p-5"
            >
              <div className="sm:w-72 sm:shrink-0">
                <VerdictBadge verdict={item.verdict} />
              </div>
              <p className="mt-3 text-sm leading-6 text-secondary sm:mt-1">{item.meaning}</p>
            </li>
          ))}
        </ul>
      </section>

      <section
        aria-labelledby="check-title"
        className="mt-10 rounded-card border border-brand-200 bg-brand-50 p-5 sm:mt-12 sm:p-6"
      >
        <h2 id="check-title" className="flex items-center gap-2 text-lg font-bold text-brand">
          <Icon name="fingerprint" size={22} />
          Check a correction yourself
        </h2>
        <p className="mt-2 text-sm leading-6 text-secondary">
          Every sent correction has its own public page. It shows the fingerprint, the previous
          correction's fingerprint and the exact record text. Run that text through SHA-256: if the
          result equals the fingerprint, nobody changed it after it was approved.
        </p>
      </section>

      <div className="mt-10 flex flex-col gap-3 sm:flex-row">
        <Button as="link" to="/check" icon="search">
          Verify a claim
        </Button>
        <Button as="link" to="/subscribe" variant="outline">
          Get text alerts
        </Button>
      </div>
    </div>
  );
}
