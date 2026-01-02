// Galaxy Animation
const canvas = document.getElementById('galaxy-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let stars = [];
const STAR_COUNT = 800;
const GALAXY_SPEED = 0.05;

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
}

class Star {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = (Math.random() - 0.5) * width * 2;
        this.y = (Math.random() - 0.5) * height * 2;
        this.z = Math.random() * width;
        this.size = Math.random() * 2;
        this.color = this.getRandomColor();
    }

    getRandomColor() {
        const colors = ['#ffffff', '#ffe9c4', '#d4fbff', '#3b82f6', '#8b5cf6'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    update() {
        this.z -= GALAXY_SPEED * 20; // Move stars towards viewer

        if (this.z <= 0) {
            this.reset();
            this.z = width;
        }
    }

    draw() {
        const x = (this.x / this.z) * width + width / 2;
        const y = (this.y / this.z) * height + height / 2;
        const size = (1 - this.z / width) * this.size * 2;

        if (x < 0 || x > width || y < 0 || y > height) return;

        ctx.beginPath();
        ctx.fillStyle = this.color;
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
        
        // Add glow effect for larger stars
        if (size > 1.5) {
            ctx.shadowBlur = 10;
            ctx.shadowColor = this.color;
        } else {
            ctx.shadowBlur = 0;
        }
    }
}

function init() {
    resize();
    for (let i = 0; i < STAR_COUNT; i++) {
        stars.push(new Star());
    }
    animate();
}

function animate() {
    ctx.fillStyle = 'rgba(5, 5, 5, 0.2)'; // Trail effect
    ctx.fillRect(0, 0, width, height);

    stars.forEach(star => {
        star.update();
        star.draw();
    });

    requestAnimationFrame(animate);
}

window.addEventListener('resize', () => {
    resize();
    stars = [];
    for (let i = 0; i < STAR_COUNT; i++) {
        stars.push(new Star());
    }
});

init();

// Glitch Text Effect
const glitchText = document.querySelector('.glitch');
if (glitchText) {
    setInterval(() => {
        glitchText.classList.add('active');
        setTimeout(() => {
            glitchText.classList.remove('active');
        }, 200);
    }, 3000);
}

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Live Clock in Mock UI
function updateMockClock() {
    const timeDisplay = document.querySelector('.time-display');
    const dateDisplay = document.querySelector('.date-display');
    
    if (timeDisplay && dateDisplay) {
        const now = new Date();
        timeDisplay.textContent = now.toLocaleTimeString('en-US', { hour12: false });
        dateDisplay.textContent = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    }
}

setInterval(updateMockClock, 1000);
updateMockClock();
