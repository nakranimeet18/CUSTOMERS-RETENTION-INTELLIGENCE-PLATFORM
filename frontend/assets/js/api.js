/**
 * Central API client for Customer Retention Intelligence Platform
 */
const API = {
  BASE_URL: window.location.port === '8000' ? '' : (window.API_BASE_URL || 'http://localhost:8000'),

  getToken() {
    return localStorage.getItem('crip_token') || sessionStorage.getItem('crip_token');
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${this.BASE_URL}${endpoint}`;
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (response.status === 401) {
        // Redirect on session expiry
        localStorage.removeItem('crip_token');
        localStorage.removeItem('crip_user');
        sessionStorage.clear();
        if (!window.location.pathname.endsWith('login.html')) {
          window.location.href = '/login.html';
        }
        return { success: false, error: 'Session expired. Please log in again.' };
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        const msg = errData.detail || errData.message || `Request failed with status ${response.status}`;
        return { success: false, error: msg };
      }

      const data = await response.json();
      return { success: true, data };
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      return { success: false, error: err.message || 'Network connection failed' };
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body: JSON.stringify(body) });
  },

  put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body: JSON.stringify(body) });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};

window.API = API;
