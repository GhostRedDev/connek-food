import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { api, ApiError } from '../../lib/api';
import { signOut, useAuth } from '../../lib/auth-store';

export function DashboardPage() {
  const { user } = useAuth();
  const [activeOrgId, setActiveOrgId] = useState<string | null>(null);

  const me = useQuery({
    queryKey: ['me'],
    queryFn: api.identity.me,
    retry: false,
  });

  // Auto-seleccionar primera org cuando llegue
  if (me.data && !activeOrgId && me.data.organizations[0]) {
    setActiveOrgId(me.data.organizations[0].id);
  }

  const activeOrg = me.data?.organizations.find((o) => o.id === activeOrgId);

  return (
    <div className="min-h-screen flex flex-col">
      <Topbar
        userEmail={user?.email ?? ''}
        orgName={activeOrg?.name ?? '—'}
        plan={activeOrg?.plan ?? '—'}
      />

      <main className="flex-1 px-6 py-8 max-w-5xl mx-auto w-full">
        <Header user={user?.email ?? ''} />

        {me.isLoading && <Skeleton />}
        {me.isError && <ErrorPanel error={me.error} />}
        {me.data && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
            <ProfileCard email={me.data.email} userId={me.data.user_id} />
            <OrgCard org={activeOrg} membershipCount={me.data.memberships.length} />
            <RolesCard memberships={me.data.memberships} />
            <ComingSoonCard />
          </div>
        )}
      </main>
    </div>
  );
}

function Topbar({
  userEmail,
  orgName,
  plan,
}: {
  userEmail: string;
  orgName: string;
  plan: string;
}) {
  return (
    <header className="bg-white border-b border-zinc-200/80 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="inline-flex items-center justify-center w-9 h-9 rounded-xl bg-connek-600">
          <svg width="20" height="20" viewBox="0 0 32 32" fill="none">
            <path d="M9 22c0-4 3-7 7-7s7 3 7 7" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
            <circle cx="16" cy="12" r="2.5" fill="white" />
          </svg>
        </div>
        <div>
          <div className="text-sm font-semibold text-zinc-900 leading-tight">{orgName}</div>
          <div className="text-xs text-zinc-500 leading-tight">
            Plan <span className="font-medium capitalize">{plan}</span>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-zinc-600 hidden sm:inline">{userEmail}</span>
        <button
          onClick={() => void signOut()}
          className="text-sm text-zinc-700 hover:text-rose-600 transition px-3 py-1.5 rounded-lg hover:bg-zinc-100"
        >
          Salir
        </button>
      </div>
    </header>
  );
}

function Header({ user }: { user: string }) {
  return (
    <div>
      <h1 className="text-3xl font-semibold tracking-tight text-zinc-900">
        Hola{user ? `, ${user.split('@')[0]}` : ''} 👋
      </h1>
      <p className="text-zinc-500 mt-1">
        Bienvenido a Connek Restaurant OS. Este es tu dashboard inicial.
      </p>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="bg-white border border-zinc-200/80 rounded-2xl p-6 h-32 animate-pulse" />
      ))}
    </div>
  );
}

function ErrorPanel({ error }: { error: unknown }) {
  const msg = error instanceof ApiError ? `${error.status}: ${JSON.stringify(error.payload)}` : String(error);
  return (
    <div className="mt-8 bg-rose-50 border border-rose-200 rounded-2xl p-6">
      <h3 className="font-medium text-rose-900">No se pudo cargar tu perfil</h3>
      <p className="text-sm text-rose-700 mt-1 font-mono">{msg}</p>
      <p className="text-xs text-rose-600 mt-3">
        Si recién creaste la cuenta, espera unos segundos y refresca. Si persiste, revisa que el
        backend tenga las env vars de Supabase configuradas.
      </p>
    </div>
  );
}

function Card({
  title,
  children,
  accent,
}: {
  title: string;
  children: React.ReactNode;
  accent?: boolean;
}) {
  return (
    <div
      className={`bg-white border rounded-2xl p-6 shadow-sm ${
        accent ? 'border-connek-200' : 'border-zinc-200/80'
      }`}
    >
      <h3 className="text-xs uppercase tracking-wide text-zinc-400 mb-3 font-medium">{title}</h3>
      {children}
    </div>
  );
}

function ProfileCard({ email, userId }: { email: string; userId: string }) {
  return (
    <Card title="Tu perfil">
      <div className="text-lg text-zinc-900 font-medium">{email}</div>
      <div className="text-xs text-zinc-400 mt-1 font-mono">{userId.slice(0, 18)}…</div>
    </Card>
  );
}

function OrgCard({
  org,
  membershipCount,
}: {
  org: { name: string; slug: string; plan: string } | undefined;
  membershipCount: number;
}) {
  if (!org) {
    return (
      <Card title="Organización" accent>
        <div className="text-zinc-500 text-sm">Sin organización activa</div>
      </Card>
    );
  }
  return (
    <Card title="Organización activa" accent>
      <div className="text-lg text-zinc-900 font-medium">{org.name}</div>
      <div className="text-xs text-zinc-500 mt-1">
        <code className="bg-zinc-100 px-1.5 py-0.5 rounded">{org.slug}</code> ·{' '}
        <span className="capitalize">{org.plan}</span> · {membershipCount} miembro(s)
      </div>
    </Card>
  );
}

function RolesCard({
  memberships,
}: {
  memberships: Array<{ organization_id: string; role: string }>;
}) {
  return (
    <Card title="Tus roles">
      <div className="space-y-1">
        {memberships.map((m) => (
          <div key={m.organization_id} className="text-sm text-zinc-700">
            <span className="font-medium capitalize">{m.role}</span> en{' '}
            <span className="font-mono text-xs text-zinc-500">{m.organization_id.slice(0, 8)}…</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ComingSoonCard() {
  return (
    <Card title="Próximamente">
      <ul className="text-sm text-zinc-600 space-y-1.5">
        <li>📅 Reservas + calendar + timeline</li>
        <li>🪑 Floor plan en tiempo real</li>
        <li>📲 Waitlist con WhatsApp</li>
        <li>⭐ Reviews con respuesta IA</li>
      </ul>
    </Card>
  );
}
