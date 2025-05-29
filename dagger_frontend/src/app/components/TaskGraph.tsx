// NOTE: You must install reactflow and dagre: npm install reactflow dagre
// For types: npm install --save-dev @types/dagre
import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, Edge, Node, Position, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import TaskNode from './TaskNode';
import type { DagWithDetails } from '../contexts/dag_context';
import type { Task, TaskPriority } from '@/client/types.gen';

const nodeWidth = 220;
const nodeHeight = 100;

const nodeTypes = {
  task: TaskNode,
};

interface TaskGraphProps {
  dags: DagWithDetails[];
  tasksDict: { [key: string]: Task };
  onNodeClick?: (taskId: string) => void;
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

function getLayoutedElements(nodes: Node[], edges: Edge[]) {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: 'LR' });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
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

const TaskGraph: React.FC<TaskGraphProps> = ({ dags, tasksDict, onNodeClick }) => {
  // Collect all task IDs that are part of any DAG
  const dagTaskIds = useMemo(() => {
    const ids = new Set<string>();
    dags.forEach(dag => {
      Object.keys(dag.nodes).forEach(id => ids.add(id));
    });
    return ids;
  }, [dags]);

  // Build nodes: all DAG nodes + orphan tasks
  const nodes: Node[] = useMemo(() => {
    const dagNodes: Node[] = [];
    dags.forEach(dag => {
      Object.values(dag.nodes).forEach(task => {
        dagNodes.push({
          id: task.id!,
          type: 'task',
          data: {
            label: task.task_name,
            priority: task.priority as TaskPriority,
            assigned_users: task.assigned_users,
          },
          position: { x: 0, y: 0 },
        });
      });
    });
    // Orphan tasks (not in any DAG)
    const orphanNodes: Node[] = Object.values(tasksDict)
      .filter(task => task.id && !dagTaskIds.has(task.id))
      .map(task => ({
        id: task.id!,
        type: 'task',
        data: {
          label: task.task_name,
          priority: task.priority as TaskPriority,
          assigned_users: [],
        },
        position: { x: 0, y: 0 },
      }));
    return [...dagNodes, ...orphanNodes];
  }, [dags, tasksDict, dagTaskIds]);

  // Build edges: all DAG edges
  const edges: Edge[] = useMemo(() => {
    const result: Edge[] = [];
    dags.forEach((dag, dagIndex) => {
      const color = getDagColor(dagIndex);
      Object.entries(dag.dag_graph).forEach(([from, tos]) => {
        (tos as string[]).forEach((to: string) => {
          result.push({
            id: `${from}->${to}`,
            source: to,
            target: from,
            animated: true,
            style: { stroke: color, strokeWidth: 2 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: color,
            },
          });
        });
      });
    });
    return result;
  }, [dags]);

  // Layout
  const layoutedNodes = useMemo(() => getLayoutedElements(nodes, edges), [nodes, edges]);

  return (
    <div style={{ width: '100%', height: '600px', background: '#18181b', borderRadius: '1rem' }}>
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
  );
};

export default TaskGraph;
