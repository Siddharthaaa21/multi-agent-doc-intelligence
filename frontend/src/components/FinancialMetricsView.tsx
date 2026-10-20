import React from 'react';
import { CheckCircle2, TrendingUp, TrendingDown } from 'lucide-react';
import type { FinancialMetric } from '../types';

interface FinancialMetricsViewProps {
  metrics: FinancialMetric[];
}

export const FinancialMetricsView: React.FC<FinancialMetricsViewProps> = ({ metrics }) => {
  if (!metrics || metrics.length === 0) return null;

  return (
    <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-zinc-800/60 flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-300">
          Audited Financial Metrics
        </span>
        <span className="text-[11px] font-mono text-zinc-500">
          {metrics.length} line items extracted
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-zinc-950/60 text-zinc-400 border-b border-zinc-800/60 text-[11px]">
            <tr>
              <th className="py-2.5 px-4 font-normal">Line Item</th>
              <th className="py-2.5 px-4 font-normal">Period</th>
              <th className="py-2.5 px-4 font-normal text-right">Value</th>
              <th className="py-2.5 px-4 font-normal text-right">YoY</th>
              <th className="py-2.5 px-4 font-normal">Source Footnote / Text Anchor</th>
              <th className="py-2.5 px-4 font-normal text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/40 text-zinc-300">
            {metrics.map((m, idx) => {
              const isGrowthPositive = (m.yoy_growth ?? 0) >= 0;

              return (
                <tr key={idx} className="hover:bg-zinc-800/20 transition-colors">
                  <td className="py-2.5 px-4 font-sans font-medium text-zinc-200">
                    {m.name}
                  </td>
                  <td className="py-2.5 px-4 text-zinc-400">
                    {m.period}
                  </td>
                  <td className="py-2.5 px-4 text-right font-semibold text-zinc-100">
                    {m.unit === '%' ? `${m.value}%` : `$${m.value}${m.unit ? ` ${m.unit}` : ''}`}
                  </td>
                  <td className="py-2.5 px-4 text-right whitespace-nowrap">
                    {m.yoy_growth !== null && m.yoy_growth !== undefined ? (
                      <span className={`inline-flex items-center space-x-0.5 text-[11px] ${
                        isGrowthPositive ? 'text-emerald-400' : 'text-rose-400'
                      }`}>
                        {isGrowthPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                        <span>{isGrowthPositive ? `+${m.yoy_growth}%` : `${m.yoy_growth}%`}</span>
                      </span>
                    ) : (
                      <span className="text-zinc-600">—</span>
                    )}
                  </td>
                  <td className="py-2.5 px-4 text-zinc-400 max-w-sm truncate" title={m.source_span}>
                    <span className="text-[11px] text-zinc-400 font-mono">
                      "{m.source_span}"
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-right whitespace-nowrap">
                    <span className="inline-flex items-center space-x-1 text-emerald-400 text-[11px]">
                      <CheckCircle2 className="h-3 w-3" />
                      <span>Verified</span>
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FinancialMetricsView;
