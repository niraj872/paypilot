import type { ReactNode } from 'react';

export function MetricCard({ label, value, hint, icon }: { label: string; value: ReactNode; hint?: string; icon?: ReactNode }) {
  return (
    <div className="rounded-2xl border border-line bg-panel/80 p-5 shadow-glow">
      <div className="flex items-center justify-between text-sm text-slate-400"><span>{label}</span><span>{icon}</span></div>
      <div className="mt-3 text-3xl font-semibold tracking-tight text-white">{value}</div>
      {hint && <div className="mt-2 text-xs text-slate-500">{hint}</div>}
    </div>
  );
}
