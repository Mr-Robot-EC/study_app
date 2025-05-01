import { requireAuth } from '@/lib/auth';
import Link from 'next/link';
import { JSX } from 'react';

export default async function DashboardPage(): Promise<JSX.Element> {
  const user = await requireAuth();
  
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 p-4">
              <h2 className="text-xl font-semibold mb-4">Welcome, {user.name || user.email}!</h2>
              <p className="mb-4">You are now signed in with the following details:</p>
              <ul className="list-disc list-inside mb-6">
                <li>Email: {user.email}</li>
                <li>User ID: {user.id}</li>
                <li>Roles: {user.roles.join(', ')}</li>
              </ul>
              
              <div className="mt-8">
                <h3 className="text-lg font-medium mb-4">Quick Links:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Link 
                    href="/documents" 
                    className="p-4 border border-gray-200 rounded-md hover:bg-gray-50"
                  >
                    <div className="font-medium">Documents</div>
                    <div className="text-sm text-gray-500">Manage your PDF documents</div>
                  </Link>
                  
                  <Link 
                    href="/profile" 
                    className="p-4 border border-gray-200 rounded-md hover:bg-gray-50"
                  >
                    <div className="font-medium">Profile</div>
                    <div className="text-sm text-gray-500">Update your account information</div>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}