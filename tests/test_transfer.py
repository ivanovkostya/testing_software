"""
Автоматизированные тесты для F-Bank
11 тест-кейсов, из которых 5 падают из-за дефектов
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBankTransfer:

    # ==================== ОБЩИЙ ХЕЛПЕР ====================
    def get_amount_input(self, driver, wait):
        """Поиск поля ввода суммы"""
        try:
            amount = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            return amount
        except:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            return inputs[1] if len(inputs) > 1 else None

    # ==================== ТК-01 ====================
    def test_01_balance_display(self, driver, base_url):
        """
        ТК-01: Проверка отображения баланса и резерва из URL-параметров
        """
        driver.get(base_url + "/?balance=30000&reserved=20000")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        balance = wait.until(EC.presence_of_element_located((By.ID, "rub-sum"))).text
        reserved = wait.until(EC.presence_of_element_located((By.ID, "rub-reserved"))).text

        assert "30000" in balance or "30'000" in balance
        assert "20000" in reserved or "20'000" in reserved

    # ==================== ТК-02 ====================
    def test_02_currency_select(self, driver, base_url):
        """
        ТК-02: Выбор валюты на главном экране
        """
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        form = wait.until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]"))
        )
        assert form.is_displayed()

    # ==================== ТК-03 ====================
    def test_03_card_input(self, driver, base_url):
        """
        ТК-03: Ввод номера карты с форматированием
        """
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        card_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '0000')]"))
        )
        card_input.send_keys("1234567890123456")

        value = card_input.get_attribute("value")
        assert len(value.replace(" ", "")) == 16

    # ==================== ТК-04 ====================
    def test_04_positive_transfer(self, driver, base_url):
        """
        ТК-04: Перевод с положительной суммой
        ❌ ПАДАЕТ ИЗ-ЗА БАГ-002: Ошибка расчёта комиссии
        """
        driver.get(base_url + "/?balance=110&reserved=0")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))

        amount = self.get_amount_input(driver, wait)
        assert amount is not None, "Поле ввода суммы не найдено"
        amount.send_keys("100")

        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert btn.is_enabled()

    # ==================== ТК-05 ====================
    def test_05_insufficient_funds(self, driver, base_url):
        """
        ТК-05: Отображение ошибки при недостатке средств
        """
        driver.get(base_url + "/?balance=100&reserved=0")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))

        amount = self.get_amount_input(driver, wait)
        assert amount is not None, "Поле ввода суммы не найдено"
        amount.send_keys("150")

        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert not btn.is_enabled()

        error = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Недостаточно')]"))
        )
        assert error.is_displayed()

    # ==================== ТК-06 ====================
    def test_06_switch_currency(self, driver, base_url):
        """
        ТК-06: Переключение между валютами
        """
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Доллары')]").click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Евро')]").click()

        time.sleep(1)
        eur_balance = driver.find_element(By.ID, "euro-sum")
        assert eur_balance.is_displayed()

    # ==================== ТК-07 ====================
    def test_07_reserved_more_than_balance(self, driver, base_url):
        """
        ТК-07: Резерв превышает баланс
        ❌ ПАДАЕТ ИЗ-ЗА БАГ-003: Отображается отрицательный остаток
        """
        driver.get(base_url + "/?balance=10000&reserved=15000")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "-" not in page_text or "На счету: 0" in page_text

    # ==================== ТК-08 ====================
    def test_08_negative_balance_url(self, driver, base_url):
        """
        ТК-08: Отрицательный баланс в URL
        ❌ ПАДАЕТ ИЗ-ЗА БАГ-004: Баланс может быть отрицательным
        """
        driver.get(base_url + "/?balance=-100&reserved=50")
        wait = WebDriverWait(driver, 10)

        assert "F-Bank" in driver.find_element(By.TAG_NAME, "h1").text

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        balance = driver.find_element(By.ID, "rub-sum").text
        assert "-" not in balance

    # ==================== ТК-09 ====================
    def test_09_non_numeric_url(self, driver, base_url):
        """
        ТК-09: Нечисловые значения в URL
        ❌ ПАДАЕТ ИЗ-ЗА БАГ-005: Отображается NaN
        """
        driver.get(base_url + "/?balance=abc&reserved=xyz")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "NaN" not in page_text

    # ==================== ТК-10 ====================
    def test_10_negative_amount_input(self, driver, base_url):
        """
        ТК-10: Ввод отрицательной суммы перевода
        ❌ ПАДАЕТ ИЗ-ЗА БАГ-001: Отрицательная сумма принимается
        """
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))

        amount = self.get_amount_input(driver, wait)
        assert amount is not None, "Поле ввода суммы не найдено"
        amount.send_keys("-500")

        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert not btn.is_enabled()

    # ==================== ТК-11 ====================
    def test_11_zero_values(self, driver, base_url):
        """
        ТК-11: Нулевые значения баланса и резерва
        """
        driver.get(base_url + "/?balance=0&reserved=0")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()

        balance = driver.find_element(By.ID, "rub-sum").text
        reserved = driver.find_element(By.ID, "rub-reserved").text

        assert "0" in balance
        assert "0" in reserved