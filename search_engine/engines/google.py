import re
from bs4 import BeautifulSoup
from urllib.parse import quote

from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..engine import SearchEngine
from ..utils import quote_url, ProxyError


class Google(SearchEngine):
    """Searches google.com"""

    class Selectors:
        # Organic Search Results
        ORGANIC_RESULTS = "div.Gx5Zad.fP1Qef.xpd.EtOod.pkphOe"
        ORGANIC_RESULT_SECTION = 'div.egMi0.kCrYT'
        ORGANIC_RESULT_DESCRIPTION = 'div.BNeawe.s3v9rd.AP7Wnd'
        ORGANIC_RESULT_EXTRA_DATA = 'span.r0bn4c.rQMQod'

    def __init__(self, proxy=PROXY, timeout=TIMEOUT, logger=None, *args, **kwargs):
        super(Google, self).__init__(proxy, timeout, logger)
        self._base_url = 'https://www.google.com'
        self._delay = (2, 6)

        self.set_headers({'User-Agent': FAKE_USER_AGENT})

    def _selectors(self, element):
        """Returns the appropriate CSS selector."""
        selectors = {
            # Organic Search Results
            'ORGANIC_RESULTS': "div.Gx5Zad.fP1Qef.xpd.EtOod.pkphOe",
            'ORGANIC_RESULT_SECTION': 'div.BNeawe.vvjwJb.AP7Wnd',
            'ORGANIC_RESULT_DESCRIPTION': 'div.BNeawe.s3v9rd.AP7Wnd',
            'ORGANIC_RESULT_EXTRA_DATA': 'span.r0bn4c.rQMQod',

            # next page selector
            'next': 'footer a[href][aria-label="Next page"]'
        }
        return selectors[element]

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
        tag = tags.select_one(self._selectors('next'))
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

    def _is_availability(self, text):
        if not text:
            return False
        availability_pattern = re.compile(r'(In\sstock|Out\sOf\sStock|Available|Unavailable|Pre\sOrder|Coming\sSoon)')
        return bool(availability_pattern.search(text))

    def _is_currency(self, text):
        if not text:
            return False
        currency_pattern = re.compile(r'[$€£¥₹₽¢₩₪฿₫₴₦₲₵₢₡₸₭₮₠₣₧]')
        return bool(currency_pattern.search(text))

    def _is_date(self, text):
        if not text:
            return False
        date_pattern = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\s\d{4}\b')
        return bool(date_pattern.search(text))

    def _is_duration(self, text):
        """Match time patterns like HH:MM:SS or MM:SS in the given text."""
        if not text:
            return False
        time_pattern = re.compile(r'\b\d{1,2}:\d{2}(:\d{2})?\b')
        return bool(time_pattern.search(text))

    def _extract_extra_data(self, extra_data_tags):
        price, date, duration, availability, rating = None, None, None, None, None
        is_rating, is_missing = False, False

        for tag in extra_data_tags:
            extra_data = tag.get_text(strip=True)
            if self._is_currency(extra_data):
                price = extra_data
            elif self._is_date(extra_data):
                date = extra_data
            elif self._is_duration(extra_data):
                duration = extra_data
            elif self._is_availability(extra_data):
                availability = extra_data
            elif is_rating:
                rating = extra_data
            is_rating = 'Rating' in extra_data

        return price, date, duration, availability, rating

    def _get_clean_description(self, description_tag, extra_data):
        if not description_tag:
            return None
        description = description_tag.get_text(strip=True) if description_tag else ''
        if description:
            for data in extra_data:
                if data:
                    description = description.replace(data, '').strip()

            return description.replace(
                '·', ''
            ).replace(
                'Duration:', ''
            ).replace(
                'Price:', ''
            ).replace(
                'Date:', ''
            ).replace(
                'Availability:', ''
            ).replace(
                'Rating', ''
            ).replace(
                'Posted:', ''
            ).strip()

        return None
    def get_organic_results(self, soup):
        """Parses the search results."""
        organic_results = []

        for result in soup.select(self.Selectors.ORGANIC_RESULTS):
            section_tag = result.select_one(self.Selectors.ORGANIC_RESULT_SECTION)
            description_tag = result.select(self.Selectors.ORGANIC_RESULT_DESCRIPTION)
            main_description_tag = description_tag[1] if len(description_tag) > 1 else None
            has_media = result.select_one('img') is not None
            if not section_tag:
                continue

            url = section_tag.select_one('a')['href'][7:].split('&sa')[0]
            title = section_tag.select_one('h3').get_text(strip=True)

            extra_data_tags = result.select(self.Selectors.ORGANIC_RESULT_EXTRA_DATA)
            extra_data = self._extract_extra_data(extra_data_tags)
            price, date, duration, availability, rating = extra_data

            description = self._get_clean_description(main_description_tag, extra_data)

            details, missing = None, None
            if description_tag and len(description_tag) > 2:
                extra_description = description_tag[2].get_text(strip=True)
                if "Missing" in extra_description:
                    missing = re.compile(r'(?:Missing:|Show results with:)\s*(\w+)').search(extra_description).group(1)
                else:
                    details = extra_description

            result_dict = {
                'title': title,
                'url': url,
                'description': description,
                'price': price,
                'date': date,
                'duration': duration,
                'missing': missing,
                'rating': rating,
                'availability': availability,
                'extra_details': details
            }

            result_dict = {k: v for k, v in result_dict.items() if v}

            organic_results.append(result_dict)

        return organic_results
