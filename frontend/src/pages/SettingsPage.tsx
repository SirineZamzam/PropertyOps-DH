import {
  Eye,
  EyeOff,
  KeyRound,
  Mail,
  Pencil,
  Phone,
  Save,
  UserRound,
  X,
} from "lucide-react";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  FormField,
  controlClass,
} from "../components/FormField";

import {
  ApiError,
  apiRequest,
  type FieldErrors,
} from "../lib/api";

import {
  errorAlert,
  successAlert,
} from "../lib/alerts";

import {
  useAuth,
} from "../contexts/AuthContext";

import type {
  User,
} from "../types/auth";


export default function SettingsPage() {
  const {
    user,
    refreshUser,
  } = useAuth();

  const [
    editingProfile,
    setEditingProfile,
  ] = useState(false);

  const [
    editingPassword,
    setEditingPassword,
  ] = useState(false);

  const [
    firstName,
    setFirstName,
  ] = useState("");

  const [
    lastName,
    setLastName,
  ] = useState("");

  const [
    phone,
    setPhone,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    profileErrors,
    setProfileErrors,
  ] =
    useState<FieldErrors>(
      {},
    );

  const [
    currentPassword,
    setCurrentPassword,
  ] = useState("");

  const [
    newPassword,
    setNewPassword,
  ] = useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [
    passwordErrors,
    setPasswordErrors,
  ] =
    useState<FieldErrors>(
      {},
    );

  const [
    showCurrentPassword,
    setShowCurrentPassword,
  ] = useState(false);

  const [
    showNewPassword,
    setShowNewPassword,
  ] = useState(false);

  const [
    showConfirmPassword,
    setShowConfirmPassword,
  ] = useState(false);


  function restoreProfileFields() {
    if (!user) {
      return;
    }

    setFirstName(
      user.first_name ?? "",
    );

    setLastName(
      user.last_name ?? "",
    );

    setPhone(
      user.phone_number ?? "",
    );

    setEmail(
      user.email,
    );

    setProfileErrors({});
  }


  useEffect(() => {
    restoreProfileFields();
  }, [user]);


  function cancelProfileEdit() {
    restoreProfileFields();
    setEditingProfile(false);
  }


  function cancelPasswordEdit() {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");

    setPasswordErrors({});

    setShowCurrentPassword(false);
    setShowNewPassword(false);
    setShowConfirmPassword(false);

    setEditingPassword(false);
  }


  function validateProfile() {
    const next:
      FieldErrors = {};

    if (!firstName.trim()) {
      next.first_name =
        "First name is required.";
    }

    if (!lastName.trim()) {
      next.last_name =
        "Last name is required.";
    }

    if (
      phone.trim().length < 7
    ) {
      next.phone_number =
        "Enter a valid phone number.";
    }

    if (
      !email.includes("@")
    ) {
      next.email =
        "Enter a valid email address.";
    }

    setProfileErrors(next);

    return (
      Object.keys(next)
        .length === 0
    );
  }


  async function saveProfile(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !validateProfile()
    ) {
      return;
    }

    try {
      await apiRequest<User>(
        "/auth/me/profile",
        {
          method: "PATCH",

          body:
            JSON.stringify({
              first_name:
                firstName.trim(),

              last_name:
                lastName.trim(),

              phone_number:
                phone.trim(),

              email:
                email.trim(),
            }),
        },
      );

      await refreshUser();

      setEditingProfile(false);

      await successAlert(
        "Profile updated",
        "Your account information has been saved.",
      );
    } catch (error) {
      if (
        error instanceof
        ApiError
      ) {
        setProfileErrors(
          error.fieldErrors,
        );
      }

      await errorAlert(
        "Unable to update profile",
        error instanceof Error
          ? error.message
          : "Update failed.",
      );
    }
  }


  function validatePassword() {
    const next:
      FieldErrors = {};

    if (
      currentPassword.length < 8
    ) {
      next.current_password =
        "Enter your current password.";
    }

    if (
      newPassword.length < 8
    ) {
      next.new_password =
        "New password must be at least 8 characters.";
    }

    if (
      newPassword ===
      currentPassword
    ) {
      next.new_password =
        "New password must be different from your current password.";
    }

    if (
      confirmPassword !==
      newPassword
    ) {
      next.confirm_password =
        "Passwords do not match.";
    }

    setPasswordErrors(next);

    return (
      Object.keys(next)
        .length === 0
    );
  }


  async function savePassword(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !validatePassword()
    ) {
      return;
    }

    try {
      await apiRequest(
        "/auth/me/password",
        {
          method: "PATCH",

          body:
            JSON.stringify({
              current_password:
                currentPassword,

              new_password:
                newPassword,
            }),
        },
      );

      cancelPasswordEdit();

      await successAlert(
        "Password changed",
        "Use your new password the next time you sign in.",
      );
    } catch (error) {
      if (
        error instanceof
          ApiError &&
        error.status === 400
      ) {
        setPasswordErrors({
          current_password:
            error.message,
        });

        return;
      }

      await errorAlert(
        "Unable to change password",
        error instanceof Error
          ? error.message
          : "Password update failed.",
      );
    }
  }


  if (!user) {
    return null;
  }


  const fullName =
    [
      user.first_name,
      user.last_name,
    ]
      .filter(Boolean)
      .join(" ") ||
    "No name added";


  return (
    <div className="mx-auto max-w-5xl page-enter">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
          Account
        </p>

        <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
          Settings
        </h1>

        <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
          Manage your personal
          information and account
          security.
        </p>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">

        {/* PROFILE */}
        <section className="rounded-[2rem] border border-celestial/10 bg-white p-6 shadow-sm dark:border-ash/10 dark:bg-dark-card">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="grid size-12 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                <UserRound
                  size={20}
                />
              </div>

              <div>
                <h2 className="text-xl font-semibold text-deep-blue dark:text-white">
                  Personal details
                </h2>

                <p className="mt-1 text-xs text-deep-blue/40 dark:text-white/35">
                  Your PropertyOps
                  account information.
                </p>
              </div>
            </div>

            {!editingProfile ? (
              <button
                type="button"
                onClick={() =>
                  setEditingProfile(
                    true,
                  )
                }
                className="flex items-center gap-2 rounded-xl bg-cyan/50 px-3 py-2 text-xs font-semibold text-deep-blue transition hover:bg-cyan dark:bg-moss dark:text-lime-soft"
              >
                <Pencil
                  size={14}
                />

                Edit profile
              </button>
            ) : (
              <button
                type="button"
                onClick={
                  cancelProfileEdit
                }
                className="grid size-9 place-items-center rounded-xl bg-ash/40 text-slate-green transition hover:bg-ash"
                title="Cancel editing"
              >
                <X size={15} />
              </button>
            )}
          </div>

          {!editingProfile ? (
            <div className="mt-7 space-y-3">
              <ReadOnlyRow
                icon={UserRound}
                label="Name"
                value={fullName}
              />

              <ReadOnlyRow
                icon={Mail}
                label="Email"
                value={user.email}
              />

              <ReadOnlyRow
                icon={Phone}
                label="Phone number"
                value={
                  user.phone_number ??
                  "No phone number"
                }
              />

              <div className="rounded-2xl bg-ash/30 p-4 text-slate-green dark:bg-moss dark:text-lime-soft">
                <p className="text-[9px] font-bold uppercase tracking-[0.15em] opacity-55">
                  Account type
                </p>

                <p className="mt-1 font-semibold">
                  {user.role}
                </p>
              </div>
            </div>
          ) : (
            <form
              onSubmit={
                saveProfile
              }
              className="mt-7 grid gap-4 sm:grid-cols-2"
            >
              <FormField
                label="First name"
                error={
                  profileErrors
                    .first_name
                }
              >
                <input
                  value={
                    firstName
                  }
                  onChange={(e) =>
                    setFirstName(
                      e.target
                        .value,
                    )
                  }
                  className={
                    controlClass
                  }
                />
              </FormField>

              <FormField
                label="Last name"
                error={
                  profileErrors
                    .last_name
                }
              >
                <input
                  value={
                    lastName
                  }
                  onChange={(e) =>
                    setLastName(
                      e.target
                        .value,
                    )
                  }
                  className={
                    controlClass
                  }
                />
              </FormField>

              <div className="sm:col-span-2">
                <FormField
                  label="Email"
                  error={
                    profileErrors
                      .email
                  }
                >
                  <div className="relative">
                    <Mail
                      size={16}
                      className="absolute left-4 top-1/2 -translate-y-1/2 text-celestial dark:text-ash"
                    />

                    <input
                      type="email"
                      value={email}
                      onChange={(
                        e,
                      ) =>
                        setEmail(
                          e.target
                            .value,
                        )
                      }
                      className={`${controlClass} pl-11`}
                    />
                  </div>
                </FormField>
              </div>

              <div className="sm:col-span-2">
                <FormField
                  label="Phone number"
                  error={
                    profileErrors
                      .phone_number
                  }
                >
                  <div className="relative">
                    <Phone
                      size={16}
                      className="absolute left-4 top-1/2 -translate-y-1/2 text-celestial dark:text-ash"
                    />

                    <input
                      value={phone}
                      onChange={(
                        e,
                      ) =>
                        setPhone(
                          e.target
                            .value,
                        )
                      }
                      className={`${controlClass} pl-11`}
                    />
                  </div>
                </FormField>
              </div>

              <div className="sm:col-span-2 flex gap-3">
                <button
                  type="button"
                  onClick={
                    cancelProfileEdit
                  }
                  className="flex-1 rounded-2xl border border-celestial/15 px-4 py-3.5 text-sm font-semibold text-deep-blue transition hover:bg-cyan/25 dark:border-ash/15 dark:text-white dark:hover:bg-moss"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-celestial px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-cyan hover:text-deep-blue dark:bg-moss dark:text-lime-soft dark:hover:bg-ash dark:hover:text-slate-green"
                >
                  <Save
                    size={16}
                  />

                  Save changes
                </button>
              </div>
            </form>
          )}
        </section>


        {/* PASSWORD */}
        <section className="rounded-[2rem] border border-celestial/10 bg-white p-6 shadow-sm dark:border-ash/10 dark:bg-dark-card">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="grid size-12 place-items-center rounded-2xl bg-ash text-slate-green dark:bg-moss dark:text-lime-soft">
                <KeyRound
                  size={20}
                />
              </div>

              <div>
                <h2 className="text-xl font-semibold text-deep-blue dark:text-white">
                  Password
                </h2>

                <p className="mt-1 text-xs text-deep-blue/40 dark:text-white/35">
                  Keep your account
                  secure.
                </p>
              </div>
            </div>

            {!editingPassword ? (
              <button
                type="button"
                onClick={() =>
                  setEditingPassword(
                    true,
                  )
                }
                className="flex items-center gap-2 rounded-xl bg-ash/40 px-3 py-2 text-xs font-semibold text-slate-green transition hover:bg-ash dark:bg-moss dark:text-lime-soft"
              >
                <Pencil
                  size={14}
                />

                Change
              </button>
            ) : (
              <button
                type="button"
                onClick={
                  cancelPasswordEdit
                }
                className="grid size-9 place-items-center rounded-xl bg-ash/40 text-slate-green"
              >
                <X size={15} />
              </button>
            )}
          </div>

          {!editingPassword ? (
            <div className="mt-7">
              <div className="rounded-[1.5rem] bg-light-canvas p-5 dark:bg-phthalo">
                <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-deep-blue/35 dark:text-white/35">
                  Password
                </p>

                <p className="mt-2 text-xl font-semibold tracking-[0.2em] text-deep-blue dark:text-white">
                  ••••••••••••
                </p>

                <p className="mt-3 text-xs leading-5 text-deep-blue/40 dark:text-white/35">
                  Your password is
                  never displayed.
                  Choose Change when
                  you want to replace
                  it.
                </p>
              </div>
            </div>
          ) : (
            <form
              onSubmit={
                savePassword
              }
              className="mt-7 space-y-4"
            >
              <PasswordInput
                label="Current password"
                value={
                  currentPassword
                }
                show={
                  showCurrentPassword
                }
                error={
                  passwordErrors
                    .current_password
                }
                onChange={
                  setCurrentPassword
                }
                onToggle={() =>
                  setShowCurrentPassword(
                    !showCurrentPassword,
                  )
                }
              />

              <PasswordInput
                label="New password"
                value={
                  newPassword
                }
                show={
                  showNewPassword
                }
                error={
                  passwordErrors
                    .new_password
                }
                onChange={
                  setNewPassword
                }
                onToggle={() =>
                  setShowNewPassword(
                    !showNewPassword,
                  )
                }
              />

              <PasswordInput
                label="Confirm new password"
                value={
                  confirmPassword
                }
                show={
                  showConfirmPassword
                }
                error={
                  passwordErrors
                    .confirm_password
                }
                onChange={
                  setConfirmPassword
                }
                onToggle={() =>
                  setShowConfirmPassword(
                    !showConfirmPassword,
                  )
                }
              />

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={
                    cancelPasswordEdit
                  }
                  className="flex-1 rounded-2xl border border-celestial/15 px-4 py-3.5 text-sm font-semibold text-deep-blue dark:border-ash/15 dark:text-white"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-ash px-4 py-3.5 text-sm font-semibold text-slate-green transition hover:bg-cyan hover:text-deep-blue dark:bg-moss dark:text-lime-soft"
                >
                  <Save
                    size={16}
                  />

                  Save password
                </button>
              </div>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}


function ReadOnlyRow({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof UserRound;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-4 rounded-2xl border border-celestial/8 bg-light-canvas p-4 dark:border-ash/8 dark:bg-phthalo">
      <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-cyan/55 text-deep-blue dark:bg-moss dark:text-lime-soft">
        <Icon size={17} />
      </div>

      <div className="min-w-0">
        <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-deep-blue/35 dark:text-white/35">
          {label}
        </p>

        <p className="mt-1 truncate text-sm font-semibold text-deep-blue dark:text-white">
          {value}
        </p>
      </div>
    </div>
  );
}


function PasswordInput({
  label,
  value,
  show,
  error,
  onChange,
  onToggle,
}: {
  label: string;
  value: string;
  show: boolean;
  error?: string;

  onChange: (
    value: string,
  ) => void;

  onToggle: () => void;
}) {
  return (
    <FormField
      label={label}
      error={error}
    >
      <div className="relative">
        <input
          type={
            show
              ? "text"
              : "password"
          }
          value={value}
          onChange={(e) =>
            onChange(
              e.target.value,
            )
          }
          className={`${controlClass} pr-12`}
        />

        <button
          type="button"
          onClick={onToggle}
          className="absolute right-4 top-1/2 -translate-y-1/2 text-deep-blue/35 transition hover:text-celestial dark:text-white/35 dark:hover:text-ash"
        >
          {show ? (
            <EyeOff
              size={17}
            />
          ) : (
            <Eye size={17} />
          )}
        </button>
      </div>
    </FormField>
  );
}