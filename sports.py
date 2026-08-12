import urllib.request
import urllib.error
import re

url = 'https://neiwfusiion-rkdyiptv.pages.dev/api/rkdyiptv/playlist'
headers = {'User-Agent': 'OTT Navigator'}

def is_sports_channel(extinf_line, channel_name):
    """
    Return True if the channel is considered sports.
    Checks:
      - group-title attribute (case‑insensitive) contains 'sport'
      - or the channel name contains 'sport' (if no group-title is given)
    """
    # Try to extract group-title from #EXTINF line
    group_match = re.search(r'group-title="([^"]*)"', extinf_line, re.IGNORECASE)
    if group_match:
        group = group_match.group(1).lower()
        if 'sport' in group:
            return True
    # Fallback: check the channel name
    return 'sport' in channel_name.lower()

def filter_m3u(content):
    """
    Parse the M3U content and return only entries that are sports channels.
    """
    lines = content.splitlines()
    filtered = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#EXTM3U'):
            # Keep the header
            filtered.append(line)
            i += 1
            continue
        if line.startswith('#EXTINF'):
            # This is an info line; the next line (usually) is the URL
            extinf = line
            channel_name = ''
            # Try to extract channel name from the last comma in #EXTINF
            if ',' in extinf:
                channel_name = extinf.split(',')[-1].strip()
            # Peek at next line to get the URL (skip empty lines)
            url_line = None
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                url_line = lines[j]
            # Decide if this is a sports channel
            if is_sports_channel(extinf, channel_name):
                filtered.append(extinf)
                if url_line:
                    filtered.append(url_line)
                # Also preserve any blank lines that might follow (optional)
                # Skip to after the URL
                i = j + 1 if url_line else j
            else:
                # Skip this entry and its URL
                i = j + 1 if url_line else j
        else:
            # If line is not #EXTINF, just pass it through (e.g., comments)
            filtered.append(line)
            i += 1
    return '\n'.join(filtered)

try:
    print(f"Fetching playlist from {url}...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')

        # Filter for sports channels
        sports_content = filter_m3u(content)

        # Save the filtered playlist
        with open('sports.m3u', 'w', encoding='utf-8') as f:
            f.write(sports_content)

        print("Successfully fetched and filtered the playlist.")
        print(f"Saved to 'sports.m3u'")
        # Show a preview
        print(f"First few lines:\n{sports_content[:200]}...")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
except Exception as e:
    print(f"Error: {e}")
