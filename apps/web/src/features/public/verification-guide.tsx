import type { PublicCorrection } from "./correction";

type Props = { correction: PublicCorrection };

export function VerificationGuide({ correction }: Props) {
  return (
    <section aria-label="Integrity" className="space-y-3 rounded-lg border border-slate-200 p-4">
      <h2 className="font-bold">Check that this was not changed</h2>
      <p className="text-sm text-slate-700">
        This correction has a fingerprint. If anyone changed even one letter after a reviewer
        approved it, the fingerprint would be different.
      </p>
      <dl className="space-y-1 text-sm">
        <dt className="font-semibold">Fingerprint ({correction.hash_algorithm})</dt>
        <dd className="break-all font-mono">{correction.integrity_hash}</dd>
        <dt className="font-semibold">Previous correction's fingerprint</dt>
        <dd className="break-all font-mono">
          {correction.previous_hash ?? "none (this was the first)"}
        </dd>
      </dl>
      <p className="text-sm">
        {correction.integrity_verified
          ? "Our server checked this record against its fingerprint: it matches."
          : "Our server checked this record against its fingerprint: it does not match."}
      </p>
      <details className="text-sm">
        <summary className="cursor-pointer font-semibold">How to check it yourself</summary>
        <ol className="mt-2 list-decimal space-y-1 pl-5">
          <li>Copy the record text below exactly, with no extra spaces or lines.</li>
          <li>
            Run it through SHA-256, for example <code>printf '%s' "..." | sha256sum</code> on a
            computer, or any SHA-256 tool you trust.
          </li>
          <li>Put sha256: in front of the result. It should equal the fingerprint above.</li>
        </ol>
        <figure aria-label="Record text" className="mt-2">
          <pre className="max-h-48 overflow-auto whitespace-pre-wrap break-all rounded-md bg-slate-50 p-2 font-mono text-xs">
            {correction.canonical_json}
          </pre>
        </figure>
      </details>
    </section>
  );
}
