'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { 
  DagRequest, 
  TaskRequest, 
  UserTasksRequest,
  Dag,
  Task,
  UserTasks,
  DagAction,
  TaskPriority,
  TaskFocus
} from '@/client/types.gen';
import { useAuth } from './auth_context';
import { useTeam } from './team_context';

// Types for DAG context using auto-generated types
export interface DagWithDetails extends Dag {
  nodes: {
    [key: string]: Task & {
      assigned_users: string[]; // User IDs
    };
  };
}

interface DagContextType {
  dags: DagWithDetails[];
  loading: boolean;
  error: string | null;
  refreshDags: () => Promise<void>;
  createDag: (request: DagRequest) => Promise<void>;
  addEdge: (request: DagRequest) => Promise<void>;
  deleteEdge: (request: DagRequest & { dag_id?: string }) => Promise<void>;
  createTask: (request: TaskRequest) => Promise<Task>;
  assignUserToTask: (request: UserTasksRequest) => Promise<void>;
  removeUserFromTask: (request: UserTasksRequest) => Promise<void>;
  tasksDict: { [key: string]: Task };
  deleteTask: (taskId: string) => Promise<void>;
  updateTask: (request: TaskRequest) => Promise<void>;
  completeTask: (taskId: string) => Promise<void>;
  get_task_dependencies: (taskId: string) => Task[];
  get_task_users: (taskId: string) => string[];
  get_dag_id_by_task_id: (taskId: string) => string | undefined;
  computeAllLeafUrgencies: (dag: DagWithDetails) => Record<string, number>;
}

const DagContext = createContext<DagContextType | undefined>(undefined);

const HOURS_PER_DAY = 8;
const PRIORITY_MULTIPLIER: Record<TaskPriority, number> = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  EMERGENCY: 100,
};

// 1. Identify Leaf Tasks (no dependencies, not completed)
function getLeafTasks(dag: DagWithDetails): string[] {
  return Object.keys(dag.nodes).filter(
    id =>
      (!dag.dag_graph[id] || dag.dag_graph[id].length === 0) &&
      !dag.nodes[id].date_of_completion
  );
}

// 2. Walk Dependency Chains (DFS from leaf, skip completed, traverse upstream)
function getAllDependencyChains(taskId: string, dag: DagWithDetails): string[][] {
  const chains: string[][] = [];
  function dfs(current: string, path: string[]) {
    // Find all tasks where current is a dependency (i.e., go upstream)
    const parents = Object.entries(dag.dag_graph)
      .filter(([from, toList]) =>
        (toList as string[]).includes(current) &&
        !dag.nodes[from]?.date_of_completion
      )
      .map(([from]) => from);
    if (parents.length === 0) {
      chains.push([...path, current]);
    } else {
      for (const parent of parents) {
        dfs(parent, [...path, current]);
      }
    }
  }
  dfs(taskId, []);
  return chains;
}

// 3. Calculate "Behind Score" for a Chain (skip completed, clamp slack)
function calculateBehindScore(chain: string[], dag: DagWithDetails): number {
  let totalPoints = 0;
  let earliestDeadline: Date | null = null;
  for (const taskId of chain) {
    const task = dag.nodes[taskId];
    if (!task) continue;
    if (task.date_of_completion) continue;
    totalPoints += task.points || 0;
    const deadline = task.deadline ? new Date(task.deadline) : null;
    if (deadline && (!earliestDeadline || deadline < earliestDeadline)) {
      earliestDeadline = deadline;
    }
  }
  if (!earliestDeadline) return 0;
  const hoursLeft = (earliestDeadline.getTime() - Date.now()) / (1000 * 60 * 60);
  const slack = hoursLeft - totalPoints;
  // Clamp slack to [-40, 40] (5 days behind/ahead)
  const clampedSlack = Math.max(-40, Math.min(40, slack));
  return clampedSlack;
}

// 4. Weight by Priority (skip completed)
function getMaxPriorityMultiplier(chain: string[], dag: DagWithDetails): number {
  return Math.max(
    ...chain
      .map(taskId => dag.nodes[taskId])
      .filter(task => task && !task.date_of_completion)
      .map(task => PRIORITY_MULTIPLIER[task!.priority ?? "LOW"])
  );
}

// 5. Final Urgency for Each Leaf Task (normalized 0-100)
function calculateUrgencyForTask(taskId: string, dag: DagWithDetails): number {
  const chains = getAllDependencyChains(taskId, dag);
  const rawScores = chains.map(chain => {
    const slack = calculateBehindScore(chain, dag); // in hours
    const priority = getMaxPriorityMultiplier(chain, dag); // 1-100
    // Normalize slack: -40h (5 days behind) → 100 urgency, +40h (5 days ahead) → 0 urgency
    const normalizedSlack = Math.max(-40, Math.min(40, slack));
    // Flip slack so lower slack = higher urgency
    const slackFactor = (40 - normalizedSlack) / 80; // from 0 (low) to 1 (high urgency)
    // Multiply by priority weight, normalize against max (100)
    const urgency = slackFactor * (priority / 100) * 100;
    return urgency;
  });
  // Return the maximum urgency across all chains this task influences, capped at 100
  return Math.min(100, Math.max(...rawScores));
}

// 6. Compute all leaf ranks for a DAG
function computeAllLeafUrgencies(dag: DagWithDetails): Record<string, number> {
  const leafTasks = getLeafTasks(dag);
  const ranks: Record<string, number> = {};
  for (const taskId of leafTasks) {
    ranks[taskId] = calculateUrgencyForTask(taskId, dag);
  }
  return ranks;
}

export function DagProvider({ children }: { children: React.ReactNode }) {
  const [dags, setDags] = useState<DagWithDetails[]>([]);
  const [tasksDict, setTasksDict] = useState<{ [key: string]: Task }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const { currentTeam } = useTeam();

  // Fetch all DAGs and their associated tasks and user assignments
  const fetchDags = useCallback(async () => {
    if (!user?.team_id) {
      setDags([]);
      setTasksDict({});
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Fetch all DAGs
      const dagsResponse = await fetch('/api/dag');
      if (!dagsResponse.ok) {
        throw new Error('Failed to fetch DAGs');
      }
      const dagsData: Dag[] = (await dagsResponse.json()).data;

      // Fetch all tasks
      const tasksResponse = await fetch('/api/task');
      if (!tasksResponse.ok) {
        throw new Error('Failed to fetch tasks');
      }
      const tasksData: Task[] = (await tasksResponse.json()).data;

      // Build tasksDict
      const newTasksDict: { [key: string]: Task } = {};
      tasksData.forEach(task => {
        if (task.id) newTasksDict[task.id] = task;
      });
      setTasksDict(newTasksDict);

      // Fetch all user task assignments
      const userTasksResponse = await fetch('/api/userTask');
      if (!userTasksResponse.ok) {
        throw new Error('Failed to fetch user task assignments');
      }
      const userTasksData: UserTasks[] = (await userTasksResponse.json()).data;

      // Process and combine the data
      const processedDags = dagsData
        .filter((dag) => dag.team_id === user.team_id)
        .map((dag) => {
          const nodes: { [key: string]: Task & { assigned_users: string[] } } = {};
          
          // Add task details to nodes
          tasksData
            .filter((task) => task.team_id === user.team_id)
            .forEach((task) => {
              nodes[task.id!] = {
                ...task,
                assigned_users: []
              };
            });

          // Add user assignments to nodes
          userTasksData
            .filter((ut) => ut.task_id in nodes)
            .forEach((ut) => {
              if (nodes[ut.task_id]) {
                nodes[ut.task_id].assigned_users.push(ut.user_id);
              }
            });

          return {
            ...dag,
            nodes
          };
        });

      setDags(processedDags);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [user?.team_id]);

  // Create a new DAG
  const createDag = async (request: DagRequest) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/dag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          action: 'create' as DagAction
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create DAG');
      }

      await fetchDags(); // Refresh DAGs after creation
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Add an edge to a DAG
  const addEdge = async (request: DagRequest) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/dag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          action: 'add_edges' as DagAction
        })
      });

      if (!response.ok) {
        throw new Error('Failed to add edge');
      }

      await fetchDags(); // Refresh DAGs after adding edge
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Delete an edge from a DAG
  const deleteEdge = async (request: DagRequest & { dag_id?: string }) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/dag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          action: 'delete_edges' as DagAction,
          ...(request.dag_id ? { dag_id: request.dag_id } : {}),
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to delete edge');
      }
      await fetchDags(); // Refresh DAGs after deleting edge
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Create a new task
  const createTask = async (request: TaskRequest): Promise<Task> => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          action: 'create',
          priority: request.priority || 'LOW' as TaskPriority,
          focus: request.focus || 'LOW' as TaskFocus
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create task');
      }

      const data = await response.json();
      // Try to get the created task from data or data.data
      const createdTask: Task = data.data || data;
      await fetchDags(); // Refresh DAGs after creating task
      return createdTask;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Assign a user to a task
  const assignUserToTask = async (request: UserTasksRequest) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/userTask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          action: 'add'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to assign user to task');
      }

      await fetchDags(); // Refresh DAGs after assigning user
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Remove a user from a task
  const removeUserFromTask = async (request: UserTasksRequest) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/userTask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          action: 'delete'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to remove user from task');
      }

      await fetchDags(); // Refresh DAGs after removing user
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Delete a task
  const deleteTask = async (taskId: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, action: 'delete' })
      });

      if (!response.ok) {
        throw new Error('Failed to delete task');
      }

      await fetchDags();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update a task
  const updateTask = async (request: TaskRequest) => {
    try {
      setLoading(true);
      setError(null);

      // Only include non-null/undefined/non-empty-string fields
      const payload: any = { action: 'edit' };
      Object.entries(request).forEach(([key, value]) => {
        if (
          value !== undefined &&
          value !== null &&
          !(typeof value === 'string' && value.trim() === '')
        ) {
          payload[key] = value;
        }
      });

      if (!payload.task_id) {
        throw new Error('task_id is required for update');
      }

      const response = await fetch('/api/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`Failed to update task: ${errorBody}`);
      }

      await fetchDags();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Mark a task as completed
  const completeTask = async (taskId: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, action: 'complete' })
      });
      if (!response.ok) {
        throw new Error('Failed to complete task');
      }
      await fetchDags();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Helper: Get dependencies of a task (returns Task[])
  const get_task_dependencies = (taskId: string): Task[] => {
    // Find the DAG that contains this task
    for (const dag of dags) {
      // dag.dag_graph: { [from]: to[] }
      // We want all tasks that are in dag.dag_graph[taskId]
      const depIds = dag.dag_graph[taskId] as string[] | undefined;
      if (depIds && depIds.length > 0) {
        return depIds
          .map(depId => tasksDict[depId])
          .filter((t): t is Task => Boolean(t));
      }
    }
    return [];
  };

  // Helper: Get user IDs assigned to a task
  const get_task_users = (taskId: string): string[] => {
    for (const dag of dags) {
      if (dag.nodes[taskId]) {
        return dag.nodes[taskId].assigned_users || [];
      }
    }
    return [];
  };

  // Helper: Get dag_id by task id
  const get_dag_id_by_task_id = (taskId: string): string | undefined => {
    for (const dag of dags) {
      if (dag.dag_graph[taskId]) {
        return dag.dag_id || undefined;
      }
    }
    return undefined;
  };

  // Initial fetch of DAGs
  useEffect(() => {
    if (user?.team_id) {
      fetchDags();
    }
  }, [user?.team_id, fetchDags]);

  const value = {
    dags,
    loading,
    error,
    refreshDags: fetchDags,
    createDag,
    addEdge,
    deleteEdge,
    createTask,
    assignUserToTask,
    removeUserFromTask,
    tasksDict,
    deleteTask,
    updateTask,
    completeTask,
    get_task_dependencies,
    get_task_users,
    get_dag_id_by_task_id,
    computeAllLeafUrgencies,
  };

  return <DagContext.Provider value={value}>{children}</DagContext.Provider>;
}

export function useDag() {
  const context = useContext(DagContext);
  if (context === undefined) {
    throw new Error('useDag must be used within a DagProvider');
  }
  return context;
}
