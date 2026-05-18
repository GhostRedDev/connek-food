// Cliente HTTP minimal contra FastAPI. Inyecta JWT de Supabase automáticamente.
// Cuando se introduzca openapi-typescript se reemplaza por openapi-fetch tipado.

import { supabase } from './supabase';

const API_BASE = import.meta.env.VITE_API_URL ?? '';

async function authHeaders(orgId?: string | null): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (data.session?.access_token) {
    headers.Authorization = `Bearer ${data.session.access_token}`;
  }
  if (orgId) headers['X-Organization-Id'] = orgId;
  return headers;
}

async function request<T>(
  method: string,
  path: string,
  opts: { body?: unknown; orgId?: string | null } = {},
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: await authHeaders(opts.orgId),
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = { detail: text };
    }
    throw new ApiError(res.status, parsed);
  }
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public payload: unknown,
  ) {
    super(`API ${status}: ${JSON.stringify(payload)}`);
  }
}

// ─── Endpoints tipados (manual hasta que tengamos openapi-typescript) ──

export type HealthResponse = {
  status: string;
  service: string;
  env: string;
  commit: string;
  region: string;
  timestamp: string;
};

export const api = {
  health: () => request<HealthResponse>('GET', '/api/v1/health'),

  identity: {
    me: () =>
      request<{
        user_id: string;
        email: string;
        memberships: Array<{
          id: string;
          user_id: string;
          organization_id: string;
          role: string;
          created_at: string;
        }>;
        organizations: Array<{
          id: string;
          name: string;
          slug: string;
          plan: string;
          created_at: string;
        }>;
      }>('GET', '/api/v1/identity/me'),

    createOrganization: (name: string) =>
      request<{ id: string; name: string; slug: string; plan: string; created_at: string }>(
        'POST',
        '/api/v1/identity/organizations',
        { body: { name } },
      ),
  },
};
