import os

from bs4 import BeautifulSoup
from time import sleep
from random import uniform as random_uniform

from .http_client import HttpClient
from . import utils
from . import config as cfg


class SearchEngine(object):
    """The base class for all Search Engines."""

    def __init__(self, proxy=cfg.PROXY, timeout=cfg.TIMEOUT, logger=None):
        """
        :param str proxy: optional, a proxy server
        :param int timeout: optional, the HTTP timeout
        """
        self._http_client = HttpClient(timeout, proxy)
        self._delay = (1, 4)
        self._query = ''

        self.is_banned = False  # Indicates if a ban occurred
        self.logger = logger

    def _first_page(self):
        """Returns the initial page URL."""
        raise NotImplementedError()

    def _next_page(self, tags):
        """Returns the next page URL and post data."""
        raise NotImplementedError()

    def _get_page(self, page, data=None):
        """Gets pagination links."""
        if data:
            return self._http_client.post(page, data)
        return self._http_client.get(page)

    def _is_ok(self, response):
        """Checks if the HTTP response is 200 OK."""
        self.is_banned = response.http in [403, 429, 503]

        if response.http == 200:
            return True

        return False

    def _get_tag_item(self, tag, item):
        """Returns Tag attributes."""
        if not tag:
            return u''
        return tag.text if item == 'text' else tag.get(item, u'')

    def set_headers(self, headers):
        """Sets HTTP headers.

        :param headers: dict The headers
        """
        self._http_client.session.headers.update(headers)

    def search(self, query, q_id, pages=cfg.SEARCH_ENGINE_RESULTS_PAGES):
        """Queries the search engine, goes through the pages and collects the results.

        :param query: str The search query
        :param q_id: int The query id
        :param pages: int Optional, the maximum number of results pages to search
        :returns SearchResults object
        """
        self.logger.info(
            "Searching for query",
            query_id=q_id, query=query[:10] + '...',
            engine=self.__class__.__name__
        )
        self._query = utils.decode_bytes(query)
        request = self._first_page()

        for page in range(1, pages + 1):
            try:
                response = self._get_page(request['url'], request['data'])
                if not self._is_ok(response):
                    raise utils.ProxyError('HTTP error: {}'.format(response.http))

                soup = BeautifulSoup(response.html, "html.parser")

                for script in soup.find_all('script'):
                    script.decompose()

                with open(f'data/{self.__class__.__name__.lower()}/{q_id}.html', 'w') as f:
                    f.write(soup.prettify())

                request = self._next_page(soup)
                if not request['url']:
                    break

                if page < pages:
                    sleep(random_uniform(*self._delay))

            except KeyboardInterrupt:
                break
