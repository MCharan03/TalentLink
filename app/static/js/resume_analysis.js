document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysis-form');
    if (!form) return;

    const neuralOverlay = document.getElementById('neural-overlay');
    const logContainer = document.getElementById('log-container');

    const agentLogs = [
        "● Extracting semantic layers from PDF...",
        "● Identifying key skill vectors...",
        "● Cross-referencing industry benchmarks...",
        "● Matching candidate profile with job market data...",
        "● Synthesizing career advancement recommendations...",
        "● Finalizing neural report..."
    ];

    function addLog(text, index) {
        setTimeout(() => {
            const div = document.createElement('div');
            div.className = "text-muted animate-in";
            div.textContent = text;
            logContainer.appendChild(div);
            // Auto-scroll logs
            logContainer.scrollTop = logContainer.scrollHeight;
        }, index * 1200);
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log("DEBUG: Analysis form submitted.");

        const formData = new FormData(form);
        const spinner = document.getElementById('spinner');
        const buttonText = document.getElementById('button-text');
        const submitButton = form.querySelector('button[type="submit"]');
        const errorMessage = document.getElementById('error-message');

        // Show neural overlay
        if (neuralOverlay) {
            neuralOverlay.classList.remove('d-none');
            neuralOverlay.classList.add('d-flex');
            agentLogs.forEach((log, i) => addLog(log, i));
        }

        // Disable button
        if (submitButton) submitButton.disabled = true;
        if (errorMessage) errorMessage.style.display = 'none';

        // Using XHR for progress tracking
        const xhr = new XMLHttpRequest();
        
        xhr.addEventListener('load', function() {
            console.log("DEBUG: XHR Load complete. Status: " + xhr.status);
            
            try {
                const result = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    if (result.redirect_url) {
                        // Delay redirect slightly to show logs
                        setTimeout(() => {
                            window.location.href = result.redirect_url;
                        }, 2000);
                    } else {
                        throw new Error('No redirect URL provided.');
                    }
                } else {
                    if (neuralOverlay) neuralOverlay.classList.add('d-none');
                    if (errorMessage) {
                        errorMessage.textContent = result.error || 'An unknown error occurred.';
                        errorMessage.style.display = 'block';
                    }
                }
            } catch (e) {
                if (neuralOverlay) neuralOverlay.classList.add('d-none');
                if (errorMessage) {
                    errorMessage.textContent = 'Server processing failed.';
                    errorMessage.style.display = 'block';
                }
            }
            
            if (submitButton) submitButton.disabled = false;
        });

        xhr.addEventListener('error', function() {
            console.log("DEBUG: XHR Network Error");
            if (neuralOverlay) neuralOverlay.classList.add('d-none');
            errorMessage.textContent = 'A network error occurred.';
            errorMessage.style.display = 'block';
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
