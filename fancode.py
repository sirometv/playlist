import requests
import base64
import os
from datetime import datetime

# Configuration
JSON_URL = "https://raw.githubusercontent.com/IPTVFlixBD/Fancode-BD/main/data.json"
DEFAULT_STREAM = "https://crichd.workspace-sultanarabi161.workers.dev/live/asportshd.m3u8"
REPO_OWNER = "sirometv"
REPO_NAME = "playlist"
GITHUB_PATH = "fancode"

def get_adfree_urls():
    """Fetch adfree URLs from JSON"""
    try:
        response = requests.get(JSON_URL, timeout=10)
        data = response.json()
        adfree_urls = []
        
        # Method 1: Check if 'matches' exists in data
        if 'matches' in data and isinstance(data['matches'], list):
            for match in data['matches']:
                if 'adfree_url' in match and match['adfree_url']:
                    adfree_urls.append(match['adfree_url'])
        
        # Method 2: If data is a list
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if 'adfree_url' in item and item['adfree_url']:
                        adfree_urls.append(item['adfree_url'])
        
        print(f"✅ Found {len(adfree_urls)} adfree URLs")
        return adfree_urls
        
    except Exception as e:
        print(f"❌ Error fetching JSON: {e}")
        return []

def create_m3u8_content(stream_url):
    """Create M3U8 file content"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:5.0, Stream
{stream_url}
"""

def update_single_file(file_number, stream_url, token):
    """Update single M3U8 file"""
    filename = f"{file_number}.m3u8"
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{GITHUB_PATH}/{filename}"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Create content
    content = create_m3u8_content(stream_url)
    encoded_content = base64.b64encode(content.encode()).decode()
    
    # Get current file SHA (if exists)
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        sha = response.json().get('sha') if response.status_code == 200 else None
    except:
        sha = None
    
    # Prepare data for GitHub API
    data = {
        "message": f"Auto-update {filename} at {datetime.now().strftime('%H:%M:%S')}",
        "content": encoded_content,
        "committer": {
            "name": "Auto Updater",
            "email": "updater@github.com"
        }
    }
    
    if sha:
        data["sha"] = sha
    
    # Update file
    response = requests.put(api_url, headers=headers, json=data, timeout=15)
    
    if response.status_code in [200, 201]:
        print(f"✅ Updated {filename}")
        return True
    else:
        print(f"❌ Failed to update {filename}: {response.status_code}")
        return False

def main():
    """Main function"""
    print("🚀 Starting M3U8 Auto Update...")
    print("-" * 50)
    
    # Get GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ ERROR: GITHUB_TOKEN not found!")
        return
    
    # Get adfree URLs
    adfree_urls = get_adfree_urls()
    
    # Update 6 M3U8 files
    total_files = 6
    success_count = 0
    
    for i in range(1, total_files + 1):
        # Choose URL: adfree if available, otherwise default
        if i <= len(adfree_urls):
            stream_url = adfree_urls[i-1]
            source = "JSON"
        else:
            stream_url = DEFAULT_STREAM
            source = "DEFAULT"
        
        print(f"\n📁 Processing {i}.m3u8 ({source})...")
        
        if update_single_file(i, stream_url, token):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 UPDATE SUMMARY:")
    print(f"Total files: {total_files}")
    print(f"Successfully updated: {success_count}")
    print(f"JSON URLs used: {min(len(adfree_urls), total_files)}")
    print(f"Default URLs used: {max(0, total_files - len(adfree_urls))}")
    print("=" * 50)
    
    if success_count == total_files:
        print("🎉 All files updated successfully!")
    else:
        print("⚠️ Some files failed to update")

if __name__ == "__main__":
    main()
