#!/usr/bin/env python3
# Configuration manager for easily handling multiple site configs

import os
import json
from datetime import datetime

class ConfigManager:
    """Manages site configurations for the news scraper"""
    
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or os.path.dirname(os.path.abspath(__file__))
        self.configs = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all site configurations from the config directory"""
        config_files = [f for f in os.listdir(self.config_dir) 
                       if f.endswith('_config.py') and not f.startswith('__')]
        
        for config_file in config_files:
            site_key = config_file.replace('_config.py', '')
            try:
                # Import the module dynamically
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    site_key, 
                    os.path.join(self.config_dir, config_file)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'SITE_CONFIG'):
                    self.configs[site_key] = module.SITE_CONFIG
                    print(f"Loaded config for: {module.SITE_CONFIG.get('name', site_key)}")
            
            except Exception as e:
                print(f"Error loading {config_file}: {str(e)}")
    
    def get_config(self, site_key):
        """Get configuration for a specific site"""
        return self.configs.get(site_key)
    
    def list_sites(self):
        """List all available sites"""
        return list(self.configs.keys())
    
    def save_config_to_json(self, site_key, output_file=None):
        """Save a specific site's configuration to JSON"""
        config = self.get_config(site_key)
        if not config:
            print(f"No configuration found for {site_key}")
            return
        
        if not output_file:
            output_file = f"{site_key}_config.json"
        
        # Remove non-serializable items (functions)
        json_config = {k: v for k, v in config.items() 
                      if not callable(v) and k not in ['date_parser', 'post_process']}
        
        with open(output_file, 'w') as f:
            json.dump(json_config, f, indent=2)
        
        print(f"Saved {site_key} configuration to {output_file}")
    
    def save_all_configs_to_json(self, output_file='all_configs.json'):
        """Save all configurations to a single JSON file"""
        all_configs = {}
        
        for site_key, config in self.configs.items():
            # Remove non-serializable items
            json_config = {k: v for k, v in config.items() 
                          if not callable(v) and k not in ['date_parser', 'post_process']}
            all_configs[site_key] = json_config
        
        with open(output_file, 'w') as f:
            json.dump(all_configs, f, indent=2)
        
        print(f"Saved all configurations to {output_file}")
    
    def create_new_config_template(self, site_key, site_name, site_url):
        """Create a new configuration file template"""
        template = f'''#!/usr/bin/env python3
# {site_name} configuration

import datetime

# Main {site_name} configuration
SITE_CONFIG = {{
    'name': '{site_name}',
    'url': '{site_url}',
    'article_container': '.article-container',  # Update with actual selector
    'selectors': {{
        'title': 'h2.headline',  # Update with actual selector
        'link': 'a.article-link',  # Update with actual selector
        'summary': 'p.description',  # Update with actual selector
        'date': 'time.published',  # Update with actual selector
        'category': '.category',  # Update with actual selector
        'author': '.author',  # Update with actual selector
        'image': 'img'  # Update with actual selector
    }},
    'remove_duplicates': True,
    'timeout': 20
}}

# Custom date parser for {site_name}
def parse_{site_key}_date(date_str):
    """Parse {site_name}'s specific date format"""
    if not date_str:
        return None
    
    # Add your custom date parsing logic here
    
    return date_str

# Custom post-processor for {site_name} articles
def process_{site_key}_article(article, container):
    """Add {site_name}-specific post-processing"""
    
    # Add your custom post-processing logic here
    
    return article

# Add custom processors to the config
SITE_CONFIG['date_parser'] = parse_{site_key}_date
SITE_CONFIG['post_process'] = process_{site_key}_article

# Export the configuration
if __name__ == "__main__":
    print(f"{site_name} Configuration:")
    print(f"Site: {{SITE_CONFIG['name']}}")
    print(f"URL: {{SITE_CONFIG['url']}}")
    print(f"Article container: {{SITE_CONFIG['article_container']}}")
    print("\\nSelectors:")
    for key, selector in SITE_CONFIG['selectors'].items():
        print(f"  {{key}}: {{selector}}")
'''
        
        # Create the config file
        config_file = os.path.join(self.config_dir, f"{site_key}_config.py")
        
        with open(config_file, 'w') as f:
            f.write(template)
        
        print(f"Created new configuration template: {config_file}")
        print("Please update the selectors with actual values from the website")
    
    def validate_config(self, site_key):
        """Validate a site configuration"""
        config = self.get_config(site_key)
        if not config:
            return False, f"No configuration found for {site_key}"
        
        required_fields = ['name', 'url', 'article_container', 'selectors']
        required_selectors = ['title', 'link']  # Minimum required selectors
        
        errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Check required selectors
        if 'selectors' in config:
            for selector in required_selectors:
                if selector not in config['selectors']:
                    errors.append(f"Missing required selector: {selector}")
        
        # Validate URL format
        if 'url' in config and not config['url'].startswith(('http://', 'https://')):
            errors.append("URL must start with http:// or https://")
        
        if errors:
            return False, "\\n".join(errors)
        else:
            return True, "Configuration is valid"
    
    def get_config_summary(self, site_key):
        """Get a summary of a site's configuration"""
        config = self.get_config(site_key)
        if not config:
            return f"No configuration found for {site_key}"
        
        summary = f"""
Configuration Summary for {config.get('name', site_key)}
----------------------------------------
URL: {config.get('url', 'Not specified')}
Article Container: {config.get('article_container', 'Not specified')}

Selectors:
"""
        
        selectors = config.get('selectors', {})
        for key, selector in selectors.items():
            summary += f"  {key}: {selector}\\n"
        
        summary += f"\\nCustom Processors:"
        if 'date_parser' in config:
            summary += f"\\n  - Date Parser: Yes"
        if 'post_process' in config:
            summary += f"\\n  - Post Processor: Yes"
        
        summary += f"\\nTimeout: {config.get('timeout', 20)} seconds"
        summary += f"\\nDuplicate Removal: {config.get('remove_duplicates', True)}"
        
        return summary

# Global config manager instance
config_manager = ConfigManager()

# Export functions for easy access
def get_config(site_key):
    """Get configuration for a site"""
    return config_manager.get_config(site_key)

def list_sites():
    """List all available sites"""
    return config_manager.list_sites()

def create_new_site_config(site_key, site_name, site_url):
    """Create a new site configuration"""
    return config_manager.create_new_config_template(site_key, site_name, site_url)

# Usage example
if __name__ == "__main__":
    print("News Scraper Configuration Manager")
    print("=" * 40)
    
    # List all available sites
    print("\\nAvailable sites:")
    for site in config_manager.list_sites():
        print(f"  - {site}")
    
    # Show summary for each site
    print("\\nConfiguration Summaries:")
    for site in config_manager.list_sites():
        print(config_manager.get_config_summary(site))
        print("-" * 40)
    
    # Validate all configurations
    print("\\nValidation Results:")
    for site in config_manager.list_sites():
        is_valid, message = config_manager.validate_config(site)
        status = "✓" if is_valid else "✗"
        print(f"{status} {site}: {message}")