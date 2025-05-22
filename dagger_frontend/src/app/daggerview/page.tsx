"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/contexts/auth_context";

export default function DaggerviewPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.replace("/login");
    }
  }, [user, router]);

  if (!user) {
    return null; // Optionally, show a loading spinner here
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-4">
      <div className="bg-white/5 rounded-xl p-8 shadow-lg w-full max-w-2xl flex flex-col items-center gap-6">
        <h1 className="text-3xl font-bold mb-2 text-center">Task DAG View</h1>
        <p className="text-gray-300 text-center max-w-lg mb-4">
          Visualize your tasks as a Directed Acyclic Graph (DAG). This view will help you understand dependencies and optimize your workflow.
        </p>
        <div className="w-full h-64 flex items-center justify-center bg-gray-800 rounded-lg border-2 border-dashed border-gray-600">
          <span className="text-gray-500 text-lg">[ DAG Visualization Placeholder ]</span>
        </div>
      </div>
    </div>
  );
}
