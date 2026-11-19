import { ArrowRight, Building2 } from "lucide-react";
import { Link } from "react-router";
import { Card } from "../../components/ui/card";
import { VerdictBadge } from "../../components/ui/verdict-badge";
import type { FactCheck, InformationArticle } from "./public-demo";

export function InformationCard({ article }: { article: InformationArticle }) {
  return (
    <Card className="flex h-full flex-col">
      <div className="flex items-center gap-2 text-xs font-semibold text-brand">
        <Building2 size={15} aria-hidden="true" /> Official guidance
      </div>
      <p className="mt-4 text-xs font-medium text-muted">{article.category}</p>
      <h2 className="mt-2 text-lg font-bold leading-6">
        <Link className="hover:text-brand" to={`/information/${article.slug}`}>
          {article.title}
        </Link>
      </h2>
      <p className="mt-3 flex-1 text-sm leading-6 text-secondary">{article.summary}</p>
      <div className="mt-5 flex items-center justify-between gap-3 border-t border-border pt-4 text-xs text-muted">
        <span>{article.sourceName}</span>
        <Link
          to={`/information/${article.slug}`}
          className="flex min-h-11 items-center gap-1 font-semibold text-brand"
        >
          Read <ArrowRight size={15} aria-hidden="true" />
        </Link>
      </div>
    </Card>
  );
}

export function FactCheckCard({ factCheck }: { factCheck: FactCheck }) {
  return (
    <Card className="h-full">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <VerdictBadge verdict={factCheck.verdict} />
        <time className="text-xs text-muted">{factCheck.publishedAt}</time>
      </div>
      <h2 className="mt-5 text-lg font-bold leading-6">{factCheck.title}</h2>
      <p className="mt-3 text-sm leading-6 text-secondary">{factCheck.summary}</p>
      <Link
        to={`/fact-checks/${factCheck.slug}`}
        className="mt-5 flex min-h-11 items-center gap-1 text-sm font-semibold text-brand"
      >
        Read fact-check <ArrowRight size={16} aria-hidden="true" />
      </Link>
    </Card>
  );
}
