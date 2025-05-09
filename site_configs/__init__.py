#!/usr/bin/env python3
# Site configuration package initializer
# Automatically loads all site configurations

import os
import importlib
import inspect

# Dictionary to store all site configurations
SITE_CONFIGURATIONS = {}

# Get the directory containing this file
config_dir = os.path.dirname(os.path.abspath(__file__))

# Automatically import all config modules
for filename in os.listdir(config_dir):
    if filename.endswith('_config.py') and not filename.startswith('__'):
        # Remove .py extension and import module
        module_name = filename[:-3]
        
        try:
            # Import the module
            module = importlib.import_module(f'.{module_name}', package='site_configs')
            
            # Look for site configuration in the module
            if hasattr(module, 'SITE_CONFIG'):
                config = module.SITE_CONFIG
                site_key = module_name.replace('_config', '')
                SITE_CONFIGURATIONS[site_key] = config
                print(f"Loaded configuration for: {config.get('name', site_key)}")
        
        except Exception as e:
            print(f"Warning: Could not load {module_name}: {str(e)}")

# Export configurations for easy import
def get_site_config(site_key):
    """Get configuration for a specific site"""
    return SITE_CONFIGURATIONS.get(site_key)

def list_available_sites():
    """List all available site configurations"""
    return list(SITE_CONFIGURATIONS.keys())

def get_all_configurations():
    """Get all site configurations"""
    return SITE_CONFIGURATIONS.copy()

# For backward compatibility
__all__ = ['SITE_CONFIGURATIONS', 'get_site_config', 'list_available_sites', 'get_all_configurations']