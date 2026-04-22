import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestBankTransfer:
    
    def test_bug_negative_amount(self, driver, base_url):
        """
        БАГ №1: Возможность ввода отрицательной суммы
        """
        driver.get(f"{base_url}/index.html?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)
        
        # Ждем загрузки страницы
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # Нажимаем на карточку Рубли
        rub_card = wait.until(EC.element_to_be_clickable((By.XPATH, "//h2[text()='Рубли']")))
        rub_card.click()
        
        # Вводим отрицательную сумму
        amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount_input.clear()
        amount_input.send_keys("-500")
        
        # Проверяем кнопку
        transfer_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        
        # ❌ Тест должен упасть - кнопка активна при отрицательной сумме
        assert not transfer_btn.is_enabled(), "БАГ: Кнопка активна при отрицательной сумме перевода!"
    
    def test_bug_commission_calculation(self, driver, base_url):
        """
        БАГ №2: Неправильный расчет комиссии
        """
        driver.get(f"{base_url}/index.html?balance=110&reserved=0")
        wait = WebDriverWait(driver, 10)
        
        # Ждем загрузки
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # Выбираем Рубли
        rub_card = wait.until(EC.element_to_be_clickable((By.XPATH, "//h2[text()='Рубли']")))
        rub_card.click()
        
        # Вводим сумму
        amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
        amount_input.clear()
        amount_input.send_keys("100")
        
        # Проверяем кнопку
        transfer_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
        
        # ❌ Тест должен упасть - кнопка неактивна
        assert transfer_btn.is_enabled(), "БАГ: Кнопка неактивна, хотя средств достаточно!"
    
    def test_valid_card_number_input(self, driver, base_url):
        """
        Позитивный тест - проверка ввода номера карты
        """
        driver.get(f"{base_url}/index.html?balance=1000&reserved=0")
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # Вводим номер карты
        card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
        card_input.send_keys("1234567890123456")
        
        # Проверяем что значение ввелось
        assert len(card_input.get_attribute('value').replace(' ', '')) == 16