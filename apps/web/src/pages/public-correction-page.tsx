import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { Container } from "../components/ui/container";
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
    <Container width="prose" className="space-y-6 py-12 md:py-16">
      <h1 className="text-xl font-bold text-brand">Official correction</h1>
      {query.isPending ? <Loading /> : null}
      {query.error ? <Notice tone="error">{query.error.message}</Notice> : null}
      {query.data ? <CorrectionView correction={query.data} /> : null}
    </Container>
  );
}
