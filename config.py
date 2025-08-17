"""
Configuration file for Telegram Product Scraper Bot
"""

# Bot configuration
BOT_TOKEN = "8327175937:AAGoWZPlDM_UX7efZv6_7vJMHDsrZ3-EyIA"  # Your token is already here
BOT_NAME = "Work_flow"
ADMIN_USER_IDS = []  # Add admin user IDs here

# Platform configuration
SUPPORTED_DOMAINS = {
    'amazon': 'amazon.in',
    'flipkart': 'flipkart.com',
    'meesho': 'meesho.com',
    'myntra': 'myntra.com',
    'ajio': 'ajio.com',
    'snapdeal': 'snapdeal.com',
    'wishlink': 'wishlink.com'
}

SHORTENER_DOMAINS = [
    'cutt.ly', 'fkrt.cc', 'amzn-to.co', 
    'bitli.in', 'spoo.me', 'da.gd', 'wishlink.com'
]

# System configuration
PIN_DEFAULT = '110001'
TIMEOUT = 15
WATERMARK_THRESHOLD = 0.85
SCREENSHOT_DIR = "screenshots"
MAX_RETRIES = 3

# Mode configuration
MODE_ADVANCED = False
