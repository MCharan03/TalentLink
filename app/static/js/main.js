document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeText = document.getElementById('theme-text');
    const themeIcon = themeToggleBtn ? themeToggleBtn.querySelector('span') : null;
    const themeStyle = document.getElementById('theme-style');
    const lightTheme = themeStyle.dataset.lightTheme;
    const darkTheme = themeStyle.dataset.darkTheme;

    // Function to set the theme
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            themeStyle.setAttribute('href', darkTheme);
            if (themeText) themeText.textContent = 'Dark';
            if (themeIcon) themeIcon.setAttribute('data-feather', 'moon');
        } else {
            themeStyle.setAttribute('href', lightTheme);
            if (themeText) themeText.textContent = 'Light';
            if (themeIcon) themeIcon.setAttribute('data-feather', 'sun');
        }
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    };

    // Apply the saved theme on page load
    const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark theme
    applyTheme(savedTheme);

    // Add event listener to the theme toggle button
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            let currentTheme = localStorage.getItem('theme') || 'dark';
            let newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Initialize feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
});
