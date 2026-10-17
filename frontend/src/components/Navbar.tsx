import React from 'react';
import { ShieldCheck, Cpu, Activity, FileSpreadsheet, Terminal, Globe } from 'lucide-react';

interface NavbarProps {
  activeTab: 'workspace' | 'sec' | 'guardrails' | 'benchmark' | 'trace';
  setActiveTab: (tab: 'workspace' | 'sec' | 'guardrails' | 'benchmark' | 'trace') => void;
  llmProvider: string;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, llmProvider }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-slate-900 border border-slate-700/80 flex items-center justify-center text-blue-400">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white tracking-wide text-base">STRATA // DOC ORCHESTRATOR</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-900/50 text-blue-300 border border-blue-700/50">
                LangGraph v0.2
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Multi-Agent Financial Document Intelligence & Guardrail Engine</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab('workspace')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'workspace'
                ? 'bg-blue-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FileSpreadsheet className="h-3.5 w-3.5" />
            <span>Analyst Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab('sec')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'sec'
                ? 'bg-cyan-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Globe className="h-3.5 w-3.5" />
            <span>SEC EDGAR Stream</span>
          </button>

          <button
            onClick={() => setActiveTab('guardrails')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'guardrails'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Guardrails Studio</span>
            <span className="text-[10px] font-mono bg-emerald-950/80 text-emerald-300 px-1.5 py-0.2 rounded border border-emerald-700/40">
              99.2%
            </span>
          </button>

          <button
            onClick={() => setActiveTab('benchmark')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'benchmark'
                ? 'bg-purple-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            <span>Regression Pipeline</span>
          </button>

          <button
            onClick={() => setActiveTab('trace')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'trace'
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Terminal className="h-3.5 w-3.5" />
            <span>State Inspector</span>
          </button>
        </nav>

        {/* Status Indicators */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md text-slate-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-mono text-[11px]">Engine:</span>
            <span className="font-semibold text-blue-400 capitalize">{llmProvider}</span>
          </div>

          <div className="hidden md:flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md text-slate-300">
            <span className="font-mono text-[11px] text-slate-400">Turnaround:</span>
            <span className="font-semibold text-emerald-400">-60% Latency</span>
          </div>
        </div>
      </div>
    </header>
  );
};
