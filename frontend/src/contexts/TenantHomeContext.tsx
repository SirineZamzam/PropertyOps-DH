import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { useAuth } from "./AuthContext";
import { apiRequest } from "../lib/api";

import type {
  TenantHome,
} from "../types/domain";


interface TenantHomeContextValue {
  homes: TenantHome[];

  selectedHome:
    | TenantHome
    | null;

  loading: boolean;

  selectHome: (
    leaseId: number,
  ) => void;

  refreshHomes:
    () => Promise<void>;
}


const TenantHomeContext =
  createContext<
    TenantHomeContextValue
    | null
  >(null);


const STORAGE_KEY =
  "propertyops_selected_lease";


export function TenantHomeProvider({
  children,
}: {
  children: ReactNode;
}) {
  const { user } =
    useAuth();

  const [
    homes,
    setHomes,
  ] = useState<TenantHome[]>(
    [],
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    selectedLeaseId,
    setSelectedLeaseId,
  ] =
    useState<number | null>(
      () => {
        const value =
          localStorage.getItem(
            STORAGE_KEY,
          );

        return value
          ? Number(value)
          : null;
      },
    );


  async function refreshHomes() {
    if (
      user?.role !==
      "TENANT"
    ) {
      setHomes([]);
      return;
    }

    setLoading(true);

    try {
      const data =
        await apiRequest<
          TenantHome[]
        >("/tenant/homes");

      setHomes(data);

      const stillExists =
        data.some(
          (home) =>
            home.lease_id ===
            selectedLeaseId,
        );

      if (
        !stillExists &&
        data.length
      ) {
        setSelectedLeaseId(
          data[0].lease_id,
        );

        localStorage.setItem(
          STORAGE_KEY,
          String(
            data[0].lease_id,
          ),
        );
      }

      if (!data.length) {
        setSelectedLeaseId(
          null,
        );

        localStorage.removeItem(
          STORAGE_KEY,
        );
      }
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    refreshHomes();
  }, [user?.id, user?.role]);


  function selectHome(
    leaseId: number,
  ) {
    setSelectedLeaseId(
      leaseId,
    );

    localStorage.setItem(
      STORAGE_KEY,
      String(leaseId),
    );
  }


  const selectedHome =
    useMemo(
      () =>
        homes.find(
          (home) =>
            home.lease_id ===
            selectedLeaseId,
        ) ??
        homes[0] ??
        null,
      [
        homes,
        selectedLeaseId,
      ],
    );


  return (
    <TenantHomeContext.Provider
      value={{
        homes,
        selectedHome,
        loading,
        selectHome,
        refreshHomes,
      }}
    >
      {children}
    </TenantHomeContext.Provider>
  );
}


export function useTenantHome() {
  const context =
    useContext(
      TenantHomeContext,
    );

  if (!context) {
    throw new Error(
      "useTenantHome must be used inside TenantHomeProvider.",
    );
  }

  return context;
}