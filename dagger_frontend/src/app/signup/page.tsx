"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import type { User } from "@/types/shared";
import { useTeam } from "@/app/contexts/team_context";
import { useAuth } from "@/app/contexts/auth_context";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [selectedTeamId, setSelectedTeamId] = useState<string>("");
  const [newTeamName, setNewTeamName] = useState("");
  const [isCreatingTeam, setIsCreatingTeam] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const { allTeams, refreshAllTeams, loading: teamsLoading } = useTeam();

  useEffect(() => {
    console.log('Signup component mounted, calling refreshAllTeams');
    refreshAllTeams();
  }, []);

  useEffect(() => {
    console.log('allTeams updated:', allTeams);
  }, [allTeams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      let teamId = selectedTeamId;

      // If creating a new team
      if (isCreatingTeam && newTeamName) {
        const teamRes = await fetch('/api/team', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ team_name: newTeamName }),
        });

        if (!teamRes.ok) {
          const errorData = await teamRes.json();
          throw new Error(errorData.error || "Failed to create team");
        }

        const teamData = await teamRes.json();
        if (teamData.data) {
          teamId = teamData.data.id;
          await refreshAllTeams(); // Refresh teams list after creating new team
        } else {
          throw new Error("Failed to create team");
        }
      }

      if (!teamId) {
        throw new Error("Please select or create a team");
      }

      const userRes = await fetch('/api/user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          team_id: teamId,
          action: "create"
        }),
      });

      if (!userRes.ok) {
        const errorData = await userRes.json();
        throw new Error(errorData.error || "Failed to create user");
      }

      const userData = await userRes.json();
      if (userData.data) {
        const newUser: User = {
          id: userData.data.id,
          username: username,
          team_id: teamId
        };
        router.push("/login");
      } else {
        throw new Error("Failed to create user");
      }
    } catch (err: unknown) {
      const message =
        typeof err === 'object' && err !== null && 'message' in err
          ? String((err as { message?: unknown }).message)
          : "Signup failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white/5 rounded-xl p-8 shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold">
            Sign up for your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Password"
              />
            </div>
            <div className="flex items-center space-x-4">
              <button
                type="button"
                onClick={() => setIsCreatingTeam(!isCreatingTeam)}
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                {isCreatingTeam ? "Select Existing Team" : "Create New Team"}
              </button>
            </div>
            {isCreatingTeam ? (
              <div>
                <label htmlFor="teamName" className="sr-only">
                  Team Name
                </label>
                <input
                  id="teamName"
                  name="teamName"
                  type="text"
                  required
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="New Team Name"
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                />
              </div>
            ) : (
              <div>
                <label htmlFor="team" className="sr-only">
                  Select Team
                </label>
                {teamsLoading ? (
                  <div className="text-center py-2 text-gray-400">Loading teams...</div>
                ) : (
                  <select
                    id="team"
                    name="team"
                    required
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={selectedTeamId}
                    onChange={(e) => setSelectedTeamId(e.target.value)}
                  >
                    <option value="">Select a team</option>
                    {Array.isArray(allTeams) && allTeams.map((team) => (
                      <option key={team.id} value={team.id}>
                        {team.team_name}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-blue-500 to-teal-400 hover:from-blue-600 hover:to-teal-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? "Signing up..." : "Sign up"}
            </button>
          </div>
        </form>
        {error && <div className="text-red-400 text-center">{error}</div>}
      </div>
    </div>
  );
}
