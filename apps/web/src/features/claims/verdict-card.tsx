import { type ClaimResult, verdictLabel, verdictTone } from "./verdict";

type Props = { result: ClaimResult };

export function VerdictCard({ result }: Props) {
  return (
    <article
      aria-label="Verdict"
      className={`rounded-lg border-2 p-5 ${verdictTone[result.verdict]}`}
    >
      <h2 className="text-lg font-bold">{verdictLabel[result.verdict]}</h2>
      <p className="mt-2 text-slate-800">{result.text}</p>
      {result.source ? (
        <p className="mt-4 text-sm text-slate-700">
          Source:{" "}
          <a className="underline" href={result.source.url} target="_blank" rel="noreferrer">
            {result.source.document_title}
          </a>{" "}
          ({result.source.publisher})
        </p>
      ) : (
        <p className="mt-4 text-sm text-muted">Sent to a reviewer for a closer look.</p>
      )}
    </article>
  );
}
