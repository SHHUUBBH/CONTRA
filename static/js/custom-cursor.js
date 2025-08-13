/**
 * CONTRA - Enhanced Custom Cursor
 * A modern, responsive and adaptive cursor with interactive behaviors
 */

function initCursor() {
  // Force cursor hiding at the document level to ensure maximum compatibility
  document.documentElement.style.cursor = 'none';
  document.body.style.cursor = 'none';
  
  // Create global style for any dynamically added elements
  const styleElement = document.createElement('style');
  styleElement.textContent = `
    * {
      cursor: none !important;
    }
  `;
  document.head.appendChild(styleElement);
  
  // Ensure cursor elements exist in the DOM
  const cursorDot = document.querySelector('.cursor-dot');
  const cursorOutline = document.querySelector('.cursor-dot-outline');
  
  if (!cursorDot || !cursorOutline) {
    console.error('Custom cursor elements not found in the DOM');
    return;
  }
  
  // Initialize position variables
  let cursorVisible = false;
  let cursorEnlarged = false;
  
  // Create trail elements for smoother movement
  const trailCount = 5;
  const trailElements = [];
  
  for (let i = 0; i < trailCount; i++) {
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    trail.style.cssText = `
      position: fixed;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: rgba(139, 92, 246, 0.5);
      pointer-events: none;
      z-index: 9998;
      opacity: ${0.7 - (i * 0.15)};
      transition: opacity 0.3s ease;
      mix-blend-mode: screen;
      transform: translate(-50%, -50%);
    `;
    document.body.appendChild(trail);
    trailElements.push({
      element: trail,
      x: 0,
      y: 0
    });
  }
  
  // Position variables
  let mouseX = 0;
  let mouseY = 0;
  let dotX = 0;
  let dotY = 0;
  let outlineX = 0;
  let outlineY = 0;
  
  // Speed variables
  let prevSpeed = 0;
  let currentSpeed = 0;
  let lastMouseX = 0;
  let lastMouseY = 0;
  
  // Make cursor visible on mouse movement
  const onMouseMove = (e) => {
    // Calculate mouse movement speed
    const deltaX = e.clientX - lastMouseX;
    const deltaY = e.clientY - lastMouseY;
    currentSpeed = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    
    lastMouseX = mouseX;
    lastMouseY = mouseY;
    
    mouseX = e.clientX;
    mouseY = e.clientY;
    
    // Make cursor visible
    if (!cursorVisible) {
      cursorDot.style.opacity = 1;
      cursorOutline.style.opacity = 1;
      trailElements.forEach(trail => {
        trail.element.style.opacity = trail.element.style.opacity;
      });
      cursorVisible = true;
    }
  };
  
  // Hide cursor when it leaves window
  const onMouseLeave = () => {
    cursorDot.style.opacity = 0;
    cursorOutline.style.opacity = 0;
    trailElements.forEach(trail => {
      trail.element.style.opacity = 0;
    });
    cursorVisible = false;
  };
  
  // Change cursor size when clicking
  const onMouseDown = () => {
    cursorDot.style.transform = 'translate(-50%, -50%) scale(0.9)';
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(1.5)';
    
    // Create click ripple effect
    const ripple = document.createElement('div');
    ripple.className = 'cursor-ripple';
    ripple.style.cssText = `
      position: fixed;
      top: ${mouseY}px;
      left: ${mouseX}px;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border: 2px solid rgba(139, 92, 246, 0.8);
      transform: translate(-50%, -50%) scale(0);
      opacity: 1;
      pointer-events: none;
      z-index: 9997;
      animation: rippleEffect 0.6s ease-out forwards;
    `;
    document.body.appendChild(ripple);
    
    // Remove ripple after animation
    setTimeout(() => {
      ripple.remove();
    }, 600);
  };
  
  const onMouseUp = () => {
    cursorDot.style.transform = 'translate(-50%, -50%) scale(1)';
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(1)';
  };
  
  // Enlarge cursor when hovering over clickable elements
  const onMouseEnterLink = () => {
    cursorDot.style.transform = 'translate(-50%, -50%) scale(1.3)';
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(1.7)';
    cursorDot.style.backgroundColor = 'rgba(139, 92, 246, 0.9)';
    cursorOutline.style.borderColor = 'rgba(139, 92, 246, 0.9)';
    cursorEnlarged = true;
  };
  
  // Enlarge cursor for buttons with different color
  const onMouseEnterButton = () => {
    cursorDot.style.transform = 'translate(-50%, -50%) scale(1.3)';
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(1.7)';
    cursorDot.style.backgroundColor = 'rgba(6, 182, 212, 0.9)';
    cursorOutline.style.borderColor = 'rgba(6, 182, 212, 0.9)';
    cursorEnlarged = true;
  };
  
  // Special effect for images
  const onMouseEnterImage = () => {
    cursorDot.style.transform = 'translate(-50%, -50%) scale(1.5)';
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(2)';
    cursorDot.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
    cursorOutline.style.borderColor = 'rgba(255, 255, 255, 0.7)';
    cursorOutline.style.mixBlendMode = 'difference';
    cursorEnlarged = true;
  };
  
  // Text selection cursor
  const onMouseEnterText = () => {
    cursorDot.style.transform = 'translate(-50%, -50%) scale(0.7)';
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(3)';
    cursorDot.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
    cursorOutline.style.borderWidth = '1px';
    cursorOutline.style.borderColor = 'rgba(255, 255, 255, 0.3)';
    cursorEnlarged = true;
  };
  
  // Return to normal cursor size
  const onMouseLeaveInteractive = () => {
    cursorDot.style.transform = 'translate(-50%, -50%) scale(1)';
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(1)';
    cursorDot.style.backgroundColor = 'white';
    cursorOutline.style.borderColor = 'white';
    cursorOutline.style.mixBlendMode = 'screen';
    cursorOutline.style.borderWidth = '2px';
    cursorEnlarged = false;
  };
  
  // Smooth animation loop for cursor movement
  const render = () => {
    // Update dot position with easing
    dotX += (mouseX - dotX) * 0.2;
    dotY += (mouseY - dotY) * 0.2;
    
    // Update outline position with different easing
    outlineX += (mouseX - outlineX) * 0.15;
    outlineY += (mouseY - outlineY) * 0.15;
    
    // Apply positions
    cursorDot.style.left = `${dotX}px`;
    cursorDot.style.top = `${dotY}px`;
    
    cursorOutline.style.left = `${outlineX}px`;
    cursorOutline.style.top = `${outlineY}px`;
    
    // Calculate and smooth speed transitions
    prevSpeed = prevSpeed + (currentSpeed - prevSpeed) * 0.1;
    
    // Apply speed effects
    if (prevSpeed > 10) {
      // Fast movement - elongate cursor, add stretch effect
      const angle = Math.atan2(mouseY - lastMouseY, mouseX - lastMouseX);
      const stretch = Math.min(prevSpeed / 40, 2);
      
      cursorDot.style.transform = `translate(-50%, -50%) scale(${1 + stretch * 0.3}, ${1 - stretch * 0.1}) rotate(${angle}rad)`;
      cursorOutline.style.transform = `translate(-50%, -50%) scale(${1 + stretch * 0.5}, ${1 - stretch * 0.2}) rotate(${angle}rad)`;
      
      // Show trail during fast movement
      trailElements.forEach((trail, index) => {
        const delay = index * 1.5;
        const trailX = dotX - Math.cos(angle) * delay * (stretch * 5);
        const trailY = dotY - Math.sin(angle) * delay * (stretch * 5);
        
        trail.x += (trailX - trail.x) * 0.3;
        trail.y += (trailY - trail.y) * 0.3;
        
        trail.element.style.left = `${trail.x}px`;
        trail.element.style.top = `${trail.y}px`;
        trail.element.style.opacity = prevSpeed > 30 ? 0.7 - (index * 0.15) : 0;
        trail.element.style.transform = `translate(-50%, -50%) scale(${1 - index * 0.1})`;
      });
    } else {
      // Hide trail during slow movement if not already modified by hover effects
      if (!cursorEnlarged) {
        cursorDot.style.transform = 'translate(-50%, -50%) scale(1)';
        cursorOutline.style.transform = 'translate(-50%, -50%) scale(1)';
      }
      
      trailElements.forEach(trail => {
        trail.element.style.opacity = 0;
      });
    }
    
    requestAnimationFrame(render);
  };
  
  // Add dynamic tone-based colors
  function updateCursorForTone() {
    const body = document.body;
    
    if (body.classList.contains('tone-humorous')) {
      cursorDot.style.backgroundColor = 'rgb(253, 186, 116)';
      cursorOutline.style.borderColor = 'rgb(253, 186, 116)';
      trailElements.forEach(trail => {
        trail.element.style.backgroundColor = 'rgba(253, 186, 116, 0.5)';
      });
    } else if (body.classList.contains('tone-dramatic')) {
      cursorDot.style.backgroundColor = 'rgb(248, 113, 113)';
      cursorOutline.style.borderColor = 'rgb(248, 113, 113)';
      trailElements.forEach(trail => {
        trail.element.style.backgroundColor = 'rgba(248, 113, 113, 0.5)';
      });
    } else if (body.classList.contains('tone-poetic')) {
      cursorDot.style.backgroundColor = 'rgb(216, 180, 254)';
      cursorOutline.style.borderColor = 'rgb(216, 180, 254)';
      trailElements.forEach(trail => {
        trail.element.style.backgroundColor = 'rgba(216, 180, 254, 0.5)';
      });
    } else if (body.classList.contains('tone-technical')) {
      cursorDot.style.backgroundColor = 'rgb(20, 184, 166)';
      cursorOutline.style.borderColor = 'rgb(20, 184, 166)';
      trailElements.forEach(trail => {
        trail.element.style.backgroundColor = 'rgba(20, 184, 166, 0.5)';
      });
    } else if (body.classList.contains('tone-simple')) {
      cursorDot.style.backgroundColor = 'rgb(132, 204, 22)';
      cursorOutline.style.borderColor = 'rgb(132, 204, 22)';
      trailElements.forEach(trail => {
        trail.element.style.backgroundColor = 'rgba(132, 204, 22, 0.5)';
      });
    } else {
      // Default/informative
      cursorDot.style.backgroundColor = 'rgb(255, 255, 255)';
      cursorOutline.style.borderColor = 'rgb(255, 255, 255)';
      trailElements.forEach(trail => {
        trail.element.style.backgroundColor = 'rgba(139, 92, 246, 0.5)';
      });
    }
  }
  
  // Observe for theme/tone changes
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.attributeName === 'class') {
        updateCursorForTone();
      }
    });
  });
  
  observer.observe(document.body, { attributes: true });
  
  // Add event listeners for cursor behavior
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseleave', onMouseLeave);
  document.addEventListener('mousedown', onMouseDown);
  document.addEventListener('mouseup', onMouseUp);
  
  // Add keyframe animation for ripple effect
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes rippleEffect {
      0% {
        transform: translate(-50%, -50%) scale(0);
        opacity: 1;
      }
      100% {
        transform: translate(-50%, -50%) scale(1);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(styleSheet);
  
  // Add event listeners for interactive elements
  const addInteractiveListeners = () => {
    const links = document.querySelectorAll('a, .btn, button, [role="button"]');
    const buttons = document.querySelectorAll('.btn, button, input[type="submit"], [role="button"]');
    const images = document.querySelectorAll('img, .image-card');
    const texts = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li');
    
    links.forEach(link => {
      link.addEventListener('mouseenter', onMouseEnterLink);
      link.addEventListener('mouseleave', onMouseLeaveInteractive);
    });
    
    buttons.forEach(button => {
      button.addEventListener('mouseenter', onMouseEnterButton);
      button.addEventListener('mouseleave', onMouseLeaveInteractive);
    });
    
    images.forEach(image => {
      image.addEventListener('mouseenter', onMouseEnterImage);
      image.addEventListener('mouseleave', onMouseLeaveInteractive);
    });
    
    texts.forEach(text => {
      text.addEventListener('mouseenter', onMouseEnterText);
      text.addEventListener('mouseleave', onMouseLeaveInteractive);
    });
  };
  
  // Initialize cursor position
  dotX = mouseX;
  dotY = mouseY;
  outlineX = mouseX;
  outlineY = mouseY;
  
  // Set cursor colors based on current tone
  updateCursorForTone();
  
  // Start animation loop
  requestAnimationFrame(render);
  
  // Add interactive listeners
  addInteractiveListeners();
  
  // Re-add listeners when DOM changes
  const contentObserver = new MutationObserver(() => {
    addInteractiveListeners();
  });
  
  contentObserver.observe(document.body, { 
    childList: true,
    subtree: true
  });
}

function robustInitCursor() {
  // Check if on a touch device
  function isTouchDevice() {
    const hasTouchPoints = navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
    const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints;
    const isTablet = /iPad|tablet|Android(?!.*Mobile)/i.test(navigator.userAgent);
    const isMobile = /iPhone|iPod|Android.*Mobile|IEMobile|BlackBerry|webOS/i.test(navigator.userAgent);
    const isMobileScreen = window.matchMedia("(max-width: 768px)").matches;
    return hasTouch || hasTouchPoints || isTablet || isMobile || isMobileScreen;
  }
  if (isTouchDevice()) return;

  // Ensure cursor elements exist
  let cursorDot = document.querySelector('.cursor-dot');
  let cursorOutline = document.querySelector('.cursor-dot-outline');
  if (!cursorDot) {
    cursorDot = document.createElement('div');
    cursorDot.className = 'cursor-dot';
    document.body.appendChild(cursorDot);
  }
  if (!cursorOutline) {
    cursorOutline = document.createElement('div');
    cursorOutline.className = 'cursor-dot-outline';
    document.body.appendChild(cursorOutline);
  }
  cursorDot.style.opacity = 1;
  cursorOutline.style.opacity = 1;

  // Now call the original initCursor if available
  if (typeof initCursor === 'function') {
    initCursor();
  } else {
    console.error('initCursor function not found!');
  }
}

document.addEventListener('DOMContentLoaded', robustInitCursor); 