from pwn import *
import base64

p = remote('2018shell2.picoctf.com', 36150)

# Get flag file name
p.recvuntil('Please choose: ')
p.sendline('i')
p.recvuntil('Files:\n')
flag_file_name = p.recvline()[2:].strip()
log.info('Flag File: ' + flag_file_name)

# Encrypt a file
p.recvuntil('Please choose: ')
p.sendline('n')
p.recvuntil('Name of file? ')
p.sendline('faker5af6ee483d057e8d1a55')
p.recvuntil('Data? ')
p.sendline("Here's my data!")
p.recvline()
share_code = p.recvline().strip()
log.info('Share Code: ' + share_code)

# Figure out result of block cipher
data = int(base64.b64decode(share_code).encode('hex'), 16)
data = data ^ int('faker5af6ee483d057e8d1a55.txt'.encode('hex'), 16)

# Use result to figure out share code for flag
flag_share_code = int(flag_file_name.encode('hex'), 16) ^ data
flag_share_code = hex(flag_share_code)[2:]

if flag_share_code.endswith('L') or flag_share_code.endswith('l'):
	flag_share_code = flag_share_code[:-1]

flag_share_code = base64.b64encode(flag_share_code.decode('hex'))
log.info('Flag share code: ' + flag_share_code)

# Decrypt flag
p.recvuntil('Please choose: ')
p.sendline('e')
p.recvuntil('Share code?')
p.sendline(flag_share_code)
print p.recvline()
print p.recvline()

# Exit
p.recvuntil('choose: ')
p.sendline('x')
p.close()
