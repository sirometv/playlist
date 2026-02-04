import json
import requests
from datetime import datetime

# JSON ফাইলের URL (আপনার JSON ফাইল URL দিয়ে রিপ্লেস করুন)
JSON_URL = "https://raw.githubusercontent.com/sirometv/playlist/main/fancode.json"

def fetch_json_data():
    """JSON ফাইল ডাউনলোড এবং পার্স করা"""
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching JSON: {e}")
        return None

def extract_streams(data, country_code):
    """JSON থেকে স্ট্রিম ডেটা এক্সট্র্যাক্ট করা"""
    streams = []
    
    if "matches" not in data:
        print("No 'matches' found in JSON")
        return streams
    
    for match in data["matches"]:
        # শুধুমাত্র adfree_url থাকলে নিবে
        if "adfree_url" in match and match["adfree_url"]:
            # country_code অনুযায়ী URL পরিবর্তন
            stream_url = match["adfree_url"]
            
            if country_code == "bd":
                # BD playlist: https://bd-mc-fdlive.fancode.com/...
                if "https://in-" in stream_url:
                    stream_url = stream_url.replace("https://in-", "https://bd-")
            elif country_code == "in":
                # IN playlist: https://in-mc-fdlive.fancode.com/...
                if "https://bd-" in stream_url:
                    stream_url = stream_url.replace("https://bd-", "https://in-")
            
            # EXTINF entry তৈরি
            extinf_entry = {
                "title": match.get("title", "Unknown"),
                "logo": match.get("logo_url", ""),
                "group": match.get("group_title", ""),
                "stream_url": stream_url
            }
            streams.append(extinf_entry)
    
    return streams

def create_m3u_content(streams, playlist_name):
    """M3U প্লেলিস্ট কন্টেন্ট তৈরি করা"""
    content = ["#EXTM3U"]
    
    for stream in streams:
        extinf_line = f'#EXTINF:-1 tvg-logo="{stream["logo"]}" group-title="{stream["group"]}", {stream["title"]}'
        content.append(extinf_line)
        content.append(stream["stream_url"])
    
    return "\n".join(content)

def update_playlist_file(filename, content):
    """ফাইলে ম3ু কন্টেন্ট লিখা"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filename}")

def main():
    print(f"Starting playlist update at {datetime.now()}")
    
    # JSON ডেটা ফেচ করা
    data = fetch_json_data()
    if not data:
        return
    
    # BD প্লেলিস্টের জন্য স্ট্রিমস
    bd_streams = extract_streams(data, "bd")
    print(f"Found {len(bd_streams)} streams for BD playlist")
    
    # IN প্লেলিস্টের জন্য স্ট্রিমস
    in_streams = extract_streams(data, "in")
    print(f"Found {len(in_streams)} streams for IN playlist")
    
    # M3U কন্টেন্ট তৈরি
    bd_content = create_m3u_content(bd_streams, "Fancode Bangladesh")
    in_content = create_m3u_content(in_streams, "Fancode India")
    
    # ফাইল আপডেট
    update_playlist_file("fancodeBD.m3u", bd_content)
    update_playlist_file("fancodeIND.m3u", in_content)
    
    print(f"Playlists updated successfully at {datetime.now()}")

if __name__ == "__main__":
    main()
