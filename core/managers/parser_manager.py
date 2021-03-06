import os
import subprocess

from bs4 import BeautifulSoup

from core.managers.site_manager import OFMTransferSiteManager
from core.models import ParsingSetting, Matchday
from core.parsers.awp_boundaries_parser import AwpBoundariesParser
from core.parsers.basic_match_row_parser import BasicMatchRowParser
from core.parsers.finances_parser import FinancesParser
from core.parsers.match_details_parser import MatchDetailsParser
from core.parsers.matchday_parser import MatchdayParser
from core.parsers.ofm_helper_version_parser import OfmHelperVersionParser
from core.parsers.player_statistics_parser import PlayerStatisticsParser
from core.parsers.players_parser import PlayersParser
from core.parsers.stadium_stand_statistics_parser import StadiumStandStatisticsParser
from core.parsers.stadium_statistics_parser import StadiumStatisticsParser
from core.web.ofm_page_constants import Constants
from ofm_helper.common_settings import BASE_DIR


class ParserManager:
    def __init__(self):
        self.parsed_matchday = None
        self.players_already_parsed = False

    def parse_all_ofm_data(self, site_manager):
        parsing_setting, _ = ParsingSetting.objects.get_or_create(user=site_manager.user)

        self.parsed_matchday = self.parse_matchday(site_manager)
        if parsing_setting.parsing_chain_includes_player_statistics:
            self.parse_players(site_manager)
            self.players_already_parsed = True
            self.parse_player_statistics(site_manager)
        if parsing_setting.parsing_chain_includes_awp_boundaries:
            self.parse_awp_boundaries(site_manager)
        if parsing_setting.parsing_chain_includes_finances:
            self.parse_finances(site_manager)
        if parsing_setting.parsing_chain_includes_matches:
            self.parse_all_matches(site_manager, parsing_setting)
        if parsing_setting.parsing_chain_includes_transfers:
            self.parse_transfers(site_manager, [self.parsed_matchday])

        self.reset_parsing_flags()

    def reset_parsing_flags(self):
        self.parsed_matchday = None
        self.players_already_parsed = False

    @staticmethod
    def parse_ofm_version(site_manager):
        site_manager.jump_to_frame(Constants.GitHub.LATEST_RELEASE)
        version_parser = OfmHelperVersionParser(site_manager.browser.page_source)
        return version_parser.parse()

    @staticmethod
    def parse_matchday(site_manager):
        site_manager.jump_to_frame(Constants.HEAD)
        matchday_parser = MatchdayParser(site_manager.browser.page_source)
        return matchday_parser.parse()

    def parse_players(self, site_manager):
        if not self.parsed_matchday:
            self.parsed_matchday = self.parse_matchday(site_manager)
        site_manager.jump_to_frame(Constants.Team.PLAYERS)
        players_parser = PlayersParser(site_manager.browser.page_source, site_manager.user, self.parsed_matchday)
        return players_parser.parse()

    def parse_player_statistics(self, site_manager):
        if not self.players_already_parsed:
            self.parse_players(site_manager)
        site_manager.jump_to_frame(Constants.Team.PLAYER_STATISTICS)
        player_stat_parser = PlayerStatisticsParser(site_manager.browser.page_source, site_manager.user,
                                                    self.parsed_matchday)
        return player_stat_parser.parse()

    def parse_awp_boundaries(self, site_manager):
        if not self.parsed_matchday:
            self.parsed_matchday = self.parse_matchday(site_manager)
        site_manager.jump_to_frame(Constants.AWP_BOUNDARIES)
        awp_boundaries_parser = AwpBoundariesParser(site_manager.browser.page_source, site_manager.user,
                                                    self.parsed_matchday)
        return awp_boundaries_parser.parse()

    def parse_finances(self, site_manager):
        if not self.parsed_matchday:
            self.parsed_matchday = self.parse_matchday(site_manager)
        site_manager.jump_to_frame(Constants.Finances.OVERVIEW)
        finances_parser = FinancesParser(site_manager.browser.page_source, site_manager.user, self.parsed_matchday)
        return finances_parser.parse()

    def parse_all_matches(self, site_manager, parsing_setting=None):
        if not self.parsed_matchday:
            self.parsed_matchday = self.parse_matchday(site_manager)
        site_manager.jump_to_frame(Constants.League.MATCH_SCHEDULE)
        soup = BeautifulSoup(site_manager.browser.page_source, "html.parser")

        rows = soup.find(id='table_head').find_all('tr')
        for row in rows:
            if row.has_attr("class"):  # exclude table header
                self._parse_single_match(site_manager, row, parsing_setting)

    def _parse_single_match(self, site_manager, row, parsing_setting):
        is_home_match = "black" in row.find_all('td')[1].a.get('class')
        match_report_image = row.find_all('img', class_='changeMatchReportImg')

        if match_report_image and self._should_parse_match_details(parsing_setting, self._is_current_matchday(row)):
            # match took place and should be parsed in detail
            link_to_match = match_report_image[0].find_parent('a')['href']
            if "spielbericht" in link_to_match:
                match = self.parse_match_details(is_home_match, link_to_match, site_manager)

                if is_home_match and self._is_current_matchday(row) and \
                   self._should_parse_stadium_statistics(parsing_setting):
                    self.parse_stadium_statistics(site_manager, match)

                return match
        else:
            # match was won by default
            # or match details should not be parsed
            # or match is scheduled, but did not take place yet
            match = BasicMatchRowParser(row, site_manager.user).parse()

            if is_home_match and self._is_current_matchday(row) and \
               self._should_parse_stadium_statistics(parsing_setting):
                self.parse_stadium_statistics(site_manager, match)

            return match

    @staticmethod
    def parse_match_details(is_home_match, link_to_match, site_manager):
        site_manager.jump_to_frame(Constants.BASE + link_to_match)
        match_details_parser = MatchDetailsParser(site_manager.browser.page_source,
                                                  site_manager.user, is_home_match)
        match = match_details_parser.parse()
        return match

    def _is_current_matchday(self, row):
        return int(row.find_all('td')[0].get_text()) == self.parsed_matchday.number

    @staticmethod
    def _should_parse_match_details(parsing_setting, is_current_matchday):
        if parsing_setting:
            return parsing_setting.parsing_chain_includes_match_details and \
                   (not parsing_setting.parsing_chain_includes_match_details_only_for_current_matchday or
                    is_current_matchday)
        return True

    @staticmethod
    def _should_parse_stadium_statistics(parsing_setting):
        if parsing_setting:
            return parsing_setting.parsing_chain_includes_stadium_details
        return True

    @staticmethod
    def parse_stadium_statistics(site_manager, match):
        site_manager.jump_to_frame(Constants.Stadium.ENVIRONMENT)
        stadium_statistics_parser = StadiumStatisticsParser(site_manager.browser.page_source,
                                                            site_manager.user, match)
        stadium_statistics_parser.parse()

        site_manager.jump_to_frame(Constants.Stadium.OVERVIEW)
        stadium_stand_stat_parser = StadiumStandStatisticsParser(site_manager.browser.page_source,
                                                                 site_manager.user, match)
        stadium_stand_stat_parser.parse()

    def parse_transfers(self, site_manager, matchdays=None):
        if not self.parsed_matchday:
            self.parsed_matchday = self.parse_matchday(site_manager)

        if not matchdays:  # get all data until current matchday
            current_season = self.parsed_matchday.season
            matchdays = []

            for matchday_number in range(self.parsed_matchday.number + 1):
                matchday, _ = Matchday.objects.get_or_create(
                                number=matchday_number,
                                season=current_season
                              )
                matchdays.append(matchday)

        site_manager = OFMTransferSiteManager(site_manager.user)
        site_manager.download_transfer_excels(matchdays)
        site_manager.kill_browser()

        self._convert_transfer_data()

    @staticmethod
    def _convert_transfer_data():
        data_folder = os.path.join(BASE_DIR, 'ofm_transfer_data')
        script_file = os.path.join(data_folder, 'convert_xls_to_csv.sh')
        subprocess.call([script_file], cwd=data_folder)
