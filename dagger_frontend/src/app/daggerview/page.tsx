"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/contexts/auth_context";
import { useDag } from "@/app/contexts/dag_context";
import { useTeam } from "@/app/contexts/team_context";
import TaskGraph from "../components/TaskGraph";
import TaskModal from "../components/TaskModal";

export default function DaggerviewPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { dags, loading, tasksDict, refreshDags } = useDag();
  const { refreshTeamsAndUsers } = useTeam();


  const [selectedDagId, setSelectedDagId] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>("create");
  const [editTaskId, setEditTaskId] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      router.replace("/login");
    }
    refreshDags();
    refreshTeamsAndUsers();
  }, [user, router, refreshDags, refreshTeamsAndUsers]);

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
    <div className="min-h-screen w-screen flex flex-row bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-0">
      {/* Center: TaskGraph (now full viewport) */}
      <TaskGraph
        dags={dags}
        tasksDict={tasksDict}
        onNodeClick={handleNodeClick}
        onCreateClick={handleCreateClick}
      />
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
