import { api } from "../../lib/api/client";
import type { Language, Message, Rendition } from "./review-rules";

const FAILED = "Something went wrong. Check your connection and try again.";

type Result<T> = { data?: T; error?: unknown; response: Response };

async function unwrap<T>(call: Promise<Result<T>>, fallback = FAILED): Promise<T> {
  const { data, error, response } = await call;
  if (response.status === 401) throw new Error("Your session ended. Sign in again.");
  if (error || data === undefined) {
    const detail = (error as { detail?: unknown } | undefined)?.detail;
    throw new Error(typeof detail === "string" ? detail : fallback);
  }
  return data;
}

export function listMessages(): Promise<Message[]> {
  return unwrap(api.GET("/messages", { params: { query: { limit: 50 } } }));
}

export function getMessage(id: string): Promise<Message> {
  return unwrap(api.GET("/messages/{message_id}", { params: { path: { message_id: id } } }));
}

export function addReview(
  id: string,
  body: {
    status: "pending" | "approved" | "rejected" | "escalated";
    note?: string;
    summary?: string;
  },
): Promise<Message> {
  return unwrap(
    api.POST("/messages/{message_id}/reviews", { params: { path: { message_id: id } }, body }),
  );
}

export function draftTranslation(id: string, language: Language, text?: string): Promise<Message> {
  return unwrap(
    api.PUT("/messages/{message_id}/localisations", {
      params: { path: { message_id: id } },
      body: text === undefined ? { language } : { language, text },
    }),
  );
}

export function approveTranslation(id: string, language: Language): Promise<Message> {
  return unwrap(
    api.POST("/messages/{message_id}/localisations/{language}/approval", {
      params: { path: { message_id: id, language } },
    }),
  );
}

export function sealMessage(id: string): Promise<Message> {
  return unwrap(api.POST("/messages/{message_id}/seal", { params: { path: { message_id: id } } }));
}

/** Speaks every approved language and makes the card and poster. Needs a sealed message. */
export function renderRenditions(id: string): Promise<Rendition[]> {
  return unwrap(
    api.POST("/messages/{message_id}/renditions", {
      params: { path: { message_id: id } },
      body: {},
    }),
  );
}

export function broadcastMessage(id: string): Promise<void> {
  return unwrap(
    api.POST("/messages/{message_id}/broadcast", {
      params: { path: { message_id: id } },
      body: {},
    }),
  ).then(() => undefined);
}
