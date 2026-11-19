import { NavLink, Outlet } from "react-router";
import { Logo } from "./brand/logo";
import { Icon, type IconName } from "./icons";

const links: readonly { to: string; label: string; icon: IconName }[] = [
  { to: "/", label: "Check a claim", icon: "search" },
  { to: "/review", label: "Review queue", icon: "shieldCheck" },
  { to: "/board", label: "Broadcast board", icon: "broadcast" },
];

function Shell({ withNav }: { withNav: boolean }) {
  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-10 focus:rounded-control focus:bg-surface focus:px-4 focus:py-2"
      >
        Skip to content
      </a>
      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3 sm:px-6">
          <NavLink to="/" aria-label="Clarion home" className="rounded-control">
            <Logo />
          </NavLink>
          {withNav ? (
            <nav aria-label="Main" className="flex flex-wrap gap-1">
              {links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end
                  className={({ isActive }) =>
                    `inline-flex min-h-10 items-center gap-2 rounded-control px-3 text-sm font-semibold transition-colors ${
                      isActive
                        ? "bg-brand-50 text-brand"
                        : "text-muted hover:bg-sunken hover:text-ink"
                    }`
                  }
                >
                  <Icon name={link.icon} size={18} />
                  {link.label}
                </NavLink>
              ))}
            </nav>
          ) : null}
        </div>
      </header>
      <main id="main" className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-6 sm:py-12">
        <Outlet />
      </main>
      <footer className="border-t border-line">
        <p className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-2 gap-y-1 px-4 py-5 text-sm text-muted sm:px-6">
          <Icon name="shieldCheck" size={16} className="text-brand" />
          <span className="font-semibold text-brand">Clarion</span>
          <span>Every correction cites an official source and is approved by a person.</span>
        </p>
      </footer>
    </div>
  );
}

export function AppLayout() {
  return <Shell withNav />;
}

/** Voters opening a shared link see the brand and the correction, not reviewer tools. */
export function PublicLayout() {
  return <Shell withNav={false} />;
}
