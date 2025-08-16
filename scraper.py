import requests
from bs4 import BeautifulSoup
import os
import hashlib

# The URL of the page to scrape
URL = "https://www.gov.wales/planning-permission-fences-gates-and-garden-walls"
# File to store the baseline hash of the content
BASELINE_HASH_FILE = "baseline_hash.txt"

def get_page_content_text(url):
    """
    Fetches the content of a URL and extracts the clean text from the body.
    Returns the text content or None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main content area. This is more robust than the whole body.
        # Let's assume the main content is within a <main> tag or a div with role="main"
        main_content = soup.find('main')
        if not main_content:
            # Fallback for sites that don't use <main>
            main_content = soup.find('div', role='main')

        # If we still can't find a main area, we have to fall back to the body
        if not main_content:
            main_content = soup.body

        if not main_content:
            return None

        # Get text and clean it up
        text = main_content.get_text(separator='\n', strip=True)
        return text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def check_regulations():
    """
    Scrapes regulation websites and checks for changes against a baseline hash.
    """
    print(f"Checking for regulation changes at {URL}...")

    content = get_page_content_text(URL)

    if content is None:
        print("Could not retrieve page content. Aborting check.")
        return

    # Create a hash of the current content
    current_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    print(f"Current content hash: {current_hash}")

    # If baseline file doesn't exist, create it with the current hash
    if not os.path.exists(BASELINE_HASH_FILE):
        print("No baseline hash found. Creating one now.")
        with open(BASELINE_HASH_FILE, 'w') as f:
            f.write(current_hash)
        print(f"Baseline hash saved to {BASELINE_HASH_FILE}.")
        return

    # Read the baseline hash
    with open(BASELINE_HASH_FILE, 'r') as f:
        baseline_hash = f.read().strip()
    print(f"Baseline hash:      {baseline_hash}")

    # Compare hashes
    if current_hash == baseline_hash:
        print("SUCCESS: No changes detected in regulations content.")
    else:
        print("\n" + "="*60)
        print("!! ALERT: CHANGES DETECTED IN REGULATIONS CONTENT !!")
        print("="*60 + "\n")
        # Placeholder for sending an email alert
        print("An email alert would be sent to the developer.")
        print("To accept the new changes, delete the old baseline_hash.txt file and run this script again.")


if __name__ == "__main__":
    check_regulations()
