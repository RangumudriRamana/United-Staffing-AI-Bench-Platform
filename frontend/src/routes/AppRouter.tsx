import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AuthLayout from "../layouts/AuthLayout";
import DashboardLayout from "../layouts/DashboardLayout";
import ProtectedRoute from "./ProtectedRoute";
import PublicRoute from "./PublicRoute";

import { lazy, Suspense } from "react";

const LoginPage = lazy(() => import("../pages/auth/LoginPage"));
const DashboardPage = lazy(() => import("../pages/dashboard/DashboardPage"));
const ConsultantsPage = lazy(() => import("../pages/consultants/ConsultantsPage"));
const RequirementsPage = lazy(() => import("../pages/requirements/RequirementsPage"));
const VendorsPage = lazy(() => import("../pages/vendors/VendorsPage"));

const SubmissionsPage = lazy(() => import("@/pages/submissions/SubmissionsPage"));
const SubmissionDetailPage = lazy(() => import("@/pages/submissions/SubmissionDetailPage"));
const NewSubmissionPage = lazy(() => import("@/pages/submissions/NewSubmissionPage"));

const AIMatchingPage = lazy(() => import("@/pages/ai/AIMatchingPage"));

const AnalyticsPage = lazy(() => import("@/pages/analytics/AnalyticsPage"));
const RecruiterAnalyticsPage = lazy(() => import("@/pages/analytics/RecruiterAnalyticsPage"));
const VendorAnalyticsPage = lazy(() => import("@/pages/analytics/VendorAnalyticsPage"));

const MarketingWorkspacePage = lazy(() => import("@/pages/marketing/MarketingWorkspacePage"));
const TasksPage = lazy(() => import("@/pages/tasks/TasksPage"));
const PlannerPage = lazy(() => import("../pages/planner/PlannerPage"));

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route element={<AuthLayout />}>
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
        </Route>

        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/"
          element={<DashboardPage />}
          />
          <Route
            path="/consultants"
            element={<ConsultantsPage />}
          />
          <Route
            path="/requirements"
            element={<RequirementsPage />}
          />
          <Route
            path="/vendors"
            element={<VendorsPage />}
          />
          <Route
            path="/submissions"
            element={<SubmissionsPage />}
          />
          <Route
            path="/submissions/new"
            element={<NewSubmissionPage />}
          />
          <Route
            path="/submissions/:publicId"
            element={<SubmissionDetailPage />}
          />
          <Route
            path="/ai-matching"
            element={<AIMatchingPage />}
          />
          <Route path="/analytics"
          element={<AnalyticsPage />}
          />
          <Route
            path="/analytics/recruiter"
            element={<RecruiterAnalyticsPage />}
          />
          <Route
            path="/analytics/vendor"
            element={<VendorAnalyticsPage />}
          />
          <Route
            path="/marketing"
            element={<MarketingWorkspacePage />}
          />
          <Route
            path="/planner"
            element={<PlannerPage />}
          />
          <Route
            path="/tasks"
            element={<TasksPage />}
          />


        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
