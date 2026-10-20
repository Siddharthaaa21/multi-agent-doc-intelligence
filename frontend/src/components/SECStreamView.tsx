import React, { useState, useEffect } from 'react';
import { ArrowRight, Loader2, Search } from 'lucide-react';
import type { SECCompanySummary, SECFilingMetadata } from '../types';
import { fetchSECTickers, fetchSECFilings, ingestSECFiling, fetchSECWatchlist } from '../services/api';

interface SECStreamViewProps {
  onIngestSuccess: (jobId: string, ticker: string, form: string) => void;
  llmProvider: string;
}

export const SECStreamView: React.FC<SECStreamViewProps> = ({ onIngestSuccess, llmProvider }) => {
  const [ticker, setTicker] = useState<string>('AAPL');
  const [supportedTickers, setSupportedTickers] = useState<Array<{ ticker: string; cik: string }>>([]);
  const [companySummary, setCompanySummary] = useState<SECCompanySummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [ingestingAccession, setIngestingAccession] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearch = async (targetTicker: string) => {
    if (!targetTicker.trim()) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const summary = await fetchSECFilings(targetTicker.trim());
      setCompanySummary(summary);
      setTicker(targetTicker.toUpperCase());
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to fetch SEC EDGAR submissions');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    async function loadInitial() {
      try {
        const [tickersRes, , summary] = await Promise.all([
          fetchSECTickers(),
          fetchSECWatchlist(),
          fetchSECFilings('AAPL'),
        ]);
        setSupportedTickers(tickersRes);
        setCompanySummary(summary);
      } catch (err) {
        console.error('Failed to load initial SEC data:', err);
      }
    }
    loadInitial();
  }, []);

  const handleIngest = async (filing: SECFilingMetadata) => {
    setIngestingAccession(filing.accession_number);
    setErrorMessage(null);
    try {
      const res = await ingestSECFiling({
        ticker: companySummary?.ticker || ticker,
        cik: companySummary?.cik,
        form_type: filing.form,
        accession_number: filing.accession_number,
        primary_document: filing.primary_document,
        llm_provider: llmProvider,
      });
      if (res && res.job_id) {
        onIngestSuccess(res.job_id, companySummary?.ticker || ticker, filing.form);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to ingest filing from SEC EDGAR');
    } finally {
      setIngestingAccession(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Ticker Search & Filter Bar */}
      <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2 flex-wrap gap-y-2">
          <span className="text-xs font-medium text-zinc-400">Watchlist:</span>
          <div className="flex items-center space-x-1.5">
            {(supportedTickers.length > 0
              ? supportedTickers.map(t => t.ticker)
              : ['AAPL', 'NVDA', 'MSFT', 'AMZN', 'TSLA']
            ).slice(0, 6).map((t) => (
              <button
                key={t}
                onClick={() => handleSearch(t)}
                className={`px-2.5 py-1 rounded text-xs font-mono font-medium transition cursor-pointer ${
                  ticker === t
                    ? 'bg-zinc-100 text-zinc-950 font-bold'
                    : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative">
            <input
              type="text"
              placeholder="Ticker / CIK..."
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch(ticker)}
              className="bg-zinc-950 border border-zinc-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-zinc-700 w-36 uppercase"
            />
            <Search className="h-3.5 w-3.5 text-zinc-500 absolute left-2.5 top-2.5" />
          </div>
          <button
            onClick={() => handleSearch(ticker)}
            disabled={isLoading}
            className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg text-xs font-medium transition disabled:opacity-50 cursor-pointer"
          >
            {isLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : 'Fetch'}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300 font-mono">
          {errorMessage}
        </div>
      )}

      {/* Submissions Result View */}
      {companySummary && (
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-zinc-800/60 flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-semibold text-white">
                  {companySummary.company_name}
                </h3>
                <span className="text-xs font-mono text-zinc-400">
                  ({companySummary.ticker})
                </span>
                <span className="text-[11px] font-mono text-zinc-500">
                  CIK: {companySummary.cik}
                </span>
              </div>
            </div>
            <div className="text-[11px] font-mono text-zinc-500">
              SEC EDGAR Feed
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-zinc-950/60 text-zinc-400 border-b border-zinc-800/60 text-[11px]">
                <tr>
                  <th className="py-2.5 px-4 font-normal">Form</th>
                  <th className="py-2.5 px-4 font-normal">Filing Date</th>
                  <th className="py-2.5 px-4 font-normal">Period End</th>
                  <th className="py-2.5 px-4 font-normal">Document Accession</th>
                  <th className="py-2.5 px-4 font-normal text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/40 text-zinc-300">
                {companySummary.recent_filings.map((filing) => (
                  <tr key={filing.accession_number} className="hover:bg-zinc-800/20 transition-colors">
                    <td className="py-3 px-4 font-bold text-zinc-100">
                      {filing.form}
                    </td>
                    <td className="py-3 px-4 text-zinc-400">
                      {filing.filing_date}
                    </td>
                    <td className="py-3 px-4 text-zinc-500">
                      {filing.report_date || '—'}
                    </td>
                    <td className="py-3 px-4 text-zinc-500 font-mono text-[11px]">
                      {filing.accession_number}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleIngest(filing)}
                        disabled={ingestingAccession === filing.accession_number}
                        className="inline-flex items-center space-x-1.5 px-3 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition disabled:opacity-50 cursor-pointer"
                      >
                        {ingestingAccession === filing.accession_number ? (
                          <>
                            <Loader2 className="h-3 w-3 animate-spin" />
                            <span>Importing...</span>
                          </>
                        ) : (
                          <>
                            <span>Analyze in Workspace</span>
                            <ArrowRight className="h-3 w-3" />
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SECStreamView;
