import { Icon } from "../../components/icons";
import { Card } from "../../components/ui/card";
import { SectionTitle } from "../../components/ui/section-title";
import { verdictAccent } from "../claims/verdict";
import { VerdictBadge } from "../claims/verdict-badge";
import { languageName } from "../review/review-rules";
import { formatWhen, type PublicCorrection } from "./correction";
import { ListenControl } from "./listen-control";
import { VerificationGuide } from "./verification-guide";

type Props = { correction: PublicCorrection };

export function CorrectionView({ correction }: Props) {
  return (
    <article className="space-y-6">
      <div className="overflow-hidden rounded-card border border-border bg-canvas shadow-lift">
        <div className={`h-1.5 ${verdictAccent[correction.verdict]}`} />
        <header className="space-y-4 p-6 sm:p-6">
          <p className="text-sm font-semibold text-muted">The message people are sharing</p>
          <blockquote className="text-2xl leading-snug text-foreground">
            {correction.claim_text}
          </blockquote>
          <VerdictBadge verdict={correction.verdict} large />
        </header>
      </div>

      <section aria-label="Answer">
        <Card className="space-y-3">
          <h2 className="text-xl font-bold text-brand">What the official source says</h2>
          <p className="text-lg">{correction.summary}</p>
          <ListenControl messageId={correction.message_id} language="en" />
          {correction.translations.length > 0 ? (
            <ul className="space-y-4 border-t border-border pt-3">
              {correction.translations.map((t) => (
                <li key={t.language} className="space-y-2">
                  <div className="flex gap-2">
                    <Icon name="language" size={18} className="mt-1 text-brand" />
                    <span>
                      <span className="font-semibold text-brand">{languageName[t.language]}:</span>{" "}
                      {t.text}
                    </span>
                  </div>
                  <ListenControl messageId={correction.message_id} language={t.language} />
                </li>
              ))}
            </ul>
          ) : null}
        </Card>
      </section>

      <section aria-label="Official source">
        <Card className="space-y-3">
          <SectionTitle icon="shieldCheck">Official source</SectionTitle>
          {correction.source ? (
            <blockquote className="space-y-3 border-l-4 border-brand pl-4">
              <p className="text-lg leading-snug">{correction.source.text}</p>
              <footer className="text-sm text-muted">
                <a
                  className="inline-flex items-center gap-1 font-semibold text-brand underline decoration-brand-line underline-offset-2 hover:decoration-brand"
                  href={correction.source.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {correction.source.document_title}
                  <Icon name="external" size={14} />
                </a>{" "}
                ({correction.source.publisher})
              </footer>
            </blockquote>
          ) : (
            <p className="text-muted">We found no official statement on this yet.</p>
          )}
        </Card>
      </section>

      <p className="flex items-start gap-2 text-sm text-muted">
        <Icon name="user" size={18} className="mt-0.5 text-brand" />
        <span>
          Approved by {correction.approved_by} on {formatWhen(correction.approved_at)}. A person
          reviews every correction before it is sent.
        </span>
      </p>

      <VerificationGuide correction={correction} />
    </article>
  );
}
