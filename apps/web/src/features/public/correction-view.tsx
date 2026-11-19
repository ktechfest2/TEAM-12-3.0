import { verdictLabel, verdictTone } from "../claims/verdict";
import { languageName } from "../review/review-rules";
import { formatWhen, type PublicCorrection } from "./correction";
import { VerificationGuide } from "./verification-guide";

type Props = { correction: PublicCorrection };

export function CorrectionView({ correction }: Props) {
  return (
    <article className="space-y-5">
      <header className="space-y-2">
        <p className="text-sm text-muted">The message people are sharing</p>
        <blockquote className="text-lg">{correction.claim_text}</blockquote>
        <p
          className={`inline-block rounded-md border-2 px-3 py-1 font-bold ${verdictTone[correction.verdict]}`}
        >
          {verdictLabel[correction.verdict]}
        </p>
      </header>

      <section aria-label="Answer" className="space-y-2">
        <h2 className="font-bold">What the official source says</h2>
        <p>{correction.summary}</p>
        {correction.translations.length > 0 ? (
          <ul className="space-y-1 text-sm">
            {correction.translations.map((t) => (
              <li key={t.language}>
                <span className="font-semibold">{languageName[t.language]}:</span> {t.text}
              </li>
            ))}
          </ul>
        ) : null}
      </section>

      <section aria-label="Official source" className="space-y-1">
        <h2 className="font-bold">Official source</h2>
        {correction.source ? (
          <blockquote className="rounded-md border-l-4 border-brand bg-slate-50 p-3">
            <p>{correction.source.text}</p>
            <footer className="mt-2 text-sm">
              <a
                className="underline"
                href={correction.source.url}
                target="_blank"
                rel="noreferrer"
              >
                {correction.source.document_title}
              </a>{" "}
              ({correction.source.publisher})
            </footer>
          </blockquote>
        ) : (
          <p className="text-muted">We found no official statement on this yet.</p>
        )}
      </section>

      <p className="text-sm text-slate-700">
        Approved by {correction.approved_by} on {formatWhen(correction.approved_at)}. A person
        reviews every correction before it is sent.
      </p>

      <VerificationGuide correction={correction} />
    </article>
  );
}
