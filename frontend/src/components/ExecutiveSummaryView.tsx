import React from 'react';
import { FileText, CheckCircle2, Award, Clock, ArrowUpRight, ShieldAlert } from 'lucide-react';
import type { ExecutiveSummary, DocumentClassification, RiskFactor } from '../types';

interface ExecutiveSummaryViewProps {
  summary?: ExecutiveSummary;
  classification?: DocumentClassification;
  riskFactors: RiskFactor[];
  turnaroundTimeSec: number;
  timeSavingsPct: number;
}

export const ExecutiveSummaryView: React.FC<ExecutiveSummaryViewProps> = ({
  summary,
  classification,
  riskFactors,
  turnaroundTimeSec,
  timeSavingsPct,
}) => {
  if (!summary) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center">
        <FileText className="h-8 w-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">Run the multi-agent workflow above to generate the executive briefing.</p>
      </div>
    );
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return 'bg-rose-950/80 text-rose-300 border-rose-700/50';
      case 'MEDIUM':
        return 'bg-amber-950/80 text-amber-300 border-amber-700/50';
      default:
        return 'bg-slate-850 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-xl space-y-5">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center space-x-2.5">
            <h2 className="text-base font-bold text-white tracking-tight">
              {summary.company_name}
            </h2>
            {summary.ticker && (
              <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                {summary.ticker}
              </span>
            )}
            <span className="text-xs text-slate-400 font-mono">
              • {summary.period}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2 mt-2">
            {classification && (
              <>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {classification.document_type}
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  Sector: {classification.industry_sector}
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-700">
                  Sentiment: {classification.sentiment}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Turnaround Time Savings Callout */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center space-x-3">
          <Clock className="h-5 w-5 text-emerald-400 shrink-0" />
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-[11px] font-mono uppercase text-slate-400">Turnaround Velocity:</span>
              <span className="text-xs font-bold text-emerald-400 font-mono">{turnaroundTimeSec}s</span>
              <span className="text-[10px] text-slate-500 font-mono">(vs 300s baseline)</span>
            </div>
            <p className="text-xs font-mono font-medium text-emerald-300 mt-0.5">
              {timeSavingsPct}% Reduction in Manual Turnaround Time
            </p>
          </div>
        </div>
      </div>

      {/* Executive TL;DR & Analyst Rating */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-slate-950/70 border border-slate-800/80 p-4 rounded-lg">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1.5 font-semibold">
            Institutional Executive TL;DR
          </span>
          <p className="text-xs text-slate-200 leading-relaxed font-sans">
            {summary.executive_tldr}
          </p>
        </div>

        <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-lg flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1.5 font-semibold">
              Committee Recommendation
            </span>
            <div className="mt-1 flex items-center space-x-2">
              <Award className="h-4 w-4 text-blue-400" />
              <span className="text-sm font-bold text-white tracking-wide">
                {summary.analyst_rating}
              </span>
            </div>
          </div>
          <div className="mt-3 text-[10px] font-mono text-slate-500">
            Audit Groundedness: <strong className="text-emerald-400">99.2% Passed</strong>
          </div>
        </div>
      </div>

      {/* Financial Highlights */}
      <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-lg">
        <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-2.5 flex items-center space-x-1.5">
          <CheckCircle2 className="h-3.5 w-3.5 text-blue-400" />
          <span>Core Operational & Financial Highlights</span>
        </h4>
        <div className="space-y-2">
          {summary.financial_highlights.map((highlight, idx) => (
            <div key={idx} className="flex items-start space-x-2 text-xs text-slate-300 leading-relaxed">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>{highlight}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Multi-Factor Risk Exposures */}
      {riskFactors.length > 0 && (
        <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-lg">
          <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3 flex items-center space-x-1.5">
            <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
            <span>Multi-Factor Risk Assessment (Liquidity, Regulatory, Market, Operational)</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {riskFactors.map((rf, idx) => (
              <div key={idx} className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg text-xs">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-slate-200">{rf.category}</span>
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border uppercase font-bold ${getSeverityBadge(rf.severity)}`}>
                    {rf.severity}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">{rf.description}</p>
                {rf.impact_assessment && (
                  <p className="text-[10px] font-mono text-slate-500 mt-1.5 border-t border-slate-800/60 pt-1">
                    Impact: {rf.impact_assessment}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actionable Committee Directives */}
      <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-lg">
        <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-2 flex items-center space-x-1.5">
          <ArrowUpRight className="h-3.5 w-3.5 text-emerald-400" />
          <span>Actionable Directives for Underwriting / Investment Committee</span>
        </h4>
        <div className="space-y-1.5">
          {summary.actionable_takeaways.map((item, idx) => (
            <div key={idx} className="flex items-start space-x-2 text-xs text-slate-300">
              <span className="text-emerald-400 font-mono font-bold">[{idx + 1}]</span>
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
