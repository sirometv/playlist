import json
import requests
import os
from datetime import datetime

# কনফিগারেশন
JSON_URL = "https://raw.githubusercontent.com/IPTVFlixBD/Fancode-BD/main/data.json"
DEFAULT_STREAM = "https://crichd.workspace-sultanarabi161.workers.dev/live/asportshd.m3u8"
M3U8_HEADER = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
"""

def fetch_json_data():
    """JSON ডেটা fetch করা"""
    try:
        print(f"Fetching JSON from: {JSON_URL}")
        response = requests.get(JSON_URL, timeout=10)
        response.raise_for_status()
        print("JSON fetched successfully")
        return response.json()
    except Exception as e:
        print(f"JSON fetch error: {e}")
        return None

def extract_adfree_urls(data):
    """JSON থেকে adfree_url গুলো extract করা"""
    adfree_urls = []
    
    if data and isinstance(data, dict):
        print(f"Data keys: {list(data.keys())}")
        
        if "matches" in data:
            print(f"Found {len(data['matches'])} matches")
            
            for i, match in enumerate(data["matches"]):
                match_title = match.get('title', f'Match {i+1}')
                print(f"Checking match {i+1}: {match_title}")
                
                if "adfree_url" in match and match["adfree_url"]:
                    url = str(match["adfree_url"]).strip()
                    if url.startswith("http"):
                        adfree_urls.append(url)
                        print(f"✓ Added adfree_url: {url[:50]}...")
                    else:
                        print(f"✗ Invalid URL format")
                else:
                    print(f"✗ No adfree_url in this match")
        else:
            print("No 'matches' key found in JSON")
    else:
        print("Invalid or empty JSON data")
    
    return adfree_urls

def update_m3u8_file(filepath, stream_url):
    """একটি M3U8 ফাইল আপডেট করা"""
    try:
        # নতুন কন্টেন্ট তৈরি (শুধু URL আপডেট)
        new_content = f"""{M3U8_HEADER}{stream_url}"""
        
        # ফাইল লিখুন
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"✗ Error writing {filepath}: {e}")
        return False

def main():
    print("=" * 50)
    print(f"Fancode to M3U8 Update Script")
    print(f"Started at: {datetime.now()}")
    print("=" * 50)
    
    # JSON ডেটা fetch করুন
    data = fetch_json_data()
    
    # adfree_url গুলো extract করুন
    adfree_urls = []
    if data:
        adfree_urls = extract_adfree_urls(data)
    else:
        print("No JSON data found, using default streams only")
    
    print(f"\nTotal adfree URLs found: {len(adfree_urls)}")
    
    # ৬টি M3U8 ফাইলের জন্য প্রস্তুত করা
    streams_to_update = []
    
    # প্রথমে adfree_url গুলো নিন
    for i in range(6):
        if i < len(adfree_urls):
            streams_to_update.append(adfree_urls[i])
            print(f"File {i+1}.m3u8 → adfree_url {i+1}")
        else:
            streams_to_update.append(DEFAULT_STREAM)
            print(f"File {i+1}.m3u8 → DEFAULT stream")
    
    # প্রতিটি M3U8 ফাইল আপডেট করুন
    print("\nUpdating M3U8 files...")
    success_count = 0
    
    for i in range(6):
        filename = f"{i+1}.m3u8"
        filepath = os.path.join("fancode", filename)
        stream_url = streams_to_update[i]
        
        print(f"\nUpdating {filename}:")
        print(f"URL: {stream_url}")
        
        # ডিরেক্টরি তৈরি করুন (যদি না থাকে)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # ফাইল আপডেট করুন
        if update_m3u8_file(filepath, stream_url):
            success_count += 1
            print(f"✓ Successfully updated")
        else:
            print(f"✗ Failed to update")
    
    print("\n" + "=" * 50)
    print(f"Update Summary:")
    print(f"Successfully updated: {success_count}/6 files")
    print(f"Completed at: {datetime.now()}")
    print("=" * 50)
    
    # GitHub Actions-এ exit code
    if success_count == 6:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
