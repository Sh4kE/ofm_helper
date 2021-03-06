import logging

from bs4 import BeautifulSoup

from core.models import Match, MatchStadiumStatistics, StadiumLevel, StadiumLevelItem
from core.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)


class StadiumStatisticsParser(BaseParser):
    def __init__(self, html_source, user, match):
        super(StadiumStatisticsParser, self).__init__()
        self.html_source = html_source
        self.user = user
        self.match = match

    def parse(self):
        soup = BeautifulSoup(self.html_source, "html.parser")
        return self.parse_html(soup)

    def parse_html(self, soup):
        """
        :param soup: BeautifulSoup of stadium environment page
        :return: parsed match stadium statidtics
        :rtype: MatchStadiumStatistics
        """

        last_stadium_level = None
        if self._has_home_matches():
            # only consider matches statistics BEFORE current match
            last_home_match = [match for match in (self._last_home_matches()) if
                               match.matchday.number <= self.match.matchday.number][0]
            last_stadium_level = self._last_stadium_level(last_home_match)

        light_row, screen_row, security_row, parking_row = self._get_stadium_items(soup)

        light = self._create_stadium_level_item_from_row(light_row)
        screen = self._create_stadium_level_item_from_row(screen_row)
        security = self._create_stadium_level_item_from_row(security_row)
        parking = self._create_stadium_level_item_from_row(parking_row)

        if self._is_under_construction(light_row) and last_stadium_level:
            light = last_stadium_level.light

        if self._is_under_construction(screen_row) and last_stadium_level:
            screen = last_stadium_level.screen

        if self._is_under_construction(security_row) and last_stadium_level:
            security = last_stadium_level.security

        if self._is_under_construction(parking_row) and last_stadium_level:
            parking = last_stadium_level.parking

        stadium_level, _ = StadiumLevel.objects.get_or_create(
            light=light,
            screen=screen,
            security=security,
            parking=parking
        )

        match_stadium_stat, _ = MatchStadiumStatistics.objects.get_or_create(
            match=self.match,
            level=stadium_level
        )

        return match_stadium_stat

    @staticmethod
    def _has_last_stadium_level(last_home_match):
        return MatchStadiumStatistics.objects.filter(match=last_home_match).count > 0

    @staticmethod
    def _last_stadium_level(last_home_match):
        last_stadium_level = MatchStadiumStatistics.objects.filter(match=last_home_match)[0].level
        return last_stadium_level

    def _has_home_matches(self):
        return Match.objects.filter(user=self.user, stadium_statistics__isnull=False).count() > 0

    def _last_home_matches(self):
        last_home_matches = Match.objects.filter(user=self.user, stadium_statistics__isnull=False).order_by('matchday')
        return last_home_matches

    @staticmethod
    def _get_stadium_items(soup):
        items = soup.find('table', id='stadiumExtra').tbody.find_all('tr')
        return items[0], items[1], items[2], items[3]

    @staticmethod
    def _is_under_construction(stadium_attribute):
        return stadium_attribute.find_all('td')[1].img is not None and \
               'underconst' in stadium_attribute.find_all('td')[1].img['src']

    @staticmethod
    def _create_stadium_level_item_from_row(row):
        stadium_level_item, _ = StadiumLevelItem.objects.get_or_create(
            current_level=row.find_all('td')[2].span.get_text(),
            value=BaseParser.strip_euro_sign(row.find_all('td')[4].span.get_text().replace('.', '').strip()),
            daily_costs=BaseParser.strip_euro_sign(row.find_all('td')[5].span.get_text().replace('.', '').strip())
        )

        return stadium_level_item
