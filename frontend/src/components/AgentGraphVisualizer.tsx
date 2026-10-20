import React from 'react';
import { Check, Loader2, RefreshCw } from 'lucide-react';
import type { AgentTraceEvent } from '../types';

interface AgentGraphVisualizerProps {
  status: string;
  trace: AgentTraceEvent[];
  needsRefinement?: boolean;
  iterations: number;
}

export const AgentGraphVisualizer: React.FC<AgentGraphVisualizerProps> = ({
  status,
  trace,
  iterations,
}) => {
  const isRunning = status === 'running' || status === 'queued';
  const isCompleted = status === 'completed';

  const stages = [
    { id: 'ingest', label: 'Ingestion', done: trace.some(t => t.stage.includes('Ingestion')) },
    { id: 'classify', label: 'Taxonomy', done: trace.some(t => t.stage.includes('Classification') || t.stage.includes('Taxonomy')) },
    { id: 'guardrail', label: 'Guardrail Critic', done: trace.some(t => t.stage.includes('Guardrail')) },
    { id: 'refine', label: iterations > 1 ? `Self-Correction (${iterations})` : 'Refinement', done: trace.some(t => t.stage.includes('Refinement')), optional: iterations <= 1 },
    { id: 'synthesis', label: 'Executive Synthesis', done: trace.some(t => t.stage.includes('Synthesis')) },
  ];

  const visibleStages = stages.filter(s => !s.optional || s.done);

  return (
    <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl px-4 py-2.5 flex items-center justify-between text-xs font-mono">
      <div className="flex items-center space-x-2">
        <span className="text-[11px] text-zinc-500 uppercase tracking-wider">Pipeline:</span>
        <div className="flex items-center space-x-1.5 overflow-x-auto">
          {visibleStages.map((stage, idx) => (
            <React.Fragment key={stage.id}>
              {idx > 0 && <span className="text-zinc-600">→</span>}
              <div
                className={`flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] transition ${
                  stage.done
                    ? 'bg-zinc-800 text-zinc-200'
                    : isRunning
                    ? 'bg-zinc-900 text-zinc-400'
                    : 'text-zinc-600'
                }`}
              >
                {stage.done ? (
                  <Check className="h-3 w-3 text-emerald-400 shrink-0" />
                ) : isRunning ? (
                  <Loader2 className="h-3 w-3 animate-spin text-zinc-400 shrink-0" />
                ) : null}
                <span>{stage.label}</span>
              </div>
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="flex items-center space-x-2 shrink-0">
        {iterations > 1 && (
          <span className="text-[10px] text-amber-400 flex items-center space-x-1">
            <RefreshCw className="h-2.5 w-2.5" />
            <span>Cycle #{iterations}</span>
          </span>
        )}
        <span className={`text-[10px] uppercase font-semibold ${
          isCompleted ? 'text-emerald-400' : isRunning ? 'text-zinc-300' : 'text-zinc-500'
        }`}>
          {status}
        </span>
      </div>
    </div>
  );
};

export default AgentGraphVisualizer;
