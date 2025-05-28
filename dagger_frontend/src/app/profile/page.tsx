'use client';

import { useAuth } from '@/app/contexts/auth_context';
import { useTeam } from '@/app/contexts/team_context';
import { useState, useEffect } from 'react';

export default function ProfilePage() {
  const { user } = useAuth();
  const { allTeams, switchTeam, loading } = useTeam();
  const [selectedTeamId, setSelectedTeamId] = useState(user?.team_id || '');

  useEffect(() => {
    if (user?.team_id) {
      setSelectedTeamId(user.team_id);
    }
  }, [user?.team_id]);

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Please log in to view your profile</p>
      </div>
    );
  }

  const handleTeamChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newTeamId = e.target.value;
    setSelectedTeamId(newTeamId);
    await switchTeam(newTeamId);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">Profile</h1>
        <div className="bg-white/5 rounded-lg p-6 shadow-lg text-white">
          <div className="mb-4">
            <p className="text-gray-300">Username:</p>
            <p className="text-xl font-semibold">{user.username || 'Not set'}</p>
          </div>
          <div className="mb-4">
            <p className="text-gray-300">Current Team:</p>
            <select
              value={selectedTeamId}
              onChange={handleTeamChange}
              disabled={loading}
              className="mt-2 w-full px-4 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {allTeams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.team_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
