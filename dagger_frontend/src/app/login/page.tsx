"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/contexts/auth_context";
import { toast } from "react-toastify";
import type { User } from "@/types/shared";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const { setUser, user } = useAuth();

  useEffect(() => {
    if (user?.team_id) {
      router.push("/daggerview");
    }
  }, [user?.team_id, router]);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/user?username=${encodeURIComponent(username)}`);
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "User not found");
      }
      const userData = await res.json();
      const user = userData.data ?? userData; // handle both {data: user} and user directly
      console.log('Login response:', user); // Debug log
      
      // Ensure we have all required fields
      if (!user.username || !user.id || !user.team_id) {
        throw new Error("Invalid user data received");
      }

      setUser(user);
    } catch (err: unknown) {
      const message =
        typeof err === 'object' && err !== null && 'message' in err
          ? String((err as { message?: unknown }).message)
          : "Login failed";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-4">
      <form onSubmit={handleLogin} className="bg-white/5 rounded-xl p-8 shadow-lg w-full max-w-sm flex flex-col gap-6">
        <h1 className="text-2xl font-bold mb-2 text-center">Login</h1>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
          className="px-4 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="password"
          placeholder="Password"
          required
          className="px-4 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-gradient-to-r from-blue-500 to-teal-400 hover:from-blue-600 hover:to-teal-500 text-white font-bold py-2 px-6 rounded-full shadow transition-all duration-200 disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
        {error && <div className="text-red-400 text-center">{error}</div>}
      </form>
    </div>
  );
}
