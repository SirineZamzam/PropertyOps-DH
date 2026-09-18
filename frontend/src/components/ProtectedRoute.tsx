import type {
  ReactNode,
} from "react";

import {
  Navigate,
} from "react-router";

import { useAuth } from "../contexts/AuthContext";
import type {
  UserRole,
} from "../types/auth";


interface ProtectedRouteProps {
  children: ReactNode;
  role?: UserRole;
}


export function ProtectedRoute({
  children,
  role,
}: ProtectedRouteProps) {
  const {
    user,
    loading,
  } = useAuth();

  if (loading) {
    return (
      <div className="grid min-h-screen place-items-center bg-canvas">
        <div className="flex items-center gap-3 text-sm font-medium text-forest/60">
          <div className="size-5 animate-spin rounded-full border-2 border-mist border-t-forest" />
          Loading workspace...
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <Navigate
        to="/auth?mode=login"
        replace
      />
    );
  }

  if (
    role &&
    user.role !== role
  ) {
    return (
      <Navigate
        to="/app"
        replace
      />
    );
  }

  return children;
}