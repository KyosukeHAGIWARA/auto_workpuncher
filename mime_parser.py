
import email
from email.header import decode_header
import base64
from dateutil.parser import parse


class MimeParser:
    """ MIMEデータを引き受けて読める形にパースするやつ """

    def __init__(self, bytes_data=b'', mail_file_path=''):
        # props
        self.email_message = None

        self.to_address = None
        self.cc_address = None
        self.from_address = None
        self.subject = None
        self.date = None
        self.body = ""
        # 添付ファイル情報 {name: file_name, data: data}
        self.attach_file_list = []
        
        
        # MIMEの解釈
        if bytes_data:
            self.email_message = email.message_from_bytes(bytes_data)
            self._parse()
        elif mail_file_path:
            self.email_message = self._get_bytes_from_file(mail_file_path)
            self._parse()
        else:
            print('Error: bytes_data or mail_file_path...')


    def _parse(self):
        """
            メールファイルの解析
            __init__で呼び出し
        """
        self.to_address = self._get_decoded_header("To")
        self.cc_address = self._get_decoded_header("Cc")
        self.from_address = self._get_decoded_header("From")
        self.subject = self._get_decoded_header("Subject")
        self.date = parse(self._get_decoded_header("Date")).isoformat()
        # print(f'{self.subject} {self.to_address} {self.cc_address} {self.from_address}')

        # メッセージ本文部分の処理
        for part in self.email_message.walk():
            # ContentTypeがmultipartの場合は実際のコンテンツはさらに
            # 中のpartにあるので読み飛ばす
            if part.get_content_maintype() == 'multipart':
                continue
            # ファイル名の取得
            attach_fname = part.get_filename()
            # ファイル名がない場合は本文のはず
            if not attach_fname:
                charset = part.get_content_charset()
                if charset:
                    self.body += part.get_payload(decode=True).decode(
                        str(charset), errors="replace")
            else:
                # ファイル名があるならそれは添付ファイルなので
                # データを取得する
                # ファイル名をいい感じにbase64=>utf8strに
                # 途中'\r\n\t'で分割されてるので、分割の各々をdecode、それを結合してファイル名に
                self.attach_file_list.append({
                    "name":
                        # attach_fname,
                        ''.join([base64.b64decode(x[10:-2]).decode('utf-8') for x in attach_fname.split('\r\n\t')]),
                    "data":
                        part.get_payload(decode=True).decode('utf-8')
                })


    def _get_decoded_header(self, key_name):
        """ ヘッダーオブジェクトからデコード済の結果を取得する """
        ret = ""

        # 該当項目がないkeyは空文字を戻す
        raw_obj = self.email_message.get(key_name)
        if raw_obj is None:
            return ""
        # デコードした結果をunicodeにする
        for fragment, encoding in decode_header(raw_obj):
            if not hasattr(fragment, "decode"):
                ret += fragment
                continue
            # encodeがなければとりあえずUTF-8でデコードする
            ret += fragment.decode(encoding if encoding else 'UTF-8',
                                   errors='replace')
        return ret


    def _get_bytes_from_file(self, file_path):
        """ ローカルファイルからMIMEデータをbytesとして読み込み """

        # TODO 実装
        return b''


    def get_mail_body_content(self):
        """ 添付ファイル以外の基本的なメールデータをdictで """
        ret = {
            'to_address': self.to_address,
            'cc_address': self.cc_address,
            'from_address': self.from_address,
            'subject': self.subject,
            'date': self.date,
            'body': self.body
        }
        return ret
    
    def get_mail_attach_files(self):
        """ 添付ファイルのデータをlistで """
        return self.attach_file_list

    def get_mail_full_content(self):
        """ 全部のメールデータをdictで """
        ret = self.get_mail_body_content()
        ret['attach_files'] = self.get_mail_attach_files()
        return ret
