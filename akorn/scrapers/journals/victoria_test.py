from akorn.scrapers.base import BaseScraper

from datetime import datetime
import time

class Scraper(BaseScraper):
    # List of domains that scraper is for
    domains = ['oxfordjournals.org', 'cercor.oxfordjournals.org']
    # Relative name of config file
    config = 'victoria_test.xml'

 
