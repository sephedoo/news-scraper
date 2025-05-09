#!/usr/bin/env python3
# Universal News Scraper with Configurable Selectors
# Allows you to inject selectors for different websites

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import datetime
import time
import re
from urllib.parse import urljoin

class UniversalNewsScraper:
    """Universal news scraper that accepts selector configurations for different websites"""
    
    def __init__(self, site_config, verbose=True):
        self.site_config = site_config
        self.verbose = verbose
        self.session = requests.Session()
        
        # Set browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # Create output directory
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def log(self, message):
        """Print log messages if verbose mode is enabled"""
        if self.verbose:
            print(f"[{self.site_config['name']}] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def save_html(self, html):
        """Save raw HTML for debugging"""
        filename = f"{self.site_config['name'].lower().replace(' ', '_')}_debug.html"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        self.log(f"Saved raw HTML to {filepath}")
        return filepath

    def scrape_news(self):
        """Scrape news using the provided selector configuration"""
        self.log(f"Fetching news from: {self.site_config['url']}")
        
        try:
            # Fetch the webpage
            response = self.session.get(self.site_config['url'], timeout=20)
            response.raise_for_status()
            
            # Save HTML for debugging
            html = response.text
            self.save_html(html)
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract articles using the configured selectors
            articles = []
            
            # Find all article containers
            article_containers = soup.select(self.site_config['article_container'])
            self.log(f"Found {len(article_containers)} article containers")
            
            for container in article_containers:
                try:
                    article = self._extract_article_from_container(container)
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.log(f"Error extracting article: {str(e)}")
            
            # Remove duplicates based on URL if specified
            if self.site_config.get('remove_duplicates', True):
                unique_articles = []
                seen_urls = set()
                
                for article in articles:
                    if article['link'] not in seen_urls:
                        seen_urls.add(article['link'])
                        unique_articles.append(article)
                
                articles = unique_articles
            
            self.log(f"Total articles found: {len(articles)}")
            
            return articles
        
        except Exception as e:
            self.log(f"Error scraping news: {str(e)}")
            return []
    
    def _extract_article_from_container(self, container):
        """Extract article information from a container using configuration"""
        try:
            # Extract title
            title = ""
            if 'title' in self.site_config['selectors']:
                title_elem = self._find_element(container, self.site_config['selectors']['title'])
                if title_elem:
                    title = title_elem.get_text().strip()
            
            if not title:
                return None
            
            # Extract link
            link = ""
            if 'link' in self.site_config['selectors']:
                # Check if link selector is the same as title (title inside link)
                if self.site_config['selectors']['link'] == 'same_as_title':
                    # Find the parent anchor of the title
                    title_elem = self._find_element(container, self.site_config['selectors']['title'])
                    if title_elem:
                        link_elem = title_elem.find_parent('a')
                        if not link_elem and title_elem.find('a'):
                            link_elem = title_elem.find('a')
                else:
                    link_elem = self._find_element(container, self.site_config['selectors']['link'])
                
                if link_elem and link_elem.get('href'):
                    link = link_elem.get('href')
            
            if not link:
                return None
            
            # Make absolute URL
            full_url = urljoin(self.site_config['url'], link)
            
            # Extract summary
            summary = ""
            if 'summary' in self.site_config['selectors']:
                summary_elem = self._find_element(container, self.site_config['selectors']['summary'])
                if summary_elem:
                    summary = summary_elem.get_text().strip()
            
            # Extract publish date
            publish_date = None
            if 'date' in self.site_config['selectors']:
                date_elem = self._find_element(container, self.site_config['selectors']['date'])
                if date_elem:
                    # Try datetime attribute first
                    publish_date = date_elem.get('datetime') or date_elem.get_text().strip()
                    # Apply custom date parser if provided
                    if 'date_parser' in self.site_config and self.site_config['date_parser']:
                        publish_date = self.site_config['date_parser'](publish_date)
                    else:
                        publish_date = self._parse_relative_date(publish_date)
            
            # Extract category
            category = None
            if 'category' in self.site_config['selectors']:
                category_elem = self._find_element(container, self.site_config['selectors']['category'])
                if category_elem:
                    category = category_elem.get_text().strip()
            
            # Extract author
            author = None
            if 'author' in self.site_config['selectors']:
                author_elem = self._find_element(container, self.site_config['selectors']['author'])
                if author_elem:
                    author = author_elem.get_text().strip()
            
            # Extract image URL
            image_url = None
            if 'image' in self.site_config['selectors']:
                image_elem = self._find_element(container, self.site_config['selectors']['image'])
                if image_elem:
                    if image_elem.name == 'img':
                        image_url = image_elem.get('src') or image_elem.get('data-src')
                    else:
                        img_tag = image_elem.find('img')
                        if img_tag:
                            image_url = img_tag.get('src') or img_tag.get('data-src')
                    
                    if image_url:
                        image_url = urljoin(self.site_config['url'], image_url)
            
            # Build article dict
            article = {
                'title': title,
                'link': full_url,
                'summary': summary,
                'publish_date': publish_date,
                'category': category,
                'author': author,
                'image_url': image_url,
                'source': self.site_config['name']
            }
            
            # Apply custom processing if provided
            if 'post_process' in self.site_config and self.site_config['post_process']:
                article = self.site_config['post_process'](article, container)
            
            return article
        
        except Exception as e:
            self.log(f"Error extracting article from container: {str(e)}")
            return None
    
    def _find_element(self, container, selector_config):
        """Find an element using selector configuration"""
        if isinstance(selector_config, str):
            # Simple selector
            return container.select_one(selector_config)
        elif isinstance(selector_config, list):
            # Multiple selectors, try each until one works
            for selector in selector_config:
                elem = container.select_one(selector)
                if elem:
                    return elem
            return None
        elif isinstance(selector_config, dict):
            # Advanced selector with multiple attempts
            for selector_type, selector_value in selector_config.items():
                if selector_type == 'css':
                    for selector in (selector_value if isinstance(selector_value, list) else [selector_value]):
                        elem = container.select_one(selector)
                        if elem:
                            return elem
                elif selector_type == 'tag':
                    return container.find(selector_value)
                elif selector_type == 'class':
                    return container.find(class_=selector_value)
                elif selector_type == 'attrs':
                    return container.find(attrs=selector_value)
            return None
    
    def _parse_relative_date(self, date_text):
        """Parse relative dates like '2 hours ago' to ISO format"""
        if not date_text:
            return None
        
        date_text = date_text.lower().strip()
        now = datetime.datetime.now()
        
        # Handle relative dates
        if 'minute' in date_text or 'min' in date_text:
            match = re.search(r'(\d+)', date_text)
            if match:
                minutes = int(match.group(1))
                return (now - datetime.timedelta(minutes=minutes)).isoformat()
        elif 'hour' in date_text:
            match = re.search(r'(\d+)', date_text)
            if match:
                hours = int(match.group(1))
                return (now - datetime.timedelta(hours=hours)).isoformat()
        elif 'day' in date_text:
            match = re.search(r'(\d+)', date_text)
            if match:
                days = int(match.group(1))
                return (now - datetime.timedelta(days=days)).isoformat()
        elif 'yesterday' in date_text:
            return (now - datetime.timedelta(days=1)).isoformat()
        elif 'today' in date_text:
            return now.isoformat()
        
        return date_text  # Return as-is if we can't parse it
    
    def save_to_json(self, articles, custom_filename=None):
        """Save articles to JSON file"""
        # Create filename
        if custom_filename:
            filename = custom_filename
        else:
            site_name = self.site_config['name'].lower().replace(' ', '_')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{site_name}_news_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        self.log(f"Data saved to: {filepath}")
        return filepath
    
    def save_to_csv(self, articles, custom_filename=None):
        """Save articles to CSV file"""
        # Create filename
        if custom_filename:
            filename = custom_filename
        else:
            site_name = self.site_config['name'].lower().replace(' ', '_')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{site_name}_news_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare fields
        fieldnames = ['title', 'link', 'summary', 'publish_date', 'category', 'author', 'image_url', 'source']
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                # Ensure all fields are present
                row = {field: article.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        self.log(f"CSV data saved to: {filepath}")
        return filepath