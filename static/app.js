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

  // Subtle hover lift for cards
  document.querySelectorAll(".meeting-card, .quick-card, .stat-card").forEach(card => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-4px)";
      card.style.transition = "0.2s ease";
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0)";
    });
  });
});
