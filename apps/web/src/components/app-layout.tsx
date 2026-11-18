import { NavLink, Outlet } from "react-router";

const links = [
  { to: "/", label: "Check a claim" },
  { to: "/review", label: "Review queue" },
  { to: "/board", label: "Broadcast board" },
] as const;

export function AppLayout() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <header className="border-b border-slate-200">
        <nav className="mx-auto flex max-w-5xl items-center gap-6 px-6 py-4">
          <span className="text-lg font-bold text-brand">Clarion</span>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end
              className={({ isActive }) =>
                isActive ? "font-semibold text-brand" : "text-muted hover:text-slate-900"
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
