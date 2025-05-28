"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import type { User } from '@/client/types.gen';

// Define the shape of the user
export type AuthUser = User & {
  password: string; // For demo purposes only; do not store plaintext passwords in production
};

// Define the context value type
type AuthContextType = {
  user: AuthUser | null;
  setUser: (user: AuthUser | null) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
