import rsa

(pubKey, privKey) = rsa.newkeys(1024)

#msg = 'hello'
#print(msg)
#crypto = rsa.encrypt(msg.encode(), pubKey)
#print(crypto)
#msg = rsa.decrypt(crypto, privKey).decode()
#print(msg)

#data = 'signaturexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#signature = rsa.sign(data.encode(), privKey, 'SHA-1')
##signature = rsa.sign(data.encode(), privKey, 'MD5')
#print(signature)
#if(rsa.verify(data.encode(), signature, pubKey)):
#    print('verified signature')
#else:
#    print('wrong signature')


#with open('public.pem','w+') as f:
#    f.write(pubKey.save_pkcs1().decode())
#
#    with open('private.pem','w+') as f:
#        f.write(privKey.save_pkcs1().decode())
#
#with open('public.pem','r') as f:
#    pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
#
#    with open('private.pem','r') as f:
#        privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())

# https://www.cnblogs.com/renfanzi/p/6062261.html
