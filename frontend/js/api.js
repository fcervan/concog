// ============================================
// CLIENTE HTTP - Wrapper para fetch
// ============================================

class APIClient {
  constructor() {
    this.baseURL = CONFIG.API_BASE_URL;
  }

  getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
  }

  getHeaders(requireAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    if (requireAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const requireAuth = options.requireAuth !== false;

    const config = {
      ...options,
      headers: {
        ...this.getHeaders(requireAuth),
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        const isAuthEndpoint = endpoint.startsWith('/auth/');
        if (!isAuthEndpoint) {
          localStorage.removeItem(CONFIG.TOKEN_KEY);
          localStorage.removeItem(CONFIG.USER_KEY);
          window.location.href = 'login.html';
        }
        const error = await response.json().catch(() => ({ detail: 'Não autorizado' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Métodos HTTP
  get(endpoint, requireAuth = true) {
    return this.request(endpoint, { method: 'GET', requireAuth });
  }

  post(endpoint, data, requireAuth = true) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      requireAuth
    });
  }

  put(endpoint, data, requireAuth = true) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      requireAuth
    });
  }

  delete(endpoint, requireAuth = true) {
    return this.request(endpoint, { method: 'DELETE', requireAuth });
  }

  // Upload de arquivo
  async uploadFile(endpoint, file, onProgress = null) {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getToken();

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', file);

      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            onProgress(percent);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => reject(new Error('Upload failed')));

      xhr.open('POST', url);
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      xhr.send(formData);
    });
  }
}

// Instância global
const api = new APIClient();
