import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

console.log("💎 Glass Robot V3 Loaded");

// --- Configuration ---
const CONFIG = {
    colorBody: 0xffffff,
    colorGlass: 0xa5b4fc, // Indigo Tint
    colorGlow: 0x00d9ff,  // Cyan Neon
    followLag: 0.08,      // Smooth drag
    tiltForce: 0.2
};

// --- Globals ---
let scene, camera, renderer;
let robotGroup, headGroup, eyeGroup;
let particleSystem;
let mouse = new THREE.Vector2();
let targetPos = new THREE.Vector3();
let currentPos = new THREE.Vector3();
let velocity = new THREE.Vector3(); // For tilt calculation

// State
let isHovering = false;
let hoverTarget = null; // DOM element

function init() {
    const container = document.createElement('div');
    Object.assign(container.style, {
        position: 'fixed', top: '0', left: '0', width: '100%', height: '100%',
        pointerEvents: 'none', zIndex: '9999'
    });
    document.body.appendChild(container);

    // 1. Scene
    scene = new THREE.Scene();

    // 2. Camera
    camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = 22;

    // 3. Renderer
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.outputEncoding = THREE.sRGBEncoding;
    container.appendChild(renderer.domElement);

    // 4. Premium Lighting (Studio Setup)
    const ambient = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambient);

    // Main Key Light (Warm)
    const light1 = new THREE.DirectionalLight(0xffffff, 2);
    light1.position.set(5, 10, 10);
    scene.add(light1);

    // Rim Light (Cool/Blue) for edges
    const light2 = new THREE.PointLight(0x6366f1, 4, 20);
    light2.position.set(-10, 0, 5);
    scene.add(light2);

    // Bottom Fill (Cyan)
    const light3 = new THREE.PointLight(CONFIG.colorGlow, 1, 10);
    light3.position.set(0, -10, 5);
    scene.add(light3);

    // 5. Build
    createGlassRobot();
    createMagicParticles();

    // 6. Listeners
    document.addEventListener('mousemove', onMouseMove);
    window.addEventListener('resize', onResize);
    attachNavListeners();

    // 7. Loop
    animate();
}

function createGlassRobot() {
    robotGroup = new THREE.Group();
    scene.add(robotGroup);

    // --- Materials ---
    // 1. Frosted Glass Body
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: CONFIG.colorBody,
        metalness: 0.1,
        roughness: 0.1,
        transmission: 0.9, // Glass-like
        thickness: 0.5,
        clearcoat: 1.0,
        clearcoatRoughness: 0.1,
    });

    // 2. Solid Core (Inside the glass)
    const coreMat = new THREE.MeshBasicMaterial({ color: CONFIG.colorGlass });
    
    // 3. Glowing Eyes
    const glowMat = new THREE.MeshBasicMaterial({ color: CONFIG.colorGlow });

    // --- Geometry ---
    // Head (Glass Shell)
    headGroup = new THREE.Group();
    const headGeo = new THREE.SphereGeometry(0.8, 64, 64);
    const headMesh = new THREE.Mesh(headGeo, glassMat);
    headGroup.add(headMesh);

    // Inner Brain (Floating Octahedron)
    const brainGeo = new THREE.OctahedronGeometry(0.4, 0);
    const brainMesh = new THREE.Mesh(brainGeo, coreMat);
    headGroup.add(brainMesh);
    
    // Eyes (Floating outside)
    eyeGroup = new THREE.Group();
    const eyeGeo = new THREE.CapsuleGeometry(0.12, 0.3, 4, 8);
    const leftEye = new THREE.Mesh(eyeGeo, glowMat);
    const rightEye = new THREE.Mesh(eyeGeo, glowMat);
    
    leftEye.rotation.z = Math.PI / 2;
    rightEye.rotation.z = Math.PI / 2;
    leftEye.position.set(-0.3, 0.1, 0.7);
    rightEye.position.set(0.3, 0.1, 0.7);

    eyeGroup.add(leftEye, rightEye);
    headGroup.add(eyeGroup);

    // Halo / Rings
    const ringGeo = new THREE.TorusGeometry(1.2, 0.02, 16, 100);
    const ringMesh = new THREE.Mesh(ringGeo, glowMat);
    ringMesh.rotation.x = Math.PI / 2;
    headGroup.add(ringMesh);

    robotGroup.add(headGroup);
    robotGroup.userData = { brain: brainMesh, ring: ringMesh };
}

function createMagicParticles() {
    // A pool of particles for the "Beam"
    const count = 50;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    
    for(let i=0; i<count; i++) {
        positions[i*3] = 0; positions[i*3+1] = 0; positions[i*3+2] = 0;
        sizes[i] = 0; // Start hidden
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    // Shader Material for glowing dots
    const material = new THREE.PointsMaterial({
        color: CONFIG.colorGlow,
        size: 0.1,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    particleSystem = new THREE.Points(geometry, material);
    particleSystem.frustumCulled = false; // Always render
    scene.add(particleSystem);

    // Store particle data for animation
    particleSystem.userData = {
        particles: Array(count).fill().map(() => ({
            t: Math.random(), // Progress 0-1
            speed: 0.02 + Math.random() * 0.03,
            offset: new THREE.Vector3((Math.random()-0.5)*0.5, (Math.random()-0.5)*0.5, (Math.random()-0.5)*0.5)
        }))
    };
}

// --- Interaction ---
function attachNavListeners() {
    const targets = document.querySelectorAll('.nav-link, .btn, .card');
    targets.forEach(el => {
        el.addEventListener('mouseenter', () => {
            isHovering = true;
            hoverTarget = el;
        });
        el.addEventListener('mouseleave', () => {
            isHovering = false;
            hoverTarget = null;
        });
    });
}

function getElementPosition(el) {
    if(!el) return null;
    const rect = el.getBoundingClientRect();
    const ndcX = (rect.left + rect.width/2) / window.innerWidth * 2 - 1;
    const ndcY = -(rect.top + rect.height/2) / window.innerHeight * 2 + 1;
    
    const vec = new THREE.Vector3(ndcX, ndcY, 0.5);
    vec.unproject(camera);
    const dir = vec.sub(camera.position).normalize();
    const dist = -camera.position.z / dir.z;
    return camera.position.clone().add(dir.multiplyScalar(dist));
}

// --- Loop ---
function animate() {
    requestAnimationFrame(animate);
    const time = Date.now() * 0.001;

    // 1. Determine Target
    let dest = new THREE.Vector3();
    
    if (isHovering && hoverTarget) {
        // Fly near the element
        const elPos = getElementPosition(hoverTarget);
        if (elPos) {
            dest.copy(elPos);
            dest.x += 3; // Float to the right
            dest.z += 2; // Come closer
        }
    } else {
        // Idle Position (Bottom Right)
        const ndcX = 0.8;
        const ndcY = -0.7;
        const vec = new THREE.Vector3(ndcX, ndcY, 0.5);
        vec.unproject(camera);
        const dir = vec.sub(camera.position).normalize();
        const dist = -camera.position.z / dir.z;
        dest.copy(camera.position.clone().add(dir.multiplyScalar(dist)));
        
        // Idle Float
        dest.y += Math.sin(time * 2) * 0.2;
    }

    // 2. Physics (Dampening)
    const force = dest.clone().sub(currentPos).multiplyScalar(CONFIG.followLag);
    velocity.add(force).multiplyScalar(0.9); // Friction
    currentPos.add(velocity);
    robotGroup.position.copy(currentPos);

    // 3. Tilt (Banking)
    // Tilt body based on velocity X (roll) and Y (pitch)
    const targetRotZ = -velocity.x * CONFIG.tiltForce * 5;
    const targetRotX = velocity.y * CONFIG.tiltForce * 5;
    
    robotGroup.rotation.z = THREE.MathUtils.lerp(robotGroup.rotation.z, targetRotZ, 0.1);
    robotGroup.rotation.x = THREE.MathUtils.lerp(robotGroup.rotation.x, targetRotX, 0.1);

    // 4. Look At Logic
    let lookTarget = new THREE.Vector3(mouse.x * 10, mouse.y * 10, 20); // Default: look at mouse plane
    if (isHovering && hoverTarget) {
        const elPos = getElementPosition(hoverTarget);
        if(elPos) lookTarget.copy(elPos);
    }
    
    // Smoothly rotate head to lookTarget
    // Note: This is simplified. Proper lookAt requires quaternion slerp, but simple rotation lerp works for small angles.
    headGroup.lookAt(lookTarget);

    // 5. Inner Animation
    robotGroup.userData.brain.rotation.y += 0.05;
    robotGroup.userData.brain.rotation.z += 0.02;
    robotGroup.userData.ring.rotation.z -= 0.01;

    // 6. Particle Stream (Magic Beam)
    updateParticles();

    renderer.render(scene, camera);
}

function updateParticles() {
    const positions = particleSystem.geometry.attributes.position.array;
    const sizes = particleSystem.geometry.attributes.size.array;
    const data = particleSystem.userData.particles;
    
    // Origin: Robot Eyes
    const origin = new THREE.Vector3();
    eyeGroup.getWorldPosition(origin);

    // Target: UI Element
    let target = new THREE.Vector3(0, 0, 0); // Default?
    let active = false;

    if (isHovering && hoverTarget) {
        const t = getElementPosition(hoverTarget);
        if(t) {
            target.copy(t);
            active = true;
        }
    }

    for(let i=0; i<data.length; i++) {
        const p = data[i];
        
        if (active) {
            // Move particle along line
            p.t += p.speed;
            if (p.t > 1) p.t = 0;

            const pos = new THREE.Vector3().lerpVectors(origin, target, p.t);
            // Add jitter
            pos.add(p.offset);

            positions[i*3] = pos.x;
            positions[i*3+1] = pos.y;
            positions[i*3+2] = pos.z;
            
            // Fade in/out
            const life = Math.sin(p.t * Math.PI); // 0 -> 1 -> 0
            sizes[i] = life * 0.15;
        } else {
            // Hide
            sizes[i] = 0;
        }
    }

    particleSystem.geometry.attributes.position.needsUpdate = true;
    particleSystem.geometry.attributes.size.needsUpdate = true;
}

function onMouseMove(e) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
}

function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

init();

function createRobot() {
    robotGroup = new THREE.Group();
    // Start hidden inside portal
    robotGroup.scale.set(0, 0, 0);
    scene.add(robotGroup);

    const bodyMat = new THREE.MeshStandardMaterial({ color: CONFIG.colorBody, roughness: 0.3, metalness: 0.1 });
    const eyeMat = new THREE.MeshBasicMaterial({ color: CONFIG.eyeColor });

    // Head
    head = new THREE.Group();
    const headGeo = new THREE.SphereGeometry(0.7, 32, 32);
    const headMesh = new THREE.Mesh(headGeo, bodyMat);
    head.add(headMesh);

    // Face (Black Glass)
    const faceGeo = new THREE.SphereGeometry(0.71, 32, 32, 0, Math.PI * 2, 0, Math.PI * 0.3);
    const faceMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const face = new THREE.Mesh(faceGeo, faceMat);
    face.rotation.x = -Math.PI / 2;
    head.add(face);

    // Eyes
    const eyeGeo = new THREE.CapsuleGeometry(0.15, 0.3, 4, 8);
    leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    
    // Rotate capsules to be horizontal ovals
    leftEye.rotation.z = Math.PI / 2;
    rightEye.rotation.z = Math.PI / 2;
    
    leftEye.position.set(-0.3, 0.1, 0.62);
    rightEye.position.set(0.3, 0.1, 0.62);
    
    // Slight tilt for aggression/focus
    leftEye.rotation.y = 0.2;
    rightEye.rotation.y = -0.2;

    head.add(leftEye, rightEye);
    robotGroup.add(head);

    // Body (Floating bits)
    const orbitGeo = new THREE.TorusGeometry(1.2, 0.05, 16, 100);
    const orbitMat = new THREE.MeshBasicMaterial({ color: CONFIG.colorDetail, transparent: true, opacity: 0.6 });
    const orbit = new THREE.Mesh(orbitGeo, orbitMat);
    orbit.rotation.x = Math.PI / 2;
    robotGroup.add(orbit);
    
    // Animate orbit later
    robotGroup.userData = { orbit: orbit };
}

function createBeam() {
    // A dynamic line connecting robot to UI
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(6 * 3); // 2 points * 3 coords
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.LineBasicMaterial({ 
        color: CONFIG.beamColor, 
        transparent: true, 
        opacity: 0,
        linewidth: 2 
    });

    beamMesh = new THREE.Line(geometry, material);
    scene.add(beamMesh);
}

function createPortal() {
    const geometry = new THREE.RingGeometry(0.1, 0.2, 64);
    const material = new THREE.MeshBasicMaterial({ 
        color: CONFIG.eyeColor, 
        side: THREE.DoubleSide, 
        transparent: true, 
        opacity: 0 
    });
    portalMesh = new THREE.Mesh(geometry, material);
    portalMesh.position.set(0, 0, -5);
    scene.add(portalMesh);
}

// --- Logic ---

function runIntroSequence() {
    console.log("🤖 Starting Intro Sequence...");
    // 1. Portal Opens
    let s = 0;
    const openPortal = setInterval(() => {
        s += 0.2;
        portalMesh.scale.set(s*20, s*20, 1);
        portalMesh.material.opacity = Math.min(1, s);
        portalMesh.rotation.z += 0.1;

        if (s >= 1.5) {
            clearInterval(openPortal);
            console.log("🤖 Portal Open. Spawning Robot...");
            // 2. Robot Bursts Out
            let rs = 0;
            const spawnRobot = setInterval(() => {
                rs += 0.05;
                robotGroup.scale.set(rs, rs, rs);
                // Move from portal z to front
                robotGroup.position.z = THREE.MathUtils.lerp(-5, 0, rs);
                
                if (rs >= 1) {
                    clearInterval(spawnRobot);
                    hasEntered = true;
                    console.log("🤖 Robot Entered!");
                    // 3. Close Portal
                    portalMesh.visible = false;
                }
            }, 16);
        }
    }, 16);
}

function attachNavListeners() {
    const targets = document.querySelectorAll('.nav-link, .btn, .card, input');
    
    targets.forEach(el => {
        el.addEventListener('mouseenter', () => {
            isHoveringNav = true;
            isBeamActive = true;
            moveRobotToElement(el);
            // Squint eyes
            setEyeScale(1, 0.5); 
        });
        el.addEventListener('mouseleave', () => {
            isHoveringNav = false;
            isBeamActive = false;
            setEyeScale(1, 1);
        });
    });
}

function moveRobotToElement(element) {
    const rect = element.getBoundingClientRect();
    
    // 1. Calculate Target for Robot (Right/Top of element)
    // Convert 2D -> 3D
    const ndcX = (rect.left + rect.width) / window.innerWidth * 2 - 1;
    const ndcY = -(rect.top + rect.height / 2) / window.innerHeight * 2 + 1;
    
    const vec = new THREE.Vector3(ndcX + 0.1, ndcY + 0.1, 0.5); // Offset slightly
    vec.unproject(camera);
    const dir = vec.sub(camera.position).normalize();
    const dist = -camera.position.z / dir.z;
    targetPosition.copy(camera.position.clone().add(dir.multiplyScalar(dist)));

    // 2. Calculate Target for Beam (Center of element)
    const beamNDCX = (rect.left + rect.width / 2) / window.innerWidth * 2 - 1;
    const beamNDCY = -(rect.top + rect.height / 2) / window.innerHeight * 2 + 1;
    
    const beamVec = new THREE.Vector3(beamNDCX, beamNDCY, 0.5);
    beamVec.unproject(camera);
    const beamDir = beamVec.sub(camera.position).normalize();
    const beamDist = -camera.position.z / beamDir.z;
    beamTarget.copy(camera.position.clone().add(beamDir.multiplyScalar(beamDist)));
}

function updateDefaultPosition() {
    if (isHoveringNav || !hasEntered) return;

    let ndcX, ndcY;
    if (isChatting) {
        ndcX = 0.75; ndcY = -0.4;
    } else {
        ndcX = 0.82; ndcY = -0.75;
    }
    
    const vec = new THREE.Vector3(ndcX, ndcY, 0.5);
    vec.unproject(camera);
    const dir = vec.sub(camera.position).normalize();
    const dist = -camera.position.z / dir.z;
    targetPosition.copy(camera.position.clone().add(dir.multiplyScalar(dist)));
}

function setEyeScale(x, y) {
    leftEye.scale.set(1, y, 1); // Capsule orientation is tricky, Y is length here due to rotation?
    // Actually our capsules are rotated Z=90. So Y-scale in local space is width in world space.
    // Let's just tween scale.
    // Tweaking logic for capsule geometry scaling
    // Default is (1,1,1).
    // Squint: reduce thickness.
    
    // Animate smoothly? For now direct set.
}

function startBlinking() {
    setInterval(() => {
        if (Math.random() > 0.1) {
            // Blink
            leftEye.visible = false;
            rightEye.visible = false;
            setTimeout(() => {
                leftEye.visible = true;
                rightEye.visible = true;
            }, 150);
        }
    }, 3000);
}

// --- Animation Loop ---

function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    const time = Date.now() * 0.001;

    if (!hasEntered) return; // Wait for intro

    updateDefaultPosition();

    // 1. Move Body (Damped Spring)
    robotGroup.position.lerp(targetPosition, CONFIG.followSpeed);
    
    // Float
    const floatY = Math.sin(time * CONFIG.floatSpeed) * CONFIG.floatAmp;
    head.position.y = floatY;
    robotGroup.userData.orbit.rotation.z += 0.02; // Spin the ring
    robotGroup.userData.orbit.rotation.x = Math.sin(time) * 0.2 + Math.PI/2;

    // 2. Look At Mouse
    const lookX = mouse.x * 0.8;
    const lookY = mouse.y * 0.8;
    head.rotation.y = THREE.MathUtils.lerp(head.rotation.y, lookX, 0.1);
    head.rotation.x = THREE.MathUtils.lerp(head.rotation.x, lookY, 0.1);

    // 3. Update Beam
    if (isBeamActive && beamMesh) {
        const positions = beamMesh.geometry.attributes.position.array;
        
        // Start Point (Robot Center/Eye)
        // We need world position of head
        const headPos = new THREE.Vector3();
        head.getWorldPosition(headPos);
        
        positions[0] = headPos.x;
        positions[1] = headPos.y;
        positions[2] = headPos.z;

        // End Point (UI Element)
        positions[3] = beamTarget.x;
        positions[4] = beamTarget.y;
        positions[5] = beamTarget.z;

        beamMesh.geometry.attributes.position.needsUpdate = true;
        beamMesh.material.opacity = THREE.MathUtils.lerp(beamMesh.material.opacity, 0.6, 0.1);
    } else {
        if (beamMesh) beamMesh.material.opacity = THREE.MathUtils.lerp(beamMesh.material.opacity, 0, 0.2);
    }

    renderer.render(scene, camera);
}

init();
