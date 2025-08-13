#!/usr/bin/env python3
"""
CONTRA Deployment Verification Script
Checks if the project is ready for Netlify deployment
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ Missing {description}: {file_path}")
        return False

def check_netlify_config():
    """Verify netlify.toml configuration"""
    config_file = "netlify.toml"
    if not check_file_exists(config_file, "Netlify configuration"):
        return False
    
    with open(config_file, 'r') as f:
        content = f.read()
        
    checks = [
        ("functions = \"netlify/functions\"", "Functions directory configured"),
        ("publish = \"HOMEPAGE/HOMEPAGE\"", "Publish directory configured"),
        ("[build]", "Build configuration present"),
        ("[[redirects]]", "Redirects configured")
    ]
    
    all_good = True
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc}")
            all_good = False
    
    return all_good

def check_frontend_files():
    """Check frontend files"""
    frontend_dir = "HOMEPAGE/HOMEPAGE"
    files_to_check = [
        (f"{frontend_dir}/index.html", "Main HTML file"),
        (f"{frontend_dir}/package.json", "Frontend package.json"),
        (f"{frontend_dir}/CSS", "CSS directory"),
        (f"{frontend_dir}/JS", "JavaScript directory"),
        (f"{frontend_dir}/assets", "Assets directory")
    ]
    
    all_good = True
    for file_path, desc in files_to_check:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    return all_good

def check_backend_files():
    """Check backend and function files"""
    files_to_check = [
        ("netlify/functions/api.py", "Netlify function"),
        ("requirements.txt", "Python requirements"),
        ("runtime.txt", "Python runtime"),
        ("app.py", "Flask application"),
        (".env", "Environment variables")
    ]
    
    all_good = True
    for file_path, desc in files_to_check:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    return all_good

def check_env_variables():
    """Check if required environment variables are present in .env"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    required_vars = [
        "GROQ_API_KEY",
        "NEWS_API_KEY", 
        "STABILITY_API_KEY"
    ]
    
    all_good = True
    for var in required_vars:
        if var in content and f"{var}=" in content:
            print(f"✅ Environment variable: {var}")
        else:
            print(f"❌ Missing environment variable: {var}")
            all_good = False
    
    return all_good

def main():
    """Main verification function"""
    print("🔍 CONTRA Deployment Readiness Check\n")
    print("=" * 50)
    
    checks = [
        ("Netlify Configuration", check_netlify_config),
        ("Frontend Files", check_frontend_files), 
        ("Backend Files", check_backend_files),
        ("Environment Variables", check_env_variables)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 SUCCESS: Your project is ready for Netlify deployment!")
        print("\n📖 Next steps:")
        print("1. Push your code to Git repository")
        print("2. Go to https://netlify.com")
        print("3. Click 'New site from Git'")
        print("4. Connect your repository")
        print("5. Set environment variables in Netlify dashboard")
        print("6. Deploy!")
        
        print("\n📚 See DEPLOYMENT.md for detailed instructions")
        return 0
    else:
        print("❌ ISSUES FOUND: Please fix the above issues before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
