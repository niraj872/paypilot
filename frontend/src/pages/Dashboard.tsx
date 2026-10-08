import { useEffect, useState } from 'react';
import { AlertTriangle, Bot, CheckCircle2, CircleDollarSign, ShieldCheck, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import type { Summary, Transaction, WorkflowResult } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusPill } from '../components/StatusPill';
import { AgentTimeline } from '../components/AgentTimeline';
import { CommandBar } from '../components/CommandBar';
import { TransactionGrid } from '../components/TransactionGrid';
import { StudioPanel } from '../components/StudioPanel';
import { PayPalButton } from '../components/PayPalButton';

const defaultTask = {
  title: 'Fix React Authentication Bug',
  description: 'Fix the React authentication bug and deliver a tested patch within the agreed deadline.',
  budget_max: 100,
  deadline_hours: 24,
  payment_condition: 'release_after_verification',
  quality_requirement: 'tests_pass',
};

export function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [rows, setRows] = useState<Transaction[]>([]);
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [queryResult, setQueryResult] = useState<any | null>(null);
  const [paymentTaskId, setPaymentTaskId] = useState<number | null>(null);
  const refresh = async () => { setSummary(await api.summary()); setRows(await api.transactions()); };
  useEffect(()=>{ refresh().catch(()=>undefined); },[]);

  const runAutonomousDemo = async () => {
    setBusy(true);
    try {
      const task = await api.createTask(defaultTask);
      const workflow = await api.runTask(task.id);
      setResult(workflow);
      setPaymentTaskId(task.id);
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const runFailure = async (scenario: 'budget_exceeded' | 'verification_failed') => {
    setBusy(true); try { const res = await api.failure(scenario); setResult({ task_id: res.task_id, status: res.status, selected_offer_id: null, selected_seller: null, negotiated_price: null, risk_score: res.risk_score, risk_level: res.risk_level, payment_status: res.status.includes('PAYMENT') ? 'BLOCKED' : 'NOT_RELEASED', verification_score: null, verification_status: res.verification_status, message: 'Reproducible failure scenario completed' }); await refresh(); } finally { setBusy(false); }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div><div className="mb-2 inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs text-sky-300"><Sparkles className="h-3.5 w-3.5"/> Agent-native commerce</div><h1 className="text-4xl font-semibold tracking-tight text-white">Autonomous Commerce<br/><span className="text-slate-500">with financial guardrails.</span></h1><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">Tell PayPilot what needs to be done. Agents discover, negotiate, verify and orchestrate payment while the backend keeps financial authority under your rules.</p></div>
        <div className="flex gap-2"><button disabled={busy} onClick={runAutonomousDemo} className="rounded-xl bg-white px-5 py-3 text-sm font-semibold text-ink disabled:opacity-50">{busy ? 'Running agents…' : 'Run autonomous demo'}</button></div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <MetricCard label="Managed value" value={`$${summary?.total_value.toLocaleString() ?? '0'}`} hint="PayPal task value" icon={<CircleDollarSign className="h-4 w-4"/>}/>
        <MetricCard label="Transactions" value={summary?.transactions ?? 0} hint="Ledger records" icon={<CheckCircle2 className="h-4 w-4"/>}/>
        <MetricCard label="Average risk" value={`${summary?.avg_risk ?? 0}`} hint="0 = safer" icon={<ShieldCheck className="h-4 w-4"/>}/>
        <MetricCard label="Verification" value={`${summary?.verification_rate ?? 0}%`} hint="Passed fulfillment" icon={<CheckCircle2 className="h-4 w-4"/>}/>
        <MetricCard label="High risk" value={summary?.high_risk ?? 0} hint="Needs attention" icon={<AlertTriangle className="h-4 w-4"/>}/>
        <MetricCard label="Agents" value="5" hint="Buyer • Seller • Risk • Verify • Orchestrator" icon={<Bot className="h-4 w-4"/>}/>
      </div>

      {result && <div className="rounded-2xl border border-sky-400/20 bg-sky-400/5 p-5"><div className="flex flex-wrap items-center justify-between gap-4"><div><div className="text-xs uppercase tracking-[.2em] text-sky-300">Latest workflow</div><div className="mt-1 text-xl font-semibold text-white">{result.status.replaceAll('_',' ')}</div><div className="mt-1 text-sm text-slate-400">Seller: {result.selected_seller ?? 'policy scenario'} · Amount: {result.negotiated_price ? `$${result.negotiated_price}` : '—'}</div></div><div className="flex gap-2"><StatusPill value={result.risk_level ? `${result.risk_level} risk` : 'Policy event'} tone={result.risk_level==='HIGH' ? 'bad' : 'good'}/><StatusPill value={result.verification_status ?? 'verification pending'} tone={result.verification_status==='FAILED' ? 'bad' : 'good'}/></div></div></div>}

      <div className="grid gap-6 xl:grid-cols-[1.15fr_.85fr]">
        <div className="space-y-6">
          <AgentTimeline result={result} />
          <div className="rounded-2xl border border-line bg-panel/80 p-5"><div className="mb-4 flex items-center justify-between"><div><h3 className="font-semibold text-white">Transaction Intelligence</h3><p className="mt-1 text-xs text-slate-500">Filter, sort, inspect and investigate agent-managed payments.</p></div><StatusPill value="AG Grid" tone="good"/></div><TransactionGrid rows={rows}/></div>
        </div>
        <div className="space-y-6">
          <div><CommandBar onRun={async q=>{ const r=await api.analytics(q); setQueryResult(r); }}/>{queryResult && <div className="mt-3 rounded-2xl border border-line bg-panel/80 p-4"><div className="text-xs uppercase tracking-[.18em] text-slate-500">Analytics Agent</div><h4 className="mt-2 font-semibold text-white">{queryResult.title}</h4><p className="mt-1 text-xs leading-5 text-slate-400">{queryResult.explanation}</p><pre className="mt-4 max-h-56 overflow-auto rounded-xl bg-ink p-3 text-xs text-slate-300">{JSON.stringify(queryResult.rows, null, 2)}</pre></div>}</div>
          <div className="rounded-2xl border border-line bg-panel/80 p-5"><div className="mb-4"><h3 className="font-semibold text-white">Reproducible failure cases</h3><p className="mt-1 text-xs text-slate-500">Show judges that autonomy never bypasses controls.</p></div><div className="grid gap-3 sm:grid-cols-2"><button onClick={()=>runFailure('budget_exceeded')} disabled={busy} className="rounded-xl border border-rose-400/20 bg-rose-400/5 p-4 text-left hover:bg-rose-400/10"><div className="text-sm font-semibold text-white">Budget violation</div><div className="mt-1 text-xs text-slate-500">AI wants $150, policy allows $100</div></button><button onClick={()=>runFailure('verification_failed')} disabled={busy} className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-4 text-left hover:bg-amber-400/10"><div className="text-sm font-semibold text-white">Verification failure</div><div className="mt-1 text-xs text-slate-500">Tests fail, payment stays unreleased</div></button></div></div>
        </div>
      </div>

      <StudioPanel transactions={rows} />
    </div>
  );
}









