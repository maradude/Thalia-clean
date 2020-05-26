"""
Utilities for UI selenium tests
"""
from time import sleep
from selenium.webdriver.common.keys import Keys

# Credentials for testing
uname = "selenium_test0"
# Password must comply with website restrictions(be over 8 chars with number and symbol)
pwd = "selenium_test_pwd0!"

# Correct url's for Thalia social media
fb_url = "https://www.facebook.com/Thalia-Backtester-101459001526511/"
twitter_url = "https://twitter.com/Thalia99627941"

# Test message for contact form
email = "selenium_test_email0"
title = "selenium_test_title0"
contents = "selenium_test_contents0"

# Test parameters for portfolios
p_name = "Selenium_test_portfolio0"
cont_amount = "10"
init_balance = "1000"


def page_wait():
    """
    wait for page to fully load.(Built in implicit wait does not work
    when checking redirects to specific addresses as there is no element
    missing but rather an incorrect value)
    """
    sleep(2)


def input_clear(element):
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(Keys.DELETE)
