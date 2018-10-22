global _start

section .data

section .text

# https://gist.github.com/yellowbyte/d91da3c3b0bc3ee6d1d1ac5327b1b4b2
_start:
	; your code goes here
	push 0xcc85310c
	push 0xda0f9ac5
	push 0xf238999b
	call asm3
	call exit

asm3:
	push   	ebp
	mov    	ebp,esp
	mov	eax,0xb6               ; eax = 0xb6
	xor	al,al                  ; eax = 0
	mov	ah,BYTE [ebp+0x8]  ; eax = 0x9b00
	sal	ax,0x10                ; eax = 0x9b000000
	sub	al,BYTE [ebp+0xf]  ; eax = 0x9b0000f4
	add	ah,BYTE [ebp+0xd]  ; eax = 0x9b009af4
	xor	ax,WORD [ebp+0x12] ; eax = 0x9b009a38
	mov	esp, ebp
	pop	ebp
	ret

exit:
	mov		eax, 01h		; exit()
	xor		ebx, ebx		; errno
	int		80h

; asm3(0xf238999b,0xda0f9ac5,0xcc85310c)




; saved ebp
; ----------------
; return addr
; 0xf238999b
; 0xda0f9ac5
; 0xcc85310c
