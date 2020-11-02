#pragma once
#include "RegisterFile.hpp"
#include "Memory.hpp"
#include "Screen.hpp"
#include "chip9types.hpp"

#define HEIGHT 64
#define WIDTH 128
#define EVENT_POLL_FREQUENCY 800

#define NEG(val) (0xFF - val + 1)

#define DISPATCH(x) \
    pc += x; \
    if (cycles_since_last_poll >= EVENT_POLL_FREQUENCY) { \
        this->screen->handleEvents(); \
        cycles_since_last_poll = 0; \
    } else { \
        cycles_since_last_poll++; \
    } \
    goto *jumptable[mem[pc]]

#define SET_ZN_FLAGS_8(val) \
    regs.set_ZFLAG(val == 0); \
    regs.set_NFLAG((int8_t)val < 0)

#define SET_ZN_FLAGS_16(val) \
    regs.set_ZFLAG(val == 0); \
    regs.set_NFLAG((int16_t)val < 0)

#define SET_ALL_FLAGS_8(x, y, res) \
    SET_ZN_FLAGS_8(res); \
    regs.set_CFLAG(((x ^ y ^ res) & (1 << 8)) != 0); \
    regs.set_HFLAG(((x ^ y ^ res) & (1 << 4)) != 0)

#define SET_ALL_FLAGS_16(x, y, res) \
    SET_ZN_FLAGS_16(res); \
    regs.set_CFLAG(((x ^ y ^ res) & (1 << 16)) != 0); \
    regs.set_HFLAG(((x ^ y ^ res) & (1 << 8)) != 0)

#define ADD_8(dst, src, inst_size) \
    res8 = dst + src; \
    SET_ALL_FLAGS_8(dst, src, res8); \
    dst = res8; \
    DISPATCH(inst_size)

#define ADD_16(dstH, dstL, src, inst_size) \
    dstVal = (dstH << 8) | (dstL); \
    res16 = dstVal + src; \
    SET_ALL_FLAGS_16(dstVal, src, res16); \
    dstH = (res16 & 0xFF00) >> 8; \
    dstL = res16 & 0xFF; \
    DISPATCH(inst_size)

#define SUB_8(dst, src, inst_size) \
    res8 = dst - src; \
    SET_ALL_FLAGS_8(dst, NEG(src), res8); \
    dst = res8; \
    DISPATCH(inst_size)

#define SIGNED_SUB_8(dst, src, inst_size) \
    sres8 = (int8_t) dst - (int8_t) src; \
    SET_ALL_FLAGS_8(dst, NEG(src), sres8); \
    dst = sres8; \
    DISPATCH(inst_size)

#define NZ_FLAGS_OP_8(op, dst, src, inst_size) \
    dst = dst op src; \
    SET_ZN_FLAGS_8(dst); \
    regs.set_CFLAG(false); \
    regs.set_HFLAG(false); \
    DISPATCH(inst_size)

class Emulator {
    private:
        Screen<HEIGHT, WIDTH> *screen;
        RegisterFile regs;
        Memory mem;
        address_t pc;
        address_t sp;
        void *jumptable[1 << 8];
        std::string names[1 << 8];
        uint8_t pixels[HEIGHT][WIDTH];
        size_t cycles_since_last_poll = 0;

        virtual void clearscreen();
        virtual void draw();
        virtual std::string inst_repr();
    public:
        Emulator() {}
        virtual void init();
        virtual void run();
};
