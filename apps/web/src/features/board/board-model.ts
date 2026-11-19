import type { components } from "../../lib/api/schema.gen";

export type Delivery = components["schemas"]["DeliveryOut"];
export type Channel = Delivery["channel"];
export type Language = Delivery["language"];

export const channelLabel: Record<Channel, string> = {
  telegram: "Telegram",
  web_feed: "Web feed",
  sms: "SMS",
  whatsapp: "WhatsApp",
  x: "X",
  instagram: "Instagram",
  console: "Console (test)",
};

export type TileState = "waiting" | "sent" | "failed" | "retracted";

export function tileState(delivery: Delivery): TileState {
  switch (delivery.status) {
    case "sent":
      return "sent";
    case "failed":
      return "failed";
    case "retracted":
      return "retracted";
    default:
      return "waiting";
  }
}

function unique<T>(items: T[]): T[] {
  return [...new Set(items)];
}

/** Rows and columns come only from real deliveries, in the order they were planned. */
export function channelsIn(deliveries: Delivery[]): Channel[] {
  return unique(deliveries.map((d) => d.channel));
}

export function languagesIn(deliveries: Delivery[]): Language[] {
  return unique(deliveries.map((d) => d.language));
}

export function deliveryFor(
  deliveries: Delivery[],
  channel: Channel,
  language: Language,
): Delivery | undefined {
  return deliveries.find((d) => d.channel === channel && d.language === language);
}

export function sentCount(deliveries: Delivery[]): number {
  return deliveries.filter((d) => d.status === "sent").length;
}

export function allSent(deliveries: Delivery[]): boolean {
  return deliveries.length > 0 && sentCount(deliveries) === deliveries.length;
}

/** Replace a delivery with the same id, or add it. Used for each live update. */
export function applyDelivery(current: Delivery[], update: Delivery): Delivery[] {
  const index = current.findIndex((d) => d.id === update.id);
  if (index === -1) return [...current, update];
  return current.map((d, i) => (i === index ? update : d));
}

export type Elapsed = { ms: number; final: boolean };

/**
 * Time from approval until the last receipt arrived. Before every channel is sent, it is the
 * time so far. Only receipt times from the server are used.
 */
export function elapsedSinceApproval(
  approvedAtIso: string,
  deliveries: Delivery[],
  nowMs: number,
): Elapsed {
  const approved = Date.parse(approvedAtIso);
  if (allSent(deliveries)) {
    const times = deliveries.map((d) => (d.sent_at ? Date.parse(d.sent_at) : approved));
    return { ms: Math.max(0, Math.max(...times) - approved), final: true };
  }
  return { ms: Math.max(0, nowMs - approved), final: false };
}

export function formatElapsed(ms: number): string {
  const total = Math.floor(ms / 1000);
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return minutes > 0 ? `${minutes} min ${seconds} s` : `${seconds} s`;
}
