import { useState } from "react";
import { NavLink, Outlet } from "react-router";
import { Logo } from "./brand/logo";
import { Icon } from "./icons";
import { Button } from "./ui/button";
import { Container } from "./ui/container";

const navigation = [
  { to: "/information", label: "Election information" },
  { to: "/fact-checks", label: "Fact-checks" },
  { to: "/guide", label: "How it works" },
  { to: "/subscribe", label: "Text alerts" },
] as const;

function FooterLinks({
  title,
  links,
}: {
  title: string;
  links: readonly { to: string; label: string }[];
}) {
  return (
    <nav aria-label={title} className="text-sm text-secondary">
      <p className="font-semibold text-foreground">{title}</p>
      <ul className="mt-1">
        {links.map((link) => (
          <li key={link.to}>
            <NavLink to={link.to} className="flex min-h-10 items-center hover:text-brand">
              {link.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export function PublicLayout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen bg-surface text-foreground">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-control focus:border focus:border-border-strong focus:bg-surface focus:px-4 focus:py-2"
      >
        Skip to content
      </a>
      <header className="sticky top-0 z-40 border-b border-border bg-surface/95 backdrop-blur">
        <nav
          className="mx-auto flex h-16 w-full max-w-page items-center justify-between px-4 sm:px-6 lg:px-8"
          aria-label="Primary navigation"
        >
          <NavLink
            to="/"
            className="flex min-h-11 items-center gap-3"
            onClick={() => setOpen(false)}
          >
            <Logo />
          </NavLink>

          <div className="hidden items-center gap-8 lg:flex">
            {navigation.map((link) => (
              <NavLink
                key={link.label}
                to={link.to}
                className="flex min-h-11 items-center text-sm font-semibold text-secondary hover:text-brand"
              >
                {link.label}
              </NavLink>
            ))}
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <Button as="link" to="/dashboard" variant="quiet" icon="user">
              Reviewer workspace
            </Button>
            <Button as="link" to="/check" variant="primary">
              Verify a claim
            </Button>
          </div>

          <button
            type="button"
            className="grid size-11 place-items-center rounded-control border border-border-strong lg:hidden"
            aria-expanded={open}
            aria-controls="mobile-navigation"
            aria-label={open ? "Close navigation" : "Open navigation"}
            onClick={() => setOpen((value) => !value)}
          >
            {open ? <Icon name="close" size={21} /> : <Icon name="menu" size={21} />}
          </button>
        </nav>

        {open ? (
          <div
            id="mobile-navigation"
            className="border-t border-border bg-surface px-4 py-4 sm:px-6 lg:hidden"
          >
            <div className="mx-auto grid max-w-page gap-1">
              {navigation.map((link) => (
                <NavLink
                  key={link.label}
                  to={link.to}
                  onClick={() => setOpen(false)}
                  className="flex min-h-11 items-center rounded-control px-3 text-sm font-semibold text-secondary hover:bg-canvas"
                >
                  {link.label}
                </NavLink>
              ))}
              <NavLink
                to="/dashboard"
                onClick={() => setOpen(false)}
                className="flex min-h-11 items-center rounded-control px-3 text-sm font-semibold text-brand hover:bg-brand-soft"
              >
                Reviewer workspace
              </NavLink>
            </div>
          </div>
        ) : null}
      </header>

      <main id="main">
        <Outlet />
      </main>

      <footer className="border-t border-border bg-canvas">
        <Container className="grid gap-8 py-12 md:grid-cols-[1.4fr_1fr_1fr]">
          <div>
            <Logo size={28} />
            <p className="mt-3 max-w-sm text-sm text-secondary">
              Official election information and verified corrections for every voter.
            </p>
          </div>
          <FooterLinks
            title="For voters"
            links={[
              { to: "/check", label: "Verify a claim" },
              { to: "/fact-checks", label: "Fact-checks" },
              { to: "/subscribe", label: "Get text alerts" },
              { to: "/guide", label: "How Clarion works" },
            ]}
          />
          <FooterLinks
            title="For reviewers"
            links={[
              { to: "/dashboard/verification", label: "Review and approve" },
              { to: "/dashboard/board", label: "Broadcast board" },
              { to: "/dashboard/evidence", label: "Evidence library" },
            ]}
          />
        </Container>
      </footer>
    </div>
  );
}
