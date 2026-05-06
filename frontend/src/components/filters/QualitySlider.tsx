import { useState, useEffect } from "react";

interface QualitySliderProps {
  value: [number, number];
  onChange: (range: [number, number]) => void;
}

export default function QualitySlider({ value, onChange }: QualitySliderProps) {
  const [localMin, setLocalMin] = useState(value[0]);
  const [localMax, setLocalMax] = useState(value[1]);

  useEffect(() => {
    setLocalMin(value[0]);
    setLocalMax(value[1]);
  }, [value]);

  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newMin = Math.min(Number(e.target.value), localMax - 5);
    setLocalMin(newMin);
  };

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newMax = Math.max(Number(e.target.value), localMin + 5);
    setLocalMax(newMax);
  };

  const handleMouseUp = () => {
    onChange([localMin, localMax]);
  };

  const getQualityColor = (val: number) => {
    if (val >= 80) return "text-green-600";
    if (val >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-3">Quality Score</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className={`font-medium ${getQualityColor(localMin)}`}>
            {localMin}
          </span>
          <span className="text-gray-400">to</span>
          <span className={`font-medium ${getQualityColor(localMax)}`}>
            {localMax}
          </span>
        </div>

        {/* Range visualization */}
        <div className="relative h-2 bg-gray-200 rounded-full">
          <div
            className="absolute h-2 bg-blue-500 rounded-full"
            style={{
              left: `${localMin}%`,
              width: `${localMax - localMin}%`,
            }}
          />
        </div>

        {/* Sliders */}
        <div className="relative">
          <input
            type="range"
            min={0}
            max={100}
            value={localMin}
            onChange={handleMinChange}
            onMouseUp={handleMouseUp}
            onTouchEnd={handleMouseUp}
            className="absolute w-full h-2 appearance-none bg-transparent pointer-events-none z-10
              [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:appearance-none
              [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-white
              [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-blue-500
              [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer
              [&::-webkit-slider-thumb]:shadow-md"
          />
          <input
            type="range"
            min={0}
            max={100}
            value={localMax}
            onChange={handleMaxChange}
            onMouseUp={handleMouseUp}
            onTouchEnd={handleMouseUp}
            className="absolute w-full h-2 appearance-none bg-transparent pointer-events-none z-10
              [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:appearance-none
              [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-white
              [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-blue-500
              [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer
              [&::-webkit-slider-thumb]:shadow-md"
          />
        </div>

        {/* Quick filters */}
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => onChange([80, 100])}
            className={`px-2 py-1 text-xs rounded-full transition-colors ${
              localMin === 80 && localMax === 100
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Good (80+)
          </button>
          <button
            onClick={() => onChange([60, 79])}
            className={`px-2 py-1 text-xs rounded-full transition-colors ${
              localMin === 60 && localMax === 79
                ? "bg-yellow-100 text-yellow-700"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Fair
          </button>
          <button
            onClick={() => onChange([0, 59])}
            className={`px-2 py-1 text-xs rounded-full transition-colors ${
              localMin === 0 && localMax === 59
                ? "bg-red-100 text-red-700"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Poor
          </button>
        </div>
      </div>
    </div>
  );
}
