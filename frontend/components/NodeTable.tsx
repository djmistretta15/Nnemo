'use client';

import Link from 'next/link';

interface Node {
  id: number;
  name: string;
  provider_name: string;
  region: string;
  gpu_model: string;
  vram_gb_total: number;
  vram_gb_free_estimate: number;
  is_active: boolean;
  updated_at: string;
}

export default function NodeTable({ nodes }: { nodes: Node[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Region
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Provider
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              GPU Model
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Total VRAM
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Free VRAM
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Updated
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {nodes.map((node) => (
            <tr key={node.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {node.name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {node.region}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {node.provider_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {node.gpu_model}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {node.vram_gb_total} GB
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {node.vram_gb_free_estimate.toFixed(1)} GB
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    node.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {node.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(node.updated_at).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-600">
                <Link href={`/dashboard/nodes/${node.id}`}>View</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {nodes.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No nodes found. Create one to get started.
        </div>
      )}
    </div>
  );
}
