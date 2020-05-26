from selenium import webdriver

import util

"""
Test registering a new/old user on the Thalia website
"""


def register_test(driver):
    driver.get("http://127.0.0.1:5000")
    driver.implicitly_wait(5)  # seconds
    # Make sure we're accessing the correct webpage
    assert "Thalia" in driver.title

    # Navigate to sign in form
    reg_button = driver.find_element_by_class_name("signup-btn")
    driver.execute_script("arguments[0].click();", reg_button)

    # Test redirect
    util.page_wait()
    assert "http://127.0.0.1:5000/register/" == driver.current_url
    assert "already registered" not in driver.page_source

    # Fill in sign in form
    uname_field = driver.find_element_by_id("username")
    uname_field.send_keys(util.uname)
    pwd_field = driver.find_element_by_id("password")
    pwd_field.send_keys(util.pwd)
    confirm_pwd_field = driver.find_element_by_id("confirm_password")
    confirm_pwd_field.send_keys(util.pwd)

    submit = driver.find_element_by_class_name("submit-btn")
    driver.execute_script("arguments[0].click();", submit)

    # check user registered and redirected already registered
    util.page_wait()
    assert ("already registered" in driver.page_source) or (
        "http://127.0.0.1:5000/login/" == driver.current_url
    )


if __name__ == "__main__":
    driver = webdriver.Firefox()
    register_test(driver)
    driver.close()
    driver = webdriver.Chrome()
    register_test(driver)
    driver.close()
