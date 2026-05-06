import { useState } from "react";
import DomainFilter from "./DomainFilter";
import QualitySlider from "./QualitySlider";
import FormatFilter from "./FormatFilter";
import PIIFilter from "./PIIFilter";

export interface FilterState {
  domains: string[];
  qualityRange: [number, number];
  formats: string[];
  piiFilter: "all" | "has_pii" | "no_pii";
}

interface FilterSidebarProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  onReset: () => void;
}

export default function FilterSidebar({
  filters,
  onChange,
  onReset,
}: FilterSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const hasActiveFilters =
    filters.domains.length > 0 ||
    filters.formats.length > 0 ||
    filters.qualityRange[0] > 0 ||
    filters.qualityRange[1] < 100 ||
    filters.piiFilter !== "all";

  return (
    <aside
      className={`shrink-0 rounded-2xl border border-slate-200 bg-white/90 shadow-sm transition-all dark:border-white/10 dark:bg-white/[0.055] ${
        isCollapsed ? "hidden w-12 md:block" : "w-full md:w-64"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 p-4 dark:border-white/10">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-slate-950 dark:text-white">Filters</h2>
            {hasActiveFilters && (
              <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                Active
              </span>
            )}
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="rounded p-1 transition-colors hover:bg-slate-100 dark:hover:bg-white/10"
          title={isCollapsed ? "Expand" : "Collapse"}
        >
          <svg
            className={`h-5 w-5 text-slate-500 transition-transform dark:text-slate-400 ${
              isCollapsed ? "rotate-180" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
            />
          </svg>
        </button>
      </div>

      {!isCollapsed && (
        <div className="space-y-6 p-4">
          {/* Domain Filter */}
          <DomainFilter
            selected={filters.domains}
            onChange={(domains) => onChange({ ...filters, domains })}
          />

          {/* Quality Slider */}
          <QualitySlider
            value={filters.qualityRange}
            onChange={(qualityRange) => onChange({ ...filters, qualityRange })}
          />

          {/* Format Filter */}
          <FormatFilter
            selected={filters.formats}
            onChange={(formats) => onChange({ ...filters, formats })}
          />

          {/* PII Filter */}
          <PIIFilter
            value={filters.piiFilter}
            onChange={(piiFilter) => onChange({ ...filters, piiFilter })}
          />

          {/* Reset Button */}
          {hasActiveFilters && (
            <button
              onClick={onReset}
              className="w-full rounded-lg py-2 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-white/10 dark:hover:text-white"
            >
              Reset all filters
            </button>
          )}
        </div>
      )}
    </aside>
  );
}
