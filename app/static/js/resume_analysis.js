document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysis-form');
    if (!form) return;

    const neuralOverlay = document.getElementById('neural-overlay');
    const logContainer = document.getElementById('log-container');
    const scannerLine = document.getElementById('scanner-line');
    const nodesContainer = document.getElementById('data-nodes-container');
    const parsingStatus = document.getElementById('parsing-status');

    const agentLogs = [
        "● Neural: Extracting semantic layers from PDF...",
        "● Neural: Identifying key skill vectors...",
        "● Logic: Cross-referencing industry benchmarks...",
        "● Logic: Matching candidate profile with job market data...",
        "● Agent: Synthesizing career advancement recommendations...",
        "● System: Finalizing neural report..."
    ];

    function addLog(text, index) {
        setTimeout(() => {
            const div = document.createElement('div');
            div.className = "text-muted animate-in";
            div.textContent = text;
            logContainer.appendChild(div);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Randomly trigger a glitch on some logs
            if (Math.random() > 0.7) {
                triggerGlitch();
            }
        }, index * 1200);
    }

    function createDataNode() {
        if (!nodesContainer) return;
        const node = document.createElement('div');
        node.className = 'data-node';
        node.style.left = Math.random() * 100 + '%';
        node.style.top = '80%';
        nodesContainer.appendChild(node);
        setTimeout(() => node.remove(), 2000);
    }

    function triggerGlitch() {
        const glitch = document.getElementById('error-glitch');
        if (!glitch) return;
        glitch.classList.remove('d-none');
        glitch.classList.add('glitch-flash');
        parsingStatus.textContent = "Neural Sync Interference Detected...";
        setTimeout(() => {
            glitch.classList.remove('glitch-flash');
            glitch.classList.add('d-none');
            parsingStatus.textContent = "Rerouting: Optimization Active";
        }, 300);
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const errorMessage = document.getElementById('error-message');

        // Show neural overlay and start animations
        if (neuralOverlay) {
            neuralOverlay.classList.remove('d-none');
            neuralOverlay.classList.add('d-flex');
            
            // Start Scanning Line
            if (scannerLine) scannerLine.classList.add('animate-scan');
            
            // Start Node Creation
            const nodeInterval = setInterval(createDataNode, 200);
            
            agentLogs.forEach((log, i) => addLog(log, i));

            // Store interval to clear later
            neuralOverlay.dataset.intervalId = nodeInterval;
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
