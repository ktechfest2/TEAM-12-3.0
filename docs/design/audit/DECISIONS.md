# T-18 design decisions

Written by the design pass after reading `AUDIT.md`. This is refinement, not redesign: forest green brand, slate neutrals, existing verdict meaning, calm civic tone. The locked result is in `docs/DESIGN.md`. Each line below gives the choice and one reason.

## Colour tokens: one name per role

| Role | Kept | Removed | Reason |
| --- | --- | --- | --- |
| Page background (slate 50) | `canvas` | old `surface` meaning | `surface` meant slate in code but white in the docs. Now `surface` is white everywhere |
| Card, input, header (white) | `surface` | `paper`, raw `bg-white` | One name for white; `bg-white` was raw colour in components |
| Quiet fill (slate 100) | `sunken` | `surface-muted` | Same value, two names |
| Body text | `foreground` | `ink` | Same value |
| Supporting text | `secondary`, `muted` | `faint` | `faint` equalled `muted` |
| Border | `border` | `line` | Same value |
| Strong border | `border-strong` | `line-strong` | Same value |
| Brand pale fill | `brand-soft` (`#dcfce7`) | `brand-100`, `beacon-soft` | Same value |
| Brand faint tint | `brand-tint` (`#f0fdf4`) | `brand-50` | Clearer role name |
| Brand hairline | `brand-line` (`#bbf7d0`) | `brand-200` | Clearer role name |
| Brand text on white | `brand` | `beacon-ink`, `brand-800`, `brand-900` | Same value or unused |
| Accent green (`#22a06b`) | none | `brand-accent`, `brand-500`, `beacon` | A third green that failed contrast on the brand panel (2.74:1). Its jobs now use `brand` (stripe) or `brand-line` (label on brand) |
| Hover green | `brand-hover` | `brand-600` | Same value, unused name |
| White on brand | `on-brand` | `text-white`, `text-paper` | Named role instead of raw white |
| Verdict: no statement | `no-official-statement` (+ `-soft`) | `unknown` | The verdict value is `no_official_statement`; colour name now matches it |

The Tailwind default palette, type scale, radii and shadows are reset in `@theme`, so a palette class such as `slate-500` no longer compiles to anything. That keeps the "tokens only" rule enforced by the build rather than by review.

## Colour value changes (all small, contrast driven)

| Token | Before | After | Reason |
| --- | --- | --- | --- |
| `muted` | `#64748b` | `#586579` | 4.34:1 on `sunken` and 4.33:1 on `brand-soft` failed. Now 5.4:1 on both, 5.65:1 on `canvas` |
| `contradicted` | `#dc2626` | `#b91c1c` | Red on `contradicted-soft` was 3.95:1 (the verdict badge). Now 5.3:1 |
| Focus ring | brand-accent at 35% | `brand`, 3 px | The old ring was faint on white. Same hue, stronger |
| Disabled primary button | white at 50% opacity on brand (3.55:1) | `muted` on `sunken` with `border` | Disabled text is now readable and states "disabled" without opacity tricks |

No new hue. `confirmed`, `confirmed-soft`, `contradicted-soft`, `brand`, `brand-hover`, `secondary`, `foreground`, `border`, `border-strong` are unchanged.

## Typography (system stacks only, no web font)

| Role | Choice | Reason |
| --- | --- | --- |
| UI, display and body | `font-sans`: `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif` | The old stack named `Inter`, which is never downloaded, so each device rendered something different. Removing the name makes the render predictable and keeps the no-font-download promise |
| Data | `font-mono`: `ui-monospace, SFMono-Regular, Menlo, Consolas, ...` | Hashes and record text |
| Serif voice | dropped | The code never used it; `DESIGN.md` is corrected. One family reads as one product |
| `font-display` token | removed | It equalled `font-sans` |
| Scale | 12, 14, 16, 18, 20, 24, 32, 44 px (`xs` to `4xl`) with line heights 16, 20, 24, 28, 28, 32, 40, 48 | Before: 13 distinct sizes including 34, 36, 40, 44, 48 and 60 px from arbitrary values. Eight steps cover every use |
| Weights | 400, 600, 700 | Before: 400, 500, 600, 700. 500 was visually indistinguishable from 600 at these sizes |
| Page title | `3xl`, from `md` `4xl`, bold | One rule for all public pages instead of five hand-set variants |
| Eyebrow, section label | `xs`, bold, uppercase, `tracking-wider` | Replaces `tracking-[0.16em]` and `tracking-tight` variants |

## Spacing, shape, depth, width

| Item | Choice | Reason |
| --- | --- | --- |
| Spacing steps | 4, 8, 12, 16, 24, 32, 48, 64 px (`1, 2, 3, 4, 6, 8, 12, 16`), plus `0.5` for 2 px icon nudges | Before: 42 distinct padding and 33 margin values. Steps `1.5, 2.5, 3.5, 5, 7, 10, 14, 20` are mapped to the nearest step |
| Page gutters | 16 px, 24 px from `sm`, 32 px from `lg`, same in both shells | Public used 20/32, guide 16/24, dashboard 16/24/40 |
| Section rhythm | `py-12`, `md:py-16` | One vertical rhythm for marketing sections |
| Radii | `control` 10 px, `card` 14 px, `full` | Before also `rounded-md` (6 px) and arbitrary values |
| Shadows | `card` (1 px hairline lift), `lift` for the one key element | Before: `card` was an 8 px blur that competed with borders. Cards already have a border, so the shadow is now barely there |
| Widths | `page` 1200 px, `workspace` 1120 px, `3xl` prose 768 px, in `Container` | Replaces five arbitrary `max-w-[...]` values |

## Primitives

| Item | Choice | Reason |
| --- | --- | --- |
| `Card` | One, `components/ui/card.tsx`, `elevation` prop (`rest` or `lift`) | Was defined twice with different padding, surface and radius |
| `surface.tsx` | Split into `page-header`, `section-title`, `pill`, `notice`, `input`, `card` | `DESIGN.md` can now name a file per primitive |
| `Container` | New, `components/ui/container.tsx` | Gutters and widths were repeated per page |
| `Select` | New, in `input.tsx` | Selects were hand-styled in three pages |
| `Button` variants | `primary`, `secondary`, `outline`, `quiet` | `ghost` merged into `quiet`, `destructive` was never used |
| `Skeleton`, `StatCard` | Use the shared radius and `Card` | Had their own radius and shadow |

## Clutter cuts

| Cut | Reason |
| --- | --- |
| Eyebrow line above every public page title | Repeated the title; the nav already says where you are |
| Reassurance panels repeated under forms | Folded into one line under the form where they carry a promise (approval, source, privacy) |
| Boxes inside boxes on the verification screen | One card per task, hairline dividers between sections |
| Second shadow on cards inside the lifted verdict card | One shadow level per view |
| `font-display` and `tracking-tight` on titles | Titles use the one scale |

The official source citation, the approval line and the fingerprint check are kept and not shortened.

## Not done here

- No API change was needed.
- Static brand files `apps/web/public/logo.svg`, `favicon.svg` and `social-card.svg` still used a navy and amber palette that the app mark does not use; they are brought to the forest green mark. See `AFTER.md`.
