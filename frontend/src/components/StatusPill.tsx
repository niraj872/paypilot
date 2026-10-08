export function StatusPill({ value, tone = 'neutral' }: { value: string; tone?: 'good' | 'warn' | 'bad' | 'neutral' }) {
  const classes = {
    good: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-300',
    warn: 'border-amber-400/20 bg-amber-400/10 text-amber-300',
    bad: 'border-rose-400/20 bg-rose-400/10 text-rose-300',
    neutral: 'border-slate-400/20 bg-slate-400/10 text-slate-300',
  }[tone];
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${classes}`}>{value}</span>;
}
