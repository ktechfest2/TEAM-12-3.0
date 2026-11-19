import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { listMessages } from "../review/review-api";
import { languageName, type Message } from "../review/review-rules";
import {
  channelLabel,
  channelsIn,
  type Delivery,
  deliveryFor,
  elapsedSinceApproval,
  formatElapsed,
  languagesIn,
  sentCount,
  tileState,
} from "./board-model";
import { useDeliveryStream } from "./use-delivery-stream";

const timeOfDay = new Intl.DateTimeFormat("en-NG", {
  timeStyle: "medium",
  timeZone: "Africa/Lagos",
});

function Tile({ delivery }: { delivery: Delivery | undefined }) {
  if (!delivery) return <td className="border border-slate-200 p-2 text-center text-muted">-</td>;
  const state = tileState(delivery);
  const style = {
    sent: "border-brand bg-green-50 text-brand",
    waiting: "border-slate-300 bg-white text-muted",
    failed: "border-contradicted bg-red-50 text-contradicted",
    retracted: "border-slate-400 bg-slate-100 text-slate-700",
  }[state];
  const label = {
    sent: `✓ Sent ${delivery.sent_at ? timeOfDay.format(new Date(delivery.sent_at)) : ""}`.trim(),
    waiting: "… Waiting",
    failed: "✗ Failed",
    retracted: "Withdrawn",
  }[state];
  return (
    <td className={`border-2 p-2 text-center text-sm font-semibold ${style}`} data-state={state}>
      {label}
    </td>
  );
}

function useNow(active: boolean): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!active) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [active]);
  return now;
}

function Board({ message }: { message: Message }) {
  const { deliveries, status, error } = useDeliveryStream(message.id);
  const approvedAt = message.review?.created_at ?? message.created_at;
  const now = useNow(status === "live" || status === "connecting");
  const elapsed = elapsedSinceApproval(approvedAt, deliveries, now);
  const channels = channelsIn(deliveries);
  const languages = languagesIn(deliveries);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-baseline gap-x-6 gap-y-1" aria-live="polite">
        <p className="text-3xl font-bold" data-testid="elapsed">
          {formatElapsed(elapsed.ms)}
        </p>
        <p className="text-muted">
          {elapsed.final
            ? "from approval until every channel was sent"
            : "since a reviewer approved it"}
        </p>
        <p className="font-semibold">
          {sentCount(deliveries)} of {deliveries.length} sent
        </p>
      </div>

      {deliveries.length === 0 && status !== "error" ? (
        <p className="text-muted">
          {status === "connecting"
            ? "Connecting..."
            : "Nothing has been sent yet. Tiles appear when sending starts."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-separate border-spacing-1">
            <caption className="sr-only">Delivery status by channel and language</caption>
            <thead>
              <tr>
                <th scope="col" className="p-2 text-left">
                  Channel
                </th>
                {languages.map((language) => (
                  <th key={language} scope="col" className="p-2">
                    {languageName[language]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {channels.map((channel) => (
                <tr key={channel}>
                  <th scope="row" className="p-2 text-left">
                    {channelLabel[channel]}
                  </th>
                  {languages.map((language) => (
                    <Tile key={language} delivery={deliveryFor(deliveries, channel, language)} />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {error ? <p role="alert">{error}</p> : null}
    </div>
  );
}

export function BroadcastBoard() {
  const query = useQuery({ queryKey: ["messages"], queryFn: listMessages, refetchInterval: 15000 });
  const [chosen, setChosen] = useState<string | null>(null);

  if (query.isPending) return <p className="text-muted">Loading...</p>;
  if (query.error) return <p role="alert">{query.error.message}</p>;

  const sealed = query.data.filter((m) => m.integrity_hash !== null);
  if (sealed.length === 0) {
    return <p className="text-muted">No approved corrections yet. Approve and seal one first.</p>;
  }
  const selected = sealed.find((m) => m.id === chosen) ?? sealed[0];
  if (!selected) return null;

  return (
    <div className="space-y-6">
      <div>
        <label htmlFor="correction" className="block font-semibold">
          Correction
        </label>
        <select
          id="correction"
          value={selected.id}
          onChange={(e) => setChosen(e.target.value)}
          className="mt-1 w-full max-w-xl rounded-md border border-slate-300 p-2"
        >
          {sealed.map((m) => (
            <option key={m.id} value={m.id}>
              {m.claim_text}
            </option>
          ))}
        </select>
      </div>
      <Board key={selected.id} message={selected} />
    </div>
  );
}
