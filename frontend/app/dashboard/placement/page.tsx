'use client';

import PlacementForm from '@/components/PlacementForm';

export default function PlacementPage() {
  return (
    <div className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Create Placement Request
        </h1>

        <div className="bg-white shadow rounded-lg p-6">
          <p className="text-sm text-gray-600 mb-6">
            Submit a placement request to find the best GPU node for your workload.
            The system will automatically select the optimal node based on VRAM
            requirements, bandwidth, and latency.
          </p>

          <PlacementForm />
        </div>
      </div>
    </div>
  );
}
