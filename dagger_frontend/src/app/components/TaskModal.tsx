import React, { useState, useMemo } from 'react';
import { useDag } from '../contexts/dag_context';
import { useTeam } from '../contexts/team_context';
import type { Task, TaskRequest, TaskPriority, TaskFocus } from '@/client/types.gen';

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
  } = useDag();
  const { teamUsers } = useTeam();

  // Form state
  const [taskName, setTaskName] = useState(task?.task_name || '');
  const [description, setDescription] = useState(task?.description || '');
  const [deadline, setDeadline] = useState(task?.deadline || '');
  const [priority, setPriority] = useState<TaskPriority>(task?.priority || 'LOW');
  const [focus, setFocus] = useState<TaskFocus>(task?.focus || 'LOW');
  const [points, setPoints] = useState<number>(task?.points || 0);
  const [notes, setNotes] = useState(task?.notes || '');

  // Dependency and user assignment state
  const [dependencies, setDependencies] = useState<string[]>([]); // task ids
  const [assignedUsers, setAssignedUsers] = useState<string[]>([]); // user ids

  // For autocomplete
  const [depInputs, setDepInputs] = useState(['']);
  const [userInputs, setUserInputs] = useState(['']);

  // Helper: get all tasks except this one
  const availableTasks = useMemo(() =>
    Object.values(tasksDict).filter(t => t.id !== task?.id),
    [tasksDict, task?.id]
  );

  // Helper: get all users
  const availableUsers = Array.isArray(teamUsers) ? teamUsers : [];

  // Handlers for dependencies
  const handleDepInputChange = (idx: number, value: string) => {
    const newInputs = [...depInputs];
    newInputs[idx] = value;
    setDepInputs(newInputs);
  };
  const addDepField = () => setDepInputs([...depInputs, '']);
  const removeDepField = (idx: number) => setDepInputs(depInputs.filter((_, i) => i !== idx));

  // Handlers for users
  const handleUserInputChange = (idx: number, value: string) => {
    const newInputs = [...userInputs];
    newInputs[idx] = value;
    setUserInputs(newInputs);
  };
  const addUserField = () => setUserInputs([...userInputs, '']);
  const removeUserField = (idx: number) => setUserInputs(userInputs.filter((_, i) => i !== idx));

  // Modal logic
  const handleSubmit = async () => {
    const request: TaskRequest = {
      task_id: task?.id || undefined,
      task_name: taskName,
      team_id: task?.team_id, // or get from context if needed
      deadline,
      points,
      priority,
      focus,
      description,
      notes,
      action: mode === 'create' ? 'create' : 'edit',
    };
    if (mode === 'create') {
      await createTask(request);
      // handle dependencies: if any, create dag or add edge
      // (pseudo: if no dag exists, createDag, else addEdge)
      // handle user assignments
    } else {
      await updateTask(request);
      // handle dependencies: addEdge/deleteEdge as needed
      // handle user assignments
    }
    onClose();
  };

  const handleDelete = async () => {
    if (task?.id) {
      await deleteTask(task.id);
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
            <label className="block mb-1 font-semibold" htmlFor="description">Description</label>
            <textarea id="description" className="w-full p-2 rounded bg-[#23232a] text-white" placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} />
          </div>
          <div>
            <label className="block mb-1 font-semibold" htmlFor="deadline">Deadline</label>
            <input id="deadline" className="w-full p-2 rounded bg-[#23232a] text-white" type="date" value={deadline || ''} onChange={e => setDeadline(e.target.value)} />
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
            </div>
          </div>
          <div>
            <label className="block mb-1 font-semibold" htmlFor="notes">Notes</label>
            <textarea id="notes" className="w-full p-2 rounded bg-[#23232a] text-white" placeholder="Notes" value={notes} onChange={e => setNotes(e.target.value)} />
          </div>
          {/* Dependencies */}
          <div>
            <label className="block mb-1 font-semibold">Dependencies</label>
            {depInputs.map((input, idx) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  className="flex-1 p-2 rounded bg-[#23232a] text-white"
                  placeholder="Search task..."
                  value={input}
                  onChange={e => handleDepInputChange(idx, e.target.value)}
                  list={`dep-tasks-${idx}`}
                />
                <datalist id={`dep-tasks-${idx}`}>
                  {availableTasks.filter(t => t.task_name.toLowerCase().includes(input.toLowerCase())).map(t => (
                    <option key={t.id} value={t.task_name} />
                  ))}
                </datalist>
                <button type="button" onClick={() => removeDepField(idx)} className="text-red-400">Remove</button>
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
                />
                <datalist id={`user-list-${idx}`}>
                  {availableUsers.filter(u => u.username.toLowerCase().includes(input.toLowerCase())).map(u => (
                    <option key={u.id} value={u.username} />
                  ))}
                </datalist>
                <button type="button" onClick={() => removeUserField(idx)} className="text-red-400">Remove</button>
              </div>
            ))}
            <button type="button" onClick={addUserField} className="text-blue-400">+ Add User</button>
          </div>
        </div>
        <div className="flex justify-between mt-8">
          {mode === 'edit' && (
            <button onClick={handleDelete} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded">Delete</button>
          )}
          <div className="flex gap-2 ml-auto">
            <button onClick={onClose} className="bg-gray-700 hover:bg-gray-800 text-white px-4 py-2 rounded">Cancel</button>
            <button onClick={handleSubmit} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
              {mode === 'create' ? 'Create' : 'Save'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
