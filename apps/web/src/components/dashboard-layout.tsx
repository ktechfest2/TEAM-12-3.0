import { NavLink, Outlet } from "react-router";
import { clearSession, useSession } from "../lib/auth/session";
import { Logo } from "./brand/logo";
import { Icon, type IconName } from "./icons";
import { Container } from "./ui/container";

const dashboardLinks = [
  { to: "/dashboard", label: "Overview", icon: "dashboard", end: true },
  { to: "/dashboard/claims", label: "Claims", icon: "messages", end: false },
  { to: "/dashboard/verification", label: "Verification", icon: "workflow", end: false },
  { to: "/dashboard/evidence", label: "Evidence", icon: "archive", end: false },
  { to: "/dashboard/board", label: "Broadcast", icon: "broadcast", end: false },
] as const satisfies readonly { to: string; label: string; icon: IconName; end: boolean }[];

function ReviewerChip({ compact = false }: { compact?: boolean }) {
  const session = useSession();
  if (!session) {
    return <span className="text-sm text-muted">Reviewer workspace</span>;
  }
  return (
    <div className="flex min-w-0 items-center gap-2">
      <span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand-soft text-brand">
        <Icon name="user" size={16} />
      </span>
      {compact ? null : (
        <span className="min-w-0 flex-1 truncate text-sm font-semibold text-foreground">
          {session.reviewerName}
        </span>
      )}
      <button
        type="button"
        onClick={clearSession}
        className="grid size-10 shrink-0 place-items-center rounded-control text-muted hover:bg-canvas hover:text-foreground"
      >
        <Icon name="logout" size={18} label="Sign out" />
      </button>
    </div>
  );
}

export function DashboardLayout() {
  return (
    <div className="min-h-screen bg-canvas text-foreground lg:grid lg:grid-cols-[232px_minmax(0,1fr)]">
      <aside className="z-20 lg:sticky lg:top-0 border-b border-border bg-surface lg:flex lg:h-screen lg:flex-col lg:border-r lg:border-b-0">
        <div className="flex h-14 items-center justify-between gap-3 px-4 lg:h-16 lg:px-6">
          <NavLink to="/" className="flex min-h-10 items-center">
            <Logo />
          </NavLink>
          <div className="lg:hidden">
            <ReviewerChip compact />
          </div>
        </div>
        <nav
          className="grid grid-cols-5 border-t border-border lg:mb-0 lg:grid-cols-1 lg:gap-1 lg:border-t-0 lg:px-3 lg:py-2"
          aria-label="Dashboard navigation"
        >
          {dashboardLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `flex min-h-14 min-w-0 flex-col items-center justify-center gap-1 border-t-2 px-1 text-xs font-semibold transition-colors lg:min-h-11 lg:flex-row lg:justify-start lg:gap-3 lg:rounded-control lg:border-t-0 lg:px-3 lg:text-sm ${
                  isActive
                    ? "border-brand text-brand lg:bg-brand-soft"
                    : "border-transparent text-secondary hover:text-foreground lg:hover:bg-canvas"
                }`
              }
            >
              <Icon name={link.icon} size={18} />
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto hidden border-t border-border p-3 lg:block">
          <ReviewerChip />
        </div>
      </aside>
      <main className="min-w-0">
        <Container width="workspace" className="py-6 lg:py-8">
          <Outlet />
        </Container>
      </main>
    </div>
  );
}
