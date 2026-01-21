// sphere_effect.js
// Final Specification Implementation: Interactive Particle Sphere with Bloom and Elastic Physics

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration ---
    const CONFIG = {
        particleCount: 8000,
        sphereRadius: 300,
        repulsionRadius: 150,
        repulsionStrength: 0.8,
        dampingFactor: 0.92,
        elasticRestoreForce: 0.02,
        rotationSpeedY: 0.0003,
        rotationSpeedX: 0.0001,
        particleSize: 2.5,
        bloomThreshold: 0.8,
        bloomStrength: 1.2,
        bloomRadius: 0.5
    };

    const container = document.getElementById('canvas-container') || (() => {
        const div = document.createElement('div');
        div.id = 'canvas-container';
        div.style.position = 'fixed';
        div.style.top = '0';
        div.style.left = '0';
        div.style.width = '100%';
        div.style.height = '100%';
        div.style.zIndex = '-1';
        div.style.background = 'radial-gradient(circle at center, #0a0a1a 0%, #000 100%)';
        document.body.prepend(div);
        return div;
    })();

    // --- Scene Setup ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.z = 800;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // --- Post Processing ---
    const renderScene = new RenderPass(scene, camera);
    const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        CONFIG.bloomStrength,
        CONFIG.bloomRadius,
        CONFIG.bloomThreshold
    );
    const composer = new EffectComposer(renderer);
    composer.addPass(renderScene);
    composer.addPass(bloomPass);

    // --- Fibonacci Sphere Generation ---
    const generateFibonacciSphere = (N, radius) => {
        const positions = new Float32Array(N * 3);
        const phi_golden = Math.PI * (3 - Math.sqrt(5)); // Golden angle

        for (let i = 0; i < N; i++) {
            const y = 1 - (i / (N - 1)) * 2; // y from 1 to -1
            const r_at_y = Math.sqrt(1 - y * y); // radius at y
            const theta = phi_golden * i;

            const x = Math.cos(theta) * r_at_y;
            const z = Math.sin(theta) * r_at_y;

            positions[i * 3] = x * radius;
            positions[i * 3 + 1] = y * radius;
            positions[i * 3 + 2] = z * radius;
        }
        return positions;
    };

    // --- Particle System ---
    const particlePositions = generateFibonacciSphere(CONFIG.particleCount, CONFIG.sphereRadius);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(particlePositions), 3));

    // Physics state
    const originalPositions = new Float32Array(particlePositions);
    const velocities = new Float32Array(CONFIG.particleCount * 3);

    const material = new THREE.PointsMaterial({
        color: 0xa855f7, // Purple glow
        size: CONFIG.particleSize,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending // Glow effect
    });

    const particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);

    // --- Cyan Cursor Indicator ---
    const cursorGeometry = new THREE.CircleGeometry(CONFIG.repulsionRadius, 32);
    const cursorMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: 0.05,
        side: THREE.DoubleSide
    });
    const cursorMesh = new THREE.Mesh(cursorGeometry, cursorMaterial);
    cursorMesh.position.z = 10;
    scene.add(cursorMesh);

    // --- Interaction ---
    const mousePos = { x: -9999, y: -9999 };
    document.addEventListener('mousemove', (e) => {
        mousePos.x = e.clientX;
        mousePos.y = e.clientY;
    });

    // Project 3D to Screen Space Utility
    const vec = new THREE.Vector3();
    const getScreenCoordinates = (x, y, z) => {
        vec.set(x, y, z);
        // Transform point to local space of the system
        vec.applyMatrix4(particleSystem.matrixWorld);
        vec.project(camera);
        return {
            x: (vec.x + 1) * window.innerWidth / 2,
            y: (-vec.y + 1) * window.innerHeight / 2
        };
    };

    // --- Animation Loop ---
    const animate = () => {
        requestAnimationFrame(animate);

        // 1. Continuous Rotation
        particleSystem.rotation.y += CONFIG.rotationSpeedY;
        particleSystem.rotation.x += CONFIG.rotationSpeedX;
        particleSystem.updateMatrixWorld();

        // 2. Physics & Repulsion
        const posAttr = geometry.attributes.position.array;
        const tempVec = new THREE.Vector3();
        const originVec = new THREE.Vector3();

        for (let i = 0; i < CONFIG.particleCount; i++) {
            const idx = i * 3;
            
            // Current local position
            const px = posAttr[idx];
            const py = posAttr[idx+1];
            const pz = posAttr[idx+2];

            // Get screen coordinates
            const screenPos = getScreenCoordinates(px, py, pz);
            
            // Calculate distance from mouse
            const dx_screen = screenPos.x - mousePos.x;
            const dy_screen = screenPos.y - mousePos.y;
            const dist_screen = Math.sqrt(dx_screen * dx_screen + dy_screen * dy_screen);

            if (dist_screen < CONFIG.repulsionRadius && dist_screen > 0) {
                const falloff = 1 - (dist_screen / CONFIG.repulsionRadius);
                const influence = falloff * CONFIG.repulsionStrength;
                
                // Repulsion Direction (in screen space, but we apply in 3D)
                // Note: Simplified logic to push away from "center of repulsion" in 3D
                // The spec asks for screen-coord based physics. 
                // We'll push along X and Y axes of the view.
                
                const pushX = (dx_screen / dist_screen) * influence * 5;
                const pushY = -(dy_screen / dist_screen) * influence * 5; // Y is inverted in screen vs 3D

                velocities[idx] += pushX;
                velocities[idx+1] += pushY;
            }

            // Damping
            velocities[idx] *= CONFIG.dampingFactor;
            velocities[idx+1] *= CONFIG.dampingFactor;
            velocities[idx+2] *= CONFIG.dampingFactor;

            // Elastic Restoration
            originVec.set(originalPositions[idx], originalPositions[idx+1], originalPositions[idx+2]);
            tempVec.set(px, py, pz);
            const toOrigin = originVec.sub(tempVec);
            
            velocities[idx] += toOrigin.x * CONFIG.elasticRestoreForce;
            velocities[idx+1] += toOrigin.y * CONFIG.elasticRestoreForce;
            velocities[idx+2] += toOrigin.z * CONFIG.elasticRestoreForce;

            // Update Positions
            posAttr[idx] += velocities[idx];
            posAttr[idx+1] += velocities[idx+1];
            posAttr[idx+2] += velocities[idx+2];
        }

        geometry.attributes.position.needsUpdate = true;

        // 3. Cursor Indicator Update
        // Plane is at Z=0 in world usually, but let's just use mouse projection
        vec.set(
            (mousePos.x / window.innerWidth) * 2 - 1,
            -(mousePos.y / window.innerHeight) * 2 + 1,
            0.5
        );
        vec.unproject(camera);
        const dir = vec.sub(camera.position).normalize();
        const distance = -camera.position.z / dir.z; // Project to Z=0 plane
        const pos = camera.position.clone().add(dir.multiplyScalar(distance));
        cursorMesh.position.set(pos.x, pos.y, 0);

        composer.render();
    };

    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        composer.setSize(window.innerWidth, window.innerHeight);
    });
});