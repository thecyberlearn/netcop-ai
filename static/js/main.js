// API Configuration
const API_BASE = '/api';
const TOKEN_KEY = 'auth_token';

// API Client
class APIClient {
    constructor() {
        this.token = localStorage.getItem(TOKEN_KEY);
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        if (this.token) {
            config.headers['Authorization'] = `Token ${this.token}`;
        }

        // Add CSRF token if available
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
        }

        try {
            const response = await fetch(url, config);
            
            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = { error: await response.text() };
            }

            if (!response.ok) {
                // Handle validation errors
                if (data && typeof data === 'object') {
                    const errorMessages = [];
                    for (const [field, errors] of Object.entries(data)) {
                        if (Array.isArray(errors)) {
                            errorMessages.push(`${field}: ${errors.join(', ')}`);
                        } else {
                            errorMessages.push(`${field}: ${errors}`);
                        }
                    }
                    if (errorMessages.length > 0) {
                        throw new Error(errorMessages.join('\n'));
                    }
                }
                throw new Error(data.error || data.detail || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint);
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem(TOKEN_KEY, token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem(TOKEN_KEY);
    }
}

// Global API client
const api = new APIClient();

// Authentication
async function login(email, password) {
    try {
        const data = await api.post('/auth/login/', { email, password });
        api.setToken(data.token);
        return data;
    } catch (error) {
        throw error;
    }
}

async function register(email, password, passwordConfirm) {
    try {
        const data = await api.post('/auth/register/', {
            email,
            password,
            password_confirm: passwordConfirm,
        });
        api.setToken(data.token);
        return data;
    } catch (error) {
        throw error;
    }
}

function logout() {
    api.clearToken();
    window.location.href = '/';
}

// UI Helpers - Minimal Toast System
function showMessage(message, type = 'success') {
    // Only show critical messages as toasts
    if (type === 'error' || message.toLowerCase().includes('insufficient') || message.toLowerCase().includes('unavailable') || message.toLowerCase().includes('failed') || message.toLowerCase().includes('unable to connect')) {
        showToast(message, type);
    }
    // Success messages are handled by visual feedback (balance animation, etc.)
}

function showToast(message, type = 'error') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(toastContainer);
    }

    // Create toast
    const toast = document.createElement('div');
    const isError = type === 'error';
    toast.style.cssText = `
        background: ${isError ? '#ef4444' : '#10b981'};
        color: white;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 500;
        line-height: 1.4;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateX(400px);
        transition: transform 0.3s ease;
        pointer-events: auto;
        max-width: 380px;
        word-wrap: break-word;
        white-space: normal;
        hyphens: auto;
    `;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Slide in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

function showLoading(element) {
    const original = element.innerHTML;
    element.innerHTML = '<span class="loading"></span> Loading...';
    element.disabled = true;
    return () => {
        element.innerHTML = original;
        element.disabled = false;
    };
}

// Form handling
function handleFormSubmit(formSelector, submitHandler) {
    const form = document.querySelector(formSelector);
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const hideLoading = showLoading(submitBtn);

        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            // Remove CSRF token from API data
            delete data.csrfmiddlewaretoken;
            await submitHandler(data);
        } catch (error) {
            showMessage(error.message, 'error');
        } finally {
            hideLoading();
        }
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

// Check authentication
function isAuthenticated() {
    return !!localStorage.getItem(TOKEN_KEY);
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}

// Agent execution functions
async function executeAgent(agentSlug, inputData) {
    try {
        const response = await api.post('/agents/execute/', {
            agent_slug: agentSlug,
            input_data: inputData
        });
        return response;
    } catch (error) {
        throw error;
    }
}

async function getAgentExecutions(page = 1) {
    try {
        const response = await api.get(`/agents/executions/?page=${page}`);
        return response;
    } catch (error) {
        throw error;
    }
}

async function getExecutionDetail(executionId) {
    try {
        const response = await api.get(`/agents/executions/${executionId}/`);
        return response;
    } catch (error) {
        throw error;
    }
}