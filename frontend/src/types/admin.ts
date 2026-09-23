import type {
  SubscriptionStatus,
} from "./subscription";


export interface AdminOverview {
  total_owners: number;
  active_owners: number;
  inactive_owners: number;
  total_properties: number;
  total_units: number;
}


export interface AdminOwnerItem {
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
  is_active: boolean;
  created_at: string;

  property_count: number;
  building_count: number;
  unit_count: number;
  active_lease_count: number;

  plan_code:
    | string
    | null;

  plan_name:
    | string
    | null;

  subscription_status:
    | SubscriptionStatus
    | null;

  max_properties:
    | number
    | null;
}


export interface AdminPageMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}


export interface AdminOwnerPage {
  items:
    AdminOwnerItem[];

  meta: AdminPageMeta;
}
