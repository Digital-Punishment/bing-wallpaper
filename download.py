import requests
import re
import time
from http import HTTPStatus
from pathlib import Path, PurePath

# Path to the wallpapers and blacklist files
wallpaperlist_filename = "bing-wallpaper.md"
blacklist_filename = "blacklist.txt"

# Download folders
download_dir = "./downloads/good"
blacklisted_dir = "./downloads/bad"


def download_image(prefix: str, url: str, full_name: Path) -> bool:
    """Download images."""
    parent_folder = Path(PurePath(full_name).parent)
    if not parent_folder.exists():
        parent_folder.mkdir(parents=True)

    need_cleanup = False
    if Path(full_name).exists():
        time.sleep(0.01)
        print(f"🚫  {prefix} File exists: {full_name}", end="\r")
        need_cleanup = True
    else:
        print(f"✅  {prefix} Downloading: {full_name}", end="\r")
        time.sleep(0.1)
        response = requests.get(url, timeout=5)
        if response.status_code == HTTPStatus.OK:
            with Path(full_name).open(mode="wb") as file:
                file.write(response.content)
                print("\033[2K", end="")
            print(f"✅  {prefix} Download complete: {full_name}")
        else:
            print("\033[2K", end="")
            print(f"🛑  {prefix} Download failed: {url}")
    return need_cleanup


def scrape_image_urls(file_path: Path) -> list:
    """Scrape image URLs from file."""
    with Path(file_path).open(mode="r") as file:
        content = file.read()

    # Regular expression to find all URLs that end with image file extensions
    return re.findall(r"(https?://[^\s]+\.jpg|png|jpeg|gif)", content)


def scrape_image_names(file_path: Path) -> list:
    """Scrape filenames from blacklist file."""
    with Path(file_path).open(mode="r") as file:
        content = file.read()

    # Regular expression to find all filenames that end with image file extensions
    return re.findall(r"([^\s]+\.jpg|png|jpeg|gif)", content)


def sort_images(
    source_folder: str,
    target_folder: str,
    imagelist: set,
    movelist: set,
) -> None:
    """Move downloaded files to appropriate folders."""
    if not Path(source_folder).exists():
        Path(source_folder).mkdir(parents=True)
    if not Path(target_folder).exists():
        Path(target_folder).mkdir(parents=True)

    for file in Path(source_folder).iterdir():
        if Path(file).is_file():
            if PurePath(file).name not in imagelist:
                file.unlink()
                print(f"🛑 Removed {file}")
            elif PurePath(file).name in movelist:
                time.sleep(0.01)
                file.rename(Path(target_folder) / PurePath(file).name)
                print(f"🔄 Moved {file} to {target_folder}")


# allow import of functions from other files
if __name__ == "__main__":
    # Scrape image URLs from the README file
    image_urls = set(scrape_image_urls(Path(wallpaperlist_filename)))
    image_files = {url.split("OHR.")[1] for url in image_urls}
    blacklisted_files = set(scrape_image_names(Path(blacklist_filename)))

    # Blacklist cleanup
    blacklist_content = (
        "#put names of blacklisted files here\n#each one on a new line\n\n\n"
    )
    for filename in sorted(blacklisted_files):
        if filename in image_files:
            blacklist_content += f"{filename}\n"

    with Path(blacklist_filename).open(mode="w") as blacklist_file:
        blacklist_file.write(blacklist_content)

    # Sort downloaded files
    if len(blacklisted_files) > 0:
        whitelisted_files = image_files - blacklisted_files
        sort_images(download_dir, blacklisted_dir, image_files, blacklisted_files)
        sort_images(blacklisted_dir, download_dir, image_files, whitelisted_files)

    # Check for existing files
    existing_files = {
        filepath.name
        for filepath in set(Path(download_dir).glob("*.jpg"))
        | set(Path(blacklisted_dir).glob("*.jpg"))
    }
    new_image_urls = {
        url for url in image_urls if url.split("OHR.")[1] not in existing_files
    }
    print(
        f"🖼️  {'Total:':<7} {len(image_urls):>10}\n🖼️  {'New:':<7} {len(new_image_urls):>10}"
    )

    # Download each image
    need_cleanup = False
    for i, url in enumerate(new_image_urls):
        file_name = url.split("OHR.")[1]
        folder_name = (
            download_dir if file_name not in blacklisted_files else blacklisted_dir
        )
        file_path = Path(folder_name) / Path(file_name)
        prefix = f"[{i + 1}/{len(new_image_urls)}]:"
        if need_cleanup:
            print("\033[2K", end="")
        need_cleanup = download_image(
            prefix,
            url,
            file_path,
        )
    if need_cleanup:
        print("\033[2K", end="")
    print("😃  Done!")
