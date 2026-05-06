import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Database, Layers3, ShieldCheck, Sparkles } from "lucide-react";
import SearchBar from "../components/common/SearchBar";
import KPICard from "../components/common/KPICard";
import DatasetCard from "../components/dataset/DatasetCard";
import { SkeletonCard } from "../components/common/SkeletonCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ThreeDataGlobe from "../components/common/ThreeDataGlobe";
import { listDatasets, searchDatasets, getGlobalStats } from "../services/api";
import { useUi } from "../contexts/useUi";
import type { Dataset, GlobalStats, SearchResult } from "../types/dataset";

const POPULAR_TAG_KEYS = ["finance", "fraud", "clients", "risk"] as const;
const TAG_CLASSES = [
  "bg-blue-100 text-blue-700 dark:bg-blue-500/15 dark:text-blue-200",
  "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-200",
  "bg-green-100 text-green-700 dark:bg-emerald-500/15 dark:text-emerald-200",
  "bg-yellow-100 text-yellow-700 dark:bg-amber-500/15 dark:text-amber-200",
];

export default function SearchPage() {
  const navigate = useNavigate();
  const { t } = useUi();
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [recentDatasets, setRecentDatasets] = useState<Dataset[]>([]);
  const [stats, setStats] = useState<GlobalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [datasetsRes, statsRes] = await Promise.all([
        listDatasets({ limit: 6, sort_by: "created_at", sort_desc: true }),
        getGlobalStats(),
      ]);
      setRecentDatasets(datasetsRes.items);
      setStats(statsRes);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const results = await searchDatasets(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setSearching(false);
    }
  };

  const handleTagClick = (tag: string) => {
    setQuery(tag);
    handleSearch(tag);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-[#060914] dark:text-slate-100">
      <section className="relative overflow-hidden px-4 pb-10 pt-8 sm:pb-14 sm:pt-12">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_32%),radial-gradient(circle_at_70%_0%,rgba(16,185,129,0.14),transparent_30%)] dark:bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.22),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(168,85,247,0.16),transparent_34%)]" />
        <div className="relative mx-auto grid max-w-7xl gap-6 lg:grid-cols-[1.08fr_0.92fr] lg:items-center">
          <div className="relative overflow-hidden rounded-[2rem] border border-white/70 bg-white/75 p-6 shadow-2xl shadow-slate-950/10 backdrop-blur-xl dark:border-white/10 dark:bg-white/[0.055] dark:shadow-black/30 sm:p-8 lg:p-10">
            <ThreeDataGlobe />
            <div className="relative z-10 max-w-3xl">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-sm font-bold text-blue-700 dark:border-blue-400/20 dark:bg-blue-500/10 dark:text-blue-200">
                <Sparkles className="h-4 w-4" /> {t("heroEyebrow")}
              </div>

              <h1 className="max-w-4xl text-4xl font-black tracking-tight text-slate-950 dark:text-white sm:text-5xl lg:text-6xl">
                {t("heroTitle")}
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300 sm:text-lg">
                {t("heroSubtitle")}
              </p>

              <div className="mt-8 max-w-2xl">
                <SearchBar
                  value={query}
                  onChange={setQuery}
                  onSearch={handleSearch}
                  placeholder={t("searchPlaceholder")}
                  size="large"
                  autoFocus
                />
              </div>

              <div className="mt-5 flex flex-wrap items-center gap-2">
                <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{t("popular")}</span>
                {POPULAR_TAG_KEYS.map((key, index) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleTagClick(t(key))}
                    className={`rounded-full px-3 py-1.5 text-sm font-bold transition-all hover:-translate-y-0.5 hover:shadow-md ${TAG_CLASSES[index]}`}
                  >
                    {t(key)}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <aside className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-950/5 dark:border-white/10 dark:bg-white/[0.055]">
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-600 dark:text-blue-300">
                  <Database className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Seed pack</p>
                  <p className="text-2xl font-black">78 datasets</p>
                </div>
              </div>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-950/5 dark:border-white/10 dark:bg-white/[0.055]">
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-300">
                  <ShieldCheck className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Quality/PII</p>
                  <p className="text-2xl font-black">Profiled</p>
                </div>
              </div>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-950/5 dark:border-white/10 dark:bg-white/[0.055]">
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-600 dark:text-violet-300">
                  <Layers3 className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Dashboards</p>
                  <p className="text-2xl font-black">Auto-built</p>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </section>

      {(searchResults.length > 0 || searching) && (
        <section className="mx-auto max-w-6xl px-4 py-8">
          <h2 className="mb-4 text-lg font-bold text-slate-950 dark:text-white">
            {searching ? t("searching") : `${t("searchResults")} (${searchResults.length})`}
          </h2>
          {searching ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {searchResults.map((result) => (
                <button
                  type="button"
                  key={result.dataset_id}
                  onClick={() => navigate(`/datasets/${result.dataset_id}`)}
                  className="group text-left rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-1 hover:border-blue-300 hover:shadow-xl dark:border-white/10 dark:bg-white/[0.055]"
                >
                  <h3 className="mb-1 font-bold text-slate-950 dark:text-white">{result.name}</h3>
                  {result.description && (
                    <p className="mb-3 line-clamp-2 text-sm text-slate-600 dark:text-slate-300">{result.description}</p>
                  )}
                  <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                    <span className="rounded-full bg-emerald-100 px-2 py-1 font-bold text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200">
                      {Math.round(result.relevance_score * 100)}% {t("match")}
                    </span>
                    {result.matched_columns.length > 0 && (
                      <span>{t("matched")}: {result.matched_columns.slice(0, 2).join(", ")}</span>
                    )}
                    <ArrowRight className="ml-auto h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      <section className="mx-auto max-w-6xl px-4 py-8">
        {loading ? (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="flex min-h-[120px] flex-col items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white p-6 dark:border-white/10 dark:bg-white/[0.055]">
              <LoadingSpinner size="sm" />
              <span className="text-sm text-slate-500 dark:text-slate-400">{t("loadingStats")}</span>
            </div>
            {[2, 3, 4].map((i) => (
              <div key={i} className="min-h-[120px] animate-pulse rounded-2xl border border-slate-200 bg-white p-6 dark:border-white/10 dark:bg-white/[0.055]">
                <div className="mb-4 h-4 w-1/2 rounded bg-slate-200 dark:bg-white/10" />
                <div className="h-8 w-3/4 rounded bg-slate-200 dark:bg-white/10" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <KPICard label={t("totalDatasets")} value={stats?.total_datasets ?? 0} color="blue" icon={<Database className="h-6 w-6" />} />
            <KPICard label={t("totalRows")} value={stats?.total_rows ? `${(stats.total_rows / 1000000).toFixed(1)}M` : "0"} color="green" icon={<Layers3 className="h-6 w-6" />} />
            <KPICard label={t("avgQuality")} value={`${stats?.avg_quality ?? 0}%`} color="yellow" icon={<ShieldCheck className="h-6 w-6" />} />
            <KPICard label={t("domains")} value={stats?.domain_count ?? 0} color="purple" icon={<Sparkles className="h-6 w-6" />} />
          </div>
        )}
      </section>

      <section className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <h2 className="text-2xl font-black text-slate-950 dark:text-white">{t("recentlyAdded")}</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{t("realDataBody")}</p>
          </div>
          <button
            type="button"
            onClick={() => navigate("/browse")}
            className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-4 py-2 text-sm font-bold text-white transition-all hover:-translate-y-0.5 dark:bg-white dark:text-slate-950"
          >
            {t("viewAll")} <ArrowRight className="h-4 w-4" />
          </button>
        </div>
        {loading ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => <SkeletonCard key={i} />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {recentDatasets.map((dataset) => <DatasetCard key={dataset.id} dataset={dataset} />)}
          </div>
        )}
      </section>
    </div>
  );
}
