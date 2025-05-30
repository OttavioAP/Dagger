export default function HeatMap({ data, label }: { data: { date: string; value: number }[]; label: string }) {
  return (
    <div className="h-32 flex items-end gap-1">
      {data.slice(-20).map((d, i) => (
        <div key={i} className="flex-1 bg-blue-200" style={{ height: `${d.value * 10 + 10}px` }} title={`${d.date}: ${d.value}`}></div>
      ))}
      <span className="ml-2 text-xs text-gray-500">{label}</span>
    </div>
  );
}

