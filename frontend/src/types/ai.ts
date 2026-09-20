export type AIJobStatus =
  | "PENDING"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED";


export type AIAnalysisScope =
  | "PROPERTY"
  | "UNIT";


export type AIQualification =
  | "LOW"
  | "MEDIUM"
  | "HIGH";


export type AIEvidenceType =
  | "MAINTENANCE"
  | "EXPENSE";


export interface AIEvidence {
  id: number;

  evidence_type:
    AIEvidenceType;

  evidence_id: number;

  evidence_date:
    | string
    | null;

  category:
    | string
    | null;

  description:
    | string
    | null;

  status:
    | string
    | null;

  amount:
    | string
    | null;

  unit_id:
    | number
    | null;
}


export interface AIInsight {
  id: number;
  job_id: number;

  finding: string;

  qualification:
    AIQualification;

  recommendation:
    | string
    | null;

  explanation: string;

  created_at: string;

  evidence:
    AIEvidence[];
}


export interface AIAnalysisJob {
  id: number;
  owner_user_id: number;

  scope_type:
    AIAnalysisScope;

  property_id:
    | number
    | null;

  unit_id:
    | number
    | null;

  status:
    AIJobStatus;

  error_message:
    | string
    | null;

  created_at: string;

  started_at:
    | string
    | null;

  completed_at:
    | string
    | null;

  insight?:
    | AIInsight
    | null;
}