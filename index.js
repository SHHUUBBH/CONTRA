/**
 * CONTRA - Node.js Server
 * 
 * This server handles the homepage and real-time updates
 * while the main Flask application handles the AI and data processing.
 */

require('dotenv').config();
const express = require('express');
const http = require('http');
const path = require('path');
const cors = require('cors');
const socketIo = require('socket.io');
const axios = require('axios');

// Create Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Environment variables
const PORT = process.env.NODE_PORT || 8080;
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'HOMEPAGE/HOMEPAGE')));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'HOMEPAGE/HOMEPAGE/index.html'));
});

app.get('/contra.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'HOMEPAGE/HOMEPAGE/contra.html'));
});

// API proxy to Flask
app.post('/api/:endpoint', async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_API_URL}/api/${req.params.endpoint}`, req.body);
    res.json(response.data);
  } catch (error) {
    console.error(`Error proxying to Flask API: ${error.message}`);
    res.status(500).json({ error: 'Failed to fetch data from API' });
  }
});

// Socket.IO for real-time updates
io.on('connection', (socket) => {
  console.log('New client connected');
  
  // Listen for generation requests
  socket.on('startGeneration', async (data) => {
    try {
      // Forward request to Flask
      const response = await axios.post(`${FLASK_API_URL}/api/generate`, data);
      
      // Send updates to client
      socket.emit('generationProgress', { progress: 100, result: response.data });
    } catch (error) {
      console.error(`Error during generation: ${error.message}`);
      socket.emit('generationError', { error: 'Generation failed' });
    }
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`CONTRA Node.js server running on port ${PORT}`);
  console.log(`Proxying API requests to Flask at ${FLASK_API_URL}`);
}); 