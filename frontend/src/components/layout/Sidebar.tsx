import {
  LayoutDashboard,
  CalendarDays,
  Users,
  Briefcase,
  Building2,
  GitBranch,
  Bot,
  BarChart3,
  Megaphone,
  ListTodo,
  Settings,
} from "lucide-react";

import AppLogo from "./AppLogo";
import NavItem from "./NavItem";

export default function Sidebar() {
  return (
    <aside className="w-72 border-r bg-white">
      <AppLogo />

      <nav className="space-y-2 px-3">
        <NavItem to="/" title="Dashboard" icon={LayoutDashboard} />
        <NavItem to="/planner" title="Daily Planner" icon={CalendarDays} />
        <NavItem to="/consultants" title="Consultants" icon={Users} />
        <NavItem to="/requirements" title="Requirements" icon={Briefcase} />
        <NavItem to="/vendors" title="Vendors" icon={Building2} />
        <NavItem to="/submissions" title="Submissions" icon={GitBranch} />
        <NavItem to="/ai-matching" title="AI Matching" icon={Bot} />
        <NavItem to="/marketing" title="Marketing" icon={Megaphone} />
        <NavItem to="/tasks" title="Tasks" icon={ListTodo} />
        <NavItem to="/analytics" title="Analytics" icon={BarChart3} />
        <NavItem to="/settings" title="Settings" icon={Settings} />
      </nav>
    </aside>
  );
}