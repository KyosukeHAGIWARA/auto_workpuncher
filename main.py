import sys
import time, datetime
import json
from selenium import webdriver

DRIVER_PATH = './chromedriver'

# ヘッドレスモード
is_headless = False

if is_headless:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
else:
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)


def login(credentials):

    # ログインページ叩く
    driver.get(credentials['url'])
    time.sleep(3)
    # print(driver.find_element_by_tag_name("body").text)
    
    # 認証情報を入れる
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
    
    # submit
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[7]/td/div/div/input').click()


def punch(punch_type):
    # 出勤or退勤で押す場所変える
    if punch_type == 'work_in':
        type_elm = '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr[2]/td[1]/div/div/table/tbody/tr/td'
    elif punch_type == 'work_out':
        type_elm = '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr[2]/td[3]/div/div/table/tbody/tr/td'
    else:
        print('{} : Error : plz set work_in or work_out'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S')))
        return -1
    
    driver.find_element_by_xpath(type_elm).click()

    submit_btn = driver.find_element_by_xpath(
        '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[3]/td/div/div/div/input')
    submit_btn.click()
    
    time.sleep(3)

    print('{} : {} done.'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S'), punch_type))
    # 以下実行すると打刻される  
    # ok_btn = driver.find_element_by_xpath(
    #     '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[6]/td/div/div/table/tbody/tr/td[1]/div/div/input')
    # ok_btn.click()

if __name__ == "__main__":
    with open("credentials.json", mode="r") as f:
        creds = json.load(f)

    login(creds)
    time.sleep(3)
 
    # コマンドライン引数を受け取って打刻する
    try:
        punch(sys.argv[1])
    except IndexError:
        # 引数書いてもらえなかったときは15時を分岐点に判断する
        if datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M') < '15:00':
            punch('work_in')
        else:
            punch('work_out')
    

    driver.quit()
