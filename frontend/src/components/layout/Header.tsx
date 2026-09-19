import { Bell } from "lucide-react";
import { useLocation } from "react-router-dom";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useNotifications } from "@/hooks/useNotifications";
import notificationService from "@/services/notification.service";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/planner": "Daily Planner",
  "/consultants": "Consultants",
  "/requirements": "Requirements",
  "/vendors": "Vendors",
  "/submissions": "Submissions",
  "/ai-matching": "AI Matching",
  "/marketing": "Marketing",
  "/tasks": "Tasks",
  "/analytics": "Analytics",
  "/settings": "Settings",
};

function getPageTitle(pathname: string) {
  if (pageTitles[pathname]) {
    return pageTitles[pathname];
  }

  if (pathname.startsWith("/submissions/")) {
    return "Submission Details";
  }

  return "Dashboard";
}

export default function Header() {
  const location = useLocation();
  const [showNotifications, setShowNotifications] = useState(false);

  const pageTitle = getPageTitle(location.pathname);

  const {
    data: notifications = [],
    isLoading,
    isError,
    refetch,
  } = useNotifications();

  const handleMarkAsRead = async (publicId: string) => {
    try {
      await notificationService.markAsRead(publicId);
      await refetch();
    } catch {
      // Notification read errors are handled by the existing UI state.
    }
  };

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <div>
        <h1 className="text-xl font-semibold">
          {pageTitle}
        </h1>
      </div>

      <div className="flex items-center gap-4">
        {/* NOTIFICATIONS */}
        <div className="relative">
          <Button
            variant="outline"
            size="icon"
            type="button"
            onClick={() =>
              setShowNotifications((current) => !current)
            }
            aria-label="Notifications"
          >
            <Bell size={18} />

            {notifications.length > 0 && (
              <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white">
                {notifications.length > 9
                  ? "9+"
                  : notifications.length}
              </span>
            )}
          </Button>

          {showNotifications && (
            <div className="absolute right-0 top-12 z-50 w-80 rounded-lg border bg-white shadow-lg">
              <div className="border-b px-4 py-3">
                <h2 className="font-semibold">
                  Notifications
                </h2>

                <p className="text-xs text-muted-foreground">
                  Unread notifications
                </p>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {isLoading && (
                  <div className="p-4 text-sm text-muted-foreground">
                    Loading notifications...
                  </div>
                )}

                {isError && (
                  <div className="p-4 text-sm text-red-600">
                    Failed to load notifications.
                  </div>
                )}

                {!isLoading &&
                  !isError &&
                  notifications.length === 0 && (
                    <div className="p-6 text-center text-sm text-muted-foreground">
                      No unread notifications.
                    </div>
                  )}

                {!isLoading &&
                  !isError &&
                  notifications.map((notification) => (
                    <div
                      key={notification.public_id}
                      className="border-b p-4 last:border-b-0"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <h3 className="text-sm font-medium">
                            {notification.title}
                          </h3>

                          <p className="mt-1 text-sm text-muted-foreground">
                            {notification.body}
                          </p>

                          <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
                            <span>
                              {notification.priority}
                            </span>

                            <span>
                              {new Date(
                                notification.created_at
                              ).toLocaleString()}
                            </span>
                          </div>
                        </div>

                        <button
                          type="button"
                          className="shrink-0 text-xs font-medium text-blue-600 hover:text-blue-700"
                          onClick={() =>
                            handleMarkAsRead(
                              notification.public_id
                            )
                          }
                        >
                          Mark read
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>

        {/* USER */}
        <div className="text-right">
          <p className="font-medium">
            Admin
          </p>

          <p className="text-sm text-gray-500">
            United Staffing
          </p>
        </div>
      </div>
    </header>
  );
}