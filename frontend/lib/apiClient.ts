import axios, { AxiosInstance, AxiosError } from 'axios';
import { getToken, clearToken } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1_PREFIX = process.env.NEXT_PUBLIC_API_V1_PREFIX || '/api/v1';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}${API_V1_PREFIX}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(data: {
    organization_name: string;
    email: string;
    password: string;
    full_name: string;
  }) {
    const response = await this.client.post('/auth/register', data);
    return response.data;
  }

  async login(data: { email: string; password: string }) {
    const response = await this.client.post('/auth/login', data);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Node endpoints
  async getNodes(params?: { region?: string; provider?: string; active?: boolean }) {
    const response = await this.client.get('/nodes', { params });
    return response.data;
  }

  async getNode(id: number) {
    const response = await this.client.get(`/nodes/${id}`);
    return response.data;
  }

  async createNode(data: any) {
    const response = await this.client.post('/nodes', data);
    return response.data;
  }

  async updateNode(id: number, data: any) {
    const response = await this.client.patch(`/nodes/${id}`, data);
    return response.data;
  }

  async deleteNode(id: number) {
    const response = await this.client.delete(`/nodes/${id}`);
    return response.data;
  }

  // Telemetry endpoints
  async createTelemetry(nodeId: number, data: any) {
    const response = await this.client.post(`/nodes/${nodeId}/telemetry`, data);
    return response.data;
  }

  async getNodeTelemetry(nodeId: number, limit = 100) {
    const response = await this.client.get(`/nodes/${nodeId}/telemetry`, {
      params: { limit },
    });
    return response.data;
  }

  // Model Profile endpoints
  async getModelProfiles() {
    const response = await this.client.get('/model-profiles');
    return response.data;
  }

  async getModelProfile(id: number) {
    const response = await this.client.get(`/model-profiles/${id}`);
    return response.data;
  }

  async createModelProfile(data: any) {
    const response = await this.client.post('/model-profiles', data);
    return response.data;
  }

  async updateModelProfile(id: number, data: any) {
    const response = await this.client.patch(`/model-profiles/${id}`, data);
    return response.data;
  }

  async deleteModelProfile(id: number) {
    const response = await this.client.delete(`/model-profiles/${id}`);
    return response.data;
  }

  // Placement endpoints
  async createPlacementRequest(data: any) {
    const response = await this.client.post('/placement/requests', data);
    return response.data;
  }

  async getPlacementRequests() {
    const response = await this.client.get('/placement/requests');
    return response.data;
  }

  async getPlacementRequest(id: number) {
    const response = await this.client.get(`/placement/requests/${id}`);
    return response.data;
  }
}

export const apiClient = new APIClient();
export default apiClient;
