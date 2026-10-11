export interface FinancialMetric {
  name: string;
  value: number;
  raw_text_value: string;
  unit: string;
  period: string;
  yoy_growth?: number;
  source_chunk_id?: string;
  source_span: string;
  confidence: number;
}

export interface RiskFactor {
  category: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
  impact_assessment: string;
  mitigation_noted?: string;
  source_span?: string;
}

export interface DocumentClassification {
  document_type: string;
  confidence: number;
  industry_sector: string;
  sentiment: string;
  sentiment_score: number;
  key_drivers: string[];
}

export interface HallucinationCheckItem {
  metric_name: string;
  extracted_value: string;
  source_span_found: boolean;
  source_quote: string;
  calculated_consistency?: boolean;
  confidence_score: number;
  status: 'VERIFIED' | 'FLAGGED_DISCREPANCY' | 'UNCERTAIN';
  notes: string;
}

export interface GuardrailVerificationResult {
  is_verified: boolean;
  overall_groundedness_score: number;
  total_metrics_evaluated: number;
  verified_count: number;
  flagged_count: number;
  items: HallucinationCheckItem[];
  iteration: number;
  needs_refinement: boolean;
}

export interface ExecutiveSummary {
  company_name: string;
  ticker?: string;
  period: string;
  executive_tldr: string;
  financial_highlights: string[];
  risk_summary: string[];
  strategic_outlook: string;
  analyst_rating: string;
  actionable_takeaways: string[];
}

export interface AgentTraceEvent {
  agent_name: string;
  stage: string;
  status: 'started' | 'running' | 'completed' | 'refining' | 'failed';
  timestamp: string;
  thought_process: string;
  latency_ms: number;
  tokens_used: number;
}

export interface DocumentMetadata {
  filename: string;
  file_type: string;
  size_bytes: number;
  page_count: number;
  uploaded_at: string;
}

export interface OrchestratorStateResponse {
  job_id: string;
  status: string;
  metadata: DocumentMetadata;
  classification?: DocumentClassification;
  financial_metrics: FinancialMetric[];
  risk_factors: RiskFactor[];
  guardrail_result?: GuardrailVerificationResult;
  executive_summary?: ExecutiveSummary;
  trace: AgentTraceEvent[];
  total_turnaround_time_sec: number;
  baseline_manual_turnaround_time_sec: number;
  turnaround_reduction_pct: number;
}

export interface SampleDoc {
  id: string;
  title: string;
  doc_type: string;
  entity: string;
  description: string;
  size_kb: number;
}

export interface BenchmarkCaseResult {
  case_id: string;
  document_name: string;
  doc_type: string;
  expected_metrics_count: number;
  extracted_metrics_count: number;
  groundedness_pass_rate: number;
  hallucination_detected: boolean;
  guardrail_caught_trap?: boolean;
  pass_status: boolean;
  latency_sec: number;
}

export interface EvaluationSuiteResult {
  total_cases_evaluated: number;
  total_assertions_checked: number;
  passed_assertions: number;
  overall_test_suite_pass_rate: number;
  mean_groundedness_score: number;
  precision_rate: number;
  recall_rate: number;
  f1_score: number;
  hallucination_catch_rate: number;
  average_processing_time_sec: number;
  manual_analyst_time_savings_pct: number;
  evaluated_at: string;
  cases: BenchmarkCaseResult[];
}
