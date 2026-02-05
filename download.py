
import requests
import re
import os
import time

# Path to the wallpapers and blacklist files
wallpaperlist_file_path = 'bing-wallpaper.md'
blacklist_file_path = 'blacklist.txt'

# Download folders
download_dir = "downloads/good"
blacklisted_dir = "downloads/bad"

# Function to download images
def download_image(i, total, url, folder_name, file_name, need_cleanup):
    if need_cleanup:
        print('\033[2K', end='')
    if not os.path.exists(os.path.join('./', folder_name)):
        os.makedirs(os.path.join('./', folder_name))
    full_name = os.path.join(folder_name, file_name)
    if os.path.exists(full_name):
        time.sleep(0.01)
        print(f"🚫 [{i + 1}/{total}]: File exists {full_name}", end="\r")
        need_cleanup = True
    else:
        time.sleep(0.1)
        response = requests.get(url)
        if response.status_code == 200:
            with open(full_name, 'wb') as file:
                file.write(response.content)
            print(f"✅ [{i + 1}/{total}]: Downloaded {full_name}")
            need_cleanup = False
        else:
            print(f"🛑 [{i + 1}/{total}]: Failed to download {url}")
            need_cleanup = False
    return need_cleanup
# Function to scrape image URLs from file
def scrape_image_urls(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regular expression to find all URLs that end with image file extensions
    image_urls = re.findall(r'(https?://[^\s]+\.jpg|png|jpeg|gif)', content)
    return image_urls
# Function to scrape filenames from blacklist file
def scrape_image_names(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regular expression to find all filenames that end with image file extensions
    image_names = re.findall(r'([^\s]+\.jpg|png|jpeg|gif)', content)
    return image_names
# Move downloaded files to appropriate folders
def sort_images(download_folder, blacklisted_folder, blacklist):
    if not os.path.exists(os.path.join('./', download_folder)):
        os.makedirs(os.path.join('./', download_folder))
    if not os.path.exists(os.path.join('./', blacklisted_folder)):
        os.makedirs(os.path.join('./', blacklisted_folder))

    for file in os.listdir(download_folder):
        if os.path.isfile(os.path.join(download_folder, file)) and file in blacklist:
            time.sleep(0.01)
            os.rename(os.path.join(download_folder, file), os.path.join(blacklisted_folder, file))
            print(f"👎 Moved {file} to {blacklisted_folder}")
    for file in os.listdir(blacklisted_folder):
        if os.path.isfile(os.path.join(blacklisted_folder, file)) and file not in blacklist:
            time.sleep(0.01)
            os.rename(os.path.join(blacklisted_folder, file), os.path.join(download_folder, file))
            print(f"👍 Moved {file} to {download_folder}")

#allow import of functions from other files
if __name__ == "__main__":
    # Scrape image URLs from the README file
    image_urls = set(scrape_image_urls(wallpaperlist_file_path))
    blacklisted_files = set(scrape_image_names(blacklist_file_path))

    # Sort downloaded files
    sort_images(download_dir, blacklisted_dir, blacklisted_files)

    # Download each image
    need_cleanup = False
    for i, url in enumerate(image_urls):
        file_name = url.split('OHR.')[1]
        folder_name = download_dir
        if file_name in blacklisted_files:
            folder_name = blacklisted_dir
        need_cleanup = download_image(i, len(image_urls), url, folder_name, file_name, need_cleanup)
    if need_cleanup:
        print('\033[2K', end='')
    print("😃 Done!")
