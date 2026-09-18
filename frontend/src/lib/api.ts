const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://127.0.0.1:8000/api";


export type FieldErrors =
  Record<string, string>;


export class ApiError extends Error {
  status: number;
  fieldErrors: FieldErrors;

  constructor(
    message: string,
    status: number,
    fieldErrors: FieldErrors = {},
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}


function getFastApiErrors(
  data: unknown,
): {
  message: string;
  fieldErrors: FieldErrors;
} {
  if (
    typeof data !== "object" ||
    data === null
  ) {
    return {
      message:
        "Something went wrong.",
      fieldErrors: {},
    };
  }

  const result =
    data as {
      detail?: unknown;
    };

  if (
    typeof result.detail ===
    "string"
  ) {
    return {
      message: result.detail,
      fieldErrors: {},
    };
  }

  if (
    Array.isArray(result.detail)
  ) {
    const fieldErrors:
      FieldErrors = {};

    for (
      const item of
      result.detail
    ) {
      if (
        typeof item !==
          "object" ||
        item === null
      ) {
        continue;
      }

      const validation =
        item as {
          loc?: unknown[];
          msg?: string;
        };

      const field =
        validation.loc
          ?.filter(
            (part) =>
              part !== "body",
          )
          .at(-1);

      if (
        typeof field ===
          "string" &&
        validation.msg
      ) {
        fieldErrors[field] =
          validation.msg;
      }
    }

    return {
      message:
        "Please check the highlighted fields.",
      fieldErrors,
    };
  }

  return {
    message:
      "Something went wrong.",
    fieldErrors: {},
  };
}


export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token =
    localStorage.getItem(
      "propertyops_access_token",
    );

  const headers =
    new Headers(
      options.headers,
    );

  if (
    options.body &&
    !headers.has(
      "Content-Type",
    )
  ) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  const response =
    await fetch(
      `${API_URL}${path}`,
      {
        ...options,
        headers,
      },
    );

  if (!response.ok) {
    let data: unknown;

    try {
      data =
        await response.json();
    } catch {
      data = null;
    }

    const {
      message,
      fieldErrors,
    } = getFastApiErrors(
      data,
    );

    throw new ApiError(
      message,
      response.status,
      fieldErrors,
    );
  }

  if (
    response.status === 204
  ) {
    return undefined as T;
  }

  const text =
    await response.text();

  if (!text) {
    return undefined as T;
  }

  return JSON.parse(
    text,
  ) as T;
}