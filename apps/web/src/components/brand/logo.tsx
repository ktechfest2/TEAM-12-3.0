type MarkProps = { size?: number; className?: string };

/** The Clarion mark: a "C" that is open on the right, with a beacon where the correction lands. */
export function LogoMark({ size = 32, className }: MarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      aria-hidden="true"
      focusable="false"
      className={className}
    >
      <rect width="32" height="32" rx="8" fill="var(--color-brand)" />
      <path
        d="M22.36 9.64A9 9 0 1 0 22.36 22.36"
        fill="none"
        stroke="var(--color-paper)"
        strokeWidth="3.5"
        strokeLinecap="round"
      />
      <circle cx="23.5" cy="16" r="2.6" fill="var(--color-beacon)" />
    </svg>
  );
}

/** Mark plus wordmark. The wordmark is real text so it scales and is read aloud. */
export function Logo({ size = 32 }: { size?: number }) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <LogoMark size={size} />
      <span className="font-display text-xl font-bold tracking-tight text-brand">Clarion</span>
    </span>
  );
}
