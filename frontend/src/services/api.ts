/**
 * API client for MNEMO backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to attach token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Load token from localStorage
    const savedToken = localStorage.getItem('mnemo_token');
    if (savedToken) {
      this.setToken(savedToken);
    }
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('mnemo_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('mnemo_token');
  }

  // Auth
  async login(email: string, password: string) {
    const response = await this.client.post('/api/auth/login', { email, password });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async register(email: string, password: string, fullName?: string, organization?: string) {
    const response = await this.client.post('/api/auth/register', {
      email,
      password,
      full_name: fullName,
      organization,
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/auth/me');
    return response.data;
  }

  // Nodes
  async listNodes(params?: any) {
    const response = await this.client.get('/api/nodes', { params });
    return response.data;
  }

  async getNode(nodeId: string) {
    const response = await this.client.get(`/api/nodes/${nodeId}`);
    return response.data;
  }

  async registerNode(nodeData: any) {
    const response = await this.client.post('/api/nodes/register', nodeData);
    return response.data;
  }

  async updateNode(nodeId: string, updates: any) {
    const response = await this.client.put(`/api/nodes/${nodeId}`, updates);
    return response.data;
  }

  // Marketplace
  async browseMarketplace(filters?: any) {
    const response = await this.client.get('/api/marketplace', { params: filters });
    return response.data;
  }

  async requestMemory(request: any) {
    const response = await this.client.post('/api/marketplace/request', request);
    return response.data;
  }

  // Contracts
  async listContracts(params?: any) {
    const response = await this.client.get('/api/contracts', { params });
    return response.data;
  }

  async getContract(contractId: string) {
    const response = await this.client.get(`/api/contracts/${contractId}`);
    return response.data;
  }

  async createContract(contractData: any) {
    const response = await this.client.post('/api/contracts/create', contractData);
    return response.data;
  }

  async settleContract(contractId: string, data?: any) {
    const response = await this.client.post(`/api/contracts/${contractId}/settle`, data || {});
    return response.data;
  }

  // Payments
  async createPayment(contractId: string, paymentMethod: string, stripeToken?: string) {
    const response = await this.client.post('/api/payments/create', {
      contract_id: contractId,
      payment_method: paymentMethod,
      stripe_token: stripeToken,
    });
    return response.data;
  }

  async processChipPayment(data: any) {
    const response = await this.client.post('/api/payments/crypto', data);
    return response.data;
  }

  // Analytics
  async getNodeEarnings(nodeId: string, days: number = 30) {
    const response = await this.client.get(`/api/analytics/node/${nodeId}/earnings`, {
      params: { days },
    });
    return response.data;
  }

  async getClientSpending(clientId: string, days: number = 30) {
    const response = await this.client.get(`/api/analytics/client/${clientId}/spending`, {
      params: { days },
    });
    return response.data;
  }

  async getMarketSupply(region?: string) {
    const response = await this.client.get('/api/analytics/market/supply', {
      params: { region },
    });
    return response.data;
  }

  async getDashboardStats() {
    const response = await this.client.get('/api/analytics/dashboard');
    return response.data;
  }

  async getNodeMetrics(nodeId: string, hours: number = 24) {
    const response = await this.client.get(`/api/analytics/node/${nodeId}/metrics`, {
      params: { hours },
    });
    return response.data;
  }

  // Clusters
  async listClusters() {
    const response = await this.client.get('/api/clusters');
    return response.data;
  }

  async getCluster(region: string) {
    const response = await this.client.get(`/api/clusters/${region}`);
    return response.data;
  }

  async getClusterNodes(region: string) {
    const response = await this.client.get(`/api/clusters/${region}/nodes`);
    return response.data;
  }

  async getClusterStats(region: string) {
    const response = await this.client.get(`/api/clusters/${region}/stats`);
    return response.data;
  }
}

export const api = new APIClient();
export default api;
