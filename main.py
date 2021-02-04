import time
import json
from selenium import webdriver

DRIVER_PATH = './chromedriver'

# ヘッドレスモード
is_headless = True

if is_headless:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
else:
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)


def login(credentials):
    driver.get(credentials['url'])
    time.sleep(3)
    print(driver.find_element_by_tag_name("body").text)
    contract_code = driver.find_element_by_xpath(
        '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/div/div/input')
    contract_code.send_keys(credentials['contract_code'])
    id_code = driver.find_element_by_xpath(
        '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[4]/td/table/tbody/tr[2]/td/div/div/input')
    id_code.send_keys(credentials['id_code'])
    password = driver.find_element_by_xpath(
        '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[5]/td/table/tbody/tr[2]/td/div/div/input')
    password.send_keys(credentials['password'])
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[7]/td/div/div/input').click()


if __name__ == "__main__":
    with open("credentials.json", mode="r") as f:
        creds = json.load(f)

    login(creds)
    time.sleep(3)


    driver.quit()
