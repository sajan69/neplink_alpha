document.addEventListener('DOMContentLoaded', (event) => {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const body = document.body;

    // Check if user preference is stored
    const darkMode = localStorage.getItem('darkMode');

    // Set initial state
    if (darkMode === 'enabled') {
        html.classList.add('dark-mode');
        body.classList.add('dark-mode');
        if (themeToggle) themeToggle.checked = true;
    }

    if (themeToggle) {
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                html.classList.add('dark-mode');
                body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'enabled');
            } else {
                html.classList.remove('dark-mode');
                body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', null);
            }
        });
    }
});