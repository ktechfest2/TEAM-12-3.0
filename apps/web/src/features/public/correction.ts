import { api } from "../../lib/api/client";
import type { components } from "../../lib/api/schema.gen";
import { env } from "../../lib/env";

export type PublicCorrection = components["schemas"]["PublicCorrectionOut"];
type Language = components["schemas"]["Language"];

/** The audio for one approved language. The server makes it the first time and reuses it after. */
export function voiceNoteUrl(messageId: string, language: Language): string {
  return `${env.apiBaseUrl}/public/corrections/${messageId}/voice/${language}`;
}

export class CorrectionNotFoundError extends Error {}

export async function fetchCorrection(messageId: string): Promise<PublicCorrection> {
  const { data, response } = await api.GET("/public/corrections/{message_id}", {
    params: { path: { message_id: messageId } },
  });
  if (response.status === 404) {
    throw new CorrectionNotFoundError("We could not find a published correction with this link.");
  }
  if (!data) throw new Error("This page could not load. Check your connection and try again.");
  return data;
}

const dateFormat = new Intl.DateTimeFormat("en-NG", {
  dateStyle: "long",
  timeStyle: "short",
  timeZone: "Africa/Lagos",
});

/** Dates are shown in Nigerian time so people read the same hour the reviewer approved it. */
export function formatWhen(iso: string): string {
  return `${dateFormat.format(new Date(iso))} (WAT)`;
}
