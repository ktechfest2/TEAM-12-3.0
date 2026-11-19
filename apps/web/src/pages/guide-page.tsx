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
    <section className="mx-auto max-w-3xl px-5 py-12 sm:px-8 md:py-16">
      <h1 className="text-3xl font-bold tracking-tight md:text-[40px]">How Clarion works</h1>
      <p className="mt-3 text-base leading-7 text-secondary">
        Clarion closes the gap between a rumour spreading and the official correction reaching the
        voter. Every answer cites an official source and is approved by a person.
      </p>

      <ol className="mt-10 space-y-6 border-l-2 border-brand-100 pl-6">
        {steps.map((step, index) => (
          <li key={step.title} className="relative">
            <span className="absolute -left-[41px] grid size-7 place-items-center rounded-full bg-brand text-xs font-bold text-white">
              {index + 1}
            </span>
            <h2 className="font-bold">{step.title}</h2>
            <p className="mt-1 text-sm leading-6 text-secondary">{step.copy}</p>
          </li>
        ))}
      </ol>

      <h2 className="mt-14 text-xl font-bold">The three answers</h2>
      <ul className="mt-4 divide-y divide-border border-y border-border">
        {verdicts.map((item) => (
          <li key={item.verdict} className="flex flex-wrap items-center gap-x-4 gap-y-2 py-4">
            <span className="sm:w-72">
              <VerdictBadge verdict={item.verdict} />
            </span>
            <p className="min-w-0 flex-1 text-sm leading-6 text-secondary">{item.meaning}</p>
          </li>
        ))}
      </ul>

      <h2 className="mt-14 text-xl font-bold">Check a correction yourself</h2>
      <p className="mt-3 flex gap-3 text-sm leading-6 text-secondary">
        <Icon name="fingerprint" size={20} className="mt-0.5 text-brand" />
        <span>
          Every sent correction has its own public page. It shows the fingerprint, the previous
          correction's fingerprint and the exact record text. Run that text through SHA-256: if the
          result equals the fingerprint, nobody changed it after it was approved.
        </span>
      </p>

      <div className="mt-10">
        <Button as="link" to="/check" icon="search">
          Verify a claim
        </Button>
      </div>
    </section>
  );
}
