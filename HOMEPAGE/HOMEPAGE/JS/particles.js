document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("particles-canvas")
    const ctx = canvas.getContext("2d")
  
    // Set canvas size
    const setCanvasSize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
  
    setCanvasSize()
    window.addEventListener("resize", setCanvasSize)
  
    // Particle class
    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width
        this.y = Math.random() * canvas.height
        this.size = Math.random() * 2 + 0.5
        this.speedX = Math.random() * 0.5 - 0.25
        this.speedY = Math.random() * 0.5 - 0.25
  
        // Colors: purple, cyan, emerald
        const colors = ["#8b5cf6", "#06b6d4", "#10b981"]
        this.color = colors[Math.floor(Math.random() * colors.length)]
        this.alpha = Math.random() * 0.5 + 0.1
      }
  
      update() {
        this.x += this.speedX
        this.y += this.speedY
  
        // Wrap around edges
        if (this.x < 0) this.x = canvas.width
        if (this.x > canvas.width) this.x = 0
        if (this.y < 0) this.y = canvas.height
        if (this.y > canvas.height) this.y = 0
      }
  
      draw() {
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        ctx.fillStyle = this.color
        ctx.globalAlpha = this.alpha
        ctx.fill()
      }
    }
  
    // Create particles
    const particlesArray = []
    const particleCount = Math.min(100, Math.floor((canvas.width * canvas.height) / 10000))
  
    for (let i = 0; i < particleCount; i++) {
      particlesArray.push(new Particle())
    }
  
    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
  
      // Update and draw particles
      for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update()
        particlesArray[i].draw()
      }
  
      // Draw connections
      connectParticles()
  
      requestAnimationFrame(animate)
    }
  
    // Connect particles with lines
    const connectParticles = () => {
      const maxDistance = 150
  
      for (let a = 0; a < particlesArray.length; a++) {
        for (let b = a; b < particlesArray.length; b++) {
          const dx = particlesArray[a].x - particlesArray[b].x
          const dy = particlesArray[a].y - particlesArray[b].y
          const distance = Math.sqrt(dx * dx + dy * dy)
  
          if (distance < maxDistance) {
            const opacity = 1 - distance / maxDistance
            ctx.beginPath()
            ctx.strokeStyle = `rgba(255, 255, 255, ${opacity * 0.15})`
            ctx.lineWidth = 0.5
            ctx.moveTo(particlesArray[a].x, particlesArray[a].y)
            ctx.lineTo(particlesArray[b].x, particlesArray[b].y)
            ctx.stroke()
          }
        }
      }
    }
  
    animate()
  })
  
  