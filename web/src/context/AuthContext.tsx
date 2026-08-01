"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";

interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  github_connected: boolean;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "synkora_access_token";
const REFRESH_KEY = "synkora_refresh_token";

function saveTokens(tokens: AuthTokens) {
  localStorage.setItem(TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // ── Fetch current user on mount ─────────────────────────────
  const fetchUser = useCallback(async () => {
    try {
      const response = await api.get<User>("/api/v1/auth/me");
      if (response.success && response.data) {
        setUser(response.data);
      } else {
        setUser(null);
        clearTokens();
      }
    } catch {
      setUser(null);
      clearTokens();
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      fetchUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [fetchUser]);

  // ── Login ───────────────────────────────────────────────────
  const login = async (email: string, password: string) => {
    const response = await api.post<{ tokens: AuthTokens; user: User }>(
      "/api/v1/auth/login",
      { email, password },
    );

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || "Login failed");
    }

    saveTokens(response.data.tokens);
    setUser(response.data.user);
  };

  // ── Register ────────────────────────────────────────────────
  const register = async (
    email: string,
    fullName: string,
    password: string,
  ) => {
    const response = await api.post<{ tokens: AuthTokens; user: User }>(
      "/api/v1/auth/register",
      { email, full_name: fullName, password },
    );

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || "Registration failed");
    }

    saveTokens(response.data.tokens);
    setUser(response.data.user);
  };

  // ── Logout ──────────────────────────────────────────────────
  const logout = () => {
    clearTokens();
    setUser(null);
  };

  // ── Refresh ─────────────────────────────────────────────────
  const refreshAuth = async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      logout();
      return;
    }

    const response = await api.post<{ tokens: AuthTokens; user: User }>(
      "/api/v1/auth/refresh",
      { refresh_token: refreshToken },
    );

    if (response.success && response.data) {
      saveTokens(response.data.tokens);
      setUser(response.data.user);
    } else {
      logout();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
