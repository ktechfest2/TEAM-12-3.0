import { useQuery } from "@tanstack/react-query";
import { Loading, Notice, Pill } from "../../components/ui/surface";
import { verdictLabel } from "../claims/verdict";
import { listMessages } from "./review-api";
import { stageLabel, stageOf } from "./review-rules";

type Props = { selectedId: string | null; onSelect: (id: string) => void };

const verdictDot = {
  confirmed: "bg-confirmed",
  contradicted: "bg-contradicted",
  no_official_statement: "bg-unknown",
} as const;

export function ReviewQueue({ selectedId, onSelect }: Props) {
  const query = useQuery({ queryKey: ["messages"], queryFn: listMessages, refetchInterval: 15000 });

  if (query.isPending) return <Loading>Loading claims...</Loading>;
  if (query.error) return <Notice tone="error">{query.error.message}</Notice>;
  if (query.data.length === 0) {
    return <Notice tone="empty">No claims are waiting. New ones appear here.</Notice>;
  }

  return (
    <ul aria-label="Claims to review" className="space-y-2">
      {query.data.map((message) => {
        const selected = message.id === selectedId;
        const stage = stageOf(message);
        return (
          <li key={message.id}>
            <button
              type="button"
              onClick={() => onSelect(message.id)}
              aria-current={selected ? "true" : undefined}
              className={`w-full rounded-control border p-3.5 text-left transition-colors ${
                selected
                  ? "border-brand bg-brand-50 shadow-card"
                  : "border-line bg-surface hover:border-line-strong hover:bg-sunken"
              }`}
            >
              <span className="line-clamp-3 block font-semibold text-ink">
                {message.claim_text}
              </span>
              <span className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted">
                <span
                  aria-hidden="true"
                  className={`size-2 rounded-full ${verdictDot[message.verdict]}`}
                />
                <span>{verdictLabel[message.verdict]}</span>
                <span aria-hidden="true">·</span>
                <Pill tone={stage === "draft" ? "attention" : "neutral"}>{stageLabel[stage]}</Pill>
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
