import type { components } from "../../lib/api/schema.gen";

export type Language = components["schemas"]["Language"];
export type Mode = components["schemas"]["DeliveryMode"];
export type Frequency = components["schemas"]["DigestFrequency"];

export const LANGUAGE_OPTIONS: ReadonlyArray<{ value: Language; label: string }> = [
  { value: "en", label: "English" },
  { value: "yo", label: "Yoruba" },
  { value: "ha", label: "Hausa" },
  { value: "ig", label: "Igbo" },
  { value: "pcm", label: "Nigerian Pidgin" },
];

export const FREQUENCY_OPTIONS: ReadonlyArray<{ value: Frequency; label: string }> = [
  { value: "hourly", label: "Every hour" },
  { value: "daily", label: "Once a day" },
  { value: "weekly", label: "Once a week" },
];

export const MAX_PER_DAY_LIMIT = 10;
export const DEFAULT_MAX_PER_DAY = 3;

/** Keep the order the person picked: the first language is the one we try first. */
export function toggleLanguage(selected: Language[], language: Language): Language[] {
  return selected.includes(language)
    ? selected.filter((item) => item !== language)
    : [...selected, language];
}

export function clampMaxPerDay(raw: number): number {
  if (!Number.isFinite(raw)) return DEFAULT_MAX_PER_DAY;
  return Math.min(MAX_PER_DAY_LIMIT, Math.max(1, Math.round(raw)));
}

/** One sentence that says what the person will get, shown before they ask for a code. */
export function describeChoice(input: {
  mode: Mode;
  frequency: Frequency;
  maxPerDay: number;
}): string {
  const cap = `${input.maxPerDay} ${input.maxPerDay === 1 ? "text" : "texts"} a day at most`;
  if (input.mode === "instant") {
    return `Each approved correction as soon as it goes out, ${cap}. Anything over that waits for the next day.`;
  }
  const when = { hourly: "every hour", daily: "once a day", weekly: "once a week" }[
    input.frequency
  ];
  return `A single text ${when} that bundles new corrections, ${cap}.`;
}

/** The API answers errors as { detail: string } (or a list for form validation). */
export function errorMessage(error: unknown, fallback: string): string {
  if (error && typeof error === "object" && "detail" in error) {
    const detail = (error as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
  }
  return fallback;
}
