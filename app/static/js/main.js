document.addEventListener('DOMContentLoaded', function () {

    // Profile picture preview
    const profileInput = document.getElementById('profile_picture');
    const profilePreview = document.getElementById('profile-preview');

    if (profileInput && profilePreview) {
        profileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                profilePreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    // Flash alert auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // Notification dismiss behavior
    const notifications = document.querySelectorAll('.notification-card');
    notifications.forEach(notification => {
        const closeBtn = document.createElement('div');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '×';

        closeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            notification.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => notification.remove(), 400);
        });

        notification.appendChild(closeBtn);
        notification.style.cursor = 'pointer';

        notification.addEventListener('click', function () {
            notification.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => notification.remove(), 400);
        });

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => notification.remove(), 400);
        }, 180000);
    });

    // Navbar logo rotation animation
    const logo = document.querySelector('.navbar-logo');

    if (logo) {
        // Initial rotate shortly after load
        setTimeout(() => {
            logo.classList.add('rotate');
            setTimeout(() => logo.classList.remove('rotate'), 1000);
        }, 800);

        // Rotate every 60 seconds
        setInterval(() => {
            logo.classList.add('rotate');
            setTimeout(() => logo.classList.remove('rotate'), 1000);
        }, 60000);
    }


    // Confirmation modal (global, from base.html)
    let pendingForm = null;

    document.addEventListener('click', function (e) {
        const trigger = e.target.closest('.js-confirm');
        if (!trigger) return;

        e.preventDefault();
        pendingForm = trigger.closest('form');

        const title = trigger.dataset.title || 'Confirm action';
        const message = trigger.dataset.message || 'Are you sure you want to continue?';

        document.getElementById('confirmTitle').textContent = title;
        document.getElementById('confirmMessage').textContent = message;
        document.getElementById('confirmModal').classList.remove('hidden');
    });

    const confirmCancel = document.getElementById('confirmCancel');
    const confirmOk = document.getElementById('confirmOk');

    if (confirmCancel && confirmOk) {
        confirmCancel.addEventListener('click', () => {
            pendingForm = null;
            document.getElementById('confirmModal').classList.add('hidden');
        });

        confirmOk.addEventListener('click', () => {
            if (pendingForm) pendingForm.submit();
        });
    }

    // Hamburger menu
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

    // Typing animation
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
                typingSpeed = 3000;
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                quoteIndex = (quoteIndex + 1) % quotes.length;
                typingSpeed = 500;
            }

            setTimeout(typeQuote, typingSpeed);
        }

        typeQuote();
    }
});
