"""
Automated tests for F-Bank
Black-box UI tests for bank transfer functionality
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBankTransfer:

    # ==================== LOCATORS ====================
    RUB_CURRENCY = (By.XPATH, "//*[contains(text(), 'Рубли')]")
    USD_CURRENCY = (By.XPATH, "//*[contains(text(), 'Доллары')]")
    EUR_CURRENCY = (By.XPATH, "//*[contains(text(), 'Евро')]")

    TRANSFER_BTN = (By.XPATH, "//button[contains(text(), 'Перевести')]")
    CARD_INPUT = (By.XPATH, "//input[contains(@placeholder, '0000')]")

    BALANCE_RUB = (By.ID, "rub-sum")
    RESERVED_RUB = (By.ID, "rub-reserved")
    BALANCE_EUR = (By.ID, "euro-sum")

    FORM_TITLE = (By.XPATH, "//h2[contains(text(), 'Перевод')]")
    ERROR_MESSAGE = (By.XPATH, "//*[contains(text(), 'Недостаточно')]")

    # ==================== HELPERS ====================
    def open_rub_form(self, driver, wait):
        wait.until(EC.element_to_be_clickable(self.RUB_CURRENCY)).click()
        wait.until(EC.presence_of_element_located(self.FORM_TITLE))

    def get_amount_input(self, wait):
        return wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "(//input[@type='text' or @type='number'])[last()]"
            ))
        )

    def get_transfer_button(self, wait):
        return wait.until(
            EC.element_to_be_clickable(self.TRANSFER_BTN)
        )

    # ==================== TEST CASES ====================

    def test_01_balance_display(self, driver, base_url):
        driver.get(base_url + "/?balance=30000&reserved=20000")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert "30000" in balance
        assert "20000" in reserved

    def test_02_currency_select(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable(self.RUB_CURRENCY)).click()

        form = wait.until(EC.presence_of_element_located(self.FORM_TITLE))
        assert form.is_displayed()

    def test_03_card_input(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        card_input = wait.until(EC.presence_of_element_located(self.CARD_INPUT))
        card_input.clear()
        card_input.send_keys("1234567890123456")

        value = card_input.get_attribute("value")
        assert len(value.replace(" ", "")) == 16

    def test_04_positive_transfer(self, driver, base_url):
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        amount = self.get_amount_input(wait)
        amount.clear()
        amount.send_keys("100")

        btn = self.get_transfer_button(wait)
        assert btn.is_enabled()

    def test_05_insufficient_funds(self, driver, base_url):
        driver.get(base_url + "/?balance=100&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        amount = self.get_amount_input(wait)
        amount.clear()
        amount.send_keys("150")

        btn = self.get_transfer_button(wait)
        assert not btn.is_enabled()

        error = wait.until(EC.presence_of_element_located(self.ERROR_MESSAGE))
        assert error.is_displayed()

    def test_06_switch_currency(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable(self.RUB_CURRENCY)).click()
        driver.find_element(*self.USD_CURRENCY).click()
        driver.find_element(*self.EUR_CURRENCY).click()

        eur_balance = wait.until(
            EC.visibility_of_element_located(self.BALANCE_EUR)
        )
        assert eur_balance.is_displayed()

    def test_07_reserved_more_than_balance(self, driver, base_url):
        driver.get(base_url + "/?balance=10000&reserved=15000")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert not balance.strip().startswith("-")
        assert not reserved.strip().startswith("-")

    def test_08_negative_balance_url(self, driver, base_url):
        driver.get(base_url + "/?balance=-100&reserved=50")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        assert not balance.strip().startswith("-")

    def test_09_non_numeric_url(self, driver, base_url):
        driver.get(base_url + "/?balance=abc&reserved=xyz")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert "NaN" not in balance
        assert "NaN" not in reserved

    def test_10_negative_amount_input(self, driver, base_url):
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        amount = self.get_amount_input(wait)
        amount.clear()
        amount.send_keys("-500")

        btn = self.get_transfer_button(wait)
        assert not btn.is_enabled()

    def test_11_zero_values(self, driver, base_url):
        driver.get(base_url + "/?balance=0&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert "0" in balance
        assert "0" in reserved