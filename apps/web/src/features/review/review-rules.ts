import type { components } from "../../lib/api/schema.gen";

export type Message = components["schemas"]["MessageOut"];
export type Language = Message["claim_language"];
export type Localisation = Message["localisations"][number];
export type Rendition = components["schemas"]["RenditionOut"];

/** Every language a correction must reach before it can be approved. English is the master text. */
export const TARGET_LANGUAGES = ["yo", "ha", "ig", "pcm"] as const satisfies readonly Language[];

export const languageName: Record<Language, string> = {
  en: "English",
  yo: "Yoruba",
  ha: "Hausa",
  ig: "Igbo",
  pcm: "Pidgin",
};

export function localisationFor(message: Message, language: Language): Localisation | undefined {
  return message.localisations.find((loc) => loc.language === language);
}

export function missingApprovals(message: Message): Language[] {
  return TARGET_LANGUAGES.filter((language) => !localisationFor(message, language)?.is_approved);
}

/** A cited verdict needs its official passage; the reviewer cannot approve one without it. */
export function hasRequiredSource(message: Message): boolean {
  return message.verdict === "no_official_statement" || message.source !== null;
}

export function canApprove(message: Message): boolean {
  return missingApprovals(message).length === 0 && hasRequiredSource(message);
}

export type Stage = "draft" | "approved" | "rejected" | "escalated" | "sealed";

export function stageOf(message: Message): Stage {
  if (message.integrity_hash) return "sealed";
  switch (message.review?.status) {
    case "approved":
      return "approved";
    case "rejected":
      return "rejected";
    case "escalated":
      return "escalated";
    default:
      return "draft";
  }
}

export const stageLabel: Record<Stage, string> = {
  draft: "Needs review",
  approved: "Approved, not sealed",
  rejected: "Rejected",
  escalated: "Escalated",
  sealed: "Sealed",
};
