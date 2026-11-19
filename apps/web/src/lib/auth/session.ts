import { useSyncExternalStore } from "react";

const STORAGE_KEY = "clarion.reviewer-session";

export type ReviewerSession = { token: string; reviewerName: string };

const listeners = new Set<() => void>();
let cached: { raw: string | null; value: ReviewerSession | null } | null = null;

function read(): ReviewerSession | null {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (cached && cached.raw === raw) return cached.value;
  let value: ReviewerSession | null = null;
  if (raw) {
    try {
      const parsed = JSON.parse(raw) as Partial<ReviewerSession>;
      if (typeof parsed.token === "string" && typeof parsed.reviewerName === "string") {
        value = { token: parsed.token, reviewerName: parsed.reviewerName };
      }
    } catch {
      value = null;
    }
  }
  cached = { raw, value };
  return value;
}

function notify() {
  for (const listener of listeners) listener();
}

/** Reviewer tokens live only for the browser tab (sessionStorage), never in a cookie or URL. */
export function getSession(): ReviewerSession | null {
  return read();
}

export function saveSession(session: ReviewerSession): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  notify();
}

export function clearSession(): void {
  sessionStorage.removeItem(STORAGE_KEY);
  notify();
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useSession(): ReviewerSession | null {
  return useSyncExternalStore(subscribe, getSession, () => null);
}
