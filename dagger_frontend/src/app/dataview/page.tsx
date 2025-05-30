"use client";

import React, { useState, useEffect } from 'react';
import { useData } from '../contexts/data_context';
import WeekComponent from '../components/week';
import type { Week } from '@/client/types.gen';
import { DataProvider } from '../contexts/data_context';

// Placeholder chart components using Tailwind
function HeatMap({ data, label }: { data: { date: string; value: number }[]; label: string }) {
  return (
    <div className="h-32 flex items-end gap-1">
      {data.slice(-20).map((d, i) => (
        <div key={i} className="flex-1 bg-blue-200" style={{ height: `${d.value * 10 + 10}px` }} title={`${d.date}: ${d.value}`}></div>
      ))}
      <span className="ml-2 text-xs text-gray-500">{label}</span>
    </div>
  );
}
function LineGraph({ data, label }: { data: { date: string; value: number }[]; label: string }) {
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
function BarChart({ data, label }: { data: { name: string; value: number }[]; label: string }) {
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

// Helper to aggregate data for charts
function getChartData(weeks: Week[]) {
  // Heatmap data: array of { date, value }
  const missedDeadlines: { date: string; value: number }[] = [];
  const completedTasks: { date: string; value: number }[] = [];
  // Line graph: array of { date, value }
  const pointsCompleted: { date: string; value: number }[] = [];
  // Bar chart: collaborator -> count
  const collaboratorCounts: Record<string, number> = {};

  weeks.forEach((week) => {
    const date = week.start_date;
    const missed = Number(week.missed_deadlines);
    const completed = Number(week.completed_tasks);
    const points = Number(week.points_completed);
    missedDeadlines.push({ date, value: isNaN(missed) ? 0 : missed });
    completedTasks.push({ date, value: isNaN(completed) ? 0 : completed });
    pointsCompleted.push({ date, value: isNaN(points) ? 0 : points });
    if (Array.isArray(week.collaborators)) {
      week.collaborators.forEach((collab: any) => {
        const name = typeof collab === 'string' ? collab : collab?.username || 'Unknown';
        collaboratorCounts[name] = (collaboratorCounts[name] || 0) + 1;
      });
    }
  });

  // Bar chart data: array of { name, value }
  const collaborators = Object.entries(collaboratorCounts).map(([name, value]) => ({ name, value }));

  return {
    missedDeadlines,
    completedTasks,
    pointsCompleted,
    collaborators,
  };
}

export default function DataView() {
  return (
    <DataProvider>
      <DataViewContent />
    </DataProvider>
  );
}

function DataViewContent() {
  const { weeks, loading, error, refresh_data } = useData();
  const [chartsReady, setChartsReady] = useState(false);
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    // On mount, refresh data, then set chart data
    (async () => {
      setChartsReady(false);
      await refresh_data();
      setChartData(getChartData(weeks));
      setChartsReady(true);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">All-Time Analytics</h1>
      {loading || !chartsReady ? (
        <div className="text-center py-4">Loading...</div>
      ) : error ? (
        <div className="text-red-500 text-center py-4">{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded shadow p-4">
            <h2 className="font-semibold mb-2">Missed Deadlines Heatmap</h2>
            <HeatMap data={chartData.missedDeadlines} label="Missed Deadlines" />
          </div>
          <div className="bg-white rounded shadow p-4">
            <h2 className="font-semibold mb-2">Completed Tasks Heatmap</h2>
            <HeatMap data={chartData.completedTasks} label="Completed Tasks" />
          </div>
          <div className="bg-white rounded shadow p-4">
            <h2 className="font-semibold mb-2">Points Completed Over Time</h2>
            <LineGraph data={chartData.pointsCompleted} label="Points Completed" />
          </div>
          <div className="bg-white rounded shadow p-4">
            <h2 className="font-semibold mb-2">Top Collaborators</h2>
            <BarChart data={chartData.collaborators} label="Collaborators" />
          </div>
        </div>
      )}
    </div>
  );
}
