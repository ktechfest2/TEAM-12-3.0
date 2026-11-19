import { Icon } from "../../components/icons";
import { type ClaimResult, verdictAccent } from "./verdict";
import { VerdictBadge } from "./verdict-badge";

type Props = { result: ClaimResult };

export function VerdictCard({ result }: Props) {
  return (
    <article
      aria-label="Verdict"
      className="overflow-hidden rounded-card border border-line bg-surface shadow-lift"
    >
      <div className={`h-1.5 ${verdictAccent[result.verdict]}`} />
      <div className="space-y-4 p-5 sm:p-6">
        <VerdictBadge verdict={result.verdict} large />
        <p className="font-display text-xl leading-snug text-ink">{result.text}</p>
        {result.source ? (
          <p className="flex flex-wrap items-center gap-x-1.5 border-t border-line pt-4 text-sm text-muted">
            <Icon name="shieldCheck" size={16} className="text-brand" />
            Source:{" "}
            <a
              className="inline-flex items-center gap-1 font-semibold text-brand underline decoration-brand-200 underline-offset-2 hover:decoration-brand"
              href={result.source.url}
              target="_blank"
              rel="noreferrer"
            >
              {result.source.document_title}
              <Icon name="external" size={14} />
            </a>{" "}
            ({result.source.publisher})
          </p>
        ) : (
          <p className="flex items-center gap-2 border-t border-line pt-4 text-sm text-muted">
            <Icon name="user" size={16} />
            Sent to a reviewer for a closer look.
          </p>
        )}
      </div>
    </article>
  );
}
