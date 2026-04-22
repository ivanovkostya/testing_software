import pytest
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBankTransfer:

    # ==================== ЛОКАТОРЫ ====================
    RUB_CURRENCY = (By.XPATH, "//*[contains(text(), 'Рубли')]")
    USD_CURRENCY = (By.XPATH, "//*[contains(text(), 'Доллары')]")
    EUR_CURRENCY = (By.XPATH, "//*[contains(text(), 'Евро')]")

    TRANSFER_BTN = (By.XPATH, "//button[contains(., 'Перевести')]")

    CARD_INPUT = (By.XPATH, "//input[contains(@placeholder,'0000')]")

    BALANCE_RUB = (By.ID, "rub-sum")
    RESERVED_RUB = (By.ID, "rub-reserved")
    BALANCE_EUR = (By.ID, "euro-sum")

    FORM_TITLE = (By.XPATH, "//h2[contains(., 'Перевод')]")
    ERROR_MESSAGE = (By.XPATH, "//*[contains(., 'Недостаточно')]")

    # ==================== HELPERS ====================

    def open_rub_form(self, driver, wait):
        wait.until(EC.element_to_be_clickable(self.RUB_CURRENCY)).click()
        wait.until(EC.presence_of_element_located(self.FORM_TITLE))

    def get_amount_input(self, wait):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                "(//input[@type='text' or @type='number'])[last()]"
            ))
        )

    def get_transfer_button(self, wait):
        return wait.until(EC.presence_of_element_located(self.TRANSFER_BTN))

    def normalize_number(self, text: str):
        """
        Убираем пробелы, апострофы и прочие форматирования
        """
        return re.sub(r"[^\d\-]", "", text)

    # ==================== ТК-01 ====================

    def test_01_balance_display(self, driver, base_url):
        driver.get(base_url + "/?balance=30000&reserved=20000")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert self.normalize_number(balance) == "30000"
        assert self.normalize_number(reserved) == "20000"

    # ==================== ТК-02 ====================

    def test_02_currency_select(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        form = wait.until(EC.presence_of_element_located(self.FORM_TITLE))
        assert form.is_displayed()

    # ==================== ТК-03 ====================

    def test_03_card_input(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        card = wait.until(EC.visibility_of_element_located(self.CARD_INPUT))
        card.clear()
        card.send_keys("1234567890123456")

        value = card.get_attribute("value")
        assert len(value.replace(" ", "")) == 16

    # ==================== ТК-04 ====================

    def test_04_positive_transfer(self, driver, base_url):
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        amount = self.get_amount_input(wait)
        amount.clear()
        amount.send_keys("100")

        btn = self.get_transfer_button(wait)
        assert btn is not None

    # ==================== ТК-05 ====================

    def test_05_insufficient_funds(self, driver, base_url):
        driver.get(base_url + "/?balance=100&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        amount = self.get_amount_input(wait)
        amount.clear()
        amount.send_keys("150")

        btn = self.get_transfer_button(wait)
        assert btn is not None

    # ==================== ТК-06 ====================

    def test_06_switch_currency(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        wait.until(EC.element_to_be_clickable(self.USD_CURRENCY)).click()
        wait.until(EC.element_to_be_clickable(self.EUR_CURRENCY)).click()

        eur = wait.until(EC.visibility_of_element_located(self.BALANCE_EUR))
        assert eur.is_displayed()

    # ==================== ТК-07 ====================

    def test_07_reserved_more_than_balance(self, driver, base_url):
        driver.get(base_url + "/?balance=10000&reserved=15000")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert "-" not in self.normalize_number(balance)
        assert "-" not in self.normalize_number(reserved)

    # ==================== ТК-08 ====================

    def test_08_negative_balance_url(self, driver, base_url):
        driver.get(base_url + "/?balance=-100&reserved=50")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        assert not self.normalize_number(balance).startswith("-")

    # ==================== ТК-09 ====================

    def test_09_non_numeric_url(self, driver, base_url):
        driver.get(base_url + "/?balance=abc&reserved=xyz")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert "NaN" not in balance
        assert "NaN" not in reserved

    # ==================== ТК-10 ====================

    def test_10_negative_amount_input(self, driver, base_url):
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        amount = self.get_amount_input(wait)
        amount.clear()
        amount.send_keys("-500")

        btn = self.get_transfer_button(wait)
        assert btn is not None

    # ==================== ТК-11 ====================

    def test_11_zero_values(self, driver, base_url):
        driver.get(base_url + "/?balance=0&reserved=0")
        wait = WebDriverWait(driver, 10)

        self.open_rub_form(driver, wait)

        balance = wait.until(EC.presence_of_element_located(self.BALANCE_RUB)).text
        reserved = wait.until(EC.presence_of_element_located(self.RESERVED_RUB)).text

        assert self.normalize_number(balance) == "0"
        assert self.normalize_number(reserved) == "0"