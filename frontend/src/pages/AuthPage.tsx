import {
  ArrowLeft,
  Eye,
  EyeOff,
  KeyRound,
  Mail,
} from "lucide-react";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  useNavigate,
  useSearchParams,
} from "react-router";

import { Brand } from "../components/Brand";
import { useAuth } from "../contexts/AuthContext";

type Mode = "login" | "register";

export default function AuthPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const navigate = useNavigate();

  const { login, register, user } = useAuth();

  const initialMode: Mode =
    searchParams.get("mode") === "register" ? "register" : "login";

  const [mode, setMode] = useState<Mode>(initialMode);

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [firstName, setFirstName] = useState("");

  const [lastName, setLastName] = useState("");

  const [phone, setPhone] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [error, setError] = useState("");

  const [submitting, setSubmitting] = useState(false);

  const isRegister = mode === "register";

  useEffect(() => {
    if (user) {
      navigate("/app", {
        replace: true,
      });
    }
  }, [user, navigate]);

  function changeMode(nextMode: Mode) {
    setMode(nextMode);
    setError("");

    setSearchParams({
      mode: nextMode,
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register({
          first_name: firstName,
          last_name: lastName,
          phone_number: phone,
          email,
          password,
        });
      }

      navigate("/app");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to continue.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="h-svh overflow-hidden bg-[#edf4f5] p-3 sm:p-4">
      <section className="relative mx-auto h-full max-w-6xl overflow-hidden rounded-[2rem] bg-white shadow-[0_30px_100px_rgba(26,54,31,0.12)]">
        {/* DESKTOP */}
        <div className="relative hidden h-full grid-cols-2 md:grid">
          {/* LOGIN */}
          <div
            className={[
              "auth-form relative flex h-full items-center px-10 lg:px-16",
              isRegister
                ? "pointer-events-none translate-x-8 opacity-0"
                : "translate-x-0 opacity-100",
            ].join(" ")}
          >
            <button
              type="button"
              onClick={() => navigate("/")}
              className="absolute left-8 top-7 z-10 flex items-center gap-2 text-sm font-semibold text-phthalo/55 transition hover:text-celestial lg:left-12"
            >
              <ArrowLeft size={16} />
              Home
            </button>

            <div className="no-scrollbar max-h-[calc(100vh-5rem)] w-full overflow-y-auto py-6">
              <AuthForm
                mode="login"
                email={email}
                password={password}
                firstName={firstName}
                lastName={lastName}
                phone={phone}
                showPassword={showPassword}
                error={error}
                submitting={submitting}
                setEmail={setEmail}
                setPassword={setPassword}
                setFirstName={setFirstName}
                setLastName={setLastName}
                setPhone={setPhone}
                setShowPassword={setShowPassword}
                onSubmit={handleSubmit}
                onSwitch={() => changeMode("register")}
              />
            </div>
          </div>

          {/* REGISTER */}
          <div
            className={[
              "auth-form relative flex h-full items-center px-10 lg:px-16",
              isRegister
                ? "translate-x-0 opacity-100"
                : "pointer-events-none -translate-x-8 opacity-0",
            ].join(" ")}
          >
            <button
              type="button"
              onClick={() => navigate("/")}
              className="absolute left-8 top-7 z-10 flex items-center gap-2 text-sm font-semibold text-phthalo/55 transition hover:text-celestial lg:left-12"
            >
              <ArrowLeft size={16} />
              Home
            </button>

            <div className="no-scrollbar max-h-[calc(100vh-5rem)] w-full overflow-y-auto py-6">
              <AuthForm
                mode="register"
                email={email}
                password={password}
                firstName={firstName}
                lastName={lastName}
                phone={phone}
                showPassword={showPassword}
                error={error}
                submitting={submitting}
                setEmail={setEmail}
                setPassword={setPassword}
                setFirstName={setFirstName}
                setLastName={setLastName}
                setPhone={setPhone}
                setShowPassword={setShowPassword}
                onSubmit={handleSubmit}
                onSwitch={() => changeMode("login")}
              />
            </div>
          </div>

          {/* IMAGE PANEL */}
          <div
            className={[
              "auth-slider absolute inset-y-0 z-20 w-1/2 overflow-hidden p-2",
              isRegister ? "translate-x-0" : "translate-x-full",
            ].join(" ")}
          >
            <div className="relative h-full overflow-hidden rounded-[1.6rem] bg-phthalo">
              <img
                src="/images/auth-building.jpg"
                alt="Residential building"
                className="absolute inset-0 h-full w-full object-cover"
              />

              {/* neutral bottom fade for readability */}
              <div className="absolute inset-x-0 bottom-0 h-[44%] bg-gradient-to-t from-black/65 to-transparent" />

              <div
                className={[
                  "absolute top-7",
                  isRegister ? "right-7" : "left-7",
                ].join(" ")}
              >
                <Brand light />
              </div>

              <div className="absolute bottom-8 left-8 right-8 text-white">
                <h2 className="max-w-sm text-3xl font-semibold tracking-[-0.045em]">
                  {isRegister
                    ? "A better view of your properties."
                    : "Welcome back."}
                </h2>

                <p className="mt-2 max-w-sm text-sm text-white/70">
                  {isRegister
                    ? "Create your owner workspace."
                    : "Your workspace is ready."}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* MOBILE */}
        <div className="flex h-full flex-col md:hidden">
          <div className="relative h-[32%] shrink-0 overflow-hidden">
            <img
              src="/images/auth-building.jpg"
              alt="Residential building"
              className="h-full w-full object-cover"
            />

            <div className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-black/55 to-transparent" />

            <button
              type="button"
              onClick={() => navigate("/")}
              className="absolute left-4 top-4 grid size-10 place-items-center rounded-full bg-black/30 text-white backdrop-blur"
            >
              <ArrowLeft size={17} />
            </button>

            <div className="absolute bottom-4 left-5">
              <Brand light />
            </div>
          </div>

          <div className="no-scrollbar flex-1 overflow-y-auto px-6 py-6">
            <AuthForm
              mode={mode}
              email={email}
              password={password}
              firstName={firstName}
              lastName={lastName}
              phone={phone}
              showPassword={showPassword}
              error={error}
              submitting={submitting}
              setEmail={setEmail}
              setPassword={setPassword}
              setFirstName={setFirstName}
              setLastName={setLastName}
              setPhone={setPhone}
              setShowPassword={setShowPassword}
              onSubmit={handleSubmit}
              onSwitch={() =>
                changeMode(isRegister ? "login" : "register")
              }
            />
          </div>
        </div>
      </section>
    </div>
  );
}

interface AuthFormProps {
  mode: Mode;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone: string;
  showPassword: boolean;
  error: string;
  submitting: boolean;

  setEmail: (value: string) => void;
  setPassword: (value: string) => void;
  setFirstName: (value: string) => void;
  setLastName: (value: string) => void;
  setPhone: (value: string) => void;
  setShowPassword: (value: boolean) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onSwitch: () => void;
}

function AuthForm({
  mode,
  email,
  password,
  firstName,
  lastName,
  phone,
  showPassword,
  error,
  submitting,
  setEmail,
  setPassword,
  setFirstName,
  setLastName,
  setPhone,
  setShowPassword,
  onSubmit,
  onSwitch,
}: AuthFormProps) {
  const isRegister = mode === "register";

  return (
    <div className="mx-auto w-full max-w-sm">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial">
        {isRegister ? "Owner account" : "PropertyOps"}
      </p>

      <h1 className="mt-3 text-4xl font-semibold tracking-[-0.055em] text-phthalo">
        {isRegister ? "Create account" : "Sign in"}
      </h1>

      <p className="mt-2 text-sm text-phthalo/50">
        {isRegister
          ? "Start managing your properties."
          : "Continue to your workspace."}
      </p>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        {isRegister && (
          <>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className="mb-2 block text-xs font-semibold text-phthalo/60">
                  First name
                </span>

                <input
                  required
                  value={firstName}
                  onChange={(event) =>
                    setFirstName(
                      event.target.value,
                    )
                  }
                  placeholder="First name"
                  className="w-full rounded-2xl border border-phthalo/10 bg-[#f6f8f6] px-4 py-3.5 text-sm font-medium text-deep-blue outline-none transition placeholder:text-deep-blue/30 focus:border-celestial/60 focus:ring-4 focus:ring-cyan/15"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-xs font-semibold text-phthalo/60">
                  Last name
                </span>

                <input
                  required
                  value={lastName}
                  onChange={(event) =>
                    setLastName(
                      event.target.value,
                    )
                  }
                  placeholder="Last name"
                  className="w-full rounded-2xl border border-phthalo/10 bg-[#f6f8f6] px-4 py-3.5 text-sm font-medium text-deep-blue outline-none transition placeholder:text-deep-blue/30 focus:border-celestial/60 focus:ring-4 focus:ring-cyan/15"
                />
              </label>
            </div>

            <label className="block">
              <span className="mb-2 block text-xs font-semibold text-phthalo/60">
                Phone number
              </span>

              <input
                required
                value={phone}
                onChange={(event) =>
                  setPhone(
                    event.target.value,
                  )
                }
                placeholder="+961..."
                className="w-full rounded-2xl border border-phthalo/10 bg-[#f6f8f6] px-4 py-3.5 text-sm font-medium text-deep-blue outline-none transition placeholder:text-deep-blue/30 focus:border-celestial/60 focus:ring-4 focus:ring-cyan/15"
              />
            </label>
          </>
        )}

        <label className="block">
          <span className="mb-2 block text-xs font-semibold text-phthalo/60">
            Email
          </span>

          <div className="flex items-center gap-3 rounded-2xl border border-phthalo/10 bg-[#f6f8f6] px-4 transition focus-within:border-celestial/60 focus-within:ring-4 focus-within:ring-cyan/15">
            <Mail size={17} className="text-celestial" />

            <input
              type="email"
              required
              value={email}
              autoComplete="email"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              className="min-w-0 flex-1 bg-transparent py-3.5 text-sm font-medium text-deep-blue outline-none placeholder:text-deep-blue/30"
            />
          </div>
        </label>

        <label className="block">
          <span className="mb-2 block text-xs font-semibold text-phthalo/60">
            Password
          </span>

          <div className="flex items-center gap-3 rounded-2xl border border-phthalo/10 bg-[#f6f8f6] px-4 transition focus-within:border-celestial/60 focus-within:ring-4 focus-within:ring-cyan/15">
            <KeyRound size={17} className="text-celestial" />

            <input
              type={showPassword ? "text" : "password"}
              required
              minLength={8}
              value={password}
              autoComplete={
                isRegister ? "new-password" : "current-password"
              }
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Minimum 8 characters"
              className="min-w-0 flex-1 bg-transparent py-3.5 text-sm font-medium text-deep-blue outline-none placeholder:text-deep-blue/30"
            />

            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-phthalo/35 transition hover:text-celestial"
            >
              {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
        </label>

        {error && (
          <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-2xl bg-phthalo px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-moss disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting
            ? "Please wait..."
            : isRegister
              ? "Create account"
              : "Sign in"}
        </button>
      </form>

      <button
        type="button"
        onClick={onSwitch}
        className="mt-5 w-full rounded-2xl border border-phthalo/10 px-5 py-3 text-sm font-semibold text-phthalo transition hover:border-celestial/30 hover:bg-skywash"
      >
        {isRegister
          ? "Already have an account? Sign in"
          : "New owner? Create an account"}
      </button>

      {isRegister && (
        <p className="mt-4 text-center text-[11px] text-phthalo/38">
          Tenant accounts are created by property owners.
        </p>
      )}
    </div>
  );
}