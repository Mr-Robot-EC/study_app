import { SessionProvider } from 'next-auth/react';
import { ReactNode } from 'react';
import { JSX } from 'react';

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps): JSX.Element {
  return <SessionProvider>{children}</SessionProvider>;
}