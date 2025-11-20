'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { useState } from 'react';

export default function ModelProfilesPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    suggested_min_vram_gb: '',
    suggested_batch_size: '',
    category: 'llm',
  });

  const { data: profiles, isLoading } = useQuery({
    queryKey: ['model-profiles'],
    queryFn: () => apiClient.getModelProfiles(),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => apiClient.createModelProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['model-profiles'] });
      setShowForm(false);
      setFormData({
        name: '',
        suggested_min_vram_gb: '',
        suggested_batch_size: '',
        category: 'llm',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      ...formData,
      suggested_min_vram_gb: parseFloat(formData.suggested_min_vram_gb),
      suggested_batch_size: formData.suggested_batch_size
        ? parseInt(formData.suggested_batch_size)
        : null,
    });
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Model Profiles</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            {showForm ? 'Cancel' : 'Add Profile'}
          </button>
        </div>

        {showForm && (
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Create Model Profile
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Model Name
                </label>
                <input
                  type="text"
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Minimum VRAM (GB)
                </label>
                <input
                  type="number"
                  step="0.1"
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
                  value={formData.suggested_min_vram_gb}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      suggested_min_vram_gb: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Suggested Batch Size (Optional)
                </label>
                <input
                  type="number"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
                  value={formData.suggested_batch_size}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      suggested_batch_size: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Category
                </label>
                <select
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
                  value={formData.category}
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                >
                  <option value="llm">LLM</option>
                  <option value="diffusion">Diffusion</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={createMutation.isPending}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Profile'}
              </button>
            </form>
          </div>
        )}

        <div className="bg-white shadow rounded-lg overflow-hidden">
          {isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Min VRAM
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Batch Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {profiles?.map((profile: any) => (
                  <tr key={profile.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {profile.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {profile.suggested_min_vram_gb} GB
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {profile.suggested_batch_size || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-primary-100 text-primary-800">
                        {profile.category}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {!isLoading && profiles?.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No model profiles yet. Create one to get started.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
