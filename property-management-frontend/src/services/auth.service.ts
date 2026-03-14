import api from './api';
import { User, LoginRequest, RegisterRequest, AuthResponse } from '../types';

export const authService = {
  /**
   * Login user
   */
  async login(credentials: LoginRequest): Promise<{ user: User; token: string }> {
    // OAuth2 password flow expects form data
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const { data } = await api.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store token
    localStorage.setItem('token', data.access_token);

    // Get user info
    const user = await this.getCurrentUser();

    return { user, token: data.access_token };
  },

  /**
   * Register new user
   */
  async register(userData: RegisterRequest): Promise<User> {
    const { data } = await api.post<User>('/auth/register', userData);
    return data;
  },

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const { data } = await api.get<User>('/auth/me');
    localStorage.setItem('user', JSON.stringify(data));
    return data;
  },

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },

  /**
   * Get stored user
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },
};