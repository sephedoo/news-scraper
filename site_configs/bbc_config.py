#!/usr/bin/env python3
# BBC News configuration

import datetime

# Main BBC configuration
SITE_CONFIG = {
    'name': 'BBC News',
    'url': 'https://www.bbc.com/innovation',
    'article_container': 'div[data-testid="dundee-card"]',
    'selectors': {
        'title': 'h2[data-testid="card-headline"]',
        'link': 'a[data-testid="internal-link"]',
        'summary': 'p[data-testid="card-description"]',
        'date': 'span[data-testid="card-metadata-lastupdated"]',
        'category': 'span[data-testid="card-metadata-tag"]',
        'author': '.byline',
        'image': 'img'
    },
    'remove_duplicates': True,
    'timeout': 20
}

# Custom date parser for BBC
def parse_bbc_date(date_str):
    """Parse BBC's specific date format"""
    if not date_str:
        return None
    
    date_str = date_str.lower().strip()
    now = datetime.datetime.now()
    
    if 'hrs ago' in date_str or 'hr ago' in date_str:
        # Extract hours
        try:
            hours = int(date_str.split()[0])
            return (now - datetime.timedelta(hours=hours)).isoformat()
        except:
            pass
    elif 'mins ago' in date_str or 'min ago' in date_str:
        # Extract minutes
        try:
            minutes = int(date_str.split()[0])
            return (now - datetime.timedelta(minutes=minutes)).isoformat()
        except:
            pass
    elif 'days ago' in date_str or 'day ago' in date_str:
        # Extract days
        try:
            days = int(date_str.split()[0])
            return (now - datetime.timedelta(days=days)).isoformat()
        except:
            pass
    elif 'yesterday' in date_str:
        return (now - datetime.timedelta(days=1)).isoformat()
    elif 'today' in date_str:
        return now.isoformat()
    
    # Return as-is if we can't parse it
    return date_str

# Custom post-processor for BBC articles
def process_bbc_article(article, container):
    """Add BBC-specific post-processing"""
    
    # Check for live coverage indicator
    live_tag = container.select_one('.live-tag, [data-testid="live-tag"]')
    if live_tag:
        article['is_live'] = True
        article['live_text'] = live_tag.get_text().strip()
    
    # Check for video indicator
    video_indicator = container.select_one('.video-icon, [data-testid="video-icon"]')
    if video_indicator:
        article['has_video'] = True
    
    # Check for audio indicator
    audio_indicator = container.select_one('.audio-icon, [data-testid="audio-icon"]')
    if audio_indicator:
        article['has_audio'] = True
    
    # Extract additional metadata
    metadata_container = container.select_one('[data-testid="card-metadata"]')
    if metadata_container:
        # Get all metadata tags
        tags = metadata_container.select('span')
        article['metadata_tags'] = [tag.get_text().strip() for tag in tags]
    
    # Get image caption if available
    image_caption = container.select_one('figcaption, .image-caption')
    if image_caption:
        article['image_caption'] = image_caption.get_text().strip()
    
    return article

# Add custom processors to the config
SITE_CONFIG['date_parser'] = parse_bbc_date
SITE_CONFIG['post_process'] = process_bbc_article

# Alternative selectors for BBC (in case the main ones change)
ALTERNATIVE_SELECTORS = {
    'article_container': [
        'div[data-testid="dundee-card"]',
        '.gs-c-promo',
        '.nw-c-promo',
        '.media-list__item'
    ],
    'title': [
        'h2[data-testid="card-headline"]',
        '.gs-c-promo-heading__title',
        '.nw-o-link-split__text',
        'h3'
    ],
    'link': [
        'a[data-testid="internal-link"]',
        'a.gs-c-promo-heading',
        'a.nw-o-link-split__anchor'
    ],
    'summary': [
        'p[data-testid="card-description"]',
        '.gs-c-promo-summary',
        '.nw-c-promo-summary'
    ],
    'date': [
        'span[data-testid="card-metadata-lastupdated"]',
        'time',
        '.gs-c-promo-date',
        '.date'
    ]
}

# BBC-specific utility functions
def is_breaking_news(article):
    """Check if an article is marked as breaking news"""
    title = article.get('title', '').lower()
    category = article.get('category', '').lower()
    
    breaking_indicators = ['breaking', 'urgent', 'alert', 'live']
    
    for indicator in breaking_indicators:
        if indicator in title or indicator in category:
            return True
    
    return article.get('is_live', False)

def get_bbc_section_url(section):
    """Generate BBC section URLs"""
    base_url = "https://www.bbc.com"
    
    section_paths = {
        'world': '/news/world',
        'uk': '/news/uk',
        'business': '/news/business',
        'politics': '/news/politics',
        'tech': '/news/technology',
        'science': '/news/science-environment',
        'health': '/news/health',
        'education': '/news/education',
        'entertainment': '/news/entertainment-arts',
        'sport': '/sport'
    }
    
    return base_url + section_paths.get(section.lower(), '/news')

# Export the configuration
if __name__ == "__main__":
    # Print configuration summary when run directly
    print(f"BBC News Configuration:")
    print(f"Site: {SITE_CONFIG['name']}")
    print(f"URL: {SITE_CONFIG['url']}")
    print(f"Article container: {SITE_CONFIG['article_container']}")
    print("\nSelectors:")
    for key, selector in SITE_CONFIG['selectors'].items():
        print(f"  {key}: {selector}")