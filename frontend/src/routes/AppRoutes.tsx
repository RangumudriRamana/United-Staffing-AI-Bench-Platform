import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore, UserRole } from "@/store/authStore";
import { ProtectedLayout } from "@/layouts/ProtectedLayout";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";

// ◄— Import your actual feature pages here instead of stubs
import { ConsultantListPage } from "@/features/consultants/pages/ConsultantListPage";
import { RequirementListPage } from "@/features/requirements/pages/RequirementListPage";
import { SubmissionListPage } from "@/features/submissions/pages/SubmissionListPage";

const SettingsView = () => <div style={{ padding: 24 }}><h3>System Configuration & Layout Parameters</h3></div>;
const AdminView = () => <div style={{ padding: 24 }}><h3>Platform Level Administration Controls</h3></div>;
const AccessDeniedView = () => <div style={{ padding: 24, color: "red" }}><h3>Access Denied: Insufficient Role Privileges</h3></div>;

interface GuardProps {
  allowedRoles: UserRole[];
  children: React.ReactElement;
}

const RoleGuard: React.FC<GuardProps> = ({ allowedRoles, children }) => {
  const { isAuthenticated, user } = useAuthStore();
  
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user && !allowedRoles.includes(user.role)) return <Navigate to="/unauthorized" replace />;
  
  return children;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/unauthorized" element={<AccessDeniedView />} />

      <Route path="/" element={<ProtectedLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        <Route path="dashboard" element={<RoleGuard allowedRoles={["ADMIN", "MANAGER", "RECRUITER"]}><DashboardPage /></RoleGuard>} />
        
        {/* ◄— Hooking up the real module pages */}
        <Route path="consultants" element={<RoleGuard allowedRoles={["ADMIN", "MANAGER", "RECRUITER"]}><ConsultantListPage /></RoleGuard>} />
        <Route path="requirements" element={<RoleGuard allowedRoles={["ADMIN", "MANAGER", "RECRUITER"]}><RequirementListPage /></RoleGuard>} />
        <Route path="submissions" element={<RoleGuard allowedRoles={["ADMIN", "MANAGER", "RECRUITER"]}><SubmissionListPage /></RoleGuard>} />
        
        <Route path="settings" element={<RoleGuard allowedRoles={["ADMIN", "MANAGER", "RECRUITER"]}><SettingsView /></RoleGuard>} />
        <Route path="admin" element={<RoleGuard allowedRoles={["ADMIN"]}><AdminView /></RoleGuard>} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};