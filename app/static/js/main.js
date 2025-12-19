const themeToggle = document.getElementById('theme-toggle');
const themeStyle = document.getElementById('theme-style');
const lightTheme = themeStyle.dataset.lightTheme;
const darkTheme = themeStyle.dataset.darkTheme;

themeToggle.addEventListener('click', () => {
    if (themeStyle.getAttribute('href') === lightTheme) {
        themeStyle.setAttribute('href', darkTheme);
    } else {
        themeStyle.setAttribute('href', lightTheme);
    }
});

const generateJdBtn = document.getElementById('generate-jd-btn');
if (generateJdBtn) {
    generateJdBtn.addEventListener('click', () => {
        const jobTitle = document.getElementById('job-title').value;
        if (!jobTitle) {
            alert('Please enter a job title first.');
            return;
        }

        fetch('/admin/generate_jd', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: jobTitle }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.description) {
                document.getElementById('job-description').value = data.description;
            } else {
                alert('Error generating job description.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while generating the job description.');
        });
    });
}
