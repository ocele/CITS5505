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
    email = f"user_{suffix}@example.com"
    password = "TestPass123"

    driver.find_element(By.NAME, "firstName").send_keys("User")
    driver.find_element(By.NAME, "lastName").send_keys(suffix)
    driver.find_element(By.NAME, "emailRegister").send_keys(email)
    driver.find_element(By.NAME, "passwordRegister").send_keys(password)
    driver.find_element(By.NAME, "passwordRegisterRepeat").send_keys(password)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "SignUpLocation"))

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container")))
    time.sleep(2)
    return email, password

def login(driver, email, password):
    driver.get(f"{BASE_URL}/auth/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "emailLogin")))
    driver.find_element(By.NAME, "emailLogin").send_keys(email)
    driver.find_element(By.NAME, "passwordLogin").send_keys(password)
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]'))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container")))
    time.sleep(2)

def test_full_user_journey():
    sender_driver = webdriver.Chrome()
    uid = str(uuid.uuid4())[:8]
    sender_email, sender_pwd = register_user(sender_driver, f"sender{uid}")

    # 添加食物
    sender_driver.get(f"{BASE_URL}/addMeal")
    WebDriverWait(sender_driver, 10).until(EC.presence_of_element_located((By.ID, "foodInput")))
    time.sleep(2)
    sender_driver.find_element(By.ID, "foodInput").send_keys("chicken")
    sender_driver.find_element(By.ID, "searchFoodLink").click()
    time.sleep(2)

    results = sender_driver.find_elements(By.CLASS_NAME, "searchResult")
    if results:
        results[0].click()
        sender_driver.find_element(By.ID, "quantityInput").clear()
        sender_driver.find_element(By.ID, "quantityInput").send_keys("150")
        sender_driver.execute_script("arguments[0].click();", sender_driver.find_element(By.CSS_SELECTOR, 'form input[type="submit"]'))
        WebDriverWait(sender_driver, 10).until(EC.presence_of_element_located((By.ID, "calorieTrendChart")))
        time.sleep(2)

    # 切换图表按钮
    btn_today = sender_driver.find_element(By.CSS_SELECTOR, 'button.time-range-btn[data-range="day"]')
    sender_driver.execute_script("arguments[0].click();", btn_today)
    time.sleep(2)

    # 分享模态框
    sender_driver.execute_script("arguments[0].click();", sender_driver.find_element(By.ID, "openShareBtn"))
    time.sleep(2)
    search_input = WebDriverWait(sender_driver, 5).until(EC.element_to_be_clickable((By.ID, "friendSearchInput")))
    search_input.send_keys(DEFAULT_RECEIVER_EMAIL)
    sender_driver.execute_script("arguments[0].click();", sender_driver.find_element(By.ID, "friendSearchBtn"))
    time.sleep(2)
    sender_driver.execute_script("arguments[0].click();", sender_driver.find_elements(By.NAME, "selected_friend_id")[0])
    sender_driver.execute_script("arguments[0].click();", sender_driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
    WebDriverWait(sender_driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "toast-body")))
    time.sleep(2)

    # ✅ 改为直接跳转到登录页（不依赖页面元素）
    sender_driver.get(f"{BASE_URL}/logout")
    time.sleep(2)
    sender_driver.get(f"{BASE_URL}/auth/login")
    time.sleep(2)
    sender_driver.quit()

    # 登录默认用户查看分享
    receiver_driver = webdriver.Chrome()
    login(receiver_driver, DEFAULT_RECEIVER_EMAIL, DEFAULT_RECEIVER_PASSWORD)
    receiver_driver.get(f"{BASE_URL}/sharing_list")
    WebDriverWait(receiver_driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "sharing-item-link"))).click()
    chart = WebDriverWait(receiver_driver, 5).until(EC.presence_of_element_located((By.ID, "chartContainer")))
    assert chart is not None
    time.sleep(2)

    print("[✅] 全流程测试通过！")
    receiver_driver.quit()

if __name__ == "__main__":
    test_full_user_journey()
