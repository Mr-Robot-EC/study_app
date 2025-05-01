// File: app/layout.tsx
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/components/auth/AuthProvider';
import { JSX } from 'react';
import './globals.css';


const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Authentication System',
  description: 'A secure, scalable authentication system',
};

export default function RootLayout({ 
  children 
}: { 
  children: React.ReactNode 
}): JSX.Element {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}