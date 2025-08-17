"""
Web scraping module for the Telegram Product Scraper Bot
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from unshortenit import UnshortenIt

from utils import clean_title, parse_price, get_domain
import config  # Import config

# Setup logging
logger = logging.getLogger(__name__)

def setup_driver():
    """Configure Chrome options for mobile emulation"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--window-size=375,812')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        return None

def unshorten_url(url):
    """Unshorten URL using multiple methods"""
    try:
        # First try unshortenit library
        try:
            return UnshortenIt().unshorten(url)
        except Exception as e:
            logger.debug(f"unshortenit failed: {str(e)}")
        
        # If that fails, try manual expansion
        try:
            import requests
            response = requests.head(url, allow_redirects=True, timeout=10)
            return response.url
        except Exception as e:
            logger.debug(f"Manual unshortening failed: {str(e)}")
            return url
    except Exception as e:
        logger.error(f"Error unshortening URL {url}: {str(e)}")
        return url

def capture_screenshot(driver, prefix="screenshot"):
    """Capture screenshot and save to file"""
    timestamp = int(time.time())
    filename = f"{config.SCREENSHOT_DIR}/{prefix}_{timestamp}.png"
    
    # Take screenshot
    driver.save_screenshot(filename)
    
    # Check if it's a valid image
    if not os.path.exists(filename) or os.path.getsize(filename) < 1000:
        raise Exception("Screenshot capture failed")
    
    return filename

def scrape_meesho(url, pin_code=config.PIN_DEFAULT):
    """Scrape Meesho product details with screenshots"""
    logger.info(f"Scraping Meesho product: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return None
            
        driver.set_page_load_timeout(config.TIMEOUT)
        
        # Load product page
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.pdp-product-title'))
        )
        
        # Extract product details
        title_element = driver.find_element(By.CSS_SELECTOR, '.pdp-product-title')
        price_element = driver.find_element(By.CSS_SELECTOR, '.price-discounted')
        size_elements = driver.find_elements(By.CSS_SELECTOR, '.size-selector-button')
        
        # Process title (gender first, clean)
        title = title_element.text.strip()
        cleaned_title = clean_title(title, is_clothing=True)
        
        # Process price
        price = price_element.text.strip()
        price_value = parse_price(price)
        
        # Process available sizes
        available_sizes = []
        for size_element in size_elements:
            if "disabled" not in size_element.get_attribute("class"):
                available_sizes.append(size_element.text.strip())
        
        # Capture screenshots
        product_screenshot = capture_screenshot(driver, "meesho_product")
        
        # Return structured data
        return {
            'platform': 'meesho',
            'title': cleaned_title,
            'price': price_value,
            'sizes': available_sizes,
            'pin': pin_code,
            'images': [product_screenshot],
            'url': url,
            'is_clothing': True
        }
        
    except Exception as e:
        logger.error(f"Meesho scraping error: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_myntra(url):
    """Scrape Myntra product details"""
    logger.info(f"Scraping Myntra product: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return None
            
        driver.set_page_load_timeout(config.TIMEOUT)
        
        # Load product page
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title'))
        )
        
        # Extract product details
        title_element = driver.find_element(By.CSS_SELECTOR, 'h1.product-title')
        price_element = driver.find_element(By.CSS_SELECTOR, 'span.product-price')
        size_elements = driver.find_elements(By.CSS_SELECTOR, 'div.size-selector span')
        
        # Process title
        title = title_element.text.strip()
        cleaned_title = clean_title(title, is_clothing=True)
        
        # Process price
        price = price_element.text.strip()
        price_value = parse_price(price)
        
        # Process available sizes
        available_sizes = []
        for size_element in size_elements:
            if "disabled" not in size_element.get_attribute("class"):
                available_sizes.append(size_element.text.strip())
        
        # Capture screenshot
        screenshot = capture_screenshot(driver, "myntra_product")
        
        # Return structured data
        return {
            'platform': 'myntra',
            'title': cleaned_title,
            'price': price_value,
            'sizes': available_sizes,
            'images': [screenshot],
            'url': url,
            'is_clothing': True
        }
        
    except Exception as e:
        logger.error(f"Myntra scraping error: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_amazon(url):
    """Scrape Amazon product details"""
    logger.info(f"Scraping Amazon product: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return None
            
        driver.set_page_load_timeout(config.TIMEOUT)
        
        # Load product page
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'productTitle'))
        )
        
        # Extract product details
        title_element = driver.find_element(By.ID, 'productTitle')
        price_element = driver.find_element(By.XPATH, '//span[contains(@class, "a-price-whole")]')
        
        # Process title
        title = title_element.text.strip()
        cleaned_title = clean_title(title, is_clothing=False)
        
        # Process price
        price = price_element.text.strip()
        price_value = parse_price(price)
        
        # Capture screenshot
        screenshot = capture_screenshot(driver, "amazon_product")
        
        # Return structured data
        return {
            'platform': 'amazon',
            'title': cleaned_title,
            'price': price_value,
            'sizes': [],
            'images': [screenshot],
            'url': url,
            'is_clothing': 'clothing' in url.lower() or 'fashion' in url.lower()
        }
        
    except Exception as e:
        logger.error(f"Amazon scraping error: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def process_link(link, pin_code=config.PIN_DEFAULT):
    """Main link processing function"""
    logger.info(f"Processing link: {link}")
    
    # Unshorten the URL
    original_url = unshorten_url(link)
    if not original_url:
        logger.warning(f"Could not unshorten URL: {link}")
        return None
    
    logger.info(f"Unshortened URL: {original_url}")
    
    # Clean URL (remove tracking parameters)
    from utils import clean_url
    clean_url = clean_url(original_url)
    logger.info(f"Cleaned URL: {clean_url}")
    
    # Determine platform
    domain = get_domain(clean_url)
    logger.info(f"Detected domain: {domain}")
    
    # Check if domain is supported
    supported_domains = [d for domains in [
        list(config.SUPPORTED_DOMAINS.values()), 
        config.SHORTENER_DOMAINS
    ] for d in domains]
    
    if not any(domain.endswith(supported) for supported in supported_domains):
        logger.warning(f"Unsupported domain: {domain}")
        return None
    
    # Scrape platform-specific data
    if 'meesho.com' in domain:
        return scrape_meesho(clean_url, pin_code)
    elif 'myntra.com' in domain:
        return scrape_myntra(clean_url)
    elif 'amazon.in' in domain:
        return scrape_amazon(clean_url)
    else:
        logger.info(f"No specific scraper for domain: {domain}")
        # Fallback to generic scraping
        driver = setup_driver()
        if not driver:
            return None
            
        try:
            driver.get(clean_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            screenshot = capture_screenshot(driver, "generic_product")
            
            return {
                'platform': 'generic',
                'title': 'Product',
                'price': 'Price unavailable',
                'sizes': [],
                'images': [screenshot],
                'url': clean_url,
                'is_clothing': False
            }
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass        
        # Process title (gender first, clean)
        title = title_element.text.strip()
        cleaned_title = clean_title(title, is_clothing=True)
        
        # Process price
        price = price_element.text.strip()
        price_value = parse_price(price)
        
        # Process available sizes
        available_sizes = []
        for size_element in size_elements:
            if "disabled" not in size_element.get_attribute("class"):
                available_sizes.append(size_element.text.strip())
        
        # Capture screenshots
        product_screenshot = capture_screenshot(driver, "meesho_product")
        
        # Return structured data
        return {
            'platform': 'meesho',
            'title': cleaned_title,
            'price': price_value,
            'sizes': available_sizes,
            'pin': pin_code,
            'images': [product_screenshot],
            'url': url,
            'is_clothing': True
        }
        
    except Exception as e:
        logger.error(f"Meesho scraping error: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_myntra(url):
    """Scrape Myntra product details"""
    logger.info(f"Scraping Myntra product: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return None
            
        driver.set_page_load_timeout(TIMEOUT)
        
        # Load product page
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title'))
        )
        
        # Extract product details
        title_element = driver.find_element(By.CSS_SELECTOR, 'h1.product-title')
        price_element = driver.find_element(By.CSS_SELECTOR, 'span.product-price')
        size_elements = driver.find_elements(By.CSS_SELECTOR, 'div.size-selector span')
        
        # Process title
        title = title_element.text.strip()
        cleaned_title = clean_title(title, is_clothing=True)
        
        # Process price
        price = price_element.text.strip()
        price_value = parse_price(price)
        
        # Process available sizes
        available_sizes = []
        for size_element in size_elements:
            if "disabled" not in size_element.get_attribute("class"):
                available_sizes.append(size_element.text.strip())
        
        # Capture screenshot
        screenshot = capture_screenshot(driver, "myntra_product")
        
        # Return structured data
        return {
            'platform': 'myntra',
            'title': cleaned_title,
            'price': price_value,
            'sizes': available_sizes,
            'images': [screenshot],
            'url': url,
            'is_clothing': True
        }
        
    except Exception as e:
        logger.error(f"Myntra scraping error: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_amazon(url):
    """Scrape Amazon product details"""
    logger.info(f"Scraping Amazon product: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return None
            
        driver.set_page_load_timeout(TIMEOUT)
        
        # Load product page
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'productTitle'))
        )
        
        # Extract product details
        title_element = driver.find_element(By.ID, 'productTitle')
        price_element = driver.find_element(By.XPATH, '//span[contains(@class, "a-price-whole")]')
        
        # Process title
        title = title_element.text.strip()
        cleaned_title = clean_title(title, is_clothing=False)
        
        # Process price
        price = price_element.text.strip()
        price_value = parse_price(price)
        
        # Capture screenshot
        screenshot = capture_screenshot(driver, "amazon_product")
        
        # Return structured data
        return {
            'platform': 'amazon',
            'title': cleaned_title,
            'price': price_value,
            'sizes': [],
            'images': [screenshot],
            'url': url,
            'is_clothing': 'clothing' in url.lower() or 'fashion' in url.lower()
        }
        
    except Exception as e:
        logger.error(f"Amazon scraping error: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def process_link(link, pin_code="110001"):
    """Main link processing function"""
    logger.info(f"Processing link: {link}")
    
    # Unshorten the URL
    original_url = unshorten_url(link)
    if not original_url:
        logger.warning(f"Could not unshorten URL: {link}")
        return None
    
    logger.info(f"Unshortened URL: {original_url}")
    
    # Clean URL (remove tracking parameters)
    from utils import clean_url
    clean_url = clean_url(original_url)
    logger.info(f"Cleaned URL: {clean_url}")
    
    # Determine platform
    domain = get_domain(clean_url)
    logger.info(f"Detected domain: {domain}")
    
    # Check if domain is supported
    supported_domains = [d for domains in [
        list(config.SUPPORTED_DOMAINS.values()), 
        config.SHORTENER_DOMAINS
    ] for d in domains]
    
    if not any(domain.endswith(supported) for supported in supported_domains):
        logger.warning(f"Unsupported domain: {domain}")
        return None
    
    # Scrape platform-specific data
    if 'meesho.com' in domain:
        return scrape_meesho(clean_url, pin_code)
    elif 'myntra.com' in domain:
        return scrape_myntra(clean_url)
    elif 'amazon.in' in domain:
        return scrape_amazon(clean_url)
    else:
        logger.info(f"No specific scraper for domain: {domain}")
        # Fallback to generic scraping
        return {
            'platform': 'generic',
            'title': 'Product',
            'price': 'Price unavailable',
            'sizes': [],
            'images': [capture_screenshot(setup_driver(), "generic_product")],
            'url': clean_url,
            'is_clothing': False
        }
