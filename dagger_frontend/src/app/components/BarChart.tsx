export default function BarChart({ data, label }: { data: { name: string; value: number }[]; label: string }) {
  return (
    <div className="flex items-end gap-1 h-32">
      {data.slice(0, 10).map((d, i) => (
        <div key={i} className="flex flex-col items-center">
          <div className="bg-blue-400 w-4" style={{ height: `${d.value * 10 + 10}px` }} title={`${d.name}: ${d.value}`}></div>
          <span className="text-xs mt-1 truncate w-8 text-center">{d.name}</span>
        </div>
      ))}
      <span className="ml-2 text-xs text-gray-500">{label}</span>
    </div>
  );
}

