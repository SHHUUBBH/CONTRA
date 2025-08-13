/**
 * CONTRA - Animations using GSAP
 * Adds smooth animations, transitions, and scroll effects
 */

document.addEventListener('DOMContentLoaded', function() {
    // Detect if we're on a mobile device
    const isMobile = window.matchMedia("(max-width: 768px)").matches || 
                    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // Initialize GSAP animations only if GSAP is loaded
    if (typeof gsap !== 'undefined') {
        console.log('GSAP animations initialized');
        initializeAnimations(isMobile);
    } else {
        console.warn('GSAP not loaded - animations disabled');
    }
});

function initializeAnimations(isMobile) {
    // Initialize scroll animations with ScrollTrigger
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
        initScrollAnimations(isMobile);
    }
    
    // Initialize page transitions and UI animations
    initPageTransitions(isMobile);
    initUIAnimations(isMobile);
    initChatboxAnimations(isMobile);
    initLogoAnimations(isMobile);
    
    // Custom animations for specific elements if they exist
    const footerLogo = document.getElementById('footer-logo');
    if (footerLogo) {
        animateFooterLogo(footerLogo, isMobile);
    }
}

/**
 * Initialize scroll-based animations
 */
function initScrollAnimations(isMobile) {
    // Animate elements when they enter the viewport
    const animateOnScroll = document.querySelectorAll('.animate-on-scroll');
    
    animateOnScroll.forEach(element => {
        gsap.set(element, { 
            opacity: 0,
            y: isMobile ? 10 : 20 // Reduced movement for mobile
        });
        
        ScrollTrigger.create({
            trigger: element,
            start: 'top 85%',
            onEnter: () => {
                gsap.to(element, {
                    opacity: 1,
                    y: 0,
                    duration: isMobile ? 0.6 : 0.8, // Faster animations on mobile
                    ease: 'power2.out'
                });
            },
            once: true
        });
    });
    
    // Staggered animations for container children
    const staggerContainers = document.querySelectorAll('.footer-links, .social-links, .data-sources');
    
    staggerContainers.forEach(container => {
        const children = container.children;
        
        ScrollTrigger.create({
            trigger: container,
            start: 'top 85%',
            onEnter: () => {
                gsap.from(children, {
                    opacity: 0,
                    y: isMobile ? 10 : 15,
                    stagger: isMobile ? 0.05 : 0.1, // Faster stagger on mobile
                    duration: isMobile ? 0.4 : 0.6,
                    ease: 'power2.out'
                });
            },
            once: true
        });
    });
    
    // Parallax effect for background elements - only on desktop
    if (!isMobile) {
        gsap.to('.cyber-grid', {
            yPercent: -20,
            ease: 'none',
            scrollTrigger: {
                trigger: 'body',
                start: 'top top',
                end: 'bottom top',
                scrub: 0.5
            }
        });
    }
}

/**
 * Initialize UI animations for interactive elements
 */
function initUIAnimations(isMobile) {
    // Buttons hover effect - reduced on mobile
    const buttons = document.querySelectorAll('.btn');
    
    if (!isMobile) {
        buttons.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                gsap.to(btn, {
                    scale: 1.05,
                    duration: 0.3,
                    ease: 'power2.out',
                    boxShadow: '0 5px 15px rgba(0,0,0,0.2)'
                });
            });
            
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, {
                    scale: 1,
                    duration: 0.3,
                    ease: 'power2.out',
                    boxShadow: 'none'
                });
            });
        });
    }
    
    // Animate form fields on focus
    const formInputs = document.querySelectorAll('input, textarea, select');
    
    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            const label = input.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                gsap.to(label, {
                    color: 'var(--color-purple)',
                    duration: 0.3,
                    ease: 'power2.out'
                });
            }
        });
        
        input.addEventListener('blur', () => {
            const label = input.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                gsap.to(label, {
                    color: 'var(--color-foreground)',
                    duration: 0.3,
                    ease: 'power2.out'
                });
            }
        });
    });
    
    // Generate button pulsing effect - simpler on mobile
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        const tl = gsap.timeline({repeat: -1, repeatDelay: isMobile ? 4 : 3});
        tl.to(generateBtn, {
            boxShadow: '0 0 15px rgba(139, 92, 246, 0.7)',
            duration: isMobile ? 1.5 : 1,
            ease: 'power2.inOut'
        });
        tl.to(generateBtn, {
            boxShadow: '0 0 5px rgba(139, 92, 246, 0.3)',
            duration: isMobile ? 1.5 : 1,
            ease: 'power2.inOut'
        });
    }
}

/**
 * Initialize animations for the chatbox UI
 */
function initChatboxAnimations(isMobile) {
    // Animate the conversation container
    const conversationContainer = document.querySelector('.conversation-container');
    if (conversationContainer) {
        // Setup initial state
        gsap.set(conversationContainer, {
            clipPath: 'inset(0% 0% 100% 0%)',
            autoAlpha: 0
        });
        
        // Create a ScrollTrigger for revealing the chatbox
        ScrollTrigger.create({
            trigger: conversationContainer,
            start: 'top 80%',
            onEnter: () => {
                gsap.to(conversationContainer, {
                    clipPath: 'inset(0% 0% 0% 0%)',
                    autoAlpha: 1,
                    duration: isMobile ? 0.7 : 1,
                    ease: 'power3.out'
                });
            },
            once: true
        });
        
        // Enhance chat message animations
        const chatSubmit = document.getElementById('chat-submit');
        const chatInput = document.getElementById('chat-input');
        const chatHistory = document.getElementById('chat-history');
        
        if (chatSubmit && chatInput && chatHistory) {
            // Initial focus animation for the input
            chatInput.addEventListener('focus', () => {
                gsap.to(chatInput, {
                    borderColor: 'var(--color-purple)',
                    boxShadow: '0 0 0 3px rgba(139, 92, 246, 0.3)',
                    duration: 0.3,
                    ease: 'power2.out'
                });
            });
            
            chatInput.addEventListener('blur', () => {
                gsap.to(chatInput, {
                    borderColor: 'var(--color-border)',
                    boxShadow: 'none',
                    duration: 0.3,
                    ease: 'power2.out'
                });
            });
        }
    }
}

/**
 * Initialize animated page transitions
 */
function initPageTransitions(isMobile) {
    // Animate the page load transition
    const mainContent = document.querySelector('main');
    if (mainContent) {
        gsap.from(mainContent, {
            opacity: 0,
            y: isMobile ? 10 : 20,
            duration: isMobile ? 0.6 : 0.8,
            delay: isMobile ? 0.3 : 0.5,
            ease: 'power2.out'
        });
    }
    
    // Animate navigation links - simpler on mobile
    const navLinks = document.querySelectorAll('.nav-link');
    
    gsap.from(navLinks, {
        opacity: 0,
        y: isMobile ? -5 : -10,
        stagger: isMobile ? 0.07 : 0.1,
        duration: isMobile ? 0.4 : 0.6,
        delay: isMobile ? 0.5 : 0.8,
        ease: 'power2.out'
    });
    
    // Tab switching animations
    const tabLinks = document.querySelectorAll('.tab-link');
    
    tabLinks.forEach(tab => {
        tab.addEventListener('click', function(e) {
            // Find the target tab content
            const targetTab = this.getAttribute('data-tab');
            const targetContent = document.getElementById(`${targetTab}-tab`);
            
            if (targetContent) {
                // Animate the tab transition
                gsap.fromTo(targetContent, 
                    { opacity: 0, y: isMobile ? 5 : 10 },
                    { 
                        opacity: 1, 
                        y: 0, 
                        duration: isMobile ? 0.3 : 0.5, 
                        ease: 'power2.out',
                        clearProps: 'opacity,transform' 
                    }
                );
            }
        });
    });
}

/**
 * Animate the logo with a glowing effect
 */
function initLogoAnimations(isMobile) {
    const logos = document.querySelectorAll('.logo');
    
    logos.forEach(logo => {
        // Only add hover effects on desktop
        if (!isMobile) {
            // Create a subtle hover effect
            logo.addEventListener('mouseenter', () => {
                gsap.to(logo, {
                    textShadow: '0 0 15px rgba(139, 92, 246, 0.8)',
                    scale: 1.05,
                    duration: 0.5,
                    ease: 'power2.out'
                });
            });
            
            logo.addEventListener('mouseleave', () => {
                gsap.to(logo, {
                    textShadow: '0 0 8px rgba(255, 255, 255, 0.4)',
                    scale: 1,
                    duration: 0.5,
                    ease: 'power2.out'
                });
            });
        }
        
        // Gentle pulsing animation - slower on mobile to save resources
        const tl = gsap.timeline({repeat: -1, yoyo: true});
        tl.to(logo, {
            textShadow: '0 0 12px rgba(139, 92, 246, 0.6)',
            duration: isMobile ? 3 : 2,
            ease: 'sine.inOut'
        });
        tl.to(logo, {
            textShadow: '0 0 8px rgba(255, 255, 255, 0.4)',
            duration: isMobile ? 3 : 2,
            ease: 'sine.inOut'
        });
    });
}

/**
 * Special animation for the footer logo
 */
function animateFooterLogo(footerLogo, isMobile) {
    // Create an observer for when the footer comes into view
    ScrollTrigger.create({
        trigger: footerLogo,
        start: 'top 90%',
        onEnter: () => {
            // Animate the logo and the text
            gsap.from(footerLogo.querySelector('.logo'), {
                y: isMobile ? 15 : 30,
                opacity: 0,
                duration: isMobile ? 0.7 : 1,
                ease: 'back.out(1.7)'
            });
            
            gsap.from(footerLogo.querySelector('p'), {
                y: isMobile ? 10 : 20,
                opacity: 0,
                duration: isMobile ? 0.7 : 1,
                delay: isMobile ? 0.2 : 0.3,
                ease: 'power2.out'
            });
        },
        once: true
    });
}

/**
 * CONTRA - Enhanced animations 
 * Adds modern 3D effects, parallax, and scroll animations
 */

document.addEventListener('DOMContentLoaded', () => {
    // Detect if we're on a mobile device
    const isMobile = window.matchMedia("(max-width: 768px)").matches || 
                    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        // Force navbar to be visible
        navbar.style.display = 'block';
        
        // Add scrolled class if page is already scrolled
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        }
        
        // Add scroll event listener
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Feature card 3D hover effect - only on desktop
    const featureCards = document.querySelectorAll('.feature-card');
    if (!isMobile) {
        featureCards.forEach(card => {
            card.addEventListener('mousemove', e => {
                const cardRect = card.getBoundingClientRect();
                const cardCenterX = cardRect.left + cardRect.width / 2;
                const cardCenterY = cardRect.top + cardRect.height / 2;
                const mouseX = e.clientX - cardCenterX;
                const mouseY = e.clientY - cardCenterY;
                
                // Calculate rotation based on mouse position
                const rotateY = mouseX / 10;
                const rotateX = -mouseY / 10;
                
                // Apply the 3D rotation transform
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
                
                // Apply highlight effect
                const glowX = (e.clientX - cardRect.left) / cardRect.width * 100;
                const glowY = (e.clientY - cardRect.top) / cardRect.height * 100;
                card.style.background = `radial-gradient(circle at ${glowX}% ${glowY}%, rgba(50, 50, 75, 0.8), rgba(31, 41, 55, 0.7))`;
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
                card.style.background = '';
            });
        });
    } else {
        // Add a simpler hover effect for mobile
        featureCards.forEach(card => {
            card.addEventListener('touchstart', () => {
                card.style.transform = 'translateY(-5px)';
                card.style.background = 'rgba(40, 44, 52, 0.7)';
            });
            
            card.addEventListener('touchend', () => {
                setTimeout(() => {
                    card.style.transform = '';
                    card.style.background = '';
                }, 300);
            });
        });
    }

    // Scroll-triggered animations
    const animateOnScroll = entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    };

    // Create an intersection observer
    const observer = new IntersectionObserver(animateOnScroll, {
        root: null,
        threshold: 0.1,
        rootMargin: '-50px'
    });

    // Target elements to animate on scroll
    const elementsToAnimate = document.querySelectorAll('.about-section, .feature-card, .process-step, .tech-category, .status-section');
    elementsToAnimate.forEach(element => {
        element.classList.add('animate-on-scroll');
        observer.observe(element);
    });

    // Parallax effect for hero section - only on desktop
    const heroSection = document.querySelector('.hero');
    if (heroSection && !isMobile) {
        window.addEventListener('scroll', () => {
            const scrollPos = window.scrollY;
            const heroContent = heroSection.querySelector('.hero-content');
            if (heroContent) {
                heroContent.style.transform = `translateY(${scrollPos * 0.3}px)`;
            }
        });
    }

    // Particle grid animation for background - optimized for mobile
    createParticleGrid(isMobile);
});

// Create animated particle grid background
function createParticleGrid(isMobile) {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Create particles - reduce count on mobile
    const particles = [];
    const baseCount = Math.floor(canvas.width * canvas.height / 10000);
    const particleCount = isMobile ? Math.min(baseCount, 30) : baseCount;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * (isMobile ? 1.5 : 2) + 1,
            speedX: (Math.random() - 0.5) * (isMobile ? 0.3 : 0.5),
            speedY: (Math.random() - 0.5) * (isMobile ? 0.3 : 0.5),
            color: `rgba(${Math.floor(Math.random() * 100 + 150)}, ${Math.floor(Math.random() * 100 + 150)}, ${Math.floor(Math.random() * 255)}, ${Math.random() * 0.5 + 0.3})`
        });
    }

    // Animate particles
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw and update particles
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
            
            // Update position
            p.x += p.speedX;
            p.y += p.speedY;
            
            // Boundary check
            if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
            if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
            
            // Draw connections - fewer connections on mobile
            if (!isMobile || i % 2 === 0) { // Skip some connections on mobile
                for (let j = i + 1; j < particles.length; j++) {
                    if (isMobile && j % 2 === 1) continue; // Skip even more on mobile
                    
                    const p2 = particles[j];
                    const distance = Math.sqrt((p.x - p2.x) ** 2 + (p.y - p2.y) ** 2);
                    
                    // Shorter connection distance on mobile
                    const maxDistance = isMobile ? 100 : 150;
                    
                    if (distance < maxDistance) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(255, 255, 255, ${(maxDistance - distance) / (maxDistance * 10)})`;
                        ctx.lineWidth = isMobile ? 0.3 : 0.5;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    // Resize handler
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        // Update mobile detection on resize
        const isMobileUpdated = window.matchMedia("(max-width: 768px)").matches;
        
        // Only resize particles if device type changed
        if (isMobileUpdated !== isMobile) {
            // Clear existing particles
            particles.length = 0;
            
            // Create new particles adjusted for device type
            const baseCount = Math.floor(canvas.width * canvas.height / 10000);
            const newParticleCount = isMobileUpdated ? Math.min(baseCount, 30) : baseCount;
            
            for (let i = 0; i < newParticleCount; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * (isMobileUpdated ? 1.5 : 2) + 1,
                    speedX: (Math.random() - 0.5) * (isMobileUpdated ? 0.3 : 0.5),
                    speedY: (Math.random() - 0.5) * (isMobileUpdated ? 0.3 : 0.5),
                    color: `rgba(${Math.floor(Math.random() * 100 + 150)}, ${Math.floor(Math.random() * 100 + 150)}, ${Math.floor(Math.random() * 255)}, ${Math.random() * 0.5 + 0.3})`
                });
            }
        }
    });
}

// Ensure navbar appears on page load
document.addEventListener('DOMContentLoaded', function() {
    // Make sure navbar is visible
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        // Force navbar to be visible
        navbar.style.display = 'block';
        
        // Add scrolled class if page is already scrolled
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        }
        
        // Add scroll event listener
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
    
    // Highlight current page in navigation
    const currentPath = window.location.pathname;
    
    // Desktop nav links
    const desktopNavLinks = document.querySelectorAll('.desktop-nav .nav-link');
    desktopNavLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (
            (linkPath === '/' && (currentPath === '/' || currentPath === '/index')) ||
            (linkPath !== '/' && currentPath.includes(linkPath))
        ) {
            link.classList.add('active');
        }
    });
    
    // Mobile nav links
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
    mobileNavLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (
            (linkPath === '/' && (currentPath === '/' || currentPath === '/index')) ||
            (linkPath !== '/' && currentPath.includes(linkPath))
        ) {
            link.classList.add('active');
        }
    });
    
    // Enhanced mobile menu toggle
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    
    if (menuToggle && mobileNav) {
        menuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileNav.classList.toggle('active');
            
            // Prevent scrolling when menu is open
            document.body.style.overflow = mobileNav.classList.contains('active') ? 'hidden' : '';
        });
        
        // Close mobile menu when clicking on a mobile nav link
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => {
                menuToggle.classList.remove('active');
                mobileNav.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (mobileNav.classList.contains('active') && 
                !mobileNav.contains(e.target) && 
                !menuToggle.contains(e.target)) {
                menuToggle.classList.remove('active');
                mobileNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
}); 