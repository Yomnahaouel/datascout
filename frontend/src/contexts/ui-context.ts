import { createContext } from "react";

type Theme = "light" | "dark";
type Locale = "en" | "fr";

type Dictionary = Record<string, string>;

export const dictionaries: Record<Locale, Dictionary> = {
  en: {
    search: "Search",
    browse: "Browse",
    upload: "Upload",
    themeDark: "Dark",
    themeLight: "Light",
    heroEyebrow: "AI-ready data catalog",
    heroTitle: "Scout every dataset before it hits production.",
    heroSubtitle:
      "Search, profile, score, and visualize banking data with clean lineage and risk signals.",
    searchPlaceholder: "Search datasets by name, content, column, or domain...",
    popular: "Popular:",
    finance: "Finance",
    fraud: "Fraud",
    clients: "Clients",
    risk: "Risk",
    searchResults: "Search Results",
    searching: "Searching...",
    match: "match",
    matched: "Matched",
    totalDatasets: "Total Datasets",
    totalRows: "Total Rows",
    avgQuality: "Avg Quality",
    domains: "Domains",
    loadingStats: "Loading stats...",
    recentlyAdded: "Recently Added",
    viewAll: "View all",
    realDataTitle: "Data reality check",
    realDataBody:
      "Current seed pack: 78 generated banking datasets. Missing for production: live connectors, provenance, RBAC, audit logs, dataset freshness, and verified PII policy flows.",
  },
  fr: {
    search: "Rechercher",
    browse: "Explorer",
    upload: "Importer",
    themeDark: "Sombre",
    themeLight: "Clair",
    heroEyebrow: "Catalogue de données prêt pour l’IA",
    heroTitle: "Analyse chaque dataset avant la production.",
    heroSubtitle:
      "Recherche, profilage, scoring et visualisation des données bancaires avec traçabilité et signaux de risque.",
    searchPlaceholder: "Rechercher par nom, contenu, colonne ou domaine...",
    popular: "Populaire :",
    finance: "Finance",
    fraud: "Fraude",
    clients: "Clients",
    risk: "Risque",
    searchResults: "Résultats",
    searching: "Recherche...",
    match: "correspondance",
    matched: "Colonnes",
    totalDatasets: "Datasets",
    totalRows: "Lignes",
    avgQuality: "Qualité moy.",
    domains: "Domaines",
    loadingStats: "Chargement...",
    recentlyAdded: "Ajouts récents",
    viewAll: "Tout voir",
    realDataTitle: "État des données",
    realDataBody:
      "Seed actuel : 78 datasets bancaires générés. Manque pour la prod : connecteurs live, provenance, RBAC, journaux d’audit, fraîcheur des datasets et workflows PII vérifiés.",
  },
};

export interface UiContextValue {
  theme: Theme;
  locale: Locale;
  setLocale: (locale: Locale) => void;
  toggleTheme: () => void;
  t: (key: string) => string;
}

export type { Theme, Locale };
export const UiContext = createContext<UiContextValue | null>(null);
