// ============================================
// CONFIGURAÇÃO GLOBAL
// ============================================

const CONFIG = {
  API_BASE_URL: 'http://localhost:8000',
  TOKEN_KEY: 'cc_token',
  USER_KEY: 'cc_user',

  // Rotas da API
  ENDPOINTS: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    CONFIGURAR_PARSER: '/auth/configurar-parser',
    PARSERS_DISPONIVEIS: '/auth/parsers-disponiveis',
    UPLOAD: '/api/upload',
    UPLOAD_HISTORY: '/api/upload/history',
    LANCAMENTOS: '/api/lancamentos',
    DASHBOARD: '/api/dashboard/stats'
  }
};

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
