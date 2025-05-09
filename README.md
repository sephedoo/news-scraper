# Universal News Scraper

A modular, configurable news scraper that allows you to easily inject selectors for different news websites. This approach makes it simple to add new sites or update existing ones when websites change their structure.

## Features

- **Configurable Selectors**: Add or update selectors without changing the core scraper code
- **Multiple Output Formats**: Save results as JSON, CSV, or both
- **Site-Specific Processors**: Add custom date parsers and post-processing for specific sites
- **Robust Error Handling**: Gracefully handles errors with individual sites
- **Duplicate Removal**: Automatically removes duplicate articles based on URL
- **Command Line Interface**: Easy-to-use CLI with multiple options

## Installation

1. Clone or download the project files
2. Install required dependencies:

```bash
pip install -r requirements.txt
