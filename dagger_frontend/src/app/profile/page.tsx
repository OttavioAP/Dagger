// app/profile/page.tsx
'use client';

import { useAuth } from '@/app/contexts/auth_context';
import { useTeam } from '@/app/contexts/team_context';
import { useState, useEffect } from 'react';
import { useData } from '@/app/contexts/data_context';

import {
  LineChart, Line, BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function ProfilePage() {
  const { user } = useAuth();
  const { allTeams, refreshTeamUsers, loading: teamLoading, teamUsers } = useTeam();
  const [selectedTeamId, setSelectedTeamId] = useState(user?.team_id || '');
  const { weeks, loading: weeksLoading, error, refresh_data } = useData();
  const { chartData } = useData();
  const [chartsReady, setChartsReady] = useState(false);

  useEffect(() => {
    if (!user) return;
    (async () => {
      setChartsReady(false);
      await refresh_data();
      setChartsReady(true);
    })();
  }, [user]);

  useEffect(() => {
    if (user?.team_id) {
      setSelectedTeamId(user.team_id);
    }
  }, [user?.team_id]);

  const handleTeamChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newTeamId = e.target.value;
    setSelectedTeamId(newTeamId);
    await refreshTeamUsers();
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen text-white">
        <p>Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Profile</h1>
        <div className="bg-gray-800/80 backdrop-blur-md border border-gray-700 rounded-xl p-6 shadow-lg mb-12">
          <div className="mb-4">
            <p className="text-sm text-gray-400">Username:</p>
            <p className="text-xl font-semibold">{user.username || 'Not set'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Current Team:</p>
            <select
              value={selectedTeamId}
              onChange={handleTeamChange}
              disabled={teamLoading}
              className="mt-2 w-full px-4 py-2 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {allTeams.map((team) => (
                <option key={team.id} value={team.id}>{team.team_name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-semibold mb-6">All-Time Analytics</h2>
          {weeksLoading || !chartsReady ? (
            <div className="text-center py-8 text-gray-300">Loading analytics...</div>
          ) : error ? (
            <div className="text-red-500 text-center py-4">{error}</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-xl p-6 shadow-md">
                <h3 className="text-lg font-semibold mb-4">Missed Deadlines</h3>
                <ResponsiveContainer width="100%" height={150}>
                  <BarChart data={chartData.missedDeadlines}>
                    <XAxis dataKey="date" tick={{ fill: '#ccc', fontSize: 12 }} angle={-45} textAnchor="end" interval={0} height={40} />
                    <YAxis tick={{ fill: '#ccc', fontSize: 12 }} allowDecimals={false} />
                    <Tooltip formatter={(value: any) => [value, 'Missed Deadlines']} labelFormatter={label => `Month: ${label}`} />
                    <Bar dataKey="value">
                      {chartData.missedDeadlines.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={`rgba(239, 68, 68, ${entry.value / 10})`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-gray-800 rounded-xl p-6 shadow-md">
                <h3 className="text-lg font-semibold mb-4">Completed Tasks</h3>
                <ResponsiveContainer width="100%" height={150}>
                  <BarChart data={chartData.completedTasks}>
                    <XAxis dataKey="date" tick={{ fill: '#ccc', fontSize: 12 }} angle={-45} textAnchor="end" interval={0} height={40} />
                    <YAxis tick={{ fill: '#ccc', fontSize: 12 }} allowDecimals={false} />
                    <Tooltip formatter={(value: any) => [value, 'Completed Tasks']} labelFormatter={label => `Month: ${label}`} />
                    <Bar dataKey="value" fill="#4ade80" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-gray-800 rounded-xl p-6 shadow-md">
                <h3 className="text-lg font-semibold mb-4">Points Completed Over Time</h3>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={chartData.pointsCompleted}>
                    <XAxis dataKey="date" tick={{ fill: '#ccc', fontSize: 12 }} angle={-45} textAnchor="end" interval={0} height={40} />
                    <YAxis tick={{ fill: '#ccc', fontSize: 12 }} />
                    <CartesianGrid strokeDasharray="3 3" />
                    <Tooltip formatter={(value: any) => [value, 'Points']} labelFormatter={label => `Month: ${label}`} />
                    <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-gray-800 rounded-xl p-6 shadow-md">
                <h3 className="text-lg font-semibold mb-4">Top Collaborators</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart
                    data={chartData.collaborators
                      .sort((a: any, b: any) => b.value - a.value)
                      .slice(0, 10)
                    }
                    layout="vertical"
                    margin={{ left: 50 }}
                  >
                    <XAxis type="number" tick={{ fill: '#ccc', fontSize: 12 }} allowDecimals={false} />
                    <YAxis type="category" dataKey="name" tick={{ fill: '#ccc', fontSize: 12 }} width={100} />
                    <Tooltip formatter={(value: any) => [value, 'Tasks']} labelFormatter={label => `Collaborator: ${label}`} />
                    <Bar dataKey="value" fill="#6366f1" radius={[0, 6, 6, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
