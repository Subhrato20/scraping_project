import os
import csv
import requests
from urllib.parse import urljoin
from PIL import Image
import ffmpeg
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --------- Helper Functions ---------

def get_image_metadata(filepath):
    try:
        with Image.open(filepath) as img:
            return {
                "format": img.format,
                "width": img.width,
                "height": img.height,
                "mode": img.mode
            }
    except Exception as e:
        print(f"Error extracting image metadata: {e}")
        return {}

def get_video_metadata(filepath):
    try:
        probe = ffmpeg.probe(filepath)
        video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        return {
            'width': video_info.get('width'),
            'height': video_info.get('height'),
            'duration': float(video_info.get('duration', 0)),
            'codec': video_info.get('codec_name')
        }
    except Exception as e:
        print(f"Error extracting video metadata: {e}")
        return {}

# --------- Scraping Part ---------

# Target URL
url = 'https://www.gentle.systems/'

# Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

# Create download folder
os.makedirs('downloaded', exist_ok=True)

# Setup headless Chrome with Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# Load page and get HTML after JavaScript execution
driver.get(url)
html = driver.page_source
driver.quit()

# Parse the fully loaded HTML
soup = BeautifulSoup(html, 'html.parser')

# Collect all media URLs
media_urls = []

# Images and gifs
for img_tag in soup.find_all('img'):
    src = img_tag.get('src')
    if src:
        full_url = urljoin(url, src)
        media_urls.append(('image', full_url, img_tag.attrs))

# Videos
for video_tag in soup.find_all('video'):
    src = video_tag.get('src')
    if src:
        full_url = urljoin(url, src)
        media_urls.append(('video', full_url, video_tag.attrs))
    for source_tag in video_tag.find_all('source'):
        src = source_tag.get('src')
        if src:
            full_url = urljoin(url, src)
            media_urls.append(('video', full_url, source_tag.attrs))

# Prepare CSV file
csv_filename = 'media_metadata.csv'
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['filename', 'type', 'url', 'format/codec', 'width', 'height', 'duration', 'mode']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Download and process each media file
    counter = 1
    for media_type, media_url, metadata in media_urls:
        try:
            # Get a clean filename
            filename = os.path.basename(media_url.split('?')[0])

            # If no filename or no extension, generate unique name
            if not filename or '.' not in filename:
                if media_type == 'image':
                    extension = '.jpg'
                elif media_type == 'video':
                    extension = '.mp4'
                else:
                    extension = ''
                filename = f"{media_type}_{counter}{extension}"

            filepath = os.path.join('downloaded', filename)

            # Download the media
            r = requests.get(media_url, headers=headers, stream=True, timeout=10)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded {filename} ({media_type})")

                # Extract and write metadata
                if media_type == 'image':
                    meta = get_image_metadata(filepath)
                    writer.writerow({
                        'filename': filename,
                        'type': 'image',
                        'url': media_url,
                        'format/codec': meta.get('format'),
                        'width': meta.get('width'),
                        'height': meta.get('height'),
                        'duration': '',
                        'mode': meta.get('mode')
                    })
                elif media_type == 'video':
                    meta = get_video_metadata(filepath)
                    writer.writerow({
                        'filename': filename,
                        'type': 'video',
                        'url': media_url,
                        'format/codec': meta.get('codec'),
                        'width': meta.get('width'),
                        'height': meta.get('height'),
                        'duration': meta.get('duration'),
                        'mode': ''
                    })

                counter += 1
            else:
                print(f"Failed to download {media_url}")
        except Exception as e:
            print(f"Error downloading {media_url}: {e}")
