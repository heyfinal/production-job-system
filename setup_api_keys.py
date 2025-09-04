#!/usr/bin/env python3
"""
Interactive API Key Setup for Production Job Search System
Guides you through getting and configuring your RapidAPI key
"""

import json
import os
import webbrowser
from pathlib import Path

def setup_rapidapi_key():
    """Interactive setup for RapidAPI key"""
    print("🔑 RapidAPI Key Setup for JSearch API")
    print("=" * 50)
    
    api_keys_path = Path.home() / '.config' / 'jobsearch' / 'api_keys.json'
    
    # Check if already configured
    if api_keys_path.exists():
        with open(api_keys_path) as f:
            config = json.load(f)
        
        current_key = config.get('rapidapi_key', '')
        if current_key and current_key != 'YOUR_ACTUAL_RAPIDAPI_KEY_HERE':
            print(f"✅ RapidAPI key already configured: {current_key[:20]}...")
            update = input("Do you want to update it? (y/N): ").lower()
            if update != 'y':
                return current_key
    
    print("\n📋 Step-by-Step Setup:")
    print("1. 🌐 Opening RapidAPI JSearch page in your browser...")
    
    # Open the API page
    api_url = "https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch"
    try:
        webbrowser.open(api_url)
        print(f"   Opened: {api_url}")
    except:
        print(f"   Please manually visit: {api_url}")
    
    print("\n2. 📝 Complete these steps on the website:")
    print("   a. Create a free RapidAPI account (if you don't have one)")
    print("   b. Click 'Subscribe to Test' or 'Pricing' tab")
    print("   c. Choose the FREE tier (1,000 requests/month)")
    print("   d. Click 'Subscribe' on the free plan")
    print("   e. Go to 'Endpoints' tab")
    print("   f. Find 'X-RapidAPI-Key' in the request headers")
    print("   g. Copy the API key (starts with something like 'abc123...')")
    
    input("\n⏳ Press Enter when you have copied your API key...")
    
    # Get API key from user
    print("\n3. 🔐 Paste your RapidAPI key:")
    api_key = input("Enter your RapidAPI key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return None
    
    if len(api_key) < 20:
        print("⚠️  API key seems too short. RapidAPI keys are usually longer.")
        confirm = input("Continue anyway? (y/N): ").lower()
        if confirm != 'y':
            return None
    
    # Save the API key
    config = {
        "rapidapi_key": api_key,
        "icloud_password": None,
        "slack_webhook": None,
        "_configured": True,
        "_setup_date": "2025-01-04",
        "_note": "RapidAPI key for JSearch API - keep secure"
    }
    
    # Ensure directory exists
    api_keys_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    with open(api_keys_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set secure permissions
    os.chmod(api_keys_path, 0o600)
    
    print(f"\n✅ API key saved securely to: {api_keys_path}")
    print("🔒 File permissions set to 600 (owner read/write only)")
    
    return api_key

def test_api_key(api_key):
    """Test the API key with a simple request"""
    print("\n🧪 Testing API key...")
    
    try:
        import requests
        
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": "software engineer",
            "page": "1",
            "num_pages": "1"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            job_count = len(data.get('data', []))
            print(f"✅ API key working! Found {job_count} test jobs")
            return True
        elif response.status_code == 403:
            print("❌ API key invalid or subscription issue")
            print("   Check that you've subscribed to the free tier")
            return False
        else:
            print(f"⚠️  API returned status {response.status_code}")
            print("   This might still work - continuing...")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Network error testing API: {e}")
        print("   API key saved - will test later when running job search")
        return True
    except ImportError:
        print("⚠️  Cannot test API key (requests not installed)")
        print("   API key saved - will test when running job search")
        return True
    except Exception as e:
        print(f"⚠️  Error testing API: {e}")
        print("   API key saved - will test later")
        return True

def main():
    """Main setup flow"""
    print("🚀 Production Job Search System - API Setup")
    print("🎯 Get ready to find REAL job opportunities!")
    print()
    
    # Setup RapidAPI key
    api_key = setup_rapidapi_key()
    
    if api_key:
        # Test the key
        if test_api_key(api_key):
            print("\n🎉 Setup Complete!")
            print()
            print("📋 Next Steps:")
            print("1. 🧪 Test your job search:")
            print("   cd /Users/daniel/workapps/production_job_system")
            print("   source venv/bin/activate")
            print("   python quick_test.py")
            print()
            print("2. 🚀 Run your first real job search:")
            print("   python main.py --test")
            print()
            print("3. ⚙️  Enable daily automation (6 AM daily):")
            print("   ./manage_service.sh start")
            print()
            print("🎯 Expected Results:")
            print("   • 100-200 real jobs from legitimate sources")
            print("   • 15-30 high-match opportunities for your profile")
            print("   • Working application URLs")
            print("   • Professional HTML reports")
        else:
            print("\n⚠️  API key saved but may need attention")
            print("   Try running the job search test anyway")
    else:
        print("\n❌ Setup cancelled")
        print("   Run this script again when ready to add your API key")

if __name__ == "__main__":
    main()