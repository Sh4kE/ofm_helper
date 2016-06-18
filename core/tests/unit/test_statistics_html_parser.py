import os

from django.test import TestCase

from core.models import PlayerStatistics, Player
from core.parsers.player_statistics_html_parser import PlayerStatisticsHtmlParser

TESTDATA_PATH = 'core/tests/assets'


class StatisticsHtmlParserTest(TestCase):
    def setUp(self):
        testdata = open(os.path.join(TESTDATA_PATH, 'player_statistics.html'), encoding='utf8')
        parser = PlayerStatisticsHtmlParser()
        parser.url = testdata
        self.player_stat_list = parser.parse()
        self.first_player_stat = self.player_stat_list[0]

    def test_parsed_player_stat_contains_all_foreign_keys(self):
        self.assertEquals(type(self.first_player_stat), PlayerStatistics)
        self.assertEquals(type(self.first_player_stat.player), Player)

    def test_parsed_player_stat_contains_all_fields(self):
        self.assertEquals(12, len(self.player_stat_list))
        self.assertEquals('TW', self.first_player_stat.player.position)
        self.assertEquals('Chrístos Tsigas', self.first_player_stat.player.name)
        self.assertEquals('15', self.first_player_stat.strength)
        self.assertEquals('47', self.first_player_stat.freshness)
        self.assertEquals('29', self.first_player_stat.games_in_season)

    def test_parsed_player_stat_contains_correct_scored_goals(self):
        player_stat = self.player_stat_list[3]
        self.assertEquals('4', player_stat.goals_in_season)

    def test_parsed_player_stat_contains_correct_tacklings(self):
        self.assertEquals('32', self.first_player_stat.won_tacklings_in_season)
        self.assertEquals('36', self.first_player_stat.lost_tacklings_in_season)
        self.assertEquals('37', self.first_player_stat.won_friendly_tacklings_in_season)
        self.assertEquals('5', self.first_player_stat.lost_friendly_tacklings_in_season)

    def test_parsed_player_stat_contains_correct_cards_received(self):
        player_stat = self.player_stat_list[1]
        self.assertEquals('3', player_stat.yellow_cards_in_season)
        self.assertEquals('1', player_stat.red_cards_in_season)

    def test_parsed_player_stat_contains_correct_player_enhancement_data(self):
        self.assertEquals('8599', self.first_player_stat.ep)
        self.assertEquals('13227', self.first_player_stat.tp)
        self.assertEquals('10422', self.first_player_stat.awp)

    def test_parsed_player_stat_contains_correct_equity(self):
        self.assertEquals('16015782', self.first_player_stat.equity)
