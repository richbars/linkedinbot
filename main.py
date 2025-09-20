"""
# Author: Richard Santos (richbars)
# Date: 2025-09-20
# Project: LinkedinBOT
# Description: Automation tool to connect on LinkedIn to selected roles
# Github: https://github.com/richbars/
# LinkedIn: https://www.linkedin.com/in/richbar/
# Version: 1.0.0
# License: MIT License (Personal/Educational Use)
"""

import json
import logging
import random
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

LOGGER.setLevel(logging.CRITICAL)

COOKIE_FILE = "linkedin_cookies.json"

def save_cookies(driver, path):
    with open(path, "w") as file:
        json.dump(driver.get_cookies(), file)


def load_cookies(driver, path):
    with open(path, "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"
            driver.add_cookie(cookie)


email = input("Enter your LinkedIn email: ")
password = input("Enter your LinkedIn password: ")
role = input("Enter the role you want to connect with: ")
target_connections = int(input("Enter the number of people you want to connect with: "))

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get("https://www.linkedin.com/")

try:
    load_cookies(driver, COOKIE_FILE)
    driver.refresh()
    print("✅ Cookies loaded successfully, you should already be logged in.")
except FileNotFoundError:
    print("⚠ No cookies found, performing manual login...")
    driver.get("https://www.linkedin.com/login")
    email_field = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "username")))
    email_field.send_keys(email)
    pass_field = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "password")))
    pass_field.send_keys(password)
    submit_login = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
    submit_login.click()

    print("⌛ Waiting for possible 2FA or captcha...")
    time.sleep(30)
    save_cookies(driver, COOKIE_FILE)
    print("✅ Login completed and cookies saved.")

driver.get(f"https://www.linkedin.com/search/results/people/?keywords={role}&origin=GLOBAL_SEARCH_HEADER&page=1")

connection_counter = 0

while connection_counter < target_connections:
    try:
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[contains(.,'Conectar')]"))
        )

        if not buttons:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Próxima')]"))
                ).click()
                time.sleep(random.uniform(1.5, 2.5))
                continue
            except TimeoutException:
                print("⚠ Could not find 'Next' button. Ending process.")
                break

        for connect_button in buttons:
            if connection_counter >= target_connections:
                break

            try:
                connect_button.click()
                time.sleep(random.uniform(0.8, 1.5))

                connection_counter += 1
                print(f"📨 Connection requests sent: {connection_counter}")

            except TimeoutException:
                print("⚠ 'Send now' button not found, skipping this one.")
                continue
            except Exception as e:
                print(f"⚠ Error while trying to connect: {e}")
                continue

    except TimeoutException:
        print("⚠ No 'Connect' buttons found on this page. Trying next page...")
        try:
            next_page = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Próxima')]"))
            )
            next_page.click()
            time.sleep(random.uniform(1.5, 3.0))
        except TimeoutException:
            print("⚠ No more pages available.")
            break

print("🎉 Process finished.")
driver.quit()