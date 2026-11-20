import { Link, useParams } from "react-router";
import { Icon } from "../components/icons";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Container } from "../components/ui/container";
import { PageHeader } from "../components/ui/page-header";
import { SectionTitle } from "../components/ui/section-title";
import { VerdictBadge } from "../features/claims/verdict-badge";
import { FactCheckCard } from "../features/public/public-cards";
import { demonstrationNotice, factChecks } from "../features/public/public-demo";

const backLink =
  "inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-secondary hover:text-brand";

export function FactCheckDetailPage() {
  const { slug } = useParams();
  const factCheck = factChecks.find((item) => item.slug === slug);

  if (!factCheck) {
    return (
      <Container className="space-y-4 py-12 md:py-16">
        <h1 className="text-2xl font-bold">Fact-check not found</h1>
        <Link to="/fact-checks" className={backLink}>
          <Icon name="arrowLeft" size={16} /> Back to fact-checks
        </Link>
      </Container>
    );
  }

  const related = factChecks.filter((item) => item.slug !== factCheck.slug).slice(0, 2);

  const share = async () => {
    if (navigator.share) {
      await navigator.share({ title: factCheck.title, url: window.location.href });
    } else {
      await navigator.clipboard.writeText(window.location.href);
    }
  };

  return (
    <Container as="article" className="space-y-8 py-12 md:py-16">
      <div className="flex items-center justify-between gap-4">
        <Link to="/fact-checks" className={backLink}>
          <Icon name="arrowLeft" size={16} /> Fact-checks
        </Link>
        <Button variant="outline" size="sm" icon="share" onClick={() => void share()}>
          Share
        </Button>
      </div>

      <div className="space-y-4">
        <VerdictBadge verdict={factCheck.verdict} />
        <PageHeader title={factCheck.title} lead={factCheck.summary} />
        <time className="block text-sm text-muted">Published {factCheck.publishedAt}</time>
        <p className="text-sm text-secondary">{demonstrationNotice}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
        <div className="grid gap-6">
          <Card>
            <SectionTitle>Original claim</SectionTitle>
            <blockquote className="mt-3 border-l-4 border-brand pl-4 text-lg font-semibold">
              {factCheck.originalClaim}
            </blockquote>
          </Card>
          <Card>
            <h2 className="text-xl font-bold">Investigation summary</h2>
            <ul className="mt-4 grid gap-3">
              {factCheck.investigation.map((paragraph) => (
                <li key={paragraph} className="flex gap-3 text-sm text-secondary">
                  <span className="mt-2 size-1.5 shrink-0 rounded-full bg-brand" />
                  {paragraph}
                </li>
              ))}
            </ul>
          </Card>
        </div>
        <Card elevation="flat" className="h-fit">
          <h2 className="font-bold">Evidence and sources</h2>
          <div className="mt-4 flex gap-3">
            <Icon name="building" size={18} className="mt-0.5 shrink-0 text-brand" />
            <div>
              <p className="text-sm font-semibold">Official source passage</p>
              <p className="mt-1 text-xs text-muted">
                No source document is attached in this demonstration.
              </p>
            </div>
          </div>
        </Card>
      </div>

      {related.length > 0 ? (
        <section className="space-y-4 pt-4">
          <h2 className="text-2xl font-bold">Related fact-checks</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {related.map((item) => (
              <FactCheckCard key={item.slug} factCheck={item} />
            ))}
          </div>
        </section>
      ) : null}
    </Container>
  );
}
