import { useState } from 'react';
import { LoginPage } from './features/auth/LoginPage';
import { SignupPage } from './features/auth/SignupPage';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { useAuth } from './lib/auth-store';

type AuthScreen = 'login' | 'signup';

export function App() {
  const { session, loading } = useAuth();
  const [screen, setScreen] = useState<AuthScreen>('login');

  if (loading) return <BootScreen />;
  if (session) return <DashboardPage />;

  return screen === 'login' ? (
    <LoginPage onSwitchToSignup={() => setScreen('signup')} />
  ) : (
    <SignupPage onSwitchToLogin={() => setScreen('login')} />
  );
}

function BootScreen() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="flex items-center gap-3 text-zinc-400">
        <span className="w-2 h-2 rounded-full bg-connek-600 animate-pulse" />
        <span className="text-sm">Cargando Connek…</span>
      </div>
    </main>
  );
}
