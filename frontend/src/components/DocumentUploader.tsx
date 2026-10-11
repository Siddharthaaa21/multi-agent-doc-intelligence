import React, { useRef } from 'react';
import { UploadCloud, FileText, AlertTriangle, Play, CheckCircle2 } from 'lucide-react';
import type { SampleDoc } from '../types';

interface DocumentUploaderProps {
  samples: SampleDoc[];
  selectedSampleId: string;
  onSelectSample: (id: string) => void;
  rawText: string;
  setRawText: (text: string) => void;
  filename: string;
  setFilename: (name: string) => void;
  injectTrap: boolean;
  setInjectTrap: (val: boolean) => void;
  onRunWorkflow: () => void;
  isRunning: boolean;
  onFileUpload: (file: File) => void;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  samples,
  selectedSampleId,
  onSelectSample,
  rawText,
  setRawText,
  filename,
  setFilename,
  injectTrap,
  setInjectTrap,
  onRunWorkflow,
  isRunning,
  onFileUpload,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center space-x-2">
            <FileText className="h-4 w-4 text-blue-400" />
            <span>Document Ingestion Source</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Select institutional sample filing or upload custom financial report (PDF, TXT, MD)
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Hidden File Input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".txt,.pdf,.md,.csv"
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium transition cursor-pointer"
          >
            <UploadCloud className="h-3.5 w-3.5 text-blue-400" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* Preset Samples Selector */}
      <div className="mt-4">
        <label className="text-[11px] font-mono uppercase text-slate-400 block mb-2">
          Benchmark Sample Documents (Instant 1-Click Load):
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {samples.map((doc) => {
            const isSelected = selectedSampleId === doc.id;
            return (
              <button
                key={doc.id}
                type="button"
                onClick={() => onSelectSample(doc.id)}
                className={`text-left p-3 rounded-lg border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-blue-950/60 border-blue-500 shadow-md shadow-blue-500/10'
                    : 'bg-slate-950/50 border-slate-800/80 hover:border-slate-700 hover:bg-slate-800/40'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {doc.doc_type.split(' ')[0]}
                  </span>
                  {isSelected && <CheckCircle2 className="h-3.5 w-3.5 text-blue-400" />}
                </div>
                <h4 className="text-xs font-semibold text-slate-100 mt-2 truncate">{doc.title}</h4>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">{doc.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Raw Text Preview Area */}
      <div className="mt-4">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-mono text-slate-400 flex items-center space-x-2">
            <span>FILE: <strong className="text-slate-200">{filename}</strong></span>
            <span>({rawText.length.toLocaleString()} characters)</span>
          </span>
          <span className="text-[11px] font-mono text-slate-500">Unstructured Text Buffer</span>
        </div>
        <textarea
          value={rawText}
          onChange={(e) => {
            setRawText(e.target.value);
            setFilename('custom_document.txt');
          }}
          rows={6}
          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-300 focus:outline-none focus:border-blue-500/80 resize-y leading-relaxed"
          placeholder="Paste or view raw financial document text here..."
        />
      </div>

      {/* Control Bar: Guardrail Adversarial Injection & Run Button */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Synthetic Trap Toggle */}
        <label className="flex items-center space-x-2.5 text-xs text-slate-300 cursor-pointer select-none bg-slate-950/60 px-3 py-2 rounded-lg border border-slate-800 hover:border-slate-700 transition">
          <input
            type="checkbox"
            checked={injectTrap}
            onChange={(e) => setInjectTrap(e.target.checked)}
            className="rounded border-slate-700 text-amber-500 focus:ring-0 bg-slate-900 cursor-pointer h-4 w-4"
          />
          <div className="flex items-center space-x-1.5">
            <AlertTriangle className={`h-3.5 w-3.5 ${injectTrap ? 'text-amber-400' : 'text-slate-500'}`} />
            <span>Adversarial Stress Test: <strong className={injectTrap ? 'text-amber-400' : 'text-slate-400'}>Inject Hallucination Trap</strong></span>
          </div>
        </label>

        {/* Action Button */}
        <button
          type="button"
          onClick={onRunWorkflow}
          disabled={isRunning || !rawText.trim()}
          className={`flex items-center space-x-2 px-5 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase shadow-lg transition-all cursor-pointer ${
            isRunning || !rawText.trim()
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-600/30'
          }`}
        >
          <Play className={`h-4 w-4 ${isRunning ? 'animate-spin' : ''}`} />
          <span>{isRunning ? 'Orchestrating Multi-Agent Graph...' : 'Execute LangGraph Workflow'}</span>
        </button>
      </div>
    </div>
  );
};
