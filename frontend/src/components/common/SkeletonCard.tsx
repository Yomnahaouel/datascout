interface SkeletonCardProps {
  lines?: number;
  showImage?: boolean;
}

export function SkeletonCard({ lines = 3, showImage = false }: SkeletonCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
      {showImage && (
        <div className="w-full h-32 bg-gray-200 rounded-lg mb-4" />
      )}
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        {Array.from({ length: lines - 1 }).map((_, i) => (
          <div
            key={i}
            className="h-3 bg-gray-200 rounded"
            style={{ width: `${60 + (i % 3) * 10}%` }}
          />
        ))}
      </div>
      <div className="flex gap-2 mt-4">
        <div className="h-6 w-16 bg-gray-200 rounded-full" />
        <div className="h-6 w-20 bg-gray-200 rounded-full" />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden animate-pulse">
      <div className="border-b border-gray-200 bg-gray-50 p-4">
        <div className="flex gap-4">
          {Array.from({ length: cols }).map((_, i) => (
            <div key={i} className="h-4 bg-gray-200 rounded flex-1" />
          ))}
        </div>
      </div>
      <div className="divide-y divide-gray-200">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="p-4 flex gap-4">
            {Array.from({ length: cols }).map((_, colIndex) => (
              <div
                key={colIndex}
                className="h-4 bg-gray-200 rounded flex-1"
                style={{ opacity: 0.5 + (rowIndex + colIndex) % 3 * 0.17 }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
