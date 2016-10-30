import os

from django.test import TestCase

from core.factories.core_factories import MatchFactory, StadiumLevelItemFactory, StadiumLevelFactory, \
    MatchStadiumStatisticsFactory, MatchdayFactory
from core.models import MatchStadiumStatistics, StadiumLevel, StadiumLevelItem, Match
from core.parsers.stadium_statistics_parser import StadiumStatisticsParser
from users.factories.users_factories import OFMUserFactory

TESTDATA_PATH = 'core/tests/assets'


class StadiumStatisticsParserTest(TestCase):
    def setUp(self):
        testdata = open(os.path.join(TESTDATA_PATH, 'stadium_environment.html'), encoding='utf8')
        self.user = OFMUserFactory.create(username='DouglasAdams')
        matchday2 = MatchdayFactory.create(number=2)
        self.match2 = MatchFactory.create(user=self.user, matchday=matchday2)

        self.parser = StadiumStatisticsParser(testdata, self.user)

    def test_stadium_environment_parser_contains_correct_types(self):
        stadium_stat = self.parser.parse()
        self.assertEquals(type(stadium_stat), MatchStadiumStatistics)
        self.assertEquals(stadium_stat.match, self.match2)
        self.assertEquals(type(stadium_stat.level), StadiumLevel)
        self.assertEquals(type(stadium_stat.level.light), StadiumLevelItem)
        self.assertEquals(type(stadium_stat.level.screen), StadiumLevelItem)
        self.assertEquals(type(stadium_stat.level.security), StadiumLevelItem)
        self.assertEquals(type(stadium_stat.level.parking), StadiumLevelItem)

    def test_stadium_environment_parser_contains_correct_light_data(self):
        stadium_stat = self.parser.parse()
        self.assertEquals(stadium_stat.level.light.current_level, '1')
        self.assertEquals(stadium_stat.level.light.value, '20')
        self.assertEquals(stadium_stat.level.light.daily_costs, '10')

    def test_stadium_environment_parser_takes_old_screen_data_while_in_construction_if_older_stat_exists(self):
        matchday1 = MatchdayFactory.create(number=1)
        last_level = StadiumLevelFactory.create()
        match1 = MatchFactory.create(user=self.user, matchday=matchday1)
        MatchStadiumStatisticsFactory.create(match=match1, level=last_level)
        stadium_stat = self.parser.parse()

        self.assertEquals(stadium_stat.level.screen.current_level, 0)
        self.assertEquals(stadium_stat.level.screen.value, 0)
        self.assertEquals(stadium_stat.level.screen.daily_costs, 0)

    def test_stadium_environment_parser_takes_new_screen_data_while_in_construction_but_no_older_stat_exists(self):
        stadium_stat = self.parser.parse()
        self.assertEquals(stadium_stat.level.screen.current_level, '1')
        self.assertEquals(stadium_stat.level.screen.value, '500000')
        self.assertEquals(stadium_stat.level.screen.daily_costs, '7500')

    def test_stadium_environment_parser_contains_correct_security_data(self):
        stadium_stat = self.parser.parse()
        self.assertEquals(stadium_stat.level.security.current_level, '2')
        self.assertEquals(stadium_stat.level.security.value, '2000')
        self.assertEquals(stadium_stat.level.security.daily_costs, '150')

    def test_stadium_environment_parser_contains_correct_parking_data(self):
        stadium_stat = self.parser.parse()
        self.assertEquals(stadium_stat.level.parking.current_level, '3')
        self.assertEquals(stadium_stat.level.parking.value, '42')
        self.assertEquals(stadium_stat.level.parking.daily_costs, '42')