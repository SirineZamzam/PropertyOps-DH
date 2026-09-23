import {
  Navigate,
  Route,
  Routes,
} from "react-router";

import {
  AppShell,
} from "./components/AppShell";

import {
  ProtectedRoute,
} from "./components/ProtectedRoute";

import {
  RoleRoute,
} from "./components/RoleRoute";

import {
  useAuth,
} from "./contexts/AuthContext";

import {
  TenantHomeProvider,
} from "./contexts/TenantHomeContext";

import AuthPage from "./pages/AuthPage";
import LandingPage from "./pages/LandingPage";
import NotFoundPage from "./pages/NotFoundPage";
import SignupPlanPage from "./pages/SignupPlanPage";

import AdminOverviewPage from "./pages/AdminOverviewPage";
import AdminOwnersPage from "./pages/AdminOwnersPage";
import AdminPlansPage from "./pages/AdminPlansPage";
import AdminSubscriptionsPage from "./pages/AdminSubscriptionsPage";
import AdminSubscriptionPaymentsPage from "./pages/AdminSubscriptionPaymentsPage";

import OwnerOverviewPage from "./pages/OwnerOverviewPage";
import OwnerSubscriptionPage from "./pages/OwnerSubscriptionPage";
import PropertiesPage from "./pages/PropertiesPage";
import PropertyDetailsPage from "./pages/PropertyDetailsPage";
import PeopleLeasesPage from "./pages/PeopleLeasesPage";
import MaintenancePage from "./pages/MaintenancePage";
import ExpensesPage from "./pages/ExpensesPage";
import RentPage from "./pages/RentPage";
import TenantHomePage from "./pages/TenantHomePage";
import SettingsPage from "./pages/SettingsPage";


function WorkspaceRedirect() {
  const {
    user,
  } = useAuth();

  if (!user) {
    return (
      <Navigate
        to="/auth?mode=login"
        replace
      />
    );
  }

  if (
    user.role === "ADMIN"
  ) {
    return (
      <Navigate
        to="/app/admin/overview"
        replace
      />
    );
  }

  if (
    user.role === "OWNER"
  ) {
    return (
      <Navigate
        to="/app/overview"
        replace
      />
    );
  }

  return (
    <Navigate
      to="/app/home"
      replace
    />
  );
}


export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <LandingPage />
        }
      />

      <Route
        path="/auth"
        element={
          <AuthPage />
        }
      />

      <Route
        path="/choose-plan"
        element={
          <ProtectedRoute role="OWNER">
            <SignupPlanPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <TenantHomeProvider>
              <AppShell />
            </TenantHomeProvider>
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={
            <WorkspaceRedirect />
          }
        />

        <Route
          path="admin/overview"
          element={
            <RoleRoute role="ADMIN">
              <AdminOverviewPage />
            </RoleRoute>
          }
        />

        <Route
          path="admin/owners"
          element={
            <RoleRoute role="ADMIN">
              <AdminOwnersPage />
            </RoleRoute>
          }
        />

        <Route
          path="admin/subscriptions"
          element={
            <RoleRoute role="ADMIN">
              <AdminSubscriptionsPage />
            </RoleRoute>
          }
        />

        <Route
          path="admin/plans"
          element={
            <RoleRoute role="ADMIN">
              <AdminPlansPage />
            </RoleRoute>
          }
        />

        <Route
          path="admin/subscription-payments"
          element={
            <RoleRoute role="ADMIN">
              <AdminSubscriptionPaymentsPage />
            </RoleRoute>
          }
        />

        <Route
          path="overview"
          element={
            <RoleRoute role="OWNER">
              <OwnerOverviewPage />
            </RoleRoute>
          }
        />

        <Route
          path="properties"
          element={
            <RoleRoute role="OWNER">
              <PropertiesPage />
            </RoleRoute>
          }
        />

        <Route
          path="properties/:propertyId"
          element={
            <RoleRoute role="OWNER">
              <PropertyDetailsPage />
            </RoleRoute>
          }
        />

        <Route
          path="people"
          element={
            <RoleRoute role="OWNER">
              <PeopleLeasesPage />
            </RoleRoute>
          }
        />

        <Route
          path="maintenance"
          element={
            <MaintenancePage />
          }
        />

        <Route
          path="expenses"
          element={
            <RoleRoute role="OWNER">
              <ExpensesPage />
            </RoleRoute>
          }
        />

        <Route
          path="rent"
          element={
            <RentPage />
          }
        />

        <Route
          path="subscription"
          element={
            <RoleRoute role="OWNER">
              <OwnerSubscriptionPage />
            </RoleRoute>
          }
        />

        <Route
          path="home"
          element={
            <RoleRoute role="TENANT">
              <TenantHomePage />
            </RoleRoute>
          }
        />

        <Route
          path="settings"
          element={
            <SettingsPage />
          }
        />
      </Route>

      <Route
        path="*"
        element={
          <NotFoundPage />
        }
      />
    </Routes>
  );
}
