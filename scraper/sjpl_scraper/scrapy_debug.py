import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# --- IMPORTANT: Ensure current working directory is the Scrapy project root ---
# This makes sure Scrapy finds scrapy.cfg and settings.py correctly.
# Get the directory of the current script (scrapy_debug.py)
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the Scrapy project root
# which is '/Users/liuxinxin/Documents/GitHub/playhard/scraper/sjpl_scraper/'
# This assumes scrapy_debug.py is directly inside sjpl_scraper.
os.chdir(current_script_dir)
print(f"Changed current working directory to: {os.getcwd()}")


# --- Adjust sys.path to allow imports from sjpl_scraper and its submodules ---
# The parent directory of sjpl_scraper is 'scraper'.
# We need 'scraper' to be on the sys.path so 'sjpl_scraper' can be imported as a package.
# Go up one level from 'current_script_dir' to get to 'scraper' directory.
scraper_parent_dir = os.path.dirname(current_script_dir)
if scraper_parent_dir not in sys.path:
    sys.path.insert(0, scraper_parent_dir)
    print(f"Added '{scraper_parent_dir}' to sys.path.")

# Now import your spider relative to the 'scraper' directory
# (i.e., 'sjpl_scraper.spiders.sjpl_events')
try:
    from sjpl_scraper.spiders.sjpl_events import SjplEventsSpider
    print("Successfully imported SjplEventsSpider.")
except ImportError as e:
    print(f"ImportError: Could not import SjplEventsSpider. Check your SPIDER_MODULES setting and sys.path. Error: {e}")
    sys.exit(1) # Exit if import fails

# Get Scrapy project settings.
# Since we changed the working directory, get_project_settings() should now find scrapy.cfg and settings.py
settings = get_project_settings()
print(f"Loaded Scrapy settings from: {settings.get('PROJECT_SETTINGS_PATH')}")
print(f"SPIDER_MODULES setting: {settings.get('SPIDER_MODULES')}")


process = CrawlerProcess(settings)
# Correct the spider name here. 'sjpl_events' is the 'name' attribute in your spider class.
process.crawl('sjpl_events')
print("Starting Scrapy process...")
process.start() # The script will block here until all crawls are finished
print("Scrapy process finished.")