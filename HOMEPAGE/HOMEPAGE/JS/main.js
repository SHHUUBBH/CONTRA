// Make scrollToTop function available globally
window.scrollToTop = function() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Preload animated GIFs to prevent flicker
function preloadImages() {
  const gifImages = [
    'assets/videos/proccessor.gif',
    'assets/videos/futuristic empire.gif',
    'assets/videos/Glitch Hacking.gif'
  ];
  
  gifImages.forEach(src => {
    const img = new Image();
    img.src = src;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  // Preload images
  preloadImages();
  
  // Initialize step video hover functionality
  initStepVideoHover();
  
  // Hide loader when page is loaded
  setTimeout(() => {
    document.querySelector('.loader-wrapper').classList.add('loader-disappear');
    // Enable custom cursor after loader disappears
    setTimeout(() => {
      document.body.style.cursor = 'none';
      initCustomCursor();
      
      // Reset and trigger navbar and hero animations after loader disappears
      resetNavbarAndHeroAnimations();
    }, 500);
  }, 1500);

  // Function to handle step card hover video functionality
  function initStepVideoHover() {
    // Get elements
    const steps = document.querySelectorAll('.step');
    const holoDisplay = document.querySelector('.holographic-display');
    const holoVideo = document.querySelector('#holo-video');
    const holoCloseBtn = document.querySelector('#holo-close');
    
    if (!steps.length || !holoDisplay || !holoVideo || !holoCloseBtn) return;
    
    // Add a specific class to the body when holographic display is active to prevent scrolling
    function toggleBodyScroll(isLocked) {
      if (isLocked) {
        document.body.classList.add('holo-active');
        document.body.style.overflow = 'hidden';
      } else {
        document.body.classList.remove('holo-active');
        document.body.style.overflow = '';
      }
    }
    
    // Create holographic glitch effect
    function createHoloGlitch() {
      const holoGlitch = document.querySelector('.holo-glitch');
      if (!holoGlitch) return;
      
      // Create random glitch lines
      setInterval(() => {
        if (holoDisplay.classList.contains('active')) {
          const randomHeight = Math.floor(Math.random() * 100);
          const randomWidth = Math.floor(Math.random() * 100);
          const randomDuration = Math.floor(Math.random() * 200) + 50;
          
          const glitchLine = document.createElement('div');
          glitchLine.style.position = 'absolute';
          glitchLine.style.top = `${randomHeight}%`;
          glitchLine.style.width = `${randomWidth}%`;
          glitchLine.style.height = '1px';
          glitchLine.style.backgroundColor = 'rgba(0, 183, 255, 0.7)';
          glitchLine.style.opacity = '0.5';
          glitchLine.style.left = Math.random() > 0.5 ? '0' : 'auto';
          glitchLine.style.right = Math.random() > 0.5 ? '0' : 'auto';
          glitchLine.style.zIndex = '10';
          
          holoGlitch.appendChild(glitchLine);
          
          // Remove the glitch line after animation
          setTimeout(() => {
            holoGlitch.removeChild(glitchLine);
          }, randomDuration);
        }
      }, 1000);
    }
    
    // Initialize holographic particles
    function initHoloParticles() {
      const particlesContainer = document.querySelector('.holo-particles');
      if (!particlesContainer) return;
      
      // Create additional particles
      for (let i = 0; i < 10; i++) {
        const particle = document.createElement('div');
        particle.className = 'holo-particle';
        particle.style.position = 'absolute';
        particle.style.width = '3px';
        particle.style.height = '3px';
        particle.style.backgroundColor = 'rgba(0, 183, 255, 0.6)';
        particle.style.borderRadius = '50%';
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.boxShadow = '0 0 3px rgba(0, 183, 255, 0.8)';
        
        // Random animation properties
        const duration = Math.random() * 10 + 5; // 5-15 seconds
        const delay = Math.random() * 5;
        
        particle.style.animation = `float-particle ${duration}s ease-in-out ${delay}s infinite`;
        
        particlesContainer.appendChild(particle);
      }
    }
    
    // Show holographic display with the selected video
    function showHolographicDisplay(videoSrc, activeStep) {
      // Set video source and load
      const videoSource = holoVideo.querySelector('source');
      if (videoSource) {
        videoSource.src = videoSrc;
      } else {
        const newSource = document.createElement('source');
        newSource.src = videoSrc;
        newSource.type = 'video/mp4';
        holoVideo.appendChild(newSource);
      }
      
      // Reload and play video
      holoVideo.load();
      
      // Activate the holographic display with delay for smoother transition
      setTimeout(() => {
        holoDisplay.classList.add('active');
        toggleBodyScroll(true);
        
        // Play video after transition
        setTimeout(() => {
          holoVideo.play().catch(err => {
            console.warn('Holographic video play error:', err);
          });
        }, 500);
      }, 100);
      
      // Mark the active step
      steps.forEach(step => step.classList.remove('active-holo'));
      if (activeStep) {
        activeStep.classList.add('active-holo');
      }
    }
    
    // Hide holographic display
    function hideHolographicDisplay() {
      // Pause the video
      holoVideo.pause();
      
      // Hide display
      holoDisplay.classList.remove('active');
      toggleBodyScroll(false);
      
      // Remove active state from steps
      steps.forEach(step => step.classList.remove('active-holo'));
    }
    
    // Event listeners for steps
    steps.forEach(step => {
      const triggerBtn = step.querySelector('.step-projection-trigger');
      let videoSrc = step.getAttribute('data-video');
      
      if (!videoSrc || !triggerBtn) return;
      
      // Add full path to video if needed
      if (!videoSrc.includes('/')) {
        videoSrc = `./${videoSrc}`;
      }
      
      // Preload the video
      const tempVideo = document.createElement('video');
      tempVideo.src = videoSrc;
      tempVideo.preload = 'auto';
      tempVideo.style.display = 'none';
      document.body.appendChild(tempVideo);
      setTimeout(() => {
        try {
          document.body.removeChild(tempVideo);
        } catch (e) {
          console.warn("Failed to remove temp video element", e);
        }
      }, 5000);
      
      // Add click event to trigger button
      triggerBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent event bubbling
        showHolographicDisplay(videoSrc, step);
      });
      
      // Also allow clicking the entire step to show the video
      step.addEventListener('click', () => {
        showHolographicDisplay(videoSrc, step);
      });
    });
    
    // Close button event
    holoCloseBtn.addEventListener('click', () => {
      hideHolographicDisplay();
    });
    
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && holoDisplay.classList.contains('active')) {
        hideHolographicDisplay();
      }
    });
    
    // Initialize holographic effects
    createHoloGlitch();
    initHoloParticles();
  }

  // Function to reset and trigger navbar and hero animations
  function resetNavbarAndHeroAnimations() {
    // Reset and animate navbar elements
    gsap.from(".logo, .nav-link, .navbar-buttons .btn", {
      y: -50,
      opacity: 0,
      stagger: 0.08,
      duration: 0.6,
      ease: "power3.out",
      clearProps: "all" // Clear all props after animation completes
    });
    
    // Reset and animate hero content
    gsap.from(".hero-content", {
      opacity: 0,
      y: 30,
      duration: 0.6,
      ease: "power2.out",
      delay: 0.2,
      clearProps: "all" // Clear all props after animation completes
    });
  }

  // Initialize custom cursor
  function initCustomCursor() {
    const cursorDot = document.querySelector('.cursor-dot');
    const cursorOutline = document.querySelector('.cursor-dot-outline');

    if (!cursorDot || !cursorOutline) return;
    
    // Remove glow point for grid
    // const glowPoint = document.createElement('div');
    // glowPoint.className = 'glow-point';
    // document.body.appendChild(glowPoint);
    
    // Get reference to cyber-grid
    const cyberGrid = document.querySelector('.cyber-grid');
    
    // Remove GSAP animation for the grid glow
    // let gridGlowTl = gsap.timeline({ paused: true });
    // gridGlowTl.to(cyberGrid, {
    //   boxShadow: '0 0 100px 20px rgba(139, 92, 246, 0.3)',
    //   duration: 0.5,
    //   ease: 'power2.out'
    // });

    // Variables for performance optimization
    let lastMouseX = 0;
    let lastMouseY = 0;
    let rafId = null;

    const moveCursor = (e) => {
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;

      // Use requestAnimationFrame for smoother animation
      if (!rafId) {
        rafId = requestAnimationFrame(updateCursorPosition);
      }
    };

    const updateCursorPosition = () => {
      // Update dot position immediately for responsive feel
      cursorDot.style.left = `${lastMouseX}px`;
      cursorDot.style.top = `${lastMouseY}px`;

      // Add a small delay to outline for trail effect
      gsap.to(cursorOutline, {
        left: lastMouseX,
        top: lastMouseY,
        duration: 0.15,
        ease: "power2.out"
      });
      
      // Remove grid glow effect code
      // Move glow point to cursor position
      // glowPoint.style.left = `${lastMouseX}px`;
      // glowPoint.style.top = `${lastMouseY}px`;
      
      // Remove Add grid glow effect based on cursor position
      // if (cyberGrid) {
      //   // Get grid cell position based on cursor
      //   const cellSize = 40; // Grid cell size from CSS
      //   const gridX = Math.floor(lastMouseX / cellSize) * cellSize;
      //   const gridY = Math.floor(lastMouseY / cellSize) * cellSize;
        
      //   // Calculate intensity based on mouse movement speed
      //   let intensity = 0.15;
      //   let mouseSpeed = 0;
        
      //   // Track mouse speed for more dynamic effects
      //   if (window.prevMouseX !== undefined) {
      //     mouseSpeed = Math.sqrt(
      //       Math.pow(lastMouseX - window.prevMouseX, 2) + 
      //       Math.pow(lastMouseY - window.prevMouseY, 2)
      //     );
          
      //     // Increase intensity with mouse speed (capped)
      //     intensity = Math.min(0.3, 0.15 + (mouseSpeed * 0.002));
          
      //     // Adjust glow point size based on speed
      //     const glowSize = 200 + (mouseSpeed * 2);
      //     glowPoint.style.width = `${glowSize}px`;
      //     glowPoint.style.height = `${glowSize}px`;
          
      //     // Adjust opacity based on speed
      //     glowPoint.style.opacity = 0.7 + (mouseSpeed * 0.005);
      //   }
        
      //   // Store current position for next frame
      //   window.prevMouseX = lastMouseX;
      //   window.prevMouseY = lastMouseY;
        
      //   // Always add the glow class but adjust the custom properties
      //   cyberGrid.classList.add('cyber-grid-glow');
      //   cyberGrid.style.setProperty('--grid-glow-opacity', intensity);
      //   cyberGrid.style.setProperty('--grid-glow-x', `${gridX}px`);
      //   cyberGrid.style.setProperty('--grid-glow-y', `${gridY}px`);
        
      //   // Animate the grid glow based on mouse speed
      //   if (mouseSpeed > 10) {
      //     // Speed up the timeline progress based on mouse speed
      //     const timelineProgress = Math.min(1, mouseSpeed / 50);
      //     gridGlowTl.progress(timelineProgress);
      //   } else {
      //     // Slowly return to normal when mouse is still
      //     gridGlowTl.progress(0);
      //   }
      // }

      // Show cursors after they've been positioned
      if (!cursorDot.classList.contains('cursor-active')) {
        cursorDot.classList.add('cursor-active');
        cursorOutline.classList.add('cursor-active');
      }

      rafId = null;
    };

    // Add click animation
    document.addEventListener('mousedown', () => {
      cursorDot.classList.add('cursor-clicking');
      cursorOutline.classList.add('cursor-clicking');
    });

    document.addEventListener('mouseup', () => {
      cursorDot.classList.remove('cursor-clicking');
      cursorOutline.classList.remove('cursor-clicking');
    });

    // Remove any existing event listener first
    window.removeEventListener('mousemove', moveCursor);
    // Add the event listener
    window.addEventListener('mousemove', moveCursor);

    // Expand cursor on clickable elements
    const clickableElements = document.querySelectorAll('a, button, .view-card-btn, .social-link, .nav-link, input, textarea, select, [role="button"]');
    
    clickableElements.forEach(el => {
      el.addEventListener('mouseenter', () => {
        cursorOutline.classList.add('cursor-expand');
        cursorDot.classList.add('cursor-expand');
      });
      
      el.addEventListener('mouseleave', () => {
        cursorOutline.classList.remove('cursor-expand');
        cursorDot.classList.remove('cursor-expand');
      });
    });

    // Hide cursor when mouse leaves window
    document.addEventListener('mouseleave', () => {
      cursorDot.classList.remove('cursor-active');
      cursorOutline.classList.remove('cursor-active');
    });
    
    // Show cursor when mouse enters window
    document.addEventListener('mouseenter', () => {
      cursorDot.classList.add('cursor-active');
      cursorOutline.classList.add('cursor-active');
    });
  }

  // Register GSAP plugins
  gsap.registerPlugin(ScrollTrigger, ScrollToPlugin)

  // Set current year in footer
  document.getElementById("current-year").textContent = new Date().getFullYear()

  // Add ScrollTrigger for all glitch-text elements
  const glitchTextElements = document.querySelectorAll('.glitch-text');
  glitchTextElements.forEach(glitchText => {
    ScrollTrigger.create({
      trigger: glitchText,
      start: "top 85%",
      end: "bottom 15%",
      toggleClass: {targets: glitchText, className: "glitch-active"},
      toggleActions: "play reverse play reverse",
      onEnter: () => {
        gsap.fromTo(glitchText, 
          { opacity: 0, y: 15 }, 
          { 
            opacity: 1, 
            y: 0, 
            duration: 0.6,
            ease: "power2.out"
          }
        );
      },
      onLeave: () => {
        gsap.to(glitchText, {
          opacity: 0.7,
          y: -5,
          duration: 0.4,
          ease: "power2.in"
        });
      },
      onEnterBack: () => {
        gsap.to(glitchText, {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: "power2.out"
        });
      },
      onLeaveBack: () => {
        gsap.to(glitchText, {
          opacity: 0.7,
          y: 15,
          duration: 0.4,
          ease: "power2.in"
        });
      }
    });
  });

  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector(".mobile-menu-toggle")
  const mobileNav = document.querySelector(".mobile-nav")

  mobileMenuToggle.addEventListener("click", function () {
    this.classList.toggle("active")
    mobileNav.classList.toggle("active")
    document.body.classList.toggle("no-scroll")
  })

  // Close mobile menu when clicking a link
  const mobileNavLinks = document.querySelectorAll(".mobile-nav-link")
  mobileNavLinks.forEach((link) => {
    link.addEventListener("click", () => {
      mobileMenuToggle.classList.remove("active")
      mobileNav.classList.remove("active")
      document.body.classList.remove("no-scroll")
    })
  })

  // Navbar animations - Initial load animation, will be reset after loader
  gsap.from(".logo, .nav-link, .navbar-buttons .btn", {
    y: -50,
    opacity: 0,
    stagger: 0.08,
    duration: 0.6,
    ease: "power3.out",
    delay: 0.1,
  })

  // Feature section animations with improved scroll trigger
  const featureItems = document.querySelectorAll(".feature-item")

  featureItems.forEach((item, index) => {
    const isEven = index % 2 === 0

    // Animate feature content with more pronounced effect
    ScrollTrigger.create({
      trigger: item,
      start: "top 85%", 
      toggleActions: "play reverse restart reverse", // Controls animation sequence: play on enter, reverse on leave, restart on re-enter, reverse on re-leave
      onEnter: () => {
        // Animation for elements inside feature without hiding the feature itself
        gsap.from(item.querySelectorAll('.feature-icon, .feature-description, .feature-divider'), {
          y: 30,
          opacity: 0,
          stagger: 0.15,
          duration: 0.7,
          ease: "back.out(1.2)",
        })

        // Animate the feature visual with a different effect
        gsap.from(item.querySelector('.feature-visual'), {
          scale: 0.95,
          opacity: 0.5,
          duration: 0.8,
          ease: "power2.out",
        })

        // Animate glowing orb if it exists
        const glowOrb = item.querySelector(".glow-orb");
        if (glowOrb) {
          gsap.to(glowOrb, {
            boxShadow: isEven
              ? "var(--shadow-glow-purple)"
              : index === 1
                ? "var(--shadow-glow-cyan)"
                : "var(--shadow-glow-emerald)",
            scale: 1.1,
            duration: 0.8,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut",
          })
        }
      }
    })
  })

  // Footer animations with enhanced effects
  ScrollTrigger.create({
    trigger: ".footer",
    start: "top 85%",
    toggleActions: "play reverse restart reverse", // Add the same behavior to footer animations
    onEnter: () => {
      // Main footer elements with stagger
      gsap.from(".footer-main .footer-logo, .footer-description, .social-links", {
        y: 40,
        opacity: 0,
        stagger: 0.15,
        duration: 0.6,
        ease: "power2.out",
      });
      
      // Social links with bounce effect
      gsap.from(".social-link", {
        scale: 0,
        opacity: 0,
        stagger: 0.1,
        duration: 0.5,
        delay: 0.4,
        ease: "back.out(1.7)",
      });
      
      // Credit profiles with a different animation
      gsap.from(".profile", {
        y: 50,
        opacity: 0,
        stagger: 0.2,
        duration: 0.7,
        delay: 0.3,
        ease: "power2.out",
      });
      
      // Footer bottom fade in
      gsap.from(".footer-bottom", {
        y: 20,
        opacity: 0,
        duration: 0.4,
        delay: 0.6,
        ease: "power2.out",
      });
    }
  })

  // Smooth scrolling for all links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (!targetElement) return;
      
      // Get navbar height for offset
      const navbarHeight = document.querySelector('.navbar').offsetHeight;
      
      // Use GSAP for smooth scrolling with a nice easing
      gsap.to(window, {
        duration: 0.2,
        scrollTo: {
          y: targetElement,
          offsetY: navbarHeight + 20
        },
        ease: "power2.out" // Changed from power3.inOut to power2.out for quicker response
      });
    });
  });

  // Ensure cursor is visible across all sections by refreshing it on scroll
  window.addEventListener('scroll', function() {
    // Check if custom cursor is active
    const cursorDot = document.querySelector('.cursor-dot');
    if (cursorDot && !cursorDot.classList.contains('cursor-active')) {
      document.body.style.cursor = 'none';
      
      // Force cursor to update position
      const event = new MouseEvent('mousemove', {
        'view': window,
        'bubbles': true,
        'cancelable': true,
        'clientX': cursorDot.getBoundingClientRect().left || 100,
        'clientY': cursorDot.getBoundingClientRect().top || 100
      });
      document.dispatchEvent(event);
    }
  });

  // Add improved loading of feature items with Intersection Observer
  function setupFeatureIntersectionObserver() {
    const featureItems = document.querySelectorAll('.feature-item');
    
    if ('IntersectionObserver' in window) {
      const featureObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const item = entry.target;
            const index = Array.from(featureItems).indexOf(item);
            const isEven = index % 2 === 0;
            
            // Fade in the feature content
            gsap.fromTo(item.querySelector('.feature-content'), 
              { opacity: 0, x: isEven ? -30 : 30 }, 
              { opacity: 1, x: 0, duration: 0.7, ease: "power2.out" }
            );
            
            // Animate the feature visual with a different effect
            gsap.fromTo(item.querySelector('.feature-visual'), 
              { opacity: 0, scale: 0.95 }, 
              { opacity: 1, scale: 1, duration: 0.8, delay: 0.2, ease: "power2.out" }
            );
            
            // Unobserve after animating
            featureObserver.unobserve(item);
          }
        });
      }, {
        threshold: 0.2,
        rootMargin: '0px 0px -100px 0px'
      });
      
      featureItems.forEach(item => {
        featureObserver.observe(item);
      });
    }
  }
  
  // Call the function after page loads
  window.addEventListener('load', setupFeatureIntersectionObserver);
})

document.querySelectorAll('.view-card-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetId = btn.getAttribute('data-card');
    document.getElementById(targetId).classList.add('active');
  });
});

document.querySelectorAll('.close-card').forEach(closeBtn => {
  closeBtn.addEventListener('click', (e) => {
    const modal = e.currentTarget.closest('.cyber-card-modal');
    if (modal) {
      modal.classList.remove('active');
    }
  });
});

// Update copyright year
document.getElementById('current-year').textContent = new Date().getFullYear();

// Holographic Video Display Enhancement with Fallback
document.addEventListener('DOMContentLoaded', function() {
  // Get elements
  const steps = document.querySelectorAll('.step');
  const holoDisplay = document.querySelector('.holographic-display');
  const holoVideo = document.getElementById('holo-video');
  const closeBtn = document.getElementById('holo-close');
  
  // Set base path for videos and fallback video
  const videoBasePath = 'assets/videos/';
  const fallbackVideo = 'assets/videos/fallback.mp4'; // This will be used if a specific video can't be loaded

  // Create placeholder video
  function createPlaceholderVideo() {
    console.log("Creating placeholder video display");
    
    // Create a canvas element to simulate a video
    const placeholderCanvas = document.createElement('canvas');
    placeholderCanvas.width = 1280;
    placeholderCanvas.height = 720;
    placeholderCanvas.style.position = 'absolute';
    placeholderCanvas.style.top = '0';
    placeholderCanvas.style.left = '0';
    placeholderCanvas.style.width = '100%';
    placeholderCanvas.style.height = '100%';
    placeholderCanvas.style.zIndex = '1';
    
    // Get the canvas context
    const ctx = placeholderCanvas.getContext('2d');
    
    // Animation function
    function animatePlaceholder() {
      // Clear canvas
      ctx.clearRect(0, 0, placeholderCanvas.width, placeholderCanvas.height);
      
      // Fill background
      ctx.fillStyle = 'rgba(10, 20, 30, 0.8)';
      ctx.fillRect(0, 0, placeholderCanvas.width, placeholderCanvas.height);
      
      // Draw grid
      ctx.strokeStyle = 'rgba(0, 195, 255, 0.3)';
      ctx.lineWidth = 1;
      
      // Grid lines
      const gridSize = 40;
      for (let x = 0; x < placeholderCanvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, placeholderCanvas.height);
        ctx.stroke();
      }
      
      for (let y = 0; y < placeholderCanvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(placeholderCanvas.width, y);
        ctx.stroke();
      }
      
      // Draw pulsing circle
      const time = Date.now() / 1000;
      const centerX = placeholderCanvas.width / 2;
      const centerY = placeholderCanvas.height / 2;
      const radius = 100 + Math.sin(time * 2) * 20;
      
      // Gradient for circle
      const gradient = ctx.createRadialGradient(
        centerX, centerY, 0,
        centerX, centerY, radius * 1.5
      );
      gradient.addColorStop(0, 'rgba(0, 195, 255, 0.8)');
      gradient.addColorStop(0.5, 'rgba(0, 195, 255, 0.3)');
      gradient.addColorStop(1, 'rgba(0, 195, 255, 0)');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.fill();
      
      // Add step number text
      const stepData = holoVideo.getAttribute('data-step');
      if (stepData) {
        ctx.font = 'bold 140px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = 'rgba(0, 195, 255, 0.2)';
        ctx.fillText(stepData, centerX, centerY);
        
        // Add smaller text
        ctx.font = '24px Arial';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.fillText('STEP ' + stepData, centerX, centerY + 100);
        ctx.fillText('Cinematic visualization', centerX, centerY + 140);
      }
      
      // Request next frame
      requestAnimationFrame(animatePlaceholder);
    }
    
    // Start animation
    animatePlaceholder();
    
    // Add canvas to video container
    const videoContainer = document.querySelector('.holo-frame');
    videoContainer.appendChild(placeholderCanvas);
    
    return placeholderCanvas;
  }
  
  // Add event listeners to steps
  steps.forEach(step => {
    step.addEventListener('click', function() {
      const videoFile = this.getAttribute('data-video');
      const stepNumber = this.getAttribute('data-step');
      
      if (videoFile) {
        console.log('Attempting to play video:', videoBasePath + videoFile);
        
        // Show holographic display with transition
        holoDisplay.style.display = 'flex';
        holoDisplay.style.opacity = '1';
        
        // Set the step data attribute on video (for fallback use)
        holoVideo.setAttribute('data-step', stepNumber || '');
        
        // Create new source element
        const source = document.createElement('source');
        source.src = videoBasePath + videoFile;
        source.type = 'video/mp4';
        
        // Clear previous sources
        holoVideo.innerHTML = '';
        
        // Add the new source
        holoVideo.appendChild(source);
        
        // Trigger fancy entry animation
        gsap.fromTo(
          '.holo-frame',
          { 
            opacity: 0, 
            y: 50, 
            rotateX: 15
          },
          { 
            opacity: 1, 
            y: 0, 
            rotateX: 5,
            duration: 1.2, 
            ease: 'power3.out'
          }
        );
        
        // Reset and load video
        holoVideo.load();
        
        // Set an error handler
        holoVideo.onerror = function() {
          console.error('Error loading video:', videoBasePath + videoFile);
          
          // Remove existing placeholder if it exists
          const existingCanvas = document.querySelector('.holo-frame canvas');
          if (existingCanvas) {
            existingCanvas.remove();
          }
          
          // Create placeholder animation
          createPlaceholderVideo();
        };
        
        // Play the video after it's loaded
        holoVideo.onloadeddata = function() {
          console.log('Video data loaded, attempting to play');
          const playPromise = holoVideo.play();
          
          if (playPromise !== undefined) {
            playPromise.then(() => {
              console.log('Video playback started successfully');
            }).catch(error => {
              console.warn('Auto-play prevented:', error);
              
              // Add play button for browsers that prevent autoplay
              if (!document.querySelector('.holo-play-button')) {
                const playButton = document.createElement('button');
                playButton.className = 'holo-play-button';
                playButton.innerHTML = '<i class="fas fa-play"></i>';
                document.querySelector('.holo-frame').appendChild(playButton);
                
                playButton.addEventListener('click', function() {
                  holoVideo.play();
                  this.style.display = 'none';
                });
              }
            });
          }
        };
        
        // Make sure the current step is highlighted
        steps.forEach(s => s.classList.remove('active-holo'));
        this.classList.add('active-holo');
      }
    });
  });
  
  // Close button functionality
  closeBtn.addEventListener('click', function() {
    // Fancy exit animation
    gsap.to('.holo-frame', { 
      opacity: 0, 
      y: 30, 
      rotateX: 15, 
      duration: 0.8, 
      ease: 'power2.in',
      onComplete: () => {
        holoDisplay.style.opacity = '0';
        
        // Delay hiding the container
        setTimeout(() => {
          holoDisplay.style.display = 'none';
          
          // Stop video playback
          holoVideo.pause();
          
          // Clear video sources
          holoVideo.innerHTML = '';
          
          // Remove any canvas placeholders
          const placeholderCanvas = document.querySelector('.holo-frame canvas');
          if (placeholderCanvas) {
            placeholderCanvas.remove();
          }
          
          // Reset active state
          steps.forEach(s => s.classList.remove('active-holo'));
        }, 800);
      }
    });
  });
  
  // Close when clicking outside the frame
  holoDisplay.addEventListener('click', function(e) {
    if (e.target === holoDisplay) {
      closeBtn.click();
    }
  });
  
  // Keyboard control (ESC to close)
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && holoDisplay.style.display === 'flex') {
      closeBtn.click();
    }
  });
});

// Add custom CSS class for active step
document.addEventListener('DOMContentLoaded', function() {
  const styleSheet = document.createElement('style');
  styleSheet.innerHTML = `
    .step.active-holo {
      border-color: rgba(0, 195, 255, 0.8);
      box-shadow: 0 0 25px rgba(0, 195, 255, 0.4);
      transform: translateY(-5px);
    }
    
    .holo-play-button {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: rgba(0, 0, 0, 0.5);
      border: 2px solid rgba(0, 195, 255, 0.6);
      color: white;
      font-size: 24px;
      cursor: pointer;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      box-shadow: 0 0 20px rgba(0, 195, 255, 0.3);
    }
    
    .holo-play-button:hover {
      background: rgba(0, 195, 255, 0.3);
      transform: translate(-50%, -50%) scale(1.1);
    }
  `;
  document.head.appendChild(styleSheet);
});

// Add 3D perspective mouse tracking
document.addEventListener('DOMContentLoaded', function() {
  const holoDisplay = document.querySelector('.holographic-display');
  const holoFrame = document.querySelector('.holo-frame');
  
  if (holoDisplay && holoFrame) {
    let isTrackingMouse = false;
    
    // Start tracking when display is active
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.attributeName === 'style' && 
            holoDisplay.style.display === 'flex' && 
            !isTrackingMouse) {
          isTrackingMouse = true;
          startTracking();
        } else if (mutation.attributeName === 'style' && 
                  holoDisplay.style.display === 'none' && 
                  isTrackingMouse) {
          isTrackingMouse = false;
        }
      });
    });
    
    observer.observe(holoDisplay, { attributes: true });
    
    function startTracking() {
      holoDisplay.addEventListener('mousemove', trackMouse);
    }
    
    function trackMouse(e) {
      if (!isTrackingMouse) return;
      
      // Calculate mouse position relative to center of display
      const rect = holoDisplay.getBoundingClientRect();
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      // Calculate rotation based on distance from center
      // Range: -3 to 3 degrees
      const rotateY = ((mouseX - centerX) / centerX) * 3;
      const rotateX = ((centerY - mouseY) / centerY) * 2;
      
      // Apply smooth rotation using GSAP
      gsap.to(holoFrame, {
        rotateY: rotateY,
        rotateX: rotateX,
        duration: 0.5,
        ease: 'power1.out'
      });
      
      // Subtle parallax for inner elements
      const videoElement = document.getElementById('holo-video');
      const scanlineElement = document.querySelector('.holo-scanline');
      const particlesElement = document.querySelector('.holo-particles');
      
      if (videoElement) {
        gsap.to(videoElement, {
          x: rotateY * -2,
          y: rotateX * -2,
          duration: 0.5,
          ease: 'power1.out'
        });
      }
      
      if (scanlineElement) {
        gsap.to(scanlineElement, {
          x: rotateY * 1.5,
          y: rotateX * 1.5,
          duration: 0.5,
          ease: 'power1.out'
        });
      }
      
      if (particlesElement) {
        gsap.to(particlesElement, {
          x: rotateY * 3,
          y: rotateX * 3,
          duration: 0.5,
          ease: 'power1.out'
        });
      }
    }
    
    // Remove tracking when display is closed
    holoDisplay.addEventListener('click', function(e) {
      if (e.target === holoDisplay) {
        isTrackingMouse = false;
        holoDisplay.removeEventListener('mousemove', trackMouse);
        
        // Reset transforms
        gsap.to(holoFrame, {
          rotateY: 0,
          rotateX: 5,
          duration: 0.5
        });
      }
    });
  }
});

// Add video progress bar functionality
document.addEventListener('DOMContentLoaded', function() {
  const holoVideo = document.getElementById('holo-video');
  
  if (holoVideo) {
    // Update progress bar during video playback
    holoVideo.addEventListener('timeupdate', updateProgress);
    
    // Function to update progress bar
    function updateProgress() {
      const progressBar = document.querySelector('.holo-progress-bar');
      const progressGlow = document.querySelector('.holo-progress-glow');
      const timeDisplay = document.querySelector('.holo-time-display');
      
      if (progressBar && timeDisplay) {
        // Calculate percentage of video played
        const percent = (holoVideo.currentTime / holoVideo.duration) * 100;
        
        // Update progress bar width
        progressBar.style.width = `${percent}%`;
        
        // Update glow position
        if (progressGlow) {
          progressGlow.style.left = `calc(${percent}% - 20px)`;
        }
        
        // Update time display
        const currentTime = formatTime(holoVideo.currentTime);
        const totalTime = formatTime(holoVideo.duration);
        timeDisplay.textContent = `${currentTime} / ${totalTime}`;
      }
    }
    
    // Format time from seconds to MM:SS
    function formatTime(timeInSeconds) {
      if (isNaN(timeInSeconds)) return "00:00";
      
      const minutes = Math.floor(timeInSeconds / 60);
      const seconds = Math.floor(timeInSeconds % 60);
      
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    // Make progress bar interactive
    const progressContainer = document.querySelector('.holo-progress-container');
    
    if (progressContainer) {
      progressContainer.addEventListener('click', function(e) {
        // Calculate clicked position
        const rect = progressContainer.getBoundingClientRect();
        const clickPosition = (e.clientX - rect.left) / rect.width;
        
        // Seek video to that position
        if (holoVideo.duration) {
          holoVideo.currentTime = clickPosition * holoVideo.duration;
        }
      });
      
      // Visual feedback on hover
      progressContainer.addEventListener('mousemove', function(e) {
        const rect = progressContainer.getBoundingClientRect();
        const hoverPosition = ((e.clientX - rect.left) / rect.width) * 100;
        
        this.style.cursor = 'pointer';
        
        // Add hover indicator if it doesn't exist
        if (!document.querySelector('.holo-progress-hover')) {
          const hoverIndicator = document.createElement('div');
          hoverIndicator.className = 'holo-progress-hover';
          hoverIndicator.style.position = 'absolute';
          hoverIndicator.style.top = '-5px';
          hoverIndicator.style.width = '10px';
          hoverIndicator.style.height = '14px';
          hoverIndicator.style.background = 'rgba(0, 255, 255, 0.7)';
          hoverIndicator.style.borderRadius = '2px';
          hoverIndicator.style.transition = 'left 0.1s ease';
          hoverIndicator.style.zIndex = '11';
          hoverIndicator.style.opacity = '0';
          
          progressContainer.appendChild(hoverIndicator);
        }
        
        // Update hover indicator position
        const hoverIndicator = document.querySelector('.holo-progress-hover');
        hoverIndicator.style.left = `calc(${hoverPosition}% - 5px)`;
        hoverIndicator.style.opacity = '1';
      });
      
      progressContainer.addEventListener('mouseleave', function() {
        const hoverIndicator = document.querySelector('.holo-progress-hover');
        if (hoverIndicator) {
          hoverIndicator.style.opacity = '0';
        }
      });
    }
    
    // Reset progress when video is loaded
    holoVideo.addEventListener('loadedmetadata', function() {
      updateProgress(); // Initialize with correct duration
    });
  }
});

