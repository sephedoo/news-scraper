#!/usr/bin/env python3
# Reuters configuration

import datetime
import re

# Main Reuters configuration
SITE_CONFIG = {
    'name': 'Reuters',
    'url': 'https://www.reuters.com/technology/',
    'article_container': 'li.story-collection__list-item__j4SQe',
    'selectors': {
        'title': 'h3[data-testid="Heading"] a.media-story-card__heading__eqhp9',
        'link': 'h3[data-testid="Heading"] a[data-testid="Link"]',
        'summary': 'p[data-testid="Body"].media-story-card__description__2icjO',
        'date': 'time[datetime]',
        'category': 'span[data-testid="Label"] a',
        'author': '.byline',  # Add if available
        'image': '.media-story-card__image-container__gQPAN img'
    },
    'remove_duplicates': True,
    'timeout': 20
}

# Custom date parser for Reuters
def parse_reuters_date(date_str):
    """Parse Reuters' specific date format"""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    now = datetime.datetime.now()
    
    # Handle ISO format with timezone (Reuters current format)
    # Example: "2025-05-09T09:21:23Z"
    if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', date_str):
        try:
            # Remove 'Z' at the end and parse
            clean_date = date_str.rstrip('Z')
            dt = datetime.datetime.strptime(clean_date, '%Y-%m-%dT%H:%M:%S')
            return dt.isoformat()
        except:
            pass
    
    # Handle ISO format with timezone offset
    if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}', date_str):
        try:
            # Clean up timezone info
            clean_date = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)
            dt = datetime.datetime.strptime(clean_date, '%Y-%m-%dT%H:%M:%S')
            return dt.isoformat()
        except:
            pass
    
    # Time ago format
    if re.match(r'(\d+)\s*(minute|hour|day)s?\s*ago', date_str, re.IGNORECASE):
        match = re.match(r'(\d+)\s*(minute|hour|day)s?\s*ago', date_str, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower()
            
            if 'minute' in unit:
                return (now - datetime.timedelta(minutes=value)).isoformat()
            elif 'hour' in unit:
                return (now - datetime.timedelta(hours=value)).isoformat()
            elif 'day' in unit:
                return (now - datetime.timedelta(days=value)).isoformat()
    
    # Time with timezone format (e.g., "5:21 AM EDT")
    time_pattern = r'(?:May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\s+·\s+(\d{1,2}:\d{2}\s+(?:AM|PM)\s+\w+)'
    match = re.search(time_pattern, date_str)
    if match:
        # This is more complex - we'd need to parse the timezone and date
        # For now, return the current date with extracted time info
        return now.isoformat()
    
    # Month day, year format with time
    # Example: "May 9, 2025 · 5:21 AM EDT"
    pattern = r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\s+·\s+(\d{1,2}:\d{2})\s+(AM|PM)\s+(\w+)'
    match = re.match(pattern, date_str)
    if match:
        try:
            month_name = match.group(1)
            day = int(match.group(2))
            year = int(match.group(3))
            time_str = match.group(4)
            am_pm = match.group(5)
            timezone = match.group(6)
            
            # Convert month name to number
            month_map = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12,
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            month = month_map.get(month_name.lower())
            if month:
                # Create datetime object (ignoring timezone for now)
                dt_str = f"{year}-{month:02d}-{day:02d} {time_str} {am_pm}"
                dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %I:%M %p')
                return dt.isoformat()
        except:
            pass
    
    # Return as-is if we can't parse it
    return date_str

# Custom post-processor for Reuters articles
def process_reuters_article(article, container):
    """Add Reuters-specific post-processing"""
    
    # Extract the test ID from container
    test_id = container.get('id')
    if test_id:
        article['reuters_id'] = test_id
    
    # Extract data attributes
    data_testid = container.get('data-testid')
    if data_testid:
        article['data_testid'] = data_testid
    
    # Check for exclusive content
    title_text = article.get('title', '').lower()
    if 'exclusive:' in title_text or 'exclusive ' in title_text:
        article['is_exclusive'] = True
    
    # Extract video indicator
    video_indicator = container.select_one('[data-testid="Media"] svg')
    if video_indicator:
        article['has_video'] = True
        # Try to get video metadata if available
        svg_parent = video_indicator.parent
        if svg_parent and 'video' in str(svg_parent.get('class', [])).lower():
            article['media_type'] = 'video'
    
    # Extract full image information
    image_elem = container.select_one('img')
    if image_elem:
        # Get responsive image sources
        srcset = image_elem.get('srcset')
        if srcset:
            article['image_srcset'] = srcset
        
        # Get image dimensions
        width = image_elem.get('width')
        height = image_elem.get('height')
        if width and height:
            article['image_dimensions'] = {
                'width': int(width),
                'height': int(height)
            }
        
        # Get image alt text
        alt_text = image_elem.get('alt')
        if alt_text:
            article['image_alt'] = alt_text
    
    # Extract more detailed date information
    date_span = container.select_one('span[data-testid="Label"]')
    if date_span:
        full_date_text = date_span.get_text()
        if ' · ' in full_date_text:
            parts = full_date_text.split(' · ')
            if len(parts) >= 2:
                article['category_path'] = parts[0].strip()
                article['full_date_text'] = parts[1].strip()
    
    # Extract aria-label for additional context
    link_elem = container.select_one('a[aria-label]')
    if link_elem:
        aria_label = link_elem.get('aria-label', '')
        if aria_label:
            article['aria_label'] = aria_label
    
    # Check for breaking news indicators
    if any(indicator in str(container).lower() for indicator in ['breaking', 'flash', 'urgent']):
        article['is_breaking'] = True
    
    # Extract section/category from URL
    if article.get('link'):
        url_parts = article['link'].split('/')
        if len(url_parts) > 3:
            article['url_section'] = url_parts[3]
    
    # Extract company/stock references
    # Look for company names or stock symbols in title
    stock_pattern = r'\b[A-Z]{1,5}\b'
    title_summary = f"{article.get('title', '')} {article.get('summary', '')}"
    potential_stocks = re.findall(stock_pattern, title_summary)
    if potential_stocks:
        # Filter out common words that aren't stocks
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'WERE', 'HER', 'SHE', 'HIM', 'HIS', 'HAS', 'HAD', 'CAN', 'WAS'}
        stocks = [s for s in potential_stocks if s not in common_words and len(s) >= 2]
        if stocks:
            article['mentioned_companies'] = stocks
    
    return article

# Add custom processors to the config
SITE_CONFIG['date_parser'] = parse_reuters_date
SITE_CONFIG['post_process'] = process_reuters_article

# Alternative selectors for Reuters (in case main ones change)
ALTERNATIVE_SELECTORS = {
    'article_container': [
        'li.story-collection__list-item__j4SQe',
        '.story-card',
        '[data-testid="MediaStoryCard"]',
        '.media-story-card',
        '.story-collection__list-item'
    ],
    'title': [
        'h3[data-testid="Heading"] a',
        '.media-story-card__heading__eqhp9',
        '.story-card-heading__heading',
        '.article-heading',
        'h3 a'
    ],
    'link': [
        'h3[data-testid="Heading"] a[data-testid="Link"]',
        '.media-story-card__heading__eqhp9',
        'a[href^="/"]'
    ],
    'summary': [
        'p[data-testid="Body"].media-story-card__description__2icjO',
        '.media-story-card__description',
        '.story-card-description',
        'p.description'
    ],
    'date': [
        'time[datetime]',
        'span[data-testid="Label"] time',
        '.story-card-timestamp',
        'time'
    ]
}

# Reuters-specific utility functions
def get_reuters_section_url(section):
    """Generate Reuters section URLs"""
    base_url = "https://www.reuters.com"
    
    section_paths = {
        'world': '/world',
        'business': '/business',
        'markets': '/markets',
        'technology': '/technology',
        'politics': '/politics',
        'lifestyle': '/lifestyle',
        'sports': '/sports/soccer',
        'science': '/science',
        'health': '/lifestyle/health',
        'environment': '/world/environment',
        'legal': '/legal',
        'breakingviews': '/breakingviews',
        'graphics': '/graphics',
        'pictures': '/pictures',
        'live-events': '/live-news'
    }
    
    return base_url + section_paths.get(section.lower(), '')

def extract_market_symbols(article):
    """Extract stock symbols and market data from Reuters article"""
    symbols = []
    market_data = []
    
    # Look for stock symbols in title and summary
    text = f"{article.get('title', '')} {article.get('summary', '')}"
    
    # Pattern for stock symbols with common exchanges
    exchange_patterns = [
        r'\((NYSE|NASDAQ|LSE|TSE):[A-Z]+\)',
        r'\b([A-Z]{2,5})\.(N|O|L|T)\b'
    ]
    
    for pattern in exchange_patterns:
        symbols.extend(re.findall(pattern, text))
    
    # Look for price movements
    price_patterns = [
        r'\$\d+(?:\.\d{2})?',
        r'up \d+(?:\.\d+)?%',
        r'down \d+(?:\.\d+)?%',
        r'rose \d+(?:\.\d+)?%',
        r'fell \d+(?:\.\d+)?%'
    ]
    
    for pattern in price_patterns:
        market_data.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return {
        'symbols': list(set(symbols)),
        'market_data': list(set(market_data))
    }

def is_breaking_reuters(article):
    """Check if a Reuters article is breaking news"""
    breaking_indicators = [
        'breaking',
        'urgent',
        'developing',
        'flash',
        'alert'
    ]
    
    title = article.get('title', '').lower()
    summary = article.get('summary', '').lower()
    
    # Check title
    for indicator in breaking_indicators:
        if indicator in title:
            return True
    
    # Check summary
    for indicator in breaking_indicators:
        if indicator in summary:
            return True
    
    # Check if marked as breaking in metadata
    return article.get('is_breaking', False)

def categorize_reuters_article(article):
    """Categorize Reuters articles based on content"""
    title_summary = f"{article.get('title', '')} {article.get('summary', '')}".lower()
    
    categories = []
    
    # Market/Finance
    if any(word in title_summary for word in ['stock', 'market', 'trading', 'investor', 'earnings', 'wall street', 'shares']):
        categories.append('Markets & Finance')
    
    # Technology
    if any(word in title_summary for word in ['tech', 'startup', 'ai', 'crypto', 'bitcoin', 'apple', 'google', 'microsoft']):
        categories.append('Technology')
    
    # International News
    if any(word in title_summary for word in ['china', 'russia', 'europe', 'asia', 'middle east', 'diplomatic']):
        categories.append('International')
    
    # Business
    if any(word in title_summary for word in ['merger', 'acquisition', 'ceo', 'earnings', 'revenue', 'profit']):
        categories.append('Business')
    
    # Politics
    if any(word in title_summary for word in ['president', 'congress', 'senate', 'election', 'government', 'policy']):
        categories.append('Politics')
    
    # Legal
    if any(word in title_summary for word in ['court', 'lawsuit', 'judge', 'legal', 'trial', 'settlement']):
        categories.append('Legal')
    
    # Exclusive Content
    if article.get('is_exclusive', False) or 'exclusive' in title_summary:
        categories.append('Exclusive')
    
    return categories

# Reuters market coverage categories
REUTERS_MARKET_CATEGORIES = {
    'equity': 'Equity Markets',
    'bonds': 'Fixed Income',
    'fx': 'Foreign Exchange',
    'commodities': 'Commodities',
    'crypto': 'Cryptocurrency',
    'economic-data': 'Economic Indicators',
    'earnings': 'Corporate Earnings',
    'ipos': 'Initial Public Offerings'
}

# Export the configuration
if __name__ == "__main__":
    # Print configuration summary when run directly
    print(f"Reuters Configuration:")
    print(f"Site: {SITE_CONFIG['name']}")
    print(f"URL: {SITE_CONFIG['url']}")
    print(f"Article containers: {SITE_CONFIG['article_container']}")
    print("\nSelectors:")
    for key, selector in SITE_CONFIG['selectors'].items():
        print(f"  {key}: {selector}")
    
    # Test the date parser
    test_dates = [
        "2025-05-09T09:21:23Z",
        "May 9, 2025 · 5:21 AM EDT"
    ]
    
    print("\nDate parsing tests:")
    for test_date in test_dates:
        parsed = parse_reuters_date(test_date)
        print(f"Input: {test_date}")
        print(f"Output: {parsed}")
        print()