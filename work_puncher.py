import sys
import time, datetime
import json
from selenium import webdriver

class WorkPuncher:
    """seleniumで勤怠打刻をしにいってくれるクラス
    """

    def __init__(self, driver_path, is_headless=True):
        """コンストラクタ

        Args:
            driver_path (str): chromeDriver.exeのpath
            is_headless (bool, optional): ヘッドレスモード指定. Defaults to True.
        """
        self.driver_path = driver_path
        self.is_headless = is_headless
        self.driver = self._generate_driver()

    def _generate_driver(self):
        """ヘッドレスかどうかを見てseleniumのchromeDriverを返す

        Returns:
            selenium.webdriver.Chrome: ChromeのDriver
        """

        if self.is_headless:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            return webdriver.Chrome(executable_path=self.driver_path, options=options)
        else:
            return webdriver.Chrome(executable_path=self.driver_path)

    def set_headless_mode(self, is_headless):
        """ヘッドレスモード切替をあとから指定する

        Args:
            is_headless (bool): ヘッドレスモードにするかどうか
        """
        self.is_headless = is_headless

        # ヘッドレスモードが変わったらdriver立ち上げなおし
        self.driver.quit()
        self.driver = self._generate_driver()
    
    def login(self, url, contract_code, id_code, password):
        """ログインページ叩いてログインする

        Args:
            url (str): ログインページurl
            contract_code (str): 社名コード
            id_code (str): 社員コード
            password (str): パスワード
        """

        # ログインページ叩く
        self.driver.get(url)
        time.sleep(3)
        
        # 認証情報を入れる
        contract_code_elm = self.driver.find_element_by_xpath(
            '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/div/div/input')
        contract_code_elm.send_keys(contract_code)
        
        id_code_elm = self.driver.find_element_by_xpath(
            '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[4]/td/table/tbody/tr[2]/td/div/div/input')
        id_code_elm.send_keys(id_code)
        
        password_elm = self.driver.find_element_by_xpath(
            '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[5]/td/table/tbody/tr[2]/td/div/div/input')
        password_elm.send_keys(password)
        
        time.sleep(1)
        
        # submit
        self.driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[7]/td/div/div/input').click()
        time.sleep(3)


    def punch(self, punch_type):
        """打刻する関数

        Args:
            punch_type (str): 打刻の種類(出勤: work_in, 退勤: work_out)
        """
        # 出勤or退勤で押す場所変える
        if punch_type == 'work_in':
            type_elm = '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr[2]/td[1]/div/div/table/tbody/tr/td'
        elif punch_type == 'work_out':
            type_elm = '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[1]/td/div/div/table/tbody/tr[2]/td[3]/div/div/table/tbody/tr/td'
        else:
            print('{} : Error : plz set work_in or work_out'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S')))
            return -1
        
        self.driver.find_element_by_xpath(type_elm).click()

        submit_btn = self.driver.find_element_by_xpath(
            '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/div/div/div/table/tbody/tr[3]/td/div/div/div/input')
        submit_btn.click()
        
        time.sleep(3)

        print('{} : {} done.'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S'), punch_type))
        # 以下実行すると打刻される
        # ok_btn = self.driver.find_element_by_xpath(
        #     '/html/body/form/table/tbody/tr[2]/td/div/div/div/table/tbody/tr[6]/td/div/div/table/tbody/tr/td[1]/div/div/input')
        # ok_btn.click()


if __name__ == '__main__':
    with open('./credentials.json', mode='r') as f:
        creds = json.load(f)
    print(creds)

    work_puncher = WorkPuncher('./chromedriver.exe', True)

    # ヘッドレスモード切り替えのテスト
    # work_puncher.set_headless_mode(True)

    # ログインする
    work_puncher.login(
        url=creds['url']
        , contract_code=creds['contract_code']
        , id_code=creds['id_code']
        , password=creds['password']
    )
 
    # コマンドライン引数を受け取って打刻する
    try:
        work_puncher.punch(sys.argv[1])
    except IndexError:
        # 引数書いてもらえなかったときは15時を分岐点に判断する
        if datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M') < '15:00':
            work_puncher.punch('work_in')
        else:
            work_puncher.punch('work_out')
    