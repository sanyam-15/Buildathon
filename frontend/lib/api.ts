export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetchStats() {
  const res = await fetch(`${API_URL}/dashboard/stats`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchCases() {
  const res = await fetch(`${API_URL}/dashboard/cases`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch cases');
  return res.json();
}

export async function triggerRecovery(payload: any) {
  const res = await fetch(`${API_URL}/recovery/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to trigger recovery');
  return res.json();
}

export async function triggerBatchRecovery(count: number = 10, segment?: string) {
  const res = await fetch(`${API_URL}/recovery/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ count, segment: segment || undefined }),
  });
  if (!res.ok) throw new Error('Failed to trigger batch recovery');
  return res.json();
}

export async function getCaseDetails(caseId: string) {
  const res = await fetch(`${API_URL}/recovery/${caseId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch case details');
  return res.json();
}
