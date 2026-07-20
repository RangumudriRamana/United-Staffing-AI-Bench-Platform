import React from "react";
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

export const ProtectedLayout: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { user, clearSession } = useAuthStore();
  const navigate = useNavigate(); 
  const location = useLocation();

  const navigationConfig = [
    { text: "Dashboard", path: "/dashboard", icon: <DashboardIcon />, roles: ["ADMIN", "MANAGER", "RECRUITER"] },
    { text: "Consultants", path: "/consultants", icon: <PeopleIcon />, roles: ["ADMIN", "MANAGER", "RECRUITER"] },
    { text: "Requirements", path: "/requirements", icon: <AssignmentIcon />, roles: ["ADMIN", "MANAGER", "RECRUITER"] },
    { text: "Submissions", path: "/submissions", icon: <SendIcon />, roles: ["ADMIN", "MANAGER", "RECRUITER"] },
    { text: "Settings", path: "/settings", icon: <SettingsIcon />, roles: ["ADMIN", "MANAGER", "RECRUITER"] },
    { text: "Administration", path: "/admin", icon: <AdminPanelSettingsIcon />, roles: ["ADMIN"] },
  ];

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: "#1976d2" }}>
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <IconButton color="inherit" onClick={toggleSidebar} edge="start">
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: "bold" }}>
              United Staffing AI Platform
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              {user?.firstName || "System Operator"} ({user?.role || "ADMIN"})
            </Typography>
            <Avatar sx={{ bgcolor: "#2196f3", width: 32, height: 32 }}>U</Avatar>
            <IconButton color="inherit" onClick={() => { clearSession(); navigate("/login"); }}>
              <ExitToAppIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
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
        }}
      >
        <List>
          {navigationConfig
            .filter((item) => !user || item.roles.includes(user.role))
            .map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <ListItemButton
                  key={item.text}
                  onClick={() => navigate(item.path)}
                  selected={isActive}
                  sx={{ minHeight: 48, px: 2.5 }}
                >
                  <ListItemIcon sx={{ minWidth: 0, mr: sidebarOpen ? 3 : "auto", justifyContent: "center", color: isActive ? "primary.main" : "inherit" }}>
                    {item.icon}
                  </ListItemIcon>
                  {sidebarOpen && <ListItemText primary={item.text} sx={{ color: isActive ? "primary.main" : "inherit" }} />}
                </ListItemButton>
              );
            })}
        </List>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8, backgroundColor: "#f5f5f5" }}>
        <Outlet />
      </Box>
    </Box>
  );
};