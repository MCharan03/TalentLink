// Main JavaScript for Smart Resume Analyzer

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Initialize Feather Icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // 2. Theme Toggle Logic (Persist choice)
    const themeToggle = document.getElementById('theme-toggle-btn');
    if (themeToggle) {
        const currentTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', currentTheme);
        updateThemeIcon(currentTheme);

        themeToggle.addEventListener('click', () => {
            let theme = document.documentElement.getAttribute('data-theme');
            let newTheme = theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        const iconEl = document.getElementById('theme-toggle-icon') || themeToggle.querySelector('span');

        // If current theme is dark, show "sun" (action: switch to light).
        // If current theme is light, show "moon" (action: switch to dark).
        const nextTheme = theme === 'dark' ? 'light' : 'dark';
        const nextIcon = nextTheme === 'light' ? 'sun' : 'moon';

        if (iconEl) iconEl.setAttribute('data-feather', nextIcon);

        themeToggle.setAttribute('aria-label', `Switch to ${nextTheme} theme`);
        themeToggle.setAttribute('title', `Switch to ${nextTheme} theme`);

        if (typeof feather !== 'undefined') feather.replace();
    }

    // 3. Assemble Animation Observer
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.visibility = 'visible';
                entry.target.classList.add('assemble-active');
                
                // If it's a grid container, stagger children manually if CSS didn't catch it
                if(entry.target.classList.contains('assemble-grid')) {
                    const children = entry.target.children;
                    Array.from(children).forEach((child, index) => {
                        child.style.animationDelay = `${index * 0.1}s`;
                        child.classList.add('anim-up');
                    });
                }
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Target elements
    const animatedElements = document.querySelectorAll('.animate-in, .assemble-in, .assemble-grid, .chart-container-animate');
    animatedElements.forEach(el => {
        // el.style.visibility = 'hidden'; // Avoid flash of unstyled content
        // Better to handle opacity in CSS with .assemble-in
        observer.observe(el);
    });

    // 4. Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

});
