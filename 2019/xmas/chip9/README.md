
## CHIP-9 Emulator

This was a CTF challenge I solved during the 2019 XMAS-CTF. To solve the challenge, I had to implement an emulator for the fictional CHIP-9 ISA. With the emulator, one could load and execute the provided ROM file and view the flag being drawn on the screen.

![](full_flag.gif)

## Implementation Details

The ISA itself is pretty straightforward, but this was my first attempt at implementing a complete emulator, including graphics output. When I first solved the challenge, I implemented the CPU in Python and used the PyGame library to render the display. This was PAINFULLY slow - by the time I could view the flag, I had waited a whole hour. I wanted to re-visit the challenge and try solving it in C++. I'm happy to say that what once took 60 minutes now only takes 5 seconds! In fact, it runs so fast that you'll often miss the first few frames of the ROM's animation :)

### Threaded Execution
A CPU does three things at its core - it fetches an instruction, decodes the instruction, and executes the instruction. Decoding is usally done by matching the instruction's opcode. The most naive implementation would look something like this:

```python
while True:

    inst = mem[pc]
    opcode = OPCODE(inst)

    if opcode == OP_ADD:
        EXEC_ADD(inst)
        pc += 3
    elif opcode == OP_SUB:
        EXEC_SUB(inst)
        ...
```

- "fetch" occurs when we retrieve an instruction from memory at the current PC.
- "decode" occurs when we match the opcode against known opcodes, like OP_ADD.
- "execute" occurs when we go to the instruction's handler, which executes on the instruction's operands.

This works just fine for a simple challenge like this. However, at worst, we may have to perform `N` condition checks before completing the "decode" phase. A more robust interpreter/emulator would not be written this way.

What if, at the end of each instruction, we fetched the next instruction. Then, in O(1) time, we jumped right to the next instruction's handler. You might be thinking, "you said O(1), I'm thinking of hashmaps!". And you'd be right! One great way to use hashmaps for O(1) jumping is with [threaded execution](https://en.wikipedia.org/wiki/Threaded_code).

The idea is to create a giant table mapping opcodes to addresses in your code. You index into the table with the opcode of the next instruction, then jump to the address in that entry of the table.

```python
jumptable = [&ADD, &SUB, ...]

first_opcode = OPCODE(mem[pc])
GOTO jumptable[first_opcode]
while True:

    ADD:
        inst = mem[pc]
        EXEC_ADD(inst)
        pc += 3

        next_opcode = OPCODE(mem[pc])
        GOTO jumptable[next_opcode]

    SUB:
        ...
```

Now, we have O(1) instruction dispatch! I don't suspect this had a huge impact on my emulator's performance since we were running such a simple ISA, but it was fun to do nonetheless.

### Graphics Library

This was one of the most painful parts of this emulator. I started with PyGame for the Python implementation. This was easy to use, but incredibly slow for my purposes. In C++, I tried to get started with OpenGL.

Being a novice at OpenGL, I found it incredibly unintuitive and difficult to use. Initializing OpenGL would sometimes introduce spurious seg-faults in my code, and most of the useful client libraries are event-driven, which didn't mesh well with how I wanted to write my emulator. I later settled with using a library called Simple DirectMedia Layer, or SDL. This library was very straightforward and a pleasure to work with. All I had to do was draw rectangles on a grid and it took care of the rendering details for me.

### Graphics Optimizations

I was getting higher speeds with SDL compared to PyGame, but it was still painfully slow. After experimenting with why, I realized it was because of the CHIP-9 "DRAW" instruction's semantics. The CHIP-9 "DRAW" only writes 1 byte to the screen at a time, so drawing a single frame could take hundreds of calls to "DRAW".

I was attempting to re-render the screen buffer after every time "DRAW" was called, resulting in a large number of rerenders and extremely poor performance. I later changed it so that SDL would only render a buffer if CHIP-9 executed a "CLRSCRN" instruction. "CLRSCRN" was usually called after a single frame was finished drawing, since this clears the virtual screen to prepare for drawing the next frame.

With that optimization, I saw _extremely_ dramatic speed improvements - in fact, the flag flew by on the screen so fast that I could barely read it! I needed to artificially limit the number of frames being rendered to the screen per second by introducing some timer delays. So, in my Screen helper class, I implemented a frame cap that would delay drawing to the screen. With this knob, I could tune down my FPS until the screen rendering looked somewhat normal.

### Bug Fixes with Carry

Finally, the last improvement I did was correctly implementing the carry flag semantics. During the real CTF, I encountered a crash in the boot rom that I never solved. I worked around it by just skipping over the crashing part and got the flag just fine, but I wanted to learn why it failed in the first place.

There were two things I did incorrecty. First, when I first did this challenge, I glossed over the fact that CMP instructions relied on subtraction. This meant that the C and H flags should be updated even though it wasn't explicitly stated in the instructions. The other thing I didn't realize was that computing the carry flag is different based on whether you're adding or subtracting.

When adding two values, you compute the C Flag like this:

```C++
uint8_t res = x + y;
regs.set_CFLAG(((x ^ y ^ res) & (1 << 8)) != 0);
```

But when subtracting, you have to make sure to negate the second operand before xoring:

```C++
uint8_t res = x - y;
uint8_t neg_y = 0xFF - y + 1;
regs.set_CFLAG(((x ^ neg_y ^ res) & (1 << 8)) != 0);
```

For an explanation of why we can use XOR to implement carry flags, see [here](https://stackoverflow.com/questions/62006764/how-is-xor-applied-when-determining-carry). It took me some time to understand what was being said but after thinking for an hour, I finally understood it! And with these two bug fixes, I no longer required a hack to get around the bootrom crashing :)

## Conclusion

All in all, I really enjoyed this CTF challenge. It inspired me to learn about the world of emulation and I hope to do more things like this in the future.
