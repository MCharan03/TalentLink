// Scene.js - "Neural Network" AI Visualization
// Represents the AI 'Brain' analyzing connections between skills and data

import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

class NeuralNetworkBackground {
    constructor() {
        this.container = document.createElement('div');
        this.container.style.position = 'fixed';
        this.container.style.top = '0';
        this.container.style.left = '0';
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        this.container.style.zIndex = '-1';
        this.container.style.pointerEvents = 'none';
        document.body.appendChild(this.container);

        // Setup Scene
        this.scene = new THREE.Scene();
        // Deep fog for depth - matches the CSS background color
        // Check if dark mode or light mode (simple check)
        const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.scene.fog = new THREE.FogExp2(isDark ? 0x000000 : 0xf5f5f7, 0.05);

        this.camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
        this.camera.position.z = 12;

        this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.container.appendChild(this.renderer.domElement);

        this.particlesData = [];
        this.maxParticleCount = 100; // Number of "Skills/Nodes"
        this.particlePositions = new Float32Array(this.maxParticleCount * 3);
        this.particleVelocities = [];
        
        // Group to hold the entire network for easy rotation
        this.networkGroup = new THREE.Group();
        this.scene.add(this.networkGroup);

        this.initLights();
        this.initNetwork();
        this.addEventListeners();
        this.animate();
    }

    initLights() {
        // Techy blue point lights
        const p1 = new THREE.PointLight(0x0071e3, 2, 50);
        p1.position.set(10, 10, 10);
        this.scene.add(p1);

        const p2 = new THREE.PointLight(0x5e5ce6, 2, 50);
        p2.position.set(-10, -10, 10);
        this.scene.add(p2);
    }

    initNetwork() {
        // 1. The Nodes (Spheres)
        const particleGeometry = new THREE.IcosahedronGeometry(0.15, 1);
        const particleMaterial = new THREE.MeshPhongMaterial({
            color: 0x0071e3,
            emissive: 0x001133,
            specular: 0xffffff,
            shininess: 50
        });

        // Create particles
        for (let i = 0; i < this.maxParticleCount; i++) {
            const particle = new THREE.Mesh(particleGeometry, particleMaterial);
            
            // Random distribution in a cloud
            const x = Math.random() * 20 - 10;
            const y = Math.random() * 20 - 10;
            const z = Math.random() * 20 - 10;

            particle.position.set(x, y, z);
            
            // Store raw positions for line calculations
            this.particlePositions[i * 3] = x;
            this.particlePositions[i * 3 + 1] = y;
            this.particlePositions[i * 3 + 2] = z;

            // Random velocity
            this.particleVelocities.push({
                x: (Math.random() - 0.5) * 0.02,
                y: (Math.random() - 0.5) * 0.02,
                z: (Math.random() - 0.5) * 0.02
            });

            // Store ref to mesh
            particle.userData = { velocity: this.particleVelocities[i] };
            this.particlesData.push(particle);
            this.networkGroup.add(particle);
        }

        // 2. The Connections (Lines)
        // We use BufferGeometry for performance
        this.segments = this.maxParticleCount * this.maxParticleCount;
        this.positions = new Float32Array(this.segments * 3);
        this.colors = new Float32Array(this.segments * 3);

        const lineGeometry = new THREE.BufferGeometry();
        lineGeometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3).setUsage(THREE.DynamicDrawUsage));
        lineGeometry.setAttribute('color', new THREE.BufferAttribute(this.colors, 3).setUsage(THREE.DynamicDrawUsage));

        const lineMaterial = new THREE.LineBasicMaterial({
            vertexColors: true,
            blending: THREE.AdditiveBlending,
            transparent: true,
            opacity: 0.4
        });

        this.linesMesh = new THREE.LineSegments(lineGeometry, lineMaterial);
        this.networkGroup.add(this.linesMesh);
    }

    addEventListeners() {
        window.addEventListener('resize', this.onResize.bind(this));
        window.addEventListener('mousemove', this.onMouseMove.bind(this));
        
        // Tilt Cards
        document.querySelectorAll('.tilt-card').forEach(card => {
            card.addEventListener('mousemove', this.handleCardTilt.bind(this));
            card.addEventListener('mouseleave', this.resetCardTilt.bind(this));
        });
    }

    onResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    onMouseMove(event) {
        // Normalize mouse for rotation
        this.mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    // Reuse tilt card logic
    handleCardTilt(e) {
        const card = e.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -8;
        const rotateY = ((x - centerX) / centerX) * 8;
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        const glare = card.querySelector('.glare');
        if (glare) {
            glare.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.3) 0%, transparent 80%)`;
            glare.style.opacity = '1';
        }
    }
    resetCardTilt(e) {
        const card = e.currentTarget;
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        const glare = card.querySelector('.glare');
        if (glare) { glare.style.opacity = '0'; }
    }

    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        // 1. Rotate the whole network slowly based on mouse (Interactive)
        if (this.mouseX) {
            this.networkGroup.rotation.y += (this.mouseX * 0.5 - this.networkGroup.rotation.y) * 0.05;
            this.networkGroup.rotation.x += (-this.mouseY * 0.5 - this.networkGroup.rotation.x) * 0.05;
        } else {
            // Idle rotation
            this.networkGroup.rotation.y += 0.001;
        }

        // 2. Update Particles & Lines
        let vertexpos = 0;
        let colorpos = 0;
        let numConnected = 0;

        // Reset all contact
        // O(N^2) loop - okay for < 150 particles
        for (let i = 0; i < this.maxParticleCount; i++) {
            const p = this.particlesData[i];
            const v = p.userData.velocity;

            // Move
            p.position.x += v.x;
            p.position.y += v.y;
            p.position.z += v.z;

            // Bounce off boundaries (keep them in a box)
            if (p.position.x < -10 || p.position.x > 10) v.x = -v.x;
            if (p.position.y < -10 || p.position.y > 10) v.y = -v.y;
            if (p.position.z < -10 || p.position.z > 10) v.z = -v.z;

            // Check connections
            // Only connect to particles *after* this one to avoid duplicates
            for (let j = i + 1; j < this.maxParticleCount; j++) {
                const p2 = this.particlesData[j];
                
                const dx = p.position.x - p2.position.x;
                const dy = p.position.y - p2.position.y;
                const dz = p.position.z - p2.position.z;
                const distSq = dx*dx + dy*dy + dz*dz;

                // If close enough, draw a line
                if (distSq < 12) { // Threshold squared
                    // Calculate alpha based on distance (closer = brighter)
                    const alpha = 1.0 - distSq / 12;

                    this.positions[vertexpos++] = p.position.x;
                    this.positions[vertexpos++] = p.position.y;
                    this.positions[vertexpos++] = p.position.z;

                    this.positions[vertexpos++] = p2.position.x;
                    this.positions[vertexpos++] = p2.position.y;
                    this.positions[vertexpos++] = p2.position.z;

                    // Color gradient (Blue to Indigo)
                    this.colors[colorpos++] = 0.0; // R
                    this.colors[colorpos++] = 0.44; // G
                    this.colors[colorpos++] = 0.89; // B (Apple Blue)

                    this.colors[colorpos++] = 0.36; // R
                    this.colors[colorpos++] = 0.36; // G
                    this.colors[colorpos++] = 0.90; // B (Indigo)

                    numConnected++;
                }
            }
        }

        // Update Geometry
        this.linesMesh.geometry.setDrawRange(0, numConnected * 2);
        this.linesMesh.geometry.attributes.position.needsUpdate = true;
        this.linesMesh.geometry.attributes.color.needsUpdate = true;

        this.renderer.render(this.scene, this.camera);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new NeuralNetworkBackground();
});
