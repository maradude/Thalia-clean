from selenium import webdriver
import pandas as pd
import numpy as np
import os
import util

"""
Test social media links
"""


def contact_test(driver):
    driver.get("http://127.0.0.1:5000/contact/")
    driver.implicitly_wait(5)  # seconds
    # Make sure we're accessing the correct webpage
    assert "Thalia" in driver.title
    util.page_wait()

    email_field = driver.find_element_by_id("email")
    email_field.send_keys(util.email)

    title_field = driver.find_element_by_id("title")
    title_field.send_keys(util.title)

    contents_field = driver.find_element_by_id("contents")
    contents_field.send_keys(util.contents)

    send_feedback_btn = driver.find_element_by_class_name("send-feedback-btn")
    driver.execute_script("arguments[0].click();", send_feedback_btn)

    # Check message was recorded
    util.page_wait()
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    df0 = pd.read_csv(os.path.join(project_dir, "feedback.csv"))
    submitted = np.array([util.email, util.title, util.contents])
    assert (df0 == submitted).all(1).any()


if __name__ == "__main__":
    driver = webdriver.Firefox()
    contact_test(driver)
    driver.close()
    driver = webdriver.Chrome()
    contact_test(driver)
    driver.close()
