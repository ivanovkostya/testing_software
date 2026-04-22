import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBankTransfer:

    # ==================== ТК-01 ====================
    def test_01_balance_display(self, driver, base_url):
        """
        ТК-01: Проверка отображения баланса и резерва из URL-параметров
        """
        driver.get(base_url + "/?balance=30000&reserved=20000")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        balance = driver.find_element(By.ID, "rub-sum").text
        reserved = driver.find_element(By.ID, "rub-reserved").text

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

        form = driver.find_element(By.XPATH, "//h2[contains(text(), 'Перевод')]")
        assert form.is_displayed()

    # ==================== ТК-03 ====================
    def test_03_card_input(self, driver, base_url):
        """
        ТК-03: Ввод номера карты с форматированием
        """
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
        card_input.send_keys("1234567890123456")

        value = card_input.get_attribute("value")
        assert len(value.replace(" ", "")) == 16

    # ==================== ТК-04 ====================
    def test_04_positive_transfer(self, driver, base_url):
        """
        ТК-04: Перевод с положительной суммой
        """
        driver.get(base_url + "/?balance=110&reserved=0")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("100")

        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        
        # Ожидание: кнопка активна (баланс 110, сумма 100 + комиссия 10 = 110)
        # Факт: кнопка неактивна
        assert btn.is_enabled(), "БАГ-002: Кнопка неактивна при балансе 110 и сумме 100"

    # ==================== ТК-05 ====================
    def test_05_insufficient_funds(self, driver, base_url):
        """
        ТК-05: Отображение ошибки при недостатке средств
        """
        driver.get(base_url + "/?balance=100&reserved=0")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("150")

        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert not btn.is_enabled()

        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Недостаточно')]")
        assert error.is_displayed()

    # ==================== ТК-06 ====================
    def test_06_switch_currency(self, driver, base_url):
        """
        ТК-06: Переключение между валютами
        """
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)

        driver.find_element(By.XPATH, "//*[contains(text(), 'Рубли')]").click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Доллары')]").click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Евро')]").click()

        assert driver.find_element(By.ID, "euro-sum").is_displayed()

    # ==================== ТК-07 ====================
    def test_07_reserved_more_than_balance(self, driver, base_url):
        """
        ТК-07: Резерв превышает баланс
        """
        driver.get(base_url + "/?balance=10000&reserved=15000")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Ожидание: нет отрицательного доступного остатка
        # Факт: отображается отрицательное число
        assert "-" not in page_text or "На счету: 0" in page_text, \
            "БАГ-003: Отображается отрицательный доступный остаток"

    # ==================== ТК-08 ====================
    def test_08_negative_balance_url(self, driver, base_url):
        """
        ТК-08: Отрицательный баланс в URL
        """
        driver.get(base_url + "/?balance=-100&reserved=50")
        wait = WebDriverWait(driver, 10)

        title = driver.find_element(By.TAG_NAME, "h1").text
        assert "F-Bank" in title

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        balance = driver.find_element(By.ID, "rub-sum").text
        
        # Ожидание: баланс не отрицательный
        # Факт: отображается -100
        assert "-" not in balance, "БАГ-004: Баланс не должен быть отрицательным"

    # ==================== ТК-09 ====================
    def test_09_non_numeric_url(self, driver, base_url):
        """
        ТК-09: Нечисловые значения в URL
        """
        driver.get(base_url + "/?balance=abc&reserved=xyz")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Ожидание: нет NaN
        # Факт: отображается NaN
        assert "NaN" not in page_text, "БАГ-005: В интерфейсе отображается NaN"

    # ==================== ТК-10 =====================
    def test_10_negative_amount_input(self, driver, base_url):
        """
        ТК-10: Ввод отрицательной суммы перевода
        """
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("-500")

        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        
        # Ожидание: кнопка неактивна
        # Факт: кнопка активна
        assert not btn.is_enabled(), "БАГ-001: Кнопка активна при отрицательной сумме"

    # ==================== ТК-11 ====================
    def test_11_zero_values(self, driver, base_url):
        """
        ТК-11: Нулевые значения баланса и резерва
        """
        driver.get(base_url + "/?balance=0&reserved=0")
        wait = WebDriverWait(driver, 10)

        rub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]")))
        rub.click()

        balance = driver.find_element(By.ID, "rub-sum").text
        reserved = driver.find_element(By.ID, "rub-reserved").text

        assert "0" in balance
        assert "0" in reserved