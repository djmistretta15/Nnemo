import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full space-y-8 text-center">
        <div>
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            Memory Arbitrage Router
          </h1>
          <p className="text-2xl text-gray-600 mb-8">
            Put Jobs Where VRAM Fits Best
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 space-y-6">
          <p className="text-lg text-gray-700">
            MAR is a VRAM-aware GPU placement engine that intelligently routes
            workloads to the optimal GPU nodes based on memory efficiency,
            locality, and system telemetry.
          </p>

          <div className="grid md:grid-cols-3 gap-6 mt-8">
            <div className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Smart Placement</h3>
              <p className="text-gray-600">
                Algorithm scores nodes based on VRAM headroom, bandwidth, and
                latency
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Real-time Telemetry</h3>
              <p className="text-gray-600">
                Track GPU utilization, VRAM usage, and temperature in real-time
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Production Ready</h3>
              <p className="text-gray-600">
                Full REST API, authentication, and comprehensive test suite
              </p>
            </div>
          </div>

          <div className="flex justify-center gap-4 mt-8">
            <Link
              href="/auth/register"
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Get Started
            </Link>
            <Link
              href="/auth/login"
              className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>

        <div className="mt-8 text-gray-500">
          <Link href="/docs" className="hover:text-primary-600">
            API Documentation
          </Link>
          {' | '}
          <Link href="/dashboard" className="hover:text-primary-600">
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
