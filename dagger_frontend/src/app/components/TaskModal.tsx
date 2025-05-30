'use client';
import React, { useState, useMemo, useEffect } from 'react';
import { useDag } from '../contexts/dag_context';
import { useTeam } from '../contexts/team_context';
import { useAuth } from '../contexts/auth_context';
import type { Task, TaskRequest, TaskPriority, TaskFocus, DagAction } from '@/client/types.gen';


interface TaskModalProps {
  mode: 'create' | 'edit';
  task?: Task;
  onClose: () => void;
}

const priorities: TaskPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'EMERGENCY'];
const focuses: TaskFocus[] = ['LOW', 'MEDIUM', 'HIGH'];

export default function TaskModal({ mode, task, onClose }: TaskModalProps) {
  const {
    tasksDict,
    dags,
    createTask,
    updateTask,
    deleteTask,
    addEdge,
    deleteEdge,
    createDag,
    assignUserToTask,
    removeUserFromTask,
    refreshDags,
    get_task_dependencies,
    get_task_users,
    get_dag_id_by_task_id,
    completeTask,
  } = useDag();
  const { teamUsers } = useTeam();
  const { user } = useAuth();
  const [taskName, setTaskName] = useState(task?.task_name || '');
  const [description, setDescription] = useState(task?.description || '');
  const [deadline, setDeadline] = useState(task?.deadline || '');
  const [priority, setPriority] = useState<TaskPriority>(task?.priority || 'LOW');
  const [focus, setFocus] = useState<TaskFocus>(task?.focus || 'LOW');
  const [points, setPoints] = useState<number>(task?.points || 0);
  const [notes, setNotes] = useState(task?.notes || '');

  // Expand/collapse state for description and notes
  const [descExpanded, setDescExpanded] = useState(false);
  const [notesExpanded, setNotesExpanded] = useState(false);

  // Dependency and user assignment state
  const [newDependencies, setNewDependencies] = useState<string[]>([]); // task ids
  const [newUsers, setNewUsers] = useState<string[]>([]); // user ids

  // For edit mode: track initial users/dependencies, and lists to add/remove
  const initialDependencies = useMemo(() => (mode === 'edit' && task?.id ? get_task_dependencies(task.id).map(t => t.id!).filter(Boolean) : []), [mode, task, get_task_dependencies]);
  const initialUsers = useMemo(() => (mode === 'edit' && task?.id ? get_task_users(task.id) : []), [mode, task, get_task_users]);
  const [dependenciesToRemove, setDependenciesToRemove] = useState<string[]>([]);
  const [usersToRemove, setUsersToRemove] = useState<string[]>([]);
  const [dependenciesToAdd, setDependenciesToAdd] = useState<string[]>([]);
  const [usersToAdd, setUsersToAdd] = useState<string[]>([]);

  // UI state for dependency/user fields
  const [depInputs, setDepInputs] = useState<{ value: string; task: Task | null }[]>(
    mode === 'edit'
      ? initialDependencies.map(id => ({ value: tasksDict[id]?.task_name || '', task: tasksDict[id] || null }))
      : [{ value: '', task: null }]
  );
  const [userInputs, setUserInputs] = useState<string[]>(mode === 'edit' ? initialUsers.map(uid => teamUsers.find(u => u.id === uid)?.username || '' ) : ['']);

  // Helper: get all tasks except this one, and only unfinished
  const availableTasks = useMemo(() =>
    Object.values(tasksDict).filter(t => t.id !== task?.id && !t.date_of_completion),
    [tasksDict, task?.id]
  );

  // Helper: get all users (only users in current team)
  const availableUsers = Array.isArray(teamUsers) ? teamUsers : [];

  // Error state for deadline
  const [deadlineError, setDeadlineError] = useState<string | null>(null);

  // Show current dependencies and users in edit mode
  const currentDependencies = useMemo(() => {
    if (mode === 'edit' && task?.id) {
      return get_task_dependencies(task.id);
    }
    return [];
  }, [mode, task, get_task_dependencies]);

  const currentUsers = useMemo(() => {
    if (mode === 'edit' && task?.id) {
      return get_task_users(task.id);
    }
    return [];
  }, [mode, task, get_task_users]);

  // Remove a dependency from UI and track for removal/addition
  const handleRemoveDependency = (idx: number) => {
    if (mode === 'create') {
      // Remove from newDependencies
      const depId = depInputs[idx]?.task?.id;
      if (depId) setNewDependencies(prev => prev.filter(id => id !== depId));
      setDepInputs(inputs => inputs.filter((_, i) => i !== idx));
    } else if (mode === 'edit') {
      const depId = depInputs[idx]?.task?.id;
      if (depId) {
        if (initialDependencies.includes(depId)) {
          setDependenciesToRemove(prev => [...new Set([...prev, depId])]);
        } else {
          setDependenciesToAdd(prev => prev.filter(id => id !== depId));
        }
      }
      setDepInputs(inputs => inputs.filter((_, i) => i !== idx));
    }
  };

  // Remove a user from UI and track for removal/addition
  const handleRemoveUser = (idx: number) => {
    if (mode === 'create') {
      const username = userInputs[idx];
      const userId = availableUsers.find(u => u.username === username)?.id;
      if (userId) setNewUsers(prev => prev.filter(id => id !== userId));
      setUserInputs(inputs => inputs.filter((_, i) => i !== idx));
    } else if (mode === 'edit') {
      const username = userInputs[idx];
      const userId = availableUsers.find(u => u.username === username)?.id;
      if (userId) {
        if (initialUsers.includes(userId)) {
          setUsersToRemove(prev => [...new Set([...prev, userId])]);
        } else {
          setUsersToAdd(prev => prev.filter(id => id !== userId));
        }
      }
      setUserInputs(inputs => inputs.filter((_, i) => i !== idx));
    }
  };

  // Add dependency field
  const addDepField = () => setDepInputs([...depInputs, { value: '', task: null }]);
  // Add user field
  const addUserField = () => setUserInputs([...userInputs, '']);

  // Handle dependency input change
  const handleDepInputChange = (idx: number, value: string) => {
    // Always update the input value
    setDepInputs(inputs => {
      const newInputs = [...inputs];
      const foundTask = availableTasks.find(t => t.task_name === value && !t.date_of_completion);
      newInputs[idx] = { value, task: foundTask || null };
      return newInputs;
    });
    const foundTask = availableTasks.find(t => t.task_name === value && !t.date_of_completion);
    if (foundTask && foundTask.id) {
      if (mode === 'create') {
        setNewDependencies(prev => [...new Set([...prev, foundTask.id!])]);
      } else if (mode === 'edit') {
        if (!initialDependencies.includes(foundTask.id!) && !dependenciesToAdd.includes(foundTask.id!)) {
          setDependenciesToAdd(prev => [...new Set([...prev, foundTask.id!])]);
        }
        // If user re-adds a dependency previously marked for removal, unmark it
        if (dependenciesToRemove.includes(foundTask.id!)) {
          setDependenciesToRemove(prev => prev.filter(id => id !== foundTask.id!));
        }
      }
    }
  };

  // Handle user input change
  const handleUserInputChange = (idx: number, value: string) => {
    setUserInputs(inputs => {
      const newInputs = [...inputs];
      newInputs[idx] = value;
      return newInputs;
    });
    const userId = availableUsers.find(u => u.username === value)?.id;
    if (userId) {
      if (mode === 'create') {
        setNewUsers(prev => [...new Set([...prev, userId])]);
      } else if (mode === 'edit') {
        if (!initialUsers.includes(userId) && !usersToAdd.includes(userId)) {
          setUsersToAdd(prev => [...new Set([...prev, userId])]);
        }
        // If user re-adds a user previously marked for removal, unmark it
        if (usersToRemove.includes(userId)) {
          setUsersToRemove(prev => prev.filter(id => id !== userId));
        }
      }
    }
  };

  // Deadline change handler with validation
  const handleDeadlineChange = (value: string) => {
    if (value) {
      const deadlineDate = new Date(value);
      const now = new Date();
      deadlineDate.setHours(23, 59, 59, 999);
      if (deadlineDate <= now) {
        setDeadlineError('Deadline must be in the future');
        return;
      }
    }
    setDeadlineError(null);
    setDeadline(value);
  };

  // Only allow completion of leaves
  const isLeaf = useMemo(() => {
    if (!task || !task.id) return false;
    // Find the DAG this task belongs to
    const dag = dags.find(d => d.nodes[task.id as string]);
    if (!dag) return false;
    // A task is a leaf if it has no UNCOMPLETED dependencies
    const deps = dag.dag_graph[task.id] || [];
    // If there are no dependencies, it's a leaf
    if (deps.length === 0) return true;
    // If all dependencies are completed, it's a leaf
    return deps.every(depId => {
      const depTask = dag.nodes[depId];
      return depTask && depTask.date_of_completion;
    });
  }, [task, dags]);

  // Modal logic
  const handleSubmit = async () => {
    // Validate deadline is in the future
    if (deadline) {
      const deadlineDate = new Date(deadline);
      const now = new Date();
      // Set time to end of day for deadline
      deadlineDate.setHours(23, 59, 59, 999);
      if (deadlineDate <= now) {
        setDeadlineError('Deadline must be in the future');
        return;
      }
    } else {
      setDeadlineError(null);
    }

    if (mode === 'create') {
      const request: TaskRequest = {
        task_name: taskName,
        team_id: user?.team_id,
        deadline,
        points,
        priority,
        focus,
        description,
        notes,
        action: 'create',
      };
      const createdTask = await createTask(request);
      if (!createdTask.id) {
        console.error('Failed to create task');
        return;
      }
      // Add users
      for (const user_id of newUsers) {
        await assignUserToTask({ user_id, task_id: createdTask.id!, action: 'add' });
      }
      // Add dependencies
      if (newDependencies.length > 0) {
        const dagReq = {
          first_task_id: createdTask.id,
          dependencies: newDependencies,
          team_id: user?.team_id!,
          action: 'add_edges' as DagAction,
        };
        await addEdge(dagReq);
      }
    } else if (mode === 'edit' && task?.id) {
      const request: TaskRequest = {
        task_id: task.id,
        task_name: taskName,
        team_id: user?.team_id,
        deadline,
        points,
        priority,
        focus,
        description,
        notes,
        action: 'edit',
      };
      await updateTask(request);
      // Remove users first
      for (const user_id of usersToRemove) {
        await removeUserFromTask({ user_id, task_id: task.id, action: 'delete' });
      }
      // Remove dependencies first
      if (dependenciesToRemove.length > 0) {
        const dag_id = get_dag_id_by_task_id(task.id);
        if (dag_id) {
          for (const depTaskId of dependenciesToRemove) {
            await deleteEdge({
              team_id: user?.team_id!,
              first_task_id: task.id,
              dependencies: [depTaskId],
              action: 'delete_edges',
              dag_id,
            });
          }
        }
      }
      // Add users
      for (const user_id of usersToAdd) {
        await assignUserToTask({ user_id, task_id: task.id, action: 'add' });
      }
      // Add dependencies
      if (dependenciesToAdd.length > 0) {
        const dag_id = get_dag_id_by_task_id(task.id);
        if (dag_id) {
          await addEdge({
            team_id: user?.team_id!,
            first_task_id: task.id,
            dependencies: dependenciesToAdd,
            action: 'add_edges' as DagAction,
            dag_id,
          });
        }
      }
    }
    refreshDags();
    onClose();
  };

  const handleDelete = async () => {
    if (task?.id) {
      await deleteTask(task.id);
      onClose();
    }
  };

  // Complete task handler
  const handleComplete = async () => {
    if (task?.id) {
      await completeTask(task.id);
      onClose();
    }
  };

  // Modal UI
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70">
      <div className="bg-[#18181b] text-white rounded-xl shadow-2xl w-full max-w-lg p-8 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white">&times;</button>
        <h2 className="text-2xl font-bold mb-4">{mode === 'create' ? 'Create Task' : 'Edit Task'}</h2>
        <div className="space-y-4">
          <div>
            <label className="block mb-1 font-semibold" htmlFor="task-name">Task Name</label>
            <input id="task-name" className="w-full p-2 rounded bg-[#23232a] text-white" placeholder="Task Name" value={taskName} onChange={e => setTaskName(e.target.value)} />
          </div>
          <div>
            <div className="flex items-center mb-1">
              <label className="font-semibold mr-2" htmlFor="description">Description</label>
              <button
                type="button"
                className="text-xs text-blue-400 underline border border-blue-400 rounded px-2 py-0.5 ml-auto focus:outline-none focus:ring-2 focus:ring-blue-400"
                style={{ minWidth: 70 }}
                onClick={() => setDescExpanded(e => !e)}
              >
                {descExpanded ? 'Collapse' : 'Expand'}
              </button>
            </div>
            <textarea
              id="description"
              className="w-full p-2 rounded bg-[#23232a] text-white transition-all"
              placeholder="Description"
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={descExpanded ? 8 : 2}
              style={descExpanded ? { minHeight: 120 } : { minHeight: 40 }}
            />
          </div>
          <div>
            <label className="block mb-1 font-semibold" htmlFor="deadline">Deadline</label>
            <input id="deadline" className="w-full p-2 rounded bg-[#23232a] text-white" type="date" value={deadline || ''} onChange={e => handleDeadlineChange(e.target.value)} />
            {deadlineError && <div className="text-red-400 text-sm mt-1">{deadlineError}</div>}
          </div>
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block mb-1 font-semibold" htmlFor="priority">Priority</label>
              <select id="priority" className="w-full p-2 rounded bg-[#23232a] text-white" value={priority} onChange={e => setPriority(e.target.value as TaskPriority)}>
                {priorities.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div className="flex-1">
              <label className="block mb-1 font-semibold" htmlFor="focus">Focus</label>
              <select id="focus" className="w-full p-2 rounded bg-[#23232a] text-white" value={focus} onChange={e => setFocus(e.target.value as TaskFocus)}>
                {focuses.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <div className="w-20">
              <label className="block mb-1 font-semibold" htmlFor="points">Points</label>
              <input id="points" className="w-full p-2 rounded bg-[#23232a] text-white" type="number" min={0} value={points} onChange={e => setPoints(Number(e.target.value))} placeholder="Points" />
              <div className="text-xs text-gray-400 italic mt-1">8 points = 1 day of work</div>
            </div>
          </div>
          <div>
            <div className="flex items-center mb-1">
              <label className="font-semibold mr-2" htmlFor="notes">Notes</label>
              <button
                type="button"
                className="text-xs text-blue-400 underline border border-blue-400 rounded px-2 py-0.5 ml-auto focus:outline-none focus:ring-2 focus:ring-blue-400"
                style={{ minWidth: 70 }}
                onClick={() => setNotesExpanded(e => !e)}
              >
                {notesExpanded ? 'Collapse' : 'Expand'}
              </button>
            </div>
            <textarea
              id="notes"
              className="w-full p-2 rounded bg-[#23232a] text-white transition-all"
              placeholder="Notes"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              rows={notesExpanded ? 8 : 2}
              style={notesExpanded ? { minHeight: 120 } : { minHeight: 40 }}
            />
          </div>
          {/* Dependencies */}
          <div>
            <label className="block mb-1 font-semibold">Dependencies</label>
            {depInputs.map((input, idx) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  className="flex-1 p-2 rounded bg-[#23232a] text-white"
                  placeholder="Search task..."
                  value={input.value}
                  onChange={e => handleDepInputChange(idx, e.target.value)}
                  list={`dep-tasks-${idx}`}
                />
                <datalist id={`dep-tasks-${idx}`}> 
                  {availableTasks
                    .filter(t => {
                      const val = input.value;
                      return t.task_name.toLowerCase().includes(val.toLowerCase());
                    })
                    .map(t => (
                      <option key={t.id} value={t.task_name} />
                    ))}
                </datalist>
                {/* Only show remove button if this field has a value */}
                {(input.value || input.task) && (
                  <button type="button" onClick={() => handleRemoveDependency(idx)} className="text-red-400">Remove</button>
                )}
              </div>
            ))}
            <button type="button" onClick={addDepField} className="text-blue-400">+ Add Dependency</button>
          </div>
          {/* Assigned Users */}
          <div>
            <label className="block mb-1 font-semibold">Assigned Users</label>
            {userInputs.map((input, idx) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  className="flex-1 p-2 rounded bg-[#23232a] text-white"
                  placeholder="Search user..."
                  value={input}
                  onChange={e => handleUserInputChange(idx, e.target.value)}
                  list={`user-list-${idx}`}
                  autoComplete="off"
                />
                <datalist id={`user-list-${idx}`}> 
                  {availableUsers
                    .filter(u => u.username.toLowerCase().includes(input.toLowerCase()))
                    .map(u => (
                      <option key={u.id} value={u.username} />
                    ))}
                </datalist>
                {/* Only show remove button if this field has a value */}
                {input && (
                  <button type="button" onClick={() => handleRemoveUser(idx)} className="text-red-400">Remove</button>
                )}
              </div>
            ))}
            <button type="button" onClick={addUserField} className="text-blue-400">+ Add User</button>
          </div>
        </div>
        <div className="flex flex-col gap-4 mt-8">
          {mode === 'edit' && (
            <>
              <div className="flex justify-between">
                <button onClick={handleDelete} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded">Delete</button>
                <div className="flex gap-2 ml-auto">
                  <button onClick={onClose} className="bg-gray-700 hover:bg-gray-800 text-white px-4 py-2 rounded">Cancel</button>
                  <button onClick={handleSubmit} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">Save</button>
                </div>
              </div>
              <button
                onClick={handleComplete}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded w-full font-semibold"
                disabled={!!task?.date_of_completion || !isLeaf}
              >
                {task?.date_of_completion ? 'Task Completed' : !isLeaf ? 'Only leaves can be completed' : 'Mark as Complete'}
              </button>
            </>
          )}
          {mode === 'create' && (
            <div className="flex gap-2 ml-auto justify-end">
              <button onClick={onClose} className="bg-gray-700 hover:bg-gray-800 text-white px-4 py-2 rounded">Cancel</button>
              <button onClick={handleSubmit} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">Create</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
