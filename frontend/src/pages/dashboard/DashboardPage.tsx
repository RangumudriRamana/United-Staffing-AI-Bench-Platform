import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">
          Welcome 👋
        </h2>

        <p className="text-muted-foreground">
          United Staffing AI Bench Platform
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Consultants
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            0
          </h2>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Requirements
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            0
          </h2>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Vendors
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            0
          </h2>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            AI Matches
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            0
          </h2>
        </div>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-xl font-semibold">
          Quick Actions
        </h3>

        <div className="flex flex-wrap gap-3">
          <Button>Add Consultant</Button>

          <Button variant="outline">
            Create Requirement
          </Button>

          <Button variant="secondary">
            AI Match
          </Button>
        </div>
      </div>
    </div>
  );
}