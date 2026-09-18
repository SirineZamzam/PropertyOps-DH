import type {
  ReactNode,
} from "react";

import { Navigate } from "react-router";

import { useAuth } from "../contexts/AuthContext";
import type {
  UserRole,
} from "../types/auth";


export function RoleRoute({
  role,
  children,
}: {
  role: UserRole;
  children: ReactNode;
}) {
  const {
    user,
    loading,
  } = useAuth();

  if (loading) {
    return null;
  }

  if (!user) {
    return (
      <Navigate
        to="/auth?mode=login"
        replace
      />
    );
  }

  if (user.role !== role) {
    return (
      <Navigate
        to={
          user.role === "OWNER"
            ? "/app/overview"
            : "/app/home"
        }
        replace
      />
    );
  }

  return children;
}