from selenium import webdriver

import util

"""
Test navbar works properly (redirects to correct pages and displays on all pages)
as well as that all pages load successfully and display the navbar and social media
links
"""


def test_navbar_redirect(driver, navbar_item, page):
    """
    test a specific navbar link [xpath] loads page '/page/' and displays navbar
    """
    # Navigate to navbar page
    navbar_link = driver.find_element_by_class_name(navbar_item)
    driver.execute_script("arguments[0].click();", navbar_link)

    # Test about page redirect and page loaded
    util.page_wait()
    if page == "/":
        assert driver.current_url == "http://127.0.0.1:5000/"
    else:
        assert driver.current_url == ("http://127.0.0.1:5000/" + page + "/")
    # Check page has loaded properly and that navbar is displayed
    driver.find_element_by_id("navbarBasicExample")
    # Check footer with links loaded
    driver.find_element_by_class_name("footer")
    driver.find_element_by_class_name("fa-facebook")
    driver.find_element_by_class_name("fa-twitter")


def navbar_test(driver):
    driver.get("http://127.0.0.1:5000")
    driver.implicitly_wait(5)  # seconds
    # Make sure we're accessing the correct webpage
    assert "Thalia" in driver.title

    test_navbar_redirect(driver, "navbar-about", "about")
    test_navbar_redirect(driver, "navbar-contact", "contact")
    test_navbar_redirect(driver, "navbar-home", "/")
    test_navbar_redirect(driver, "navbar-logo", "/")


if __name__ == "__main__":
    driver = webdriver.Firefox()
    navbar_test(driver)
    driver.close()
    driver = webdriver.Chrome()
    navbar_test(driver)
    driver.close()
