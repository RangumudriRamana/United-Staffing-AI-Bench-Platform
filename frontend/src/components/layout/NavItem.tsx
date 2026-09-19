import { NavLink } from "react-router-dom";
import type { LucideIcon } from "lucide-react";

interface Props {
  to: string;
  title: string;
  icon: LucideIcon;
}

export default function NavItem({
  to,
  title,
  icon: Icon,
}: Props) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-4 py-3 transition ${
          isActive
            ? "bg-blue-600 text-white"
            : "text-gray-700 hover:bg-gray-100"
        }`
      }
    >
      <Icon size={18} />

      <span>{title}</span>
    </NavLink>
  );
}