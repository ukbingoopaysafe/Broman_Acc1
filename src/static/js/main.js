// Main JavaScript file for BroMan Accounting System

// Global variables
let currentUser = null;
let userPermissions = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status
    checkAuthStatus();

    // Initialize tooltips
    initializeTooltips();

    // Initialize form validation
    initializeFormValidation();

    // Add loading states to forms
    addLoadingStates();
});

// Authentication functions
async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/check-auth');
        const data = await response.json();

        if (data.authenticated) {
            currentUser = data.user;
            await loadUserPermissions();
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
    }
}

async function loadUserPermissions() {
    try {
        const response = await fetch('/dashboard/api/user-permissions');
        const data = await response.json();

        if (!data.error) {
            userPermissions = data.permissions;
            updateUIBasedOnPermissions();
        }
    } catch (error) {
        console.error('Error loading user permissions:', error);
    }
}

function updateUIBasedOnPermissions() {
    // Hide/show elements based on permissions
    document.querySelectorAll('[data-permission]').forEach(element => {
        const requiredPermission = element.getAttribute('data-permission');
        if (!hasPermission(requiredPermission)) {
            element.style.display = 'none';
        }
    });
}

function hasPermission(permission) {
    return userPermissions.includes(permission) || (currentUser && currentUser.role && currentUser.role.name === 'Admin');
}

// Logout function
async function logout() {
    if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
        try {
            const response = await fetch('/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                window.location.href = '/auth/login';
            } else {
                showAlert('حدث خطأ في تسجيل الخروج', 'danger');
            }
        } catch (error) {
            console.error('Error during logout:', error);
            showAlert('حدث خطأ في الاتصال', 'danger');
        }
    }
}

// UI Helper functions
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();

    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="bi bi-${getAlertIcon(type)}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    alertContainer.insertAdjacentHTML('beforeend', alertHTML);

    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showLoading(element, text = 'جاري التحميل...') {
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        ${text}
    `;
    element.disabled = true;
}

function hideLoading(element) {
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
        element.innerHTML = originalContent;
        element.removeAttribute('data-original-content');
    }
    element.disabled = false;
}

// Form validation
function initializeFormValidation() {
    // Add Bootstrap validation classes
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function addLoadingStates() {
    // Add loading states to form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && form.checkValidity()) {
                showLoading(submitButton, 'جاري المعالجة...');
            }
        });
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Utility functions
function formatCurrency(amount, currency = 'EGP') {
    // Handle null, undefined, and string 'None' values
    if (amount === null || amount === undefined || amount === 'None' || amount === '') {
        amount = 0;
    }

    // Convert to number and handle NaN
    const numAmount = Number(amount);
    if (isNaN(numAmount)) {
        amount = 0;
    } else {
        amount = numAmount;
    }

    // English numerals, hide trailing zeros (up to 2 decimals)
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount);
}

function formatNumber(value, options = {}) {
    const { maximumFractionDigits = 2 } = options;
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits
    }).format(Number(value || 0));
}

function formatDate(dateString, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    return new Date(dateString).toLocaleDateString('en-GB', { ...defaultOptions, ...options });
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('en-GB');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const mergedOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Data table helpers
function createDataTable(tableId, options = {}) {
    const defaultOptions = {
        responsive: true,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/ar.json'
        },
        pageLength: 25,
        order: [[0, 'desc']]
    };

    return $(tableId).DataTable({ ...defaultOptions, ...options });
}

// Export functions
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    downloadFile(csv, filename + '.csv', 'text/csv');
}

function exportToExcel(data, filename) {
    // This would require a library like SheetJS
    console.log('Excel export not implemented yet');
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';

    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');

    return csvContent;
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

// Print helpers
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>طباعة</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body { font-family: Arial, sans-serif; direction: rtl; }
                    @media print { .no-print { display: none !important; } }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Local storage helpers
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return defaultValue;
    }
}

// Theme helpers
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    saveToLocalStorage('theme', newTheme);
}

function loadTheme() {
    const savedTheme = loadFromLocalStorage('theme', 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
}

// Initialize theme on load
loadTheme();

// Enhanced UI Interactions and Animations
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add hover effects to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'all 0.3s ease';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add fade-in animation to elements as they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card, .table, .alert').forEach(el => {
        observer.observe(el);
    });

    // Enhanced form interactions
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // Add loading animation to navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') && !this.getAttribute('href').startsWith('#')) {
                const spinner = document.createElement('i');
                spinner.className = 'bi bi-hourglass-split ms-2';
                this.appendChild(spinner);

                setTimeout(() => {
                    spinner.remove();
                }, 2000);
            }
        });
    });
});

// Enhanced notification system
function showNotification(title, message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-header">
            <strong>${title}</strong>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <div class="notification-body">${message}</div>
    `;

    const container = document.getElementById('notificationContainer') || createNotificationContainer();
    container.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);

    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notificationContainer';
    container.className = 'notification-container';
    document.body.appendChild(container);
    return container;
}

// Enhanced data visualization helpers
function createChart(canvasId, type, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        family: 'Tajawal, Cairo, sans-serif'
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        family: 'Tajawal, Cairo, sans-serif'
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        family: 'Tajawal, Cairo, sans-serif'
                    }
                }
            }
        }
    };

    return new Chart(ctx, {
        type: type,
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

// Enhanced search functionality
function initializeSearch(inputId, targetSelector, searchFields = []) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;

    const searchFunction = debounce((query) => {
        const targets = document.querySelectorAll(targetSelector);
        const searchTerm = query.toLowerCase().trim();

        targets.forEach(target => {
            let shouldShow = false;

            if (searchFields.length === 0) {
                // Search in all text content
                shouldShow = target.textContent.toLowerCase().includes(searchTerm);
            } else {
                // Search in specific fields
                shouldShow = searchFields.some(field => {
                    const element = target.querySelector(`[data-field="${field}"]`);
                    return element && element.textContent.toLowerCase().includes(searchTerm);
                });
            }

            target.style.display = shouldShow ? '' : 'none';
        });
    }, 300);

    searchInput.addEventListener('input', (e) => searchFunction(e.target.value));
}

// Enhanced modal helpers
function showModal(modalId, data = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    // Populate modal with data
    Object.keys(data).forEach(key => {
        const element = modal.querySelector(`[data-field="${key}"]`);
        if (element) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.value = data[key];
            } else {
                element.textContent = data[key];
            }
        }
    });

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    return bsModal;
}

// Enhanced error handling
function handleError(error, context = '') {
    console.error(`Error in ${context}:`, error);
    
    let message = 'حدث خطأ غير متوقع';
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }

    showAlert(message, 'danger');
}

// Performance monitoring
function measurePerformance(name, fn) {
    return async function(...args) {
        const start = performance.now();
        try {
            const result = await fn.apply(this, args);
            const end = performance.now();
            console.log(`${name} took ${end - start} milliseconds`);
            return result;
        } catch (error) {
            const end = performance.now();
            console.log(`${name} failed after ${end - start} milliseconds`);
            throw error;
        }
    };
}

// Add CSS for enhanced animations
const enhancedStyles = `
<style>
.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1060;
    max-width: 400px;
}

.notification {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    margin-bottom: 10px;
    transform: translateX(100%);
    transition: all 0.3s ease;
    border-left: 4px solid #007bff;
}

.notification.show {
    transform: translateX(0);
}

.notification-success {
    border-left-color: #28a745;
}

.notification-danger {
    border-left-color: #dc3545;
}

.notification-warning {
    border-left-color: #ffc107;
}

.notification-header {
    padding: 12px 16px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
}

.notification-body {
    padding: 8px 16px 12px;
    color: #666;
}

.form-control:focus {
    box-shadow: 0 0 0 0.2rem rgba(30, 58, 138, 0.25);
    border-color: var(--navy-primary);
}

.focused {
    transform: scale(1.02);
    transition: transform 0.2s ease;
}
</style>
`;

// Inject enhanced styles
document.head.insertAdjacentHTML('beforeend', enhancedStyles);
