"""
Utility functions for the Telegram Product Scraper Bot
"""

import os
import re
import time
from urllib.parse import urlparse, parse_qs, unquote
import config  # Import config

def clean_url(url):
    """Remove affiliate tags and tracking parameters from URL"""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Define parameters to keep (platform-specific)
    keep_params = {
        'meesho.com': ['pid', 'product_id', 'p'],
        'myntra.com': ['p', 'productId'],
        'amazon.in': ['asin', 'product-id'],
        'flipkart.com': ['pid', 'id']
    }
    
    # Determine which params to keep based on domain
    domain = get_domain(url)
    params_to_keep = []
    for key_domain, params in keep_params.items():
        if key_domain in domain:
            params_to_keep = params
            break
    
    # Filter query parameters
    filtered_query = '&'.join([
        f"{k}={v[0]}" for k, v in query_params.items() 
        if k.lower() in [p.lower() for p in params_to_keep]
    ])
    
    # Reconstruct URL
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if filtered_query:
        clean_url += f"?{filtered_query}"
    
    return clean_url

def get_domain(url):
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc.lower().split(':')[0]

def clean_title(title, is_clothing=False):
    """Clean product title according to requirements"""
    # Convert to English if needed
    title = title.encode('ascii', 'ignore').decode('ascii', 'ignore')
    
    # Remove repetitive words and marketing fluff
    fluff_words = ['best', 'top', 'premium', 'original', 'authentic', 'new', 'latest', '2023', '2024']
    for word in fluff_words:
        title = re.sub(r'\b' + word + r'\b', '', title, flags=re.IGNORECASE)
    
    # For clothing, ensure gender comes first
    if is_clothing:
        gender = ''
        if re.search(r'\b(women|ladies|female|girl)\b', title, re.IGNORECASE):
            gender = 'Women'
            title = re.sub(r'\b(women|ladies|female|girl)\b', '', title, flags=re.IGNORECASE)
        elif re.search(r'\b(men|gentlemen|male|boy)\b', title, re.IGNORECASE):
            gender = 'Men'
            title = re.sub(r'\b(men|gentlemen|male|boy)\b', '', title, flags=re.IGNORECASE)
        
        # Remove extra spaces and clean up
        title = re.sub(r'\s+', ' ', title).strip()
        return f"{gender} {title}".strip()
    
    return re.sub(r'\s+', ' ', title).strip()

def parse_price(price_str):
    """Parse price string to numeric value"""
    # Extract numeric value
    price_value = re.sub(r'[^\d.]', '', price_str)
    if not price_value:
        return "Price unavailable"
    
    # Convert to float and format
    try:
        return f"{float(price_value):.0f}"
    except:
        return "Price unavailable"

def format_output(data):
    """Format text according to platform-specific rules"""
    platform = data['platform']
    title = data['title']
    price = data['price']
    url = data['url']
    
    # Common footer
    footer = "\n@reviewcheckk"
    
    # Platform-specific formatting
    if platform == 'meesho':
        # Meesho format: [Gender] [Quantity] [Clean Title] @[price] rs
        formatted = f"{title} @{price} rs\n{url}"
        
        # Add size info if available
        if data.get('sizes') and data['sizes']:
            formatted += f"\nSize - {', '.join(data['sizes'])}"
        
        # Add pin code
        formatted += f"\nPin - {data.get('pin', config.PIN_DEFAULT)}"
        
        return formatted + footer
    
    elif data.get('is_clothing', False):
        # Clothing format (non-Meesho): [Gender] [Quantity] [Clean Title] @[price] rs
        formatted = f"{title} @{price} rs\n{url}"
        return formatted + footer
    
    else:
        # Non-clothing format: [Brand] [Clean Title] from @[price] rs
        formatted = f"{title} from @{price} rs\n{url}"
        return formatted + footer

def setup_directories():
    """Create necessary directories"""
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)        
        return formatted + footer
    
    elif data.get('is_clothing', False):
        # Clothing format (non-Meesho): [Gender] [Quantity] [Clean Title] @[price] rs
        formatted = f"{title} @{price} rs\n{url}"
        return formatted + footer
    
    else:
        # Non-clothing format: [Brand] [Clean Title] from @[price] rs
        formatted = f"{title} from @{price} rs\n{url}"
        return formatted + footer

def setup_directories():
    """Create necessary directories"""
    os.makedirs("screenshots", exist_ok=True)
