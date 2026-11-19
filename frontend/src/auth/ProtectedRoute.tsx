
import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import type { UserRole, Permission } from "./roles";
import { hasPermission } from "./roles";

interface ProtectedRouteProps {
  role: UserRole | null;
  permission: Permission;
  children: ReactNode;
}

export default function ProtectedRoute({
  role,
  permission,
  children,
}: ProtectedRouteProps) {
  if (!role) {
    return <Navigate to="/login" replace />;
  }

  if (!hasPermission(role, permission)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
