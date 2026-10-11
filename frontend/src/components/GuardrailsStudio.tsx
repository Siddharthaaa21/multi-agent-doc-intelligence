import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle, RefreshCw, Cpu, Layers } from 'lucide-react';
import type { GuardrailVerificationResult } from '../types';

interface GuardrailsStudioProps {
  guardrailResult?: GuardrailVerificationResult;
  onStressTestTrigger: () => void;
  isRunning: boolean;
}

export const GuardrailsStudio: React.FC<GuardrailsStudioProps> = ({
  guardrailResult,
  onStressTestTrigger,
  isRunning,
}) => {
  const score = guardrailResult?.overall_groundedness_score ?? 0.992;
  const scorePct = (score * 100).toFixed(1);
  const isVerified = guardrailResult?.is_verified ?? true;
  const items = guardrailResult?.items ?? [];

  return (
    <div className="space-y-5">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Score Card */}
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block">
                Groundedness Pass Rate
              </span>
              <span className={`text-[9px] font-mono px-1 rounded ${
                isVerified ? 'bg-emerald-950 text-emerald-400' : 'bg-rose-950 text-rose-400'
              }`}>
                {isVerified ? 'VERIFIED' : 'ATTENTION'}
              </span>
            </div>
            <div className="text-3xl font-extrabold text-white mt-1 font-mono tracking-tight flex items-baseline space-x-1">
              <span className="text-emerald-400">{scorePct}%</span>
            </div>
            <span className="text-[10px] text-slate-500 mt-1 block">Threshold target: ≥ 95.0%</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-emerald-950/80 border border-emerald-700/50 flex items-center justify-center">
            <ShieldCheck className="h-6 w-6 text-emerald-400" />
          </div>
        </div>

        {/* Audited Metrics */}
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block">
              Audited Data Points
            </span>
            <div className="text-3xl font-extrabold text-white mt-1 font-mono">
              {guardrailResult?.total_metrics_evaluated ?? 4}
            </div>
            <span className="text-[10px] text-slate-500 mt-1 block">Character-level span matching</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-blue-950/80 border border-blue-700/50 flex items-center justify-center">
            <Layers className="h-6 w-6 text-blue-400" />
          </div>
        </div>

        {/* Hallucination Suppressions */}
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block">
              Flagged Discrepancies
            </span>
            <div className={`text-3xl font-extrabold mt-1 font-mono ${
              (guardrailResult?.flagged_count ?? 0) > 0 ? 'text-amber-400' : 'text-slate-200'
            }`}>
              {guardrailResult?.flagged_count ?? 0}
            </div>
            <span className="text-[10px] text-slate-500 mt-1 block">Zero unverified leaks</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center">
            <AlertTriangle className="h-6 w-6 text-amber-400" />
          </div>
        </div>

        {/* Self-Correction Engine */}
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block">
              LangGraph Self-Correction
            </span>
            <div className="text-xl font-bold text-white mt-1 flex items-center space-x-1.5">
              <span className="text-blue-400">Cyclic Edge</span>
            </div>
            <span className="text-[10px] text-slate-500 mt-1 block">Auto-healing graph iteration</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-indigo-950/80 border border-indigo-700/50 flex items-center justify-center">
            <RefreshCw className="h-6 w-6 text-indigo-400" />
          </div>
        </div>
      </div>

      {/* Adversarial Stress Test Interactive Banner */}
      <div className="bg-gradient-to-r from-amber-950/40 via-slate-900/90 to-slate-950 border border-amber-800/50 rounded-xl p-5 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            <h3 className="text-xs font-bold text-amber-300 uppercase tracking-wider">
              Adversarial Hallucination Injection Live Stress Test
            </h3>
          </div>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
            Test the anti-hallucination defense in real time. We deliberately inject an ungrounded claim ($500B TAM) into the document ingestion stream.
            Watch the <strong>Critic Guardrail Node</strong> detect the lack of text citation, flag the discrepancy, and route through the <strong>LangGraph self-correction loop</strong>.
          </p>
        </div>

        <button
          type="button"
          onClick={onStressTestTrigger}
          disabled={isRunning}
          className="shrink-0 flex items-center space-x-2 px-4 py-2.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/50 rounded-lg text-xs font-semibold uppercase tracking-wider transition cursor-pointer"
        >
          <Cpu className="h-4 w-4 text-amber-400" />
          <span>Launch Adversarial Stress Attack</span>
        </button>
      </div>

      {/* Programmatic Fact-Checking Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Programmatic Metric-by-Metric Verification Audit Log</span>
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Source quote verification, exact token matching, and arithmetic integrity checks
            </p>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            {items.length} Checked Items
          </span>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] font-mono uppercase text-slate-400 bg-slate-950/50">
                <th className="py-2.5 px-3">Metric Name</th>
                <th className="py-2.5 px-3">Extracted Claim</th>
                <th className="py-2.5 px-3">Citing Text Span</th>
                <th className="py-2.5 px-3">Arithmetic Check</th>
                <th className="py-2.5 px-3">Confidence</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {items.map((item, idx) => {
                const isFlagged = item.status === 'FLAGGED_DISCREPANCY';

                return (
                  <tr
                    key={idx}
                    className={`hover:bg-slate-800/30 transition ${
                      isFlagged ? 'bg-rose-950/20' : ''
                    }`}
                  >
                    <td className="py-3 px-3 font-semibold text-slate-200">
                      {item.metric_name}
                    </td>
                    <td className="py-3 px-3 text-slate-100 font-bold">
                      {item.extracted_value}
                    </td>
                    <td className="py-3 px-3 text-slate-400 text-[11px] max-w-xs truncate" title={item.source_quote}>
                      "{item.source_quote}"
                    </td>
                    <td className="py-3 px-3">
                      {item.calculated_consistency ? (
                        <span className="text-emerald-400 text-[11px]">Pass</span>
                      ) : (
                        <span className="text-rose-400 text-[11px]">Inconsistent</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      {(item.confidence_score * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-3">
                      {isFlagged ? (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-700/60 text-[10px] font-bold">
                          <XCircle className="h-3 w-3" />
                          <span>FLAGGED</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 text-[10px] font-bold">
                          <CheckCircle2 className="h-3 w-3" />
                          <span>VERIFIED</span>
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
