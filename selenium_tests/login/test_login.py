import unittest
import warnings

import pyodbc
import pytest
from time import sleep
from selenium.webdriver.support.ui import Select
import json
from pathlib import Path
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from Comman.work_flow_methods import CommanMethods
from page_objects.Pages.ManagmentPage import ManagementPageButtons
from selenium.webdriver.chrome.service import Service
from page_objects.Pages.LoginPage import LoginButtons


@pytest.mark.run(order=6)
@pytest.mark.flaky(max_runs=4)
class WesignLoginTests(unittest.TestCase):
    def setUp(self):
        settingsFilePath = Path(__file__).with_name('settings.json')
        with open(settingsFilePath) as f:
            self.settings = json.load(f)
        service = Service(self.settings['chrome_driver'])
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("start-maximized")
        options.add_argument("window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extenstions")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("force-device-scale-factor=0.75")
        options.add_argument("high-dpi-support=0.75")
        options.add_argument("--unsafely-treat-insecure-origin-as-secure=http://www.devtest.co.il")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=service,options=options)
        warnings.simplefilter('ignore', ResourceWarning)
        warnings.simplefilter('ignore', DeprecationWarning)
        self.methods = CommanMethods(self.driver, self.settings)
        self.login = LoginButtons(self.driver)

    @pytest.mark.sanity_part_3
    # @pytest.mark.english
    def test_login_success_english(self):
        self.methods.login(self.settings['company_user'], self.settings['company_user_password'])
        self.__change_to_english()
        self.__check_english_language()
        assert self.driver.current_url == self.settings["base_url"] + "dashboard/main"

    @pytest.mark.sanity_dev
    def test_login_success_wesign_dev_english(self):
        driver = self.driver
        self.driver.get(self.settings["wesign_dev_url"] + "login")
        self.__change_to_english()
        sleep(2)
        WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.ID, "loginInput")))
        element = self.driver.find_element(By.NAME,"email")
        element.send_keys(self.settings["company_user"])
        element = self.driver.find_element(By.NAME,"password")
        element.send_keys(self.settings["company_user_password"])
        element = self.driver.find_element(By.ID,"loginInput")
        element.click()
        sleep(3)
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['wesign_dev_url'] + 'dashboard/main')))
        self.__check_english_language()
        assert self.driver.current_url == self.settings["wesign_dev_url"] + "dashboard/main"

    @pytest.mark.sanity_part_1
    # @pytest.mark.english
    def test_login_with_username_success_english(self):
        self.methods.login(self.settings['second_company_username'], self.settings['company_user_password'])
        self.__change_to_english()
        WebDriverWait(self.driver, 30).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        self.__check_english_language()
        assert self.driver.current_url == self.settings["base_url"] + "dashboard/main"

    @pytest.mark.sanity_dev
    # @pytest.mark.english
    def test_login_with_username_success_wesign_dev_english(self):
        driver = self.driver
        self.driver.get(self.settings["wesign_dev_url"] + "login")
        self.__change_to_english()
        sleep(2)
        element = self.driver.find_element(By.NAME, "email")
        element.send_keys(self.settings["second_company_username"])
        element = self.driver.find_element(By.NAME, "password")
        element.send_keys(self.settings["company_user_password"])
        element = self.driver.find_element(By.ID, "loginInput")
        element.click()
        sleep(3)
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['wesign_dev_url'] + 'dashboard/main')))
        self.__check_english_language()
        assert self.driver.current_url == self.settings["wesign_dev_url"] + "dashboard/main"

    @pytest.mark.english1
    def test_login_logout_success_english(self):
        self.methods.login(self.settings['company_user'], self.settings['company_user_password'])
        self.__check_english_language()
        assert self.driver.current_url == self.settings["base_url"] + "dashboard/main"
        sign_out = self.driver.find_element(By.XPATH,"//a[text()='Sign out']")
        sign_out.click()
        sleep(2)
        submit_button = self.driver.find_element(By.XPATH,"(//sgn-pop-up-confirm/div/div/div/div[4]/button[2])[2]")
        submit_button.click()
        WebDriverWait(self.driver, 30).until(EC.url_to_be((self.settings['base_url'] + 'login')))
        assert self.driver.current_url == self.settings["base_url"] + "login"

    @pytest.mark.sanity_dev
    def test_login_logout_success_wesign_dev_english(self):
        driver = self.driver
        self.driver.get(self.settings["wesign_dev_url"] + "login")
        self.__change_to_english()
        sleep(2)
        element = self.driver.find_element(By.NAME, "email")
        element.send_keys(self.settings["company_user"])
        element = self.driver.find_element(By.NAME, "password")
        element.send_keys(self.settings["company_user_password"])
        element = self.driver.find_element(By.ID, "loginInput")
        element.click()
        sleep(3)
        self.__check_english_language()
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['wesign_dev_url'] + 'dashboard/main')))
        assert self.driver.current_url == self.settings["wesign_dev_url"] + "dashboard/main"
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='Sign out']")))
        sign_out = self.driver.find_element(By.XPATH, "//a[text()='Sign out']")
        sign_out.click()
        sleep(2)
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@class='ct-button--primary'])[3]")))
        submit_button = self.driver.find_element(By.XPATH, "(//*[@class='ct-button--primary'])[3]")
        submit_button.click()
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['wesign_dev_url'] + 'login')))
        assert self.driver.current_url == self.settings["wesign_dev_url"] + "login"

    @pytest.mark.english2
    def test_login_failed_invalid_password_english(self):
        driver = self.driver
        self.driver.get(self.settings["base_url"] + "login")
        self.__change_to_english()
        sleep(2)
        element = self.driver.find_element(By.NAME,"email")
        element.send_keys(self.settings["company_user"])
        element = self.driver.find_element(By.NAME,"password")
        invalid_password = "invalid password"
        element.send_keys(invalid_password)
        element = self.driver.find_element(By.ID,"loginInput")
        element.click()
        sleep(3)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//label[@class='is-error']")))
        element = self.driver.find_element(By.XPATH,"//label[@class='is-error']")
        error_text = element.text
        self.__check_english_language()
        assert self.driver.current_url == self.settings["base_url"] + "login"
        assert error_text == "One (or more) of the credential details is incorrect"

    @pytest.mark.english
    def test_login_failed_user_not_exist_english(self):
        driver = self.driver
        self.driver.get(self.settings["base_url"] + "login")
        self.__change_to_english()
        sleep(2)
        element = self.driver.find_element(By.NAME,"email")
        invalid_user = "invalid@user.co.il"
        element.send_keys(invalid_user)
        element = self.driver.find_element(By.NAME,"password")
        element.send_keys(self.settings["company_user_password"])
        element = self.driver.find_element(By.ID,"loginInput")
        element.click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "is-error")))
        element = self.driver.find_element(By.CLASS_NAME,"is-error")
        error_text = element.text
        self.__check_english_language()
        assert self.driver.current_url == self.settings["base_url"] + "login"
        assert error_text == "One (or more) of the credential details is incorrect"

    @pytest.mark.english1
    def test_login_using_sso(self):
        url = (self.settings["base_url"] + "auth")
        clean_url = url.replace("https://", "")
        user = self.settings['JenkinsUser']
        password = self.settings['JenkinsPassword']
        auth_url = f"https://{user}:{password}@{clean_url}"
        sleep(2)
        for x in range(10):
            sleep(3)
            self.driver.get(auth_url)
            if self.driver.current_url == self.settings['base_url'] + 'dashboard/main':
                break
            else:
                continue

    @pytest.mark.hebrew
    @pytest.mark.hebrew3
    def test_login_failed_user_not_exist_hebrew(self):
        driver = self.driver
        self.driver.get(self.settings["base_url"] + "login")
        self.__change_to_hebrew()
        sleep(2)
        element = self.driver.find_element(By.NAME,"email")
        invalid_user = "invalid@user.co.il"
        element.send_keys(invalid_user)
        element = self.driver.find_element(By.NAME,"password")
        element.send_keys(self.settings["company_user_password"])
        element = self.driver.find_element(By.ID,"loginInput")
        element.click()
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "is-error")))
        element = self.driver.find_element(By.CLASS_NAME,"is-error")
        error_text = element.text
        sleep(3)
        self.__check_hebrew_language()
        assert self.driver.current_url == self.settings["base_url"] + "login"
        assert error_text == "אחד או יותר מפרטי הזיהוי אינו תקין"

    @pytest.mark.hebrew
    @pytest.mark.hebrew2
    def test_login_failed_invalid_password_hebrew(self):
        self.driver.get(self.settings["base_url"] + "login")
        self.__change_to_hebrew()
        sleep(2)
        element = self.driver.find_element(By.NAME,"email")
        element.send_keys(self.settings["company_user"])
        element = self.driver.find_element(By.NAME,"password")
        invalid_password = "invalid password"
        element.send_keys(invalid_password)
        element = self.driver.find_element(By.ID,"loginInput")
        element.click()
        sleep(3)
        element = self.driver.find_element(By.XPATH,"//label[@class='is-error']")
        error_text = element.text
        self.__check_hebrew_language()
        assert self.driver.current_url == self.settings["base_url"] + "login"
        assert error_text == "אחד או יותר מפרטי הזיהוי אינו תקין"

    @pytest.mark.sanity_part_2
    def test_login_management_success_english(self):
        driver = self.driver
        management_page = ManagementPageButtons(driver)
        self.driver.get(self.settings["management_url"])
        sleep(3)
        element = self.driver.find_element(By.NAME,"email")
        sleep(3)
        element.send_keys(self.settings["management_user_email"])
        sleep(3)
        element = self.driver.find_element(By.NAME,"pass")
        sleep(3)
        element.send_keys(self.settings["management_user_password"])
        sleep(3)
        element = self.driver.find_element(By.CLASS_NAME,"ws_button--login")
        sleep(3)
        element.click()
        sleep(3)
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['management_url'] + 'dashboard/license')))
        management_page.click_logs_page()
        management_page.click_report_page()
        management_page.click_programs_page()
        management_page.click_license_page()
        management_page.click_company_page()
        management_page.click_configuration_page()
        management_page.click_user_page()

    @pytest.mark.sanity_part_3
    def test_login_management_success_english(self):
        driver = self.driver
        management_page = ManagementPageButtons(driver)
        self.driver.get(self.settings["management_url"])
        sleep(3)
        element = self.driver.find_element(By.NAME, "email")
        sleep(3)
        element.send_keys(self.settings["management_user_email"])
        sleep(3)
        element = self.driver.find_element(By.NAME, "pass")
        sleep(3)
        element.send_keys(self.settings["management_user_password"])
        sleep(3)
        element = self.driver.find_element(By.CLASS_NAME, "ws_button--login")
        sleep(3)
        element.click()
        sleep(3)
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['management_url'] + 'dashboard/license')))
        management_page.click_logs_page()
        management_page.click_report_page()
        management_page.click_programs_page()
        management_page.click_license_page()
        management_page.click_company_page()
        management_page.click_configuration_page()
        management_page.click_user_page()

    @pytest.mark.sanity_part_1
    # @pytest.mark.english
    #Bug number = WES-1304
    def test_login_with_user_name_success_english(self):
        driver = self.driver
        self.driver.get(self.settings["base_url"] + "login")
        sleep(2)
        element = self.driver.find_element(By.NAME, "email")
        element.send_keys(self.settings["second_company_username"])
        element = self.driver.find_element(By.NAME, "password")
        element.send_keys(self.settings["company_user_password"])
        element = self.driver.find_element(By.ID, "loginInput")
        element.click()
        sleep(3)
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        self.__check_english_language()
        assert self.driver.current_url == self.settings["base_url"] + "dashboard/main"

    @pytest.mark.sanity_dev
    # @pytest.mark.english
    # Bug number = WES-1304
    def test_login_with_user_name_success_wesign_dev_english(self):
        driver = self.driver
        self.driver.get(self.settings["wesign_dev_url"] + "login")
        sleep(2)
        WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.ID, "loginInput")))
        element = self.driver.find_element(By.NAME, "email")
        element.send_keys(self.settings["second_company_username"])
        element = self.driver.find_element(By.NAME, "password")
        element.send_keys(self.settings["company_user_password"])
        element = self.driver.find_element(By.ID, "loginInput")
        element.click()
        sleep(3)
        WebDriverWait(driver, 30).until(EC.url_to_be((self.settings['wesign_dev_url'] + 'dashboard/main')))
        self.__check_english_language()
        assert self.driver.current_url == self.settings["wesign_dev_url"] + "dashboard/main"

    ##WES-1505
    @pytest.mark.english
    def test_enter_using_otp(self):
        driver = self.driver
        self.methods.login("devtest11@comda.co.il", self.settings['company_user_password'])
        sleep(3.5)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "(//*[contains(text(),'OTP code')])")))
        driver.execute_script("window.open('');")
        sleep(1.5)
        self.driver.switch_to.window(self.driver.window_handles[1])
        sleep(8)
        self.methods.enter_comda_mail(self.settings['devTestMailUsingOtp'], self.settings['comda_mail_password'])
        sleep(1)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "(//*[contains(text(),'Your validation code is')])[1]")))
        self.driver.find_element(By.XPATH, "(//*[contains(text(),'Your validation code is')])[1]").click()
        sleep(3)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@style='direction:LTR']")))
        otp_number = self.driver.find_element(By.XPATH, "//*[@style='direction:LTR']").text
        sleep(2)
        delete_mail = self.driver.find_element(By.XPATH,
                                               "//div[5]/div/div[1]/div/div[5]/div[1]/div/div[1]/div/div/div[3]/div/button/span[2]")
        delete_mail.click()
        sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[0])
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='auth']")))
        self.driver.find_element(By.XPATH, "//*[@id='auth']").send_keys(otp_number[24:30])
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@value='Submit'])")))
        self.driver.find_element(By.XPATH, "(//*[@value='Submit'])").click()
        WebDriverWait(self.driver, 20).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))

    ##WES-1569
    @pytest.mark.hebrew3
    def test_expired_password_after_x_days_hebrew(self):
        driver = self.driver
        conn = pyodbc.connect(f'Driver=SQL Server;'
                              "Server=DEVTEST\SQLEXPRESS;"
                              f'Database={self.settings["db_name"]};'
                              f'UID={self.settings["db_user"]};'
                              F'PWD={self.settings["db_password"]};'
                              'Trusted_Connection=no;')
        sleep(1)
        cursor = conn.cursor()
        cursor.execute(
            f"update Users set Password = 'ykmqOMYFXDCfiH8CtSigRwroqzTK11W3thCHKKa3XdUoQbV7' where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        cursor.execute(
            f"delete from UsersPasswordHistory")
        conn.commit()
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        passwords = ['Comsign1!','Comsign2!','Comsign333333!', 'Comsign444444!', 'comsign555555!', "Comsign666666!"]
        self.methods.login("PassWordReset@comda.co.il", self.settings['company_user_password'])
        self.login.change_language(False)
        sleep(3.5)
        WebDriverWait(self.driver, 40).until(EC.url_to_be((self.settings['base_url'] + 'login')))
        WebDriverWait(self.driver, 40).until(EC.presence_of_element_located((By.XPATH, "//sgn-expired-password/h2")))

        #Check old password as new password
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[0])
        self.login.reenter_new_password([passwords[0]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "סיסמה חדשה צריכה להיות שונה מהסיסמה הישנה"

        #Check Minimum password length
        self.login.clear_password_inputs(True,True,True)
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[1])
        self.login.reenter_new_password([passwords[1]])
        self.login.click_update()
        sleep(2)
        is_error = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "הסיסמה צריכה לכלול לפחות ספרה אחת, תו מיוחד אחד ולהיות באורך של לפחות 14 תווים"

        # Check invalid password
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[1])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[2]])
        self.login.click_update()
        sleep(2)
        is_error = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "פרטי הזדהות אינם תקינים"

        # Check match password
        self.methods.login("PassWordReset@comda.co.il", self.settings['company_user_password'])
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[3]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "הסיסמאות צריכות להיות תואמות. בנוסף, הסיסמה צריכה להכיל לפחות ספרה אחת ותו מיוחד אחד"

        # Change password first time
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[2]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'סיסמה שונתה בהצלחה'
        self.methods.login("PassWordReset@comda.co.il", passwords[2])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

        #Check cant use old password
        sleep(1.5)
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        sleep(1.5)
        self.methods.login("PassWordReset@comda.co.il", passwords[2])
        self.login.change_language(False)
        WebDriverWait(self.driver, 40).until(EC.presence_of_element_located((By.XPATH, "//sgn-expired-password/h2")))

        # Change password second time and check cant use new password
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[2])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[2]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "סיסמה חדשה צריכה להיות שונה מהסיסמה הישנה"

        sleep(2)

        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[2])
        self.login.enter_new_password(passwords[3])
        self.login.reenter_new_password([passwords[3]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'סיסמה שונתה בהצלחה'
        self.methods.login("PassWordReset@comda.co.il", passwords[3])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

        # Change password third time and check cant use new password
        sleep(1.5)
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        self.methods.login("PassWordReset@comda.co.il", passwords[3])
        self.login.change_language(False)
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[3])
        self.login.enter_new_password(passwords[3])
        self.login.reenter_new_password([passwords[3]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "סיסמה חדשה צריכה להיות שונה מהסיסמה הישנה"

        sleep(2)

        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[3])
        self.login.enter_new_password(passwords[4])
        self.login.reenter_new_password([passwords[4]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'סיסמה שונתה בהצלחה'
        self.methods.login("PassWordReset@comda.co.il", passwords[4])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

        sleep(1.5)
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        sleep(2)
        self.methods.login("PassWordReset@comda.co.il", passwords[4])
        self.login.change_language(False)
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[4])
        self.login.enter_new_password(passwords[5])
        self.login.reenter_new_password([passwords[5]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'סיסמה שונתה בהצלחה'
        self.methods.login("PassWordReset@comda.co.il", passwords[5])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

    ##WES-1569
    @pytest.mark.english2
    def test_expired_password_after_x_days(self):
        driver = self.driver
        conn = pyodbc.connect(f'Driver=SQL Server;'
                              "Server=DEVTEST\SQLEXPRESS;"
                              f'Database={self.settings["db_name"]};'
                              f'UID={self.settings["db_user"]};'
                              F'PWD={self.settings["db_password"]};'
                              'Trusted_Connection=no;')
        sleep(1)
        cursor = conn.cursor()
        cursor.execute(
            f"update Users set Password = 'ykmqOMYFXDCfiH8CtSigRwroqzTK11W3thCHKKa3XdUoQbV7' where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        cursor.execute(
            f"delete from UsersPasswordHistory")
        conn.commit()
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        passwords = ['Comsign1!', 'Comsign2!', 'Comsign333333!', 'Comsign444444!', 'comsign555555!',
                     "Comsign666666!"]
        self.methods.login("PassWordReset@comda.co.il", self.settings['company_user_password'])
        sleep(3.5)
        WebDriverWait(self.driver, 40).until(EC.url_to_be((self.settings['base_url'] + 'login')))
        WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//sgn-expired-password/h2")))

        # Check old password as new password
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[0])
        self.login.reenter_new_password([passwords[0]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "New password must be different from the old password."

        # Check Minimum password length
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[1])
        self.login.reenter_new_password([passwords[1]])
        self.login.click_update()
        sleep(2)
        is_error = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "Password should contain at least one digit, one special character and at least 14 characters long"

        # Check invalid password
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[1])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[2]])
        self.login.click_update()
        sleep(2)
        is_error = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "Invalid credential"

        # Check match password
        self.methods.login("PassWordReset@comda.co.il", self.settings['company_user_password'])
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[3]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "Passwords should match. Additionally, password should contain at least one digit and one special character"

        # Change password first time
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(self.settings['company_user_password'])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[2]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'Password changed successfully'
        self.methods.login("PassWordReset@comda.co.il", passwords[2])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

        # Check cant use old password
        sleep(1.5)
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        sleep(1.5)
        self.methods.login("PassWordReset@comda.co.il", passwords[2])
        WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//sgn-expired-password/h2")))

        # Change password second time and check cant use new password
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[2])
        self.login.enter_new_password(passwords[2])
        self.login.reenter_new_password([passwords[2]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "New password must be different from the old password."

        sleep(2)

        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[2])
        self.login.enter_new_password(passwords[3])
        self.login.reenter_new_password([passwords[3]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'Password changed successfully'
        self.methods.login("PassWordReset@comda.co.il", passwords[3])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

        # Change password third time and check cant use new password
        sleep(1.5)
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        self.methods.login("PassWordReset@comda.co.il", passwords[3])
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[3])
        self.login.enter_new_password(passwords[3])
        self.login.reenter_new_password([passwords[3]])
        self.login.click_update()
        is_error = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@class='ws_error_msg_big_font is-error']")))
        assert is_error.text == "New password must be different from the old password."

        sleep(2)

        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[3])
        self.login.enter_new_password(passwords[4])
        self.login.reenter_new_password([passwords[4]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'Password changed successfully'
        self.methods.login("PassWordReset@comda.co.il", passwords[4])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

        sleep(1.5)
        cursor.execute(
            f"update Users set PasswordSetupTime =  DATEADD(DAY, -31, GETDATE()) where users.Id = '402D2112-5649-47EF-CC16-08DCB4405DFF'")
        conn.commit()
        sleep(2)
        self.methods.login("PassWordReset@comda.co.il", passwords[4])
        self.login.clear_password_inputs(True, True, True)
        self.login.enter_old_password(passwords[4])
        self.login.enter_new_password(passwords[5])
        self.login.reenter_new_password([passwords[5]])
        self.login.click_update()
        is_confirm = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-confirm")))
        assert is_confirm.text == 'Password changed successfully'
        self.methods.login("PassWordReset@comda.co.il", passwords[5])
        WebDriverWait(self.driver, 60).until(EC.url_to_be((self.settings['base_url'] + 'dashboard/main')))
        sleep(2)
        assert self.driver.current_url == (self.settings['base_url'] + 'dashboard/main')
        self.methods.home_page.click_my_profile_button()
        self.methods.my_profile_buttons.click_sign_out()

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    if __name__ == "__main__":
        unittest.main()

    def __check_english_language(self):
        sleep(10)
        element = self.driver.find_element(By.TAG_NAME,"html")
        language = element.get_attribute("lang")
        direction = element.get_attribute("dir")
        assert language == "en"
        assert direction == "ltr"

    def __check_hebrew_language(self):
        sleep(10)
        element = self.driver.find_element(By.TAG_NAME,"html")
        language = element.get_attribute("lang")
        direction = element.get_attribute("dir")
        assert language == "he"
        assert direction == "rtl"

    def __change_to_hebrew(self):
        sleep(8)
        element = self.driver.find_element(By.TAG_NAME,"html")
        if element.get_attribute('dir') == 'ltr':
            sleep(2)
            language_list = self.driver.find_element(By.CLASS_NAME, "ng-arrow-wrapper")
            language_list.click()
            sleep(3)
            hebrew = self.driver.find_element(By.XPATH, "//*[contains(text(),'עברית')]")
            hebrew.click()
        else:
            pass

    def __change_to_english(self):
        sleep(8)
        element = self.driver.find_element(By.TAG_NAME,"html")
        if element.get_attribute('dir') == 'rtl':
            sleep(2)
            select = Select(self.driver.find_element(By.ID,"languagesOptions"))
            select.select_by_visible_text("English")
        else:
            pass


