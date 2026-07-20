import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import Box from "@mui/material/Box";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import IconButton from "@mui/material/IconButton";
import Avatar from "@mui/material/Avatar";
import MenuIcon from "@mui/icons-material/Menu";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import AssignmentIcon from "@mui/icons-material/Assignment";
import SendIcon from "@mui/icons-material/Send";
import SettingsIcon from "@mui/icons-material/Settings";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import { useUIStore } from "@/store/uiStore";
import { useAuthStore } from "@/store/authStore";
const DRAWER_WIDTH = 260;
export const ProtectedLayout = () => {
    const { sidebarOpen, toggleSidebar } = useUIStore();
    const { user, clearSession } = useAuthStore();
    const navigate = useNavigate();
    const location = useLocation();
    const navigationConfig = [
        { text: "Dashboard", path: "/dashboard", icon: _jsx(DashboardIcon, {}), roles: ["ADMIN", "MANAGER", "RECRUITER"] },
        { text: "Consultants", path: "/consultants", icon: _jsx(PeopleIcon, {}), roles: ["ADMIN", "MANAGER", "RECRUITER"] },
        { text: "Requirements", path: "/requirements", icon: _jsx(AssignmentIcon, {}), roles: ["ADMIN", "MANAGER", "RECRUITER"] },
        { text: "Submissions", path: "/submissions", icon: _jsx(SendIcon, {}), roles: ["ADMIN", "MANAGER", "RECRUITER"] },
        { text: "Settings", path: "/settings", icon: _jsx(SettingsIcon, {}), roles: ["ADMIN", "MANAGER", "RECRUITER"] },
        { text: "Administration", path: "/admin", icon: _jsx(AdminPanelSettingsIcon, {}), roles: ["ADMIN"] },
    ];
    return (_jsxs(Box, { sx: { display: "flex", minHeight: "100vh" }, children: [_jsx(AppBar, { position: "fixed", sx: { zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: "#1976d2" }, children: _jsxs(Toolbar, { sx: { justifyContent: "space-between" }, children: [_jsxs(Box, { sx: { display: "flex", alignItems: "center", gap: 1 }, children: [_jsx(IconButton, { color: "inherit", onClick: toggleSidebar, edge: "start", children: _jsx(MenuIcon, {}) }), _jsx(Typography, { variant: "h6", noWrap: true, component: "div", sx: { fontWeight: "bold" }, children: "United Staffing AI Platform" })] }), _jsxs(Box, { sx: { display: "flex", alignItems: "center", gap: 2 }, children: [_jsxs(Typography, { variant: "body2", sx: { opacity: 0.9 }, children: [user?.firstName || "System Operator", " (", user?.role || "ADMIN", ")"] }), _jsx(Avatar, { sx: { bgcolor: "#2196f3", width: 32, height: 32 }, children: "U" }), _jsx(IconButton, { color: "inherit", onClick: () => { clearSession(); navigate("/login"); }, children: _jsx(ExitToAppIcon, {}) })] })] }) }), _jsx(Drawer, { variant: "permanent", sx: {
                    width: sidebarOpen ? DRAWER_WIDTH : 64,
                    flexShrink: 0,
                    "& .MuiDrawer-paper": {
                        width: sidebarOpen ? DRAWER_WIDTH : 64,
                        boxSizing: "border-box",
                        top: 64,
                        height: "calc(100vh - 64px)",
                        overflowX: "hidden",
                        transition: "width 0.2s ease-in-out",
                    },
                }, children: _jsx(List, { children: navigationConfig
                        .filter((item) => !user || item.roles.includes(user.role))
                        .map((item) => {
                        const isActive = location.pathname === item.path;
                        return (_jsxs(ListItemButton, { onClick: () => navigate(item.path), selected: isActive, sx: { minHeight: 48, px: 2.5 }, children: [_jsx(ListItemIcon, { sx: { minWidth: 0, mr: sidebarOpen ? 3 : "auto", justifyContent: "center", color: isActive ? "primary.main" : "inherit" }, children: item.icon }), sidebarOpen && _jsx(ListItemText, { primary: item.text, sx: { color: isActive ? "primary.main" : "inherit" } })] }, item.text));
                    }) }) }), _jsx(Box, { component: "main", sx: { flexGrow: 1, p: 3, mt: 8, backgroundColor: "#f5f5f5" }, children: _jsx(Outlet, {}) })] }));
};
