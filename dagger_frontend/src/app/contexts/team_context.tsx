'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { Team, User } from '@/client/types.gen';
import { useAuth } from '../contexts/auth_context';

interface TeamWithUsers extends Team {
  users: User[];
}

interface TeamContextType {
  currentTeam: TeamWithUsers | null;
  allTeams: TeamWithUsers[];
  teamUsers: User[]; // Users in the current team
  loading: boolean;
  error: string | null;
  refreshTeams: () => Promise<void>;
  refreshTeamUsers: () => Promise<void>;
  refreshTeamsAndUsers: () => Promise<void>;
}

const TeamContext = createContext<TeamContextType | undefined>(undefined);

export function TeamProvider({ children }: { children: React.ReactNode }) {
  const [currentTeam, setCurrentTeam] = useState<TeamWithUsers | null>(null);
  const [allTeams, setAllTeams] = useState<TeamWithUsers[]>([]);
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
      const users: User[] = (await response.json()).data;
      setTeamUsers(users);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [user?.team_id]);

  const fetchTeams = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/team');
      if (!response.ok) {
        throw new Error('Failed to fetch teams');
      }
      const responseData = await response.json();
      const teamsData = responseData.data || [];
      setAllTeams(teamsData);

      if (user?.team_id) {
        const foundTeam = teamsData.find((team: Team) => team.id === user.team_id);
        if (foundTeam) {
          const usersResponse = await fetch(`/api/user/byTeam?team_id=${user.team_id}`);
          const users: User[] = usersResponse.ok ? (await usersResponse.json()).data : [];
          setCurrentTeam({ ...foundTeam, users });
        } else {
          setCurrentTeam(null);
        }
      } else {
        setCurrentTeam(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [user?.team_id]);

  const refreshTeamsAndUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/team');
      if (!response.ok) {
        throw new Error('Failed to fetch teams');
      }
      const responseData = await response.json();
      const teamsData: Team[] = responseData.data || [];
      const teamsWithUsers: TeamWithUsers[] = await Promise.all(
        teamsData.map(async (team) => {
          const usersResponse = await fetch(`/api/user/byTeam?team_id=${team.id}`);
          const users: User[] = usersResponse.ok ? (await usersResponse.json()).data : [];
          return { ...team, users };
        })
      );
      setAllTeams(teamsWithUsers);
      if (user?.team_id) {
        const foundTeam = teamsWithUsers.find((team) => team.id === user.team_id) || null;
        setCurrentTeam(foundTeam);
        setTeamUsers(foundTeam ? foundTeam.users : []);
      } else {
        setCurrentTeam(null);
        setTeamUsers([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [user?.team_id]);

  useEffect(() => {
    if (!initialFetchDone.current) {
      fetchTeams();
      initialFetchDone.current = true;
    }
  }, [fetchTeams]);

  const value = {
    currentTeam,
    allTeams,
    teamUsers,
    loading,
    error,
    refreshTeams: fetchTeams,
    refreshTeamUsers: fetchTeamUsers,
    refreshTeamsAndUsers,
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
