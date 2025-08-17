/**
 * Notification system for ScraperV4
 * Handles displaying user notifications with different types and auto-dismissal
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.notifications = new Map();
        this.defaultDuration = 5000; // 5 seconds
        this.maxNotifications = 5;
    }

    init() {
        // Create notification container if it doesn't exist
        this.container = document.getElementById('notifications-container');
        if (!this.container) {
            this.container = this.createContainer();
        }
        
        console.log('Notification system initialized');
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notifications-container';
        container.className = 'notifications-container';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Show a notification
     * @param {Object} options - Notification options
     * @param {string} options.type - Type: 'success', 'error', 'warning', 'info'
     * @param {string} options.title - Notification title
     * @param {string} options.message - Notification message
     * @param {number} options.duration - Duration in ms (0 for persistent)
     * @param {boolean} options.closable - Whether notification can be closed manually
     */
    show(options) {
        const {
            type = 'info',
            title = '',
            message = '',
            duration = this.defaultDuration,
            closable = true
        } = options;

        // Generate unique ID
        const id = this.generateId();
        
        // Create notification element
        const notification = this.createNotification(id, type, title, message, closable);
        
        // Add to container
        this.container.appendChild(notification);
        
        // Store reference
        this.notifications.set(id, {
            element: notification,
            type,
            title,
            message,
            duration
        });

        // Remove oldest if too many
        this.enforceMaxNotifications();

        // Auto-dismiss if duration is set
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(id);
            }, duration);
        }

        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        return id;
    }

    createNotification(id, type, title, message, closable) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.dataset.id = id;

        // Get icon for type
        const icon = this.getIconForType(type);

        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="notification-text">
                    ${title ? `<div class="notification-title">${title}</div>` : ''}
                    <div class="notification-message">${message}</div>
                </div>
                ${closable ? `
                    <button class="notification-close" onclick="window.notifications.dismiss('${id}')">
                        <i class="fas fa-times"></i>
                    </button>
                ` : ''}
            </div>
        `;

        return notification;
    }

    getIconForType(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Dismiss a notification by ID
     */
    dismiss(id) {
        const notificationData = this.notifications.get(id);
        if (!notificationData) return;

        const element = notificationData.element;
        
        // Animate out
        element.classList.add('dismissing');
        
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            this.notifications.delete(id);
        }, 300);
    }

    /**
     * Dismiss all notifications
     */
    dismissAll() {
        this.notifications.forEach((_, id) => {
            this.dismiss(id);
        });
    }

    /**
     * Show success notification
     */
    success(title, message, duration) {
        return this.show({
            type: 'success',
            title,
            message,
            duration
        });
    }

    /**
     * Show error notification
     */
    error(title, message, duration = 0) {
        return this.show({
            type: 'error',
            title,
            message,
            duration // Error notifications are persistent by default
        });
    }

    /**
     * Show warning notification
     */
    warning(title, message, duration) {
        return this.show({
            type: 'warning',
            title,
            message,
            duration
        });
    }

    /**
     * Show info notification
     */
    info(title, message, duration) {
        return this.show({
            type: 'info',
            title,
            message,
            duration
        });
    }

    /**
     * Show loading notification
     */
    loading(message = 'Loading...') {
        return this.show({
            type: 'info',
            title: '',
            message: `<i class="fas fa-spinner fa-spin"></i> ${message}`,
            duration: 0,
            closable: false
        });
    }

    enforceMaxNotifications() {
        if (this.notifications.size > this.maxNotifications) {
            const oldestId = this.notifications.keys().next().value;
            this.dismiss(oldestId);
        }
    }

    generateId() {
        return `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get current notification count
     */
    getCount() {
        return this.notifications.size;
    }

    /**
     * Check if notification exists
     */
    exists(id) {
        return this.notifications.has(id);
    }
}

// Add CSS for notifications if not already present
function addNotificationStyles() {
    if (document.getElementById('notification-styles')) {
        return;
    }

    const styles = document.createElement('style');
    styles.id = 'notification-styles';
    styles.textContent = `
        .notification {
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease-out;
            margin-bottom: 0.5rem;
        }

        .notification.show {
            opacity: 1;
            transform: translateX(0);
        }

        .notification.dismissing {
            opacity: 0;
            transform: translateX(100%);
        }

        .notification-content {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }

        .notification-icon {
            color: currentColor;
            font-size: 1.25rem;
            margin-top: 0.125rem;
        }

        .notification-text {
            flex: 1;
        }

        .notification-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .notification-message {
            font-size: 0.875rem;
            line-height: 1.4;
        }

        .notification-close {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 1rem;
            padding: 0.25rem;
            border-radius: var(--radius-sm);
            transition: all 0.2s;
        }

        .notification-close:hover {
            background: rgba(0, 0, 0, 0.1);
            color: var(--text-primary);
        }

        .notification.success .notification-icon {
            color: var(--success-color);
        }

        .notification.error .notification-icon {
            color: var(--error-color);
        }

        .notification.warning .notification-icon {
            color: var(--warning-color);
        }

        .notification.info .notification-icon {
            color: var(--primary-color);
        }
    `;
    document.head.appendChild(styles);
}

// Initialize notification system
document.addEventListener('DOMContentLoaded', () => {
    addNotificationStyles();
    window.notifications = new NotificationSystem();
});

// Global notification shortcuts
window.showNotification = (type, title, message, duration) => {
    if (window.notifications) {
        return window.notifications.show({ type, title, message, duration });
    }
};

window.showSuccess = (title, message, duration) => {
    if (window.notifications) {
        return window.notifications.success(title, message, duration);
    }
};

window.showError = (title, message, duration) => {
    if (window.notifications) {
        return window.notifications.error(title, message, duration);
    }
};

window.showWarning = (title, message, duration) => {
    if (window.notifications) {
        return window.notifications.warning(title, message, duration);
    }
};

window.showInfo = (title, message, duration) => {
    if (window.notifications) {
        return window.notifications.info(title, message, duration);
    }
};

window.showLoading = (message) => {
    if (window.notifications) {
        return window.notifications.loading(message);
    }
};