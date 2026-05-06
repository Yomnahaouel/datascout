import { useState, useCallback } from "react";
import { Search, X } from "lucide-react";

interface SearchBarProps {
  value?: string;
  onChange?: (value: string) => void;
  onSearch?: (query: string) => void;
  placeholder?: string;
  size?: "large" | "small";
  autoFocus?: boolean;
}

export default function SearchBar({
  value = "",
  onChange,
  onSearch,
  placeholder = "Search datasets...",
  size = "large",
  autoFocus = false,
}: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value);
  const currentValue = onChange ? value : localValue;

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      if (onChange) onChange(newValue);
      else setLocalValue(newValue);
    },
    [onChange],
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      onSearch?.(currentValue);
    },
    [currentValue, onSearch],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") onSearch?.(currentValue);
    },
    [currentValue, onSearch],
  );

  const sizeClasses = {
    large: "h-14 rounded-2xl px-5 text-base shadow-xl shadow-slate-950/10 sm:h-16 sm:text-lg",
    small: "h-11 rounded-xl px-4 text-sm shadow-sm",
  };

  const iconSizeClasses = {
    large: "left-4 h-5 w-5 sm:left-5 sm:h-6 sm:w-6",
    small: "left-3 h-4 w-4",
  };

  const inputPaddingClasses = {
    large: "pl-12 pr-12 sm:pl-14",
    small: "pl-10 pr-10",
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <Search className={`absolute top-1/2 -translate-y-1/2 text-slate-400 ${iconSizeClasses[size]}`} />
      <input
        type="text"
        value={currentValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className={`w-full border border-slate-200/80 bg-white/95 text-slate-950 outline-none transition-all placeholder:text-slate-400 focus:border-blue-400 focus:ring-4 focus:ring-blue-500/15 dark:border-white/10 dark:bg-slate-950/70 dark:text-white dark:placeholder:text-slate-500 ${sizeClasses[size]} ${inputPaddingClasses[size]}`}
      />
      {currentValue && (
        <button
          type="button"
          onClick={() => {
            if (onChange) onChange("");
            else setLocalValue("");
          }}
          className="absolute right-4 top-1/2 inline-flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-white/10 dark:hover:text-white"
          aria-label="Clear search"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </form>
  );
}
