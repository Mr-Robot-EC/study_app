import NextAuth, { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import axios from 'axios';
import { JWT } from 'next-auth/jwt';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Helper function to refresh an access token
async function refreshAccessToken(token: JWT): Promise<JWT> {
  try {
    const response = await axios.post(`${API_URL}/token/refresh`, {
      refresh_token: token.refreshToken,
    });

    return {
      ...token,
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      iat: Math.floor(Date.now() / 1000),
    };
  } catch (error) {
    console.error('Error refreshing access token:', error);
    return {
      ...token,
      error: 'RefreshAccessTokenError',
    };
  }
}

export const authOptions: NextAuthOptions = {
  providers: [
    // Email/Password authentication
    CredentialsProvider({
      id: 'credentials',
      name: 'Email & Password',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        try {
          if (!credentials?.email || !credentials?.password) {
            return null;
          }
          
          // Call your own API for authentication
          const formData = new FormData();
          formData.append('username', credentials.email);
          formData.append('password', credentials.password);

          const response = await axios.post(`${API_URL}/token`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          if (response.data) {
            // Get user details
            const userResponse = await axios.get(`${API_URL}/users/me`, {
              headers: {
                Authorization: `Bearer ${response.data.access_token}`,
              },
            });

            // Return tokens and user info
            return {
              ...userResponse.data,
              accessToken: response.data.access_token,
              refreshToken: response.data.refresh_token,
            };
          }
          return null;
        } catch (error) {
          console.error('Authentication error:', error);
          return null;
        }
      },
    }),
    
    // Google OAuth
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
      authorization: {
        params: {
          scope: 'openid email profile',
        },
      },
    }),
  ],
  
  session: {
    strategy: 'jwt',
    maxAge: 60 * 60, // 1 hour
  },
  
  callbacks: {
    async jwt({ token, user, account }) {
      // Initial sign in
      if (account && user) {
        if (account.provider === 'credentials') {
          return {
            ...token,
            accessToken: user.accessToken,
            refreshToken: user.refreshToken,
            id: user.id,
            roles: user.roles,
          };
        } else if (account.provider === 'google') {
          try {
            // Exchange Google token for our own JWT
            const response = await axios.post(`${API_URL}/auth/google/token`, {
              access_token: account.access_token,
            });
            
            return {
              ...token,
              accessToken: response.data.access_token,
              refreshToken: response.data.refresh_token,
              id: response.data.user.id,
              roles: response.data.user.roles,
            };
          } catch (error) {
            console.error('Error exchanging Google token:', error);
            return { ...token, error: 'RefreshAccessTokenError' };
          }
        }
      }

      // On subsequent calls, check if the token needs refreshing
      if (token.accessToken) {
        const expiryTime = (token.iat as number + 60 * 60) * 1000;
        const currentTime = Date.now();
        
        if (currentTime < expiryTime) {
          return token;
        }
        
        return await refreshAccessToken(token);
      }
      
      return token;
    },
    
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id as string;
        session.user.roles = (token.roles as string[]) || [];
        session.accessToken = token.accessToken as string;
        session.error = token.error as string | undefined;
      }
      
      return session;
    },
  },
  
  pages: {
    signIn: '/auth/signin',
    signOut: '/auth/signout',
    error: '/auth/error',
  },
  
  events: {
    async signIn({ user, account }) {
      // Handle successful sign in (analytics, logging, etc.)
    },
    async signOut({ token }) {
      if (token?.refreshToken) {
        try {
          await axios.post(`${API_URL}/logout`, {
            refresh_token: token.refreshToken,
          }, {
            headers: {
              Authorization: `Bearer ${token.accessToken}`,
            },
          });
        } catch (error) {
          console.error('Error during logout:', error);
        }
      }
    },
  },
  
  debug: process.env.NODE_ENV === 'development',
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };