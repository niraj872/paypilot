import { useState } from 'react';
import { Search, Sparkles } from 'lucide-react';

export function CommandBar({ onRun }: { onRun: (query: string) => void }) {
  const [query, setQuery] = useState('Show me high-risk transactions');
  return (
    <div className="rounded-2xl border border-line bg-panel/80 p-3">
      <div className="flex gap-2">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-line bg-ink px-3"><Search className="h-4 w-4 text-slate-500"/><input className="w-full bg-transparent py-3 text-sm text-white outline-none placeholder:text-slate-600" value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')onRun(query)}}/></div>
        <button onClick={()=>onRun(query)} className="inline-flex items-center gap-2 rounded-xl bg-white px-4 text-sm font-medium text-ink hover:bg-slate-200"><Sparkles className="h-4 w-4"/>Ask Agent</button>
      </div>
    </div>
  );
}
