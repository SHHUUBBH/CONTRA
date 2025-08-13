import sys
import os
from pathlib import Path

# Add project root to the path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')

try:
    from app import app
except ImportError:
    # Fallback if app structure is different
    from app import create_app
    app = create_app()

def handler(event, context):
    """Netlify Functions handler"""
    import json
    
    # Handle different HTTP methods
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    query = event.get('queryStringParameters') or {}
    body = event.get('body', '')
    
    # Simple routing for API endpoints
    if path.startswith('/api/'):
        # Remove /api prefix since Netlify redirects handle this
        path = path[4:] or '/'
    
    # Mock WSGI environ
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join([f'{k}={v}' for k, v in query.items()]),
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'wsgi.input': body,
        'HTTP_HOST': headers.get('host', 'localhost'),
    }
    
    # Add headers to environ
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value
    
    try:
        with app.test_request_context(path, method=method, headers=headers, query_string=environ['QUERY_STRING'], data=body):
            response = app.full_dispatch_request()
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
