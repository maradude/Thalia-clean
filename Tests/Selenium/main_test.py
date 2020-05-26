"""
main script for running selenium tests
"""
from selenium import webdriver

from register_test import register_test
from login_test import login_test, logout_test
from social_test import social_test
from navbar_test import navbar_test
from contact_test import contact_test
from dashboard_test import dashboard_test


def run_tests(driver):
    print("[0] -- Testing navbar, footer and page loading.")
    navbar_test(driver)
    print("[1] -- Testing social media integration.")
    social_test(driver)
    print("[2] -- Testing contact form.")
    contact_test(driver)
    print("[3] -- Testing registration form.")
    register_test(driver)
    print("[4] -- Testing login form.")
    login_test(driver)
    print("[5] -- Testing dashboard.")
    dashboard_test(driver)
    print("[6] -- Testing log out")
    logout_test(driver)
    print("[-] -- Closing driver.")
    driver.close()

print("Testing on Mozilla Firefox webdriver ...")
firefox_ops = webdriver.firefox.options.Options()
firefox_ops.headless = True
run_tests(webdriver.Firefox(options=firefox_ops))
print("Testing on Google Chrome webdriver ...")
chrome_ops = webdriver.chrome.options.Options()
chrome_ops.add_argument("--headless")
run_tests(webdriver.Chrome(options=chrome_ops))
print("Testing successfull")
