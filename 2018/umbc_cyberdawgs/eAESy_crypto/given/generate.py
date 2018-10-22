#!/usr/bin/env python3
from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16

TESTFILE = """So I decided 2 be a nice person and give you a test file, so you
can see what the output of this program looks like. Unfortunately, I didn't give
you the flag, which means you'll have to figure it out on your own :}

If no one gets this challenge, it'll make this Dawg pretty sad, s0 pleas3 so1ve
it for me before the end of the CTF :_{
"""

FLAG = open("flag.txt", "rb").read()

KEY = Random.new().read(BLOCK_SIZE)
IV = Random.new().read(BLOCK_SIZE)

def encrypt(msg, key, iv):
    ciphertext = b''
    for i in msg:
        cipher = AES.new(key, AES.MODE_CFB, iv)
        ct = cipher.encrypt(chr(i))
        ciphertext += ct
    return IV + ciphertext

def decrypt(msg, key):
    plaintext = b''
    iv = msg[0:BLOCK_SIZE]
    ciphertext = msg[BLOCK_SIZE:]
    for i in ciphertext:
        cipher = AES.new(key, AES.MODE_CFB, iv)
        pt = cipher.decrypt(chr(i))
        plaintext += pt
    return plaintext

test_ciphertext = encrypt(TESTFILE.encode('ascii'), KEY, IV)
with open("testfile_ciphertext.txt", "wb") as f:
    f.write(test_ciphertext)

test_plaintext = decrypt(test_ciphertext, KEY)
with open("testfile_plaintext.txt", "wb") as f:
    f.write(test_plaintext)

flag_ciphertext = encrypt(FLAG, KEY, IV)
with open("encrypted_flag.txt", "wb") as f:
    f.write(flag_ciphertext)
