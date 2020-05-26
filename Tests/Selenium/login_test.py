from selenium import webdriver

import util

"""
Test logging in as default user 'asdf' on Thalia website
"""


def login_test(driver):
    driver.get("http://127.0.0.1:5000")
    driver.implicitly_wait(5)  # seconds
    # Make sure we're accessing the correct webpage
    assert "Thalia" in driver.title
    # Check reg form displayed
    driver.find_element_by_class_name("registration-form")
    # Navigate to log in form
    login_button = driver.find_element_by_class_name("login-btn")
    driver.execute_script("arguments[0].click();", login_button)

    # Test redirect
    util.page_wait()
    assert "http://127.0.0.1:5000/login/" == driver.current_url

    # Fill in login form
    uname_field = driver.find_element_by_id("username")
    uname_field.send_keys(util.uname)
    pwd_field = driver.find_element_by_id("password")
    pwd_field.send_keys(util.pwd)

    submit = driver.find_element_by_class_name("signin-btn")
    driver.execute_script("arguments[0].click();", submit)

    # Check log in successfull
    disabled_login_button = driver.find_element_by_class_name("greeting")

    assert "http://127.0.0.1:5000/" == driver.current_url
    assert ("Hi " + util.uname + "!") in disabled_login_button.get_attribute(
        "innerHTML"
    )

    # Test twitter feed integration
    driver.find_element_by_class_name("twitter-timeline")


def logout_test(driver):
    driver.get("http://127.0.0.1:5000")
    driver.implicitly_wait(2)  # seconds
    # Make sure we're accessing the correct webpage
    assert "Thalia" in driver.title

    # Test we are logged in
    disabled_login_button = driver.find_element_by_class_name("greeting")
    assert ("Hi " + util.uname + "!") in disabled_login_button.get_attribute(
        "innerHTML"
    )

    # Click logout button
    logout_button = driver.find_element_by_class_name("logout-btn")
    driver.execute_script("arguments[0].click();", logout_button)

    # Check we have logged out and been redirected
    util.page_wait()
    driver.find_element_by_class_name("login-btn")
    assert "http://127.0.0.1:5000/" == driver.current_url
    util.page_wait()


if __name__ == "__main__":
    from register_test import register_test

    driver = webdriver.Firefox()
    register_test(driver)
    login_test(driver)
    logout_test(driver)
    driver.close()

    driver = webdriver.Chrome()
    register_test(driver)
    login_test(driver)
    logout_test(driver)
    driver.close()
