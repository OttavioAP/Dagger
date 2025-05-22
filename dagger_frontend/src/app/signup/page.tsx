"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { updateUserUserPost } from "@/client/sdk.gen";
import type { UpdateUserRequest } from "@/client/types.gen";

export default function SignupPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const req: UpdateUserRequest = {
        user: {
          username,
          id: "dummy-id-" + Math.random().toString(36).substring(2, 10),
        },
        action: "create",
      };
      await updateUserUserPost({ body: req });
      router.push("/");
    } catch (err: unknown) {
      const message =
        typeof err === 'object' && err !== null && 'message' in err
          ? String((err as { message?: unknown }).message)
          : "Signup failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-4">
      <form onSubmit={handleSignup} className="bg-white/5 rounded-xl p-8 shadow-lg w-full max-w-sm flex flex-col gap-6">
        <h1 className="text-2xl font-bold mb-2 text-center">Sign Up</h1>
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
          placeholder="Password (for show)"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          className="px-4 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-gradient-to-r from-blue-500 to-teal-400 hover:from-blue-600 hover:to-teal-500 text-white font-bold py-2 px-6 rounded-full shadow transition-all duration-200 disabled:opacity-50"
        >
          {loading ? "Signing up..." : "Sign Up"}
        </button>
        {error && <div className="text-red-400 text-center">{error}</div>}
      </form>
    </div>
  );
}
