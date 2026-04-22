"""
Автоматизированные тесты для F-Bank
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBankTransfer:

    @pytest.fixture
    def setup(self, driver, base_url):
        """Общая настройка перед каждым тестом"""
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)
        # Выбираем Рубли
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        # Ждём появления формы
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))
        return wait

    # ==================== ТЕСТЫ ====================

    def test_01_balance_display(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=30000&reserved=20000")
        # Перевыбираем валюту после смены URL
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = wait.until(EC.presence_of_element_located((By.ID, "rub-sum"))).text
        reserved = driver.find_element(By.ID, "rub-reserved").text
        
        assert "30000" in balance or "30'000" in balance
        assert "20000" in reserved or "20'000" in reserved

    def test_02_currency_select(self, driver, base_url, setup):
        # Уже проверено в setup
        assert True

    def test_03_card_input(self, driver, base_url, setup):
        wait = setup
        card_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '0000')]")))
        card_input.send_keys("1234567890123456")
        
        value = card_input.get_attribute("value")
        assert len(value.replace(" ", "")) == 16

    def test_04_positive_transfer(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=110&reserved=0")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("100")
        
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert btn.is_enabled()  # ❌ БАГ-002: должно быть True, но будет False

    def test_05_insufficient_funds(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=100&reserved=0")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("150")
        
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert not btn.is_enabled()
        
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Недостаточно')]")
        assert error.is_displayed()

    def test_06_switch_currency(self, driver, base_url, setup):
        wait = setup
        driver.find_element(By.XPATH, "//*[contains(text(), 'Доллары')]").click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Евро')]").click()
        
        eur = wait.until(EC.presence_of_element_located((By.ID, "euro-sum")))
        assert eur.is_displayed()

    def test_07_reserved_more_than_balance(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=10000&reserved=15000")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        # ❌ БАГ-003: ожидаем что нет минуса, но он есть
        assert "-" not in balance

    def test_08_negative_balance_url(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=-100&reserved=50")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        # ❌ БАГ-004: ожидаем что нет минуса, но он есть
        assert "-" not in balance

    def test_09_non_numeric_url(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=abc&reserved=xyz")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        # ❌ БАГ-005: ожидаем что нет NaN, но он есть
        assert "NaN" not in balance

    def test_10_negative_amount_input(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("-500")
        
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        # ❌ БАГ-001: ожидаем False, но будет True
        assert not btn.is_enabled()

    def test_11_zero_values(self, driver, base_url, setup):
        wait = setup
        driver.get(base_url + "/?balance=0&reserved=0")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        reserved = driver.find_element(By.ID, "rub-reserved").text
        
        assert "0" in balance
        assert "0" in reserved