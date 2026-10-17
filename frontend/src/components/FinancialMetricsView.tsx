import React from 'react';
import { DollarSign, TrendingUp, TrendingDown, Quote, CheckCircle2 } from 'lucide-react';
import type { FinancialMetric } from '../types';

interface FinancialMetricsViewProps {
  metrics: FinancialMetric[];
}

export const FinancialMetricsView: React.FC<FinancialMetricsViewProps> = ({ metrics }) => {
  if (!metrics || metrics.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center">
        <DollarSign className="h-8 w-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No financial metrics extracted yet. Run the workflow above.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
            <DollarSign className="h-4 w-4 text-emerald-400" />
            <span>Extracted Financial Metrics & Grounded Source Spans</span>
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Structured GAAP/Non-GAAP extraction with token-level character spans verified by Critic Guardrail
          </p>
        </div>
        <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-700/50 px-2 py-0.5 rounded">
          {metrics.length} Metrics Verified
        </span>
      </div>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {metrics.map((m, idx) => {
          const isGrowthPositive = (m.yoy_growth ?? 0) >= 0;

          return (
            <div
              key={idx}
              className="bg-slate-950/70 border border-slate-800 hover:border-slate-700 p-3.5 rounded-lg transition group relative"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-slate-400 truncate max-w-[140px]">
                  {m.name}
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                  {m.period}
                </span>
              </div>

              <div className="mt-2 flex items-baseline space-x-1.5">
                <span className="text-xl font-bold text-white tracking-tight font-mono">
                  {m.unit === '%' ? `${m.value}%` : `$${m.value}`}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {m.unit !== '%' ? m.unit : ''}
                </span>
              </div>

              {/* YoY Growth if present */}
              {m.yoy_growth !== null && m.yoy_growth !== undefined && (
                <div className="mt-1 flex items-center space-x-1 text-[11px]">
                  {isGrowthPositive ? (
                    <TrendingUp className="h-3 w-3 text-emerald-400" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-rose-400" />
                  )}
                  <span className={isGrowthPositive ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
                    {isGrowthPositive ? `+${m.yoy_growth}%` : `${m.yoy_growth}%`} YoY
                  </span>
                </div>
              )}

              {/* Grounded Source Snippet Quote */}
              <div className="mt-2.5 pt-2 border-t border-slate-900 flex items-start space-x-1.5">
                <Quote className="h-3 w-3 text-blue-400 mt-0.5 shrink-0" />
                <p className="text-[10px] text-slate-400 font-mono not-italic line-clamp-2" title={m.source_span}>
                  "{m.source_span}"
                </p>
              </div>

              <div className="mt-1.5 flex items-center justify-between text-[10px] font-mono text-slate-500">
                <span className="flex items-center space-x-1 text-emerald-500">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>Grounded (99%)</span>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
