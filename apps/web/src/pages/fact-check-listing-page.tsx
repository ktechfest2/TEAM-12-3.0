import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import type { Verdict } from "../features/claims/verdict";
import { FactCheckCard } from "../features/public/public-cards";
import { demonstrationNotice, factChecks } from "../features/public/public-demo";

export function FactCheckListingPage() {
  const [query, setQuery] = useState("");
  const [verdict, setVerdict] = useState<"all" | Verdict>("all");
  const [topic, setTopic] = useState("All");

  const results = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return factChecks.filter((factCheck) => {
      const matchesQuery =
        normalized.length === 0 ||
        `${factCheck.title} ${factCheck.summary} ${factCheck.originalClaim}`
          .toLowerCase()
          .includes(normalized);
      const matchesVerdict = verdict === "all" || factCheck.verdict === verdict;
      const matchesTopic = topic === "All" || factCheck.topic === topic;
      return matchesQuery && matchesVerdict && matchesTopic;
    });
  }, [query, verdict, topic]);

  return (
    <section className="mx-auto max-w-[1200px] px-5 py-10 sm:px-8 md:py-14">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
        Verified checks
      </p>
      <h1 className="mt-3 text-3xl font-bold md:text-[40px]">Fact-checks</h1>
      <p className="mt-3 max-w-2xl text-base leading-7 text-secondary">
        Read clearly cited outcomes and the evidence behind published corrections.
      </p>
      <p className="mt-4 rounded-[10px] border border-border bg-surface px-4 py-3 text-xs leading-5 text-secondary">
        {demonstrationNotice}
      </p>

      <div className="mt-8 grid gap-3 sm:grid-cols-[1fr_180px_180px]">
        <label className="relative">
          <span className="sr-only">Search fact-checks</span>
          <Search size={18} className="absolute left-3 top-3.5 text-muted" aria-hidden="true" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search fact-checks"
            className="min-h-11 w-full rounded-[10px] border border-border pl-10 pr-3"
          />
        </label>
        <label>
          <span className="sr-only">Filter by verdict</span>
          <select
            value={verdict}
            onChange={(event) => setVerdict(event.target.value as "all" | Verdict)}
            className="min-h-11 w-full rounded-[10px] border border-border bg-white px-3"
          >
            <option value="all">All verdicts</option>
            <option value="confirmed">Confirmed</option>
            <option value="contradicted">Contradicted</option>
            <option value="no_official_statement">No official statement</option>
          </select>
        </label>
        <label>
          <span className="sr-only">Filter by topic</span>
          <select
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            className="min-h-11 w-full rounded-[10px] border border-border bg-white px-3"
          >
            <option>All</option>
            <option>Voter registration</option>
            <option>PVC</option>
            <option>Voting procedures</option>
          </select>
        </label>
      </div>

      <p className="mt-6 text-sm text-muted" role="status">
        {results.length} {results.length === 1 ? "fact-check" : "fact-checks"}
      </p>
      {results.length > 0 ? (
        <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {results.map((factCheck) => (
            <FactCheckCard key={factCheck.slug} factCheck={factCheck} />
          ))}
        </div>
      ) : (
        <div className="mt-4 rounded-[14px] border border-border bg-surface p-8 text-center">
          <h2 className="font-bold">No fact-checks found</h2>
          <p className="mt-2 text-sm text-muted">Try a different search or filter.</p>
        </div>
      )}
    </section>
  );
}
