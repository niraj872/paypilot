import { useMemo, useState } from 'react';
import { AgStudio } from 'ag-studio-react';

export function StudioPanel({ transactions }: { transactions: any[] }) {
  const [mode, setMode] = useState<'view' | 'edit'>('view');
  const data = useMemo(() => ({ transactions }), [transactions]);
  return (
    <div className="rounded-2xl border border-line bg-panel/80 p-5">
      <div className="mb-4 flex items-center justify-between">
        <div><h3 className="font-semibold text-white">AG Studio Intelligence</h3><p className="mt-1 text-xs text-slate-500">Interactive analytics canvas over PayPilot transaction data</p></div>
        <button onClick={()=>setMode(m=>m==='view'?'edit':'view')} className="rounded-lg border border-line px-3 py-2 text-xs text-slate-200 hover:bg-white/5">{mode === 'view' ? 'Edit dashboard' : 'Lock dashboard'}</button>
      </div>
      <div className="h-[480px] overflow-hidden rounded-xl border border-line bg-ink">
        <AgStudio data={data as any} mode={mode as any} />
      </div>
      <p className="mt-3 text-[11px] text-slate-500">AG Studio can be tested locally without a production licence; a trial licence is needed for production use without the development watermark. See the README for enablement steps.</p>
    </div>
  );
}
