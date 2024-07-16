from bs4 import BeautifulSoup
from urllib.parse import quote

from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..engine import SearchEngine
from ..utils import quote_url, ProxyError


def _selectors(element):
    """Returns the appropriate CSS selector."""
    selectors = {
        'next': 'footer a[href][aria-label="Next page"]'
    }
    return selectors[element]


class Google(SearchEngine):
    """Searches google.com"""

    def __init__(self, proxy=PROXY, timeout=TIMEOUT, logger=None, *args, **kwargs):
        super(Google, self).__init__(proxy, timeout, logger)
        self._base_url = 'https://www.google.com'
        self._delay = (2, 6)

        self.set_headers({'User-Agent': FAKE_USER_AGENT})

    def _first_page(self):
        """Returns the initial page and query."""
        url = u'{}/search?q={}'.format(self._base_url, quote_url(self._query, ''))
        response = self._get_page(url)
        bs = BeautifulSoup(response.html, "html.parser")

        url = bs.select_one('noscript a')['href']
        url = u'{}/search?{}'.format(self._base_url, url)
        response = self._get_page(url)
        bs = BeautifulSoup(response.html, "html.parser")

        inputs = {i['name']: i.get('value') for i in bs.select('form input[name]') if i['name'] != 'btnI'}
        inputs['q'] = quote_url(self._query, '')
        # web interface language codes (hl=en), search language codes (lr=lang_en)
        # region (gl=us), results per page (num=100)
        inputs['lr'] = 'lang_{}'.format('en')
        inputs['gl'] = 'us'
        inputs['hl'] = 'en'
        inputs['num'] = '100'
        url = u'{}/search?{}'.format(self._base_url, '&'.join([k + '=' + (v or '') for k, v in inputs.items()]))

        return {'url': url, 'data': None}

    def _next_page(self, tags):
        """Returns the next page URL and post data (if any)"""
        # tags = self._check_consent(tags)
        tag = tags.select_one(_selectors('next'))
        next_page = self._get_tag_item(tag, 'href')

        url = None
        if next_page:
            url = self._base_url + next_page
        return {'url': url, 'data': None}

    def _check_consent(self, page):
        """Checks if cookies consent is required"""
        url = 'https://consent.google.com/save'
        bs = BeautifulSoup(page.html, "html.parser")
        consent_form = bs.select('form[action="{}"] input[name]'.format(url))
        if consent_form:
            data = {i['name']: i.get('value') for i in consent_form if i['name'] not in ['set_sc', 'set_aps']}
            page = self._get_page(url, data)
        return page

    def _get_page(self, page, data=None):
        """Gets pagination links."""
        page = super(Google, self)._get_page(page, data)
        if not self._is_ok(page):
            raise ProxyError('HTTP error: {}'.format(page.http))
        page = self._check_consent(page)
        return page
