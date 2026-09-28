import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">
          GSTLens
        </Link>
        <div className="flex items-center gap-4 text-sm">
          {user && (
            <>
              <span className="text-slate-400">{user.email}</span>
              <span className="px-2 py-1 rounded bg-slate-800 text-xs">
                {user.plan?.name ?? "No plan"}
              </span>
              <button
                onClick={logout}
                className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </header>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}