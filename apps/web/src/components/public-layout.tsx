import { useState } from "react";
import { NavLink, Outlet } from "react-router";
import { Logo } from "./brand/logo";
import { Icon } from "./icons";
import { Button } from "./ui/button";

const navigation = [
  { to: "/information", label: "Election information" },
  { to: "/fact-checks", label: "Fact-checks" },
  { to: "/guide", label: "How it works" },
] as const;

export function PublicLayout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen bg-white text-foreground">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-control focus:bg-white focus:px-4 focus:py-2"
      >
        Skip to content
      </a>
      <header className="sticky top-0 z-40 border-b border-border bg-white/95 backdrop-blur">
        <nav
          className="mx-auto flex h-[72px] max-w-[1200px] items-center justify-between px-5 sm:px-8"
          aria-label="Primary navigation"
        >
          <NavLink
            to="/"
            className="flex min-h-11 items-center gap-2.5"
            onClick={() => setOpen(false)}
          >
            <Logo />
          </NavLink>

          <div className="hidden items-center gap-7 lg:flex">
            {navigation.map((link) => (
              <NavLink
                key={link.label}
                to={link.to}
                className="flex min-h-11 items-center text-sm font-medium text-secondary hover:text-brand"
              >
                {link.label}
              </NavLink>
            ))}
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <Button as="link" to="/dashboard" variant="ghost" icon="user">
              Reviewer workspace
            </Button>
            <Button as="link" to="/check" variant="primary">
              Verify a claim
            </Button>
          </div>

          <button
            type="button"
            className="grid size-11 place-items-center rounded-md border border-border lg:hidden"
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
            className="border-t border-border bg-white px-5 py-4 lg:hidden"
          >
            <div className="mx-auto grid max-w-[1200px] gap-1">
              {navigation.map((link) => (
                <NavLink
                  key={link.label}
                  to={link.to}
                  onClick={() => setOpen(false)}
                  className="flex min-h-11 items-center rounded-md px-3 text-sm font-semibold text-secondary hover:bg-surface"
                >
                  {link.label}
                </NavLink>
              ))}
              <NavLink
                to="/dashboard"
                onClick={() => setOpen(false)}
                className="flex min-h-11 items-center rounded-md px-3 text-sm font-semibold text-brand hover:bg-brand-soft"
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

      <footer className="border-t border-border bg-surface">
        <div className="mx-auto grid max-w-[1200px] gap-8 px-5 py-10 sm:px-8 md:grid-cols-[1.4fr_1fr_1fr]">
          <div>
            <Logo size={28} />
            <p className="mt-3 max-w-sm text-sm leading-6 text-muted">
              Official election information and verified corrections for every voter.
            </p>
          </div>
          <div className="grid gap-2 text-sm text-secondary">
            <span className="font-semibold text-foreground">For voters</span>
            <NavLink to="/check" className="hover:text-brand">
              Verify a claim
            </NavLink>
            <NavLink to="/fact-checks" className="hover:text-brand">
              Fact-checks
            </NavLink>
            <NavLink to="/guide" className="hover:text-brand">
              How Clarion works
            </NavLink>
          </div>
          <div className="grid gap-2 text-sm text-secondary">
            <span className="font-semibold text-foreground">For reviewers</span>
            <NavLink to="/dashboard/verification" className="hover:text-brand">
              Review and approve
            </NavLink>
            <NavLink to="/dashboard/board" className="hover:text-brand">
              Broadcast board
            </NavLink>
            <NavLink to="/dashboard/evidence" className="hover:text-brand">
              Evidence library
            </NavLink>
          </div>
        </div>
      </footer>
    </div>
  );
}
