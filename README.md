# auto_work_puncher

## description

手で勤怠タイムカードを押しに行くのがめんどくなったので、機械に任せることにしました  
RESTAPIなどは生えてるわけもないので、コマンドラインからSeleniumChromeヘッドレスを動かします。

## Usage

出勤or退勤

```python
python ./main.py [work_in|work_out]
```

タイムカードのURLとログイン情報を別途`./credentials.json`として設定する

```credentials.json
{
    "url": "<打刻ページのURL>"
    , "contract_code": "<会社コード>"
    , "id_code": "<社員コード>"
    , "password": "<パスワード>"
}
```

## Future Update

+ メールで出勤退勤をお知らせしているので、IMAP鯖とか立ててメール受信をトリガーにこれを走らせるようにしたい
  + AmazonSESを建てて、Lambdaで回させる作戦
+ 現在時刻をもとにある程度出勤なのか退勤なのかを自動判断してほしい(15時ごろが分岐点かな) → できるようにした
