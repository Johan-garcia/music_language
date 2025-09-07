#!/usr/bin/env python3
"""
Interactive script to help users set up their API keys.
Run this script to automatically configure your .env file.
"""

import os
import sys
from pathlib import Path

def print_header():
    print("🎵" + "="*60 + "🎵")
    print("    MUSIC RECOMMENDATION API - API KEYS SETUP")
    print("🎵" + "="*60 + "🎵")
    print()

def print_instructions():
    print("📋 You'll need to get API keys from these platforms:")
    print()
    print("1. 🎬 YouTube Data API v3:")
    print("   → https://console.developers.google.com/")
    print("   → Enable YouTube Data API v3")
    print("   → Create credentials (API key)")
    print()
    print("2. 🎵 Spotify Web API:")
    print("   → https://developer.spotify.com/dashboard/")
    print("   → Create an app")
    print("   → Get Client ID and Client Secret")
    print()
    print("3. 🎤 Genius API:")
    print("   → https://genius.com/api-clients")
    print("   → Create a new API client")
    print("   → Get Access Token")
    print()
    print("4. 🔐 JWT Secret Key:")
    print("   → Generate a secure random string (32+ characters)")
    print("   → Or use: openssl rand -hex 32")
    print()

def get_user_input(prompt, required=True, default=None):
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        
        print("❌ This field is required. Please enter a value.")

def validate_api_key(key, key_name):
    if not key or key == f"your_{key_name.lower().replace(' ', '_')}_here":
        return False
    if len(key) < 10:  # Basic length check
        return False
    return True

def setup_env_file():
    env_path = Path(".env")
    template_path = Path(".env.template")
    
    # Read template
    if not template_path.exists():
        print("❌ .env.template file not found!")
        return False
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    print("🔧 Setting up your API keys...")
    print()
    
    # Get API keys from user
    api_keys = {}
    
    print("1️⃣ YouTube Data API Key:")
    youtube_key = get_user_input("Enter your YouTube API key")
    if not validate_api_key(youtube_key, "youtube_api_key"):
        print("⚠️  Warning: YouTube API key looks invalid")
    api_keys['YOUTUBE_API_KEY'] = youtube_key
    
    print("\n2️⃣ Spotify API Credentials:")
    spotify_client_id = get_user_input("Enter your Spotify Client ID")
    spotify_client_secret = get_user_input("Enter your Spotify Client Secret")
    if not validate_api_key(spotify_client_id, "spotify_client_id"):
        print("⚠️  Warning: Spotify Client ID looks invalid")
    if not validate_api_key(spotify_client_secret, "spotify_client_secret"):
        print("⚠️  Warning: Spotify Client Secret looks invalid")
    api_keys['SPOTIFY_CLIENT_ID'] = spotify_client_id
    api_keys['SPOTIFY_CLIENT_SECRET'] = spotify_client_secret
    
    print("\n3️⃣ Genius API Token:")
    genius_token = get_user_input("Enter your Genius Access Token")
    if not validate_api_key(genius_token, "genius_access_token"):
        print("⚠️  Warning: Genius Access Token looks invalid")
    api_keys['GENIUS_ACCESS_TOKEN'] = genius_token
    
    print("\n4️⃣ Security Configuration:")
    secret_key = get_user_input("Enter JWT Secret Key (32+ characters)", 
                               default="your-super-secret-jwt-key-change-in-production-minimum-32-characters")
    if len(secret_key) < 32:
        print("⚠️  Warning: Secret key should be at least 32 characters long")
    api_keys['SECRET_KEY'] = secret_key
    
    print("\n5️⃣ Admin Configuration:")
    admin_email = get_user_input("Admin email", default="admin@musicapi.com")
    admin_password = get_user_input("Admin password", default="admin123")
    api_keys['ADMIN_EMAIL'] = admin_email
    api_keys['ADMIN_PASSWORD'] = admin_password
    
    # Replace placeholders in template
    env_content = template_content
    for key, value in api_keys.items():
        placeholder = f"{key}=your_{key.lower()}_here"
        if placeholder not in env_content:
            # Try different placeholder formats
            placeholder = f"{key}=your-super-secret-jwt-key-change-in-production-minimum-32-characters"
            if placeholder not in env_content:
                placeholder = f"{key}=admin@musicapi.com"
                if placeholder not in env_content:
                    placeholder = f"{key}=admin123"
        
        env_content = env_content.replace(placeholder, f"{key}={value}")
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to {env_path}")
    return True

def test_configuration():
    print("\n🧪 Testing configuration...")
    
    try:
        from app.core.config import settings
        print("✅ Configuration loaded successfully!")
        print(f"   Project: {settings.PROJECT_NAME}")
        print(f"   Admin: {settings.ADMIN_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        print("   Please check your API keys and try again.")
        return False

def main():
    print_header()
    
    # Check if .env already exists
    if Path(".env").exists():
        overwrite = get_user_input("⚠️  .env file already exists. Overwrite? (y/N)", 
                                 required=False, default="N")
        if overwrite.lower() not in ['y', 'yes']:
            print("❌ Setup cancelled.")
            return
    
    print_instructions()
    
    ready = get_user_input("📝 Ready to set up your API keys? (Y/n)", 
                          required=False, default="Y")
    if ready.lower() in ['n', 'no']:
        print("❌ Setup cancelled.")
        return
    
    if setup_env_file():
        if test_configuration():
            print("\n🎉 Setup complete! You can now run the application:")
            print("   docker-compose up --build -d")
            print("   or")
            print("   uvicorn app.main:app --reload")
        else:
            print("\n⚠️  Setup completed but configuration test failed.")
            print("   Please check your API keys manually.")

if __name__ == "__main__":
    main()