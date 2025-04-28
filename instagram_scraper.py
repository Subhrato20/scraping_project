import time
import re
import os
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class InstagramScraper:
    def __init__(self, headless=False):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")

        if not self.username or not self.password:
            raise ValueError("❌ Username or Password environment variables are missing!")

        self.login()

    def login(self):
        driver = self.driver
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        username_input = driver.find_element(By.NAME, "username")
        username_input.send_keys(self.username)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(self.password)

        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()

        # Wait for page to load
        time.sleep(7)

        # Handle "Save Your Login Info?" popup
        try:
            save_info_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="Not Now"]'))
            )
            save_info_button.click()
            print("ℹ️ Dismissed 'Save Your Login Info' popup")
        except:
            pass  # no popup appeared

        # Handle "Turn on Notifications" popup
        try:
            notif_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="Not Now"]'))
            )
            notif_button.click()
            print("ℹ️ Dismissed 'Turn on Notifications' popup")
        except:
            pass  # no popup appeared

        # Now wait for nav bar
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//nav'))
            )
            print("✅ Logged into Instagram and Home Page loaded.")
        except:
            print("⚠️ Warning: Home page didn't fully load, but continuing...")

    def human_scroll(self, max_scrolls=500):
        driver = self.driver
        last_posts_count = 0
        scrolls = 0

        while scrolls < max_scrolls:
            # Scroll down significantly
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(random.uniform(2.5, 4.0))  # Longer wait to load posts

            posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
            current_posts_count = len(posts)

            if current_posts_count == last_posts_count:
                print("🔚 No more new posts loaded.")
                break

            last_posts_count = current_posts_count
            scrolls += 1

        print(f"✅ Finished scrolling. Total posts found: {last_posts_count}")



    def extract_hashtags(self, text):
        return re.findall(r"#(\w+)", text) if text else []

    def scrape_profile(self, profile_username, max_scrolls):
        driver = self.driver
        profile_url = f"https://www.instagram.com/{profile_username}/"
        driver.get(profile_url)
        time.sleep(3)

        self.human_scroll(max_scrolls)

        posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
        post_urls = list({p.get_attribute("href") for p in posts})

        print(f"🔎 Found {len(post_urls)} posts to scrape.")

        results = []

        for post_url in post_urls:
            driver.get(post_url)
            time.sleep(3)

            caption, hashtags, date, num_comments, photos, videos, likes, location = "", [], "", 0, [], [], None, None

            try:
                caption_el = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//ul//span'))
                )
                caption = caption_el.text
                hashtags = self.extract_hashtags(caption)
            except:
                pass

            try:
                date = driver.find_element(By.XPATH, '//time').get_attribute("datetime")
            except:
                pass

            try:
                comments = driver.find_elements(By.XPATH, '//ul/ul')
                num_comments = len(comments)
            except:
                pass

            try:
                images = driver.find_elements(By.XPATH, '//article//img')
                photos = list({img.get_attribute("src") for img in images})
            except:
                pass

            try:
                video_elements = driver.find_elements(By.XPATH, '//article//video')
                videos = [v.get_attribute("src") for v in video_elements]
            except:
                pass

            try:
                likes_el = driver.find_element(By.XPATH, '//section/div/span/span')
                likes = likes_el.text
            except:
                likes = None

            try:
                location_el = driver.find_element(By.XPATH, '//div[contains(@class, "x1vjfegm")]/div/a')
                location = location_el.text
            except:
                location = None

            results.append({
                "url": post_url,
                "user_posted": profile_username,
                "description": caption,
                "hashtags": hashtags,
                "num_comments": num_comments,
                "date_posted": date,
                "likes": likes,
                "photos": photos,
                "videos": videos,
                "location": location
            })

        return results

    def save_to_csv(self, data, filename="instagram_posts.csv"):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"✅ Data saved to {filename}")

    def close(self):
        self.driver.quit()
        print("✅ Closed browser session")

# ---------- MAIN ----------

if __name__ == "__main__":
    profile_to_scrape = "doverstreetmarketnewyork"

    scraper = InstagramScraper(headless=False)
    posts_data = scraper.scrape_profile(profile_to_scrape, max_scrolls=300)
    scraper.save_to_csv(posts_data, filename="instagram_posts.csv")
    scraper.close()
