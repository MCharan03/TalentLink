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
        const icon = themeToggle.querySelector('span'); // feather icon
        if (theme === 'light') {
            // Switch to moon icon for dark mode toggle
            if(icon) icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
        } else {
            // Switch to sun icon
            if(icon) icon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
        }
        if(typeof feather !== 'undefined') feather.replace();
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
