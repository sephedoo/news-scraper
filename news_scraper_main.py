#!/usr/bin/env python3
# Main News Scraper Script
# Uses the universal scraper with modular site configurations

import argparse
import sys
from site_configs import SITE_CONFIGURATIONS, get_site_config, list_available_sites
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
    parser.add_argument('--validate', action='store_true', help='Validate site configurations')
    parser.add_argument('--create-config', nargs=3, metavar=('SITE_KEY', 'SITE_NAME', 'SITE_URL'),
                       help='Create a new site configuration')
    
    args = parser.parse_args()
    
    # Create new configuration if requested
    if args.create_config:
        site_key, site_name, site_url = args.create_config
        from site_configs.config_manager import create_new_site_config
        create_new_site_config(site_key, site_name, site_url)
        return
    
    # List available sites if requested
    if args.list:
        print("Available news sites:")
        sites = list_available_sites()
        for site_key in sorted(sites):
            config = get_site_config(site_key)
            if config:
                print(f"  {site_key}: {config.get('name', site_key)}")
        return
    
    # Validate configurations if requested
    if args.validate:
        from site_configs.config_manager import config_manager
        print("Validating site configurations...")
        for site_key in list_available_sites():
            is_valid, message = config_manager.validate_config(site_key)
            status = "✓" if is_valid else "✗"
            print(f"{status} {site_key}: {message}")
        return
    
    # Determine which sites to scrape
    sites_to_scrape = []
    
    if args.all:
        sites_to_scrape = list_available_sites()
    elif args.sites:
        # Validate requested sites
        for site in args.sites:
            if site.lower() in list_available_sites():
                sites_to_scrape.append(site.lower())
            else:
                print(f"Warning: Site '{site}' not found in configurations")
                print(f"Available sites: {', '.join(sorted(list_available_sites()))}")
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
            config = get_site_config(site_key)
            print(f"Scraping {config.get('name', site_key)}")
            print('=' * 50)
            
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
                print(f"Found {len(articles)} articles from {config.get('name', site_key)}")
                
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
                        
                    # Show configuration being used
                    print(f"\nConfiguration summary:")
                    print(f"  URL: {config['url']}")
                    print(f"  Container: {config['article_container']}")
                    print(f"  Custom processors: {'Yes' if config.get('date_parser') or config.get('post_process') else 'No'}")
            else:
                print(f"No articles found from {config.get('name', site_key)}")
        
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