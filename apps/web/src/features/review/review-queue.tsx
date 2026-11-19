import { useQuery } from "@tanstack/react-query";
import { verdictLabel } from "../claims/verdict";
import { listMessages } from "./review-api";
import { stageLabel, stageOf } from "./review-rules";

type Props = { selectedId: string | null; onSelect: (id: string) => void };

export function ReviewQueue({ selectedId, onSelect }: Props) {
  const query = useQuery({ queryKey: ["messages"], queryFn: listMessages, refetchInterval: 15000 });

  if (query.isPending) return <p className="text-muted">Loading claims...</p>;
  if (query.error) return <p role="alert">{query.error.message}</p>;
  if (query.data.length === 0) {
    return <p className="text-muted">No claims are waiting. New ones appear here.</p>;
  }

  return (
    <ul aria-label="Claims to review" className="space-y-2">
      {query.data.map((message) => {
        const selected = message.id === selectedId;
        return (
          <li key={message.id}>
            <button
              type="button"
              onClick={() => onSelect(message.id)}
              aria-current={selected ? "true" : undefined}
              className={`w-full rounded-md border p-3 text-left ${
                selected ? "border-brand bg-slate-50" : "border-slate-200"
              }`}
            >
              <span className="block font-semibold">{message.claim_text}</span>
              <span className="mt-1 block text-sm text-muted">
                {verdictLabel[message.verdict]} · {stageLabel[stageOf(message)]}
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
