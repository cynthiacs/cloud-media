from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
#http://www.cnblogs.com/huxianglin/p/6387045.html
#https://www.npmjs.com/package/jsencrypt

# pip install pycrypto
# openssl genrsa -out rsa_1024_priv.pem 1024
# openssl rsa -pubout -in rsa_1024_priv.pem -out rsa_1024_pub.pem

cipher_text = 'UgQodcTz1xThuJThItVQwBYLCo6sIf0MwugG+/dEXKc9Fby3dtytZ8OVxjY2NHNnTaMCXNFpc9x6FKa+1yZwBzybX1POvFYfdPuPYFMrMV+OxnqySKMq0ByjiWoKa+1KShFvCwDyO0p50B192aWloDvPlTce3p0Q47CiLYghu5g='

with open('rsa_1024_priv.pem') as f:
    key = f.read()
    rsakey = RSA.importKey(key)  # 导入读取到的私钥
    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
    text = cipher.decrypt(base64.b64decode(cipher_text), "ERROR")  # 将密文解密成明文，返回的是一个bytes类型数据，需要自己转换成str
    print(text)
