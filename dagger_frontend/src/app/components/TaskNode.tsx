// NOTE: You must install reactflow: npm install reactflow
import React from 'react';
import type { NodeProps } from 'reactflow';
import { Handle, Position } from 'reactflow';
import { useTeam } from '../contexts/team_context';
import { useDag } from '../contexts/dag_context';
import type { TaskPriority } from '@/client/types.gen';

// Softer, pastel/muted gradients for priorities
const priorityGradientStyle: Record<TaskPriority, React.CSSProperties> = {
  LOW: { background: 'linear-gradient(135deg, #b9fbc0 0%, #6ec6a6 100%)' },
  MEDIUM: { background: 'linear-gradient(135deg, #fef9c3 0%, #fde68a 100%)' },
  HIGH: { background: 'linear-gradient(135deg, #fecaca 0%, #fca5a5 100%)' },
  EMERGENCY: { background: 'linear-gradient(135deg, #e0e7ef 0%, #a1a1aa 100%)' },
};

// White boundary text shadow
const whiteOutline = '0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff, 0 0 4px #fff';

function toSentenceCase(str: string) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

interface TaskNodeData {
  label: string;
  priority: TaskPriority;
  assigned_users: string[]; // user IDs
  date_of_completion?: string;
}

const TaskNode: React.FC<NodeProps<TaskNodeData>> = ({ data, id }) => {
  const { teamUsers } = useTeam();
  const { dags, computeAllLeafUrgencies } = useDag();
  const collaborators = data.assigned_users
    .map((uid: string) => teamUsers.find(u => u.id === uid)?.username)
    .filter((name: string | undefined): name is string => Boolean(name));
  const isCompleted = !!data.date_of_completion;
  const formattedLabel = toSentenceCase(data.label);

  // Find the DAG this task belongs to
  const dag = React.useMemo(() => dags.find(d => d.nodes[id]), [dags, id]);
  // Compute leaf urgencies for this DAG
  const leafUrgencies = React.useMemo(() => dag ? computeAllLeafUrgencies(dag) : {}, [dag, computeAllLeafUrgencies]);
  // If this task is a leaf, show its urgency
  const urgency = leafUrgencies[id];
  const isLeaf = urgency !== undefined;

  return (
    <div
      style={isCompleted
        ? { background: 'linear-gradient(135deg, #e0e7ef 0%, #a1a1aa 100%)', opacity: 0.7 }
        : priorityGradientStyle[data.priority]
      }
      className={`
        rounded-xl p-4 border-2 shadow-2xl outline outline-2 outline-white/30
        ${isCompleted ? 'border-gray-400' : 'border-white/40'}
        transition-all duration-300
      `}
    >
      <div
        className="font-extrabold text-lg mb-2 truncate"
        style={{ color: '#111', textShadow: whiteOutline }}
        title={data.label}
      >
        {formattedLabel}
      </div>
      {isLeaf && (
        <div className="text-xs font-bold text-blue-900 bg-blue-100 rounded px-2 py-0.5 mb-1 inline-block" title="Urgency score (lower is more urgent)">
          Urgency: {urgency.toFixed(1)}
        </div>
      )}
      <div
        className="text-xs mb-1 font-semibold"
        style={{ color: '#222', textShadow: whiteOutline }}
      >Collaborators:</div>
      <div className="flex flex-wrap gap-1">
        {collaborators.length > 0 ? (
          collaborators.map((name: string) => (
            <span
              key={name}
              className="bg-black/30 rounded px-2 py-0.5 text-xs font-bold"
              style={{ color: '#111', textShadow: whiteOutline }}
            >{name}</span>
          ))
        ) : (
          <span className="italic" style={{ color: '#222', textShadow: whiteOutline }}>None</span>
        )}
      </div>
      {/* React Flow handles for edges */}
      <Handle type="target" position={Position.Left} className="w-2 h-2 bg-white/60" />
      <Handle type="source" position={Position.Right} className="w-2 h-2 bg-white/60" />
    </div>
  );
};

export default TaskNode;
