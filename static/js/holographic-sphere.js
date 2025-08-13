document.addEventListener('DOMContentLoaded', function() {
  const sphereContainer = document.getElementById('holographic-sphere');
  if (!sphereContainer) return;
  
  // Clear existing children
  sphereContainer.innerHTML = '';
  
  // Create layers with different sizes and animation speeds
  for (let i = 0; i < 5; i++) {
    const sphere = document.createElement('div');
    sphere.className = 'holographic-layer';
    sphere.style.setProperty('--index', i);
    
    // Add additional styling for better visibility
    sphere.style.opacity = 0.4 - (i * 0.05);
    sphere.style.backgroundColor = 'rgba(139, 92, 246, 0.05)';
    sphere.style.boxShadow = `0 0 ${30 + (i * 10)}px rgba(139, 92, 246, ${0.3 - (i * 0.05)})`;
    
    sphereContainer.appendChild(sphere);
  }
  
  // Add subtle animation to the entire sphere
  window.addEventListener('mousemove', function(e) {
    if (!sphereContainer) return;
    
    const mouseX = e.clientX;
    const mouseY = e.clientY;
    
    const rect = sphereContainer.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const deltaX = (mouseX - centerX) / 20;
    const deltaY = (mouseY - centerY) / 20;
    
    sphereContainer.style.transform = `translate(-50%, -50%) rotateX(${-deltaY}deg) rotateY(${deltaX}deg)`;
  });
}); 