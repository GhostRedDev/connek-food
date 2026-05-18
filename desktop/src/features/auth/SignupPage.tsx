import { useState, type FormEvent } from 'react';
import { supabase } from '../../lib/supabase';
import { OAuthButtons, OrDivider } from './OAuthButtons';

type Props = { onSwitchToLogin: () => void };

export function SignupPage({ onSwitchToLogin }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [restaurantName, setRestaurantName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
    setLoading(true);
    const { data, error: err } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { organization_name: restaurantName || 'Mi Restaurante' },
      },
    });
    setLoading(false);
    if (err) {
      setError(err.message);
      return;
    }
    if (data.user && !data.session) {
      setInfo('Cuenta creada. Revisa tu email para confirmar antes de iniciar sesión.');
    }
    // Si Supabase project tiene "Confirm email" OFF, ya hay sesión y onAuthStateChange redirige.
  }

  return (
    <AuthCard title="Crear cuenta" subtitle="Empieza tu prueba gratis de Connek">
      <OAuthButtons mode="signup" organizationName={restaurantName || undefined} />
      <OrDivider />

      <form onSubmit={onSubmit} className="space-y-4">
        <Field
          label="Nombre del restaurante"
          value={restaurantName}
          onChange={setRestaurantName}
          placeholder="Mi Restaurante"
          autoComplete="organization"
        />
        <Field
          label="Email"
          type="email"
          value={email}
          onChange={setEmail}
          placeholder="tu@restaurante.com"
          required
          autoComplete="email"
        />
        <Field
          label="Contraseña"
          type="password"
          value={password}
          onChange={setPassword}
          placeholder="mínimo 6 caracteres"
          required
          minLength={6}
          autoComplete="new-password"
        />

        {error && <Alert kind="error">{error}</Alert>}
        {info && <Alert kind="info">{info}</Alert>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-connek-600 hover:bg-connek-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl py-3 transition shadow-sm shadow-connek-600/25"
        >
          {loading ? 'Creando…' : 'Crear cuenta'}
        </button>
      </form>

      <p className="text-center text-sm text-zinc-500 mt-6">
        ¿Ya tienes cuenta?{' '}
        <button onClick={onSwitchToLogin} className="text-connek-600 hover:underline font-medium">
          Inicia sesión
        </button>
      </p>
    </AuthCard>
  );
}

// ─── shared bits (export para reusar en LoginPage) ───────────────

export function AuthCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-connek-600 shadow-lg shadow-connek-600/25 mb-4">
            <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
              <path d="M9 22c0-4 3-7 7-7s7 3 7 7" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
              <circle cx="16" cy="12" r="2.5" fill="white" />
            </svg>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900">{title}</h1>
          <p className="text-sm text-zinc-500 mt-2">{subtitle}</p>
        </div>
        <div className="bg-white border border-zinc-200/80 rounded-2xl p-8 shadow-sm">
          {children}
        </div>
      </div>
    </main>
  );
}

export function Field({
  label,
  value,
  onChange,
  type = 'text',
  ...rest
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, 'value' | 'onChange' | 'type'>) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-zinc-700 mb-1.5">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border border-zinc-300 focus:border-connek-600 focus:ring-2 focus:ring-connek-600/20 focus:outline-none px-3.5 py-2.5 text-sm text-zinc-900 placeholder-zinc-400 transition"
        {...rest}
      />
    </label>
  );
}

export function Alert({ kind, children }: { kind: 'error' | 'info'; children: React.ReactNode }) {
  const cls =
    kind === 'error'
      ? 'bg-rose-50 border-rose-200 text-rose-700'
      : 'bg-blue-50 border-blue-200 text-blue-700';
  return (
    <div className={`text-sm rounded-lg border px-3 py-2 ${cls}`}>{children}</div>
  );
}
