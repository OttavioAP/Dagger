'use client';

import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import type { Week, WeekRequestType } from '@/client/types.gen';
import { useAuth } from './auth_context';
import { useTeam } from './team_context';
import { format, subMonths } from 'date-fns';
import { useDag } from './dag_context';

interface DataContextType {
  weeks: Week[];
  loading: boolean;
  error: string | null;
  refreshWeeks: () => Promise<void>;
  searchWeeks: (query: string) => Promise<void>;
  compareWeeks: (weekIds: string[]) => Promise<void>;
  refresh_data: () => Promise<void>;
  chartData: any;
  getChartData: (weeks: any[], teamUsers: any[]) => any;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

// Helper to aggregate data for charts
function getChartData(weeks: any[], teamUsers: any[] = [], tasksDict: Record<string, any> = {}) {
  if (!Array.isArray(weeks)) weeks = [];
  // Debug: log teamUsers and weeks
  console.log('getChartData: teamUsers', teamUsers);
  console.log('getChartData: weeks', weeks);
  console.log('getChartData: tasksDict', tasksDict);

  // Get last 12 months as x-axis
  const months: string[] = [];
  for (let i = 11; i >= 0; i--) {
    months.push(format(subMonths(new Date(), i), 'yyyy-MM'));
  }

  // Build a map from user ID to username (case-insensitive)
  const userIdToName: Record<string, string> = {};
  teamUsers.forEach(u => {
    userIdToName[String(u.id)] = u.username || u.name || u.id;
  });

  // Aggregate by month (using actual task dates)
  const missedDeadlinesMap: Record<string, number> = {};
  const completedTasksMap: Record<string, number> = {};
  const pointsCompletedMap: Record<string, number> = {};
  const collaboratorCounts: Record<string, number> = {};

  weeks.forEach((week, weekIdx) => {
    // Missed Deadlines: aggregate by task deadline
    if (Array.isArray(week.missed_deadlines)) {
      week.missed_deadlines.forEach((taskId: string) => {
        const task = tasksDict[taskId];
        if (!task || !task.deadline) return;
        const month = format(new Date(task.deadline), 'yyyy-MM');
        missedDeadlinesMap[month] = (missedDeadlinesMap[month] || 0) + 1;
      });
    }
    // Completed Tasks: aggregate by task completion date
    if (Array.isArray(week.completed_tasks)) {
      week.completed_tasks.forEach((taskId: string) => {
        const task = tasksDict[taskId];
        if (!task || !task.date_of_completion) return;
        const month = format(new Date(task.date_of_completion), 'yyyy-MM');
        completedTasksMap[month] = (completedTasksMap[month] || 0) + 1;
        // Points completed: sum by completion month
        pointsCompletedMap[month] = (pointsCompletedMap[month] || 0) + (task.points || 0);
      });
    }
    // Collaborators: aggregate by user ID
    if (Array.isArray(week.collaborators)) {
      week.collaborators.forEach((collab: any, idx: number) => {
        let name = 'Unknown';
        if (typeof collab === 'string') {
          name = userIdToName[String(collab)] || collab;
        } else if (collab && typeof collab === 'object') {
          name = collab.username || collab.name || collab.id || 'Unknown';
        }
        collaboratorCounts[name] = (collaboratorCounts[name] || 0) + 1;
        // Debug: log each collaborator mapping
        console.log(
          `Week[${weekIdx}] collaborator:`,
          collab,
          '->',
          name,
          '| teamUsers:',
          teamUsers
        );
      });
    }
  });

  // Fill in months with zero if missing
  const missedDeadlines = months.map(month => ({ date: month, value: missedDeadlinesMap[month] || 0 }));
  const completedTasks = months.map(month => ({ date: month, value: completedTasksMap[month] || 0 }));
  const pointsCompleted = months.map(month => ({ date: month, value: pointsCompletedMap[month] || 0 }));
  const collaborators = Object.entries(collaboratorCounts).map(([name, value]) => ({ name, value }));

  const chartData = {
    missedDeadlines,
    completedTasks,
    pointsCompleted,
    collaborators,
  };
  // Debug: log final chartData
  console.log('getChartData: chartData', chartData);
  return chartData;
}

export function DataProvider({ children }: { children: React.ReactNode }) {
  const [weeks, setWeeks] = useState<Week[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const { currentTeam, teamUsers, loading: teamUsersLoading } = useTeam();
  const { tasksDict } = useDag();

  const fetchWeeks = async (requestType: WeekRequestType = 'get_weeks', additionalParams: Record<string, any> = {}) => {
    console.log('fetching weeks');
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
      console.log('response', response);
      
      const responseData = await response.json();
      let fetchedWeeks = [];
      if (Array.isArray(responseData.data?.weeks)) {
        fetchedWeeks = responseData.data.weeks;
        console.log('weeks from responseData.data.weeks', fetchedWeeks);
      } else {
        console.log('weeks not found in response or not an array', responseData);
      }
      setWeeks(fetchedWeeks);
      console.log('weeks', fetchedWeeks);
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

  const chartData = useMemo(() => getChartData(weeks, teamUsers, tasksDict), [weeks, teamUsers, tasksDict]);

  const value = {
    weeks,
    loading,
    error,
    refreshWeeks,
    searchWeeks,
    compareWeeks,
    refresh_data,
    chartData,
    getChartData: (w: any[], t: any[]) => getChartData(w, t, tasksDict),
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
