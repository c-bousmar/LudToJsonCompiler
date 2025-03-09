import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import time
from tqdm import tqdm


BASE_URL = "https://ludii.games/library.php"
DOWNLOAD_DIR = "data/raw"


os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_game_links():
    """Scrape the Ludii library page and get all game detail links."""
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("Failed to fetch the main page")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    game_links = []

    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if href.startswith("details.php?keyword="):             # Filter only valid game pages
            full_url = urljoin(BASE_URL, href)
            game_links.append(full_url)
    
    return game_links

import urllib.parse

def find_matching_urls(url_list, target_name):
    """
    Finds URLs where the keyword at the end matches the given target_name.
    
    Parameters:
    - url_list (list of str): List of URLs.
    - target_name (str): The name to match against the URL keyword.

    Returns:
    - list: Matched URLs.
    """
    normalized_target = target_name.strip().lower()
    # .replace(" ", "%20")  # Encode spaces as %20
    
    matching_urls = [
        url for url in url_list 
        if urllib.parse.unquote(url.split("=")[-1]).strip().lower() == target_name.strip().lower()
    ]
    return matching_urls


def download_lud_file(game_url):
    """Download the .lud file from a game details page."""
    response = requests.get(game_url)
    if response.status_code != 200:
        return False
    
    soup = BeautifulSoup(response.text, 'html.parser')
    download_link = soup.find("a", href=lambda href: href and href.startswith("lud/games/") and href.endswith(".lud"))
    
    if download_link:
        lud_url = urljoin(game_url, download_link.get("href"))
        game_name = unquote(game_url.split("=")[-1])
        filename = os.path.join(DOWNLOAD_DIR, f"{game_name}.lud")
        
        lud_response = requests.get(lud_url)
        if lud_response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(lud_response.content)
            return True
    return False

def main(file="all"):
    print("Fetching game links...")
    game_links = get_game_links()
    total_games = len(game_links)
    if total_games == 0:
        print("No games found.")
        return
    print(f"Found {total_games} game links.")
    
    failed_downloads = []
    if file == "all":
        with tqdm(total=total_games, desc="Downloading .lud files", unit="game") as pbar:
            for game_url in game_links:
                success = download_lud_file(game_url)
                if not success:
                    failed_downloads.append(game_url)
                pbar.update(1)
                time.sleep(0.5)                                       # Avoid overwhelming the server => 30mins total to download all files
    else:
        urls = find_matching_urls(game_links, file)
        if not urls:
            print(f"Game '{file}' not found.")
            return
        print(f"Downloading {file}...")
        for game_url in urls:
            success = download_lud_file(game_url)
            if not success:
                failed_downloads.append(game_url)
            time.sleep(0.5)                                       # Avoid overwhelming the server => 30mins total to download all files

    if failed_downloads:
            print("Failed to download the following games:")
            for url in failed_downloads:
                print(url)
    print("All downloads completed.")

if __name__ == "__main__":
    main()
