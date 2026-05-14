// ============================================
// SIDEBAR - Navegação e informações do usuário
// ============================================

class SidebarManager {
  constructor() {
    this.currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
  }

  render() {
    const user = auth.getUser();
    const initials = user?.nome ? user.nome.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'U';

    return `
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
            </svg>
            <span>ConciliaContábil</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <div class="nav-section">
            <div class="nav-section-title">Menu Principal</div>
            <a href="dashboard.html" class="nav-item ${this.isActive('dashboard.html')}">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
              </svg>
              Dashboard
            </a>
            <a href="upload.html" class="nav-item ${this.isActive('upload.html')}">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
              </svg>
              Upload de Planilha
            </a>
            <a href="consulta.html" class="nav-item ${this.isActive('consulta.html')}">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              Consulta Lançamentos
            </a>
            <a href="validacao.html" class="nav-item ${this.isActive('validacao.html')}">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              Validação
            </a>
          </div>
        </nav>

        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar">${initials}</div>
            <div class="user-details">
              <div class="user-name">${user?.nome || 'Usuário'}</div>
              <div class="user-email">${user?.email || ''}</div>
            </div>
            <button onclick="auth.logout()" class="nav-item" style="width: auto; padding: 8px;">
              <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
            </button>
          </div>
        </div>
      </aside>
    `;
  }

  isActive(page) {
    return this.currentPage === page ? 'active' : '';
  }

  init() {
    const sidebarContainer = document.getElementById('sidebar-container');
    if (sidebarContainer) {
      sidebarContainer.innerHTML = this.render();
    }
  }
}

const sidebar = new SidebarManager();
