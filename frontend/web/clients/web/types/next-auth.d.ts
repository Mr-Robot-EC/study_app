import { DefaultSession } from 'next-auth';
import { JWT } from 'next-auth/jwt';

declare module 'next-auth' {
  interface Session extends DefaultSession {
    user: {
      id: string;
      roles: string[];
      name?: string | null;
      email: string;
    } & DefaultSession['user'];
    accessToken: string;
    error?: string;
  }
  
  interface User {
    id: string;
    roles: string[];
    accessToken: string;
    refreshToken: string;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id?: string;
    roles?: string[];
    accessToken?: string;
    refreshToken?: string;
    error?: string;
  }
}