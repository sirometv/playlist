import json
import requests
import os
from datetime import datetime

# কনফিগারেশন
JSON_URL = "https://raw.githubusercontent.com/IPTVFlixBD/Fancode-BD/main/data.json"
DEFAULT_STREAM = "https://crichd.workspace-sultanarabi161.workers.dev/live/asportshd.m3u8"
M3U8_FILES = [
    "1.m3u8",
    "2.m3u8", 
    "3.m3u8",
    "4.m3u8",
    "5.m3u8",
    "6.m3u8"
]
M3U8_DIR = "fancode/"

def fetch_json_data():
    """JSON ডেটা fetch করা"""
    try:
        response = requests.get(JSON_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"JSON fetch error: {e}")
        return None

def extract_adfree_urls(data):
    """JSON থেকে adfree_url গুলো extract করা"""
    adfree_urls = []
    
    if data and "matches" in data:
        for match in data["matches"]:
            if "adfree_url" in match and match["adfree_url"]:
                # URL ভ্যালিডেশন
                url = match["adfree_url"].strip()
                if url.startswith("http"):
                    adfree_urls.append(url)
                    print(f"Found adfree_url: {url}")
    
    return adfree_urls

def create_m3u8_content(stream_url):
    """M3U8 ফাইল কন্টেন্ট তৈরি করা"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:5.0,
{stream_url}
"""

def update_m3u8_files(adfree_urls):
    """সব M3U8 ফাইল আপডেট করা"""
    # প্রাপ্ত URL এবং ডিফল্ট URL মিলিয়ে লিস্ট তৈরি
    streams = []
    
    # প্রথমে adfree_url গুলো নিন
    for url in adfree_urls:
        if len(streams) < 6:
            streams.append(url)
    
    # বাকিগুলোর জন্য ডিফল্ট স্ট্রিম
    while len(streams) < 6:
        streams.append(DEFAULT_STREAM)
    
    print(f"Total streams to update: {len(streams)}")
    
    # প্রতিটি M3U8 ফাইল আপডেট করুন
    for i, (filename, stream_url) in enumerate(zip(M3U8_FILES, streams)):
        filepath = os.path.join(M3U8_DIR, filename)
        content = create_m3u8_content(stream_url)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filepath} with stream {i+1}")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")

def main():
    print(f"=== Starting update at {datetime.now()} ===")
    
    # JSON ডেটা fetch করুন
    data = fetch_json_data()
    
    if not data:
        print("Using default streams only")
        adfree_urls = []
    else:
        # adfree_url গুলো extract করুন
        adfree_urls = extract_adfree_urls(data)
        print(f"Extracted {len(adfree_urls)} adfree URLs")
    
    # M3U8 ফাইলগুলো আপডেট করুন
    update_m3u8_files(adfree_urls)
    
    print(f"=== Update completed at {datetime.now()} ===")

if __name__ == "__main__":
    main()
