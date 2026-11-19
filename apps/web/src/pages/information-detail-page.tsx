import { Link, useParams } from "react-router";
import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { InformationCard } from "../features/public/public-cards";
import { demonstrationNotice, informationArticles } from "../features/public/public-demo";

export function InformationDetailPage() {
  const { slug } = useParams();
  const article = informationArticles.find((item) => item.slug === slug);

  if (!article) {
    return (
      <section className="mx-auto max-w-[1200px] px-5 py-16 sm:px-8">
        <h1 className="text-2xl font-bold">Information not found</h1>
        <Link to="/information" className="mt-4 inline-flex min-h-11 items-center text-brand">
          <Icon name="arrowLeft" size={16} className="mr-2" /> Back to election information
        </Link>
      </section>
    );
  }

  const related = informationArticles.filter((item) => item.slug !== article.slug).slice(0, 2);

  return (
    <article className="mx-auto max-w-[1200px] px-5 py-10 sm:px-8 md:py-14">
      <Link
        to="/information"
        className="inline-flex min-h-11 items-center text-sm font-semibold text-secondary hover:text-brand"
      >
        <Icon name="arrowLeft" size={16} className="mr-2" /> Election information
      </Link>
      <div className="mt-6 grid gap-8 lg:grid-cols-[1fr_280px]">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
            {article.category}
          </p>
          <h1 className="mt-3 max-w-3xl text-3xl font-bold leading-tight md:text-[44px]">
            {article.title}
          </h1>
          <p className="mt-5 text-lg leading-8 text-secondary">{article.summary}</p>
          <div className="mt-5 flex flex-wrap gap-4 text-xs text-muted">
            <span className="flex items-center gap-1.5">
              <Icon name="calendar" size={15} /> Updated {article.updatedAt}
            </span>
            <span className="flex items-center gap-1.5">
              <Icon name="building" size={15} /> {article.sourceName}
            </span>
          </div>
          <p className="mt-6 rounded-[10px] border border-border bg-surface px-4 py-3 text-xs leading-5 text-secondary">
            {demonstrationNotice}
          </p>
          <Card className="mt-8 p-6 md:p-8">
            <h2 className="text-xl font-bold">What to do</h2>
            <ol className="mt-5 grid gap-5">
              {article.content.map((paragraph, index) => (
                <li key={paragraph} className="flex gap-4 text-sm leading-7 text-secondary">
                  <span className="grid size-7 shrink-0 place-items-center rounded-full bg-brand-soft text-xs font-bold text-brand">
                    {index + 1}
                  </span>
                  {paragraph}
                </li>
              ))}
            </ol>
          </Card>
        </div>
        <aside className="h-fit rounded-[14px] border border-border p-5">
          <h2 className="font-bold">Official source</h2>
          <p className="mt-2 text-sm leading-6 text-muted">{article.sourceName}</p>
          <span className="mt-4 flex min-h-11 items-center gap-2 text-sm font-semibold text-brand">
            Source link unavailable <Icon name="external" size={15} />
          </span>
        </aside>
      </div>
      {related.length > 0 ? (
        <section className="mt-14">
          <h2 className="text-2xl font-bold">Related information</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {related.map((item) => (
              <InformationCard key={item.slug} article={item} />
            ))}
          </div>
        </section>
      ) : null}
    </article>
  );
}
