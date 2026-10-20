import React from 'react';
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
  if (!summary) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
      {/* Primary Synthesis (7 cols) */}
      <div className="lg:col-span-7 bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-5 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-zinc-800/60 pb-3">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-semibold text-white tracking-tight">
                {summary.company_name}
              </h2>
              {summary.ticker && (
                <span className="text-[11px] font-mono font-medium px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300">
                  {summary.ticker}
                </span>
              )}
              <span className="text-xs text-zinc-500 font-mono">
                {summary.period}
              </span>
            </div>
            {classification && (
              <div className="text-[11px] text-zinc-400 mt-1 flex items-center space-x-2">
                <span>{classification.document_type}</span>
                <span>•</span>
                <span>Sector: {classification.industry_sector}</span>
                <span>•</span>
                <span>Sentiment: {classification.sentiment}</span>
              </div>
            )}
          </div>

          <div className="text-right">
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-zinc-800 text-zinc-200 border border-zinc-700/60 font-mono">
              {summary.analyst_rating}
            </span>
          </div>
        </div>

        {/* TL;DR */}
        <div>
          <div className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider mb-1">
            Executive Synthesis
          </div>
          <p className="text-xs text-zinc-300 leading-relaxed font-sans">
            {summary.executive_tldr}
          </p>
        </div>

        {/* Highlights */}
        {summary.financial_highlights.length > 0 && (
          <div>
            <div className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider mb-1.5">
              Key Highlights
            </div>
            <ul className="space-y-1.5">
              {summary.financial_highlights.slice(0, 4).map((h, i) => (
                <li key={i} className="text-xs text-zinc-300 flex items-start space-x-2">
                  <span className="text-zinc-500 shrink-0 mt-0.5">•</span>
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Directives */}
        {summary.actionable_takeaways.length > 0 && (
          <div className="pt-2 border-t border-zinc-800/40">
            <div className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider mb-1.5">
              Directives
            </div>
            <div className="space-y-1">
              {summary.actionable_takeaways.slice(0, 3).map((item, idx) => (
                <div key={idx} className="text-xs text-zinc-400 flex items-start space-x-2">
                  <span className="text-zinc-500 font-mono text-[11px]">0{idx + 1}.</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Side Panel: Risk & Audit Stats (5 cols) */}
      <div className="lg:col-span-5 space-y-4">
        {/* Velocity Card */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider">
              Turnaround Velocity
            </div>
            <div className="text-xl font-bold font-mono text-zinc-100 mt-0.5">
              {turnaroundTimeSec}s
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs font-mono font-semibold text-emerald-400">
              -{timeSavingsPct}%
            </span>
            <div className="text-[10px] text-zinc-500 font-mono">vs 300s baseline</div>
          </div>
        </div>

        {/* Risk Assessment */}
        {riskFactors.length > 0 && (
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 space-y-2.5">
            <div className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider">
              Risk Factors
            </div>
            <div className="space-y-2">
              {riskFactors.slice(0, 4).map((rf, idx) => (
                <div key={idx} className="flex items-start justify-between gap-2 text-xs">
                  <div className="flex-1">
                    <span className="font-medium text-zinc-200">{rf.category}</span>
                    <p className="text-[11px] text-zinc-400 line-clamp-1 mt-0.5">{rf.description}</p>
                  </div>
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded uppercase shrink-0 font-medium ${
                    rf.severity === 'HIGH'
                      ? 'bg-rose-950/60 text-rose-300 border border-rose-800/50'
                      : rf.severity === 'MEDIUM'
                      ? 'bg-amber-950/60 text-amber-300 border border-amber-800/50'
                      : 'bg-zinc-800 text-zinc-400'
                  }`}>
                    {rf.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExecutiveSummaryView;
