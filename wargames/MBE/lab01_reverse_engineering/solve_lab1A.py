#!/usr/bin/python

from __future__ import print_function
from unicorn import *
from unicorn.x86_const import *
from pwn import *
pwnlib.args.SILENT('SILENT')

# Assembled code from: https://defuse.ca/online-x86-assembler.htm#disassembly
"""
The following is a slightly modified version of the serial generation logic from Lab1A.
The main difference is that initially, I assume:
    - eax contains the current letter in the username
    - ebx contains the current seed

This way, I avoided operating anything in memory.

0:  0f be c0                movsx  eax,al
3:  31 d8                   xor    eax,ebx
5:  89 c1                   mov    ecx,eax
7:  ba 2b 3b 23 88          mov    edx,0x88233b2b
c:  89 c8                   mov    eax,ecx
e:  f7 e2                   mul    edx
10: 89 c8                   mov    eax,ecx
12: 29 d0                   sub    eax,edx
14: d1 e8                   shr    eax,1
16: 01 d0                   add    eax,edx
18: c1 e8 0a                shr    eax,0xa
1b: 69 c0 39 05 00 00       imul   eax,eax,0x539
21: 29 c1                   sub    ecx,eax
23: 89 c8                   mov    eax,ecx
25: 01 c3                   add    ebx,eax
"""
X86_CODE32 = b"\x0F\xBE\xC0\x31\xD8\x89\xC1\xBA\x2B\x3B\x23\x88\x89\xC8\xF7\xE2\x89\xC8\x29\xD0\xD1\xE8\x01\xD0\xC1\xE8\x0A\x69\xC0\x39\x05\x00\x00\x29\xC1\x89\xC8\x01\xC3"

# Initial values
username = "banana"
seed = (ord(username[3]) ^ 0x1337) + 0x5eeded

# Compute each serial digit
for letter in username:

    # Memory address where emulation starts
    ADDRESS = 0x1000000

    print("Current letter: {}".format(letter))
    try:
        # Initialize emulator in X86-32bit mode
        mu = Uc(UC_ARCH_X86, UC_MODE_32)

        # map 2MB memory for this emulation
        mu.mem_map(ADDRESS, 2 * 1024 * 1024)

        # write machine code to be emulated to memory
        mu.mem_write(ADDRESS, X86_CODE32)

        # initialize machine registers
        mu.reg_write(UC_X86_REG_EAX, ord(letter))
        mu.reg_write(UC_X86_REG_EBX, seed)

        # emulate code in infinite time & unlimited instructions
        mu.emu_start(ADDRESS, ADDRESS + len(X86_CODE32))

        # now print out some registers
        r_ebx = mu.reg_read(UC_X86_REG_EBX)
        # print("Emulation done. Below is the CPU context")
        # print(">>> EBX = 0x%x" %r_ebx)

        # Update the seed
        seed = r_ebx

    except UcError as e:
        print("ERROR: %s" % e)

print("Desired Serial: {}".format(seed))

# Send username and serial to binary
p = process('./lab1A')
p.sendline(username)
p.sendline(str(seed))

print(p.recvuntil("'---------------------------'"))
print(username)
print(p.recvuntil("'---------------------------'"))
print(str(seed))
p.interactive()
