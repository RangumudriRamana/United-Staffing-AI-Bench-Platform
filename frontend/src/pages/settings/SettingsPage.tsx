import { LogOut, UserCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/auth/useAuth";

export default function SettingsPage() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = "/login";
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">
          Settings
        </h2>
        <p className="text-muted-foreground">
          Manage your account and session.
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <UserCircle className="h-6 w-6" />
            <CardTitle>Account Information</CardTitle>
          </div>
        </CardHeader>

        <CardContent className="space-y-5">
          <div>
            <p className="text-sm text-muted-foreground">
              Full Name
            </p>
            <p className="font-medium">
              {user
                ? `${user.first_name} ${user.last_name}`
                : "User"}
            </p>
          </div>

          <Separator />

          <div>
            <p className="text-sm text-muted-foreground">
              Email
            </p>
            <p className="font-medium">
              {user?.email ?? "Not available"}
            </p>
          </div>

          <Separator />

          <div>
            <p className="text-sm text-muted-foreground">
              Role
            </p>
            <p className="font-medium capitalize">
              {user?.role ?? "User"}
            </p>
          </div>

          <Separator />

          <div>
            <p className="text-sm text-muted-foreground">
              Account Status
            </p>
            <p className="font-medium">
              {user?.is_active ? "Active" : "Inactive"}
            </p>
          </div>

          <Separator />

          <div>
            <p className="text-sm text-muted-foreground">
              User ID
            </p>
            <p className="break-all font-mono text-sm">
              {user?.public_id ?? "Not available"}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Session</CardTitle>
        </CardHeader>

        <CardContent>
          <Button
            variant="destructive"
            type="button"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}