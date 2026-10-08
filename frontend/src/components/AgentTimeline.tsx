import type { WorkflowResult } from '../types';

type AgentTimelineProps = {
  result?: WorkflowResult | null;
};

type TimelineState = 'done' | 'active' | 'pending' | 'blocked';

function getStateIcon(state: TimelineState) {
  if (state === 'done') return '?';
  if (state === 'blocked') return '!';
  if (state === 'active') return '?';
  return '?';
}

export function AgentTimeline({ result }: AgentTimelineProps) {
  const hasWorkflow = Boolean(result);

  const riskDone = result?.risk_score != null;
  const verificationDone = result?.verification_status === 'PASSED';

  const paymentStatus = result?.payment_status?.toUpperCase() ?? '';

  const paymentDone =
    paymentStatus.includes('AUTHORIZED') ||
    paymentStatus.includes('COMPLETED') ||
    paymentStatus.includes('CAPTURED');

  const paymentBlocked =
    paymentStatus.includes('BLOCKED') ||
    paymentStatus.includes('FAILED');

  const items: [string, string, TimelineState][] = [
    [
      'Buyer Agent',
      hasWorkflow
        ? 'Task intent converted into financial requirements'
        : 'Waiting for autonomous workflow',
      hasWorkflow ? 'done' : 'pending',
    ],
    [
      'Negotiation Agent',
      result?.selected_seller
        ? `Selected seller: ${result.selected_seller}`
        : 'Waiting for seller offer selection',
      result?.selected_offer_id != null ? 'done' : 'pending',
    ],
    [
      'Risk Guardian',
      riskDone
        ? `Risk evaluated: ${result.risk_score}/100`
        : 'Waiting for risk evaluation',
      riskDone
        ? result?.risk_level === 'HIGH'
          ? 'blocked'
          : 'done'
        : 'pending',
    ],
    [
      'PayPal',
      paymentDone
        ? `Payment status: ${result?.payment_status}`
        : paymentBlocked
          ? `Payment blocked: ${result?.payment_status}`
          : 'Buyer approval / payment action pending',
      paymentDone
        ? 'done'
        : paymentBlocked
          ? 'blocked'
          : 'active',
    ],
    [
      'Verification Agent',
      verificationDone
        ? `Verification passed${result?.verification_score != null ? `: ${result.verification_score}/100` : ''}`
        : result?.verification_status === 'FAILED'
          ? 'Verification failed — payment remains unreleased'
          : 'Verification pending',
      verificationDone
        ? 'done'
        : result?.verification_status === 'FAILED'
          ? 'blocked'
          : 'pending',
    ],
  ];

  return (
    <div className="rounded-2xl border border-line bg-panel/80 p-5">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white">Agent Activity</h3>
          <p className="mt-1 text-xs text-slate-500">Real workflow state</p>
        </div>

        <span className="rounded-full border border-sky-400/20 bg-sky-400/10 px-2.5 py-1 text-[10px] uppercase tracking-wider text-sky-300">
          {hasWorkflow ? 'Live' : 'Waiting'}
        </span>
      </div>

      <div className="space-y-5">
        {items.map(([name, desc, state], i) => (
          <div key={name} className="flex gap-4">
            <div className="relative flex w-5 justify-center">
              <div
                className={[
                  'mt-0.5 flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold',
                  state === 'done' && 'bg-emerald-400/15 text-emerald-300 ring-1 ring-emerald-400/30',
                  state === 'active' && 'bg-sky-400/15 text-sky-300 ring-1 ring-sky-400/30 shadow-[0_0_18px_rgba(96,165,250,.35)]',
                  state === 'blocked' && 'bg-rose-400/15 text-rose-300 ring-1 ring-rose-400/30',
                  state === 'pending' && 'bg-slate-700/40 text-slate-500 ring-1 ring-slate-700',
                ].filter(Boolean).join(' ')}
              >
                {getStateIcon(state)}
              </div>

              {i < items.length - 1 && (
                <div className="absolute top-6 h-9 w-px bg-line" />
              )}
            </div>

            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <div className="text-sm font-medium text-white">{name}</div>
                <span className="text-[10px] uppercase tracking-wider text-slate-600">
                  {state}
                </span>
              </div>

              <div className="mt-1 text-xs leading-5 text-slate-400">{desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
