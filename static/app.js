document.addEventListener('DOMContentLoaded', function() {
    
    const profileInput = document.getElementById('profile_picture');
    const profilePreview = document.getElementById('profile-preview');
    
    if (profileInput && profilePreview) {
        profileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = document.createElement('div');
        closeBtn.className = 'alert-close';
        closeBtn.innerHTML = '×';
        closeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            alert.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => alert.remove(), 400);
        });
        alert.appendChild(closeBtn);
        
        alert.style.cursor = 'pointer';
        alert.addEventListener('click', function() {
            this.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => this.remove(), 400);
        });
        
        setTimeout(() => {
            alert.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
    
    const notifications = document.querySelectorAll('.notification-card');
    notifications.forEach(notification => {
        const closeBtn = document.createElement('div');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '×';
        closeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notification.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => notification.remove(), 400);
        });
        notification.appendChild(closeBtn);
        
        notification.style.cursor = 'pointer';
        notification.addEventListener('click', function() {
            this.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => this.remove(), 400);
        });
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => notification.remove(), 400);
        }, 180000);
    });
    
    document.querySelectorAll('form[action*="delete-slot"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            showConfirmation(
                'Are you sure you want to delete this availability slot?',
                () => form.submit()
            );
        });
    });
    
    document.querySelectorAll('form[action*="cancel-meeting"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            showConfirmation(
                'Are you sure you want to cancel this meeting? The student will be notified.',
                () => form.submit()
            );
        });
    });
});

function showConfirmation(message, onConfirm) {
    const backdrop = document.createElement('div');
    backdrop.className = 'confirmation-backdrop';
    
    const modal = document.createElement('div');
    modal.className = 'confirmation-modal';
    modal.innerHTML = `
        <div class="confirmation-content">
            <p class="confirmation-message">${message}</p>
            <div class="confirmation-buttons">
                <button type="button" class="btn-cancel">Cancel</button>
                <button type="button" class="btn-confirm">OK</button>
            </div>
        </div>
    `;
    
    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);
    
    setTimeout(() => {
        backdrop.style.opacity = '1';
        modal.style.transform = 'scale(1)';
    }, 10);
    
    const cancelBtn = modal.querySelector('.btn-cancel');
    const confirmBtn = modal.querySelector('.btn-confirm');
    
    function closeModal() {
        backdrop.style.opacity = '0';
        modal.style.transform = 'scale(0.9)';
        setTimeout(() => backdrop.remove(), 300);
    }
    
    cancelBtn.addEventListener('click', function() {
        closeModal();
    });
    
    confirmBtn.addEventListener('click', function() {
        closeModal();
        setTimeout(onConfirm, 100);
    });
    
    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
            closeModal();
        }
    });
}