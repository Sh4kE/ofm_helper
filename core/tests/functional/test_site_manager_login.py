import unittest

from django.conf import settings

from core.web.ofm_page_constants import Constants
from core.web.site_manager import SiteManager


class LoginTest(unittest.TestCase):
    def setUp(self):
        self.site_manager = SiteManager()
        self.site_manager.login()

    def tearDown(self):
        self.site_manager.browser.quit()
        if settings.USE_DISPLAY_FOR_AWS:
            self.site_manager.display.stop()

    def test_login(self):
        self.assertIn("OFM", self.site_manager.browser.title)
        self.site_manager.browser.get(Constants.HEAD)
        self.assertIn("Spieltag", self.site_manager.browser.page_source)
        self.assertIn("Saison", self.site_manager.browser.page_source)
        self.assertIn("Team", self.site_manager.browser.page_source)
        self.assertIn("Liga", self.site_manager.browser.page_source)