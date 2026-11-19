import { NavLink, Outlet } from "react-router";
import { useSession } from "../lib/auth/session";
import { Logo } from "./brand/logo";
import { Icon, type IconName } from "./icons";

const dashboardLinks = [
  { to: "/dashboard", label: "Overview", icon: "dashboard", end: true },
  { to: "/dashboard/claims", label: "Claims", icon: "messages", end: false },
  { to: "/dashboard/verification", label: "Verification", icon: "workflow", end: false },
  { to: "/dashboard/evidence", label: "Evidence library", icon: "archive", end: false },
  { to: "/dashboard/board", label: "Broadcast board", icon: "broadcast", end: false },
] as const satisfies readonly { to: string; label: string; icon: IconName; end: boolean }[];

export function DashboardLayout() {
  const session = useSession();

  return (
    <div className="min-h-screen bg-surface text-foreground lg:grid lg:grid-cols-[240px_1fr]">
      <aside className="border-b border-border bg-white lg:min-h-screen lg:border-r lg:border-b-0">
        <div className="flex h-[72px] items-center border-b border-border px-5 lg:px-6">
          <NavLink to="/" className="flex items-center gap-2.5 font-bold">
            <Logo />
          </NavLink>
        </div>
        <nav
          className="flex gap-2 overflow-x-auto p-3 lg:grid lg:overflow-visible"
          aria-label="Dashboard navigation"
        >
          {dashboardLinks.map((link) => {
            return (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  `flex min-h-11 shrink-0 items-center gap-3 rounded-[10px] px-3 text-sm font-medium ${
                    isActive ? "bg-brand-soft text-brand" : "text-secondary hover:bg-surface"
                  }`
                }
              >
                <Icon name={link.icon} size={18} />
                {link.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <div className="min-w-0">
        <header className="hidden h-[72px] items-center justify-end border-b border-border bg-white px-8 lg:flex">
          {session ? (
            <span className="text-sm font-medium text-secondary">{session.reviewerName}</span>
          ) : (
            <span className="text-sm text-muted">Reviewer workspace</span>
          )}
        </header>
        <main className="mx-auto max-w-[1120px] p-5 sm:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
