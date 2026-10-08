import { useEffect, useState } from 'react';
import {
  Activity,
  BarChart3,
  Bot,
  CircleDollarSign,
  ShieldCheck,
  AlertTriangle,
} from 'lucide-react';

import { Dashboard } from './pages/Dashboard';
import { AgentTimeline } from './components/AgentTimeline';
import { CommandBar } from './components/CommandBar';
import { MetricCard } from './components/MetricCard';
import { StatusPill } from './components/StatusPill';
import { StudioPanel } from './components/StudioPanel';
import { TransactionGrid } from './components/TransactionGrid';
import { api } from './services/api';
import type { Summary, Transaction } from './types';
import { PayPalScriptProvider } from '@paypal/react-paypal-js';

type Tab = 'command' | 'risk' | 'agents' | 'ledger' | 'analytics';

type SectionViewProps = {
  tab: Exclude<Tab, 'command'>;
};

function SectionView({ tab }: SectionViewProps) {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [rows, setRows] = useState<Transaction[]>([]);
  const [busy, setBusy] = useState(false);
  const [failureResult, setFailureResult] = useState<any | null>(null);
  const [queryResult, setQueryResult] = useState<any | null>(null);

  const refresh = async () => {
    const [summaryData, transactionData] = await Promise.all([
      api.summary(),
      api.transactions(),
    ]);

    setSummary(summaryData);
    setRows(transactionData);
  };

  useEffect(() => {
    refresh().catch((error) => {
      console.error('PayPilot refresh failed:', error);
    });
  }, []);

  const runFailure = async (
    scenario: 'budget_exceeded' | 'verification_failed',
  ) => {
    setBusy(true);

    try {
      const result = await api.failure(scenario);
      setFailureResult(result);
      await refresh();
    } catch (error) {
      console.error('Failure demo failed:', error);
      setFailureResult({
        status: 'ERROR',
        message: 'Failure scenario could not be completed.',
      });
    } finally {
      setBusy(false);
    }
  };

  if (tab === 'risk') {
    return (
      <div className="space-y-6">
        <div>
          <div className="text-xs uppercase tracking-[.2em] text-sky-300">
            Risk Center
          </div>
          <h1 className="mt-2 text-3xl font-semibold text-white">
            Financial guardrails
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Reproduce controlled failure scenarios and inspect risk decisions.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <button
            disabled={busy}
            onClick={() => runFailure('budget_exceeded')}
            className="rounded-2xl border border-line bg-panel/80 p-5 text-left hover:bg-white/5 disabled:opacity-50"
          >
            <AlertTriangle className="h-5 w-5 text-amber-300" />
            <div className="mt-3 font-semibold text-white">
              Budget exceeded
            </div>
            <div className="mt-1 text-xs text-slate-500">
              Verify that the payment is blocked when the budget policy fails.
            </div>
          </button>

          <button
            disabled={busy}
            onClick={() => runFailure('verification_failed')}
            className="rounded-2xl border border-line bg-panel/80 p-5 text-left hover:bg-white/5 disabled:opacity-50"
          >
            <ShieldCheck className="h-5 w-5 text-red-300" />
            <div className="mt-3 font-semibold text-white">
              Verification failed
            </div>
            <div className="mt-1 text-xs text-slate-500">
              Verify that payment remains unreleased after failed verification.
            </div>
          </button>
        </div>

        {failureResult && (
          <div className="rounded-2xl border border-line bg-panel/80 p-5">
            <pre className="overflow-auto text-xs text-slate-300">
              {JSON.stringify(failureResult, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  }

  if (tab === 'agents') {
    return (
      <div className="space-y-6">
        <div>
          <div className="text-xs uppercase tracking-[.2em] text-sky-300">
            Agents
          </div>
          <h1 className="mt-2 text-3xl font-semibold text-white">
            Agent orchestration
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Autonomous discovery, negotiation, verification and payment flow.
          </p>
        </div>

        <div className="rounded-2xl border border-line bg-panel/80 p-5">
          <AgentTimeline />
        </div>
      </div>
    );
  }

  if (tab === 'ledger') {
    return (
      <div className="space-y-6">
        <div>
          <div className="text-xs uppercase tracking-[.2em] text-sky-300">
            Ledger
          </div>
          <h1 className="mt-2 text-3xl font-semibold text-white">
            Transaction intelligence
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Inspect agent-managed payment records and transaction outcomes.
          </p>
        </div>

        <div className="rounded-2xl border border-line bg-panel/80 p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-white">Payment ledger</h2>
              <p className="mt-1 text-xs text-slate-500">
                Live records from the PayPilot API.
              </p>
            </div>
            <StatusPill value="AG Grid" tone="good" />
          </div>

          <TransactionGrid rows={rows} />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="text-xs uppercase tracking-[.2em] text-sky-300">
          Analytics
        </div>
        <h1 className="mt-2 text-3xl font-semibold text-white">
          Transaction analytics
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Ask the analytics agent questions about PayPilot transaction data.
        </p>
      </div>

      <CommandBar
        onRun={async (query) => {
          try {
            setQueryResult(await api.analytics(query));
          } catch (error) {
            console.error('Analytics query failed:', error);
            setQueryResult({
              title: 'Analytics error',
              explanation: 'Unable to query analytics right now.',
              rows: [],
            });
          }
        }}
      />

      {queryResult && (
        <div className="rounded-2xl border border-line bg-panel/80 p-5">
          <div className="text-xs uppercase tracking-[.18em] text-slate-500">
            Analytics Agent
          </div>

          <h2 className="mt-2 font-semibold text-white">
            {queryResult.title}
          </h2>

          <p className="mt-1 text-sm leading-6 text-slate-400">
            {queryResult.explanation}
          </p>

          <pre className="mt-4 max-h-72 overflow-auto rounded-xl bg-ink p-4 text-xs text-slate-300">
            {JSON.stringify(queryResult.rows, null, 2)}
          </pre>
        </div>
      )}

      <StudioPanel transactions={rows} />
    </div>
  );
}

export default function App() {
  const tabs: Array<[Tab, string, typeof Activity]> = [
    ['command', 'Command Center', Activity],
    ['risk', 'Risk Center', ShieldCheck],
    ['agents', 'Agents', Bot],
    ['ledger', 'Ledger', CircleDollarSign],
    ['analytics', 'Analytics', BarChart3],
  ];

  const [tab, setTab] = useState<Tab>('command');

  useEffect(() => {
    const path = window.location.pathname;
    if (path !== '/paypal/success') return;
  }, []);

  return (
    <PayPalScriptProvider
      options={{
        clientId: import.meta.env.VITE_PAYPAL_CLIENT_ID,
        currency: 'USD',
        intent: 'authorize',
      }}
    >
      <div className="min-h-screen bg-ink text-slate-200">
        <header className="sticky top-0 z-20 border-b border-line bg-ink/90 backdrop-blur-xl">
          <div className="mx-auto flex max-w-[1500px] items-center justify-between px-5 py-4 lg:px-8">
            <div className="flex items-center gap-3">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-white font-black text-ink">
                P
              </div>

              <div>
                <div className="font-semibold text-white">PAYPILOT</div>
                <div className="text-[10px] uppercase tracking-[.25em] text-slate-500">
                  Autonomous Commerce
                </div>
              </div>
            </div>

            <div className="hidden rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-300 sm:block">
              Demo mode · PayPal integration ready
            </div>
          </div>
        </header>

        <div className="mx-auto flex max-w-[1500px] gap-8 px-5 lg:px-8">
          <aside className="hidden w-52 shrink-0 py-6 md:block">
            <nav className="space-y-1">
              {tabs.map(([id, label, Icon]) => (
                <button
                  key={id}
                  onClick={() => setTab(id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm ${
                    tab === id
                      ? 'bg-white text-ink'
                      : 'text-slate-400 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </button>
              ))}
            </nav>

            <div className="mt-10 rounded-2xl border border-line bg-panel/70 p-4">
              <div className="text-xs font-semibold text-white">
                Policy-first autonomy
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-500">
                AI recommends. The backend authorizes. PayPal moves the money.
              </p>
            </div>
          </aside>

          <main className="min-w-0 flex-1 py-6 lg:py-8">
            {tab === 'command' ? (
              <Dashboard />
            ) : (
              <SectionView tab={tab} />
            )}
          </main>
        </div>
      </div>
    </PayPalScriptProvider>
  );
}
