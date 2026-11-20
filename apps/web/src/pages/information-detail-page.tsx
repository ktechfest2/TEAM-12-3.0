import { Link, useParams } from "react-router";
import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { Container } from "../components/ui/container";
import { PageHeader } from "../components/ui/page-header";
import { InformationCard } from "../features/public/public-cards";
import { demonstrationNotice, informationArticles } from "../features/public/public-demo";

const backLink =
  "inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-secondary hover:text-brand";

export function InformationDetailPage() {
  const { slug } = useParams();
  const article = informationArticles.find((item) => item.slug === slug);

  if (!article) {
    return (
      <Container className="space-y-4 py-12 md:py-16">
        <h1 className="text-2xl font-bold">Information not found</h1>
        <Link to="/information" className={backLink}>
          <Icon name="arrowLeft" size={16} /> Back to election information
        </Link>
      </Container>
    );
  }

  const related = informationArticles.filter((item) => item.slug !== article.slug).slice(0, 2);

  return (
    <Container as="article" className="space-y-8 py-12 md:py-16">
      <Link to="/information" className={backLink}>
        <Icon name="arrowLeft" size={16} /> Election information
      </Link>
      <div className="grid gap-8 lg:grid-cols-[1fr_20rem]">
        <div className="space-y-6">
          <div className="space-y-3">
            <p className="text-sm font-semibold text-brand">{article.category}</p>
            <PageHeader title={article.title} lead={article.summary} />
            <div className="flex flex-wrap gap-4 text-xs text-muted">
              <span className="flex items-center gap-2">
                <Icon name="calendar" size={16} /> Updated {article.updatedAt}
              </span>
              <span className="flex items-center gap-2">
                <Icon name="building" size={16} /> {article.sourceName}
              </span>
            </div>
            <p className="text-sm text-secondary">{demonstrationNotice}</p>
          </div>
          <Card>
            <h2 className="text-xl font-bold">What to do</h2>
            <ol className="mt-4 grid gap-4">
              {article.content.map((paragraph, index) => (
                <li key={paragraph} className="flex gap-4 text-sm text-secondary">
                  <span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand-soft text-xs font-bold text-brand">
                    {index + 1}
                  </span>
                  <span className="pt-1">{paragraph}</span>
                </li>
              ))}
            </ol>
          </Card>
        </div>
        <Card elevation="flat" className="h-fit">
          <h2 className="font-bold">Official source</h2>
          <p className="mt-2 text-sm text-secondary">{article.sourceName}</p>
          <p className="mt-4 flex items-center gap-2 text-sm text-muted">
            Source link unavailable <Icon name="external" size={16} />
          </p>
        </Card>
      </div>
      {related.length > 0 ? (
        <section className="space-y-4 pt-4">
          <h2 className="text-2xl font-bold">Related information</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {related.map((item) => (
              <InformationCard key={item.slug} article={item} />
            ))}
          </div>
        </section>
      ) : null}
    </Container>
  );
}
