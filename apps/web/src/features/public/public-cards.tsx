import { Link } from "react-router";
import { Icon } from "../../components/icons";
import { Card } from "../../components/ui/card";
import { VerdictBadge } from "../claims/verdict-badge";
import type { FactCheck, InformationArticle } from "./public-demo";

export function InformationCard({ article }: { article: InformationArticle }) {
  return (
    <Card className="flex h-full flex-col">
      <p className="text-xs font-semibold text-brand">{article.category}</p>
      <h2 className="mt-2 text-lg font-bold">
        <Link
          className="inline-flex min-h-10 items-center hover:text-brand"
          to={`/information/${article.slug}`}
        >
          {article.title}
        </Link>
      </h2>
      <p className="mt-3 flex-1 text-sm text-secondary">{article.summary}</p>
      <div className="mt-4 flex items-center justify-between gap-3 border-t border-border pt-2 text-xs text-muted">
        <span className="flex items-center gap-2">
          <Icon name="building" size={16} /> {article.sourceName}
        </span>
        <Link
          to={`/information/${article.slug}`}
          className="flex min-h-10 items-center gap-1 text-sm font-semibold text-brand"
        >
          Read <Icon name="arrowRight" size={16} />
        </Link>
      </div>
    </Card>
  );
}

export function FactCheckCard({ factCheck }: { factCheck: FactCheck }) {
  return (
    <Card className="flex h-full flex-col">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <VerdictBadge verdict={factCheck.verdict} />
        <time className="text-xs text-muted">{factCheck.publishedAt}</time>
      </div>
      <h2 className="mt-4 text-lg font-bold">{factCheck.title}</h2>
      <p className="mt-3 flex-1 text-sm text-secondary">{factCheck.summary}</p>
      <Link
        to={`/fact-checks/${factCheck.slug}`}
        className="mt-4 flex min-h-10 items-center gap-1 text-sm font-semibold text-brand"
      >
        Read fact-check <Icon name="arrowRight" size={16} />
      </Link>
    </Card>
  );
}
