from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
browser = webdriver.Chrome(options=chrome_options)
browser.get("http://localhost:3000")
loginBtn = browser.find_element(By.CSS_SELECTOR,"#__next > div > div:nth-child(3) > div > div.hidden.mr-3.md\:flex.items-center.gap-4 > button.px-4.py-2.text-purple.rounded-\[10px\].font-semibold.border-2.border-white2.transition.hover\:bg-purple.hover\:text-white.hover\:border-purple")
loginBtn.click()
WebDriverWait(browser, 15).until(EC.url_changes("http://localhost:3000/"))

url = browser.current_url
email = browser.find_element(By.CSS_SELECTOR,"#identifierId")
email.send_keys("tpigltest@gmail.com")
browser.find_element(By.CSS_SELECTOR,"#identifierNext > div > button").click()
WebDriverWait(browser, 150).until(EC.url_changes(url))
password = browser.find_element(By.CSS_SELECTOR,"#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input")
password.send_keys("Bilelsef")
url = browser.current_url
browser.find_element(By.CSS_SELECTOR,"#passwordNext > div > button").click()

WebDriverWait(browser, 150).until(EC.url_changes(url))
browser.find_element(By.CSS_SELECTOR,"#__next > div > div:nth-child(3) > div > ul > li:nth-child(2) > a").click()
url = browser.current_url

WebDriverWait(browser, 150).until(EC.url_changes(url))
browser.find_element(By.CSS_SELECTOR,"#__next > div > div:nth-child(4) > div.flex.flex-col.justify-center.mx-2.sm\:mx-8.md\:mx-\[6vw\].lg\:mx-\[8vw\] > div.overflow-x-auto.w-full.px-4.py-6.min-h-\[400px\] > div.flex-col.md\:flex-row.gap-4.flex.w-full.items-center.justify-center > div").click()
browser.implicitly_wait(100)
browser.implicitly_wait(100)

browser.find_element(By.CSS_SELECTOR,"#description").send_keys("description test")
browser.implicitly_wait(100)

browser.find_element(By.CSS_SELECTOR,"#prix").send_keys("50000")
browser.implicitly_wait(100)
browser.find_element(By.CSS_SELECTOR,"#surface").send_keys("200")
browser.implicitly_wait(100)
browser.find_element(By.CSS_SELECTOR,"#__next > div > div:nth-child(4) > div.flex.flex-col.justify-center.mx-2.sm\:mx-8.md\:mx-\[6vw\].lg\:mx-\[8vw\] > div.modal.hero.lg\:min-w-xl > div > div > div > form > div.form-control.mt-6.loading > button").click()

