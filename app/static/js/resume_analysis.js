document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysis-form');
    if (!form) return;

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log("DEBUG: Analysis form submitted.");

        const formData = new FormData(form);
        const spinner = document.getElementById('spinner');
        const buttonText = document.getElementById('button-text');
        const submitButton = form.querySelector('button[type="submit"]');
        const errorMessage = document.getElementById('error-message');

        // Show spinner and disable button
        if (spinner) spinner.style.display = 'inline-block';
        if (buttonText) buttonText.textContent = 'Uploading...';
        if (submitButton) submitButton.disabled = true;
        if (errorMessage) errorMessage.style.display = 'none';

        // Using XHR for progress tracking
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                console.log("DEBUG: Upload progress: " + percent + "%");
                if (buttonText) buttonText.textContent = 'Uploading (' + percent + '%)...';
            }
        });

        xhr.addEventListener('load', function() {
            console.log("DEBUG: XHR Load complete. Status: " + xhr.status);
            if (buttonText) buttonText.textContent = 'Processing...';
            
            try {
                const result = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    if (result.redirect_url) {
                        window.location.href = result.redirect_url;
                    } else {
                        throw new Error('No redirect URL provided.');
                    }
                } else {
                    if (errorMessage) {
                        errorMessage.textContent = result.error || 'An unknown error occurred.';
                        errorMessage.style.display = 'block';
                    }
                }
            } catch (e) {
                if (errorMessage) {
                    errorMessage.textContent = 'Server processing failed.';
                    errorMessage.style.display = 'block';
                }
            }
            
            if (spinner) spinner.style.display = 'none';
            if (buttonText) buttonText.textContent = 'Analyze Resume';
            if (submitButton) submitButton.disabled = false;
        });

        xhr.addEventListener('error', function() {
            console.log("DEBUG: XHR Network Error");
            errorMessage.textContent = 'A network error occurred.';
            errorMessage.style.display = 'block';
            spinner.style.display = 'none';
            buttonText.textContent = 'Analyze Resume';
            submitButton.disabled = false;
        });

        xhr.open('POST', window.resumeAnalysisUrl);
        // Include CSRF Token from the form
        const csrfToken = form.querySelector('input[name="csrf_token"]').value;
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        
        console.log("DEBUG: XHR sending...");
        xhr.send(formData);
    });
});
