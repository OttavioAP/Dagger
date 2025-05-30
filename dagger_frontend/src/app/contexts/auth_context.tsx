"use client";

import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import type { User } from '@/types/shared';

// --- Cookie helpers ---
function setCookie(name: string, value: string, days: number) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
}

function getCookie(name: string) {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=');
    return parts[0] === name ? decodeURIComponent(parts[1]) : r
  }, '');
}

function deleteCookie(name: string) {
  document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
}
// --- End cookie helpers ---

// Define the context value type
type AuthContextType = {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  // Load user from cookie on mount
  useEffect(() => {
    const storedUser = getCookie('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse stored user from cookie:', e);
        deleteCookie('user');
      }
    }
  }, []);

  // Custom setUser that also updates cookie
  const setUserWithCookie = (newUser: User | null) => {
    if (newUser) {
      setCookie('user', JSON.stringify(newUser), 7); // 7 days expiry
    } else {
      deleteCookie('user');
    }
    setUser(newUser);
  };

  const logout = () => {
    deleteCookie('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser: setUserWithCookie, logout }}>
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
