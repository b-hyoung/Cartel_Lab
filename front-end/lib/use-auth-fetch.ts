"use client";

import { useSession } from "next-auth/react";
import { useCallback } from "react";
import { API_BASE_URL } from "./api-client";

export function useAuthFetch() {
  const { data: session } = useSession();

  const authFetch = useCallback(
    async (endpoint: string, options: RequestInit = {}) => {
      const token = session?.user?.access_token;

      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(options.headers as Record<string, string>),
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`API 오류: ${response.status}`);
      }

      return response.json();
    },
    [session]
  );

  return authFetch;
}
