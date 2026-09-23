export type SubscriptionStatus =
  | "FREE"
  | "ACTIVE"
  | "INCOMPLETE"
  | "PAST_DUE"
  | "CANCELED";


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

  property_count: number;

  plan:
    SubscriptionPlan;
}
