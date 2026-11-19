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

Forest green is the primary brand colour. Neutral slate surfaces support readable public information and reviewer tools. Verdict colours are reserved for verdicts and delivery state.

| Token | Hex | Role |
| --- | --- | --- |
| `brand` / `brand-hover` | forest green | Brand, headings, primary buttons |
| `brand-soft` | pale forest green | Selected controls and supporting panels |
| `surface` / `surface-muted` | white / slate-50 | Cards, inputs and quiet fills |
| `foreground` / `secondary` / `muted` | slate tones | Body, secondary and supporting text |
| `border` / `border-strong` | slate borders | Dividers and input borders |
| `confirmed` / `confirmed-soft` | green | Verdict: confirmed, delivery sent |
| `contradicted` / `contradicted-soft` | red | Verdict: contradicted, delivery failed |
| `no-official-statement` | slate | Verdict: no official statement |

Rules
- Never use raw hex or Tailwind palette colours in components. Use tokens.
- Colour is never the only signal. Every verdict and state also carries an icon and words.
- Body text must reach 4.5:1 contrast. `foreground` and `secondary` on `surface` pass. Do not put `muted` on text that carries meaning.
- Brand blue is not a verdict colour. Do not use green or red for brand or navigation.

## Typography

| Role | Token | Stack | Use |
| --- | --- | --- | --- |
| Display | `font-display` | System sans display stack | h1, h2, quoted claims, official passages, big numbers |
| UI and body | `font-sans` | System UI | Everything else |
| Data | `font-mono` | System monospace | Hashes, record text |

System stacks are deliberate: no font download on low bandwidth connections, and full coverage for Yoruba, Igbo and Hausa diacritics. A serif voice for claims and sources says "this is the record"; the sans voice says "this is the tool".

Scale: page title `text-4xl` to `text-5xl` (marketing page) or `text-3xl` to `text-4xl`; section `text-xl`; body `text-base`; lead `text-lg`; labels `text-sm`; eyebrow and section titles `text-xs` uppercase with `tracking-wider`. Body line height 1.6. Use `tabular-nums` for any number that ticks.

## Shape, depth, motion

- Radii: `rounded-control` for inputs and buttons, `rounded-card` for cards, `rounded-full` for pills and badges.
- Depth: `shadow-card` for resting cards, `shadow-lift` for the one thing that matters on the page (verdict, board header). Never stack shadows.
- Motion: colour transitions only, plus the loading spinner. Everything respects `prefers-reduced-motion`.
- Focus: a visible brand-colour outline on every focusable element. Do not remove it.

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

## Components

In `src/components/ui/`: `Button` (primary, secondary, quiet; md and sm), `Card`, `PageHeader`, `SectionTitle`, `Pill`, `Notice` (error, info, empty), `Loading`, and `controlClass` for inputs. Feature code composes these; it does not restyle them.

Verdict display is always `VerdictBadge` plus the `verdictAccent` stripe on cards. Do not hand build a verdict.

## Layout

Page width `max-w-5xl`; public correction `max-w-2xl` so it reads on a phone. Page padding `px-4` on mobile, `px-6` from `sm`. Vertical rhythm in steps of `space-y-6` and `space-y-8`. Reviewer tools show the main nav; the public correction page (`/c/:id`) shows only the logo, because voters should not see reviewer tools.

## Accessibility checklist

- Every control has a visible or `sr-only` label.
- Every page works at 360 px wide and at 200 percent zoom.
- Touch targets at least 40 px (`min-h-10` or `min-h-11`).
- Errors use `role="alert"`; progress and empty states use `role="status"`.
- Skip link first in the document; one `h1` per page.

## Adding to the system

Change a token or add a primitive in one place, update this file, and use it from there. Do not introduce a second palette, a second icon style or a web font without an ADR (a font download changes the performance and data cost promise).
