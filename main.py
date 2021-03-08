from work_puncher import WorkPuncher
import json
import sys
import datetime, time

CREDENTIAL_PATH = './credentials.json'
DRIVER_PATH = './chromedriver.exe'


if __name__ == '__main__':
    """打刻する

       クレデンシャルファイルをjsonで用意する(url, contract_code, id_code, passwordをstrでもたせた辞書オブジェクト)
    """

    with open(CREDENTIAL_PATH, mode='r') as f:
        creds = json.load(f)
    # print(creds)

    work_puncher = WorkPuncher(DRIVER_PATH, True)

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