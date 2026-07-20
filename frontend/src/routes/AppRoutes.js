import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { ProtectedLayout } from "@/layouts/ProtectedLayout";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
// ◄— Import your actual feature pages here instead of stubs
import { ConsultantListPage } from "@/features/consultants/pages/ConsultantListPage";
import { RequirementListPage } from "@/features/requirements/pages/RequirementListPage";
import { SubmissionListPage } from "@/features/submissions/pages/SubmissionListPage";
const SettingsView = () => _jsx("div", { style: { padding: 24 }, children: _jsx("h3", { children: "System Configuration & Layout Parameters" }) });
const AdminView = () => _jsx("div", { style: { padding: 24 }, children: _jsx("h3", { children: "Platform Level Administration Controls" }) });
const AccessDeniedView = () => _jsx("div", { style: { padding: 24, color: "red" }, children: _jsx("h3", { children: "Access Denied: Insufficient Role Privileges" }) });
const RoleGuard = ({ allowedRoles, children }) => {
    const { isAuthenticated, user } = useAuthStore();
    if (!isAuthenticated)
        return _jsx(Navigate, { to: "/login", replace: true });
    if (user && !allowedRoles.includes(user.role))
        return _jsx(Navigate, { to: "/unauthorized", replace: true });
    return children;
};
export const AppRoutes = () => {
    return (_jsxs(Routes, { children: [_jsx(Route, { path: "/login", element: _jsx(LoginPage, {}) }), _jsx(Route, { path: "/unauthorized", element: _jsx(AccessDeniedView, {}) }), _jsxs(Route, { path: "/", element: _jsx(ProtectedLayout, {}), children: [_jsx(Route, { index: true, element: _jsx(Navigate, { to: "/dashboard", replace: true }) }), _jsx(Route, { path: "dashboard", element: _jsx(RoleGuard, { allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], children: _jsx(DashboardPage, {}) }) }), _jsx(Route, { path: "consultants", element: _jsx(RoleGuard, { allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], children: _jsx(ConsultantListPage, {}) }) }), _jsx(Route, { path: "requirements", element: _jsx(RoleGuard, { allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], children: _jsx(RequirementListPage, {}) }) }), _jsx(Route, { path: "submissions", element: _jsx(RoleGuard, { allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], children: _jsx(SubmissionListPage, {}) }) }), _jsx(Route, { path: "settings", element: _jsx(RoleGuard, { allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], children: _jsx(SettingsView, {}) }) }), _jsx(Route, { path: "admin", element: _jsx(RoleGuard, { allowedRoles: ["ADMIN"], children: _jsx(AdminView, {}) }) })] }), _jsx(Route, { path: "*", element: _jsx(Navigate, { to: "/dashboard", replace: true }) })] }));
};
