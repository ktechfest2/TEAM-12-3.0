import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Icon, type IconName } from "../../components/icons";
import { controlClass, Loading, Notice } from "../../components/ui/surface";
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

const tileLook = {
  sent: { style: "border-confirmed/30 bg-confirmed-soft text-confirmed", icon: "checkCircle" },
  waiting: { style: "border-line bg-surface text-muted", icon: "wait" },
  failed: { style: "border-contradicted/30 bg-contradicted-soft text-contradicted", icon: "xCircle" },
  retracted: { style: "border-line-strong bg-sunken text-muted", icon: "undo" },
} as const satisfies Record<string, { style: string; icon: IconName }>;

function Tile({ delivery }: { delivery: Delivery | undefined }) {
  if (!delivery) return <td className="rounded-control bg-sunken p-2 text-center text-faint">-</td>;
  const state = tileState(delivery);
  const look = tileLook[state];
  const label = {
    sent: `Sent ${delivery.sent_at ? timeOfDay.format(new Date(delivery.sent_at)) : ""}`.trim(),
    waiting: "Waiting",
    failed: "Failed",
    retracted: "Withdrawn",
  }[state];
  return (
    <td
      className={`rounded-control border p-2.5 text-center text-sm font-semibold ${look.style}`}
      data-state={state}
    >
      <span className="inline-flex items-center justify-center gap-1.5">
        <Icon name={look.icon} size={16} />
        {label}
      </span>
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
    <div className="space-y-5">
      <div
        className="flex flex-wrap items-end justify-between gap-x-8 gap-y-3 rounded-card bg-brand p-6 text-paper shadow-lift"
        aria-live="polite"
      >
        <div>
          <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-beacon">
            <Icon name="clock" size={16} />
            Correction gap
          </p>
          <p
            className="font-display text-5xl font-bold tabular-nums sm:text-6xl"
            data-testid="elapsed"
          >
            {formatElapsed(elapsed.ms)}
          </p>
          <p className="text-brand-200">
            {elapsed.final
              ? "from approval until every channel was sent"
              : "since a reviewer approved it"}
          </p>
        </div>
        <p className="rounded-full bg-paper/10 px-4 py-1.5 font-semibold tabular-nums">
          {sentCount(deliveries)} of {deliveries.length} sent
        </p>
      </div>

      {deliveries.length === 0 && status !== "error" ? (
        status === "connecting" ? (
          <Loading>Connecting...</Loading>
        ) : (
          <Notice tone="empty">Nothing has been sent yet. Tiles appear when sending starts.</Notice>
        )
      ) : (
        <div className="overflow-x-auto rounded-card border border-line bg-surface p-3 shadow-card">
          <table className="w-full border-separate border-spacing-1">
            <caption className="sr-only">Delivery status by channel and language</caption>
            <thead>
              <tr>
                <th scope="col" className="p-2 text-left text-xs font-bold uppercase tracking-wider text-muted">
                  Channel
                </th>
                {languages.map((language) => (
                  <th
                    key={language}
                    scope="col"
                    className="p-2 text-xs font-bold uppercase tracking-wider text-muted"
                  >
                    {languageName[language]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {channels.map((channel) => (
                <tr key={channel}>
                  <th scope="row" className="whitespace-nowrap p-2 text-left font-semibold text-brand">
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

      {error ? <Notice tone="error">{error}</Notice> : null}
    </div>
  );
}

export function BroadcastBoard() {
  const query = useQuery({ queryKey: ["messages"], queryFn: listMessages, refetchInterval: 15000 });
  const [chosen, setChosen] = useState<string | null>(null);

  if (query.isPending) return <Loading />;
  if (query.error) return <Notice tone="error">{query.error.message}</Notice>;

  const sealed = query.data.filter((m) => m.integrity_hash !== null);
  if (sealed.length === 0) {
    return (
      <Notice tone="empty">No approved corrections yet. Approve and seal one first.</Notice>
    );
  }
  const selected = sealed.find((m) => m.id === chosen) ?? sealed[0];
  if (!selected) return null;

  return (
    <div className="space-y-6">
      <div>
        <label htmlFor="correction" className="block text-sm font-semibold">
          Correction
        </label>
        <select
          id="correction"
          value={selected.id}
          onChange={(e) => setChosen(e.target.value)}
          className={`${controlClass} mt-1.5 max-w-xl`}
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
