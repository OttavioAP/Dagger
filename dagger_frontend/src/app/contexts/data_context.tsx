'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import type { Week, WeekRequestType } from '@/client/types.gen';
import { useAuth } from './auth_context';
import { useTeam } from './team_context';

interface DataContextType {
  weeks: Week[];
  loading: boolean;
  error: string | null;
  refreshWeeks: () => Promise<void>;
  searchWeeks: (query: string) => Promise<void>;
  compareWeeks: (weekIds: string[]) => Promise<void>;
  refresh_data: () => Promise<void>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export function DataProvider({ children }: { children: React.ReactNode }) {
  const [weeks, setWeeks] = useState<Week[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const { currentTeam } = useTeam();

  const fetchWeeks = async (requestType: WeekRequestType = 'get_weeks', additionalParams: Record<string, any> = {}) => {
    if (!user?.id) {
      setWeeks([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Build query parameters
      const params = new URLSearchParams({
        request_type: requestType,
        number_of_weeks: '100', // Fetch a large number to get all weeks
        user_id: user.id,
        ...(currentTeam?.id && { team_id: currentTeam.id }),
        ...additionalParams
      });

      const response = await fetch(`/api/week?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch weeks');
      }

      const responseData = await response.json();
      const weeks = responseData.data?.weeks || responseData.weeks || [];
      setWeeks(weeks);
      console.log('weeks', weeks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const refreshWeeks = async () => {
    await fetchWeeks();
  };

  const searchWeeks = async (query: string) => {
    await fetchWeeks('search_query', { query });
  };

  const compareWeeks = async (weekIds: string[]) => {
    await fetchWeeks('compare_weeks', { week_ids: weekIds.join(',') });
  };

  // Initial fetch of weeks
  useEffect(() => {
    if (user?.id) {
      fetchWeeks();
    } else {
      setWeeks([]);
    }
  }, [user?.id, currentTeam?.id]); // Refresh when user or team changes

  // Unified refresh_data function (can be extended to refresh more in the future)
  const refresh_data = async () => {
    await refreshWeeks();
  };

  const value = {
    weeks,
    loading,
    error,
    refreshWeeks,
    searchWeeks,
    compareWeeks,
    refresh_data,
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData() {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
}
