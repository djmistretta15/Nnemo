'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import NodeTable from '@/components/NodeTable';
import Link from 'next/link';

export default function NodesPage() {
  const { data: nodes, isLoading } = useQuery({
    queryKey: ['nodes'],
    queryFn: () => apiClient.getNodes(),
  });

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">GPU Nodes</h1>
          <Link
            href="/dashboard/nodes/create"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            Add Node
          </Link>
        </div>

        <div className="bg-white shadow rounded-lg overflow-hidden">
          {isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <NodeTable nodes={nodes || []} />
          )}
        </div>
      </div>
    </div>
  );
}
