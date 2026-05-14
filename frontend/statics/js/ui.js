// ============================================
// UI UTILITIES - Alertas, Modais, Loading
// ============================================

class UIManager {
  constructor() {
    this.alertsContainer = null;
  }

  // Alertas
  showAlert(message, type = 'info', duration = 5000) {
    const container = document.getElementById('alerts-container') || document.body;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
      <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        ${type === 'success' 
          ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>'
          : type === 'error'
          ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>'
          : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
        }
      </svg>
      <span>${message}</span>
    `;

    container.insertBefore(alert, container.firstChild);

    if (duration > 0) {
      setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 300);
      }, duration);
    }

    return alert;
  }

  showSuccess(message) {
    return this.showAlert(message, 'success');
  }

  showError(message) {
    return this.showAlert(message, 'error');
  }

  showInfo(message) {
    return this.showAlert(message, 'info');
  }

  // Loading
  showLoading(element, text = 'Carregando...') {
    const originalContent = element.innerHTML;
    element.disabled = true;
    element.innerHTML = `
      <div class="spinner" style="width: 16px; height: 16px; border-width: 2px; display: inline-block; vertical-align: middle; margin-right: 8px;"></div>
      ${text}
    `;
    return () => {
      element.disabled = false;
      element.innerHTML = originalContent;
    };
  }

  // Modal
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  // Formatação
  formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  }

  formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
  }

  formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('pt-BR');
  }

  // Status badge HTML
  getStatusBadge(status) {
    const statusMap = {
      'conciliado': { class: 'badge-conciliado', label: 'Conciliado', color: '#10b981' },
      'nao_conciliado': { class: 'badge-nao-conciliado', label: 'Não Conciliado', color: '#ef4444' },
      'pendente': { class: 'badge-pendente', label: 'Pendente', color: '#f59e0b' }
    };

    const config = statusMap[status] || statusMap['pendente'];

    return `
      <span class="badge ${config.class}">
        <span class="badge-dot" style="background: ${config.color}"></span>
        ${config.label}
      </span>
    `;
  }
}

// Instância global
const ui = new UIManager();
