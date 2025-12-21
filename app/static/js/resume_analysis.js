document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysis-form');
    if (!form) return;

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const spinner = document.getElementById('spinner');
        const buttonText = document.getElementById('button-text');
        const submitButton = form.querySelector('button[type="submit"]');
        const errorMessage = document.getElementById('error-message');

        // Show spinner and disable button
        spinner.style.display = 'inline-block';
        buttonText.textContent = 'Analyzing...';
        submitButton.disabled = true;
        errorMessage.style.display = 'none';

        try {
            const response = await fetch(window.resumeAnalysisUrl, {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                if (result.redirect_url) {
                    window.location.href = result.redirect_url;
                } else {
                    throw new Error('No redirect URL provided.');
                }
            } else {
                errorMessage.textContent = result.error || 'An unknown error occurred.';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            errorMessage.textContent = 'A network error occurred. Please try again.';
            errorMessage.style.display = 'block';
        } finally {
            // Hide spinner and re-enable button
            spinner.style.display = 'none';
            buttonText.textContent = 'Analyze Resume';
            submitButton.disabled = false;
        }
    });
});
