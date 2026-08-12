import json
import urllib.request


url = "https://raw.githubusercontent.com/qwerty180506/json/refs/heads/main/Geoplus.json"
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode("utf-8"))


m3u_lines = ["#EXTM3U"]

for item in data:
    name = item.get("name", "")
    tvg_id = item.get("id", "")
    category = item.get("category", "")
    logo = item.get("logo", "")
    mpd = item.get("mpd", "")
    cookie = item.get("cookie", "")
    key_id = item.get("keyId", "")
    key = item.get("key", "")

    # 构建 license_key（格式：key_id:key）
    license_key = f"{key_id}:{key}" if key_id and key else ""

    # EXTINF 行
    extinf = (
        f'#EXTINF:-1 tvg-id="{tvg_id}" '
        f'tvg-name="{name}" '
        f'tvg-logo="{logo}" '
        f'group-title="{category}",{name}'
    )
    m3u_lines.append(extinf)

    
    m3u_lines.append("#KODIPROP:inputstream.adaptive.manifest_type=mpd")
    m3u_lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
    if license_key:
        m3u_lines.append(f"#KODIPROP:inputstream.adaptive.license_key={license_key}")

    
    m3u_lines.append("#EXTVLCOPT:http-user-agent=Virat Paglu")

   
    if cookie:
        m3u_lines.append(f'#EXTHTTP:{{"cookie":"{cookie}","Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}')

    
    if mpd:
        m3u_lines.append(mpd)

    
    m3u_lines.append("")


with open("jtvplus6.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u_lines))

print("M3U ：jtvplus6.m3u")
