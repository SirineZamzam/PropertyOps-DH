export type UserRole =
  | "ADMIN"
  | "OWNER"
  | "TENANT";


export interface User {
  id: number;

  first_name:
    | string
    | null;

  last_name:
    | string
    | null;

  phone_number:
    | string
    | null;

  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}


export interface LoginResponse {
  access_token: string;
  token_type: string;
}
