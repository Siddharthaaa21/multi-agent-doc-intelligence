import React from 'react';
import { FileText, Globe, ShieldCheck } from 'lucide-react';

interface NavbarProps {
  activeTab: 'workspace' | 'sec' | 'audit';
  setActiveTab: (tab: 'workspace' | 'sec' | 'audit') => void;
  llmProvider: string;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, llmProvider }) => {
  return (
    <header className="border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur-sm sticky top-0 z-50 px-6 py-3">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-2.5">
          <span className="font-semibold text-white tracking-tight text-sm">STRATA</span>
          <span className="text-zinc-600 text-xs">/</span>
          <span className="text-xs text-zinc-400 font-normal">Document Intelligence</span>
        </div>

        {/* Calm Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-zinc-900/60 p-1 rounded-lg border border-zinc-800/60">
          <button
            onClick={() => setActiveTab('workspace')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'workspace'
                ? 'bg-zinc-800 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab('sec')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'sec'
                ? 'bg-zinc-800 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Globe className="h-3.5 w-3.5" />
            <span>SEC EDGAR</span>
          </button>

          <button
            onClick={() => setActiveTab('audit')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'audit'
                ? 'bg-zinc-800 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Audit & Metrics</span>
          </button>
        </nav>

        {/* Quiet Status */}
        <div className="flex items-center space-x-2 text-xs text-zinc-500 font-mono">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          <span className="capitalize">{llmProvider}</span>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
