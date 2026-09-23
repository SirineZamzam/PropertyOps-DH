import {
  Building2,
  CreditCard,
  Home,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  ReceiptText,
  Settings,
  ShieldCheck,
  Sun,
  Users,
  Wrench,
  X,
  BadgeDollarSign,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router";

import {
  Brand,
} from "./Brand";

import {
  useAuth,
} from "../contexts/AuthContext";


type Theme =
  | "light"
  | "dark";


export function AppShell() {
  const {
    user,
    logout,
  } = useAuth();

  const navigate =
    useNavigate();

  const [
    collapsed,
    setCollapsed,
  ] = useState(false);

  const [
    mobileOpen,
    setMobileOpen,
  ] = useState(false);

  const [
    theme,
    setTheme,
  ] = useState<Theme>(
    () => {
      return (
        localStorage.getItem(
          "propertyops_dashboard_theme",
        ) === "dark"
          ? "dark"
          : "light"
      );
    },
  );


  useEffect(() => {
    localStorage.setItem(
      "propertyops_dashboard_theme",
      theme,
    );
  }, [
    theme,
  ]);


  const adminNavigation = [
    {
      label:
        "Overview",
      to:
        "/app/admin/overview",
      icon:
        LayoutDashboard,
    },
    {
      label:
        "Owners",
      to:
        "/app/admin/owners",
      icon:
        ShieldCheck,
    },
    {
      label:
        "Plans",
      to:
        "/app/admin/plans",
      icon:
        BadgeDollarSign,
    },
    {
      label:
        "Settings",
      to:
        "/app/settings",
      icon:
        Settings,
    },
  ];


  const ownerNavigation = [
    {
      label:
        "Overview",
      to:
        "/app/overview",
      icon:
        LayoutDashboard,
    },
    {
      label:
        "Properties",
      to:
        "/app/properties",
      icon:
        Building2,
    },
    {
      label:
        "People & leases",
      to:
        "/app/people",
      icon:
        Users,
    },
    {
      label:
        "Maintenance",
      to:
        "/app/maintenance",
      icon:
        Wrench,
    },
    {
      label:
        "Expenses",
      to:
        "/app/expenses",
      icon:
        ReceiptText,
    },
    {
      label:
        "Rent",
      to:
        "/app/rent",
      icon:
        CreditCard,
    },
    {
      label:
        "Settings",
      to:
        "/app/settings",
      icon:
        Settings,
    },
  ];


  const tenantNavigation = [
    {
      label:
        "My home",
      to:
        "/app/home",
      icon:
        Home,
    },
    {
      label:
        "Maintenance",
      to:
        "/app/maintenance",
      icon:
        Wrench,
    },
    {
      label:
        "Rent",
      to:
        "/app/rent",
      icon:
        CreditCard,
    },
    {
      label:
        "Settings",
      to:
        "/app/settings",
      icon:
        Settings,
    },
  ];


  const navigation =
    user?.role === "ADMIN"
      ? adminNavigation
      : user?.role === "OWNER"
        ? ownerNavigation
        : tenantNavigation;


  function handleLogout() {
    logout();
    navigate("/");
  }


  const accountLabel =
    user?.first_name
      ? (
        `${user.first_name} ${user.last_name ?? ""}`
      ).trim()
      : user?.email;


  const workspaceLabel =
    user?.role === "ADMIN"
      ? "Admin workspace"
      : user?.role === "OWNER"
        ? "Owner workspace"
        : "Tenant workspace";


  return (
    <div
      data-theme={theme}
      className="min-h-screen bg-light-canvas text-deep-blue transition-colors duration-300 dark:bg-dark-canvas dark:text-white"
    >
      <aside
        className={[
          "fixed inset-y-0 left-0 z-40 hidden flex-col transition-[width,background-color] duration-300 lg:flex",
          "sidebar-bg text-light-slate dark:text-white",
          collapsed
            ? "w-20"
            : "w-72",
        ].join(" ")}
      >
        <div
          className={[
            "flex h-20 items-center border-b px-4",
            "border-white/15",
            collapsed
              ? "justify-center"
              : "justify-between",
          ].join(" ")}
        >
          <Brand
            light
            compact={collapsed}
          />

          {!collapsed && (
            <button
              type="button"
              onClick={() =>
                setCollapsed(true)
              }
              className="grid size-9 place-items-center rounded-xl text-white/70 transition hover:bg-white/12 hover:text-white"
              title="Collapse sidebar"
            >
              <PanelLeftClose
                size={18}
              />
            </button>
          )}
        </div>

        {collapsed && (
          <button
            type="button"
            onClick={() =>
              setCollapsed(false)
            }
            title="Expand sidebar"
            className="mx-auto mt-4 grid size-10 place-items-center rounded-xl text-white/75 transition hover:bg-white/12 hover:text-white"
          >
            <PanelLeftOpen
              size={18}
            />
          </button>
        )}

        <nav className="mt-5 space-y-1 px-3">
          {navigation.map(
            ({
              label,
              to,
              icon: Icon,
            }) => (
              <NavLink
                key={to}
                to={to}
                title={
                  collapsed
                    ? label
                    : undefined
                }
                className={({
                  isActive,
                }) =>
                  [
                    "flex items-center rounded-2xl py-3 text-sm font-semibold transition",
                    collapsed
                      ? "justify-center px-2"
                      : "gap-3 px-4",

                    isActive
                      ? [
                          "bg-cyan text-deep-blue shadow-sm",
                          "dark:bg-moss dark:text-lime-soft",
                        ].join(" ")
                      : [
                          "text-light-slate hover:bg-white/12 hover:text-white",
                          "dark:text-white/64 dark:hover:bg-moss/60 dark:hover:text-lime-soft",
                        ].join(" "),
                  ].join(" ")
                }
              >
                <Icon
                  size={19}
                  className="shrink-0"
                />

                {!collapsed && (
                  <span>
                    {label}
                  </span>
                )}
              </NavLink>
            ),
          )}
        </nav>

        <div className="mt-auto p-3">
          <button
            type="button"
            onClick={
              handleLogout
            }
            className={[
              "flex w-full items-center rounded-2xl py-3 text-sm font-medium transition",
              "text-light-slate hover:bg-white/12 hover:text-white",
              "dark:text-white/60 dark:hover:bg-moss/60 dark:hover:text-lime-soft",
              collapsed
                ? "justify-center"
                : "gap-3 px-4",
            ].join(" ")}
          >
            <LogOut
              size={18}
            />

            {!collapsed && (
              <span>
                Sign out
              </span>
            )}
          </button>
        </div>
      </aside>


      <header
        className={[
          "fixed right-0 top-0 z-30 flex h-20 items-center justify-between border-b px-5 backdrop-blur-xl transition-[left,background-color] duration-300 md:px-8",
          "border-celestial/12 bg-light-canvas/92",
          "dark:border-ash/12 dark:bg-dark-canvas/92",
          collapsed
            ? "left-0 lg:left-20"
            : "left-0 lg:left-72",
        ].join(" ")}
      >
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() =>
              setMobileOpen(true)
            }
            className="grid size-10 place-items-center rounded-xl bg-cyan text-deep-blue lg:hidden dark:bg-moss dark:text-lime-soft"
          >
            <Menu
              size={19}
            />
          </button>

          <div className="lg:hidden">
            <Brand />
          </div>

          <div className="hidden lg:block">
            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
              {workspaceLabel}
            </p>

            <p className="mt-1 max-w-sm truncate text-sm font-semibold text-deep-blue dark:text-white">
              {accountLabel}
            </p>
          </div>
        </div>


        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() =>
              setTheme(
                theme ===
                "light"
                  ? "dark"
                  : "light",
              )
            }
            title="Toggle theme"
            className="grid size-10 place-items-center rounded-xl bg-cyan text-deep-blue transition hover:bg-celestial hover:text-white dark:bg-moss dark:text-lime-soft dark:hover:bg-ash dark:hover:text-slate-green"
          >
            {theme ===
            "light" ? (
              <Moon
                size={18}
              />
            ) : (
              <Sun
                size={18}
              />
            )}
          </button>

          <div className="hidden text-right sm:block">
            <p className="max-w-[220px] truncate text-sm font-semibold text-deep-blue dark:text-white">
              {accountLabel}
            </p>

            <p className="mt-0.5 text-[10px] font-bold uppercase tracking-[0.14em] text-celestial dark:text-ash">
              {user?.role}
            </p>
          </div>
        </div>
      </header>


      {mobileOpen && (
        <>
          <button
            type="button"
            onClick={() =>
              setMobileOpen(false)
            }
            aria-label="Close menu"
            className="fixed inset-0 z-40 bg-black/35 backdrop-blur-sm lg:hidden"
          />

          <aside className="fixed inset-y-0 left-0 z-50 flex w-[84%] max-w-sm flex-col sidebar-bg p-4 text-white shadow-2xl lg:hidden">
            <div className="flex items-center justify-between">
              <Brand light />

              <button
                type="button"
                onClick={() =>
                  setMobileOpen(false)
                }
                className="grid size-10 place-items-center rounded-xl bg-white/12"
              >
                <X
                  size={18}
                />
              </button>
            </div>

            <nav className="mt-8 space-y-1">
              {navigation.map(
                ({
                  label,
                  to,
                  icon: Icon,
                }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() =>
                      setMobileOpen(
                        false,
                      )
                    }
                    className={({
                      isActive,
                    }) =>
                      [
                        "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold",
                        isActive
                          ? "bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft"
                          : "text-white/75",
                      ].join(" ")
                    }
                  >
                    <Icon
                      size={19}
                    />

                    {label}
                  </NavLink>
                ),
              )}
            </nav>

            <button
              type="button"
              onClick={
                handleLogout
              }
              className="mt-auto flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-white/70"
            >
              <LogOut
                size={18}
              />

              Sign out
            </button>
          </aside>
        </>
      )}


      <main
        className={[
          "min-h-screen pt-20 transition-[padding] duration-300",
          collapsed
            ? "lg:pl-20"
            : "lg:pl-72",
        ].join(" ")}
      >
        <div className="p-5 md:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
