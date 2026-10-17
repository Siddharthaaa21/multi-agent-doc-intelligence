import React, { useState, useEffect } from 'react';
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
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [recentIngestions, setRecentIngestions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [ingestingAccession, setIngestingAccession] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load supported tickers and watchlist on mount
  useEffect(() => {
    async function loadInitial() {
      try {
        const [tickersRes, watchRes] = await Promise.all([
          fetchSECTickers(),
          fetchSECWatchlist()
        ]);
        setSupportedTickers(tickersRes);
        setWatchlist(watchRes.watchlist || []);
        setRecentIngestions(watchRes.recent_ingestions || []);
      } catch (err) {
        console.error('Failed to load initial SEC data:', err);
      }
    }
    loadInitial();
    handleSearch('AAPL');
  }, []);

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
        llm_provider: llmProvider
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Banner / Compliance Protocol */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 18px',
          background: 'var(--color-bg-card, #131722)',
          border: '1px solid var(--color-border, #2a2e39)',
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
          <span style={{ fontWeight: 600, color: 'var(--color-text-primary, #e1e7ec)' }}>
            SEC EDGAR SUBMISSION INGESTION PIPELINE
          </span>
          <span style={{ color: 'var(--color-text-secondary, #787b86)' }}>|</span>
          <span style={{ color: 'var(--color-text-secondary, #787b86)' }}>
            data.sec.gov API Protocol v1.0
          </span>
        </div>
        <div style={{ display: 'flex', gap: '16px', color: 'var(--color-text-secondary, #787b86)' }}>
          <span>WATCHLIST: <strong>{watchlist.length > 0 ? watchlist.length : 6} ENTITIES</strong></span>
          <span>RATE LIMIT: <strong>10 req/s</strong></span>
          <span>FORMAT: <strong>iXBRL & HTML Tables</strong></span>
          <span>STATUS: <strong style={{ color: '#10b981' }}>ONLINE</strong></span>
        </div>
      </div>

      {/* Ticker Search & Institutional Watchlist Bar */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
          padding: '18px',
          background: 'var(--color-bg-card, #131722)',
          border: '1px solid var(--color-border, #2a2e39)',
          borderRadius: '4px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary, #e1e7ec)' }}>
            MONITORED TICKERS:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {(supportedTickers.length > 0
              ? supportedTickers.map(t => t.ticker)
              : ['AAPL', 'NVDA', 'MSFT', 'AMZN', 'TSLA', 'JPM']
            ).slice(0, 8).map((t) => (
              <button
                key={t}
                onClick={() => handleSearch(t)}
                style={{
                  padding: '5px 12px',
                  background: ticker === t ? '#2563eb' : '#1e222d',
                  color: ticker === t ? '#ffffff' : '#d1d5db',
                  border: '1px solid #2a2e39',
                  borderRadius: '3px',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                  cursor: 'pointer',
                  fontWeight: 600,
                }}
              >
                {t}
              </button>
            ))}
          </div>

          <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
            <input
              type="text"
              placeholder="Search ticker or CIK..."
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch(ticker)}
              style={{
                padding: '6px 12px',
                background: '#0a0d14',
                border: '1px solid #2a2e39',
                borderRadius: '3px',
                color: '#e1e7ec',
                fontFamily: 'monospace',
                fontSize: '12px',
                width: '180px',
              }}
            />
            <button
              onClick={() => handleSearch(ticker)}
              disabled={isLoading}
              style={{
                padding: '6px 14px',
                background: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '3px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: isLoading ? 'not-allowed' : 'pointer',
              }}
            >
              {isLoading ? 'Querying...' : 'Query EDGAR'}
            </button>
          </div>
        </div>

        {errorMessage && (
          <div
            style={{
              padding: '10px 14px',
              background: '#3f1515',
              border: '1px solid #ef4444',
              color: '#fca5a5',
              fontSize: '12px',
              fontFamily: 'monospace',
              borderRadius: '3px',
            }}
          >
            {errorMessage}
          </div>
        )}
      </div>

      {/* Submissions Result View */}
      {companySummary && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            padding: '20px',
            background: 'var(--color-bg-card, #131722)',
            border: '1px solid var(--color-border, #2a2e39)',
            borderRadius: '4px',
          }}
        >
          {/* Header Info */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #2a2e39', paddingBottom: '14px' }}>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#f3f4f6', letterSpacing: '-0.01em' }}>
                {companySummary.company_name}
              </div>
              <div style={{ display: 'flex', gap: '16px', marginTop: '6px', fontSize: '12px', fontFamily: 'monospace', color: '#9ca3af' }}>
                <span>TICKER: <strong style={{ color: '#e5e7eb' }}>{companySummary.ticker}</strong></span>
                <span>CIK: <strong style={{ color: '#e5e7eb' }}>{companySummary.cik}</strong></span>
                {companySummary.sic && <span>SIC: <strong style={{ color: '#e5e7eb' }}>{companySummary.sic}</strong></span>}
                {companySummary.fiscal_year_end && <span>FY END: <strong style={{ color: '#e5e7eb' }}>{companySummary.fiscal_year_end}</strong></span>}
              </div>
            </div>
            <div style={{ fontSize: '12px', color: '#9ca3af', textAlign: 'right', fontFamily: 'monospace' }}>
              OFFICIAL SEC ARCHIVES DISCOVERY
            </div>
          </div>

          {/* Filings Table */}
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#e5e7eb', marginBottom: '10px' }}>
              AVAILABLE STATUTORY PERIODIC FILINGS (10-K, 10-Q, 8-K)
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left', fontFamily: 'monospace' }}>
                <thead>
                  <tr style={{ background: '#0d1017', borderBottom: '1px solid #2a2e39', color: '#9ca3af' }}>
                    <th style={{ padding: '8px 12px' }}>FORM</th>
                    <th style={{ padding: '8px 12px' }}>FILING DATE</th>
                    <th style={{ padding: '8px 12px' }}>PERIOD END</th>
                    <th style={{ padding: '8px 12px' }}>ACCESSION NUMBER</th>
                    <th style={{ padding: '8px 12px' }}>PRIMARY DOCUMENT</th>
                    <th style={{ padding: '8px 12px', textAlign: 'right' }}>ACTION</th>
                  </tr>
                </thead>
                <tbody>
                  {companySummary.recent_filings.map((f, idx) => {
                    const isIngesting = ingestingAccession === f.accession_number;
                    const isForm10K = f.form === '10-K';
                    const isForm10Q = f.form === '10-Q';
                    return (
                      <tr
                        key={idx}
                        style={{
                          borderBottom: '1px solid #1e222d',
                          background: idx % 2 === 0 ? 'transparent' : '#0d101780',
                        }}
                      >
                        <td style={{ padding: '10px 12px' }}>
                          <span
                            style={{
                              padding: '2px 6px',
                              borderRadius: '2px',
                              fontWeight: 700,
                              fontSize: '11px',
                              background: isForm10K ? '#064e3b' : isForm10Q ? '#1e3a8a' : '#1f2937',
                              color: isForm10K ? '#6ee7b7' : isForm10Q ? '#93c5fd' : '#d1d5db',
                            }}
                          >
                            {f.form}
                          </span>
                        </td>
                        <td style={{ padding: '10px 12px', color: '#e5e7eb' }}>{f.filing_date || '—'}</td>
                        <td style={{ padding: '10px 12px', color: '#9ca3af' }}>{f.report_date || '—'}</td>
                        <td style={{ padding: '10px 12px', color: '#9ca3af' }}>{f.accession_number}</td>
                        <td style={{ padding: '10px 12px' }}>
                          {f.document_url ? (
                            <a
                              href={f.document_url}
                              target="_blank"
                              rel="noreferrer"
                              style={{ color: '#60a5fa', textDecoration: 'none' }}
                            >
                              {f.primary_document || 'View Doc'} ↗
                            </a>
                          ) : (
                            <span>{f.primary_document || '—'}</span>
                          )}
                        </td>
                        <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                          <button
                            onClick={() => handleIngest(f)}
                            disabled={Boolean(ingestingAccession)}
                            style={{
                              padding: '5px 12px',
                              background: isForm10K || isForm10Q ? '#059669' : '#374151',
                              color: '#ffffff',
                              border: 'none',
                              borderRadius: '3px',
                              fontSize: '11px',
                              fontWeight: 600,
                              cursor: ingestingAccession ? 'not-allowed' : 'pointer',
                            }}
                          >
                            {isIngesting ? 'Ingesting...' : 'Ingest & Orchestrate'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Recently Ingested Stream History */}
      {recentIngestions.length > 0 && (
        <div
          style={{
            padding: '18px',
            background: 'var(--color-bg-card, #131722)',
            border: '1px solid var(--color-border, #2a2e39)',
            borderRadius: '4px',
          }}
        >
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#e5e7eb', marginBottom: '12px' }}>
            RECENT INSTITUTIONAL EDGAR INGESTION AUDIT LOG
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {recentIngestions.map((item, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 12px',
                  background: '#0d1017',
                  border: '1px solid #1e222d',
                  borderRadius: '3px',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                }}
              >
                <div>
                  <strong style={{ color: '#60a5fa' }}>{item.ticker}</strong> ({item.form}) — {item.company_name}
                  <span style={{ color: '#6b7280', marginLeft: '10px' }}>Accession: {item.accession_number}</span>
                </div>
                <div style={{ display: 'flex', gap: '16px', color: '#9ca3af' }}>
                  <span>Tables: {item.tables_extracted}</span>
                  <span style={{ color: '#10b981' }}>Status: {item.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
