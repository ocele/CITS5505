from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, uuid

BASE_URL = "http://127.0.0.1:5000"
DEFAULT_EMAIL = "william@dailybite.com"
DEFAULT_PASSWORD = "DailyBite"
RECEIVER_EMAIL = "haoran@dailybite.com"
RECEIVER_PASSWORD = "DailyBite"

def login(driver, email, password):
    driver.get(f"{BASE_URL}/auth/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "emailLogin")))
    time.sleep(1)
    driver.find_element(By.NAME, "emailLogin").send_keys(email)
    time.sleep(0.5)
    driver.find_element(By.NAME, "passwordLogin").send_keys(password)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]'))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container")))
    time.sleep(1)

def test_register_user():
    driver = webdriver.Chrome()
    driver.get(f"{BASE_URL}/auth/register")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "firstName")))
    suffix = str(uuid.uuid4())[:8]
    email = f"user_{suffix}@example.com"
    pwd = "TestPass123"
    driver.find_element(By.NAME, "firstName").send_keys("User")
    driver.find_element(By.NAME, "lastName").send_keys(suffix)
    driver.find_element(By.NAME, "emailRegister").send_keys(email)
    driver.find_element(By.NAME, "passwordRegister").send_keys(pwd)
    driver.find_element(By.NAME, "passwordRegisterRepeat").send_keys(pwd)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "SignUpLocation"))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container")))
    print("[✅] Registration test passed")
    time.sleep(1)
    driver.quit()

def test_login():
    driver = webdriver.Chrome()
    login(driver, DEFAULT_EMAIL, DEFAULT_PASSWORD)
    print("[✅] Login test passed")
    time.sleep(1)
    driver.quit()

def test_add_meal():
    driver = webdriver.Chrome()
    login(driver, DEFAULT_EMAIL, DEFAULT_PASSWORD)
    driver.get(f"{BASE_URL}/addMeal")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "foodInput")))
    driver.find_element(By.ID, "foodInput").send_keys("chicken")
    driver.find_element(By.ID, "searchFoodLink").click()
    time.sleep(2)
    driver.find_elements(By.CLASS_NAME, "searchResult")[0].click()
    driver.find_element(By.ID, "quantityInput").clear()
    driver.find_element(By.ID, "quantityInput").send_keys("150")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "addMealSubmit"))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "calorieTrendChart")))
    print("[✅] Add meal test passed")
    time.sleep(1)
    driver.quit()

def test_switch_view():
    driver = webdriver.Chrome()
    login(driver, DEFAULT_EMAIL, DEFAULT_PASSWORD)
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.time-range-btn[data-range="day"]')))
    driver.execute_script("arguments[0].click();", button)
    print("[✅] View switch test passed")
    time.sleep(1)
    driver.quit()

def test_share_and_receive():
    driver = webdriver.Chrome()
    login(driver, DEFAULT_EMAIL, DEFAULT_PASSWORD)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "openShareBtn"))
    time.sleep(1)
    driver.find_element(By.ID, "friendSearchInput").send_keys(RECEIVER_EMAIL)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "friendSearchBtn"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_elements(By.NAME, "selected_friend_id")[0])
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "toast-body")))
    time.sleep(1)

    driver.get(f"{BASE_URL}/auth/logout")
    login(driver, RECEIVER_EMAIL, RECEIVER_PASSWORD)
    driver.get(f"{BASE_URL}/sharing_list")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "sharing-item-link"))).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "chartContainer")))
    print("[✅] Share & receive test passed")
    time.sleep(1)
    driver.quit()
