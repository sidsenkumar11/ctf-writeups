.intel_syntax noprefix
.bits 32
	
.global asm3

asm3:
	push   	ebp
	mov    	ebp,esp
	mov	eax,0xb6
	xor	al,al
	mov	ah,BYTE PTR [ebp+0x8]
	sal	ax,0x10
	sub	al,BYTE PTR [ebp+0xf]
	add	ah,BYTE PTR [ebp+0xd]
	xor	ax,WORD PTR [ebp+0x12]
	mov	esp, ebp
	pop	ebp
	ret
