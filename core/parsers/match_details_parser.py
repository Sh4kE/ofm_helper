import logging

from bs4 import BeautifulSoup
from django.core.exceptions import MultipleObjectsReturned

from core.models import Matchday, Match, MatchTeamStatistics
from core.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)


class MatchDetailsParser(BaseParser):
    def __init__(self, html_source, user, is_home_match):
        super(MatchDetailsParser, self).__init__()
        self.html_source = html_source
        self.user = user
        self.is_home_match = is_home_match

    def parse(self):
        soup = BeautifulSoup(self.html_source, "html.parser")
        return self.parse_html(soup)

    def parse_html(self, soup):  # pylint: disable=too-many-locals
        """
        :param soup: BeautifulSoup of match page
        :return: parsed match
        :rtype: Match
        """

        # we assume to have parsed the season beforehand (via matchday)
        season = Matchday.objects.all()[0].season
        matchday_number = soup.find_all('tbody')[2].find_all('b')[0].get_text().split(',')[1].split('.')[0].strip()
        matchday, _ = Matchday.objects.get_or_create(season=season, number=matchday_number)

        home_team_score, guest_team_score = self._get_scores(soup)
        home_team_name, guest_team_name = self._get_names(soup)
        home_team_strength, guest_team_strength = self._get_strengths(soup)
        home_team_ball_possession, guest_team_ball_possession = self._get_ball_posessions(soup)
        home_team_chances, guest_team_chances = self._get_team_chances(soup)
        home_team_yellow_cards, guest_team_yellow_cards = self._get_yellow_cards(soup)
        home_team_red_cards, guest_team_red_cards = self._get_red_cards(soup)

        existing_match = Match.objects.filter(matchday=matchday, user=self.user)

        if len(existing_match) == 1:
            match = existing_match[0]

            match.home_team_statistics.score = home_team_score
            match.home_team_statistics.team_name = home_team_name
            match.home_team_statistics.strength = home_team_strength
            match.home_team_statistics.ball_possession = home_team_ball_possession
            match.home_team_statistics.chances = home_team_chances
            match.home_team_statistics.yellow_cards = home_team_yellow_cards
            match.home_team_statistics.red_cards = home_team_red_cards
            match.home_team_statistics.save()

            match.guest_team_statistics.score = guest_team_score
            match.guest_team_statistics.team_name = guest_team_name
            match.guest_team_statistics.strength = guest_team_strength
            match.guest_team_statistics.ball_possession = guest_team_ball_possession
            match.guest_team_statistics.chances = guest_team_chances
            match.guest_team_statistics.yellow_cards = guest_team_yellow_cards
            match.guest_team_statistics.red_cards = guest_team_red_cards
            match.guest_team_statistics.save()
        elif not existing_match:
            home_team_stat = MatchTeamStatistics.objects.create(
                score=home_team_score,
                team_name=home_team_name,
                strength=home_team_strength,
                ball_possession=home_team_ball_possession,
                chances=home_team_chances,
                yellow_cards=home_team_yellow_cards,
                red_cards=home_team_red_cards
            )

            guest_team_stat = MatchTeamStatistics.objects.create(
                score=guest_team_score,
                team_name=guest_team_name,
                strength=guest_team_strength,
                ball_possession=guest_team_ball_possession,
                chances=guest_team_chances,
                yellow_cards=guest_team_yellow_cards,
                red_cards=guest_team_red_cards
            )

            match = Match.objects.create(
                matchday=matchday,
                is_home_match=self.is_home_match,
                user=self.user,
                home_team_statistics=home_team_stat,
                guest_team_statistics=guest_team_stat
            )
        else:
            raise MultipleObjectsReturned('There are multiple games on matchday: {}'.format(matchday))

        match.venue = soup.find_all('em')[1].get_text()
        match.save()
        return match

    @staticmethod
    def _get_red_cards(soup):
        red_cards = soup.find_all('table')[5].find_all('tr')[9].find_all('b')
        home_team_red_cards = red_cards[0].get_text().strip()
        guest_team_red_cards = red_cards[1].get_text().strip()
        return home_team_red_cards, guest_team_red_cards

    @staticmethod
    def _get_yellow_cards(soup):
        yellow_cards = soup.find_all('table')[5].find_all('tr')[8].find_all('b')
        home_team_yellow_cards = yellow_cards[0].get_text().strip()
        guest_team_yellow_cards = yellow_cards[1].get_text().strip()
        return home_team_yellow_cards, guest_team_yellow_cards

    @staticmethod
    def _get_team_chances(soup):
        chances = soup.find_all('table')[5].find_all('tr')[7].find_all('b')
        home_team_chances = chances[0].get_text().strip()
        guest_team_chances = chances[1].get_text().strip()
        return home_team_chances, guest_team_chances

    @staticmethod
    def _get_ball_posessions(soup):
        ball_possesions = soup.find_all('table')[5].find_all('tr')[6].find_all('b')
        home_team_ball_possession = ball_possesions[0].get_text().replace(',', '.').replace('%', '').strip()
        guest_team_ball_possession = ball_possesions[1].get_text().replace(',', '.').replace('%', '').strip()
        return home_team_ball_possession, guest_team_ball_possession

    @staticmethod
    def _get_strengths(soup):
        strength = soup.find_all('table')[5].find_all('tr')[5].find_all('b')
        home_team_strength = strength[0].get_text().split(':')[1].strip()
        guest_team_strength = strength[1].get_text().split(':')[1].strip()
        return home_team_strength, guest_team_strength

    @staticmethod
    def _get_names(soup):
        home_team_name = soup.find_all('td', class_='erganz')[0].get_text().strip()
        guest_team_name = soup.find_all('td', class_='erganz')[1].get_text().strip()
        return home_team_name, guest_team_name

    @staticmethod
    def _get_scores(soup):
        match_result = soup.find_all('table')[5].find_all('tr')[0].find_all('td')[3].div.font.get_text()
        home_team_score = match_result.split(':')[0]
        guest_team_score = match_result.split(':')[1]
        return home_team_score, guest_team_score
