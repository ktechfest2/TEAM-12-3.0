# T-18 after the revamp

Measured by the same script and the same 120 captures (routes x states x 360, 768, 1440) as `AUDIT.md`. Dashboard data is mocked with invented fixtures; a real reviewer login was not available, so the signed-in dashboard was not checked against real data. Screenshots are in `docs/design/audit/shots/after/` (git ignored).

## Before and after

| Measure | Before | After |
| --- | --- | --- |
| Distinct font sizes | 13 | 8 (12, 14, 16, 18, 20, 24, 32, 44 px) |
| Distinct font weights | 4 | 3 (400, 600, 700) |
| Distinct line heights | 16 | 8 |
| Distinct paddings | 42 | 35 |
| Distinct margins | 33 | 21 |
| Distinct gaps | 13 | 9 |
| Distinct radii | 5 | 4 (10 px, 14 px, full, 50% for dots) |
| Distinct shadows | 2 | 2 (the resting card shadow is now lighter, and 181 elements carried a shadow before against 142 after) |
| Distinct text colours | 9 | 8 |
| Text under 4.5:1 (unique combinations) | 7 | 0 |
| Captures with horizontal overflow | 29 (the 360 px dashboard nav) | 0 |
| Small targets under 40 px (unique) | 25 | 10 before the last fix, see below |
| Console, page and API errors | same | same |

Static checks: no hex or palette class in `apps/web/src` outside `styles.css`; no usage of `paper`, `beacon`, `faint`, `ink`, `line`, `line-strong`, `brand-accent`, `brand-50/100/200/500/600/800/900`, `unknown`, `surface-muted` or `font-display`. One `Card` remains (`components/ui/card.tsx`).

## What changed

- One token per role, defined in `styles.css`; Tailwind's own palette, scale, radii and shadows are reset so only Clarion names compile. Names and the value changes (`muted`, `contradicted`, focus ring, disabled buttons) are in `DECISIONS.md`.
- System font stacks only, one sans family, an 8 step type scale, three weights, a spacing scale of 4 to 64 px.
- `surface.tsx` split into `card`, `page-header`, `section-title`, `pill`, `notice`, `input`; added `Container` and `Select`; `Button` reduced to four variants.
- Both shells share gutters and widths. The reviewer nav on phones is an equal-width icon and label bar instead of a sideways scroller.
- Public pages share one `PageHeader`; eyebrow lines, reassurance boxes and boxes inside boxes were removed. The source citation, the approval line and the fingerprint check are kept.
- Static `logo.svg`, `favicon.svg` and `social-card.svg` now use the forest green mark (they were navy and amber with a serif).
- `DESIGN.md` is updated and marked as the locked spec.

## Remaining known issues

- After the re-shoot, one more pass made the standalone title links on information cards, the source links and the "Watch the broadcast board" link 40 px tall. That last change was checked by lint, typecheck, tests and build, but not re-shot. The two checkbox inputs and the two radio inputs are 20 px; their labels are 44 px, so the touch target is fine, but the measurement script still lists the bare input.
- Padding and margin still show 35 and 21 distinct composite values. They are built from the 8 allowed steps, but they combine per side, so the composite count stays high.
- The resting and lifted shadow are still two distinct values. Each is used for a stated purpose.
- The `/c/:id` page with no matching message logs one console error for the expected 404, and unknown routes log two; there is no catch-all route. Both are the same as before and outside this task.
- The board's delivery stream request shows `net::ERR_ABORTED` at 360 px under the mocked empty stream; cause not traced.
- Real dashboard data and the real login were not exercised. The vitest suite passes (44 tests) and covers the review, board and correction behaviour.
- Voice-note rendering was not captured (it needs rendition API responses).
- No API change was needed.
