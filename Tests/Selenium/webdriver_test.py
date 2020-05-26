from selenium import webdriver
from selenium.webdriver.common.keys import Keys

"""
Snippet of code from selenium website, run this while connected to the
internet to test wether webdriver is configured properly
"""


def test(driver):
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source


if __name__ == "__main__":
    # Test chrome and firefox drivers,
    # webdrivers must be installed on system path for this to work
    driver = webdriver.Chrome()
    test(driver)
    driver.close()

    driver = webdriver.Firefox()
    test(driver)
    driver.close()
