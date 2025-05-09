# Universal News Scraper

A modular, configurable news scraper with individual configuration modules for each news site. This approach makes it extremely easy to add new sites, update existing ones, and maintain site-specific customizations.

## New Modular Architecture

Each news site now has its own dedicated configuration module, making the system more maintainable and organized:

```
news-scraper/
├── universal_news_scraper.py      # Core scraper class
├── news_scraper_main.py           # Main CLI script
├── site_configs/                  # Site configuration modules
│   ├── __init__.py               # Auto-loads all configurations
│   ├── config_manager.py         # Configuration management utilities
│   ├── bbc_config.py             # BBC News configuration
│   └── [site]_config.py          # Additional site configs
├── requirements.txt              # Dependencies
├── .gitignore                   # Git ignore rules
└── output/                      # Generated output directory
```

## Features

- **Modular Site Configurations**: Each site has its own module with selectors and custom processors
- **Automatic Configuration Loading**: New sites are automatically discovered when added
- **Site-Specific Customizations**: Custom date parsers and post-processors for each site
- **Configuration Manager**: Tools for creating, validating, and managing site configurations
- **Multiple Output Formats**: Save results as JSON, CSV, or both
- **Robust Error Handling**: Gracefully handles errors with individual sites
- **Duplicate Removal**: Automatically removes duplicate articles based on URL
- **Command Line Interface**: Easy-to-use CLI with multiple options

## Installation

1. Clone or download the project files
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Scrape BBC News (default)
python news_scraper_main.py

# Scrape multiple sites
python news_scraper_main.py --sites bbc cnn reuters

# Scrape all configured sites
python news_scraper_main.py --all

# List available sites
python news_scraper_main.py --list
```

### Advanced Options

```bash
# Validate all configurations
python news_scraper_main.py --validate

# Create a new site configuration
python news_scraper_main.py --create-config theguardian "The Guardian" "https://www.theguardian.com"

# Save as JSON only
python news_scraper_main.py --sites bbc --output json

# Combine results from multiple sites
python news_scraper_main.py --all --combine

# Limit articles per site
python news_scraper_main.py --sites cnn --max-articles 10

# Enable verbose output
python news_scraper_main.py --sites reuters --verbose
```

## Adding New Sites

### Option 1: Using the Command Line

```bash
python news_scraper_main.py --create-config nytimes "The New York Times" "https://www.nytimes.com"
```

This creates a template that you can then customize with the actual selectors.

### Option 2: Manual Creation

Create a new file in the `site_configs` directory (e.g., `nytimes_config.py`):

```python
#!/usr/bin/env python3
# The New York Times configuration

SITE_CONFIG = {
    'name': 'The New York Times',
    'url': 'https://www.nytimes.com',
    'article_container': '.story-wrapper',
    'selectors': {
        'title': 'h2.headline',
        'link': 'a.story-link',
        'summary': 'p.summary',
        'date': 'time.published',
        'category': '.section-name',
        'author': '.byline',
        'image': 'img'
    },
    'remove_duplicates': True,
    'timeout': 20
}

# Optional: Custom date parser
def parse_nytimes_date(date_str):
    # Your custom parsing logic
    return date_str

# Optional: Custom post-processor
def process_nytimes_article(article, container):
    # Your custom processing logic
    return article

# Add custom processors if defined
SITE_CONFIG['date_parser'] = parse_nytimes_date
SITE_CONFIG['post_process'] = process_nytimes_article
```

## Updating Existing Sites

When a website changes its HTML structure, simply edit the corresponding config file in `site_configs/`:

```python
# site_configs/bbc_config.py
SITE_CONFIG = {
    'name': 'BBC News',
    'url': 'https://www.bbc.com/news',
    'article_container': 'div[data-testid="new-card-style"]',  # Updated
    'selectors': {
        'title': 'h2[data-testid="new-headline"]',           # Updated
        # ... other selectors
    }
}
```

## Configuration Structure

Each site configuration includes:

- **Basic Information**: Name, URL, timeout settings
- **Selectors**: CSS selectors for extracting data
- **Custom Processors**: Optional date parsers and post-processors
- **Alternative Selectors**: Fallback options when sites change

### Selector Types

```python
# Simple selector
'title': 'h2.headline'

# Multiple fallback selectors
'title': ['h2.headline', 'h3.title', '.article-title']

# Special selector for links
'link': 'same_as_title'  # When link contains the title element
```

## Site-Specific Features

### BBC Configuration
- Custom relative date parsing ("2 hrs ago", "yesterday")
- Live coverage detection
- Video/audio content indicators
- BBC-specific metadata extraction

### CNN Configuration
- Breaking news detection
- Video content identification
- CNN correspondent recognition
- Topic tag extraction

### Reuters Configuration
- Market data extraction
- Stock symbol identification
- Exclusive content marking
- Bureau information parsing

## Configuration Manager

The included configuration manager provides:

```python
from site_configs.config_manager import config_manager

# List all sites
sites = config_manager.list_sites()

# Get a specific configuration
config = config_manager.get_config('bbc')

# Validate a configuration
is_valid, message = config_manager.validate_config('bbc')

# Create a new configuration template
config_manager.create_new_config_template('guardian', 'The Guardian', 'https://www.theguardian.com')

# Save configurations to JSON
config_manager.save_all_configs_to_json('all_configs.json')
```

## Output Files

All output files are saved in the `output` directory:

- Individual site files: `{sitename}_news_{timestamp}.json/csv`
- Combined results: `combined_news.json/csv`
- Debug HTML files: `{sitename}_debug.html`

## Troubleshooting

### Site Not Working?

1. Check the debug HTML file in the output directory
2. Use the validation command: `python news_scraper_main.py --validate`
3. Inspect the website using browser developer tools
4. Update selectors in the site's config file
5. Add a custom date parser if needed

### Common Issues

- **No articles found**: Update the `article_container` selector
- **Missing data**: Check individual selectors for each field
- **Rate limiting**: Use the `--verbose` flag to see timing information

## Contributing New Configurations

To contribute a new site configuration:

1. Create a new `{site}_config.py` file in `site_configs/`
2. Follow the existing pattern with proper selectors
3. Add custom processors if needed
4. Test thoroughly and ensure it passes validation

## License

This project is provided as-is for educational purposes. Please respect websites' terms of service and robots.txt files when scraping.