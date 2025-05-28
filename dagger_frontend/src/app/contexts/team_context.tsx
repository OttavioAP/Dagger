'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { Team, User } from '@/client/types.gen';
import { useAuth } from './auth_context';

interface TeamWithUsers extends Team {
  users: User[];
}

interface TeamContextType {
  currentTeam: TeamWithUsers | null;
  allTeams: Team[];
  teamUsers: User[]; // Users in the current team
  loading: boolean;
  error: string | null;
  refreshCurrentTeam: () => Promise<void>;
  refreshAllTeams: () => Promise<void>;
  refreshTeamUsers: () => Promise<void>;
  switchTeam: (teamId: string) => Promise<void>;
}

const TeamContext = createContext<TeamContextType | undefined>(undefined);

export function TeamProvider({ children }: { children: React.ReactNode }) {
  const [currentTeam, setCurrentTeam] = useState<TeamWithUsers | null>(null);
  const [allTeams, setAllTeams] = useState<Team[]>([]);
  const [teamUsers, setTeamUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const initialFetchDone = useRef(false);

  const fetchTeamUsers = useCallback(async () => {
    if (!user?.team_id) {
      setTeamUsers([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/user/byTeam?team_id=${user.team_id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch team users');
      }
      const users: User[] = await response.json();
      setTeamUsers(users);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [user?.team_id]);

  const fetchCurrentTeam = useCallback(async () => {
    if (!user?.team_id) {
      setCurrentTeam(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Fetch team details
      const teamResponse = await fetch(`/api/team/${user.team_id}`);
      if (!teamResponse.ok) {
        throw new Error('Failed to fetch current team');
      }
      const teamData: Team = await teamResponse.json();

      // Fetch team users
      const usersResponse = await fetch(`/api/user/byTeam?team_id=${user.team_id}`);
      if (!usersResponse.ok) {
        throw new Error('Failed to fetch team users');
      }
      const users: User[] = await usersResponse.json();

      setCurrentTeam({
        ...teamData,
        users,
      });
      setTeamUsers(users);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [user?.team_id]);

  const fetchAllTeams = useCallback(async () => {
    try {
      console.log('fetchAllTeams: starting fetch');
      setLoading(true);
      setError(null);

      const response = await fetch('/api/team');
      if (!response.ok) {
        throw new Error('Failed to fetch teams');
      }
      const responseData = await response.json();
      console.log('fetchAllTeams: received data:', responseData);
      // Extract the teams array from the response data
      const teamsData = responseData.data || [];
      console.log('fetchAllTeams: extracted teams:', teamsData);
      setAllTeams(teamsData);
      console.log('fetchAllTeams: setAllTeams called');
    } catch (err) {
      console.error('fetchAllTeams: error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      console.log('fetchAllTeams: loading set to false');
    }
  }, []);

  const switchTeam = useCallback(async (teamId: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.id,
          team_id: teamId,
          action: 'update'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to switch team');
      }

      await Promise.all([fetchCurrentTeam(), fetchTeamUsers()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [user?.id, fetchCurrentTeam, fetchTeamUsers]);

  // Initial fetch of all teams
  useEffect(() => {
    if (!initialFetchDone.current) {
      console.log('TeamProvider: initial fetch starting');
      fetchAllTeams();
      initialFetchDone.current = true;
    }
  }, [fetchAllTeams]);

  // Fetch current team and team users when user changes
  useEffect(() => {
    if (user?.team_id) {
      Promise.all([fetchCurrentTeam(), fetchTeamUsers()]);
    } else {
      setCurrentTeam(null);
      setTeamUsers([]);
    }
  }, [user?.team_id, fetchCurrentTeam, fetchTeamUsers]);

  const value = {
    currentTeam,
    allTeams,
    teamUsers,
    loading,
    error,
    refreshCurrentTeam: fetchCurrentTeam,
    refreshAllTeams: fetchAllTeams,
    refreshTeamUsers: fetchTeamUsers,
    switchTeam,
  };

  return <TeamContext.Provider value={value}>{children}</TeamContext.Provider>;
}

export function useTeam() {
  const context = useContext(TeamContext);
  if (context === undefined) {
    throw new Error('useTeam must be used within a TeamProvider');
  }
  return context;
}
