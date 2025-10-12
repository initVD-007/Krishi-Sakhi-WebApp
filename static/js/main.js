import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

console.log("Krishi Sakhi JavaScript file loaded!");

// --- 3D Hero Scene on Dashboard ---
const heroCanvas = document.querySelector('#hero-canvas');
if (heroCanvas) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, heroCanvas.clientWidth / heroCanvas.clientHeight, 0.1, 1000);
    camera.position.set(5, 1, 4);

    const renderer = new THREE.WebGLRenderer({ canvas: heroCanvas, antialias: true, alpha: true });
    renderer.setSize(heroCanvas.clientWidth, heroCanvas.clientHeight);

    const ambientLight = new THREE.AmbientLight(0xffffff, 2);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 3);
    directionalLight.position.set(5, 10, 7.5);
    scene.add(directionalLight);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.0;
    controls.enableZoom = true;

    const loader = new GLTFLoader();
    loader.load(
        'static/models/mini.glb', // Make sure this path is correct
        (gltf) => {
            const model = gltf.scene;
            model.scale.set(30, 30, 30);

            // --- CODE TO CENTER THE MODEL ---
            // 1. Calculate the bounding box of the model
            const box = new THREE.Box3().setFromObject(model);
            // 2. Get the center of that box
            const center = box.getCenter(new THREE.Vector3());
            // 3. Move the model by the negative of the center vector
            model.position.sub(center);

            scene.add(model);
        },
        undefined,
        (error) => console.error('Error loading 3D model:', error)
    );

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}


// --- Image Preview Logic (for diagnose page) ---
const imageUpload = document.getElementById('imageUpload');
const imagePreview = document.getElementById('imagePreview');

if (imageUpload && imagePreview) {
    imageUpload.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                imagePreview.src = event.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
}

// --- Voice Recognition Logic (for ask page) ---
const micButton = document.getElementById('micButton');
const questionText = document.getElementById('questionText');

if (micButton && questionText && 'webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'hi-IN'; // Set language to hindi(India)

    micButton.addEventListener('click', () => {
        recognition.start();
        questionText.placeholder = 'Listening...';
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        questionText.value = transcript;
        questionText.placeholder = 'e.g., Which fertilizer is best for bananas during the monsoon?';
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        questionText.placeholder = 'Sorry, I could not hear you. Please try again.';
    };

} else if (micButton) {
    // Hide the mic button if the browser doesn't support the API
    micButton.style.display = 'none';
}