import type { ReactNode } from "react";

/**
 * Clarion icon set: 24 px grid, 1.75 px round stroke, drawn in currentColor.
 * Icons are decorative by default; pass `label` when an icon stands alone.
 */
const paths = {
  check: <path d="m5 12.5 4.5 4.5L19 7.5" />,
  shieldCheck: (
    <>
      <path d="M12 3 5 6v5.5c0 4.2 2.8 7.6 7 9.5 4.2-1.9 7-5.3 7-9.5V6l-7-3Z" />
      <path d="m9 12 2.2 2.2L15.2 10" />
    </>
  ),
  xCircle: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m9 9 6 6M15 9l-6 6" />
    </>
  ),
  checkCircle: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m8.5 12.3 2.4 2.4 4.6-5" />
    </>
  ),
  searchOff: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 4.5 4.5M8.5 11h5" />
    </>
  ),
  send: <path d="M21 3 10 14M21 3l-7 18-4-7-7-4 18-7Z" />,
  broadcast: (
    <>
      <circle cx="12" cy="12" r="1.8" />
      <path d="M8.2 8.2a5.4 5.4 0 0 0 0 7.6M15.8 8.2a5.4 5.4 0 0 1 0 7.6M5.4 5.4a9.4 9.4 0 0 0 0 13.2M18.6 5.4a9.4 9.4 0 0 1 0 13.2" />
    </>
  ),
  inbox: (
    <>
      <path d="M3.5 13.5 6 5.5h12l2.5 8" />
      <path d="M3.5 13.5V18a1.5 1.5 0 0 0 1.5 1.5h14a1.5 1.5 0 0 0 1.5-1.5v-4.5H15a3 3 0 0 1-6 0H3.5Z" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 4.5 4.5" />
    </>
  ),
  language: (
    <>
      <path d="M4 6h9M8.5 4v2M6 6c.5 3 2.8 5.5 6 7M12 6c-.5 3-3 5.5-7 7" />
      <path d="m12.5 20 4-9 4 9M13.9 17h5.2" />
    </>
  ),
  arrowRight: <path d="M5 12h14m-5.5-5.5L19 12l-5.5 5.5" />,
  external: (
    <path d="M14 4h6v6M20 4l-9 9M18 14v4.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10" />
  ),
  lock: (
    <>
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V8a4 4 0 0 1 8 0v3" />
    </>
  ),
  fingerprint: (
    <>
      <path d="M6 10a6 6 0 0 1 12 0M9 20c-.8-1.6-1-3-1-5a4 4 0 0 1 8 0c0 1.3.2 2.2.6 3.2M12 12v3c0 2 .5 3.5 1.5 5" />
      <path d="M4.5 13.5c0-.5 0-1 .1-1.5M19.5 13c0 2.5-.5 4.5-1.5 6.5" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  alert: (
    <>
      <path d="M12 4 2.8 19.5h18.4L12 4Z" />
      <path d="M12 10v4.5M12 17.2v.1" />
    </>
  ),
  user: (
    <>
      <circle cx="12" cy="8.5" r="3.5" />
      <path d="M5 20c.6-3.6 3.4-5.5 7-5.5s6.4 1.9 7 5.5" />
    </>
  ),
  logout: <path d="M10 4H6.5A1.5 1.5 0 0 0 5 5.5v13A1.5 1.5 0 0 0 6.5 20H10m4-12 4 4-4 4m4-4H9" />,
  undo: <path d="M9 7 4.5 11.5 9 16M5 11.5h9a5 5 0 0 1 0 10h-2" />,
  wait: (
    <>
      <circle cx="6" cy="12" r="1.2" />
      <circle cx="12" cy="12" r="1.2" />
      <circle cx="18" cy="12" r="1.2" />
    </>
  ),
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
  close: <path d="m6 6 12 12M18 6 6 18" />,
  arrowLeft: <path d="M19 12H5m5.5-5.5L5 12l5.5 5.5" />,
  building: (
    <>
      <path d="M5 20V5.5A1.5 1.5 0 0 1 6.5 4h7A1.5 1.5 0 0 1 15 5.5V20M15 10h3.5a1.5 1.5 0 0 1 1.5 1.5V20M3.5 20h17" />
      <path d="M8.5 8h3M8.5 12h3M8.5 16h3" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5.5" width="16" height="14.5" rx="2" />
      <path d="M4 10h16M8 3.5v4M16 3.5v4" />
    </>
  ),
  share: (
    <>
      <circle cx="6" cy="12" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <circle cx="18" cy="18" r="2.5" />
      <path d="m8.2 10.8 7.6-3.6M8.2 13.2l7.6 3.6" />
    </>
  ),
  book: (
    <path d="M12 6.5C10.5 5 8 4.5 4.5 4.5v13c3.5 0 6 .5 7.5 2 1.5-1.5 4-2 7.5-2v-13c-3.5 0-6 .5-7.5 2ZM12 6.5v13" />
  ),
  archive: (
    <>
      <rect x="3.5" y="4.5" width="17" height="4" rx="1" />
      <path d="M5 8.5V18a1.5 1.5 0 0 0 1.5 1.5h11A1.5 1.5 0 0 0 19 18V8.5M10 12.5h4" />
    </>
  ),
  dashboard: (
    <>
      <rect x="4" y="4" width="7" height="8" rx="1.5" />
      <rect x="13" y="4" width="7" height="5" rx="1.5" />
      <rect x="13" y="11" width="7" height="9" rx="1.5" />
      <rect x="4" y="14" width="7" height="6" rx="1.5" />
    </>
  ),
  messages: (
    <path d="M5 5h14a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 19 17h-7l-4.5 3.5V17H5a1.5 1.5 0 0 1-1.5-1.5v-9A1.5 1.5 0 0 1 5 5ZM8 9.5h8M8 13h5" />
  ),
  workflow: (
    <>
      <rect x="3.5" y="4" width="6" height="6" rx="1.5" />
      <rect x="14.5" y="14" width="6" height="6" rx="1.5" />
      <path d="M6.5 10v4a2 2 0 0 0 2 2h6" />
    </>
  ),
  volume: (
    <>
      <path d="M4 9.5v5h3.5l4.5 4v-13l-4.5 4H4Z" />
      <path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a8 8 0 0 1 0 11" />
    </>
  ),
  download: <path d="M12 4v11m-4.5-4.5L12 15l4.5-4.5M5 19.5h14" />,
} satisfies Record<string, ReactNode>;

export type IconName = keyof typeof paths;

type Props = { name: IconName; size?: number; className?: string; label?: string };

export function Icon({ name, size = 20, className, label }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`shrink-0 ${className ?? ""}`}
      role={label ? "img" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      focusable="false"
    >
      {paths[name]}
    </svg>
  );
}
