import json
import requests
import os
import csv

# Load the JSON file
with open('bd_20250428_122852_0.json', 'r') as f:
    data = json.load(f)

# Create a folder to save images
os.makedirs('downloaded_images', exist_ok=True)

# Prepare metadata for CSV
metadata_records = []

# Loop through each post and download the images
for post in data:
    photos = post.get('photos', [])
    for idx, photo_url in enumerate(photos):
        try:
            response = requests.get(photo_url)
            if response.status_code == 200:
                # Create a filename based on content_id and index
                filename = f"{post['content_id']}_{idx}.jpg"
                filepath = os.path.join('downloaded_images', filename)
                with open(filepath, 'wb') as f_img:
                    f_img.write(response.content)
                print(f"Downloaded {filename}")

                # Collect metadata
                metadata_records.append({
                    'filename': filename,
                    'content_id': post.get('content_id', ''),
                    'user_posted': post.get('user_posted', ''),
                    'description': post.get('description', ''),
                    'date_posted': post.get('date_posted', ''),
                    'likes': post.get('likes', 0),
                    'num_comments': post.get('num_comments', 0),
                    'post_url': post.get('url', '')
                })
            else:
                print(f"Failed to download {photo_url}")
        except Exception as e:
            print(f"Error downloading {photo_url}: {e}")

# Save metadata to a CSV file
csv_filename = 'image_metadata.csv'
csv_fields = ['filename', 'content_id', 'user_posted', 'description', 'date_posted', 'likes', 'num_comments', 'post_url']

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
    writer.writeheader()
    writer.writerows(metadata_records)

print("Download complete and metadata CSV created!")
