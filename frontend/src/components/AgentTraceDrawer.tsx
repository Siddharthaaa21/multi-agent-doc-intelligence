import React, { useState } from 'react';
import { Terminal, Clock, Cpu, ChevronDown, ChevronRight, Code } from 'lucide-react';
import type { AgentTraceEvent, OrchestratorStateResponse } from '../types';

interface AgentTraceDrawerProps {
  trace: AgentTraceEvent[];
  currentState?: OrchestratorStateResponse;
}

export const AgentTraceDrawer: React.FC<AgentTraceDrawerProps> = ({ trace, currentState }) => {
  const [showJsonState, setShowJsonState] = useState(false);
  const [expandedTraceIdx, setExpandedTraceIdx] = useState<number | null>(null);

  const toggleTraceItem = (idx: number) => {
    setExpandedTraceIdx(expandedTraceIdx === idx ? null : idx);
  };

  return (
    <div className="space-y-5">
      {/* Top Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <Terminal className="h-5 w-5 text-indigo-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              LangGraph State & Multi-Agent Execution Trace Inspector
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Complete step-by-step audit trail: agent reasoning, latency benchmarks, and state graph transitions
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowJsonState(!showJsonState)}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-mono transition cursor-pointer"
        >
          <Code className="h-3.5 w-3.5 text-indigo-400" />
          <span>{showJsonState ? 'Hide Raw Graph State' : 'Inspect Raw Graph State'}</span>
        </button>
      </div>

      {/* Raw JSON State Modal/View */}
      {showJsonState && currentState && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-2xl">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
            <span className="text-xs font-mono text-indigo-400 font-semibold">DocumentState (TypedDict):</span>
            <span className="text-[10px] font-mono text-slate-500">Job ID: {currentState.job_id}</span>
          </div>
          <pre className="text-[11px] font-mono text-slate-300 overflow-x-auto max-h-96 p-3 bg-slate-900/60 rounded-lg">
            {JSON.stringify(currentState, null, 2)}
          </pre>
        </div>
      )}

      {/* Step by step timeline */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-xl">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center space-x-2">
          <span>Agent Trajectory Timeline ({trace.length} Events)</span>
        </h3>

        {trace.length === 0 ? (
          <p className="text-xs text-slate-500 py-6 text-center font-mono">No execution events recorded yet.</p>
        ) : (
          <div className="space-y-3 font-mono">
            {trace.map((event, idx) => {
              const isExpanded = expandedTraceIdx === idx;
              const isCycle = event.stage.includes('Refinement') || event.agent_name.includes('Correction');

              return (
                <div
                  key={idx}
                  className={`border rounded-lg transition-all ${
                    isCycle
                      ? 'bg-amber-950/20 border-amber-800/60'
                      : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div
                    onClick={() => toggleTraceItem(idx)}
                    className="p-3.5 flex items-center justify-between cursor-pointer select-none"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="h-6 w-6 rounded-full bg-slate-800 text-slate-300 text-xs flex items-center justify-center font-bold">
                        {idx + 1}
                      </span>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-white font-sans">{event.agent_name}</span>
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                            {event.stage}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-500 mt-0.5 block">{event.timestamp}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 text-xs">
                      <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                        <Clock className="h-3 w-3 text-slate-500" />
                        <span>{event.latency_ms}ms</span>
                      </span>
                      <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                        <Cpu className="h-3 w-3 text-slate-500" />
                        <span>{event.tokens_used} tokens</span>
                      </span>
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-slate-400" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-slate-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Thought Details */}
                  {isExpanded && (
                    <div className="px-4 pb-4 pt-1 border-t border-slate-800/60 text-xs text-slate-300 leading-relaxed font-sans">
                      <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                        Agent Chain-of-Thought & Execution Audit:
                      </span>
                      <p className="bg-slate-900/90 p-3 rounded border border-slate-800 font-mono text-[11px] text-slate-300">
                        {event.thought_process}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
