import { useState, type FormEvent } from 'react';
import { supabase } from '../../lib/supabase';
import { Alert, AuthCard, Field } from './SignupPage';

type Props = { onSwitchToSignup: () => void };

export function LoginPage({ onSwitchToSignup }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error: err } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (err) setError(err.message);
    // onAuthStateChange en auth-store redirige al dashboard automáticamente.
  }

  return (
    <AuthCard title="Bienvenido" subtitle="Inicia sesión en Connek">
      <form onSubmit={onSubmit} className="space-y-4">
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
          required
          autoComplete="current-password"
        />

        {error && <Alert kind="error">{error}</Alert>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-connek-600 hover:bg-connek-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl py-3 transition shadow-sm shadow-connek-600/25"
        >
          {loading ? 'Entrando…' : 'Iniciar sesión'}
        </button>
      </form>

      <p className="text-center text-sm text-zinc-500 mt-6">
        ¿No tienes cuenta?{' '}
        <button onClick={onSwitchToSignup} className="text-connek-600 hover:underline font-medium">
          Crea una
        </button>
      </p>
    </AuthCard>
  );
}
