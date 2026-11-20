# Clarion design system

How Clarion looks, sounds and behaves. Tokens live in `apps/web/src/styles.css`. If this file and the code disagree, fix whichever is wrong in the same change.

## Identity

**Idea.** A clarion is a clear, carrying call. Clarion closes the gap between a rumour and its correction, so the product should feel like a calm, trusted voice: official without being cold, fast without being loud.

**Personality.** Civic, plain, assured. Think a well run newsroom or a good public notice, not a startup dashboard and not a political campaign.

**Voice.** Plain English, short sentences, no jargon, no opinion words. Verdict labels are fixed in `features/claims/verdict.ts` and never reworded. Say what we know and where it came from.

**Two promises the design must show.** Every correction cites an official source. A person approved it. If a screen hides either, it is wrong.

## Logo

The Clarion mark is a clear, civic wordmark used with the forest-green brand colour.

| Asset | File | Use |
| --- | --- | --- |
| Mark and wordmark (React) | `src/components/brand/logo.tsx` | In app chrome. Uses tokens, so it follows the theme |
| Favicon | `apps/web/public/favicon.svg` | Browser tab |
| Static lockup | `apps/web/public/logo.svg` | Docs, slides, README |
| Social card | `apps/web/public/social-card.svg` | Link previews |

Rules: keep clear space around the mark, preserve its proportions, and use the provided logo assets rather than recreating the wordmark.

## Colour

**Locked specification.** Change a value or a name only by editing this table and `apps/web/src/styles.css` in the same commit. The Tailwind default palette is reset in `@theme`, so only these names exist. Decisions and reasons: `docs/design/audit/DECISIONS.md`.

Forest green is the primary brand colour. Neutral slate surfaces support readable public information and reviewer tools. Verdict colours are reserved for verdicts and delivery state.

| Token | Value | Role |
| --- | --- | --- |
| `brand` | `#14532d` | Brand, headings, primary buttons, focus ring |
| `brand-hover` | `#166534` | Primary button hover |
| `brand-soft` | `#dcfce7` | Selected controls, step numbers, soft buttons |
| `brand-tint` | `#f0fdf4` | Supporting panels (integrity check, send step) |
| `brand-line` | `#bbf7d0` | Hairline on brand panels, label on a `brand` background |
| `on-brand` | `#ffffff` | Text on `brand` |
| `canvas` | `#f8fafc` | Page background, quiet fills, hover |
| `surface` | `#ffffff` | Cards, inputs, headers |
| `sunken` | `#f1f5f9` | Pills, skeletons, pressed fills |
| `foreground` | `#0f172a` | Body text and titles |
| `secondary` | `#475569` | Supporting text that carries meaning |
| `muted` | `#586579` | Metadata: dates, counts, placeholders (5.4:1 on `sunken`) |
| `border` | `#e2e8f0` | Dividers and card borders |
| `border-strong` | `#cbd5e1` | Input borders, dashed empty states |
| `confirmed` / `confirmed-soft` | `#15803d` / `#dcfce7` | Verdict: confirmed, delivery sent |
| `contradicted` / `contradicted-soft` | `#b91c1c` / `#fee2e2` | Verdict: contradicted, delivery failed, errors |
| `no-official-statement` / `-soft` | `#475569` / `#f1f5f9` | Verdict: no official statement |

Rules
- Never use raw hex or Tailwind palette colours in components. Use tokens.
- Colour is never the only signal. Every verdict and state also carries an icon and words.
- Body text must reach 4.5:1 contrast. `foreground`, `secondary` and `muted` pass on `surface`, `canvas`, `sunken` and `brand-soft`. Do not use `muted` for text a person must read to act.
- Green and red are verdict colours. Brand green is used for brand and navigation; never use `confirmed` or `contradicted` for either.
- There is no `misleading` colour: the verdict has exactly three values.

## Typography

**Locked specification.** System stacks only: no font download on low bandwidth connections, and full coverage for Yoruba, Igbo and Hausa diacritics. A web font needs an ADR.

| Role | Token | Stack |
| --- | --- | --- |
| UI, display and body | `font-sans` | `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif` |
| Data | `font-mono` | `ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace` |

One family for everything reads as one product. Claims and official passages are set in the same sans, larger and with the green rule, not in a serif.

| Step | Size / line height | Use |
| --- | --- | --- |
| `text-xs` | 12 / 16 | Metadata, section labels (uppercase, `tracking-wider`), table heads |
| `text-sm` | 14 / 20 | Labels, helper text, buttons, nav, card body |
| `text-base` | 16 / 24 | Body, form fields |
| `text-lg` | 18 / 28 | Lead paragraph, card title, quoted official passage |
| `text-xl` | 20 / 28 | Section title in a card, verdict answer |
| `text-2xl` | 24 / 32 | Page section title, claim quoted on a correction, big stat |
| `text-3xl` | 32 / 40 | Page title (mobile), board elapsed time (mobile) |
| `text-4xl` | 44 / 48 | Page title and hero from `md`, board elapsed time from `sm` |

Weights: 400 body, 600 labels, buttons and nav, 700 titles. No 500. Use `tabular-nums` for any number that ticks. No arbitrary `text-[..]` sizes.

## Spacing, shape, depth, width, motion

**Locked specification.**

| Item | Values |
| --- | --- |
| Spacing | 4, 8, 12, 16, 24, 32, 48, 64 px (`1, 2, 3, 4, 6, 8, 12, 16`). `0.5` (2 px) only to nudge an icon. No other steps |
| Page gutters | 16 px, 24 px from `sm`, 32 px from `lg` (`Container`) |
| Section rhythm | `py-12`, `md:py-16` on public pages; `py-6`, `lg:py-8` in the reviewer shell |
| Card padding | 16 px, 24 px from `sm` |
| Widths | `max-w-page` 1200 px (listings, marketing), `max-w-3xl` 768 px (forms and reading), `max-w-workspace` 1120 px (reviewer pages) |
| Radii | `rounded-control` 10 px (inputs, buttons), `rounded-card` 14 px (cards), `rounded-full` (pills, badges) |
| Shadows | `shadow-card` for resting cards, `shadow-lift` for the one thing that matters on the page (correction header, board header). Tinted panels and cards inside cards are flat. Never stack shadows |
| Targets | At least 40 px (`min-h-10` or `min-h-11`) |
| Motion | Colour transitions and the loading spinner only. `prefers-reduced-motion` turns both off |
| Focus | A 3 px `brand` outline on every focusable element. Do not remove it |

## Iconography

`src/components/icons.tsx`. 24 px grid, 1.75 px round stroke, `currentColor`. Drawn for this product; no icon library. Decorative by default (`aria-hidden`); pass `label` only when an icon stands alone. Add a new icon there, keep the stroke style, and use it by name: `<Icon name="shieldCheck" />`.

| Meaning | Icon |
| --- | --- |
| Confirmed / approved / sent | `checkCircle` |
| Contradicted / failed | `xCircle` |
| No official statement | `searchOff` |
| Official source, human approved | `shieldCheck` |
| Integrity fingerprint | `fingerprint` |
| Sealed | `lock` |
| Send, broadcast | `send`, `broadcast` |
| Translation | `language` |
| Waiting | `wait`, `clock` |
| Navigation and pages | `dashboard`, `messages`, `workflow`, `archive`, `book`, `building`, `calendar`, `share`, `menu`, `close`, `arrowLeft`, `arrowRight`, `external` |

## Components

All in `apps/web/src/components/ui/`, one file each. Feature code composes these; it does not restyle them.

| Primitive | File | Use |
| --- | --- | --- |
| `Button` | `button.tsx` | `primary` (the one main action), `secondary` (soft green), `outline`, `quiet` (text only); `md` 44 px and `sm` 40 px. Renders a link with `as="link"` |
| `Card` | `card.tsx` | The only card. `elevation`: `rest`, `lift` (the key element) or `flat` (tinted panel, nested card); `padding="none"` for edge to edge rows and tables |
| `Container` | `container.tsx` | Page gutters and width: `page`, `prose`, `workspace` |
| `PageHeader`, `PageTitle` | `page-header.tsx` | Public pages: one `h1` and an optional lead. Reviewer pages: a screen-reader-only `h1`, no visible title |
| `SectionTitle` | `section-title.tsx` | Small uppercase label above a block; `as="h2"` when it heads a page section |
| `Pill` | `pill.tsx` | Stage and status words. Tones: neutral, good, bad, attention |
| `Notice`, `Loading` | `notice.tsx` | `error` (`role="alert"`), `info` and `empty` (`role="status"`); loading spinner with words |
| `Input`, `Select`, `controlClass` | `input.tsx` | Single-line controls, 44 px tall |
| `Textarea` | `textarea.tsx` | Multi-line control |
| `Skeleton`, `StatCard` | `skeleton.tsx`, `stat-card.tsx` | Loading block; count tile built on `Card` |

Every form control has a `label` with `htmlFor`, or a screen-reader-only one.

Verdict display is always `VerdictBadge` plus the `verdictAccent` stripe on cards. Do not hand build a verdict.

## Layout and routes

Two shells. The public shell (`PublicLayout`) holds `/` (homepage with the claim check), `/check`, `/guide` (how Clarion works), `/information`, `/fact-checks` and the public correction page `/c/:id`. The reviewer shell (`DashboardLayout`, under `/dashboard`) holds the overview, claims table, `verification` (review, per-language approval, seal, send), `evidence` and `board`. Old `/review` and `/board` redirect. Once a message is sealed, the Send step shows a voice notes panel: the reviewer prepares the audio, listens to each language, and can open the social card and poster before sending. On the public correction page every approved language, and English, has a Listen button; nothing is downloaded until it is pressed, and a failure says plainly that audio is not available right now (ADR 0009). The public header always links to the reviewer workspace, and the claim check, the approval rule and the fingerprint check are all visible on the page, never behind a tab. On phones the reviewer shell shows its five sections as an equal-width bar of icon over label, so it never scrolls sideways; from `lg` it is a left sidebar.

The fact-check and information pages currently show demonstration content and say so on the page. They must not be presented as real verdicts until they are fed from sealed corrections and the official source registry.

## Accessibility checklist

- Every control has a visible or `sr-only` label.
- Every page works at 360 px wide and at 200 percent zoom.
- Touch targets at least 40 px (`min-h-10` or `min-h-11`).
- Errors use `role="alert"`; progress and empty states use `role="status"`.
- Skip link first in the document; one `h1` per page.

## Adding to the system

Change a token or add a primitive in one place, update this file, and use it from there. Do not introduce a second palette, a second icon style or a web font without an ADR (a font download changes the performance and data cost promise).
