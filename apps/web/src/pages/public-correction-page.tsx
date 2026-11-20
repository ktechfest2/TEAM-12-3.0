import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { Loading, Notice } from "../components/ui/notice";
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
    <section className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-sm font-bold uppercase tracking-wider text-brand">Official correction</h1>
      {query.isPending ? <Loading /> : null}
      {query.error ? <Notice tone="error">{query.error.message}</Notice> : null}
      {query.data ? <CorrectionView correction={query.data} /> : null}
    </section>
  );
}
