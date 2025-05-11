from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, uuid

BASE_URL = "http://127.0.0.1:5000"
DEFAULT_RECEIVER_EMAIL = "william@DailyBite.com"
DEFAULT_RECEIVER_PASSWORD = "DailyBite"

def register_user(driver, suffix=""):
    driver.get(f"{BASE_URL}/auth/register")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "firstName")))
    time.sleep(1)

    email = f"user_{suffix}@example.com"
    password = "TestPass123"

    driver.find_element(By.NAME, "firstName").send_keys("User")
    time.sleep(0.5)
    driver.find_element(By.NAME, "lastName").send_keys(suffix)
    time.sleep(0.5)
    driver.find_element(By.NAME, "emailRegister").send_keys(email)
    time.sleep(0.5)
    driver.find_element(By.NAME, "passwordRegister").send_keys(password)
    time.sleep(0.5)
    driver.find_element(By.NAME, "passwordRegisterRepeat").send_keys(password)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "SignUpLocation"))
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container")))
    time.sleep(2)
    return email, password

def login(driver, email, password):
    driver.get(f"{BASE_URL}/auth/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "emailLogin")))
    time.sleep(1)

    driver.find_element(By.NAME, "emailLogin").send_keys(email)
    time.sleep(0.5)
    driver.find_element(By.NAME, "passwordLogin").send_keys(password)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]'))
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container")))
    time.sleep(2)

def test_full_user_journey():
    driver = webdriver.Chrome()
    uid = str(uuid.uuid4())[:8]
    sender_email, sender_pwd = register_user(driver, f"sender{uid}")

    # Add meal
    driver.get(f"{BASE_URL}/addMeal")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "foodInput")))
    time.sleep(1)

    driver.find_element(By.ID, "foodInput").send_keys("chicken")
    time.sleep(1)
    driver.find_element(By.ID, "searchFoodLink").click()
    time.sleep(2)

    results = driver.find_elements(By.CLASS_NAME, "searchResult")
    if results:
        results[0].click()
        time.sleep(1)

        meal_type_select = driver.find_element(By.ID, "mealTypeInput")
        for option in meal_type_select.find_elements(By.TAG_NAME, "option"):
            if option.text.strip() == "Lunch":
                option.click()
                break
        time.sleep(1)

        driver.find_element(By.ID, "quantityInput").clear()
        driver.find_element(By.ID, "quantityInput").send_keys("150")
        time.sleep(1)

        submit_btn = driver.find_element(By.ID, "addMealSubmit")
        driver.execute_script("arguments[0].click();", submit_btn)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "calorieTrendChart")))
        time.sleep(2)

    # Change view mode today/last 7 days
    btn_today = driver.find_element(By.CSS_SELECTOR, 'button.time-range-btn[data-range="day"]')
    driver.execute_script("arguments[0].click();", btn_today)
    time.sleep(2)

    # share
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "openShareBtn"))
    time.sleep(1)

    search_input = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "friendSearchInput")))
    search_input.send_keys(DEFAULT_RECEIVER_EMAIL)
    time.sleep(1)

    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "friendSearchBtn"))
    time.sleep(2)

    driver.execute_script("arguments[0].click();", driver.find_elements(By.NAME, "selected_friend_id")[0])
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "toast-body")))
    time.sleep(2)

    # logout and login as receiver
    driver.get(f"{BASE_URL}/auth/logout")
    time.sleep(1)

    login(driver, DEFAULT_RECEIVER_EMAIL, DEFAULT_RECEIVER_PASSWORD)

    # check shared meal
    driver.get(f"{BASE_URL}/sharing_list")
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "sharing-item-link"))).click()
    time.sleep(1)

    chart = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "chartContainer")))
    assert chart is not None
    time.sleep(2)

    print("[✅] ALL Pass!")
    driver.quit()

if __name__ == "__main__":
    test_full_user_journey()
