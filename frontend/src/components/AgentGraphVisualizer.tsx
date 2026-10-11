import React from 'react';
import { Database, Tags, ShieldCheck, RefreshCw, FileText, ArrowRight, CheckCircle, Clock } from 'lucide-react';
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
  needsRefinement = false,
  iterations,
}) => {
  void needsRefinement;
  // Determine node states
  const hasIngested = trace.some(t => t.stage.includes('Ingestion'));
  const hasClassified = trace.some(t => t.stage.includes('Classification') || t.stage.includes('Taxonomy'));
  const hasGuardrails = trace.some(t => t.stage.includes('Guardrail') || t.stage.includes('Hallucination'));
  const hasRefined = trace.some(t => t.stage.includes('Refinement') || t.agent_name.includes('Correction'));
  const hasSynthesized = trace.some(t => t.stage.includes('Synthesis') || t.stage.includes('Briefing'));

  const isRunning = status === 'running' || status === 'queued';

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-blue-500 animate-ping"></span>
            <span>Live LangGraph Multi-Agent Topology & State Graph</span>
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Cyclic state machine featuring adversarial verification critic and self-correcting refinement loop
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {iterations > 1 && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-700/50 flex items-center space-x-1">
              <RefreshCw className="h-3 w-3 animate-spin" />
              <span>Self-Correction Cycle #{iterations}</span>
            </span>
          )}
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold ${
            status === 'completed'
              ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-700/50'
              : isRunning
              ? 'bg-blue-950/80 text-blue-300 border border-blue-700/50'
              : 'bg-slate-800 text-slate-400'
          }`}>
            Status: {status}
          </span>
        </div>
      </div>

      {/* Nodes Flow */}
      <div className="mt-5 grid grid-cols-1 md:grid-cols-5 gap-3 items-center">
        {/* Node 1: Ingestion */}
        <div className={`p-3 rounded-lg border transition-all ${
          hasIngested
            ? 'bg-slate-950/80 border-emerald-500/60 shadow-lg shadow-emerald-500/5'
            : isRunning
            ? 'bg-slate-950 border-blue-500 agent-node-active'
            : 'bg-slate-950/40 border-slate-800/80 opacity-60'
        }`}>
          <div className="flex items-center justify-between">
            <Database className="h-4 w-4 text-blue-400" />
            {hasIngested ? (
              <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <Clock className="h-3.5 w-3.5 text-slate-500" />
            )}
          </div>
          <h4 className="text-xs font-semibold text-slate-200 mt-2">1. Ingestion Agent</h4>
          <p className="text-[10px] text-slate-400 mt-0.5">Semantic chunking & tabular extraction</p>
        </div>

        {/* Node 2: Classification */}
        <div className={`p-3 rounded-lg border transition-all ${
          hasClassified
            ? 'bg-slate-950/80 border-emerald-500/60 shadow-lg shadow-emerald-500/5'
            : isRunning && hasIngested
            ? 'bg-slate-950 border-blue-500 agent-node-active'
            : 'bg-slate-950/40 border-slate-800/80 opacity-60'
        }`}>
          <div className="flex items-center justify-between">
            <Tags className="h-4 w-4 text-indigo-400" />
            {hasClassified ? (
              <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <Clock className="h-3.5 w-3.5 text-slate-500" />
            )}
          </div>
          <h4 className="text-xs font-semibold text-slate-200 mt-2">2. Classifier Agent</h4>
          <p className="text-[10px] text-slate-400 mt-0.5">Filing taxonomy & risk mapping</p>
        </div>

        {/* Node 3: Guardrails Verification Critic */}
        <div className={`p-3 rounded-lg border transition-all ${
          hasGuardrails
            ? hasRefined
              ? 'bg-slate-950/80 border-amber-500/80 shadow-lg shadow-amber-500/10'
              : 'bg-slate-950/80 border-emerald-500/60 shadow-lg shadow-emerald-500/5'
            : isRunning && hasClassified
            ? 'bg-slate-950 border-blue-500 agent-node-active'
            : 'bg-slate-950/40 border-slate-800/80 opacity-60'
        }`}>
          <div className="flex items-center justify-between">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            {hasGuardrails ? (
              <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <Clock className="h-3.5 w-3.5 text-slate-500" />
            )}
          </div>
          <h4 className="text-xs font-semibold text-slate-200 mt-2">3. Guardrail Critic</h4>
          <p className="text-[10px] text-slate-400 mt-0.5">Hallucination check & arithmetic audit</p>
        </div>

        {/* Node 4: Cyclic Refinement Loop (Conditional Edge) */}
        <div className={`p-3 rounded-lg border transition-all ${
          hasRefined
            ? 'bg-amber-950/40 border-amber-500 text-amber-200 shadow-md shadow-amber-500/10'
            : 'bg-slate-950/30 border-dashed border-slate-800 opacity-60'
        }`}>
          <div className="flex items-center justify-between">
            <RefreshCw className={`h-4 w-4 ${hasRefined ? 'text-amber-400 animate-spin' : 'text-slate-600'}`} />
            <span className="text-[9px] font-mono uppercase bg-slate-800 text-slate-400 px-1 py-0.5 rounded">
              Conditional Edge
            </span>
          </div>
          <h4 className="text-xs font-semibold text-slate-200 mt-2">4. LangGraph Cycle</h4>
          <p className="text-[10px] text-slate-400 mt-0.5">Self-healing state refinement</p>
        </div>

        {/* Node 5: Executive Synthesis */}
        <div className={`p-3 rounded-lg border transition-all ${
          hasSynthesized
            ? 'bg-slate-950/80 border-purple-500/80 shadow-lg shadow-purple-500/5'
            : isRunning && hasGuardrails
            ? 'bg-slate-950 border-purple-500 agent-node-active'
            : 'bg-slate-950/40 border-slate-800/80 opacity-60'
        }`}>
          <div className="flex items-center justify-between">
            <FileText className="h-4 w-4 text-purple-400" />
            {hasSynthesized ? (
              <CheckCircle className="h-3.5 w-3.5 text-purple-400" />
            ) : (
              <Clock className="h-3.5 w-3.5 text-slate-500" />
            )}
          </div>
          <h4 className="text-xs font-semibold text-slate-200 mt-2">5. Synthesis Agent</h4>
          <p className="text-[10px] text-slate-400 mt-0.5">Executive memo & committee brief</p>
        </div>
      </div>

      {/* Latest Agent Activity Trace Banner */}
      {trace.length > 0 && (
        <div className="mt-4 p-3 bg-slate-950 border border-slate-800/80 rounded-lg flex items-start space-x-3">
          <div className="p-1 rounded bg-blue-900/40 text-blue-400 mt-0.5">
            <ArrowRight className="h-3.5 w-3.5" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200">
                {trace[trace.length - 1].agent_name}
              </span>
              <span className="text-[10px] font-mono text-slate-500">
                Latency: {trace[trace.length - 1].latency_ms}ms | Tokens: {trace[trace.length - 1].tokens_used}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono leading-relaxed">
              {trace[trace.length - 1].thought_process}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
