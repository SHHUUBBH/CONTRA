import logging
import traceback
from flask import jsonify, request

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Import app
from app import create_app

# Create application
app = create_app()

# Add more error handling
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions with detailed traceback."""
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(traceback.format_exc())
    
    # Print request data for debugging
    if request:
        logger.error(f"Request URL: {request.url}")
        logger.error(f"Request method: {request.method}")
        logger.error(f"Request data: {request.get_data(as_text=True)}")
    
    return jsonify({
        "success": False,
        "error": "Server error",
        "details": str(e),
        "traceback": traceback.format_exc()
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 