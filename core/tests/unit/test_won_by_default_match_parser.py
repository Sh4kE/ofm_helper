import os

from django.test import TestCase

from core.factories.core_factories import MatchdayFactory
from core.models import Match, MatchTeamStatistics
from core.parsers.won_by_default_match_parser import WonByDefaultMatchParser
from users.factories.users_factories import OFMUserFactory

TESTDATA_PATH = 'core/tests/assets'


class WonByDefaultMatchParserTest(TestCase):
    def setUp(self):
        testdata = open(os.path.join(TESTDATA_PATH, 'home_match_won_by_default.html'), encoding='utf8')
        MatchdayFactory.create(number=1)
        self.user = OFMUserFactory.create()

        self.parser = WonByDefaultMatchParser(testdata, self.user)
        self.match_stat = self.parser.parse()

    def test_match_parser_general_informations(self):
        self.assertEquals(type(self.match_stat), Match)
        self.assertEquals(self.match_stat.matchday.number, 1)
        self.assertEquals(self.match_stat.user, self.user)
        self.assertEquals(self.match_stat.match_type, 'L')
        self.assertEquals(self.match_stat.venue, '')

    def test_match_home_team_statistics(self):
        self.assertEquals(type(self.match_stat.home_team_statistics), MatchTeamStatistics)
        self.assertEquals(self.match_stat.home_team_statistics.score, '3')
        self.assertEquals(self.match_stat.home_team_statistics.team_name, 'BSC Wittenau')
        self.assertEquals(self.match_stat.home_team_statistics.strength, '59')
        self.assertEquals(self.match_stat.home_team_statistics.ball_possession, 100)
        self.assertEquals(self.match_stat.home_team_statistics.chances, 0)
        self.assertEquals(self.match_stat.home_team_statistics.yellow_cards, 0)
        self.assertEquals(self.match_stat.home_team_statistics.red_cards, 0)

    def test_match_guest_team_statistics(self):
        self.assertEquals(type(self.match_stat.guest_team_statistics), MatchTeamStatistics)
        self.assertEquals(self.match_stat.guest_team_statistics.score, '0')
        self.assertEquals(self.match_stat.guest_team_statistics.team_name, 'Borussia Paniermehl')
        self.assertEquals(self.match_stat.guest_team_statistics.strength, '0')
        self.assertEquals(self.match_stat.guest_team_statistics.ball_possession, 0)
        self.assertEquals(self.match_stat.guest_team_statistics.chances, 0)
        self.assertEquals(self.match_stat.guest_team_statistics.yellow_cards, 0)
        self.assertEquals(self.match_stat.guest_team_statistics.red_cards, 0)