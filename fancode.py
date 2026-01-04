import json
import requests
import os
from datetime import datetime

# কনফিগারেশন
JSON_URL = "https://raw.githubusercontent.com/IPTVFlixBD/Fancode-BD/main/data.json"
DEFAULT_STREAM = "https://crichd.workspace-sultanarabi161.workers.dev/live/asportshd.m3u8"

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
                print(f"Checking match {i+1}: {match.get('title', 'No title')}")
                
                if "adfree_url" in match and match["adfree_url"]:
                    url = str(match["adfree_url"]).strip()
                    if url.startswith("http"):
                        adfree_urls.append(url)
                        print(f"✓ Added adfree_url: {url}")
                    else:
                        print(f"✗ Invalid URL format: {url}")
                else:
                    print(f"✗ No adfree_url in match {i+1}")
        else:
            print("No 'matches' key found in JSON")
    else:
        print("Invalid or empty JSON data")
    
    return adfree_urls

def create_m3u8_content(stream_url):
    """M3U8 ফাইল কন্টেন্ট তৈরি করা"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:5.0,
{stream_url}
#EXTINF:5.0,
{stream_url}
"""

def update_m3u8_files(adfree_urls):
    """সব M3U8 ফাইল আপডেট করা"""
    print(f"\nUpdating M3U8 files...")
    print(f"Available adfree URLs: {len(adfree_urls)}")
    
    # ৬টি ফাইলের জন্য streams প্রস্তুত করা
    streams = []
    
    # adfree_url গুলো যোগ করুন
    for i, url in enumerate(adfree_urls):
        if i >= 6:  # সর্বোচ্চ ৬টি
            break
        streams.append(url)
        print(f"Stream {i+1}: {url}")
    
    # বাকি জায়গায় ডিফল্ট স্ট্রিম
    for i in range(len(streams), 6):
        streams.append(DEFAULT_STREAM)
        print(f"Stream {i+1}: [DEFAULT] {DEFAULT_STREAM}")
    
    # প্রতিটি M3U8 ফাইল আপডেট করুন
    for i in range(6):
        filename = f"{i+1}.m3u8"
        filepath = os.path.join("fancode", filename)
        stream_url = streams[i]
        
        try:
            # ডিরেক্টরি তৈরি করুন
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # কন্টেন্ট তৈরি করুন
            content = create_m3u8_content(stream_url)
            
            # ফাইল লিখুন
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Updated {filepath}")
            
        except Exception as e:
            print(f"✗ Error writing {filepath}: {e}")

def main():
    print("=" * 50)
    print(f"Fancode to M3U8 Update Script")
    print(f"Started at: {datetime.now()}")
    print("=" * 50)
    
    # JSON ডেটা fetch করুন
    data = fetch_json_data()
    
    # adfree_url গুলো extract করুন
    if data:
        adfree_urls = extract_adfree_urls(data)
    else:
        adfree_urls = []
        print("Using default streams only")
    
    # M3U8 ফাইলগুলো আপডেট করুন
    update_m3u8_files(adfree_urls)
    
    print("=" * 50)
    print(f"Completed at: {datetime.now()}")
    print("=" * 50)

if __name__ == "__main__":
    main()
