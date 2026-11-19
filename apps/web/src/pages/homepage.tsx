import { ArrowRight, BookOpen, Search, ShieldCheck } from "lucide-react";
import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { FactCheckCard, InformationCard } from "../features/public/public-cards";
import { factChecks, informationArticles } from "../features/public/public-demo";

export function Homepage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const onSearch = (event: FormEvent) => {
    event.preventDefault();
    navigate(`/information${query.trim() ? `?q=${encodeURIComponent(query.trim())}` : ""}`);
  };

  return (
    <>
      <section className="border-b border-border bg-surface">
        <div className="mx-auto grid max-w-[1200px] gap-10 px-5 py-14 sm:px-8 md:grid-cols-[1.2fr_.8fr] md:items-center md:py-20">
          <div>
            <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-brand-soft px-3 py-1 text-xs font-semibold text-brand">
              <ShieldCheck size={15} aria-hidden="true" /> Verified election information
            </p>
            <h1 className="max-w-[760px] text-[38px] leading-[1.08] font-bold tracking-tight text-foreground md:text-[58px]">
              Know the facts. Make informed decisions.
            </h1>
            <p className="mt-5 max-w-[620px] text-base leading-7 text-secondary md:text-lg">
              Check election claims against official sources and clear, evidence-based guidance.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button as="link" to="/check" variant="primary" className="sm:min-w-40">
                Verify a claim <ArrowRight size={17} aria-hidden="true" />
              </Button>
              <Button as="link" to="/information" variant="outline" className="sm:min-w-48">
                Explore election information
              </Button>
            </div>
          </div>
          <Card className="p-6">
            <label htmlFor="home-search" className="text-sm font-semibold">
              Search election information
            </label>
            <form className="mt-2 flex gap-2" onSubmit={onSearch}>
              <input
                id="home-search"
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search voter registration, PVC..."
                className="min-h-11 min-w-0 flex-1 rounded-[10px] border border-border px-3"
              />
              <button
                type="submit"
                className="grid size-11 shrink-0 place-items-center rounded-[10px] bg-brand text-white"
                aria-label="Search"
              >
                <Search size={19} aria-hidden="true" />
              </button>
            </form>
            <p className="mt-4 text-xs leading-5 text-muted">
              Find guidance from official election sources.
            </p>
          </Card>
        </div>
      </section>

      <section className="mx-auto max-w-[1200px] px-5 py-14 sm:px-8">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
              Official guidance
            </p>
            <h2 className="mt-2 text-2xl font-bold md:text-[32px]">Election information</h2>
          </div>
          <Button as="link" to="/information" variant="ghost" className="hidden sm:inline-flex">
            View all <ArrowRight size={16} aria-hidden="true" />
          </Button>
        </div>
        <div className="mt-7 grid gap-4 md:grid-cols-3">
          {informationArticles.slice(0, 3).map((article) => (
            <InformationCard key={article.slug} article={article} />
          ))}
        </div>
      </section>

      <section className="border-y border-border bg-surface">
        <div className="mx-auto max-w-[1200px] px-5 py-14 sm:px-8">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
                Latest checks
              </p>
              <h2 className="mt-2 text-2xl font-bold md:text-[32px]">
                Recently fact-checked claims
              </h2>
            </div>
            <Button as="link" to="/fact-checks" variant="ghost" className="hidden sm:inline-flex">
              View all <ArrowRight size={16} aria-hidden="true" />
            </Button>
          </div>
          <div className="mt-7 grid gap-4 md:grid-cols-3">
            {factChecks.map((factCheck) => (
              <FactCheckCard key={factCheck.slug} factCheck={factCheck} />
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-[1200px] px-5 py-14 sm:px-8">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
              Stay informed
            </p>
            <h2 className="mt-2 text-2xl font-bold md:text-[32px]">How Clarion works</h2>
          </div>
        </div>
        <div className="mt-7 grid gap-4 md:grid-cols-3">
          {[
            ["01", "Submit a claim", "Share an election message, screenshot or link for review."],
            [
              "02",
              "Compare evidence",
              "A reviewer checks the claim against official source passages.",
            ],
            [
              "03",
              "Read the correction",
              "Follow the cited verdict and supporting official source.",
            ],
          ].map(([step, title, copy]) => (
            <Card key={step}>
              <span className="text-xs font-bold text-brand">{step}</span>
              <h3 className="mt-4 text-lg font-bold">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-secondary">{copy}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="border-y border-border bg-surface">
        <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-5 py-10 sm:px-8 md:flex-row md:items-center md:justify-between">
          <div className="flex gap-4">
            <span className="grid size-11 shrink-0 place-items-center rounded-[10px] bg-brand-soft text-brand">
              <BookOpen size={20} aria-hidden="true" />
            </span>
            <div>
              <h2 className="text-xl font-bold">Learn to verify election information</h2>
              <p className="mt-1 text-sm text-secondary">
                Simple guides for identifying misleading claims and checking sources.
              </p>
            </div>
          </div>
          <Button as="link" to="/" variant="outline">
            Read the verification guide
          </Button>
        </div>
      </section>
    </>
  );
}
