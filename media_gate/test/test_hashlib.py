import hashlib
import time

def md5sum(src):
    m = hashlib.md5()
    m.update(src.encode("utf8"))
    return m.hexdigest()

def get_hashvalue(account, key, exp):
    rand = "0"      # "0" by default, other value is ok
    uid = "0"       # "0" by default, other value is ok
    sstring = "%s-%s-%s-%s-%s" %(account, exp, rand, uid, key)
    hashvalue = md5sum(sstring)
    print(hashvalue)
    return hashvalue

#expire_time = int(time.time()) + 100
expire_time = 100 
ret = get_hashvalue('A0001', 'abcd.1234', expire_time)


