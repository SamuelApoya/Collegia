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
    
    // Alert auto-dismiss (no need to create close button, it's already in HTML)
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto-dismiss after 5 seconds
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
    
    // Hamburger Menu
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });

        document.addEventListener('click', (e) => {
            if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }

    // Typing animation for quotes
    const typingElement = document.getElementById('typing-quote');
    
    if (typingElement) {
        const quotes = [
            "Good advising is about listening, not just talking.",
            "Every student's journey is unique and deserves personalized guidance.",
            "Effective advising builds bridges between ambition and achievement.",
            "Academic success starts with strong mentor-student relationships.",
            "The best advisors help students discover their own path.",
            "Regular advising sessions keep students on track to graduate.",
            "Proactive advising prevents problems before they arise.",
            "Great advisors empower students to make informed decisions.",
            "Academic advising is an investment in student success.",
            "Good advising transforms confusion into clarity."
        ];
        
        let quoteIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let typingSpeed = 80;
        
        function typeQuote() {
            const currentQuote = quotes[quoteIndex];
            
            if (isDeleting) {
                typingElement.textContent = currentQuote.substring(0, charIndex - 1);
                charIndex--;
                typingSpeed = 40;
            } else {
                typingElement.textContent = currentQuote.substring(0, charIndex + 1);
                charIndex++;
                typingSpeed = 80;
            }
            
            if (!isDeleting && charIndex === currentQuote.length) {
                // Pause at end of quote
                typingSpeed = 3000;
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                // Move to next quote
                isDeleting = false;
                quoteIndex = (quoteIndex + 1) % quotes.length;
                typingSpeed = 500;
            }
            
            setTimeout(typeQuote, typingSpeed);
        }
        
        // Start typing animation
        typeQuote();
    }
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