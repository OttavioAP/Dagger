"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/contexts/auth_context";
import { useDag } from "@/app/contexts/dag_context";
import TaskGraph from "../components/TaskGraph";
import TaskModal from "../components/TaskModal";

export default function DaggerviewPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { dags, loading, tasksDict, refreshDags } = useDag();

  const [selectedDagId, setSelectedDagId] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>("create");
  const [editTaskId, setEditTaskId] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      router.replace("/login");
    }
    refreshDags();
  }, [user, router, refreshDags]);

  // Set default selected DAG when dags load
  useEffect(() => {
    if (dags.length > 0 && !selectedDagId) {
      setSelectedDagId(dags[0].dag_id || null);
    }
  }, [dags, selectedDagId]);

  if (!user) {
    return null; // Optionally, show a loading spinner here
  }

  const handleNodeClick = (taskId: string) => {
    setEditTaskId(taskId);
    setModalMode("edit");
    setShowModal(true);
  };

  const handleCreateClick = () => {
    setEditTaskId(null);
    setModalMode("create");
    setShowModal(true);
  };

  return (
    <div className="min-h-screen flex flex-row bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-4">
      {/* Center: TaskGraph */}
      <div className="flex-1 flex flex-col items-center justify-center py-12">
        {loading ? (
          <div className="text-gray-400">Loading DAGs...</div>
        ) : (dags.length > 0 || Object.keys(tasksDict).length > 0) ? (
          <TaskGraph dags={dags} tasksDict={tasksDict} onNodeClick={handleNodeClick} />
        ) : (
          <div className="w-full h-[600px] flex items-center justify-center bg-gray-800 rounded-lg border-2 border-dashed border-gray-600">
            <span className="text-gray-500 text-lg">No tasks or DAGs available</span>
          </div>
        )}
      </div>
      {/* Right: Create Task button */}
      <div className="w-64 flex flex-col items-end justify-start pt-12 pl-6">
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded font-semibold shadow-lg"
          onClick={handleCreateClick}
        >
          + Create Task
        </button>
      </div>
      {/* Task Modal */}
      {showModal && (
        <TaskModal
          mode={modalMode}
          task={modalMode === 'edit' && editTaskId ? tasksDict[editTaskId] : undefined}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
