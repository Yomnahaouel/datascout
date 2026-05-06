interface FormatFilterProps {
  selected: string[];
  onChange: (formats: string[]) => void;
}

const FORMATS = [
  { value: "csv", label: "CSV", icon: "📊" },
  { value: "excel", label: "Excel", icon: "📗" },
  { value: "json", label: "JSON", icon: "📋" },
  { value: "parquet", label: "Parquet", icon: "⚡" },
  { value: "tsv", label: "TSV", icon: "📊" },
];

export default function FormatFilter({ selected, onChange }: FormatFilterProps) {
  const toggleFormat = (format: string) => {
    if (selected.includes(format)) {
      onChange(selected.filter((f) => f !== format));
    } else {
      onChange([...selected, format]);
    }
  };

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-3">File Format</h3>
      <div className="space-y-2">
        {FORMATS.map((format) => (
          <label
            key={format.value}
            className="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              checked={selected.includes(format.value)}
              onChange={() => toggleFormat(format.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm">{format.icon}</span>
            <span className="text-sm text-gray-600 group-hover:text-gray-900">
              {format.label}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}
