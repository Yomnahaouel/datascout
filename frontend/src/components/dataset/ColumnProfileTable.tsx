import { useState, useMemo } from "react";
import type { ColumnProfile } from "../../types/dataset";

interface ColumnProfileTableProps {
  profiles: ColumnProfile[];
}

type SortKey = "column_name" | "inferred_type" | "missing_pct" | "unique_count" | "mean";
type SortDir = "asc" | "desc";

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  return (
    <svg
      className={`w-4 h-4 ${active ? "text-blue-600" : "text-gray-400"}`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d={dir === "asc" ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"}
      />
    </svg>
  );
}

export default function ColumnProfileTable({ profiles }: ColumnProfileTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("column_name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [filter, setFilter] = useState("");

  const sortedProfiles = useMemo(() => {
    let filtered = profiles;
    if (filter) {
      const lower = filter.toLowerCase();
      filtered = profiles.filter(
        (p) =>
          p.column_name.toLowerCase().includes(lower) ||
          p.inferred_type.toLowerCase().includes(lower)
      );
    }

    return [...filtered].sort((a, b) => {
      let aVal: string | number = a[sortKey] ?? "";
      let bVal: string | number = b[sortKey] ?? "";

      if (typeof aVal === "string") aVal = aVal.toLowerCase();
      if (typeof bVal === "string") bVal = bVal.toLowerCase();

      if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
  }, [profiles, sortKey, sortDir, filter]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      integer: "bg-blue-100 text-blue-700",
      decimal: "bg-cyan-100 text-cyan-700",
      text: "bg-gray-100 text-gray-700",
      datetime: "bg-purple-100 text-purple-700",
      boolean: "bg-green-100 text-green-700",
      email: "bg-amber-100 text-amber-700",
      identifier: "bg-orange-100 text-orange-700",
    };
    return colors[type] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Column Profiles ({profiles.length})
        </h2>
        <input
          type="text"
          placeholder="Filter columns..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th
                className="px-4 py-3 text-left cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort("column_name")}
              >
                <div className="flex items-center gap-1">
                  Column
                  <SortIcon active={sortKey === "column_name"} dir={sortDir} />
                </div>
              </th>
              <th
                className="px-4 py-3 text-left cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort("inferred_type")}
              >
                <div className="flex items-center gap-1">
                  Type
                  <SortIcon active={sortKey === "inferred_type"} dir={sortDir} />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort("missing_pct")}
              >
                <div className="flex items-center justify-end gap-1">
                  Missing %
                  <SortIcon active={sortKey === "missing_pct"} dir={sortDir} />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort("unique_count")}
              >
                <div className="flex items-center justify-end gap-1">
                  Unique
                  <SortIcon active={sortKey === "unique_count"} dir={sortDir} />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort("mean")}
              >
                <div className="flex items-center justify-end gap-1">
                  Mean
                  <SortIcon active={sortKey === "mean"} dir={sortDir} />
                </div>
              </th>
              <th className="px-4 py-3 text-left">Sample Values</th>
              <th className="px-4 py-3 text-center">PII</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedProfiles.map((profile) => (
              <tr key={profile.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <span className="font-medium text-gray-900">{profile.column_name}</span>
                  <span className="ml-2 text-xs text-gray-400">({profile.raw_dtype})</span>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${getTypeColor(profile.inferred_type)}`}
                  >
                    {profile.inferred_type}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={
                      profile.missing_pct > 10
                        ? "text-red-600"
                        : profile.missing_pct > 0
                          ? "text-yellow-600"
                          : "text-gray-600"
                    }
                  >
                    {profile.missing_pct.toFixed(1)}%
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-gray-600">
                  {profile.unique_count.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right text-gray-600">
                  {profile.mean !== null ? profile.mean.toFixed(2) : "—"}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {profile.sample_values.slice(0, 3).map((val, i) => (
                      <span
                        key={i}
                        className="px-1.5 py-0.5 bg-gray-100 rounded text-xs text-gray-600 truncate max-w-[80px]"
                        title={String(val)}
                      >
                        {String(val)}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  {profile.is_pii ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {profile.pii_type || "PII"}
                    </span>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sortedProfiles.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          No columns match your filter.
        </div>
      )}
    </div>
  );
}
