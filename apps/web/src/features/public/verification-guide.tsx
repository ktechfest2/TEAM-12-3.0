import { Icon } from "../../components/icons";
import type { PublicCorrection } from "./correction";

type Props = { correction: PublicCorrection };

export function VerificationGuide({ correction }: Props) {
  return (
    <section
      aria-label="Integrity"
      className="space-y-4 rounded-card border border-brand-line bg-brand-tint p-6 sm:p-6"
    >
      <h2 className="flex items-center gap-2 text-xl font-bold text-brand">
        <Icon name="fingerprint" size={22} />
        Check that this was not changed
      </h2>
      <p className="text-sm text-muted">
        This correction has a fingerprint. If anyone changed even one letter after a reviewer
        approved it, the fingerprint would be different.
      </p>
      <dl className="space-y-3 text-sm">
        <div>
          <dt className="font-semibold">Fingerprint ({correction.hash_algorithm})</dt>
          <dd className="mt-1 break-all rounded-control bg-canvas p-2 font-mono text-xs">
            {correction.integrity_hash}
          </dd>
        </div>
        <div>
          <dt className="font-semibold">Previous correction's fingerprint</dt>
          <dd className="mt-1 break-all rounded-control bg-canvas p-2 font-mono text-xs">
            {correction.previous_hash ?? "none (this was the first)"}
          </dd>
        </div>
      </dl>
      <p
        className={`flex items-center gap-2 text-sm font-semibold ${
          correction.integrity_verified ? "text-confirmed" : "text-contradicted"
        }`}
      >
        <Icon name={correction.integrity_verified ? "checkCircle" : "xCircle"} size={18} />
        {correction.integrity_verified
          ? "Our server checked this record against its fingerprint: it matches."
          : "Our server checked this record against its fingerprint: it does not match."}
      </p>
      <details className="text-sm">
        <summary className="cursor-pointer font-semibold text-brand">
          How to check it yourself
        </summary>
        <ol className="mt-2 list-decimal space-y-1 pl-6">
          <li>Copy the record text below exactly, with no extra spaces or lines.</li>
          <li>
            Run it through SHA-256, for example <code>printf '%s' "..." | sha256sum</code> on a
            computer, or any SHA-256 tool you trust.
          </li>
          <li>Put sha256: in front of the result. It should equal the fingerprint above.</li>
        </ol>
        <figure aria-label="Record text" className="mt-3">
          <pre className="max-h-48 overflow-auto whitespace-pre-wrap break-all rounded-control bg-canvas p-3 font-mono text-xs">
            {correction.canonical_json}
          </pre>
        </figure>
      </details>
    </section>
  );
}
