// landing_animations.js - Global Background & UI Interactions

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Interactive Global Canvas Background (Constellation Effect)
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Attach to body for global persistence
    canvas.id = 'bg-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '-1'; // Behind everything
    canvas.style.pointerEvents = 'none';
    document.body.appendChild(canvas);

    let width, height;
    let particles = [];

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.size = Math.random() * 2 + 1;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }
        draw() {
            const theme = document.documentElement.getAttribute('data-theme');
            const color = theme === 'light' ? '99, 102, 241' : '165, 180, 252'; // Indigo 500 / Indigo 300
            
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${color}, 0.2)`;
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        const count = Math.min(Math.floor(window.innerWidth / 15), 100); // Responsive density
        for (let i = 0; i < count; i++) particles.push(new Particle());
    }

    function animateParticles() {
        ctx.clearRect(0, 0, width, height);
        
        const theme = document.documentElement.getAttribute('data-theme');
        const color = theme === 'light' ? '99, 102, 241' : '165, 180, 252';
        
        // Draw connections
        for (let i = 0; i < particles.length; i++) {
            let p1 = particles[i];
            p1.update();
            p1.draw();
            
            for (let j = i + 1; j < particles.length; j++) {
                let p2 = particles[j];
                let dx = p1.x - p2.x;
                let dy = p1.y - p2.y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if (dist < 180) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(${color}, ${0.15 - dist/1200})`;
                    ctx.lineWidth = 0.8;
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animateParticles);
    }

    window.addEventListener('resize', () => {
        resize();
        initParticles();
    });
    
    resize();
    initParticles();
    animateParticles();

    // 2. Vanilla Tilt Effect for Cards (3D Hover)
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });
    });
});
