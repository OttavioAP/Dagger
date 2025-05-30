// NOTE: You must install reactflow and dagre: npm install reactflow dagre
// For types: npm install --save-dev @types/dagre
import React, { useMemo, useState } from 'react';
import ReactFlow, { Background, Controls, Edge, Node, Position, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import TaskNode from './TaskNode';
import type { DagWithDetails } from '../contexts/dag_context';
import type { Task, TaskPriority } from '@/client/types.gen';
import { useDag } from '../contexts/dag_context';
import { useTeam } from '../contexts/team_context';
import { format, subWeeks } from 'date-fns';
import { useAuth } from '../contexts/auth_context';

const nodeWidth = 220;
const nodeHeight = 100;

const nodeTypes = {
  task: TaskNode,
};

interface TaskGraphProps {
  dags: DagWithDetails[];
  tasksDict: { [key: string]: Task };
  onNodeClick?: (taskId: string) => void;
  onCreateClick?: () => void;
}

// Color palette for DAGs
const dagColors = [
  '#60a5fa', // blue
  '#f59e42', // orange
  '#10b981', // green
  '#f43f5e', // red
  '#a78bfa', // purple
  '#fbbf24', // yellow
  '#6366f1', // indigo
  '#14b8a6', // teal
];

const getDagColor = (dagIndex: number) => dagColors[dagIndex % dagColors.length];

// Arrow color palette (soft, visually distinct)
const arrowColors = [
  '#60a5fa', // blue
  '#f59e42', // orange
  '#10b981', // green
  '#f43f5e', // red
  '#a78bfa', // purple
  '#fbbf24', // yellow
  '#6366f1', // indigo
  '#14b8a6', // teal
  '#e879f9', // pink
  '#f472b6', // rose
  '#38bdf8', // sky
  '#facc15', // gold
  '#4ade80', // mint
  '#f87171', // coral
  '#a3e635', // lime
  '#fcd34d', // amber
];

// Helper: Compute level (number of dependencies from leaf) for each node
function computeTaskLevels(dag: DagWithDetails): Record<string, number> {
  const levels: Record<string, number> = {};
  const getLevel = (id: string): number => {
    if (levels[id] !== undefined) return levels[id];
    const deps = dag.dag_graph[id] || [];
    if (deps.length === 0) {
      levels[id] = 0;
    } else {
      levels[id] = Math.max(...deps.map(getLevel)) + 1;
    }
    return levels[id];
  };
  Object.keys(dag.nodes).forEach(getLevel);
  return levels;
}

function getLayoutedElements(nodes: Node[], edges: Edge[], dag?: DagWithDetails) {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({
    rankdir: 'LR',
    nodesep: 180,
    ranksep: 320,
  });

  // If a DAG is provided, compute levels and assign as rank
  let levels: Record<string, number> = {};
  if (dag) {
    levels = computeTaskLevels(dag);
  }

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: nodeWidth,
      height: nodeHeight,
      ...(levels[node.id] !== undefined ? { rank: levels[node.id] } : {}),
    });
  });
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  return nodes.map((node) => {
    const { x, y } = dagreGraph.node(node.id);
    return {
      ...node,
      position: { x, y },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    };
  });
}

const TaskGraph: React.FC<TaskGraphProps> = ({ dags, tasksDict, onNodeClick, onCreateClick }) => {
  const { currentTeam, teamUsers } = useTeam();
  const { get_task_users } = useDag();
  const { user } = useAuth();

  // Filter modal state
  const [showFilter, setShowFilter] = useState(false);
  const [filterDate, setFilterDate] = useState(format(subWeeks(new Date(), 2), 'yyyy-MM-dd'));
  const [filterMine, setFilterMine] = useState(false);
  const [filterUrgency, setFilterUrgency] = useState<'ALL' | TaskPriority>('ALL');

  // Open/close filter modal
  const openFilter = () => setShowFilter(true);
  const closeFilter = () => setShowFilter(false);

  // Filtering logic
  const filteredTasksDict = useMemo(() => {
    const result: { [key: string]: Task } = {};
    Object.values(tasksDict).forEach(task => {
      // Filter by mine using get_task_users from dag_context
      if (filterMine && (!user || !get_task_users(task.id || '').includes(user.id))) return;
      // Filter by urgency
      if (filterUrgency !== 'ALL' && task.priority !== filterUrgency) return;
      // Filter by date
      const filterDateObj = new Date(filterDate);
      const deadline = task.deadline ? new Date(task.deadline) : null;
      if (
        deadline && deadline < filterDateObj && task.date_of_completion
      ) {
        // Deadline is before filter date and task is completed, skip
        return;
      }
      result[task.id!] = task;
    });
    return result;
  }, [tasksDict, filterMine, filterUrgency, filterDate, user, get_task_users]);

  // 1. Only show DAGs with at least one incomplete task (and belong to current team)
  const visibleDags = useMemo(() =>
    dags.filter(dag => dag.team_id === currentTeam?.id && Object.values(dag.nodes).some(task => filteredTasksDict[task.id!] && !task.date_of_completion)),
    [dags, currentTeam, filteredTasksDict]
  );

  // 2. Collect all task IDs that are in visible DAGs
  const visibleDagTaskIds = useMemo(() => {
    const ids = new Set<string>();
    visibleDags.forEach(dag => {
      Object.keys(dag.nodes).forEach(id => ids.add(id));
    });
    return ids;
  }, [visibleDags]);

  // Build nodes: all DAG nodes (from visible DAGs) + orphan tasks (not in any visible DAG and not completed, and belong to current team)
  const nodes: Node[] = useMemo(() => {
    const dagNodes: Node[] = [];
    visibleDags.forEach(dag => {
      Object.values(dag.nodes).forEach(task => {
        if (!filteredTasksDict[task.id!]) return;
        dagNodes.push({
          id: task.id!,
          type: 'task',
          data: {
            label: task.task_name,
            priority: task.priority as TaskPriority,
            assigned_users: get_task_users(task.id!),
            date_of_completion: task.date_of_completion,
          },
          position: { x: 0, y: 0 },
        });
      });
    });
    // Orphan tasks: not in any visible DAG, and in filteredTasksDict, and belong to current team
    const orphanNodes: Node[] = Object.values(filteredTasksDict)
      .filter(task => task.id && !visibleDagTaskIds.has(task.id) && task.team_id === currentTeam?.id)
      .map(task => ({
        id: task.id!,
        type: 'task',
        data: {
          label: task.task_name,
          priority: task.priority as TaskPriority,
          assigned_users: [],
          date_of_completion: task.date_of_completion,
        },
        position: { x: 0, y: 0 },
      }));
    return [...dagNodes, ...orphanNodes];
  }, [visibleDags, filteredTasksDict, visibleDagTaskIds, currentTeam]);

  // Build edges: all DAG edges (from filtered DAGs)
  const edges: Edge[] = useMemo(() => {
    const result: Edge[] = [];
    let colorIdx = 0;
    visibleDags.forEach((dag, dagIndex) => {
      Object.entries(dag.dag_graph).forEach(([from, tos]) => {
        (tos as string[]).forEach((to: string) => {
          const color = arrowColors[colorIdx % arrowColors.length];
          colorIdx++;
          result.push({
            id: `${from}->${to}`,
            source: to,
            target: from,
            animated: true,
            style: { stroke: color, strokeWidth: 6 }, // 3x thicker (was 2)
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: color,
            },
          });
        });
      });
    });
    return result;
  }, [visibleDags]);

  // Layout
  const layoutedNodes = useMemo(() => getLayoutedElements(nodes, edges, visibleDags[0]), [nodes, edges, visibleDags]);

  return (
    <div className="relative w-screen" style={{ height: 'calc(100vh - 4rem)', background: '#18181b', borderRadius: '1rem' }}>
      <div className="absolute inset-0">
        <ReactFlow
          nodes={layoutedNodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          panOnScroll
          zoomOnScroll
          defaultEdgeOptions={{ type: 'smoothstep' }}
          onNodeClick={(_event, node) => onNodeClick?.(node.id)}
        >
          <Background color="#23232a" gap={24} />
          <Controls />
        </ReactFlow>
      </div>
      {/* Centered Create Task button at the bottom, and Filter button next to it */}
      <div className="absolute left-1/2 transform -translate-x-1/2 z-10 flex gap-4" style={{ bottom: '2rem' }}>
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded font-semibold shadow-lg"
          onClick={onCreateClick}
        >
          + Create Task
        </button>
        <button
          className="bg-gray-700 hover:bg-gray-800 text-white px-6 py-3 rounded font-semibold shadow-lg"
          onClick={openFilter}
        >
          Filter
        </button>
      </div>
      {/* Filter Modal */}
      {showFilter && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
          <div className="bg-[#232324] p-8 rounded-lg shadow-xl w-full max-w-md relative">
            <button className="absolute top-2 right-2 text-gray-400 hover:text-white" onClick={closeFilter}>&times;</button>
            <h2 className="text-xl font-bold mb-4">Filter Tasks</h2>
            <div className="mb-4">
              <label className="block mb-1 font-semibold">Show tasks assigned to me only</label>
              <input type="checkbox" checked={filterMine} onChange={e => setFilterMine(e.target.checked)} />
            </div>
            <div className="mb-4">
              <label className="block mb-1 font-semibold">Urgency</label>
              <select value={filterUrgency} onChange={e => setFilterUrgency(e.target.value as any)} className="w-full p-2 rounded bg-[#18181b] text-white">
                <option value="ALL">All</option>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="EMERGENCY">Emergency</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="block mb-1 font-semibold">Show tasks active after</label>
              <input
                type="date"
                value={filterDate}
                max={format(new Date(), 'yyyy-MM-dd')}
                onChange={e => setFilterDate(e.target.value)}
                className="w-full p-2 rounded bg-[#18181b] text-white"
              />
              <div className="text-xs text-gray-400 mt-1">(Only dates in the past allowed)</div>
            </div>
            <div className="flex justify-end">
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded" onClick={closeFilter}>Apply</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskGraph;
