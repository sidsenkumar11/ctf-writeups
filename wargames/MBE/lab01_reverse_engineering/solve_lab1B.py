from __future__ import print_function
from pwn import *
pwnlib.args.SILENT('SILENT')

initial_bytes = [0x51, 0x7D, 0x7C, 0x75, 0x60, 0x73, 0x66, 0x67, 0x7e, 0x73, 0x66, 0x7b, 0x7d, 0x7c, 0x61, 0x33]
message = "Congratulations!"
difference = [ord(x) ^ y for x,y in zip(message, initial_bytes)]
password = 0x1337d00d - int(difference[0])

p = process('./lab1B')
p.sendline(str(password))

print("Password: " + str(password))
p.interactive()
