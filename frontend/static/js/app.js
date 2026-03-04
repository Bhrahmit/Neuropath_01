/**
 * CareerAI - App.js
 * ====================
 * Shared utility functions used across all pages:
 * - API base URL
 * - Auth token helpers
 * - Common UI utilities
 */

// API base URL - adjust if backend runs on different port
window.API_BASE = '';

/**
 * Get stored auth token
 */
function getToken() {
  return localStorage.getItem('careerai_token');
}

/**
 * Get stored user object
 */
function getUser() {
  return JSON.parse(localStorage.getItem('careerai_user') || 'null');
}

/**
 * Make an authenticated API request
 * @param {string} endpoint - API endpoint (e.g. '/api/skill-gap')
 * @param {object} options - fetch options
 */
async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };
  
  const response = await fetch(`${window.API_BASE}${endpoint}`, {
    ...options,
    headers
  });
  
  if (response.status === 401) {
    localStorage.removeItem('careerai_token');
    localStorage.removeItem('careerai_user');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  
  return response;
}

/**
 * Logout function - clears auth and redirects to login
 */
function logout() {
  localStorage.removeItem('careerai_token');
  localStorage.removeItem('careerai_user');
  window.location.href = '/';
}

/**
 * Format a match score (0-1 float) to a percentage string
 */
function formatScore(score) {
  return `${Math.round(score * 100)}%`;
}

/**
 * Get a Bootstrap color class based on match score
 */
function scoreColorClass(score) {
  const pct = score * 100;
  if (pct >= 70) return 'success';
  if (pct >= 40) return 'warning';
  return 'danger';
}

/**
 * Get a CSS class for candidate card styling based on score
 */
function candidateScoreClass(score) {
  const pct = score * 100;
  if (pct >= 70) return 'score-high';
  if (pct >= 40) return 'score-mid';
  return 'score-low';
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'info') {
  // Create toast container if not exists
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const colors = { success: '#22c55e', error: '#ef4444', warning: '#f59e0b', info: '#6366f1' };
  
  const toast = document.createElement('div');
  toast.style.cssText = `
    background: #1e293b;
    border: 1px solid ${colors[type]}40;
    border-left: 3px solid ${colors[type]};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.875rem;
    color: #e2e8f0;
    max-width: 320px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    animation: slideInRight 0.3s ease;
  `;
  toast.innerHTML = `${icons[type] || ''} ${message}`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight { from { opacity:0; transform:translateX(30px); } to { opacity:1; transform:translateX(0); } }
  @keyframes fadeOut { from { opacity:1; } to { opacity:0; transform:translateX(30px); } }
`;
document.head.appendChild(style);

/**
 * Protect dashboard pages - redirect to login if not authenticated
 */
function requireAuth(requiredRole = null) {
  const token = getToken();
  const user = getUser();
  
  if (!token || !user) {
    window.location.href = '/login';
    return false;
  }
  
  if (requiredRole && user.role !== requiredRole) {
    if (user.role === 'recruiter') {
      window.location.href = '/recruiter';
    } else {
      window.location.href = '/dashboard';
    }
    return false;
  }
  
  return true;
}

/**
 * Toggle mobile sidebar
 */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}
