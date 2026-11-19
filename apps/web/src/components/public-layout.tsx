import { Menu, Search, ShieldCheck, X } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router";
import { Button } from "./ui/button";

const navigation = [
  { to: "/check", label: "Verify a claim" },
  { to: "/information", label: "Election information" },
  { to: "/fact-checks", label: "Fact-checks" },
] as const;

export function PublicLayout() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white text-slate-900">
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
            <span className="grid size-9 place-items-center rounded-[10px] bg-brand text-white">
              <ShieldCheck size={20} aria-hidden="true" />
            </span>
            <span className="text-xl font-bold tracking-tight">Clarion</span>
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
            <button
              type="button"
              className="grid size-11 place-items-center rounded-md text-secondary hover:bg-surface"
              aria-label="Search"
              onClick={() => navigate("/information")}
            >
              <Search size={20} aria-hidden="true" />
            </button>
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
            {open ? <X size={21} /> : <Menu size={21} />}
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
            </div>
          </div>
        ) : null}
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="border-t border-border bg-surface">
        <div className="mx-auto grid max-w-[1200px] gap-8 px-5 py-10 sm:px-8 md:grid-cols-3">
          <div>
            <div className="flex items-center gap-2 font-bold">
              <ShieldCheck size={18} className="text-brand" /> Clarion
            </div>
            <p className="mt-3 max-w-sm text-sm leading-6 text-muted">
              Official election information and verified corrections for every voter.
            </p>
          </div>
          <div className="grid gap-2 text-sm text-secondary">
            <span className="font-semibold text-foreground">About</span>
            <NavLink to="/" className="hover:text-brand">
              How Clarion works
            </NavLink>
            <NavLink to="/" className="hover:text-brand">
              Source directory
            </NavLink>
          </div>
          <div className="grid gap-2 text-sm text-secondary">
            <span className="font-semibold text-foreground">Support</span>
            <NavLink to="/" className="hover:text-brand">
              Verification guide
            </NavLink>
            <NavLink to="/" className="hover:text-brand">
              Privacy and legal
            </NavLink>
          </div>
        </div>
      </footer>
    </div>
  );
}
