import { requireAuth } from '@/lib/auth';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { JSX } from 'react';

// In a real app, you would fetch the document from your API
async function getDocument(id: string) {
  // This is a placeholder; in a real app, use fetch or your API client
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API delay
  
  // For demo purposes
  if (id === '1' || id === '2') {
    return {
      id,
      title: `Sample Document ${id}`,
      content: `This is the content of document ${id}. It contains some sample text for demonstration purposes.`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      user_id: 'current-user-id',
    };
  }
  
  return null;
}

export default async function DocumentDetailPage({
  params
}: {
  params: { id: string }
}): Promise<JSX.Element> {
  await requireAuth();
  const document = await getDocument(params.id);
  
  if (!document) {
    notFound();
  }
  
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Document Details</h1>
          <div className="flex space-x-3">
            <Link
              href={`/documents/${params.id}/edit`}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Edit
            </Link>
            <Link
              href="/documents"
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
            >
              Back to List
            </Link>
          </div>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h2 className="text-lg leading-6 font-medium text-gray-900">{document.title}</h2>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                  Last updated on {new Date(document.updated_at).toLocaleString()}
                </p>
              </div>
              <div className="border-t border-gray-200">
                <div className="px-4 py-5 sm:p-6">
                  <p className="text-gray-700 whitespace-pre-wrap">{document.content}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}