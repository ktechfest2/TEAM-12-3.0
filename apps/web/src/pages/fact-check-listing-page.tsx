import { useMemo, useState } from "react";
import { Icon } from "../components/icons";
import { Container } from "../components/ui/container";
import { Input, Select } from "../components/ui/input";
import { Notice } from "../components/ui/notice";
import { PageHeader } from "../components/ui/page-header";
import type { Verdict } from "../features/claims/verdict";
import { FactCheckCard } from "../features/public/public-cards";
import { demonstrationNotice, factChecks } from "../features/public/public-demo";

const allTopics = "All topics";

export function FactCheckListingPage() {
  const [query, setQuery] = useState("");
  const [verdict, setVerdict] = useState<"all" | Verdict>("all");
  const [topic, setTopic] = useState(allTopics);

  const results = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return factChecks.filter((factCheck) => {
      const matchesQuery =
        normalized.length === 0 ||
        `${factCheck.title} ${factCheck.summary} ${factCheck.originalClaim}`
          .toLowerCase()
          .includes(normalized);
      const matchesVerdict = verdict === "all" || factCheck.verdict === verdict;
      const matchesTopic = topic === allTopics || factCheck.topic === topic;
      return matchesQuery && matchesVerdict && matchesTopic;
    });
  }, [query, verdict, topic]);

  return (
    <Container className="space-y-8 py-12 md:py-16">
      <div className="space-y-4">
        <PageHeader
          title="Fact-checks"
          lead="Read clearly cited outcomes and the evidence behind published corrections."
        />
        <p className="text-sm text-secondary">{demonstrationNotice}</p>
      </div>

      <div className="grid gap-3 sm:grid-cols-[1fr_11rem_11rem]">
        <div className="relative">
          <label htmlFor="search-fact-checks" className="sr-only">
            Search fact-checks
          </label>
          <Icon name="search" size={18} className="absolute left-3 top-3 text-muted" />
          <Input
            id="search-fact-checks"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search fact-checks"
            className="pl-10"
          />
        </div>
        <div>
          <label htmlFor="filter-by-verdict" className="sr-only">
            Filter by verdict
          </label>
          <Select
            id="filter-by-verdict"
            value={verdict}
            onChange={(event) => setVerdict(event.target.value as "all" | Verdict)}
          >
            <option value="all">All verdicts</option>
            <option value="confirmed">Confirmed</option>
            <option value="contradicted">Contradicted</option>
            <option value="no_official_statement">No official statement</option>
          </Select>
        </div>
        <div>
          <label htmlFor="filter-by-topic" className="sr-only">
            Filter by topic
          </label>
          <Select
            id="filter-by-topic"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
          >
            <option>{allTopics}</option>
            <option>Voter registration</option>
            <option>PVC</option>
            <option>Voting procedures</option>
          </Select>
        </div>
      </div>

      <div className="space-y-4">
        <p className="text-sm text-muted" role="status">
          {results.length} {results.length === 1 ? "fact-check" : "fact-checks"}
        </p>
        {results.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {results.map((factCheck) => (
              <FactCheckCard key={factCheck.slug} factCheck={factCheck} />
            ))}
          </div>
        ) : (
          <Notice tone="empty">No fact-checks found. Try a different search or filter.</Notice>
        )}
      </div>
    </Container>
  );
}
