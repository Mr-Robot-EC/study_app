import SignUpForm from '@/components/auth/SignUpForm';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import { authOptions } from '@/app/api/[...nextauth]/route';
import { JSX } from 'react';

export default async function SignUpPage(): Promise<JSX.Element> {
  // Redirect if already authenticated
  const session = await getServerSession(authOptions);
  if (session) {
    redirect('/dashboard');
  }
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 className="text-center text-3xl font-extrabold text-gray-900">
          Create a new account
        </h1>
        <p className="mt-2 text-center text-sm text-gray-600">
          Fill in your details to get started
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <SignUpForm />
      </div>
    </div>
  );
}