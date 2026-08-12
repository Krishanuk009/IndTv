#!/usr/bin/env python3


import re
import json
import requests
from datetime import datetime
from urllib.parse import unquote, urlparse
import pytz

PLAYLIST_URL = "https://go.streamstar18.workers.dev/"
JSON_OUTPUT = "jtv.json"
M3U_OUTPUT = "jtv.m3u"

# Default user agent if not specified
DEFAULT_USER_AGENT = "IndTv"


def compute_hdnea_expiry(cookie_str):
    """Decodes exp=<epoch> out of a __hdnea__ cookie into an IST string."""
    if not cookie_str or "__hdnea__" not in cookie_str:
        return ""
    match = re.search(r"exp=(\d+)", cookie_str)
    if not match:
        return ""
    try:
        ist = pytz.timezone("Asia/Kolkata")
        dt = datetime.fromtimestamp(int(match.group(1)), ist)
        return f"{dt.day}/{dt.month}/{dt.year} {dt.strftime('%I:%M:%S %p').lstrip('0')} IST"
    except (ValueError, OSError):
        return ""


def extract_key_from_m3u8(text):
    """Extract clearkey from #KODIPROP lines in M3U8 content."""
    # Look for #KODIPROP:inputstream.adaptive.license_key=<key>
    match = re.search(r'#KODIPROP:inputstream\.adaptive\.license_key=([a-f0-9]+):([a-f0-9]+)', text, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return "", ""


def parse_stream_line(line):
    """
    Parse stream URL line. Handles both:
    1. Simple URL with optional query params
    2. URL with pipe-separated headers
    """
    decoded = unquote(line.strip())
    
    # If no pipe, it's a simple URL
    if "|" not in decoded:
        return decoded, "", DEFAULT_USER_AGENT
    
    base_url, header_part = decoded.split("|", 1)
    cookie = ""
    user_agent = DEFAULT_USER_AGENT
    
    # Extract cookie if present
    m = re.search(r"(?:^|&)cookie=([^&]+)", header_part, re.IGNORECASE)
    if m:
        cookie = m.group(1)
    
    # Extract user agent if present
    m = re.search(r"(?:^|&)User-Agent=([^&]+)", header_part, re.IGNORECASE)
    if m:
        user_agent = m.group(1)
    
    return base_url.strip(), cookie.strip(), user_agent.strip()


def parse_playlist(text):
    """Parse the playlist content into channel objects."""
    blocks = re.split(r"\n\s*\n", text)
    channels = []

    for block in blocks:
        if "#EXTINF" not in block:
            continue

        lines = [l.strip() for l in block.splitlines() if l.strip()]
        
        # Extract EXTINF line
        extinf_line = next((l for l in lines if l.startswith("#EXTINF")), "")
        if not extinf_line:
            continue

        def attr(key):
            m = re.search(rf'{key}="([^"]*)"', extinf_line)
            return m.group(1) if m else ""

        channel_id = attr("tvg-id")
        logo = attr("tvg-logo")
        group = attr("group-title")
        name = extinf_line.rsplit(",", 1)[-1].strip()
        
        # Extract user agent from EXTVLCOPT if present
        user_agent = DEFAULT_USER_AGENT
        for l in lines:
            if l.startswith("#EXTVLCOPT:http-user-agent="):
                user_agent = l.split("=", 1)[1].strip()
                break
        
        # Extract license key if present in block
        key_id, key = "", ""
        for l in lines:
            if l.startswith("#KODIPROP:inputstream.adaptive.license_key="):
                key_part = l.split("=", 1)[1].strip()
                if ":" in key_part:
                    key_id, key = key_part.split(":", 1)
                break
        
        # Get stream URL
        stream_line = next((l for l in lines if not l.startswith("#") and not l.startswith("//")), "")
        if not stream_line:
            continue

        base_url, cookie, ua = parse_stream_line(stream_line)
        
        # Use user agent from EXTVLCOPT if available
        if user_agent != DEFAULT_USER_AGENT:
            ua = user_agent

        channels.append({
            "id": channel_id,
            "name": name,
            "logo": logo,
            "group": group,
            "stream_url": base_url,
            "cookie": cookie,
            "user_agent": ua,
            "key_id": key_id,
            "key": key,
            "raw_block": block  # Keep raw block for M3U8 key extraction
        })

    return channels


def fetch_and_build():
    print(f"[*] Fetching playlist: {PLAYLIST_URL}")
    resp = requests.get(PLAYLIST_URL, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=20)
    resp.raise_for_status()

    channels = parse_playlist(resp.text)
    print(f"[+] Parsed {len(channels)} channels from playlist")
    
    # Process channels that need key resolution from M3U8
    for ch in channels:
        # If key already extracted from KODIPROP in playlist, skip
        if ch["key_id"] and ch["key"]:
            continue
            
        # If it's an M3U8 URL, fetch and extract key
        url = ch["stream_url"]
        if url and ".m3u8" in url.lower():
            try:
                print(f"[*] Fetching M3U8 for {ch['name']}: {url}")
                headers = {"User-Agent": ch["user_agent"]}
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    key_id, key = extract_key_from_m3u8(resp.text)
                    if key_id and key:
                        ch["key_id"] = key_id
                        ch["key"] = key
                        print(f"[+] Found key for {ch['name']}: {key_id}:{key}")
            except Exception as e:
                print(f"[!] Failed to fetch M3U8 for {ch['name']}: {e}")

    final_channels = []
    for ch in channels:
        final_channels.append({
            "id": ch["id"],
            "name": ch["name"],
            "stream_url": ch["stream_url"],
            "cookie": ch["cookie"],
            "cookie_expires": compute_hdnea_expiry(ch["cookie"]),
            "key_id": ch["key_id"],
            "key": ch["key"],
            "logo": ch["logo"],
            "group": ch["group"],
            "user_agent": ch["user_agent"]
        })

    # Save JSON
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(final_channels, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved JSON: {JSON_OUTPUT}")

    # Generate M3U8
    m3u_lines = ["#EXTM3U"]
    skipped = 0
    
    for ch in final_channels:
        if not ch["stream_url"]:
            skipped += 1
            continue
            
        # Build stream URL (without cookie in URL)
        stream_url = ch["stream_url"]
        
        # Determine if it's HLS or DASH based on URL
        manifest_type = "hls" if ".m3u8" in stream_url.lower() else "mpd"
        
        # Add EXTVLCOPT for user agent
        m3u_lines.append(f'#EXTVLCOPT:http-user-agent={ch["user_agent"]}')
        
        # Add EXTINF line
        m3u_lines.append(
            f'#EXTINF:-1 tvg-id="{ch["id"]}" group-title="{ch["group"]}" '
            f'tvg-logo="{ch["logo"]}",{ch["name"]}'
        )
        
        # Add KODIPROP lines if key exists
        if ch["key_id"] and ch["key"]:
            m3u_lines.append("#KODIPROP:inputstream.adaptive.manifest_type=" + manifest_type)
            m3u_lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
            m3u_lines.append(f'#KODIPROP:inputstream.adaptive.license_key={ch["key_id"]}:{ch["key"]}')
        
        # Add stream URL
        m3u_lines.append(stream_url)
        m3u_lines.append("")

    with open(M3U_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    playable = len(final_channels) - skipped
    print(f"[+] Saved M3U: {M3U_OUTPUT} ({playable} playable, {skipped} skipped)")


if __name__ == "__main__":
    fetch_and_build()
