export default function LineGraph({ data, label }: { data: { date: string; value: number }[]; label: string }) {
  // Simple SVG line graph
  const points = data.slice(-20).map((d, i) => `${i * 10},${40 - d.value * 3}`).join(' ');
  return (
    <div>
      <svg width={200} height={40} className="bg-blue-50">
        <polyline fill="none" stroke="#3b82f6" strokeWidth="2" points={points} />
      </svg>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

