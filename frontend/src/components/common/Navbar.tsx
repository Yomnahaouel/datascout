import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { Moon, Sun, Upload, Menu, X, Search, Grid2X2, DatabaseZap } from "lucide-react";
import { useUi } from "../../contexts/useUi";

interface NavbarProps {
  onUploadClick: () => void;
}

export default function Navbar({ onUploadClick }: NavbarProps) {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const { theme, locale, setLocale, toggleTheme, t } = useUi();

  const isActive = (path: string) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  const navLinkClass = (path: string) =>
    `inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition-all ${
      isActive(path)
        ? "bg-blue-600 text-white shadow-lg shadow-blue-500/25"
        : "text-slate-600 hover:bg-white/80 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-white/10 dark:hover:text-white"
    }`;

  const mobileLinkClass = (path: string) =>
    `block rounded-2xl px-4 py-3 text-sm font-semibold ${
      isActive(path)
        ? "bg-blue-600 text-white"
        : "text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-white/10"
    }`;

  return (
    <nav className="fixed inset-x-0 top-0 z-50 border-b border-white/30 bg-white/80 shadow-sm shadow-slate-950/5 backdrop-blur-xl dark:border-white/10 dark:bg-[#080b16]/80">
      <div className="mx-auto max-w-7xl px-3 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-3">
          <Link to="/" className="flex min-w-0 items-center gap-2">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-cyan-400 to-emerald-400 text-white shadow-lg shadow-blue-500/25">
              <DatabaseZap className="h-5 w-5" />
            </div>
            <span className="truncate text-xl font-black tracking-tight text-slate-950 dark:text-white">
              DataScout
            </span>
          </Link>

          <div className="hidden items-center rounded-full border border-slate-200/80 bg-slate-100/70 p-1 dark:border-white/10 dark:bg-white/5 md:flex">
            <Link to="/" className={navLinkClass("/")}> <Search className="h-4 w-4" /> {t("search")}</Link>
            <Link to="/browse" className={navLinkClass("/browse")}> <Grid2X2 className="h-4 w-4" /> {t("browse")}</Link>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <div className="hidden rounded-full border border-slate-200 bg-white p-1 dark:border-white/10 dark:bg-white/5 sm:flex">
              {(["en", "fr"] as const).map((code) => (
                <button
                  key={code}
                  type="button"
                  onClick={() => setLocale(code)}
                  className={`rounded-full px-3 py-1.5 text-xs font-bold uppercase transition-all ${
                    locale === code
                      ? "bg-slate-950 text-white dark:bg-white dark:text-slate-950"
                      : "text-slate-500 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
                  }`}
                >
                  {code}
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={toggleTheme}
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition-all hover:-translate-y-0.5 hover:shadow-lg dark:border-white/10 dark:bg-white/5 dark:text-slate-100"
              aria-label={theme === "dark" ? t("themeLight") : t("themeDark")}
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>

            <button
              type="button"
              onClick={onUploadClick}
              className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-500/25 transition-all hover:-translate-y-0.5 hover:bg-blue-500"
            >
              <Upload className="h-4 w-4" />
              <span className="hidden sm:inline">{t("upload")}</span>
            </button>

            <button
              type="button"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 dark:border-white/10 dark:bg-white/5 dark:text-slate-100 md:hidden"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Toggle menu"
            >
              {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="space-y-2 border-t border-slate-200/70 py-3 dark:border-white/10 md:hidden">
            <Link to="/" className={mobileLinkClass("/")} onClick={() => setMenuOpen(false)}>
              {t("search")}
            </Link>
            <Link to="/browse" className={mobileLinkClass("/browse")} onClick={() => setMenuOpen(false)}>
              {t("browse")}
            </Link>
            <div className="flex gap-2 pt-2 sm:hidden">
              {(["en", "fr"] as const).map((code) => (
                <button
                  key={code}
                  type="button"
                  onClick={() => setLocale(code)}
                  className={`flex-1 rounded-xl px-3 py-2 text-xs font-bold uppercase ${
                    locale === code
                      ? "bg-slate-950 text-white dark:bg-white dark:text-slate-950"
                      : "bg-slate-100 text-slate-700 dark:bg-white/10 dark:text-slate-200"
                  }`}
                >
                  {code}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
