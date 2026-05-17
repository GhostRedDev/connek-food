// Cliente HTTP minimal contra el backend FastAPI.
// Cuando se introduzca openapi-typescript, este archivo se reemplaza por openapi-fetch.

const API_BASE = import.meta.env.VITE_API_URL ?? '';

export type HealthResponse = {
  status: string;
  service: string;
  env: string;
  commit: string;
  region: string;
  timestamp: string;
};

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
  return res.json();
}
