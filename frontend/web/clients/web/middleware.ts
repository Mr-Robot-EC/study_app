import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';
import { JWT } from 'next-auth/jwt';
import { NextRequest } from 'next/server';

// This middleware handles protected routes and role-based access
export default withAuth(
  function middleware(req: NextRequest & { nextauth: { token: JWT | null } }) {
    const pathname = req.nextUrl.pathname;
    const token = req.nextauth.token;
    
    // Redirect to login if no token (should be handled by withAuth, but extra safety)
    if (!token) {
      return NextResponse.redirect(new URL('/auth/signin', req.url));
    }
    
    // Check for admin-only routes
    if (pathname.startsWith('/admin')) {
      // Check if user has admin role
      const roles = token?.roles as string[] || [];
      
      if (!roles.includes('admin')) {
        // Redirect non-admins to unauthorized page
        return NextResponse.redirect(new URL('/unauthorized', req.url));
      }
    }
    
    // Pass request through if authorized
    return NextResponse.next();
  },
  {
    callbacks: {
      // Only run middleware on protected routes
      authorized: ({ token }) => !!token,
    },
  }
);

// Specify which routes should be protected
export const config = {
  matcher: [
    '/dashboard/:path*', 
    '/documents/:path*',
    '/admin/:path*',
    '/api/protected/:path*'
  ],
};