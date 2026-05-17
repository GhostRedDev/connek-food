import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from './lib/api';

export function App() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl">
        <Hero />
        <BackendStatus />
        <Footer />
      </div>
    </main>
  );
}

function Hero() {
  return (
    <header className="text-center mb-12">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-connek-600 shadow-lg shadow-connek-600/25 mb-6">
        <Logo />
      </div>
      <h1 className="text-5xl md:text-6xl font-semibold tracking-tight text-zinc-900 mb-4">
        Connek
      </h1>
      <p className="text-xl text-zinc-600 mb-2">Restaurant OS</p>
      <p className="text-sm text-zinc-500 max-w-md mx-auto">
        Plataforma multi-tenant para restaurantes. Reservas, waitlist, floor plan,
        comunicación automatizada y reviews con IA.
      </p>
    </header>
  );
}

function BackendStatus() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 10_000,
  });

  return (
    <section className="rounded-2xl border border-zinc-200/80 bg-white/80 backdrop-blur p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium text-zinc-700">Backend status</h2>
        <StatusBadge state={isLoading ? 'loading' : isError ? 'down' : 'up'} />
      </div>

      {isLoading && <div className="text-sm text-zinc-500">Comprobando…</div>}

      {isError && (
        <div className="text-sm text-rose-600">
          {(error as Error)?.message ?? 'Error desconocido'}
        </div>
      )}

      {data && (
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
          <Row label="Service" value={data.service} />
          <Row label="Environment" value={data.env} />
          <Row label="Region" value={data.region} mono />
          <Row label="Commit" value={data.commit} mono />
        </dl>
      )}
    </section>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-zinc-400 mb-1">{label}</dt>
      <dd className={`text-zinc-900 ${mono ? 'font-mono text-xs' : ''}`}>{value}</dd>
    </div>
  );
}

function StatusBadge({ state }: { state: 'loading' | 'up' | 'down' }) {
  const cfg = {
    loading: { dot: 'bg-zinc-400', text: 'text-zinc-600', label: 'Comprobando' },
    up:      { dot: 'bg-emerald-500', text: 'text-emerald-700', label: 'Online' },
    down:    { dot: 'bg-rose-500', text: 'text-rose-700', label: 'Offline' },
  }[state];
  return (
    <span className={`inline-flex items-center gap-2 text-xs font-medium ${cfg.text}`}>
      <span className={`w-2 h-2 rounded-full ${cfg.dot} ${state === 'loading' ? 'animate-pulse' : ''}`} />
      {cfg.label}
    </span>
  );
}

function Footer() {
  return (
    <footer className="mt-12 text-center text-xs text-zinc-400">
      <p>v0.0.1 · MVP en construcción · 30 días</p>
    </footer>
  );
}

function Logo() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 22c0-4 3-7 7-7s7 3 7 7" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="16" cy="12" r="2.5" fill="white" />
    </svg>
  );
}
