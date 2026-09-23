import type {
  ReactNode,
} from "react";

import {
  Navigate,
} from "react-router";

import {
  useAuth,
} from "../contexts/AuthContext";

import type {
  UserRole,
} from "../types/auth";


function homeForRole(
  role: UserRole,
) {
  if (role === "ADMIN") {
    return "/app/admin/overview";
  }

  if (role === "OWNER") {
    return "/app/overview";
  }

  return "/app/home";
}


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
          homeForRole(
            user.role,
          )
        }
        replace
      />
    );
  }

  return children;
}
