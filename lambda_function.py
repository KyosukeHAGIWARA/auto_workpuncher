from mime_parser import MimeParser
from work_puncher import WorkPuncher
import json
import boto3
from boto3.session import Session 
import urllib.request
import logging
from collections import OrderedDict

def lambda_handler(event, context):
    """ 実際にLambdaで呼ばれる関数 
        s3のメールオブジェクトファイルの格納を受けて打刻までをハンドリング
    """

    # === 各種keyたちのinitialize ===
    # クレデンシャルの読み込み
    with open('./aws_credentials.json', 'r', encoding='utf-8') as f:
        credentials = json.load(f)

    session = Session(
        aws_access_key_id=credentials['aws_access_key_id']
        , aws_secret_access_key=credentials['aws_secret_access_key']
        , region_name=credentials['region_name']
    )
    s3  = session.client('s3')

    # 再帰事故防止でバケットを使いまわさない前提
    INPUT_BUCKET_NAME = credentials['input_bucket_name'] 
    OUTPUT_BUCKET_NAME = credentials['output_bucket_name'] 

    # === eventからs3ファイル情報抜いてs3にfetch、BytesをMIMEとしてParserに投げる ===

    # eventから今回のMIMEファイルのオブジェクトキーを引っこ抜き 
    MIME_OBJECT_KEY = event['Records'][0]['s3']['object']['key']
    # s3にfetchしてパースする
    fetch_response = fetch_s3_object(s3, INPUT_BUCKET_NAME, MIME_OBJECT_KEY)
    parser_response = MimeParser(bytes_data=fetch_response['Body'].read()).get_mail_body_content()

    print(parser_response)

    # === 解析したメールobjをもとに出勤or退勤を見極めて打刻する ===
    if parser_response['from_address'] == credentials['mail_from']:
        # 送信元が合っているか
        punch_type = seek_mail_body(parser_response['body'])
        if punch_type == 1:
            # 出勤がmatch
            return_status_text = work_punch(punch_type='work_in')
            notice_to_slack(credentials['webhook_url'], return_status_text)
        elif punch_type == 2:
            # 退勤がmatch
            return_status_text = work_punch(punch_type='work_out')
            notice_to_slack(credentials['webhook_url'], return_status_text)
        else:
            # どちらもmatchしなかった
            notice_to_slack(credentials['webhook_url'], 'No match, No Punch. Confirm your mail.')        
    else:
        # 送信元が違った
        notice_to_slack(credentials['webhook_url'], 'Different from address. Confirm your mail.')

def fetch_s3_object(session, bucket_name, object_key):
    """
        s3から指定のオブジェクトデータをとってくる
    """
    try:
        response = session.get_object(
            Bucket = bucket_name,
            Key    = object_key
        )
    except Exception as e:
        raise e
    
    return response

def seek_mail_body(body_text):
    """出勤か退勤かをメール本文から判別する

    Args:
        body_text (str): メール本文

    Returns:
        (int): punch_type (1:出勤, 2:退勤, 0:判別不可)
    """

    # メール本文に出勤/退勤が出てこないかを調べる
    # 複数ヒットの場合、より前のほうに出てくるものをピック(返信メールとかで複数含まれることが考えられる)
    match_list = [
        '[出勤]'
        , '[退勤]'
    ]

    current_key = 0
    current_position = 999999

    for ind, keyword in enumerate(match_list, 1):
        pos = body_text.find(keyword)
        if -1 < pos and pos < current_position:
            current_position = pos
            current_key = ind
    
    return current_key

def work_punch(punch_type):
    """Seleniumで打刻する

    Args:
        punch_type (str): 打刻の種類(出勤: work_in, 退勤: work_out)
    """
    with open('./credentials.json', mode='r') as f:
        creds = json.load(f)

    work_puncher = WorkPuncher('./chromedriver.exe', True)

    # ログインする
    work_puncher.login(
        url=creds['url']
        , contract_code=creds['contract_code']
        , id_code=creds['id_code']
        , password=creds['password']
    )
 
    # 引数に応じて打刻する
    ret_status = work_puncher.punch(punch_type)
    return ret_status

def notice_to_slack(hook_url, message_text):
    """slackの特定channelにメッセージをポストする

    Args:
        hook_url (str): slackのincoming webhook url
        message_text (str): 投げたいテキスト
    Ref:
        AWS LambdaでSlack通知してみる(Qiita)(URL省略)
    """

    send_data = {
        "text": message_text,
    }
    send_text = json.dumps(send_data)
    request = urllib.request.Request(
        hook_url, 
        data=send_text.encode('utf-8'), 
        method="POST"
    )
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode('utf-8')

if __name__ == '__main__':
    """main関数
    """
    # ローカルテスト用

    with open('./test/test_event_data_1.json', 'r', encoding='utf-8') as f:
        event_data = json.load(f)

    # print('event_data')
    # print(event_data)
    
    lambda_handler(event_data, {})