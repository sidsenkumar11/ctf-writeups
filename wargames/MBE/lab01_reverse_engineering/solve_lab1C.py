from __future__ import print_function
from pwn import *
pwnlib.args.SILENT('SILENT')

p = process('./lab1C')
p.sendline('5274')

print(p.recvuntil('Password: '), end='')
print('5274')
p.interactive()
