import { useEffect, useState, useCallback } from "react";
import SearchBar from "../components/common/SearchBar";
import FilterSidebar, { type FilterState } from "../components/filters/FilterSidebar";
import DatasetCardExpanded from "../components/dataset/DatasetCardExpanded";
import { SkeletonCard } from "../components/common/SkeletonCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
// LoadingSpinner available if needed
import { listDatasets } from "../services/api";
import { useUi } from "../contexts/useUi";
import type { Dataset } from "../types/dataset";

const DEFAULT_FILTERS: FilterState = {
  domains: [],
  qualityRange: [0, 100],
  formats: [],
  piiFilter: "all",
};

export default function BrowsePage() {
  const { t } = useUi();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [page, setPage] = useState(0);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortDesc, setSortDesc] = useState(true);

  const pageSize = 12;

  const loadDatasets = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        skip: page * pageSize,
        limit: pageSize,
        sort_by: sortBy,
        sort_desc: sortDesc,
      };

      if (searchQuery) {
        params.search_name = searchQuery;
      }

      if (filters.formats.length === 1) {
        params.format = filters.formats[0];
      }

      const response = await listDatasets(params as Parameters<typeof listDatasets>[0]);

      // Client-side filtering for quality range (ideally should be server-side)
      let filteredItems = response.items;

      if (filters.qualityRange[0] > 0 || filters.qualityRange[1] < 100) {
        filteredItems = filteredItems.filter((d) => {
          if (d.quality_score === null) return false;
          return (
            d.quality_score >= filters.qualityRange[0] &&
            d.quality_score <= filters.qualityRange[1]
          );
        });
      }

      setDatasets(filteredItems);
      setTotal(response.total);
    } catch (err) {
      console.error("Failed to load datasets:", err);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, sortBy, sortDesc, searchQuery, filters]);

  useEffect(() => {
    loadDatasets();
  }, [loadDatasets]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setPage(0);
  };

  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters);
    setPage(0);
  };

  const handleResetFilters = () => {
    setFilters(DEFAULT_FILTERS);
    setPage(0);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#060914]">
      {/* Header */}
      <div className="sticky top-16 z-40 border-b border-slate-200 bg-white/85 backdrop-blur-xl dark:border-white/10 dark:bg-[#080b16]/85">
        <div className="mx-auto max-w-7xl px-4 py-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
            <div className="w-full flex-1 sm:max-w-xl">
              <SearchBar
                value={searchQuery}
                onChange={setSearchQuery}
                onSearch={handleSearch}
                placeholder={t("searchPlaceholder")}
                size="small"
              />
            </div>
            <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-white/10 dark:bg-slate-950/70 dark:text-white"
              >
                <option value="created_at">Date Added</option>
                <option value="name">Name</option>
                <option value="quality_score">Quality</option>
                <option value="row_count">Size</option>
              </select>
              <button
                onClick={() => setSortDesc(!sortDesc)}
                className="rounded-xl border border-slate-300 p-2 hover:bg-slate-100 dark:border-white/10 dark:text-white dark:hover:bg-white/10"
                title={sortDesc ? "Descending" : "Ascending"}
              >
                <svg
                  className={`w-4 h-4 transition-transform ${sortDesc ? "" : "rotate-180"}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-6">
        <div className="flex flex-col gap-6 md:flex-row">
          {/* Sidebar */}
          <FilterSidebar
            filters={filters}
            onChange={handleFilterChange}
            onReset={handleResetFilters}
          />

          {/* Dataset Grid */}
          <div className="min-w-0 flex-1">
            {/* Results count */}
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-slate-600 dark:text-slate-300">
                {loading ? (
                  <span className="inline-flex items-center gap-2">
                    <LoadingSpinner size="sm" />
                    Loading datasets...
                  </span>
                ) : (
                  <>
                    Showing{" "}
                    <span className="font-medium">
                      {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)}
                    </span>{" "}
                    of <span className="font-medium">{total}</span> datasets
                  </>
                )}
              </p>
            </div>

            {/* Grid */}
            {loading ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <SkeletonCard key={i} lines={4} />
                ))}
              </div>
            ) : datasets.length === 0 ? (
              <div className="rounded-2xl border border-slate-200 bg-white py-12 text-center dark:border-white/10 dark:bg-white/[0.055]">
                <svg
                  className="w-16 h-16 text-gray-300 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-1">No datasets found</h3>
                <p className="text-gray-500">Try adjusting your filters or search query</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {datasets.map((dataset) => (
                  <DatasetCardExpanded key={dataset.id} dataset={dataset} tags={dataset.tags ?? []} />
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="rounded-xl border border-slate-300 px-3 py-2 text-sm hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-white/10 dark:text-white dark:hover:bg-white/10"
                >
                  Previous
                </button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                    let pageNum: number;
                    if (totalPages <= 5) {
                      pageNum = i;
                    } else if (page < 3) {
                      pageNum = i;
                    } else if (page > totalPages - 4) {
                      pageNum = totalPages - 5 + i;
                    } else {
                      pageNum = page - 2 + i;
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`w-10 h-10 text-sm rounded-lg transition-colors ${
                          page === pageNum
                            ? "bg-blue-600 text-white"
                            : "text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-white/10"
                        }`}
                      >
                        {pageNum + 1}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page === totalPages - 1}
                  className="rounded-xl border border-slate-300 px-3 py-2 text-sm hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-white/10 dark:text-white dark:hover:bg-white/10"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
