#!/usr/bin/env python3
# AWS Blog configuration

import datetime
import re

# Main AWS Blog configuration
SITE_CONFIG = {
    'name': 'AWS Blog',
    'url': 'https://aws.amazon.com/blogs/aws',
    'article_container': '.lb-row.lb-snap',
    'selectors': {
        'title': 'h2.lb-bold.blog-post-title span[property="name headline"]',
        'link': 'h2.lb-bold.blog-post-title a[property="url"]',
        'summary': '.blog-post-excerpt p',
        'date': 'time[property="datePublished"]',
        'category': '.blog-post-categories a span[property="articleSection"]',
        'author': 'span[property="author"] span[property="name"]',
        'image': '.lb-col.lb-mid-6.lb-tiny-24 img'
    },
    'remove_duplicates': True,
    'timeout': 20
}

# Custom date parser for AWS Blog
def parse_aws_date(date_str):
    """Parse AWS Blog's date format"""
    if not date_str:
        return None
    
    # AWS uses format like "2025-05-07T06:34:48-07:00"
    try:
        # Clean up the datetime string if it has timezone offset
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}', date_str):
            # Remove timezone offset for parsing
            clean_date = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)
            dt = datetime.datetime.strptime(clean_date, '%Y-%m-%dT%H:%M:%S')
            return dt.isoformat()
    except:
        pass
    
    # Try other formats if needed
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
        '%d %b %Y',
        '%B %d, %Y'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except:
            continue
    
    # Return as-is if we can't parse it
    return date_str

# Custom post-processor for AWS Blog articles
def process_aws_article(article, container):
    """Add AWS-specific post-processing"""
    
    # Extract all categories (AWS blogs can have multiple)
    category_elements = container.select('.blog-post-categories a span[property="articleSection"]')
    if category_elements:
        article['categories'] = [cat.get_text().strip() for cat in category_elements]
        # Set the first category as the main category
        if article['categories']:
            article['category'] = article['categories'][0]
    
    # Extract sharing information
    share_links = container.select('.blog-share-dialog a.lb-txt')
    if share_links:
        social_platforms = []
        for link in share_links:
            if 'facebook' in link.get('href', ''):
                social_platforms.append('Facebook')
            elif 'twitter' in link.get('href', ''):
                social_platforms.append('Twitter')
            elif 'linkedin' in link.get('href', ''):
                social_platforms.append('LinkedIn')
            elif 'mailto:' in link.get('href', ''):
                social_platforms.append('Email')
        
        if social_platforms:
            article['social_sharing'] = social_platforms
    
    # Extract AWS-specific metadata
    # Check for AWS service mentions in title or summary
    aws_services = [
        'EC2', 'S3', 'Lambda', 'RDS', 'CloudFormation', 'ECS', 'EKS', 'SQS', 'SNS',
        'DynamoDB', 'CloudFront', 'Route 53', 'VPC', 'IAM', 'CloudWatch', 'Kinesis',
        'Redshift', 'EMR', 'Glue', 'SageMaker', 'CodeDeploy', 'CodePipeline', 'CodeBuild'
    ]
    
    title_and_summary = f"{article.get('title', '')} {article.get('summary', '')}".upper()
    mentioned_services = []
    
    for service in aws_services:
        if service in title_and_summary:
            mentioned_services.append(service)
    
    if mentioned_services:
        article['aws_services'] = mentioned_services
    
    # Check for AWS Region announcements
    if any(keyword in title_and_summary for keyword in ['REGION', 'AVAILABILITY ZONE', 'AZ']):
        article['is_region_announcement'] = True
        
        # Try to extract region name
        region_pattern = r'([A-Z][a-z]+(?:\s+[A-Za-z]+)*)\s+Region'
        matches = re.findall(region_pattern, article.get('title', '') + article.get('summary', ''))
        if matches:
            article['aws_regions'] = list(set(matches))
    
    # Check for feature announcements
    if any(keyword in title_and_summary for keyword in ['LAUNCH', 'ANNOUNCE', 'INTRODUCE', 'NEW']):
        article['is_feature_announcement'] = True
    
    # Extract additional metadata from footer
    footer = container.select_one('.blog-post-meta')
    if footer:
        # Get permalink URL
        permalink = footer.select_one('a[property="url"]')
        if permalink:
            article['permalink'] = permalink.get('href')
        
        # Check for comments
        comments_link = footer.select_one('a[href$="#Comments"]')
        if comments_link:
            article['comments_enabled'] = True
    
    # Get image alternative text
    image_elem = container.select_one('img')
    if image_elem:
        alt_text = image_elem.get('alt', '')
        if alt_text:
            article['image_alt'] = alt_text
        
        # Get image dimensions
        width = image_elem.get('width')
        height = image_elem.get('height')
        if width and height:
            article['image_dimensions'] = {
                'width': int(width),
                'height': int(height)
            }
    
    return article

# Add custom processors to the config
SITE_CONFIG['date_parser'] = parse_aws_date
SITE_CONFIG['post_process'] = process_aws_article

# Alternative selectors for AWS (in case main ones change)
ALTERNATIVE_SELECTORS = {
    'article_container': [
        '.lb-row.lb-snap',
        '.blog-post-container',
        '.aws-blog-post',
        '.lb-post-item'
    ],
    'title': [
        'h2.blog-post-title span[property="name headline"]',
        'h2.blog-post-title a',
        '.lb-bold.blog-post-title',
        'h2'
    ],
    'link': [
        'h2.blog-post-title a[property="url"]',
        'a[property="url"][rel="bookmark"]',
        '.blog-post-title a'
    ],
    'summary': [
        '.blog-post-excerpt p',
        '.blog-post-excerpt',
        'section[property="description"] p',
        '.lb-rtxt p'
    ],
    'date': [
        'time[property="datePublished"]',
        '.blog-post-meta time',
        '.blog-post-date',
        'time'
    ]
}

# AWS-specific utility functions
def extract_aws_regions(text):
    """Extract AWS region names from text"""
    region_patterns = [
        r'us-east-\d',
        r'us-west-\d',
        r'eu-west-\d',
        r'eu-central-\d',
        r'ap-northeast-\d',
        r'ap-southeast-\d',
        r'ap-south-\d',
        r'ca-central-\d',
        r'sa-east-\d',
        r'af-south-\d',
        r'me-south-\d',
        r'ap-east-\d',
        r'eu-north-\d',
        r'me-central-\d'
    ]
    
    regions = []
    for pattern in region_patterns:
        matches = re.findall(pattern, text.lower())
        regions.extend(matches)
    
    return list(set(regions))

def get_aws_blog_feed_url():
    """Get AWS blog RSS feed URL"""
    return "https://aws.amazon.com/blogs/aws/feed/"

def categorize_aws_blog_post(article):
    """Categorize AWS blog post based on content"""
    title_summary = f"{article.get('title', '')} {article.get('summary', '')}".lower()
    
    categories = []
    
    # Service announcements
    if any(word in title_summary for word in ['launch', 'announce', 'introduce', 'new', 'available']):
        categories.append('Service Announcement')
    
    # Regional news
    if any(word in title_summary for word in ['region', 'availability zone', 'az', 'data center']):
        categories.append('Regional News')
    
    # Security and compliance
    if any(word in title_summary for word in ['security', 'compliance', 'iam', 'secrets', 'kms']):
        categories.append('Security & Compliance')
    
    # Pricing and cost
    if any(word in title_summary for word in ['pricing', 'cost', 'billing', 'free tier', 'savings']):
        categories.append('Pricing & Cost')
    
    # Customer stories
    if any(word in title_summary for word in ['customer', 'case study', 'success story']):
        categories.append('Customer Story')
    
    # Technical deep dives
    if any(word in title_summary for word in ['architecture', 'best practices', 'migration', 'performance']):
        categories.append('Technical Deep Dive')
    
    return categories

# AWS service categories
AWS_SERVICE_CATEGORIES = {
    'Compute': ['EC2', 'Lambda', 'ECS', 'EKS', 'Batch', 'Fargate', 'Lightsail'],
    'Storage': ['S3', 'EBS', 'EFS', 'Glacier', 'Storage Gateway', 'FSx'],
    'Database': ['RDS', 'DynamoDB', 'Aurora', 'ElastiCache', 'Redshift', 'DocumentDB'],
    'Networking': ['VPC', 'CloudFront', 'Route 53', 'ELB', 'Direct Connect', 'API Gateway'],
    'Security': ['IAM', 'KMS', 'Secrets Manager', 'WAF', 'GuardDuty', 'Security Hub'],
    'Analytics': ['Kinesis', 'EMR', 'Glue', 'Athena', 'QuickSight', 'Lake Formation'],
    'AI/ML': ['SageMaker', 'Rekognition', 'Comprehend', 'Textract', 'Personalize', 'Lex'],
    'Developer Tools': ['CodeCommit', 'CodeBuild', 'CodeDeploy', 'CodePipeline', 'Cloud9'],
    'Management': ['CloudWatch', 'CloudFormation', 'Systems Manager', 'Organizations', 'Config']
}

# Export the configuration
if __name__ == "__main__":
    # Print configuration summary when run directly
    print(f"AWS Blog Configuration:")
    print(f"Site: {SITE_CONFIG['name']}")
    print(f"URL: {SITE_CONFIG['url']}")
    print(f"Article container: {SITE_CONFIG['article_container']}")
    print("\nSelectors:")
    for key, selector in SITE_CONFIG['selectors'].items():
        print(f"  {key}: {selector}")
    
    # Test the date parser
    test_date = "2025-05-07T06:34:48-07:00"
    parsed = parse_aws_date(test_date)
    print(f"\nDate parsing test:")
    print(f"Input: {test_date}")
    print(f"Output: {parsed}")