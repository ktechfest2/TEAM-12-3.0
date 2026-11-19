import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { fetchCorrection } from "../features/public/correction";
import { CorrectionView } from "../features/public/correction-view";

export function PublicCorrectionPage() {
  const { messageId = "" } = useParams();
  const query = useQuery({
    queryKey: ["public-correction", messageId],
    queryFn: () => fetchCorrection(messageId),
    retry: false,
  });

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Official correction</h1>
      {query.isPending ? <p className="text-muted">Loading...</p> : null}
      {query.error ? <p role="alert">{query.error.message}</p> : null}
      {query.data ? <CorrectionView correction={query.data} /> : null}
    </section>
  );
}
