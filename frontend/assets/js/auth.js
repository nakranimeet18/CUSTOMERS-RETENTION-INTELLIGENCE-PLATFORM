/**
 * Authentication module (Login, Register, Session & Role verification)
 */
const Auth = {
  setSession(token, user, remember = true) {
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem('crip_token', token);
    storage.setItem('crip_user', JSON.stringify(user));
    storage.setItem('crip_role', (user.role || 'user').toLowerCase());
  },

  getToken() {
    return localStorage.getItem('crip_token') || sessionStorage.getItem('crip_token');
  },

  getUser() {
    const str = localStorage.getItem('crip_user') || sessionStorage.getItem('crip_user');
    if (!str) return null;
    try { return JSON.parse(str); } catch (e) { return null; }
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  isAdmin() {
    const role = localStorage.getItem('crip_role') || sessionStorage.getItem('crip_role');
    return role === 'admin';
  },

  async login(email, password, remember = true) {
    const res = await API.post('/api/auth/login', { email, password });
    if (res.success && res.data) {
      const token = res.data.access_token;
      const user = {
        id: res.data.user_id,
        email: res.data.email || email,
        name: (res.data.email || email).split('@')[0],
        role: (res.data.role || 'user').toLowerCase()
      };

      this.setSession(token, user, remember);
      return { success: true, user };
    }
    return { success: false, error: res.error || 'Invalid credentials' };
  },

  async register(payload) {
    return await API.post('/api/auth/register', payload);
  },

  logout() {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/login.html';
  },

  requireAuth(requiredRole = null) {
    if (!this.isAuthenticated()) {
      window.location.href = '/login.html';
      return false;
    }
    if (requiredRole === 'admin' && !this.isAdmin()) {
      alert('Administrator privileges required.');
      window.location.href = '/user/dashboard.html';
      return false;
    }
    return true;
  }
};

window.Auth = Auth;
