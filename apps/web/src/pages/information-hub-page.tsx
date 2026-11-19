import { useMemo, useState } from "react";
import { useSearchParams } from "react-router";
import { Icon } from "../components/icons";
import { InformationCard } from "../features/public/public-cards";
import { demonstrationNotice, informationArticles } from "../features/public/public-demo";

const categories = [
  "All",
  "Voter registration",
  "PVC",
  "Polling units",
  "Voting procedures",
  "Election dates",
] as const;

export function InformationHubPage() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get("q") ?? "");
  const [category, setCategory] = useState<(typeof categories)[number]>("All");

  const results = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return informationArticles.filter((article) => {
      const matchesCategory = category === "All" || article.category === category;
      const matchesQuery =
        normalized.length === 0 ||
        `${article.title} ${article.summary} ${article.category}`
          .toLowerCase()
          .includes(normalized);
      return matchesCategory && matchesQuery;
    });
  }, [category, query]);

  const onQueryChange = (value: string) => {
    setQuery(value);
    const next = new URLSearchParams(params);
    if (value) next.set("q", value);
    else next.delete("q");
    setParams(next, { replace: true });
  };

  return (
    <section className="mx-auto max-w-[1200px] px-5 py-10 sm:px-8 md:py-14">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
        Election guidance
      </p>
      <h1 className="mt-3 text-3xl font-bold md:text-[40px]">Election information hub</h1>
      <p className="mt-3 max-w-2xl text-base leading-7 text-secondary">
        Find practical guidance and verified pathways to official election information.
      </p>
      <p className="mt-4 rounded-[10px] border border-border bg-surface px-4 py-3 text-xs leading-5 text-secondary">
        {demonstrationNotice}
      </p>

      <div className="mt-8 flex flex-col gap-3 md:flex-row">
        <label className="relative flex-1">
          <span className="sr-only">Search election information</span>
          <Icon name="search" size={18} className="absolute left-3 top-3.5 text-muted" />
          <input
            type="search"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Search election information"
            className="min-h-11 w-full rounded-[10px] border border-border pl-10 pr-3"
          />
        </label>
        <label>
          <span className="sr-only">Filter by category</span>
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value as (typeof categories)[number])}
            className="min-h-11 w-full rounded-[10px] border border-border bg-white px-3 md:w-56"
          >
            {categories.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
      </div>

      <p className="mt-6 text-sm text-muted" role="status">
        {results.length} {results.length === 1 ? "guide" : "guides"}
      </p>
      {results.length > 0 ? (
        <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {results.map((article) => (
            <InformationCard key={article.slug} article={article} />
          ))}
        </div>
      ) : (
        <div className="mt-4 rounded-[14px] border border-border bg-surface p-8 text-center">
          <h2 className="font-bold">No information found</h2>
          <p className="mt-2 text-sm text-muted">Try a different search or category.</p>
        </div>
      )}
    </section>
  );
}
