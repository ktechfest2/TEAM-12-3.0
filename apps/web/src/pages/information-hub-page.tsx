import { useMemo, useState } from "react";
import { useSearchParams } from "react-router";
import { Icon } from "../components/icons";
import { Container } from "../components/ui/container";
import { Input, Select } from "../components/ui/input";
import { Notice } from "../components/ui/notice";
import { PageHeader } from "../components/ui/page-header";
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
    <Container className="space-y-8 py-12 md:py-16">
      <div className="space-y-4">
        <PageHeader
          title="Election information hub"
          lead="Find practical guidance and verified pathways to official election information."
        />
        <p className="text-sm text-secondary">{demonstrationNotice}</p>
      </div>

      <div className="flex flex-col gap-3 md:flex-row">
        <div className="relative flex-1">
          <label htmlFor="search-election-information" className="sr-only">
            Search election information
          </label>
          <Icon name="search" size={18} className="absolute left-3 top-3 text-muted" />
          <Input
            id="search-election-information"
            type="search"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Search election information"
            className="pl-10"
          />
        </div>
        <div>
          <label htmlFor="filter-by-category" className="sr-only">
            Filter by category
          </label>
          <Select
            id="filter-by-category"
            value={category}
            onChange={(event) => setCategory(event.target.value as (typeof categories)[number])}
            className="md:w-56"
          >
            {categories.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </Select>
        </div>
      </div>

      <div className="space-y-4">
        <p className="text-sm text-muted" role="status">
          {results.length} {results.length === 1 ? "guide" : "guides"}
        </p>
        {results.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {results.map((article) => (
              <InformationCard key={article.slug} article={article} />
            ))}
          </div>
        ) : (
          <Notice tone="empty">No information found. Try a different search or category.</Notice>
        )}
      </div>
    </Container>
  );
}
