import type { Summary, Transaction, WorkflowResult } from '../types';

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  summary: () => request<Summary>('/dashboard/summary'),
  transactions: () => request<Transaction[]>('/transactions'),
  createTask: (body: { title: string; description: string; budget_max: number; deadline_hours: number; payment_condition: string; quality_requirement: string }) =>
    request<{ id: number; status: string }>('/tasks', { method: 'POST', body: JSON.stringify(body) }),
  runTask: (id: number) => request<WorkflowResult>(`/tasks/${id}/run`, { method: 'POST' }),
  failure: (scenario: 'budget_exceeded' | 'verification_failed') => request<any>('/demo/failure', { method: 'POST', body: JSON.stringify({ scenario }) }),
  createPayment: (task_id: number) => request<any>('/payments/create', { method: 'POST', body: JSON.stringify({ task_id }) }),
  authorize: (task_id: number) => request<any>('/payments/authorize', { method: 'POST', body: JSON.stringify({ task_id }) }),
  capture: (task_id: number) => request<any>('/payments/capture', { method: 'POST', body: JSON.stringify({ task_id }) }),
  audit: (id: number) => request<any[]>(`/tasks/${id}/audit`),
  analytics: (query: string) => request<{ title: string; rows: any[]; explanation: string }>('/analytics/query', { method: 'POST', body: JSON.stringify({ query }) }),
};


