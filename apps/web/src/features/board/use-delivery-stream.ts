import { useEffect, useState } from "react";
import { applyDelivery, type Delivery } from "./board-model";
import { streamDeliveries } from "./delivery-stream";

export type StreamStatus = "idle" | "connecting" | "live" | "done" | "error";

export type DeliveryStream = {
  deliveries: Delivery[];
  status: StreamStatus;
  error: string | null;
};

/** Live deliveries for one message. Reconnects are left to the user (reload) on purpose. */
export function useDeliveryStream(messageId: string | null): DeliveryStream {
  const [state, setState] = useState<DeliveryStream>({
    deliveries: [],
    status: "idle",
    error: null,
  });

  useEffect(() => {
    if (!messageId) {
      setState({ deliveries: [], status: "idle", error: null });
      return;
    }
    const controller = new AbortController();
    setState({ deliveries: [], status: "connecting", error: null });
    streamDeliveries(
      messageId,
      {
        onSnapshot: (deliveries) =>
          setState((s) => ({ ...s, deliveries, status: "live", error: null })),
        onDelivery: (delivery) =>
          setState((s) => ({ ...s, deliveries: applyDelivery(s.deliveries, delivery) })),
        onDone: () => setState((s) => ({ ...s, status: "done" })),
      },
      controller.signal,
    )
      .then(() =>
        setState((s) =>
          s.status === "live"
            ? { ...s, status: "error", error: "The live feed closed early. Reload to reconnect." }
            : s,
        ),
      )
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const message = error instanceof Error ? error.message : "The live feed stopped.";
        setState((s) => ({ ...s, status: "error", error: message }));
      });
    return () => controller.abort();
  }, [messageId]);

  return state;
}
