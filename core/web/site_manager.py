import time

from core.configuration_provider import ConfigurationProvider
from core.web.ofm_page_constants import LOGIN
from django.conf import settings
from selenium import webdriver


class SiteManager:
    def __init__(self):
        cfg = ConfigurationProvider()

        self.browser = webdriver.PhantomJS()

        self._handle_aws_display_bug()
        self._handle_phantomjs_bug(cfg)

        self._login_user = cfg.get("credentials", "OFM_USERNAME")
        self._login_password = cfg.get("credentials", "OFM_PASSWORD")

    def login(self):
        self.browser.get(LOGIN)
        self._switch_to_login_div()

        self._insert_login_credentials()
        self._click_login_button()

    def _handle_phantomjs_bug(self, cfg):
        if cfg.get("phantomjs", "PHANTOMJS_PATH"):
            self.browser = webdriver.PhantomJS(executable_path=r'' + cfg.get("phantomjs", "PHANTOMJS_PATH"))

    def _handle_aws_display_bug(self):
        if settings.USE_DISPLAY_FOR_AWS:
            from pyvirtualdisplay import Display
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()

    def _switch_to_login_div(self):
        link_login_account = self.browser.find_element_by_xpath("//div[@id='register_div']//a")
        link_login_account.click()
        time.sleep(1)

    def _insert_login_credentials(self):
        login_field_user = self.browser.find_element_by_xpath("//form[@id='login_form']//input[@id='login']")
        login_field_user.send_keys(self._login_user)
        login_field_password = self.browser.find_element_by_xpath("//form[@id='login_form']//input[@id='password']")
        login_field_password.send_keys(self._login_password)

    def _click_login_button(self):
        login_button = self.browser.find_element_by_xpath("//form[@id='login_form']//button[@id='logingrafikbutton']")
        login_button.click()
        time.sleep(1)
