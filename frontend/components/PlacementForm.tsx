'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';

export default function PlacementForm() {
  const queryClient = useQueryClient();
  const [modelName, setModelName] = useState('');
  const [requiredVramGb, setRequiredVramGb] = useState('');
  const [preferredRegion, setPreferredRegion] = useState('');
  const [priority, setPriority] = useState('normal');
  const [result, setResult] = useState<any>(null);

  const placementMutation = useMutation({
    mutationFn: (data: any) => apiClient.createPlacementRequest(data),
    onSuccess: (data) => {
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ['placements'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setResult(null);

    const payload: any = {
      model_name: modelName,
      priority,
    };

    if (requiredVramGb) {
      payload.required_vram_gb = parseFloat(requiredVramGb);
    }

    if (preferredRegion) {
      payload.preferred_region = preferredRegion;
    }

    placementMutation.mutate(payload);
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="modelName"
            className="block text-sm font-medium text-gray-700"
          >
            Model Name
          </label>
          <input
            type="text"
            id="modelName"
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
            placeholder="e.g., Llama-2-13B"
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
          />
        </div>

        <div>
          <label
            htmlFor="requiredVram"
            className="block text-sm font-medium text-gray-700"
          >
            Required VRAM (GB) - Optional
          </label>
          <input
            type="number"
            id="requiredVram"
            step="0.1"
            min="0"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
            placeholder="Leave empty to use model profile"
            value={requiredVramGb}
            onChange={(e) => setRequiredVramGb(e.target.value)}
          />
        </div>

        <div>
          <label
            htmlFor="region"
            className="block text-sm font-medium text-gray-700"
          >
            Preferred Region - Optional
          </label>
          <select
            id="region"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
            value={preferredRegion}
            onChange={(e) => setPreferredRegion(e.target.value)}
          >
            <option value="">Any region</option>
            <option value="us-east-1">us-east-1</option>
            <option value="us-west-2">us-west-2</option>
            <option value="eu-west-1">eu-west-1</option>
            <option value="ap-southeast-1">ap-southeast-1</option>
          </select>
        </div>

        <div>
          <label
            htmlFor="priority"
            className="block text-sm font-medium text-gray-700"
          >
            Priority
          </label>
          <select
            id="priority"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-4 py-2 border"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            <option value="normal">Normal</option>
            <option value="high">High</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={placementMutation.isPending}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          {placementMutation.isPending ? 'Finding Best Node...' : 'Submit Placement Request'}
        </button>

        {placementMutation.isError && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">
              {(placementMutation.error as any)?.response?.data?.detail ||
                'Failed to create placement request'}
            </p>
          </div>
        )}
      </form>

      {result && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Placement Decision
          </h3>
          <div className="space-y-4">
            <div>
              <span className="text-sm font-medium text-gray-500">
                Chosen Node:
              </span>
              <p className="mt-1 text-sm text-gray-900">
                {result.decision.node.name} ({result.decision.node.gpu_model})
              </p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">
                Fit Score:
              </span>
              <p className="mt-1 text-sm text-gray-900">
                {result.decision.estimated_fit_score.toFixed(2)} / 100
              </p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Reason:</span>
              <p className="mt-1 text-sm text-gray-900">
                {result.decision.reason}
              </p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">
                Node Details:
              </span>
              <ul className="mt-1 text-sm text-gray-900 list-disc list-inside">
                <li>Region: {result.decision.node.region}</li>
                <li>Provider: {result.decision.node.provider_name}</li>
                <li>
                  Total VRAM: {result.decision.node.vram_gb_total} GB
                </li>
                <li>
                  Free VRAM: {result.decision.node.vram_gb_free_estimate} GB
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
