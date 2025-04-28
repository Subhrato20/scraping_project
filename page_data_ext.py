from firecrawl import FirecrawlApp, ScrapeOptions
import csv

app = FirecrawlApp(api_key="fc-7547e649f584437c9b6060a94c06c733")

# Crawl
crawl_status = app.crawl_url(
    'https://www.gentle.systems/',
    limit=1,
    scrape_options=ScrapeOptions(formats=['markdown', 'html']),
    poll_interval=30
)

# Extract Firecrawl documents
documents = crawl_status.data

# Open a CSV to write
with open('gentle_systems_data.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['url', 'title', 'description', 'markdown', 'html']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for doc in documents:
        writer.writerow({
            'url': doc.metadata.get('url') if doc.metadata else '',
            'title': doc.metadata.get('title') if doc.metadata else '',
            'description': doc.metadata.get('description') if doc.metadata else '',
            'markdown': doc.markdown if doc.markdown else '',
            'html': doc.html if doc.html else ''
        })

print("✅ Data saved to gentle_systems_data.csv")
