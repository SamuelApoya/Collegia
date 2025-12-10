// ===================================
// NOTIFICATION TOAST SYSTEM
// ===================================

class NotificationToastManager {
    constructor() {
        this.container = null;
        this.checkInterval = null;
        this.init();
    }

    init() {
        // Create toast container
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);

        // Start checking for notifications every 30 seconds
        this.startChecking();
        
        // Check immediately on page load
        this.checkForNewNotifications();
    }

    startChecking() {
        // Check every 15 seconds for new notifications (more frequent = less missed)
        this.checkInterval = setInterval(() => {
            this.checkForNewNotifications();
        }, 15000); // 15 seconds - faster checking means no missed notifications
    }

    async checkForNewNotifications() {
        try {
            const response = await fetch('/api/notifications/check');
            const data = await response.json();

            if (data.count > 0) {
                data.notifications.forEach(notification => {
                    this.showToast(notification);
                    // Mark as read AFTER showing
                    this.markAsRead(notification.id);
                });
            }
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }

    async markAsRead(notificationId) {
        try {
            await fetch('/api/notifications/mark-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: notificationId })
            });
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    showToast(notification) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${notification.type}`;
        
        // Get icon based on notification type
        const icon = this.getIcon(notification.type);
        
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-message">${notification.message}</div>
                <div class="toast-time">${notification.timestamp}</div>
            </div>
            <button class="toast-close" aria-label="Close">×</button>
        `;

        // Add to container
        this.container.appendChild(toast);

        // Close button functionality
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.removeToast(toast);
        });

        // Auto-remove after 12 seconds (longer so you don't miss it)
        setTimeout(() => {
            if (toast.parentElement) {
                this.removeToast(toast);
            }
        }, 12000);

        // NO SOUND - it's annoying on every notification
    }

    removeToast(toast) {
        toast.classList.add('removing');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }

    getIcon(type) {
        const icons = {
            'meeting_reminder': '📅',
            'meeting_reminder_12hr': '⚡',
            'booking_confirmation': '✅',
            'new_availability': '🔔'
        };
        return icons[type] || '🔔';
    }

    playNotificationSound() {
        // Optional: Play a subtle notification sound
        // You can add an audio element here if desired
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZUQ0PVare67ZXGQ1BmN70xHInBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwOUKXh8bllHQU2j9Xy0H8pBSl+zPLaizsIGGS56+ibUgwO');
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Ignore errors if sound can't play
            });
        } catch (error) {
            // Silent fail for sound
        }
    }

    destroy() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
        if (this.container && this.container.parentElement) {
            this.container.remove();
        }
    }
}

// Initialize toast manager when DOM is ready
let toastManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        toastManager = new NotificationToastManager();
        window.toastManager = toastManager; // Make it globally accessible
    });
} else {
    toastManager = new NotificationToastManager();
    window.toastManager = toastManager; // Make it globally accessible
}

// ===================================
// EXISTING APP.JS CODE BELOW
// ===================================

// Stats animation on homepage
document.addEventListener('DOMContentLoaded', function() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent);
        const duration = 1500;
        const increment = target / (duration / 16);
        let current = 0;
        
        const updateNumber = () => {
            current += increment;
            if (current < target) {
                stat.textContent = Math.floor(current);
                requestAnimationFrame(updateNumber);
            } else {
                stat.textContent = target;
            }
        };
        
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                updateNumber();
                observer.disconnect();
            }
        });
        
        observer.observe(stat);
    });

    // Card hover effects
    const cards = document.querySelectorAll('.stat-card, .action-card, .session-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Role selection cards
    const roleCards = document.querySelectorAll('.role-card');
    roleCards.forEach(card => {
        card.addEventListener('click', function() {
            roleCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            
            const roleInput = document.getElementById('role-input');
            if (roleInput) {
                roleInput.value = this.dataset.role;
            }
        });
    });

    // Announcement bar close functionality
    const announcementClose = document.querySelector('.announcement-close');
    if (announcementClose) {
        // Check if announcement was previously closed
        const announcementId = announcementClose.dataset.announcementId || 'default';
        const isClosed = localStorage.getItem(`announcement_${announcementId}_closed`);
        
        if (isClosed === 'true') {
            const announcement = announcementClose.closest('.announcement-bar');
            if (announcement) {
                announcement.style.display = 'none';
            }
        }
        
        // Add click handler
        announcementClose.addEventListener('click', function() {
            const announcement = this.closest('.announcement-bar');
            const announcementId = this.dataset.announcementId || 'default';
            
            if (announcement) {
                announcement.style.opacity = '0';
                announcement.style.transform = 'translateY(-20px)';
                
                setTimeout(() => {
                    announcement.style.display = 'none';
                    // Remember that user closed this announcement
                    localStorage.setItem(`announcement_${announcementId}_closed`, 'true');
                }, 300);
            }
        });
    }
});