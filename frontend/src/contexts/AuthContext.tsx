import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { apiRequest } from "../lib/api";

import type {
  LoginResponse,
  User,
} from "../types/auth";

export interface RegisterDetails {
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string;
  password: string;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;

  login: (
    email: string,
    password: string,
  ) => Promise<User>;

  register: (
    details: RegisterDetails,
  ) => Promise<User>;

  refreshUser:
    () => Promise<void>;

  logout: () => void;
}

const AuthContext =
  createContext<
    AuthContextValue | null
  >(null);

const TOKEN_KEY =
  "propertyops_access_token";

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [
    user,
    setUser,
  ] =
    useState<User | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  async function getProfile() {
    return apiRequest<User>(
      "/auth/me/profile",
    );
  }

  useEffect(() => {
    async function restore() {
      const token =
        localStorage.getItem(
          TOKEN_KEY,
        );

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        setUser(
          await getProfile(),
        );
      } catch {
        localStorage.removeItem(
          TOKEN_KEY,
        );

        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    restore();
  }, []);

  async function login(
    email: string,
    password: string,
  ): Promise<User> {
    const response =
      await apiRequest<
        LoginResponse
      >(
        "/auth/login",
        {
          method: "POST",

          body:
            JSON.stringify({
              email,
              password,
            }),
        },
      );

    localStorage.setItem(
      TOKEN_KEY,
      response.access_token,
    );

    try {
      const profile =
        await getProfile();

      setUser(profile);

      return profile;
    } catch (error) {
      localStorage.removeItem(
        TOKEN_KEY,
      );

      throw error;
    }
  }

  async function register(
    details: RegisterDetails,
  ): Promise<User> {
    await apiRequest(
      "/auth/register",
      {
        method: "POST",

        body:
          JSON.stringify({
            email:
              details.email,

            password:
              details.password,
          }),
      },
    );

    await login(
      details.email,
      details.password,
    );

    const profile =
      await apiRequest<User>(
        "/auth/me/profile",
        {
          method: "PATCH",

          body:
            JSON.stringify({
              first_name:
                details.first_name,

              last_name:
                details.last_name,

              phone_number:
                details.phone_number,
            }),
        },
      );

    setUser(profile);

    return profile;
  }

  async function refreshUser() {
    setUser(
      await getProfile(),
    );
  }

  function logout() {
    localStorage.removeItem(
      TOKEN_KEY,
    );

    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context =
    useContext(
      AuthContext,
    );

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider.",
    );
  }

  return context;
}