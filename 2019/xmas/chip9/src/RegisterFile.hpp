#pragma once
#include <cstdint>
#include "chip9types.hpp"

enum Register { A, B, C, D, E, H, L, count };

class RegisterFile {
    private:
        byte_t registers[count];
        byte_t flags;
    public:
        RegisterFile() {}

        byte_t & operator[] (Register regname)
        {
            return registers[regname];
        }

        virtual word_t BC();
        virtual word_t DE();
        virtual word_t HL();
        virtual void set_BC(word_t val);
        virtual void set_DE(word_t val);
        virtual void set_HL(word_t val);

        virtual int ZFLAG();
        virtual int NFLAG();
        virtual int HFLAG();
        virtual int CFLAG();
        virtual void set_ZFLAG(bool set);
        virtual void set_NFLAG(bool set);
        virtual void set_HFLAG(bool set);
        virtual void set_CFLAG(bool set);
};
