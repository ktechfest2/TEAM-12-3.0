import { getSession } from "../../lib/auth/session";
import { env } from "../../lib/env";
import type { Delivery } from "./board-model";
import { parseSse } from "./sse";

export type StreamHandlers = {
  onSnapshot: (deliveries: Delivery[]) => void;
  onDelivery: (delivery: Delivery) => void;
  onDone: () => void;
};

/**
 * Read the server sent events for one message. The browser EventSource cannot send an
 * Authorization header, so this reads the stream with fetch.
 */
export async function streamDeliveries(
  messageId: string,
  handlers: StreamHandlers,
  signal: AbortSignal,
): Promise<void> {
  const token = getSession()?.token;
  const response = await fetch(`${env.apiBaseUrl}/messages/${messageId}/deliveries/events`, {
    headers: {
      Accept: "text/event-stream",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    signal,
  });
  if (response.status === 401) throw new Error("Your session ended. Sign in again.");
  if (!response.ok || !response.body) throw new Error("The live feed could not start.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parsed = parseSse(buffer);
    buffer = parsed.rest;
    for (const { event, data } of parsed.events) {
      if (event === "snapshot") handlers.onSnapshot(JSON.parse(data) as Delivery[]);
      else if (event === "delivery") handlers.onDelivery(JSON.parse(data) as Delivery);
      else if (event === "done") handlers.onDone();
    }
  }
}
