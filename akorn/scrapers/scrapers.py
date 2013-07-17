import journals
import logging
import urlparse

logging.basicConfig()
logger = logging.getLogger('scrapers')

class ScraperNotFound(Exception):
  pass


class Scrapers(object):

    def __init__(self):
        self.modules = self.discover()
        self.domains = dict(self.domain_map(self.modules))

        # Add generic scraper, to be used if no match is found
        # TODO Could be an awful design decision?

    def discover(self):
        """
        Return list of all of the Scrapers supported
        """
        # Find all of the submodules in journals
        return [getattr(journals, _) for _ in journals.__all__]

    def domain_map(self, scraper_plugins):
        """
        Generator that yields domains and their associated scrapers

        Arguments:
            scraper_plugins -- list, a list of modules that describe scrapers
        """
        for scraper_module in scraper_plugins:
            try:
                scraper = scraper_module.Scraper()
                scraper_method = scraper.scrape_article
                domains = scraper.domains
            except AttributeError:
                try:
                # TODO Remove once deprecated scrapers are removed
                    # TODO Replace with meaningful exception
                    domains = scraper_module.SCRAPER_DOMAINS
                    scraper_method = scraper_module.scrape
                except AttributeError:
                    logger.warning('Plugin {} is invalid'.format(scraper_module.__name__))
                    continue
            # For each domain found associate the relavent scrape method
            for domain in domains:
                yield domain, scraper_method

    def get_domain(self, url):
        url_parsed = urlparse.urlparse(url)
        return url_parsed.netloc

    def generic_scraper(self):
        """
        Return hard-coded generic scraper
        """
        scrape_method = journals.scrape_meta_tags.scrape
        # TODO Move module setting into base scraper
        return scrape_method.__module__, scrape_method

    def resolve_scraper(self, url):
        """
        Return the scrape method for a given domain
        Do it by domain for now. This might not always work, a full
        url prefix might be needed, but this is cheaper.

        Arguments:
            url -- str, url for article to scrape
        """
        domain = self.get_domain(url)
        try:
            scrape_method = self.domains[domain]
        except KeyError:
            # TODO Was doing resolve_url... what for?
            raise ScraperNotFound("Scraper not found for {}".format(domain))

        # TODO Move into base scraper once deprecated scrapers are removed
        module_path = scrape_method.__module__
        if module_path == 'akorn.scrapers.base':
            module_path = scrape_method.im_class().__module__

        return module_path, scrape_method
