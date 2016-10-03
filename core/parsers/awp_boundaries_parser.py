import logging

from bs4 import BeautifulSoup
from core.models import Matchday, AwpBoundaries, Dictionary
from core.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)


class AwpBoundariesParser(BaseParser):
    def __init__(self, html_source, user):
        self.html_source = html_source
        self.user = user

    def parse(self):
        soup = BeautifulSoup(self.html_source, "html.parser")
        return self.parse_html(soup)

    def parse_html(self, soup):
        """
        :param soup: BeautifulSoup of awp boundaries forum page
        :return: parsed awp boundaries
        :rtype: AWP Boundaries object
        """
        matchday = Matchday.objects.all()[0]

        boundaries_raw = soup.find_all('pre', 'bbcode_code')[-1]
        boundaries = boundaries_raw.text.split()[2:]

        try:
            awp_boundaries = AwpBoundaries.get_from_matchday(matchday)
        except Dictionary.DoesNotExist:
            awp_boundaries = AwpBoundaries.create_from_matchday(matchday)

        for i in range(26):
            strength = boundaries[i * 4]
            awp = boundaries[i * 4 + 1]
            awp_boundaries[strength] = awp

        return awp_boundaries
