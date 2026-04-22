"""
Автоматизированные тесты для F-Bank
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBankTransfer:

    # ========== ТК-01 ==========
    def test_01_balance_display(self, driver, base_url):
        driver.get(base_url + "/?balance=30000&reserved=20000")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))
        
        balance = wait.until(EC.presence_of_element_located((By.ID, "rub-sum"))).text
        reserved = driver.find_element(By.ID, "rub-reserved").text
        
        assert "30000" in balance or "30'000" in balance
        assert "20000" in reserved or "20'000" in reserved

    # ========== ТК-02 ==========
    def test_02_currency_select(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        form = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))
        
        assert form.is_displayed()

    # ========== ТК-03 ==========
    def test_03_card_input(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))
        
        card = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '0000')]")))
        card.send_keys("1234567890123456")
        
        value = card.get_attribute("value")
        assert len(value.replace(" ", "")) == 16

    # ========== ТК-04 (БАГ-002) ==========
    def test_04_positive_transfer(self, driver, base_url):
        driver.get(base_url + "/?balance=110&reserved=0")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))
        
        amount = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']")))
        amount.send_keys("100")
        
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert btn.is_enabled()

    # ========== ТК-05 ==========
    def test_05_insufficient_funds(self, driver, base_url):
        driver.get(base_url + "/?balance=100&reserved=0")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))
        
        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("150")
        
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert not btn.is_enabled()
        
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Недостаточно')]")
        assert error.is_displayed()

    # ========== ТК-06 ==========
    def test_06_switch_currency(self, driver, base_url):
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Доллары')]").click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Евро')]").click()
        
        eur = wait.until(EC.presence_of_element_located((By.ID, "euro-sum")))
        assert eur.is_displayed()

    # ========== ТК-07 (БАГ-003) ==========
    def test_07_reserved_more_than_balance(self, driver, base_url):
        driver.get(base_url + "/?balance=10000&reserved=15000")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        assert "-" not in balance

    # ========== ТК-08 (БАГ-004) ==========
    def test_08_negative_balance_url(self, driver, base_url):
        driver.get(base_url + "/?balance=-100&reserved=50")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        assert "-" not in balance

    # ========== ТК-09 (БАГ-005) ==========
    def test_09_non_numeric_url(self, driver, base_url):
        driver.get(base_url + "/?balance=abc&reserved=xyz")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        assert "NaN" not in balance

    # ========== ТК-10 (БАГ-001) ==========
    def test_10_negative_amount_input(self, driver, base_url):
        driver.get(base_url + "/?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Перевод')]")))
        
        amount = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount.send_keys("-500")
        
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        assert not btn.is_enabled()

    # ========== ТК-11 ==========
    def test_11_zero_values(self, driver, base_url):
        driver.get(base_url + "/?balance=0&reserved=0")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Рубли')]"))).click()
        
        balance = driver.find_element(By.ID, "rub-sum").text
        reserved = driver.find_element(By.ID, "rub-reserved").text
        
        assert "0" in balance
        assert "0" in reserved