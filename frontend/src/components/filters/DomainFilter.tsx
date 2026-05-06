interface DomainFilterProps {
  selected: string[];
  onChange: (domains: string[]) => void;
}

const DOMAINS = [
  { value: "finance", label: "Finance", icon: "💰" },
  { value: "risk", label: "Risk", icon: "⚠️" },
  { value: "marketing", label: "Marketing", icon: "📢" },
  { value: "hr", label: "HR", icon: "👥" },
  { value: "operations", label: "Operations", icon: "⚙️" },
  { value: "sales", label: "Sales", icon: "📈" },
  { value: "customer", label: "Customer", icon: "🎯" },
];

export default function DomainFilter({ selected, onChange }: DomainFilterProps) {
  const toggleDomain = (domain: string) => {
    if (selected.includes(domain)) {
      onChange(selected.filter((d) => d !== domain));
    } else {
      onChange([...selected, domain]);
    }
  };

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-3">Domain</h3>
      <div className="space-y-2">
        {DOMAINS.map((domain) => (
          <label
            key={domain.value}
            className="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              checked={selected.includes(domain.value)}
              onChange={() => toggleDomain(domain.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm">{domain.icon}</span>
            <span className="text-sm text-gray-600 group-hover:text-gray-900">
              {domain.label}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}
