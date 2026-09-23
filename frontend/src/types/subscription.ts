export type SubscriptionStatus =
  | "FREE"
  | "ACTIVE"
  | "INCOMPLETE"
  | "PAST_DUE"
  | "CANCELED";


export type BillingInterval =
  | "MONTHLY"
  | "YEARLY";


export type SubscriptionPaymentStatus =
  | "PAID"
  | "FAILED";


export interface SubscriptionPlan {
  id: number;
  code: string;
  name: string;

  monthly_price:
    | string
    | number;

  yearly_price:
    | string
    | number;

  max_properties:
    | number
    | null;

  sort_order: number;
  is_active: boolean;

  created_at: string;
  updated_at: string;
}


export interface OwnerSubscription {
  id: number;
  owner_id: number;

  status:
    SubscriptionStatus;

  billing_interval:
    | BillingInterval
    | null;

  current_period_end:
    | string
    | null;

  cancel_at_period_end:
    boolean;

  property_count: number;

  effective_max_properties:
    | number
    | null;

  plan:
    SubscriptionPlan;
}


export interface SubscriptionPaymentItem {
  id: number;
  plan_id: number;
  plan_code: string;
  plan_name: string;

  stripe_invoice_id: string;

  amount:
    | string
    | number;

  currency: string;

  status:
    SubscriptionPaymentStatus;

  created_at: string;
}


export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}


export interface AdminSubscriptionSummary {
  total: number;
  free: number;
  active_paid: number;
  incomplete: number;
  past_due: number;
  canceled: number;
}


export interface AdminSubscriptionItem {
  owner_id: number;
  owner_email: string;

  owner_first_name:
    | string
    | null;

  owner_last_name:
    | string
    | null;

  owner_is_active: boolean;

  plan_id: number;
  plan_code: string;
  plan_name: string;

  status:
    SubscriptionStatus;

  billing_interval:
    | BillingInterval
    | null;

  property_count: number;

  max_properties:
    | number
    | null;

  current_period_end:
    | string
    | null;

  cancel_at_period_end:
    boolean;
}


export interface AdminSubscriptionPage {
  items:
    AdminSubscriptionItem[];

  meta: PageMeta;
}


export interface AdminSubscriptionPaymentItem {
  id: number;

  owner_id: number;
  owner_email: string;

  owner_first_name:
    | string
    | null;

  owner_last_name:
    | string
    | null;

  plan_id: number;
  plan_code: string;
  plan_name: string;

  stripe_invoice_id: string;

  amount:
    | string
    | number;

  currency: string;

  status:
    SubscriptionPaymentStatus;

  created_at: string;
}


export interface AdminSubscriptionPaymentPage {
  items:
    AdminSubscriptionPaymentItem[];

  meta: PageMeta;
}
