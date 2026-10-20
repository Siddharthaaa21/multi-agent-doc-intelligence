import React, { useState, useRef } from 'react';
import { UploadCloud, ChevronDown, ChevronUp, Play, Loader2 } from 'lucide-react';
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
  const [showSourceText, setShowSourceText] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-4 space-y-3">
      {/* Primary Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Document Selector */}
        <div className="flex items-center space-x-2 flex-1 max-w-lg">
          <label className="text-xs text-zinc-400 font-medium whitespace-nowrap">Document:</label>
          <select
            value={selectedSampleId}
            onChange={(e) => onSelectSample(e.target.value)}
            className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-700 w-full"
          >
            {samples.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.title} ({doc.doc_type.split(' ')[0]})
              </option>
            ))}
            {selectedSampleId === '' && (
              <option value="">Custom Upload: {filename}</option>
            )}
          </select>

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
            className="p-1.5 rounded-lg border border-zinc-800 hover:border-zinc-700 bg-zinc-950 text-zinc-400 hover:text-zinc-200 transition shrink-0"
            title="Upload custom filing (PDF, TXT)"
          >
            <UploadCloud className="h-4 w-4" />
          </button>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3 shrink-0">
          <label className="flex items-center space-x-1.5 text-xs text-zinc-400 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={injectTrap}
              onChange={(e) => setInjectTrap(e.target.checked)}
              className="rounded border-zinc-700 text-amber-500 bg-zinc-950 h-3.5 w-3.5 focus:ring-0"
            />
            <span className="text-[11px]">Inject Trap</span>
          </label>

          <button
            type="button"
            onClick={onRunWorkflow}
            disabled={isRunning || !rawText.trim()}
            className={`flex items-center space-x-1.5 px-4 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
              isRunning || !rawText.trim()
                ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                : 'bg-zinc-100 hover:bg-white text-zinc-950 font-semibold shadow-sm'
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="h-3 w-3 fill-current" />
                <span>Analyze Document</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Subdued Collapsible Source Text Disclosure */}
      <div className="pt-2 border-t border-zinc-800/50 flex items-center justify-between text-[11px] text-zinc-500">
        <span className="font-mono">
          {filename} • {(rawText.length / 1000).toFixed(1)}k chars
        </span>
        <button
          type="button"
          onClick={() => setShowSourceText(!showSourceText)}
          className="flex items-center space-x-1 text-zinc-400 hover:text-zinc-200 transition"
        >
          <span>{showSourceText ? 'Hide Source' : 'View Source Text'}</span>
          {showSourceText ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </button>
      </div>

      {showSourceText && (
        <textarea
          value={rawText}
          onChange={(e) => {
            setRawText(e.target.value);
            setFilename('custom_document.txt');
          }}
          rows={6}
          className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-300 focus:outline-none focus:border-zinc-700 resize-y leading-relaxed"
          placeholder="Paste or inspect source text..."
        />
      )}
    </div>
  );
};
