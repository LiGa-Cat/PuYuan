from itsdangerous import URLSafeTimedSerializer as utsr #as[別名]
import base64
from base64 import b64encode,b64decode
import re
import json
from PuYuan.settings import  SECRET_KEY

class email_token():
    def __init__(self,sk=SECRET_KEY): #SECRET_KEY一个特定 Django 安装的密钥。用于提供 加密签名，并且应该设置为一个唯一的、不可预测的值。
        # sk =sk.lstrip('*')
        # sk = sk.replace('+','')
        print("self1:",self)
        self.sk = sk
        a = bytes(sk,'utf-8')         #use of utf-8 encoding  convert objects  into bytes objects (使用UTF-8編碼轉換成bytes type)
        self.salt = base64.encodestring(a)#.decode().replace('\n','') # encode the string using base64 encoded data into the binary form.(將字串使用base64編碼成二位元)
    def generate_validate_token(self, username):
        serializer = utsr(self.sk)
        return serializer.dumps(username, self.salt)
    def confirm_validate_token(self,token,expiration=3600):
        serializer = utsr(self.sk)
        return serializer.loads(token, self.salt, max_age=expiration)