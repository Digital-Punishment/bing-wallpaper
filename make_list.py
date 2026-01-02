
import requests
import re
import os
import time
import datetime
from urllib.parse import urljoin
from download import scrape_image_urls

wallpaperlist_file = "bing-wallpaper.md"
bing_server = "https://cn.bing.com/"

db_URL = "https://raw.githubusercontent.com/zigou23/Bing-Daily-Wallpaper/"
db_json_dir = "refs/heads/main/bing/"
db_old_json_dir = "refs/heads/main/bing/old-2408/"

# Regions to parse
bing_regions = [
    "bing_en-US",
    "bing_en-CA",
    "bing_en-GB",
    "bing_en-IN",
    "bing_de-DE",
    "bing_es-ES",
    "bing_fr-CA",
    "bing_fr-FR",
    "bing_it-IT",
    "bing_ja-JP",
    "bing_pt-BR",
    "bing_zh-CN",
    "bing_ROW",
]

# Image resolutions to check for
bing_resolutions = [
    "UHD", # (3840×2160) 4K Ultra HD
    "1920x1080", # Full HD
    # "1366x768", # HD
    # "1280x720", # HD 720p
    #
    # "1920x1200", # WUXGA
    # "1280x768", # WXGA
    # "1024x768", # XGA
    # "800x600", # SVGA
    # "640x480", # VGA
    # "400x240", # Thumbnail
    # "320x240", # QVGA Thumbnail
    #
    # "1080x1920", # Full HD Mobile
    # "720x1280", # HD Mobile
    #
    # "768x1280", # WXGA Mobile
    # "480x800", # WVGA
    # "240x320", # Portrait Thumbnail
]

# Parse JSON files from github and make a list of unique wallpapers
def parse_json(regions):
    uppercase_langs = list(map(lambda i: i.split("_")[1].upper(), regions))
    uppercase_langs.append("EN-AU")

    checklist = set()
    wallpapers = []
    wallpapers_count = 0

    for region in regions:
        for dir in [db_old_json_dir, db_json_dir]:
            json_URL = urljoin(urljoin(db_URL, dir), region+".json")
            print(f"Processing: {json_URL}")
            time.sleep(0.1)
            json_file = requests.get(json_URL)
            if json_file.status_code == 200:
                data = json_file.json()
                print(f"\t    {len(data)} records in file")
                for item in data:
                    if item['date'] != "" and item['urlbase'] != "":
                        date = item['date']
                        urlbase = item['urlbase']
                        copyright = item['copyright']

                        basename = urlbase.split('OHR.')[1].rsplit('_', maxsplit = 1)
                        checkname = basename[0]
                        reg = basename[1][:5] if basename[1][:3] != "ROW" else basename[1][:3]

                        if checkname not in checklist:
                            if reg in uppercase_langs:
                                wallpapers.append({'date': date, 'region': reg, 'copyright': copyright, 'urlbase': urlbase})
                                checklist.add(checkname)
                            else:
                                print(f"🛑 Unknown region: {reg}")

                print(f"\t    {len(checklist)} unique filenames total (+{len(checklist) - wallpapers_count})")
                wallpapers_count = len(checklist)
            else:
                print("😞 File not available")

    return sorted(wallpapers, key=lambda i: (len(uppercase_langs) - uppercase_langs.index(i['region']), i['date']), reverse=True)

# Generate a human readable list of wallpapers
def generate_filecontent(wallpapers_list, resolutions):
    image_urls = set(scrape_image_urls(wallpaperlist_file))
    content = "## Bing Wallpaper\n\n"
    for wallpaper in wallpapers_list:
        date = datetime.date(int(wallpaper['date'][:4]), int(wallpaper['date'][4:6]),int(wallpaper['date'][6:])) + datetime.timedelta(days=1)
        urlbase = wallpaper['urlbase'].replace("https://bing.com/", bing_server).replace("https://www.bing.com/", bing_server)
        copyright = wallpaper['copyright']
        reg = wallpaper['region']
        reg = " " if reg == "EN-US" else f" [{reg}] "

        resolution = ""
        for res in resolutions:
            wallpaper_URL = f"{urlbase}_{res}.jpg"
            if wallpaper_URL in image_urls:
                resolution = res
                print(f"✅ Record found in {wallpaperlist_file}: {urlbase}")
                break

        if resolution == "":
            for res in resolutions:
                wallpaper_URL = f"{urlbase}_{res}.jpg"
                time.sleep(0.1)
                response = requests.head(wallpaper_URL, timeout=5)
                if response.status_code == 200:
                    resolution = res
                    print(f"👍 Link to {resolution} file found: {urlbase}")
                    break

        if resolution == "":
            print(f"👎 No links found: {urlbase}")
        else:
            content += f"{date}{reg}| [{copyright}]({urlbase}_{resolution}.jpg)\n\n"
    return content

if __name__ == "__main__":
    file_content = generate_filecontent(parse_json(bing_regions), bing_resolutions)
    with open(wallpaperlist_file, 'w') as file:
        file.write(file_content)
    print(f"😃 {wallpaperlist_file} created!")
