import random
import uuid
from time import sleep
import json
from pathlib import Path
import names
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginButtons():
    def __init__(self, driver):
        self.driver = driver
        self.index = 1
        settingsFilePath = Path(__file__).parent.parent.parent / 'settings.json'
        with open(settingsFilePath) as f:
            self.settings = json.load(f)

    def enter_old_password(self, password):
        old_password = WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[1]")))
        old_password.send_keys(password)

    def enter_new_password(self, password):
        new_password = WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[2]")))
        new_password.send_keys(password)

    def reenter_new_password(self, password):
        reenter_new_password = WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[3]")))
        reenter_new_password.send_keys(password)

    def click_update(self):
        button = WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']")))
        button.click()

    def clear_password_inputs(self, old=True, new=True, reenter=True):
        if old:
            old_password = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[1]")))
            old_password.clear()
        if new:
            new_password = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[2]")))
            new_password.clear()
        if reenter:
            reenter_new_password = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[3]")))
            reenter_new_password.clear()


    def change_language(self, english=True):
        sleep(1.5)
        if english:
            pass
        else:
            list = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "//ng-select/div/span")))
            list.click()
            click_hebrew = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, "//div[2]/div[2]/div")))
            click_hebrew.click()







