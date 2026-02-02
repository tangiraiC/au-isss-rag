import requests
from bs4 import BeautifulSoup
import csv
import sys
from urllib.parse import urljoin, urlparse
import time

def get_soup(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_content(soup, url, current_section="General"):
    data = []
    
    main_content = soup.find('main') or soup.find('div', id='main-content') or soup.body
    
    if not main_content:
        return data

    # Iterate through elements to group by header
    for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'div']):
        if element.name in ['h1', 'h2', 'h3']:
            current_section = element.get_text(strip=True)
        elif element.name in ['p', 'ul', 'ol', 'div']:
             # Extract text and links
            text = element.get_text(strip=True)
            if not text:
                continue
            
            # Find links in this element
            links = element.find_all('a')
            for link in links:
                link_text = link.get_text(strip=True)
                href = link.get('href')
                if href and not href.startswith('#') and not href.startswith('javascript'):
                     full_url = urljoin(url, href)
                     
                     data.append({
                         'Source URL': url,
                         'Section': current_section,
                         'Text': text, # Capture full text
                         'Link Text': link_text,
                         'URL': full_url
                     })
            
            # If no links, just add the text as info
            if not links:
                 data.append({
                     'Source URL': url,
                     'Section': current_section,
                     'Text': text,
                     'Link Text': '',
                     'URL': ''
                 })
    return data

def scrape_isss():
    start_url = "https://www.american.edu/student-affairs/isss/"
    
    # Store unique data items
    all_data = []
    seen_urls = set()
    urls_to_visit = {start_url}
    visited_urls = set()

    # Domain to restrict crawling
    base_domain = "www.american.edu"
    base_path = "/student-affairs/isss/"

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        
        if current_url in visited_urls:
            continue
        
        print(f"Scraping: {current_url}")
        soup = get_soup(current_url)
        visited_urls.add(current_url)

        if not soup:
            continue

        # Extract content from current page
        page_data = extract_content(soup, current_url)
        all_data.extend(page_data)

        # Find new internal links to add to queue
        # For this task, we want to scrape "info that is in the scu pages"
        # We will restrict to pages within the ISSS subpath to avoid crawling the whole university site
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Normalize URL
            full_url = urljoin(current_url, href)
            parsed_url = urlparse(full_url)
            
            # Clean fragment
            full_url = full_url.split('#')[0]

            if (parsed_url.netloc == base_domain and 
                parsed_url.path.startswith(base_path) and 
                full_url not in visited_urls and
                full_url not in urls_to_visit and
                not full_url.endswith('.pdf') and # Skip PDFs
                not full_url.endswith('.jpg') and # Skip Images
                '@' not in full_url): # Skip emails
                
                urls_to_visit.add(full_url)
        
        # Polite delay
        time.sleep(0.5)

    # Deduplicate entries loosely
    unique_data = []
    seen_entries = set()
    for item in all_data:
        # Create a unique key 
        key = (item['Source URL'], item['Section'], item['Text'], item['URL'])
        
        if key not in seen_entries:
            seen_entries.add(key)
            unique_data.append(item)

    # Write to CSV
    filename = 'processed_data/isss_data.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Source URL', 'Section', 'Text', 'Link Text', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in unique_data:
            writer.writerow(row)

    print(f"Successfully scrapped {len(unique_data)} items from {len(visited_urls)} pages to {filename}")

if __name__ == "__main__":
    scrape_isss()
