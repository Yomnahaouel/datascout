import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { dictionaries, UiContext } from "./ui-context";
import type { Locale, Theme, UiContextValue } from "./ui-context";

const getInitialTheme = (): Theme => {
  const stored = localStorage.getItem("datascout-theme") as Theme | null;
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

const getInitialLocale = (): Locale => {
  const stored = localStorage.getItem("datascout-locale") as Locale | null;
  return stored === "fr" ? "fr" : "en";
};

export function UiProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const [locale, setLocaleState] = useState<Locale>(getInitialLocale);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.documentElement.style.colorScheme = theme;
    localStorage.setItem("datascout-theme", theme);
  }, [theme]);

  useEffect(() => {
    document.documentElement.lang = locale;
    localStorage.setItem("datascout-locale", locale);
  }, [locale]);

  const value = useMemo<UiContextValue>(
    () => ({
      theme,
      locale,
      setLocale: setLocaleState,
      toggleTheme: () => setTheme((current) => (current === "dark" ? "light" : "dark")),
      t: (key: string) => dictionaries[locale][key] ?? key,
    }),
    [theme, locale],
  );

  return <UiContext.Provider value={value}>{children}</UiContext.Provider>;
}
