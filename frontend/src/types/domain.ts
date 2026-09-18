import type {
  User,
} from "./auth";


export type UnitType =
  | "APARTMENT"
  | "OFFICE"
  | "RETAIL"
  | "STORAGE"
  | "OTHER";


export type UnitStatus =
  | "VACANT"
  | "OCCUPIED"
  | "UNAVAILABLE";


export type LeaseStatus =
  | "ACTIVE"
  | "ENDED";


export type MaintenanceStatus =
  | "OPEN"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "RESOLVED";


export type RentObligationStatus =
  | "PENDING"
  | "PAID"
  | "CANCELED";


export interface Property {
  id: number;
  owner_id: number;
  name: string;
  address: string;
  city: string;
  country: string;
  created_at: string;
}


export interface Building {
  id: number;
  property_id: number;
  name: string;
  created_at: string;
}


export interface Unit {
  id: number;
  building_id: number;
  unit_number: string;
  unit_type: UnitType;
  status: UnitStatus;
  created_at: string;
}


export interface Lease {
  id: number;
  unit_id: number;
  tenant_user_id: number;

  start_date: string;

  end_date:
    | string
    | null;

  rent_amount:
    | string
    | number;

  status: LeaseStatus;
  created_at: string;
}


export interface LeaseWithContext
  extends Lease {
  property_name: string;
  building_name: string;
  unit_number: string;
}


export interface Maintenance {
  id: number;
  unit_id: number;
  created_by_user_id: number;
  category: string;
  description: string;
  status: MaintenanceStatus;
  created_at: string;

  resolved_at:
    | string
    | null;
}


export interface Expense {
  id: number;
  property_id: number;

  unit_id:
    | number
    | null;

  maintenance_id:
    | number
    | null;

  amount:
    | string
    | number;

  category: string;
  expense_date: string;

  description:
    | string
    | null;

  created_at: string;
}


export interface RentObligation {
  id: number;
  lease_id: number;

  amount:
    | string
    | number;

  due_date: string;

  status:
    RentObligationStatus;

  created_at: string;
}


export interface BuildingNode
  extends Building {
  units: Unit[];
}


export interface PropertyNode
  extends Property {
  buildings:
    BuildingNode[];
}


export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}


export interface OwnerLeaseItem {
  id: number;
  status: LeaseStatus;
  start_date: string;

  end_date:
    | string
    | null;

  rent_amount:
    | number
    | string;

  created_at: string;

  property_id: number;
  property_name: string;

  building_id: number;
  building_name: string;

  unit_id: number;
  unit_number: string;

  tenant: User;
}


export interface OwnerLeasePage {
  items: OwnerLeaseItem[];
  meta: PageMeta;
}


export interface OwnerMaintenanceItem {
  id: number;

  category: string;
  description: string;

  status:
    MaintenanceStatus;

  created_at: string;

  resolved_at:
    | string
    | null;

  property_id: number;
  property_name: string;

  building_id: number;
  building_name: string;

  unit_id: number;
  unit_number: string;

  creator: User;
}


export interface OwnerMaintenancePage {
  items:
    OwnerMaintenanceItem[];

  meta: PageMeta;
}


export interface OwnerExpenseItem {
  id: number;

  property_id: number;
  property_name: string;

  building_id:
    | number
    | null;

  building_name:
    | string
    | null;

  unit_id:
    | number
    | null;

  unit_number:
    | string
    | null;

  maintenance_id:
    | number
    | null;

  amount:
    | string
    | number;

  category: string;
  expense_date: string;

  description:
    | string
    | null;

  created_at: string;
}


export interface OwnerExpensePage {
  items:
    OwnerExpenseItem[];

  meta: PageMeta;
}


export interface OwnerRentItem {
  id: number;

  amount:
    | string
    | number;

  due_date: string;

  status:
    RentObligationStatus;

  created_at: string;

  lease_id: number;

  property_id: number;
  property_name: string;

  building_id: number;
  building_name: string;

  unit_id: number;
  unit_number: string;

  tenant: User;
}


export interface OwnerRentPage {
  items:
    OwnerRentItem[];

  meta: PageMeta;
}


export interface UnitOccupancy {
  occupied: boolean;

  lease:
    | Lease
    | null;

  tenant:
    | User
    | null;
}


export interface TenantHome {
  lease_id: number;

  property_id: number;
  property_name: string;

  building_id: number;
  building_name: string;

  unit_id: number;
  unit_number: string;

  rent_amount:
    | number
    | string;

  start_date: string;

  end_date:
    | string
    | null;
}