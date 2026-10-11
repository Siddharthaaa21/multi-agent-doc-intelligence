import type {
  SampleDoc,
  OrchestratorStateResponse,
  EvaluationSuiteResult
} from '../types';

const API_BASE = '/api';

export async function fetchSamples(): Promise<SampleDoc[]> {
  const res = await fetch(`${API_BASE}/documents/samples`);
  if (!res.ok) throw new Error('Failed to fetch samples');
  return res.json();
}

export async function fetchSampleContent(filename: string): Promise<{ filename: string; content: string }> {
  const res = await fetch(`${API_BASE}/documents/sample/${filename}`);
  if (!res.ok) throw new Error('Failed to fetch sample content');
  return res.json();
}

export async function uploadDocumentFile(file: File): Promise<{ filename: string; content: string; preview: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload file');
  return res.json();
}

export async function runOrchestration(
  rawText: string,
  filename: string,
  injectTrap: boolean = false,
  provider: string = 'simulation'
): Promise<{ job_id: string; status: string }> {
  const res = await fetch(`${API_BASE}/orchestrator/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      raw_text: rawText,
      filename,
      inject_hallucination_trap: injectTrap,
      llm_provider: provider,
    }),
  });
  if (!res.ok) throw new Error('Failed to initiate orchestrator run');
  return res.json();
}

export async function getJobStatus(jobId: string): Promise<OrchestratorStateResponse> {
  const res = await fetch(`${API_BASE}/orchestrator/status/${jobId}`);
  if (!res.ok) throw new Error('Failed to fetch job status');
  return res.json();
}

export async function fetchBenchmark(): Promise<EvaluationSuiteResult> {
  const res = await fetch(`${API_BASE}/eval/benchmark`);
  if (!res.ok) throw new Error('Failed to fetch benchmark report');
  return res.json();
}

export async function runEvaluationSuite(): Promise<EvaluationSuiteResult> {
  const res = await fetch(`${API_BASE}/eval/run`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to execute evaluation suite');
  return res.json();
}
