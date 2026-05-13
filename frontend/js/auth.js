// ============================================
// AUTENTICAÇÃO - Login, Registro, Logout
// ============================================

class AuthManager {
  constructor() {
    this.token = localStorage.getItem(CONFIG.TOKEN_KEY);
    this.user = JSON.parse(localStorage.getItem(CONFIG.USER_KEY) || 'null');
  }

  isAuthenticated() {
    return !!this.token;
  }

  getUser() {
    return this.user;
  }

  setSession(token, user) {
    this.token = token;
    this.user = user;
    localStorage.setItem(CONFIG.TOKEN_KEY, token);
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
  }

  clearSession() {
    this.token = null;
    this.user = null;
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
  }

  async login(email, senha) {
    try {
      const response = await api.post(CONFIG.ENDPOINTS.LOGIN, { email, senha }, false);
      this.setSession(response.access_token, response.usuario);
      return { success: true, user: response.usuario };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async register(nome, email, senha, confirmarSenha) {
    try {
      const response = await api.post(CONFIG.ENDPOINTS.REGISTER, {
        nome,
        email,
        senha,
        confirmar_senha: confirmarSenha
      }, false);
      this.setSession(response.access_token, response.usuario);
      return { success: true, user: response.usuario };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async forgotPassword(email) {
    try {
      await api.post(CONFIG.ENDPOINTS.FORGOT_PASSWORD, { email }, false);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  logout() {
    this.clearSession();
    window.location.href = '/pages/login.html';
  }

  // Proteger rotas - redireciona se não autenticado
  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = '/pages/login.html';
      return false;
    }
    return true;
  }

  // Redireciona se já autenticado (para login/register)
  redirectIfAuth() {
    if (this.isAuthenticated()) {
      window.location.href = '/pages/dashboard.html';
      return true;
    }
    return false;
  }
}

// Instância global
const auth = new AuthManager();
