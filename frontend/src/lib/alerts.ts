import Swal from "sweetalert2";


function darkMode() {
  return (
    localStorage.getItem(
      "propertyops_dashboard_theme",
    ) === "dark"
  );
}


function colors() {
  const dark =
    darkMode();

  return {
    background:
      dark
        ? "#1A361F"
        : "#ffffff",

    color:
      dark
        ? "#E2EFAD"
        : "#17324B",

    confirm:
      dark
        ? "#35603F"
        : "#519DC4",

    cancel:
      dark
        ? "#B7BEAA"
        : "#87D2F8",

    cancelText:
      "#17324B",
  };
}


export async function confirmAction({
  title,
  text,
  confirmText = "Continue",
}: {
  title: string;
  text: string;
  confirmText?: string;
}) {
  const palette =
    colors();

  const result =
    await Swal.fire({
      title,
      text,
      icon: "warning",

      background:
        palette.background,

      color:
        palette.color,

      iconColor:
        "#B7BEAA",

      showCancelButton:
        true,

      confirmButtonText:
        confirmText,

      cancelButtonText:
        "Cancel",

      confirmButtonColor:
        palette.confirm,

      cancelButtonColor:
        palette.cancel,

      reverseButtons:
        true,

      customClass: {
        popup:
          "rounded-[2rem]",
      },
    });

  return result.isConfirmed;
}


export async function successAlert(
  title: string,
  text?: string,
) {
  const palette =
    colors();

  await Swal.fire({
    title,
    text,
    icon: "success",

    background:
      palette.background,

    color:
      palette.color,

    iconColor:
      "#519DC4",

    confirmButtonColor:
      palette.confirm,

    confirmButtonText:
      "Done",
  });
}


export async function errorAlert(
  title: string,
  text: string,
) {
  const palette =
    colors();

  await Swal.fire({
    title,
    text,
    icon: "error",

    background:
      palette.background,

    color:
      palette.color,

    confirmButtonColor:
      palette.confirm,
  });
}