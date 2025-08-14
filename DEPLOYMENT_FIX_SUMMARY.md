# CONTRA - AI Page Routing Fix

## Problem
Your homepage buttons were linking to `/api/AI` but this route didn't exist in your Node.js server, causing a 404 "Page not found" error.

## Root Cause
You have two separate applications:
1. **Node.js server** (index.js) - serves the homepage (deployed on Netlify)
2. **Flask server** (app.py) - serves the AI application

The homepage buttons were pointing to the wrong URL.

## What We Fixed

### 1. Updated Homepage Buttons
**File:** `HOMEPAGE/HOMEPAGE/index.html`
- Changed both "START CREATING" and "START NOW" buttons from `/api/AI` to `/AI`
- This makes them point to the correct route

### 2. Added Route Handler in Node.js Server
**File:** `index.js`
- Added a new route: `app.get('/AI', (req, res) => ...)`
- This route redirects users to your Flask application
- It uses the `FLASK_APP_URL` environment variable

### 3. Updated Environment Configuration
**File:** `.env`
- Added `FLASK_APP_URL=http://localhost:5000` for local development
- Added `NODE_PORT=8080` for the Node.js server

## What You Need to Do Next

### Option 1: Deploy Flask App (Recommended)
1. Deploy your Flask application (`app.py`) to a hosting service like:
   - Heroku (free tier)
   - Railway (free tier)
   - Render (free tier)
   - PythonAnywhere (free tier)

2. Update the `.env` file with your Flask app's URL:
   ```
   FLASK_APP_URL=https://your-flask-app.herokuapp.com
   ```

3. Redeploy to Netlify

### Option 2: Test Locally
1. Run both servers locally:
   ```bash
   # Terminal 1: Flask server
   python app.py
   
   # Terminal 2: Node.js server
   node index.js
   ```

2. Visit `http://localhost:8080` and test the buttons

## Files Modified
- `HOMEPAGE/HOMEPAGE/index.html` - Updated button URLs
- `index.js` - Added `/AI` route handler
- `.env` - Added Flask configuration

## Current Status
✅ Homepage buttons now point to `/AI`
✅ Node.js server has route handler for `/AI`
✅ Environment variables configured
❌ Flask app needs to be deployed (see options above)

Once you deploy the Flask app and update the URL in `.env`, your AI page should work perfectly!
