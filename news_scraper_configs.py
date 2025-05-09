#!/usr/bin/env python3
# News Scraper Site Configurations
# This file contains selector configurations for different news websites

import datetime

# You can easily add or update configurations here
# When a website changes its HTML structure, just update the selectors

SITE_CONFIGURATIONS = {
    'bbc': {
        'name': 'BBC News',
        'url': 'https://www.bbc.com/news',
        'article_container': 'div[data-testid="dundee-card"]',
        'selectors': {
            'title': 'h2[data-testid="card-headline"]',
            'link': 'a[data-testid="internal-link"]',
            'summary': 'p[data-testid="card-description"]',
            'date': 'span[data-testid="card-metadata-lastupdated"]',
            'category': 'span[data-testid="card-metadata-tag"]',
            'author': '.byline',  # Add if available
            'image': 'img'
        },
        'remove_duplicates': True,
        'timeout': 20
    },
    
    'cnn': {
        'name': 'CNN',
        'url': 'https://www.cnn.com',
        'article_container': ['.container__item', '.card', '.story-card'],
        'selectors': {
            'title': ['.container__headline', '.card__headline', 'h3', 'h4'],
            'link': 'same_as_title',  # Title is usually inside the link
            'summary': ['.container__text', '.card__text', '.summary', 'p'],
            'date': ['time', '.container__timestamp', '.card__timestamp'],
            'category': ['.container__label', '.card__label', '.section'],
            'author': ['.byline', '.author'],
            'image': 'img'
        },
        'remove_duplicates': True,
        'timeout': 20
    },
    
    'reuters': {
        'name': 'Reuters',
        'url': 'https://www.reuters.com',
        'article_container': ['.story-card', '[data-testid="story-card"]'],
        'selectors': {
            'title': ['.story-card-heading__heading', '.article-heading', 'h3'],
            'link': 'same_as_title',
            'summary': ['.story-card-description', '.article-description', 'p'],
            'date': ['.story-card-timestamp', 'time'],
            'category': ['.story-card-section', '.section'],
            'author': ['.byline', '.author'],
            'image': 'img'
        },
        'remove_duplicates': True,
        'timeout': 20
    },
    
    'nytimes': {
        'name': 'The New York Times',
        'url': 'https://www.nytimes.com',
        'article_container': ['.story-wrapper', '.css-8atqhb'],
        'selectors': {
            'title': ['h2', 'h3', '.headline'],
            'link': 'a',
            'summary': '.summary',
            'date': 'time',
            'category': '.section-name',
            'author': '.byline',
            'image': 'img'
        },
        'remove_duplicates': True,
        'timeout': 20
    },
    
    'guardian': {
        'name': 'The Guardian',
        'url': 'https://www.theguardian.com/international',
        'article_container': '[data-component="Card"]',
        'selectors': {
            'title': '.fc-item__title',
            'link': 'a.fc-item__link',
            'summary': '.fc-item__standfirst',
            'date': 'time',
            'category': '.fc-sublink__title',
            'author': '.fc-item__byline',
            'image': 'img'
        },
        'remove_duplicates': True,
        'timeout': 20
    },
    
    'wsj': {
        'name': 'Wall Street Journal',
        'url': 'https://www.wsj.com',
        'article_container': '.WSJTheme--story-item',
        'selectors': {
            'title': 'h3.WSJTheme--headline',
            'link': 'a',
            'summary': '.WSJTheme--summary',
            'date': 'time',
            'category': '.WSJTheme--category',
            'author': '.author',
            'image': 'img'
        },
        'remove_duplicates': True,
        'timeout': 20
    },
    
    'apnews': {
        'name': 'Associated Press',
        'url': 'https://apnews.com',
        'article_container': '[data-key="card-headline"]',
        'selectors': {
            'title': '.CardHeadline',
            'link': 'a',
            'summary': '.content',
            'date': '.Timestamp',
            'category': '.Tag',
            'author': '.byline',
            'image': 'img'
        },
        'remove_duplicates': True,
        'timeout': 20
    }
}

# Custom date parsers for specific sites (if needed)
def parse_bbc_date(date_str):
    """Parse BBC's date format"""
    if 'hrs ago' in date_str:
        hours = int(date_str.split()[0])
        return (datetime.datetime.now() - datetime.timedelta(hours=hours)).isoformat()
    elif 'min ago' in date_str:
        minutes = int(date_str.split()[0])
        return (datetime.datetime.now() - datetime.timedelta(minutes=minutes)).isoformat()
    return date_str

def parse_cnn_date(date_str):
    """Parse CNN's date format"""
    # Add CNN-specific date parsing if needed
    return date_str

# You can add custom parsers for each site
CUSTOM_DATE_PARSERS = {
    'bbc': parse_bbc_date,
    'cnn': parse_cnn_date,
    # Add more as needed
}

# Custom post-processing functions for specific sites
def process_bbc_article(article, container):
    """Add any BBC-specific post-processing"""
    # Example: Extract additional metadata
    live_tag = container.select_one('.live-tag')
    if live_tag:
        article['is_live'] = True
    return article

def process_cnn_article(article, container):
    """Add any CNN-specific post-processing"""
    # Example: Check if article has video
    video_indicator = container.select_one('.video-icon')
    if video_indicator:
        article['has_video'] = True
    return article

# Custom post-processors for each site
CUSTOM_POST_PROCESSORS = {
    'bbc': process_bbc_article,
    'cnn': process_cnn_article,
    # Add more as needed
}

# Helper function to add custom processors to configs
def get_config_with_processors(site_key):
    """Get configuration with custom processors if available"""
    config = SITE_CONFIGURATIONS.get(site_key, {}).copy()
    
    if site_key in CUSTOM_DATE_PARSERS:
        config['date_parser'] = CUSTOM_DATE_PARSERS[site_key]
    
    if site_key in CUSTOM_POST_PROCESSORS:
        config['post_process'] = CUSTOM_POST_PROCESSORS[site_key]
    
    return config

# Utility function to update configurations from a JSON file
def load_configs_from_json(json_file):
    """Load configurations from a JSON file and merge with existing configs"""
    import json
    try:
        with open(json_file, 'r') as f:
            json_configs = json.load(f)
            SITE_CONFIGURATIONS.update(json_configs)
        print(f"Loaded configurations from {json_file}")
    except Exception as e:
        print(f"Could not load configurations from {json_file}: {str(e)}")

# Save current configurations to JSON for easy editing
def save_configs_to_json(json_file='site_configs.json'):
    """Save current configurations to a JSON file"""
    import json
    try:
        # Remove function references for JSON serialization
        json_configs = {}
        for site, config in SITE_CONFIGURATIONS.items():
            json_config = config.copy()
            # Remove non-serializable items
            json_config.pop('date_parser', None)
            json_config.pop('post_process', None)
            json_configs[site] = json_config
        
        with open(json_file, 'w') as f:
            json.dump(json_configs, f, indent=2)
        print(f"Saved configurations to {json_file}")
    except Exception as e:
        print(f"Could not save configurations to {json_file}: {str(e)}")

# Usage example
if __name__ == "__main__":
    # Save current configs to JSON for easy editing
    save_configs_to_json()
    
    # Example: Print all available configurations
    print("Available news site configurations:")
    for site, config in SITE_CONFIGURATIONS.items():
        print(f"- {site}: {config['name']}")
    
    # Example: Get configuration for BBC with custom processors
    bbc_config = get_config_with_processors('bbc')
    print(f"\nBBC configuration: {bbc_config['name']}")
    print(f"Article container: {bbc_config['article_container']}")