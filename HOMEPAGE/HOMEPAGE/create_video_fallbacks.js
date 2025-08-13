/**
 * This script creates fallback GIF videos for the How It Works section
 * for cases where real videos aren't available or can't be loaded.
 * 
 * To use, run with Node.js:
 * node create_video_fallbacks.js
 */

const fs = require('fs');
const path = require('path');

// Create the videos directory if it doesn't exist
const videosDir = path.join(__dirname, 'assets', 'videos');
if (!fs.existsSync(videosDir)) {
  fs.mkdirSync(videosDir, { recursive: true });
  console.log(`Created directory: ${videosDir}`);
}

// Create an HTML file that we can open to generate .mp4 videos from HTML canvas
const generateVideoHtml = () => {
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Generate Step Videos</title>
  <script src="https://cdn.jsdelivr.net/npm/gif.js/dist/gif.js"></script>
  <style>
    body { background: #000; margin: 0; padding: 20px; font-family: Arial, sans-serif; color: white; }
    .controls { margin-bottom: 20px; }
    button { padding: 8px 16px; margin-right: 10px; background: #0066ff; color: white; border: none; cursor: pointer; }
    canvas { border: 1px solid #333; max-width: 100%; margin-bottom: 20px; }
    .preview { margin-top: 20px; }
    h2 { color: #0af; }
  </style>
</head>
<body>
  <h1>Step Video Generator</h1>
  <div class="controls">
    <button id="generateBtn">Generate All Step Videos</button>
    <button id="downloadBtn" disabled>Download All</button>
  </div>
  
  <div id="canvasContainer"></div>
  <div class="preview" id="preview"></div>
  
  <script>
    const WIDTH = 1280;
    const HEIGHT = 720;
    
    // Create canvases for each step
    function createStepCanvas(step) {
      const container = document.createElement('div');
      container.innerHTML = \`<h2>Step \${step}</h2>\`;
      
      const canvas = document.createElement('canvas');
      canvas.width = WIDTH;
      canvas.height = HEIGHT;
      canvas.id = \`canvas\${step}\`;
      container.appendChild(canvas);
      
      document.getElementById('canvasContainer').appendChild(container);
      return canvas;
    }
    
    // Draw content on a canvas for a specific step
    function drawStepCanvas(ctx, step, frameCount) {
      // Clear canvas
      ctx.clearRect(0, 0, WIDTH, HEIGHT);
      
      // Fill background
      ctx.fillStyle = 'rgba(10, 20, 30, 0.9)';
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
      
      // Draw grid
      ctx.strokeStyle = 'rgba(0, 195, 255, 0.2)';
      ctx.lineWidth = 1;
      
      // Grid lines
      const gridSize = 40;
      for (let x = 0; x < WIDTH; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, HEIGHT);
        ctx.stroke();
      }
      
      for (let y = 0; y < HEIGHT; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(WIDTH, y);
        ctx.stroke();
      }
      
      // Draw animated elements based on the step
      const time = frameCount / 10;
      const centerX = WIDTH / 2;
      const centerY = HEIGHT / 2;
      
      // Different visualization for each step
      switch(step) {
        case 1:
          // Topic input visualization
          // Main circle
          const radius1 = 100 + Math.sin(time * 0.2) * 20;
          const gradient1 = ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, radius1 * 1.5
          );
          gradient1.addColorStop(0, 'rgba(0, 195, 255, 0.8)');
          gradient1.addColorStop(0.5, 'rgba(0, 195, 255, 0.3)');
          gradient1.addColorStop(1, 'rgba(0, 195, 255, 0)');
          
          ctx.fillStyle = gradient1;
          ctx.beginPath();
          ctx.arc(centerX, centerY, radius1, 0, Math.PI * 2);
          ctx.fill();
          
          // Input field visualization
          ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
          ctx.fillRect(centerX - 200, centerY + 50, 400, 50);
          
          // Animate typing cursor
          if (Math.floor(time) % 2 === 0) {
            ctx.fillStyle = '#fff';
            ctx.fillRect(centerX - 180 + (Math.min(frameCount % 100, 50) * 5), centerY + 55, 2, 40);
          }
          break;
          
        case 2:
          // Button clicking visualization
          // Main circle
          const radius2 = 120 + Math.sin(time * 0.2) * 10;
          const gradient2 = ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, radius2 * 1.5
          );
          gradient2.addColorStop(0, 'rgba(255, 100, 100, 0.6)');
          gradient2.addColorStop(0.5, 'rgba(255, 100, 100, 0.2)');
          gradient2.addColorStop(1, 'rgba(255, 100, 100, 0)');
          
          ctx.fillStyle = gradient2;
          ctx.beginPath();
          ctx.arc(centerX, centerY, radius2, 0, Math.PI * 2);
          ctx.fill();
          
          // Button visualization
          ctx.fillStyle = frameCount % 40 < 20 ? 'rgba(0, 195, 255, 0.8)' : 'rgba(0, 195, 255, 0.4)';
          ctx.fillRect(centerX - 100, centerY - 25, 200, 50);
          
          // Button text
          ctx.font = '24px Arial';
          ctx.fillStyle = '#fff';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('GENERATE', centerX, centerY);
          break;
          
        case 3:
          // AI Processing visualization
          // Processing circles
          for (let i = 0; i < 5; i++) {
            const angle = (time * 0.1) + (i * Math.PI * 2 / 5);
            const x = centerX + Math.cos(angle) * 150;
            const y = centerY + Math.sin(angle) * 150;
            const pulseRadius = 30 + Math.sin(time * 0.5 + i) * 10;
            
            const gradientNode = ctx.createRadialGradient(
              x, y, 0,
              x, y, pulseRadius * 1.5
            );
            gradientNode.addColorStop(0, \`rgba(\${i * 50}, 195, 255, 0.9)\`);
            gradientNode.addColorStop(0.5, \`rgba(\${i * 50}, 195, 255, 0.4)\`);
            gradientNode.addColorStop(1, \`rgba(\${i * 50}, 195, 255, 0)\`);
            
            ctx.fillStyle = gradientNode;
            ctx.beginPath();
            ctx.arc(x, y, pulseRadius, 0, Math.PI * 2);
            ctx.fill();
            
            // Connection lines
            ctx.strokeStyle = 'rgba(0, 195, 255, 0.3)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.stroke();
          }
          
          // Central node
          ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
          ctx.beginPath();
          ctx.arc(centerX, centerY, 20 + Math.sin(time) * 5, 0, Math.PI * 2);
          ctx.fill();
          break;
          
        case 4:
          // Results visualization
          // Data visualization
          ctx.fillStyle = 'rgba(0, 200, 100, 0.2)';
          ctx.fillRect(centerX - 200, centerY - 150, 400, 100);
          
          // Image result
          ctx.fillStyle = 'rgba(0, 195, 255, 0.2)';
          ctx.fillRect(centerX - 200, centerY - 30, 190, 190);
          
          // Text blocks
          ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
          ctx.fillRect(centerX + 10, centerY - 30, 190, 40);
          ctx.fillRect(centerX + 10, centerY + 20, 190, 40);
          ctx.fillRect(centerX + 10, centerY + 70, 190, 40);
          ctx.fillRect(centerX + 10, centerY + 120, 190, 40);
          
          // Animated indicator
          const indicatorX = centerX - 220 + (Math.sin(time) + 1) * 440;
          ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
          ctx.beginPath();
          ctx.arc(indicatorX, centerY + 200, 5, 0, Math.PI * 2);
          ctx.fill();
          break;
      }
      
      // Add step number text
      ctx.font = 'bold 140px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = 'rgba(0, 195, 255, 0.2)';
      ctx.fillText(step.toString(), centerX, centerY);
      
      // Add smaller text
      ctx.font = '24px Arial';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.fillText('STEP ' + step, centerX, centerY + 150);
      
      // Different text for each step
      const stepTexts = [
        '',
        'Input Your Topic',
        'Click the button',
        'AI Processing',
        'Results'
      ];
      ctx.fillText(stepTexts[step], centerX, centerY + 190);
    }
    
    // Create and download a GIF for a step
    function createGif(step) {
      return new Promise((resolve) => {
        const canvas = document.getElementById(\`canvas\${step}\`);
        const ctx = canvas.getContext('2d');
        const gif = new GIF({
          workers: 2,
          quality: 10,
          width: WIDTH,
          height: HEIGHT,
          workerScript: 'https://cdn.jsdelivr.net/npm/gif.js/dist/gif.worker.js'
        });
        
        // Add frames
        const frameCount = 40; // Number of frames in the animation
        for (let frame = 0; frame < frameCount; frame++) {
          drawStepCanvas(ctx, step, frame);
          gif.addFrame(canvas, { copy: true, delay: 50 });
        }
        
        gif.on('finished', function(blob) {
          // Create download link
          const downloadLink = document.createElement('a');
          downloadLink.href = URL.createObjectURL(blob);
          downloadLink.download = \`card \${step}.gif\`;
          downloadLink.innerHTML = \`Download Step \${step} GIF\`;
          downloadLink.className = 'download-link';
          downloadLink.style.display = 'block';
          downloadLink.style.margin = '10px 0';
          downloadLink.style.color = '#0af';
          document.getElementById('preview').appendChild(downloadLink);
          
          // Auto-download
          // downloadLink.click();
          
          resolve(downloadLink);
        });
        
        // Start rendering
        gif.render();
      });
    }
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
      // Create canvases for each step
      for (let step = 1; step <= 4; step++) {
        const canvas = createStepCanvas(step);
        const ctx = canvas.getContext('2d');
        
        // Draw initial frame
        drawStepCanvas(ctx, step, 0);
        
        // Animate canvas
        let frameCount = 0;
        setInterval(() => {
          drawStepCanvas(ctx, step, frameCount++);
        }, 50);
      }
      
      // Generate button
      document.getElementById('generateBtn').addEventListener('click', async () => {
        const downloadLinks = [];
        for (let step = 1; step <= 4; step++) {
          const link = await createGif(step);
          downloadLinks.push(link);
        }
        
        document.getElementById('downloadBtn').disabled = false;
        document.getElementById('generateBtn').disabled = true;
      });
      
      // Download all button
      document.getElementById('downloadBtn').addEventListener('click', () => {
        document.querySelectorAll('.download-link').forEach(link => {
          link.click();
        });
      });
    });
  </script>
</body>
</html>
  `;

  const htmlFilePath = path.join(__dirname, 'generate_videos.html');
  fs.writeFileSync(htmlFilePath, htmlContent);
  console.log(`Generated HTML file for video creation: ${htmlFilePath}`);
  console.log('Open this file in a web browser to generate GIF animations for all steps.');
  return htmlFilePath;
};

// Create an HTML file to help generate videos
const htmlFilePath = generateVideoHtml();

// Also create a simple placeholder for videos
// Create placeholder video for card 1.mp4
const createCanvasDataURL = (step) => {
  const WIDTH = 1280;
  const HEIGHT = 720;
  const canvas = require('canvas').createCanvas(WIDTH, HEIGHT);
  const ctx = canvas.getContext('2d');
  
  // Fill background
  ctx.fillStyle = 'rgba(10, 20, 30, 0.8)';
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  
  // Draw grid
  ctx.strokeStyle = 'rgba(0, 195, 255, 0.3)';
  ctx.lineWidth = 1;
  
  // Grid lines
  const gridSize = 40;
  for (let x = 0; x < WIDTH; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, HEIGHT);
    ctx.stroke();
  }
  
  for (let y = 0; y < HEIGHT; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(WIDTH, y);
    ctx.stroke();
  }
  
  // Draw pulsing circle
  const centerX = WIDTH / 2;
  const centerY = HEIGHT / 2;
  const radius = 100;
  
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
  ctx.font = 'bold 140px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = 'rgba(0, 195, 255, 0.2)';
  ctx.fillText(step.toString(), centerX, centerY);
  
  // Add smaller text
  ctx.font = '24px Arial';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
  ctx.fillText('STEP ' + step, centerX, centerY + 100);
  ctx.fillText('Please open generate_videos.html to create animated GIFs', centerX, centerY + 140);
  
  return canvas.toDataURL('image/png');
};

// Print next steps
console.log('\nNext steps:');
console.log('1. Open the generate_videos.html file in a browser.');
console.log('2. Click the "Generate All Step Videos" button.');
console.log('3. Click "Download All" to save all the GIF files.');
console.log('4. Move the downloaded GIFs to the assets/videos directory.');
console.log('\nAlternatively, upload your own .mp4 videos to the assets/videos directory with names:');
console.log('- card 1.mp4');
console.log('- card 2.mp4');
console.log('- card 3.mp4');
console.log('- card 4.mp4'); 