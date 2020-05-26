from selenium import webdriver

import util

"""
Tests for social media links and integrations
"""


def social_test(driver):
    driver.get("http://127.0.0.1:5000")
    driver.implicitly_wait(5)  # seconds

    # Make sure we're accessing the correct webpage
    assert "Thalia" in driver.title

    fb_link = driver.find_element_by_class_name("facebook-link")
    driver.execute_script("arguments[0].click();", fb_link)
    # fb_link.click()

    # Test redirect
    util.page_wait()
    assert util.fb_url == driver.current_url

    driver.get("http://127.0.0.1:5000")
    twitter_link = driver.find_element_by_class_name("twitter-link")
    driver.execute_script("arguments[0].click();", twitter_link)
    # twitter_link.click()

    # Test redirect
    util.page_wait()
    assert util.twitter_url == driver.current_url


if __name__ == "__main__":
    driver = webdriver.Firefox()
    social_test(driver)
    driver.close()

    driver = webdriver.Chrome()
    social_test(driver)
    driver.close()
