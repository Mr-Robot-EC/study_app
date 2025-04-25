import { requireAuth } from '@/lib/auth';
import Link from 'next/link';

// In a real app, you would fetch documents from your API
async function getDocuments() {
  // This is a placeholder; in a real app, use fetch or your API client
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API delay
  
  return [
    {
      id: '1',
      title: 'Sample Document 1',
      created_at: new Date().toISOString(),
    },
    {
      id: '2',
      title: 'Sample Document 2',
      created_at: new Date().toISOString(),
    },
  ];
}

export default async function DocumentsPage(): Promise<JSX.Element> {
  await requireAuth();
  const documents = await getDocuments();
  
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <Link
            href="/documents/create"
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Create New
          </Link>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            {documents.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No documents found</p>
                <Link
                  href="/documents/create"
                  className="mt-4 inline-block bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Create your first document
                </Link>
              </div>
            ) : (
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                  {documents.map((doc) => (
                    <li key={doc.id}>
                      <Link href={`/documents/${doc.id}`} className="block hover:bg-gray-50">
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-blue-600 truncate">{doc.title}</p>
                            <div className="ml-2 flex-shrink-0 flex">
                              <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                View
                              </p>
                            </div>
                          </div>
                          <div className="mt-2 flex justify-between">
                            <div className="sm:flex">
                              <p className="flex items-center text-sm text-gray-500">
                                Created on {new Date(doc.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}