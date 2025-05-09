#!/usr/bin/env python3
# Main News Scraper Script
# Uses the universal scraper with configurable selectors

import argparse
import sys
from news_scraper_configs import SITE_CONFIGURATIONS, get_config_with_processors
from universal_news_scraper import UniversalNewsScraper

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Universal News Scraper')
    
    parser.add_argument('--sites', nargs='+', help='Sites to scrape (e.g., bbc cnn reuters)')
    parser.add_argument('--all', action='store_true', help='Scrape all configured sites')
    parser.add_argument('--list', action='store_true', help='List all available sites')
    parser.add_argument('--output', choices=['json', 'csv', 'both'], default='both', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--combine', action='store_true', help='Combine results from all sites')
    parser.add_argument('--max-articles', type=int, help='Maximum articles per site')
    
    args = parser.parse_args()
    
    # List available sites if requested
    if args.list:
        print("Available news sites:")
        for site_key, config in SITE_CONFIGURATIONS.items():
            print(f"  {site_key}: {config['name']}")
        return
    
    # Determine which sites to scrape
    sites_to_scrape = []
    
    if args.all:
        sites_to_scrape = list(SITE_CONFIGURATIONS.keys())
    elif args.sites:
        # Validate requested sites
        for site in args.sites:
            if site.lower() in SITE_CONFIGURATIONS:
                sites_to_scrape.append(site.lower())
            else:
                print(f"Warning: Site '{site}' not found in configurations")
    else:
        # Default to BBC if no sites specified
        sites_to_scrape = ['bbc']
        print("No sites specified, defaulting to BBC")
    
    if not sites_to_scrape:
        print("No valid sites to scrape. Use --list to see available sites.")
        return
    
    # Storage for all articles
    all_articles = []
    
    # Scrape each site
    for site_key in sites_to_scrape:
        try:
            print(f"\n{'=' * 50}")
            print(f"Scraping {SITE_CONFIGURATIONS[site_key]['name']}")
            print('=' * 50)
            
            # Get configuration with custom processors
            config = get_config_with_processors(site_key)
            
            # Create scraper instance
            scraper = UniversalNewsScraper(config, verbose=args.verbose)
            
            # Scrape articles
            articles = scraper.scrape_news()
            
            # Limit articles if requested
            if args.max_articles and len(articles) > args.max_articles:
                articles = articles[:args.max_articles]
                if args.verbose:
                    print(f"Limited to {args.max_articles} articles")
            
            if articles:
                print(f"Found {len(articles)} articles from {config['name']}")
                
                # Save individual site results
                if not args.combine:
                    if args.output in ['json', 'both']:
                        scraper.save_to_json(articles)
                    
                    if args.output in ['csv', 'both']:
                        scraper.save_to_csv(articles)
                
                # Add to combined results
                all_articles.extend(articles)
                
                # Print first few articles as sample
                if args.verbose and articles:
                    print("\nSample articles:")
                    for i, article in enumerate(articles[:3]):
                        print(f"  {i+1}. {article['title'][:60]}...")
            else:
                print(f"No articles found from {config['name']}")
        
        except Exception as e:
            print(f"Error scraping {site_key}: {str(e)}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Save combined results if requested
    if args.combine and all_articles:
        print(f"\n{'=' * 50}")
        print(f"Combined Results: {len(all_articles)} total articles")
        print('=' * 50)
        
        # Create combined scraper for saving
        combined_config = {'name': 'Combined News'}
        combined_scraper = UniversalNewsScraper(combined_config, verbose=args.verbose)
        
        if args.output in ['json', 'both']:
            combined_scraper.save_to_json(all_articles, 'combined_news.json')
        
        if args.output in ['csv', 'both']:
            combined_scraper.save_to_csv(all_articles, 'combined_news.csv')
        
        # Print summary statistics
        print("\nSummary by source:")
        source_counts = {}
        for article in all_articles:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in sorted(source_counts.items()):
            print(f"  {source}: {count} articles")
    
    print("\nScraping completed!")

if __name__ == "__main__":
    main()