/**
 * 🧠 Cherry AI - Emotional Telemetry Engine
 * Tracks user behavior patterns to detect Stress, Flow, or Fatigue.
 */

class TelemetryEngine {
    constructor() {
        this.metrics = {
            mouseVelocity: 0,
            clickRate: 0,
            typingSpeed: 0,
            backspaceRate: 0,
            stressScore: 0 // 0 to 100
        };
        
        this.history = {
            mousePositions: [],
            keyPresses: []
        };

        this.lastMouseTime = Date.now();
        this.lastClickTime = Date.now();
        this.clickCount = 0;

        this.init();
    }

    init() {
        document.addEventListener('mousemove', (e) => this.trackMouse(e));
        document.addEventListener('click', () => this.trackClick());
        document.addEventListener('keydown', (e) => this.trackTyping(e));
        
        // Analyze every 2 seconds
        setInterval(() => this.analyzeState(), 2000);
    }

    trackMouse(e) {
        const now = Date.now();
        const dt = now - this.lastMouseTime;
        if (dt > 50) { // Throttle
            this.history.mousePositions.push({ x: e.clientX, y: e.clientY, t: now });
            if (this.history.mousePositions.length > 20) this.history.mousePositions.shift();
            this.lastMouseTime = now;
        }
    }

    trackClick() {
        const now = Date.now();
        if (now - this.lastClickTime < 300) {
            this.clickCount++; // Rapid clicking
        } else {
            this.clickCount = 1;
        }
        this.lastClickTime = now;
    }

    trackTyping(e) {
        const now = Date.now();
        this.history.keyPresses.push({ key: e.key, t: now });
        if (this.history.keyPresses.length > 30) this.history.keyPresses.shift();
    }

    analyzeState() {
        const now = Date.now();

        // 1. Calculate Mouse Jitter (Erratic Movement)
        let totalDist = 0;
        let erraticScore = 0;
        for (let i = 1; i < this.history.mousePositions.length; i++) {
            const p1 = this.history.mousePositions[i-1];
            const p2 = this.history.mousePositions[i];
            const dist = Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
            totalDist += dist;
        }
        // High distance in short time = agitation
        if (totalDist > 3000) erraticScore += 20;

        // 2. Calculate Typing Stress (High Backspace Rate = Hesitation/Frustration)
        const recentKeys = this.history.keyPresses.filter(k => now - k.t < 2000);
        const backspaces = recentKeys.filter(k => k.key === 'Backspace').length;
        const totalKeys = recentKeys.length;
        
        let typingStress = 0;
        if (totalKeys > 5) {
            const backspaceRatio = backspaces / totalKeys;
            if (backspaceRatio > 0.2) typingStress += 30; // 20% backspaces is high
        }

        // 3. Rage Clicks
        let clickStress = 0;
        if (this.clickCount > 3) clickStress += 40;

        // Total Stress Score calculation
        let newStress = erraticScore + typingStress + clickStress;
        
        // Smoothing
        this.metrics.stressScore = (this.metrics.stressScore * 0.7) + (newStress * 0.3);

        this.triggerReaction();
    }

    triggerReaction() {
        const body = document.body;
        const hudStatus = document.querySelector('.sentient-status-text');

        if (this.metrics.stressScore > 50) {
            // High Stress: Cool down the UI, reduce contrast
            if (!body.classList.contains('mode-calm')) {
                body.classList.add('mode-calm');
                console.log("🍒 Cherry: Sensing stress. Activating Calm Mode.");
                if(hudStatus) hudStatus.innerText = "State: High Load";
                this.flashMessage("Detected high cognitive load. Stabilizing UI...");
            }
        } else {
            // Normal State
            if (body.classList.contains('mode-calm')) {
                body.classList.remove('mode-calm');
                if(hudStatus) hudStatus.innerText = "State: Flow";
            }
        }
    }

    flashMessage(msg) {
        const botWidget = document.getElementById('ai-bot-widget');
        if (botWidget) {
            // Create a temporary toast
            const toast = document.createElement('div');
            toast.className = 'position-fixed bottom-0 start-50 translate-middle-x mb-5 badge bg-primary border-glass p-3 animate-up';
            toast.style.zIndex = 1050;
            toast.innerHTML = `<i class="fas fa-heartbeat me-2"></i> ${msg}`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.cherryTelemetry = new TelemetryEngine();
});
