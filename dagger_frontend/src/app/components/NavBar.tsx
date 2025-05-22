'use client';

import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/app/contexts/auth_context";

export default function NavBar() {
  const { user, logout } = useAuth();

  return (
    <nav className="w-full bg-gray-900 text-white shadow-md">
      <div className="container mx-auto flex items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-3">
          <Image
            src="/Dagger_Logo.png"
            alt="Dagger Logo"
            width={40}
            height={40}
            className="rounded-full bg-white/10"
            priority
          />
          <span className="text-xl font-bold tracking-wide">Dagger</span>
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/" className="hover:text-teal-400 transition">Home</Link>
          <Link href="/daggerview" className="hover:text-teal-400 transition">DAG View</Link>
          {user ? (
            <>
              <Link href="/profile" className="hover:text-teal-400 transition">Profile</Link>
              <button
                onClick={logout}
                className="ml-4 px-4 py-2 bg-teal-500 hover:bg-teal-600 rounded text-white font-semibold transition"
              >
                Logout
              </button>
            </>
          ) : (
            <Link href="/login" className="bg-teal-500 hover:bg-teal-600 px-4 py-2 rounded text-white font-semibold transition">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
