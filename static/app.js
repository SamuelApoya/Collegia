// Animated stat counters
document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".stat-value");

  counters.forEach(counter => {
    const target = parseInt(counter.innerText);
    if (isNaN(target)) return;

    let current = 0;
    const increment = Math.max(1, Math.floor(target / 30));

    const update = () => {
      current += increment;
      if (current >= target) {
        counter.innerText = target;
      } else {
        counter.innerText = current;
        requestAnimationFrame(update);
      }
    };

    update();
  });

  // Hover effects for cards
  document.querySelectorAll(".meeting-card, .quick-card, .stat-card, .session-card").forEach(card => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-4px)";
      card.style.transition = "all 0.3s ease";
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0)";
    });
  });

  // Role selection functionality
  const roleOptions = document.querySelectorAll(".role-option");
  const roleInput = document.querySelector("input[name='role']");

  roleOptions.forEach(option => {
    option.addEventListener("click", () => {
      roleOptions.forEach(opt => opt.classList.remove("selected"));
      option.classList.add("selected");
      if (roleInput) {
        roleInput.value = option.dataset.role;
      }
    });
  });
});