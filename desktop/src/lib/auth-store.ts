// Estado de auth global usando React state simple (sin libs extra para MVP).
// Se hidrata al montar la app con supabase.auth.getSession() y se actualiza
// con onAuthStateChange. Cuando crezca, migrar a Zustand.

import type { Session, User } from '@supabase/supabase-js';
import { useEffect, useState } from 'react';
import { supabase } from './supabase';

let cachedSession: Session | null = null;
const listeners = new Set<(s: Session | null) => void>();

function broadcast(s: Session | null) {
  cachedSession = s;
  listeners.forEach((l) => l(s));
}

// Bootstrap: lee la sesión actual y se suscribe a cambios.
let initialized = false;
async function initAuth() {
  if (initialized) return;
  initialized = true;
  const { data } = await supabase.auth.getSession();
  broadcast(data.session);
  supabase.auth.onAuthStateChange((_event, session) => broadcast(session));
}

void initAuth();

export function useAuth(): {
  session: Session | null;
  user: User | null;
  loading: boolean;
} {
  const [session, setSession] = useState<Session | null>(cachedSession);
  const [loading, setLoading] = useState(cachedSession === null && !initialized);

  useEffect(() => {
    const sub = (s: Session | null) => {
      setSession(s);
      setLoading(false);
    };
    listeners.add(sub);
    // ya hidratamos si está disponible
    if (cachedSession !== null) setLoading(false);
    void supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    return () => {
      listeners.delete(sub);
    };
  }, []);

  return { session, user: session?.user ?? null, loading };
}

export async function signOut() {
  await supabase.auth.signOut();
}
