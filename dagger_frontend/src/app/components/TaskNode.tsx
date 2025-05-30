// NOTE: You must install reactflow: npm install reactflow
import React from 'react';
import type { NodeProps } from 'reactflow';
import { Handle, Position } from 'reactflow';
import { useTeam } from '../contexts/team_context';
import type { TaskPriority } from '@/client/types.gen';

// Priority color map
const priorityColor: Record<TaskPriority, string> = {
  LOW: 'bg-green-600',
  MEDIUM: 'bg-yellow-500',
  HIGH: 'bg-red-600',
  EMERGENCY: 'bg-black',
};

interface TaskNodeData {
  label: string;
  priority: TaskPriority;
  assigned_users: string[]; // user IDs
  date_of_completion?: string;
}

const TaskNode: React.FC<NodeProps<TaskNodeData>> = ({ data }) => {
  const { teamUsers } = useTeam();
  const collaborators = data.assigned_users
    .map((uid: string) => teamUsers.find(u => u.id === uid)?.username)
    .filter((name: string | undefined): name is string => Boolean(name));
  const isCompleted = !!data.date_of_completion;

  return (
    <div
      className={`rounded-lg p-4 shadow-md border-2
        ${isCompleted
          ? 'bg-gray-700 border-gray-500 text-gray-300'
          : `${priorityColor[data.priority]} border-[#35373B] text-white`}
      `}
    >
      <div className="font-bold text-lg truncate mb-2">{data.label}</div>
      <div className="text-xs text-gray-200 mb-1">Collaborators:</div>
      <div className="flex flex-wrap gap-1">
        {collaborators.length > 0 ? (
          collaborators.map((name: string) => (
            <span key={name} className="bg-gray-800 rounded px-2 py-0.5 text-xs">{name}</span>
          ))
        ) : (
          <span className="text-gray-400 italic">None</span>
        )}
      </div>
      {/* React Flow handles for edges */}
      <Handle type="target" position={Position.Left} className="w-2 h-2 bg-gray-400" />
      <Handle type="source" position={Position.Right} className="w-2 h-2 bg-gray-400" />
    </div>
  );
};

export default TaskNode;
