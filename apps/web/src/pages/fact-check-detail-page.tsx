import { Link, useParams } from "react-router";
import { Icon } from "../components/icons";
import { Card } from "../components/ui/card";
import { VerdictBadge } from "../features/claims/verdict-badge";
import { FactCheckCard } from "../features/public/public-cards";
import { demonstrationNotice, factChecks } from "../features/public/public-demo";

export function FactCheckDetailPage() {
  const { slug } = useParams();
  const factCheck = factChecks.find((item) => item.slug === slug);

  if (!factCheck) {
    return (
      <section className="mx-auto max-w-page px-6 py-16 sm:px-8">
        <h1 className="text-2xl font-bold">Fact-check not found</h1>
        <Link to="/fact-checks" className="mt-4 inline-flex min-h-11 items-center text-brand">
          <Icon name="arrowLeft" size={16} className="mr-2" /> Back to fact-checks
        </Link>
      </section>
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
    <article className="mx-auto max-w-page px-6 py-12 sm:px-8 md:py-16">
      <div className="flex items-center justify-between gap-4">
        <Link
          to="/fact-checks"
          className="inline-flex min-h-11 items-center text-sm font-semibold text-secondary hover:text-brand"
        >
          <Icon name="arrowLeft" size={16} className="mr-2" /> Fact-checks
        </Link>
        <button
          type="button"
          onClick={() => void share()}
          className="flex min-h-11 items-center gap-2 rounded-control border border-border px-3 text-sm font-semibold hover:bg-canvas"
        >
          <Icon name="share" size={16} /> Share
        </button>
      </div>

      <header className="mt-6 max-w-4xl">
        <VerdictBadge verdict={factCheck.verdict} />
        <h1 className="mt-4 text-3xl font-bold leading-tight md:text-[44px]">{factCheck.title}</h1>
        <p className="mt-4 text-lg leading-8 text-secondary">{factCheck.summary}</p>
        <time className="mt-4 block text-sm text-muted">Published {factCheck.publishedAt}</time>
      </header>

      <p className="mt-6 rounded-control border border-border bg-canvas px-4 py-3 text-xs leading-5 text-secondary">
        {demonstrationNotice}
      </p>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="grid gap-6">
          <Card>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
              Original claim
            </p>
            <blockquote className="mt-3 border-l-4 border-brand pl-4 text-lg font-semibold leading-7">
              {factCheck.originalClaim}
            </blockquote>
          </Card>
          <Card>
            <h2 className="text-xl font-bold">Investigation summary</h2>
            <ul className="mt-4 grid gap-3">
              {factCheck.investigation.map((paragraph) => (
                <li key={paragraph} className="flex gap-3 text-sm leading-7 text-secondary">
                  <span className="mt-2 size-1.5 shrink-0 rounded-full bg-brand" />
                  {paragraph}
                </li>
              ))}
            </ul>
          </Card>
        </div>
        <aside className="h-fit rounded-card border border-border p-6">
          <h2 className="font-bold">Evidence and sources</h2>
          <div className="mt-4 flex gap-3 rounded-control bg-canvas p-3">
            <Icon name="building" size={18} className="shrink-0 text-brand" />
            <div>
              <p className="text-sm font-semibold">Official source passage</p>
              <p className="mt-1 text-xs leading-5 text-muted">
                No source document is attached in this demonstration.
              </p>
            </div>
          </div>
        </aside>
      </div>

      {related.length > 0 ? (
        <section className="mt-16">
          <h2 className="text-2xl font-bold">Related fact-checks</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {related.map((item) => (
              <FactCheckCard key={item.slug} factCheck={item} />
            ))}
          </div>
        </section>
      ) : null}
    </article>
  );
}
